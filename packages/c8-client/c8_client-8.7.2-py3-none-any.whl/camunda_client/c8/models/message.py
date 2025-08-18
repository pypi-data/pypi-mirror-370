from pydantic import Field

from camunda_client.utils import JsonBaseModel


class PublishMessageResponse(JsonBaseModel):
    """
    Response returned after publishing a message.

    Attributes
    ----------
    tenant_id : str
        The tenant ID of the message.
    message_key : str
        The key of the message.
    """
    tenant_id: str = Field(
        ..., alias="tenantId", description="The tenant ID of the message."
    )
    message_key: str = Field(
        ..., alias="messageKey", description="The key of the message."
    )


class PublishMessageRequest(JsonBaseModel):
    """
    Request model to publish a message.

    Attributes
    ----------
    name : str
        The name of the message.
    correlation_key : str
        The correlation key of the message.
    time_to_live : int
        Timespan (in ms) to buffer the message on the broker.
    message_id : str or None
        The unique ID of the message. Ensures only one message with this ID will be published during its lifetime.
    variables : dict or None
        The message variables as a JSON document.
    tenant_id : str or None
        The tenant of the message sender.
    """
    name: str = Field(..., alias="name", description="The name of the message.")
    correlation_key: str = Field(
        default="",
        alias="correlationKey",
        description="The correlation key of the message.",
    )
    time_to_live: int = Field(
        default=0,
        alias="timeToLive",
        description="Timespan (in ms) to buffer the message on the broker.",
    )
    message_id: str | None = Field(
        default=None,
        alias="messageId",
        description="The unique ID of the message. Only useful to ensure only one message with the given ID will ever "
                    "be published (during its lifetime).",
    )
    variables: dict | None = Field(
        default=None,
        alias="variables",
        description="The message variables as JSON document.",
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="The tenant of the message sender."
    )


class CorrelateMessageResponse(JsonBaseModel):
    """
    Response model for a correlated message.

    Attributes
    ----------
    tenant_id : str
        The tenant ID of the correlated message.
    message_key : str
        The key of the correlated message.
    process_instance_key : str
        The key of the first process instance the message correlated with.
    """
    tenant_id: str = Field(
        ..., alias="tenantId", description="The tenant ID of the correlated message"
    )
    message_key: str = Field(
        ..., alias="messageKey", description="The key of the correlated message"
    )
    process_instance_key: str = Field(
        ...,
        alias="processInstanceKey",
        description="The key of the first process instance the message correlated with",
    )


class CorrelateMessageRequest(JsonBaseModel):
    """
    Request model to correlate a message to a process instance.

    Attributes
    ----------
    name : str
        The message name as defined in the BPMN process.
    correlation_key : str
        The correlation key of the message.
    variables : dict or None
        The message variables as a JSON document.
    tenant_id : str
        The tenant for which the message is published.
    """
    name: str = Field(
        ..., alias="name", description="The message name as defined in the BPMN process"
    )
    correlation_key: str = Field(
        default="",
        alias="correlationKey",
        description="The correlation key of the message",
    )
    variables: dict | None = Field(
        default=None,
        alias="variables",
        description="The message variables as JSON document",
    )
    tenant_id: str = Field(
        ...,
        alias="tenantId",
        description="the tenant for which the message is published",
    )
