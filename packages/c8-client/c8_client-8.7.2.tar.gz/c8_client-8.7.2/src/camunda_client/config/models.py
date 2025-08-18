import logging
import os

from pydantic import Field, ValidationError, field_validator, model_validator

from camunda_client.utils import JsonBaseModel

log = logging.getLogger(__name__)


class JobConfig(JsonBaseModel):
    """
    Configuration settings for job workers in Camunda 8.

    Attributes
    ----------
    polling_interval : int
        Polling interval for activating jobs in milliseconds.
    worker : str
        The name of the worker activating the jobs, mostly used for logging purposes.
    timeout : int
        A job returned after this call will not be activated by another call until the timeout (in ms) has been reached.
    max_jobs_to_activate : int
        Maximum number of jobs to activate in one request.
    request_timeout : int or None
        The request will be completed when at least one job is activated or after the requestTimeout (in ms).
    tenant_ids : list of str or None
        A list of IDs of tenants for which to activate jobs.
    """
    polling_interval: int = Field(
        default=5000, alias="pollingInterval",
        description="Polling interval for activating jobs in ms")
    worker: str = Field(
        default="camunda-8-client-worker", alias="worker",
        description="The name of the worker activating the jobs, mostly used for logging purposes")
    timeout: int = Field(
        default=10000, alias="timeout",
        description="A job returned after this call will not be activated by another call until the timeout (in ms) "
                    "has been reached")
    max_jobs_to_activate: int = Field(default=5, alias="maxJobsToActivate")
    request_timeout: int | None = Field(
        default=None, alias="requestTimeout",
        description="The request will be completed when at least one job is activated or after the requestTimeout (in ms).")
    tenant_ids: list[str] | None = Field(default=None, alias="tenantIds",
                                         description="A list of IDs of tenants for which to activate jobs")


class ApiConfig(JsonBaseModel):
    """
    Configuration for the Camunda 8 API client.

    Attributes
    ----------
    base_url : str
        Base URL of the Camunda 8 REST API.
    job : JobConfig
        Global configuration for all job workers.
    """
    base_url: str = Field(..., alias="baseUrl", description="Base URL of the Camunda 8 REST API")
    job: JobConfig = Field(default=JobConfig(), description="Global configuration for all job worker")


class SelfManagedAuthConfig(JsonBaseModel):
    """
    Configuration for self-managed Camunda 8 authentication using OIDC.

    Attributes
    ----------
    oidc_token_url : str
        The URL of the token endpoint of the OIDC Identity Provider used by Camunda.
    client_id : str
        OIDC Client ID to use when retrieving an access token for Camunda.
    client_secret : str
        OIDC Client Secret to use when retrieving an access token for Camunda.
    """
    oidc_token_url: str = Field(..., alias="oidcTokenUrl",
                                description="The URL of the token endpoint of the OIDC Identity Provider used by Camunda")
    client_id: str = Field(..., alias="clientId",
                           description="OIDC Client ID to use when retrieving an access token for Camunda")
    client_secret: str = Field(..., alias="clientSecret",
                               description="OIDC Client Secret to use when retrieving an access token for Camunda")


class SaasAuthConfig(JsonBaseModel):
    """
    Authentication configuration for SaaS Camunda 8 instances.

    Attributes
    ----------
    client_id : str
        Client ID.
    client_secret : str
        Client Secret.
    authorization_server_url : str
        Authorization Server URL. Defaults to "https://login.cloud.camunda.io/oauth/token".
    audience : str
        Audience. Defaults to "zeebe.camunda.io".
    """
    client_id: str = Field(..., alias="clientId", description="Client ID")
    client_secret: str = Field(..., alias="clientSecret", description="Client Secret")
    authorization_server_url: str = Field(default="https://login.cloud.camunda.io/oauth/token",
                                          alias="authorizationServerUrl", description="Authorization Server URL")
    audience: str = Field(default="zeebe.camunda.io", alias="audience", description="Audience")

    @field_validator("audience", mode="before")
    def use_default_audience_if_none(cls, audience):
        """
        Sets 'zeebe.camunda.io' as default ``audience`` if configured audience is ``None``.
        """
        return audience if audience is not None else "zeebe.camunda.io"

    @field_validator("authorization_server_url", mode="before")
    def use_default_auth_url_if_none(cls, v):
        """
        Sets 'https://login.cloud.camunda.io/oauth/token' as default ``authorization_server_url`` if configured
        authorization_server_url is ``None``.
        """
        return v if v is not None else "https://login.cloud.camunda.io/oauth/token"


class AuthConfig(JsonBaseModel):
    """
    Authentication configuration for different Camunda 8 deployment types.

    Attributes
    ----------
    self_managed : SelfManagedAuthConfig | None
        Authentication configuration for self-managed Camunda 8 instances.
    saas : SaasAuthConfig | None
        Authentication configuration for SaaS Camunda 8 instances.
    """

    self_managed: SelfManagedAuthConfig | None = Field(
        default=None, alias="selfManaged",
        description="Authentication configuration for self-managed Camunda 8 deployments")
    saas: SaasAuthConfig | None = Field(
        default=None, alias="saas",
        description="Authentication configuration for SaaS Camunda 8 deployments")

    def get_url(self) -> str:
        """
        Returns the authorization server URL depending on whether the config is for SaaS or self-managed.
        :return: Authorization server URL
        """
        if self.saas is not None:
            return self.saas.authorization_server_url
        return self.self_managed.oidc_token_url

    def get_request_data(self) -> dict[str, str]:
        """
        Returns the authentication request payload based on the configuration type.
        :return: Authentication request payload as dict[str, str]
        """
        if self.saas is not None:
            return {
                "grant_type": "client_credentials",
                "audience": self.saas.audience,
                "client_id": self.saas.client_id,
                "client_secret": self.saas.client_secret
            }
        return {
            "client_id": self.self_managed.client_id,
            "client_secret": self.self_managed.client_secret,
            "grant_type": "client_credentials",
        }

    @model_validator(mode="after")
    def validate(self):
        """
        Validates that only one of self_managed or saas is configured. If none are configured, tries to create one from
        environment variables. Raises ValidationError if invalid.
        """
        if self.self_managed is not None and self.saas is not None:
            raise ValidationError("Cannot configure self managed and SaaS Camunda instance at the same time.")
        if self.self_managed is not None and self.saas is None:
            log.info("Use config for self managed Camunda instance.")
            return self
        if self.self_managed is None and self.saas is not None:
            log.info("Use config for SaaS Camunda instance.")
            return self
        log.debug("No auth configuration provided; try to create auth config based on Zeebe environment variables")
        client_id, client_secret, auth_server_url, audience = os.getenv("ZEEBE_CLIENT_ID"), os.getenv(
            "ZEEBE_CLIENT_SECRET"), os.getenv("ZEEBE_AUTHORIZATION_SERVER_URL"), os.getenv("ZEEBE_TOKEN_AUDIENCE")
        if client_id is not None and client_secret is not None:
            self.saas = SaasAuthConfig(
                clientId=client_id,
                clientSecret=client_secret,
                authorizationServerUrl=auth_server_url,
                audience=audience
            )
            log.info("Use config for SaaS Camunda instance from environment variables.")
            return self

        client_id, client_secret, token_url = os.getenv("OIDC_CLIENT_ID"), os.getenv("OIDC_CLIENT_SECRET"), os.getenv(
            "OIDC_TOKEN_URL")
        if client_id is None or client_secret is None:
            log.error("Cannot initialize SaaS or self-managed auth configuration from environment variables.")
            raise ValidationError("Cannot create SaaS or self-managed authentication configuration.")
        return self
