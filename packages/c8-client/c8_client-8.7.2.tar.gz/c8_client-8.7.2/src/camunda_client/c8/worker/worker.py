import inspect
import threading
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, TypeVar

from camunda_client.c8.api import (
    activate_jobs,
    complete_job,
    mark_job_as_failed,
    throw_error_for_job,
)
from camunda_client.c8.auth import get_c8_api_headers
from camunda_client.c8.auth.auth import AuthenticationManager
from camunda_client.c8.models import ActivatedJob, ActivateJobRequest
from camunda_client.config import get_config
from camunda_client.error import (
    ServiceException,
    CamundaBusinessException,
    error_code_message_mapper,
    ErrorCode,
    WorkerSignatureException,
)
from camunda_client.log import get_logger
from camunda_client.utils import JsonBaseModel

log = get_logger(__name__)


@dataclass
class JobWorkerRequest:
    type: str
    worker: str
    timeout: int
    max_jobs_to_activate: int
    fetch_variables: list[str] | None
    request_timeout: int | None
    tenant_ids: list[str] | None


@dataclass
class JobWorker:
    """"
    Pending job worker
    """
    job_type: str
    handler: Callable[[ActivatedJob], dict | JsonBaseModel]  # could be dict or JsonBaseModel if needed
    polling_interval: int | None = None
    request: JobWorkerRequest | None = None


# Pending job workers, waiting for registration
_pending_camunda_workers: list[JobWorker] = []


class CamundaWorkerManager:
    """
    Manages registered Camunda worker decorated with @camunda_worker
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # Singleton
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CamundaWorkerManager, cls).__new__(cls)
                    cls._instance._initialize_client_state()
        return cls._instance

    def _initialize_client_state(self):
        """Initializes client-specific state and gets the initial access token."""
        self._worker_threads = []
        self._job_type_and_worker: dict[str, JobWorker] = {}
        self._job_type_worker_lock = threading.Lock()
        self._stop_event = threading.Event()
        if not AuthenticationManager().is_healthy():
            log.critical("Could not initialize Camunda worker manager because authentication manager is not healthy.")
        log.info("Camunda worker manager initialized.")

    def _handle_job_failed(self, job: ActivatedJob, e: Exception):

        try:
            mark_job_as_failed(job=job, error_message=str(e))
            log.warning(f"Successfully failed job of type {job.job_type} with key {job.job_key}.")
        except ServiceException as e:
            log.critical(e.get_log_formatted_message())

    def _handle_job_throws_error(self, job: ActivatedJob, e: CamundaBusinessException):
        try:
            log.info(f"Throw error for job of type {job.job_type} and key {job.job_key}")
            throw_error_for_job(job, e)
        except ServiceException as e:
            log.critical(e.get_log_formatted_message())

    def _process_jobs(self, activated_jobs: list[ActivatedJob], handler_func):
        for job in activated_jobs:
            try:
                result = handler_func(job)
                log.info(f"Job of type {job.job_type} and key {job.job_key} was handled successfully")
            except CamundaBusinessException as e:
                log.warning(
                    error_code_message_mapper(ErrorCode.C8_JOB_WITH_ERROR, [job.job_type, job.job_key, e])
                )
                self._handle_job_throws_error(job, e)
                continue
            except ServiceException as e:
                log.error(e.get_log_formatted_message())
                self._handle_job_failed(job, e)
                continue
            except Exception as e:
                log.error(f"An error occurred while processing job of type {job.job_type}: {e}")
                self._handle_job_failed(job, e)
                continue

            try:
                if isinstance(result, JsonBaseModel):
                    result = result.model_dump()
                complete_job(job, variables=result or {})
                log.info(f"Successfully completed job with key {job.job_key} of type {job.job_type}.")
            except ServiceException as e:
                log.error(e.get_log_formatted_message())
            except Exception as e:
                log.error(
                    f"An error occurred while completing job of type {job.job_type}: {e}"
                )

    def _activate_jobs(self, job_type, job_request: JobWorkerRequest) -> list[ActivatedJob]:
        """Fetches jobs for a given job_type and processes them."""
        # Ensure token is valid before making request
        if not AuthenticationManager().is_healthy():
            log.error("Cannot fetch jobs: Access token is invalid or could not be refreshed.")
            time.sleep(5)  # Wait before retrying token refresh
            return []

        log.debug(f"Worker '{get_config().api.job.worker}' polling for jobs of type '{job_type}'")
        job_conf = get_config().api.job
        job_request = ActivateJobRequest(
            type=job_type,
            worker=job_request.worker or job_conf.worker,
            maxJobsToActivate=job_request.max_jobs_to_activate or job_conf.max_jobs_to_activate,
            timeout=job_request.timeout or job_conf.timeout,
            requestTimeout=job_request.request_timeout or job_conf.request_timeout,
            fetchVariable=job_request.fetch_variables,
            tenantIds=job_request.tenant_ids or job_conf.tenant_ids
        )
        try:
            jobs_response = activate_jobs(
                job_type=job_type,
                request=job_request
            )
            if not jobs_response or len(jobs_response.jobs) == 0:
                log.debug(f"No jobs of type {job_type} available")
                return []

            log.info(f"Fetched {len(jobs_response.jobs)} jobs of type {job_type}")
            return jobs_response.jobs

        except ServiceException as e:
            log.error(e.get_log_formatted_message())
            return []

    def _worker_loop(self, job_worker: JobWorker, stop_event):
        """The main loop for a single job worker."""
        while not stop_event.is_set():
            active_jobs = self._activate_jobs(job_worker.job_type, job_worker.request)
            self._process_jobs(active_jobs, handler_func=job_worker.handler)
            stop_event.wait((job_worker.polling_interval or get_config().api.job.polling_interval) / 1000.0)

    def add_worker(self, job_worker: JobWorker):
        with self._job_type_worker_lock:
            if job_worker.job_type in self._job_type_and_worker:
                log.warning(
                    f"Job type '{job_worker.job_type}' already has a handler registered. Overwriting job worker."
                )
            self._job_type_and_worker[job_worker.job_type] = job_worker

    def start_workers(self):
        """Starts all registered Camunda workers in separate threads."""
        if get_c8_api_headers() is None:
            log.critical("Cannot start workers: Initial access token not obtained. Please check settings and network.")
            return

        if not self._job_type_and_worker:
            log.warning("No Camunda worker functions registered using @camunda_worker decorator.")
            return

        log.info("Starting Camunda worker threads...")
        self._stop_event.clear()  # Clear event to allow workers to run if previously stopped
        self._worker_threads.clear()  # Clear any previous thread references

        for job_type, job_worker in self._job_type_and_worker.items():
            thread = threading.Thread(
                target=self._worker_loop,
                args=(job_worker, self._stop_event),
                name=f"camunda-worker-{job_type}",
            )
            thread.daemon = (
                True  # Allow main program to exit even if threads are running
            )
            thread.start()
            self._worker_threads.append(thread)
            log.info(f"Worker thread for job type '{job_type}' started.")
        log.info(f"Launched {len(self._worker_threads)} threads for Camunda workers.")

    def stop_workers(self):
        """Signals all worker threads to stop and waits for them to finish."""
        if not self._worker_threads:
            log.info("No Camunda worker threads are running.")
            return

        log.info("Signaling Camunda worker threads to stop...")
        self._stop_event.set()  # Set the event to signal threads to exit their loops

        for thread in self._worker_threads:
            if thread.is_alive():
                log.info(f"Waiting for worker thread '{thread.name}' to finish...")
                thread.join(timeout=10)  # Wait up to 10 seconds for each thread
                if thread.is_alive():
                    log.warning(
                        f"Worker thread '{thread.name}' did not terminate cleanly."
                    )
        self._worker_threads.clear()
        log.info("All Camunda worker threads stopped.")


R = TypeVar('R', bound=JsonBaseModel)


def camunda_worker(job_type: str,
                   polling_interval: int = None,
                   worker: str = None,
                   timeout: int = None,
                   max_jobs_to_activate: int = None,
                   fetch_variables: list[str] = None,
                   request_timeout: int = None,
                   tenant_ids: list[str] = None,
                   ):
    """
    Decorator to mark a function as a Camunda 8 job worker.
    The decorated function will receive a ActivatedJob as its argument
    and should return a dictionary of variables to complete the job, or None.
    :param job_type: The type of the job defined in Camunda Modeler
    :param worker: (optional) the name of the worker activating the jobs, mostly used for logging purposes
    :param polling_interval:
    :param timeout: (optional) An activated job will not be activated again until the timeout (in ms) has been reached.
        Will use ``C8CoreConfig.job_lock_duration`` by default.
    :param fetch_variables: a list of variables to fetch as the job variables; if empty, all visible variables at the
        time of activation for the scope of the job will be returned
    :param max_jobs_to_activate: the maximum jobs to activate by this request
    :param request_timeout: The request will be completed when at least one job is activated or after the requestTimeout
        (in ms).
    :param tenant_ids: a list of IDs of tenants for which to activate jobs
    :return:

    """

    def decorator(func: Callable[[ActivatedJob], dict | R]):
        """

        :param func: Job handler
        :return: job response variables as dict or TypeVar('R', bound=JsonBaseModel)
        """
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        job_type_param = params[0]
        # Check parameter kind (ensure it's not *args or **kwargs)
        if job_type_param.kind not in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_ONLY,
        ):
            raise WorkerSignatureException(
                error_code=ErrorCode.C8_WORKER_SIG_FIRST_ARGUMENT_INVALID,
                parameters=[func.__name__, job_type, job_type_param.kind],
            )

        if job_type_param.annotation is inspect.Parameter.empty:
            log.warning(
                f"Worker function '{func.__name__}' for job type '{job_type}' "
                f"has no type hint for its 'job' parameter. Recommended to use 'ActivatedJob'."
            )
        elif job_type_param.annotation is not ActivatedJob:
            # Strictly enforce ActivatedJob here.
            raise WorkerSignatureException(
                error_code=ErrorCode.C8_WORKER_SIG_FIRST_ARGUMENT_NOT_JOB,
                parameters=[
                    func.__name__,
                    job_type,
                    (
                        job_type_param.annotation.__name__
                        if hasattr(job_type_param.annotation, "__name__")
                        else str(job_type_param.annotation)
                    ),
                ],
            )
        request = JobWorkerRequest(
            type=job_type,
            worker=worker,
            timeout=timeout,
            max_jobs_to_activate=max_jobs_to_activate,
            fetch_variables=fetch_variables,
            request_timeout=request_timeout,
            tenant_ids=tenant_ids
        )
        pending_worker = JobWorker(
            job_type=job_type,
            handler=func,
            polling_interval=polling_interval,
            request=request
        )

        _pending_camunda_workers.append(pending_worker)
        log.info(
            f"Worker function '{func.__name__}' collected for job type '{job_type}'."
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def register_workers():
    """
    Explicitly registers all workers that were previously decorated with @camunda_worker.
    This function should only be called *after* the application configuration
    (e.g., Camunda client details) has been properly initialized.
    """
    manager = CamundaWorkerManager()
    for job_worker in _pending_camunda_workers:
        manager.add_worker(job_worker)
        log.info(f"Worker '{job_worker.handler.__name__}' registered for job type '{job_worker.job_type}'.")
    _pending_camunda_workers.clear()


def add_job_worker(
        job_type: str,
        handler: Callable[[ActivatedJob], dict | R],
        polling_interval: int = None,
        worker: str = None,
        timeout: int = None,
        max_jobs_to_activate: int = None,
        fetch_variables: list[str] = None,
        request_timeout: int = None,
        tenant_ids: list[str] = None,

):
    sig = inspect.signature(handler)
    params = list(sig.parameters.values())
    if not params:
        log.warning(f"Worker function '{handler.__name__}' for job type '{job_type}' has no parameters.")
    if params[0].annotation is inspect.Parameter.empty:
        log.warning(
            f"Worker function '{handler.__name__}' for job type '{job_type}' "
            f"has no type hint for its 'job' parameter. Recommended to use 'ActivatedJob'."
        )
    elif params[0].annotation is not ActivatedJob:
        raise WorkerSignatureException(
            error_code=ErrorCode.C8_WORKER_SIG_FIRST_ARGUMENT_NOT_JOB,
            parameters=[
                handler.__name__,
                job_type,
                (
                    params[0].annotation.__name__
                    if hasattr(params[0].annotation, "__name__")
                    else str(params[0].annotation)
                ),
            ],
        )
    manager = CamundaWorkerManager()
    job_worker = JobWorker(
        job_type=job_type,
        handler=handler,
        polling_interval=polling_interval,
        request=JobWorkerRequest(
            type=job_type,
            worker=worker,
            timeout=timeout,
            max_jobs_to_activate=max_jobs_to_activate,
            fetch_variables=fetch_variables,
            request_timeout=request_timeout,
            tenant_ids=tenant_ids
        )
    )
    manager.add_worker(job_worker)
    log.info(f"Worker '{handler.__name__}' registered for job type '{job_worker.job_type}'.")


def start_camunda_workers():
    """Starts all registered Camunda workers."""
    log.info("Starting registered Camunda job workers...")
    manager = CamundaWorkerManager()
    manager.start_workers()


def stop_camunda_workers():
    """Stops all running Camunda workers."""
    log.info("Stopping all running Camunda job workers...")
    manager = CamundaWorkerManager()
    manager.stop_workers()


def clear():
    CamundaWorkerManager._instance = None
    _pending_camunda_workers.clear()
