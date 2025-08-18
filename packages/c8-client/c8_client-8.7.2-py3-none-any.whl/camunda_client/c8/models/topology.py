from pydantic import Field

from camunda_client.utils import JsonBaseModel


class Partition(JsonBaseModel):
    """
    Representation of a partition as it is returned as part of the cluster topology.
    
    Attributes
    ----------
    partition_id : int
        The unique ID of this partition.
    role : str
        Describes the Raft role of the broker for a given partition.
    health : str
        Describes the current health of the partition.
    """
    partition_id: int = Field(..., alias="partitionId",
                              description="The unique ID of this partition.")
    role: str = Field(..., alias="role",
                      description="Describes the Raft role of the broker for a given partition.")
    health: str = Field(..., alias="health",
                        description="Describes the current health of the partition.")


class Broker(JsonBaseModel):
    """
    Representation of a broker as it is returned as part of the cluster topology.

    Attributes
    ----------
    node_id : int
        The unique (within a cluster) node ID for the broker.
    host : str
        The hostname for reaching the broker.
    port : int
        The port for reaching the broker.
    partitions : list[Partition]
        A list of partitions managed or replicated on this broker.
    version : str
        The broker version.
    """

    node_id: int = Field(..., alias="nodeId",
                         description="The unique (within a cluster) node ID for the broker.")
    host: str = Field(..., alias="host",
                      description="The hostname for reaching the broker.")
    port: int = Field(..., alias="port",
                      description="The port for reaching the broker.")
    partitions: list[Partition] = Field(..., alias="partitions",
                                        description="A list of partitions managed or replicated on this broker.")
    version: str = Field(..., alias="version",
                         description="The broker version.")


class ClusterTopology(JsonBaseModel):
    """
    Representation of the cluster topoloy information that is returned by the 'GET /v2/topology' endpoint.

     Attributes
    ----------
    brokers : list[Broker]
        A list of brokers that are part of this cluster.
    cluster_size : int
        The number of brokers in the cluster.
    partitions_count : int
        The number of partitions that are spread across the cluster.
    replication_factor : int
        The configured replication factor for this cluster.
    gateway_version : str
        The version of the Zeebe Gateway.
    """
    brokers: list[Broker] = Field(..., alias="brokers",
                                  description="A list of brokers that are part of this cluster.")
    cluster_size: int = Field(..., alias="clusterSize",
                              description="The number of brokers in the cluster.")
    partitions_count: int = Field(..., alias="partitionsCount",
                                  description="The number of partitions are spread across the cluster.")
    replication_factor: int = Field(..., alias="replicationFactor",
                                    description="The configured replication factor for this cluster.")
    gateway_version: str = Field(..., alias="gatewayVersion",
                                 description="The version of the Zeebe Gateway.")
