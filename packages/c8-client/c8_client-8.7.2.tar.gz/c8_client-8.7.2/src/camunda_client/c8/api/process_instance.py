import requests

from camunda_client.c8.auth import get_c8_api_headers
from camunda_client.c8.models import (
    CreateProcessInstanceResponse,
    CreateProcessInstanceRequest,
)
from camunda_client.c8.models.process_instance import (
    MigrateProcessInstanceRequest,
    ModifyProcessInstanceRequest,
)
from camunda_client.config import get_config
from camunda_client.error import ServiceException, ErrorCode


def create_process_instance(
        request: CreateProcessInstanceRequest,
) -> CreateProcessInstanceResponse:
    """
    Creates and starts an instance of the specified process. The process definition to use to create the instance can be
    specified either using its unique key (as returned by Deploy resources), or using the BPMN process ID and a version.

    Waits for the completion of the process instance before returning a result when awaitCompletion is enabled.

    Calls '/v2/process-instances'
    :param request: CreateProcessInstanceRequest
    :raises ServiceException
    :return: CreateProcessInstanceResponse
    """
    try:
        url = f"{get_config().api.base_url}/v2/process-instances"
        response = requests.post(
            url=url,
            headers=get_c8_api_headers(),
            data=request.model_dump_json(),
        )
        response.raise_for_status()
        return CreateProcessInstanceResponse.model_validate(response.json())
    except Exception as e:
        raise ServiceException(
            ErrorCode.C8_FAILED_TO_CREATE_PROCESS_INSTANCE, parameters=[e]
        )


def cancel_process_instance(process_instance_key: str, operation_reference: int = None):
    """
    Cancels a running process instance.

    Calls '/v2/process-instances/:processInstanceKey/cancellation'
    :param process_instance_key: The key of the process instance to cancel.
    :param operation_reference: A reference key chosen by the user that will be part of all records resulting from
        this operation. Must be > 0 if provided.
    :raises ServiceException
    :return:
    """
    body = (
        {"operationReference": operation_reference}
        if operation_reference is not None
        else None
    )
    try:
        url = f"{get_config().api.base_url}/v2/process-instances/{process_instance_key}/cancellation"
        response = requests.post(url=url, headers=get_c8_api_headers(), data=body)
        response.raise_for_status()
    except Exception as e:
        raise ServiceException(
            ErrorCode.C8_FAILED_TO_CANCEL_PROCESS_INSTANCE,
            parameters=[process_instance_key, e],
        )


def migrate_process_instance(
        process_instance_key: str, request: MigrateProcessInstanceRequest
):
    """
    Migrates a process instance to a new process definition. This request can contain multiple mapping instructions to
    define mapping between the active process instance's elements and target process definition elements.

    Use this to upgrade a process instance to a new version of a process or to a different process definition, e.g. to
    keep your running instances up-to-date with the latest process improvements.

    Calls '/v2/process-instances/:processInstanceKey/migration'

    :param process_instance_key: The key of the process instance that should be migrated.
    :param request: MigrateProcessInstanceRequest
    :raises ServiceException

    :return:
    """
    try:
        url = f"{get_config().api.base_url}/v2/process-instances/{process_instance_key}/migration"
        response = requests.post(
            url,
            headers=get_c8_api_headers(),
            data=request.model_dump_json(),
        )
        response.raise_for_status()
    except Exception as e:
        raise ServiceException(
            ErrorCode.C8_FAILED_TO_MIGRATE_PROCESS_INSTANCE,
            parameters=[process_instance_key, e],
        )


def modify_process_instance(
        process_instance_key: str, request: ModifyProcessInstanceRequest
):
    """
    Modifies a running process instance. This request can contain multiple instructions to activate an element of the
    process or to terminate an active instance of an element.

    Use this to repair a process instance that is stuck on an element or took an unintended path. For example, because
    an external system is not available or doesn't respond as expected.

    Calls '/v2/process-instances/:processInstanceKey/modification'

    :param process_instance_key: The key of the process instance that should be modified.
    :param request: ModifyProcessInstanceRequest
    :raises ServiceException
    :return:
    """

    try:
        url = f"{get_config().api.base_url}/v2/process-instances/{process_instance_key}/modification"
        response = requests.post(
            url,
            headers=get_c8_api_headers(),
            data=request.model_dump_json(),
        )
        response.raise_for_status()
    except Exception as e:
        raise ServiceException(
            ErrorCode.C8_FAILED_TO_MODIFY_PROCESS_INSTANCE,
            parameters=[process_instance_key, e],
        )
