from pydantic import Field

from camunda_client.utils.base_model import JsonBaseModel


class BroadcastSignalResponse(JsonBaseModel):
    """
    Representation of the response returned after broadcasting a signal.

    Attributes
    ----------
    tenant_id : str
        The tenant ID of the signal that was broadcast.
    signal_key : str
        The unique ID of the signal that was broadcast.
    """

    tenant_id: str = Field(
        ...,
        alias="tenantId",
        description="The tenant ID of the signal that was broadcast.",
    )
    signal_key: str = Field(
        ...,
        alias="signalKey",
        description="The unique ID of the signal that was broadcast.",
    )


class BroadcastSignalRequest(JsonBaseModel):
    """
    Representation of a broadcast signal request.

    Attributes
    ----------
    signal_name : str
        The name of the signal to broadcast.
    variables : dict | None
        The signal variables as a JSON object.
    tenant_id : str | None
        The ID of the tenant that owns the signal.
    """
    signal_name: str = Field(
        ..., alias="signalName", description="The name of the signal to broadcast."
    )
    variables: dict | None = Field(
        default=None,
        alias="variables",
        description="The signal variables as a JSON object",
    )
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="The ID of the tenant that owns the signal.",
    )
