import requests

from camunda_client.c8.auth import get_c8_api_headers
from camunda_client.c8.models.topology import ClusterTopology
from camunda_client.config.lib_config import get_config
from camunda_client.error.error_code import ErrorCode
from camunda_client.error.service_exception import ServiceException


def get_cluster_topology() -> ClusterTopology:
    """Retrieves the cluster topology from the 'GET /topology' endpoint."""

    url = f"{get_config().api.base_url}/v2/topology"
    try:
        response = requests.get(url, headers=get_c8_api_headers())
        response.raise_for_status()
        return ClusterTopology.model_validate(response.json())
    except requests.exceptions.RequestException as e:
        raise ServiceException(ErrorCode.C8_GET_CLUSTER_TOPOLOGY_FAILED, parameters=[e])
