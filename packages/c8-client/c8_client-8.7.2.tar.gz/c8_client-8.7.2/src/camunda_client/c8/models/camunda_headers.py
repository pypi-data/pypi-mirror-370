from pydantic import Field, field_validator

from camunda_client.utils.base_model import JsonBaseModel


class C8ApiHeaders(JsonBaseModel):
    """
    Representation of the required Camunda 8 API headers.

    Attributes
    ----------
    auth_token : str
        Authorization token, must start with ``Bearer ``. (alias: ``Authorization``)
    content_type : str
        The MIME type of the request body. Defaults to ``application/json``. (alias: ``Content-Type``)
    """

    auth_token: str = Field(
        ..., alias="Authorization", description="Authorization token, must start with 'Bearer '",
    )
    content_type: str = Field(
        default="application/json", alias="Content-Type"
    )

    @field_validator("auth_token")
    def validate_bearer_prefix(cls, auth_token: str) -> str:
        if not auth_token.startswith("Bearer "):
            raise ValueError(
                "Authorization token must start with 'Bearer ' (e.g., 'Bearer your_token_here')."
            )
        return auth_token
