# `c8-client` Python Library

## License

This project is licensed under the Apache License 2.0 with the Commons Clause restriction.

- ✅ You may use this library in commercial or private projects.
- ✅ You may modify, distribute, and embed it in your own products.
- ❌ You may **not** sell this library as a standalone product or offer it as a paid hosted service.
- ❌ You may **not** create a product whose primary value comes from this library's functionality and sell it.

See [LICENSE](LICENSE) for full details.

## `camunda_client.c8` Camunda 8 Module

Contains Camunda 8 (C8) API related features to handle jobs

### `camunda_client.c8.models`

Contains C8 API related request and response data transfer object classes to structure data used for
communication with the C8 API.

All models are based on a custom implementation `camunda_client.utils.JsonBaseModel` based on `pydantic.BaseModel`

### `camunda_client.c8.api`

Contains functions to request Camunda 8 API endpoints.

#### Included API Endpoints:

__Job API:__

1. [Activate Jobs](https://docs.camunda.io/docs/8.7/apis-tools/camunda-api-rest/camunda-api-rest-overview/)
   `camunda_client.c8.api.activate_jobs`
2. [Complete Job](https://docs.camunda.io/docs/8.7/apis-tools/camunda-api-rest/camunda-api-rest-overview/)
   `camunda_client.c8.api.complete_job`
3. [Mark Job as Failed](https://docs.camunda.io/docs/8.7/apis-tools/camunda-api-rest/camunda-api-rest-overview/)
   `camunda_client.c8.api.mark_job_as_failed`
4. [Throw Error for Job](https://docs.camunda.io/docs/8.7/apis-tools/camunda-api-rest/camunda-api-rest-overview/)
   `camunda_client.c8.api.throw_error_for_job`

__Process Instance API:__

1. [Create process instance](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/specifications/create-process-instance/)
   `camunda_client.c8.api.create_process_instance`
2. [Cancel process instance](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/specifications/cancel-process-instance/)
   `camunda_client.c8.api.cancel_process_instance`
3. [Migrate process instance](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/specifications/migrate-process-instance/)
   `camunda_client.c8.api.migrate_process_instance`
4. [Modify process instance](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/specifications/modify-process-instance/)
   `camunda_client.c8.api.modify_process_instance`

__Message API:__

1. [Publish a message](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/specifications/publish-a-message/)
   `camunda_client.c8.api.publish_message`
2. [Correlate a message](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/specifications/correlate-a-message/)
   `camunda_client.c8.api.correlate_message`

__Signal API:__

1. [Broadcast signal](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/specifications/broadcast-signal/)
   `camunda_client.c8.api.broadcast_signal`

__Authentication API:__

1. [Generate a Token](https://docs.camunda.io/docs/apis-tools/camunda-api-rest/camunda-api-rest-authentication/)
   `camunda_client.c8.auth.get_token`

### `camunda_client.c8.worker`

Camunda job worker can be defined by decorating a worker function with `@camunda_worker` and passing the job type:

```python
# app.py
from camunda_client.c8.models import ActivatedJob
from camunda_client.c8.worker import camunda_worker


@camunda_worker(job_type="a-camunda-job-type")
def a_camunda_job_worker(job: ActivatedJob) -> dict:
    job_variables = job.variables
    # Worker processes...
    return {
        "output": "some output for the next task"
    }


```

To keep the application alive and to activate jobs for each registered `@camunda_worker`, a main application loop should
be implemented:

```python
# app.py
import time
import logging
import os

from dotenv import load_dotenv

import camunda_client.config as config
from camunda_client.c8.models import ActivatedJob
from camunda_client.c8.worker import (
    start_camunda_workers,
    stop_camunda_workers,
    camunda_worker,
    register_workers
)

log = logging.getLogger(__name__)


@camunda_worker(job_type="a-camunda-job-type")
def a_camunda_job_worker(job: ActivatedJob) -> dict:
    job_variables = job.variables
    # Worker processes...
    return {
        "output": "some output for the next task"
    }


def configure():
    load_dotenv()
    config.initialize_config(
        config=config.C8Config(
            auth=config.AuthConfig(
                selfManaged=config.SelfManagedAuthConfig(
                    clientId=os.getenv("CAMUNDA_CLIENT_ID"),
                    clientSecret=os.getenv("CAMUNDA_CLIENT_SECRET"),
                    oidcTokenUrl=os.getenv("CAMUNDA_TOKEN_URL")
                )
            ),
            api=config.ApiConfig(
                baseUrl=os.getenv("CAMUNDA_API_BASE_URL"),
                job=config.JobConfig(
                    worker="c8-example-worker",
                    timeout=5000,
                )
            )
        )
    )


def application_loop():
    """
    Primary application loop that starts the Camunda job workers and busy-waits
    until a Keyboard interruption (Ctrl+C) is received or an exception occurs.
    Then, it stops the workers and the server.
    """
    try:
        register_workers()
        start_camunda_workers()
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        log.info("Ctrl+C detected. Stopping application gracefully.")
    except Exception as e:
        log.critical(
            f"An unhandled exception occurred in the main application loop: {e}",
            exc_info=True,
        )
    finally:
        stop_camunda_workers()
        log.info("Application stopped.")

```

## `camunda_client.error` Error Module

Contains `camunda_client` specific exceptions:

`CamundaBusinessException`: Can be thrown on business error in a `@camunda_worker` decorated function. Will cause a call
to the Camunda 8 API 'Throw Error for Job' endpoint.

`ServiceException`: Will be thrown on technical errors (e.g. Camunda 8 API is not reachable). The activated job will be
marked as failed.

`SignatureException`: Is thrown on initialization errors for `@camunda_worker` (e.g. decorated function does not accept
`ActivatedJob` as parameter)

## `camunda_client.config` Configuration Module

Handles the configuration for the `camunda_client` library.
On application start, the configuration must be passed:

```python
import camunda_client.config as config
import os

config.initialize_config(
    config=config.C8Config(
        auth=config.AuthConfig(
            selfManaged=config.SelfManagedAuthConfig(
                clientId=os.getenv("CAMUNDA_CLIENT_ID"),
                clientSecret=os.getenv("CAMUNDA_CLIENT_SECRET"),
                oidcTokenUrl=os.getenv("CAMUNDA_TOKEN_URL")
            )
        ),
        api=config.ApiConfig(
            baseUrl=os.getenv("CAMUNDA_API_BASE_URL"),
            job=config.JobConfig(
                worker="c8-example-worker",
                timeout=5000,
            )
        )
    )
)
```

