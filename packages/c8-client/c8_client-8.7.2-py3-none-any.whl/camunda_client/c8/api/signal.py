import requests

from camunda_client.c8.auth import get_c8_api_headers
from camunda_client.c8.models.signal import (
    BroadcastSignalRequest,
    BroadcastSignalResponse,
)
from camunda_client.config import get_config
from camunda_client.error import ServiceException, ErrorCode


def broadcast_signal(request: BroadcastSignalRequest) -> BroadcastSignalResponse:
    """
    Broadcasts a signal.

    Calls '/v2/signals/broadcast'

    :param request:
    :return:
    """

    try:
        url = f"{get_config().api.base_url}/v2/signals/broadcast"
        response = requests.post(
            url,
            headers=get_c8_api_headers(),
            data=request.model_dump_json(),
        )
        response.raise_for_status()
        return BroadcastSignalResponse.model_validate(response.json())
    except Exception as e:
        raise ServiceException(ErrorCode.C8_FAILED_TO_BROADCAST_SIGNAL, parameters=[e])
