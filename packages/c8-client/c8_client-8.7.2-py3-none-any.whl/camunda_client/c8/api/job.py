import json

import requests

from camunda_client.c8.auth import get_c8_api_headers
from camunda_client.c8.models import ActivatedJobResponse, JobFailedRequest, ActivatedJob, \
    ThrowErrorForJobRequest, ActivateJobRequest
from camunda_client.config import get_config
from camunda_client.error import CamundaBusinessException
from camunda_client.error import ServiceException, ErrorCode


def activate_jobs(
        job_type: str,
        worker: str = None,
        timeout: int = None,
        max_jobs_to_activate: int = 5,
        fetch_variables: list[str] = None,
        request_timeout: int = None,
        tenant_ids: list[str] = None,
        request: ActivateJobRequest = None

) -> ActivatedJobResponse:
    """
    Activates jobs for the provided job type using the 'POST /jobs/activation' endpoint.
    :param request: Overwrites all other parameters.
    :param tenant_ids: (optional) a list of IDs of tenants for which to activate jobs
    :param request_timeout: (optional)
    :param fetch_variables: (optional)
    :param max_jobs_to_activate: the maximum jobs to activate by this request
    :param timeout: a job returned after this call will not be activated by another call until the timeout (in ms) has
        been reached
    :param worker: (optional) the name of the worker activating the jobs, mostly used for logging purposes
    :param job_type: The job type, as defined in the BPMN process (e.g. <zeebe:taskDefinition type="payment-service" />)
    :raises ServiceException
    :return: ActivatedJobResponse which contains all activated jobs
    """
    if request is None:
        request = ActivateJobRequest(
            type=job_type,
            worker=worker or get_config().api.job.worker,
            timeout=timeout or get_config().api.job.timeout,
            maxJobsToActivate=max_jobs_to_activate or get_config().api.job.max_jobs_to_activate,
            fetchVariable=fetch_variables,
            requestTimeout=request_timeout,
            tenantIds=tenant_ids
        )

    url = f"{get_config().api.base_url}/v2/jobs/activation"
    try:
        response = requests.post(url, headers=get_c8_api_headers(), data=request.model_dump_json())
        response.raise_for_status()
        jobs = response.json()
        return ActivatedJobResponse.model_validate(jobs)
    except requests.exceptions.Timeout as e:
        return ActivatedJobResponse.model_validate({"jobs": []})
    except Exception as e:
        raise ServiceException(ErrorCode.C8_FAILED_TO_ACTIVATE_JOBS, parameters=[job_type, e])


def complete_job(job: ActivatedJob, variables: dict = None):
    """
    Complete the provided job using the 'POST /jobs/:jobKey/completion' endpoint
    :param job: The job to complete
    :param variables: The variables that should be sent as the result of the job
    :raises ServiceException
    :return:
    """

    if variables is None:
        variables = {}

    try:
        url = f"{get_config().api.base_url}/v2/jobs/{job.job_key}/completion"
        payload = {
            "variables": variables
        }
        response = requests.post(url, headers=get_c8_api_headers(), data=json.dumps(payload))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ServiceException(ErrorCode.C8_FAILED_TO_COMPLETE_JOB, parameters=[job.job_key, job.element_id, e])


def mark_job_as_failed(job: ActivatedJob, error_message: str, variables=None):
    """
    Marks the provided job as failed using the 'POST /jobs/:jobKey/failure' endpoint
    :param job: The job to mark as failed
    :param error_message: A error message to explain why the job failed
    :param variables: Additional variables
    :raises ServiceException
    :return:
    """
    if variables is None:
        variables = {}
    try:
        url = f"{get_config().api.base_url}/v2/jobs/{job.job_key}/failure"
        payload_data = {
            "retries": job.retries - 1 if job.retries - 1 > 0 else 0,
            "errorMessage": error_message,
            "variables": variables
        }
        payload = JobFailedRequest(**payload_data).model_dump_json()
        response = requests.post(url, headers=get_c8_api_headers(), data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ServiceException(ErrorCode.C8_FAILED_TO_MARK_JOB_AS_FAILED, parameters=[job.job_type, job.job_key, e])


def throw_error_for_job(job: ActivatedJob, error: CamundaBusinessException):
    """
    Throws an error for the job if a business (non-technical) error occurs using the 'POST /jobs/:jobKey/error' endpoint
    :param job: the job to throw the error for
    :param error: CamundaBusinessException that captures the occurred error
    :raises ServiceException
    :return:
    """
    try:
        url = f"{get_config().api.base_url}/v2/jobs/{job.job_key}/error"
        payload_data = {
            "errorMessage": error.error_message,
            "errorCode": error.error_code,
            "variables": error.variables
        }
        payload = ThrowErrorForJobRequest(**payload_data).model_dump_json()
        response = requests.post(url, headers=get_c8_api_headers(), data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ServiceException(ErrorCode.C8_FAILED_TO_THROW_JOB_ERROR, parameters=[job.job_type, job.job_key, e])
