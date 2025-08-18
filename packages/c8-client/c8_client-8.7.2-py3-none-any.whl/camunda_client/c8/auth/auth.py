import threading
from datetime import datetime, timedelta

import requests

from camunda_client.c8.models.camunda_headers import C8ApiHeaders
from camunda_client.config import get_config
from camunda_client.error import ServiceException, ErrorCode
from camunda_client.log import get_logger

log = get_logger(__name__)


class AuthenticationManager:
    """
    Authentication Manager to request and refresh Camunda 8 API Open ID JWT tokens.

    Provides Camunda 8 API HTTP headers.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AuthenticationManager, cls).__new__(cls)
                    cls._instance._initialize_client_state()
        return cls._instance

    def is_healthy(self):
        return self._refresh_token()

    def _initialize_client_state(self):
        self._access_token = None
        self._token_expires_at = datetime.min
        self._camunda_headers: C8ApiHeaders | None = None

    def _refresh_token(self):
        """Fetches a new access token if needed."""
        if self._access_token and datetime.now() < self._token_expires_at:
            return True  # Token is still valid

        log.debug("Attempting to refresh Camunda access token...")

        try:
            self._access_token, expires_in = get_token()

            # Set expiry slightly before actual expiry to avoid race conditions
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            if self._access_token:
                # noinspection PyArgumentList
                self._camunda_headers = C8ApiHeaders(
                    auth_token=f"Bearer {self._access_token}",
                    content_type="application/json",
                )
                log.debug("Camunda access token refreshed successfully.")
                return True
            else:
                log.error("Access token not found in response.")
                self._camunda_headers = None
                return False
        except Exception as e:
            log.error(f"Failed to get Camunda access token: {e}", exc_info=True)
            self._access_token = None
            self._token_expires_at = datetime.min
            self._camunda_headers = None
            return False

    def get_c8_api_headers(self) -> dict | None:
        if not self._refresh_token():
            raise ServiceException(
                ErrorCode.C8_AUTH_GET_TOKEN_FAILED,
                parameters=[
                    "Refresh access token failed; cannot create Camunda headers."
                ],
            )
        return self._camunda_headers.model_dump()


def get_c8_api_headers() -> dict | None:
    try:
        return AuthenticationManager().get_c8_api_headers()
    except ServiceException as e:
        log.error(e.get_log_formatted_message())
        return None


def get_token() -> tuple[str, int]:
    """
    Get a JWT token based on the Camunda client credentials (client ID and client secret)
    :raises ServiceException
    :return: tuple of token and expires_in (seconds)
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(get_config().auth.get_url(), headers=headers,
                                 data=get_config().auth.get_request_data(), timeout=10)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)

        return access_token, expires_in

    except Exception as e:
        raise ServiceException(
            error_code=ErrorCode.C8_AUTH_GET_TOKEN_FAILED, parameters=[e]
        )
