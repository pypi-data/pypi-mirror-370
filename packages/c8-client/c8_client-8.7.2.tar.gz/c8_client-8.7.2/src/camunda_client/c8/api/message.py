import requests

from camunda_client.c8.auth import get_c8_api_headers
from camunda_client.c8.models import PublishMessageResponse
from camunda_client.c8.models.message import (
    PublishMessageRequest,
    CorrelateMessageRequest,
    CorrelateMessageResponse,
)
from camunda_client.config import get_config
from camunda_client.error import ServiceException, ErrorCode


def publish_message(request: PublishMessageRequest) -> PublishMessageResponse:
    """
    Publishes a single message. Messages are published to specific partitions computed from their correlation keys. The
    endpoint does not wait for a correlation result. Use the message correlation endpoint for such use cases.

    Calls '/v2/messages/publication'

    :param request: PublishMessageRequest
    :raises ServiceException
    :return: PublishMessageResponse
    """
    try:
        url = f"{get_config().api.base_url}/v2/messages/publication"
        response = requests.post(
            url,
            headers=get_c8_api_headers(),
            data=request.model_dump_json(),
        )
        response.raise_for_status()
        return PublishMessageResponse.model_validate(response.json())
    except Exception as e:
        raise ServiceException(ErrorCode.C8_FAILED_TO_PUBLISH_MESSAGE, parameters=[e])


def correlate_message(request: CorrelateMessageRequest) -> CorrelateMessageResponse:
    """
    Publishes a message and correlates it to a subscription. If correlation is successful it will return the first
    process instance key the message correlated with.

    Correlate '/v2/messages/correlation'

    :param request: CorrelateMessageRequest
    :raises ServiceException
    :return: CorrelateMessageResponse
    """

    try:
        url = f"{get_config().api.base_url}/v2/messages/correlation"
        response = requests.post(
            url,
            headers=get_c8_api_headers(),
            data=request.model_dump_json(),
        )
        response.raise_for_status()
        return CorrelateMessageResponse.model_validate(response.json())
    except Exception as e:
        raise ServiceException(ErrorCode.C8_FAILED_TO_CORRELATE_MESSAGE, parameters=[e])
