import requests
import os
import json

import logging
from urllib.parse import urlparse
from .token import AIWBTokenProvider
from .model import ServiceModel

logger = logging.getLogger(__name__)


class Client:
    """
    A aiwb client stores configuration state and allows you to create service
    clients and resources.

    :param access_key: AIWB personal access key ID
    :param cloud_type: AIWB Cloud type
    :param tenant: AIWB tenant name
    :param token_provider: AIWB auth provider
    """

    def __init__(
        self,
        access_key: str | None = None,
        cloud: str | None = "aws",
        tenant: str | None = None,
        token_provider: str = "aiwb",
        log_level: str = "info",
    ):
        """
        Create a new Session object.
        """
        self._access_key = access_key
        self._cloud = cloud
        self._token_provider = token_provider
        self._tenant = tenant
        self._session = requests.Session()
        if self._access_key:
            # AIWB Personal access key
            auth_token = f"{self._access_key}"
        else:
            # OIDC Device flow
            token = self.load_auth_token()
            # for AIWB Service, using id token
            auth_token = f"{token.get('id_token')}"
        self._log_level = log_level

        url = urlparse(self.url)

        if url.port:
            self._domain = f"{url.hostname}:{url.port}"
        elif url.scheme == "https":
            self._domain = f"{url.hostname}:443"
        elif url.scheme == "http":
            self._domain = f"{url.hostname}:80"
        else:
            self._domain = url.hostname
        self._session.cookies.set("access-token", auth_token, domain=self._domain)

    @property
    def token_provider(self):
        if self._token_provider == "aiwb":
            return AIWBTokenProvider(self)

    @property
    def url(self):
        return os.getenv(
            "AIWB_URL",
            f"https://ai.{self._cloud}.renesasworkbench.com",
        )

    def generate_auth_token(self):
        return self.token_provider.generate_token()

    def revoke_auth_token(self, token=None):
        return self.token_provider.revoke_token(token)

    def load_auth_token(self):
        return self.token_provider.load_token()

    def _error_message(self, error_response: requests.Response):
        """
        Tries to extract an error message from an HTTP response.

        Attempts to parse the response body as JSON and extract common error fields.
        Falls back to using the raw response text if the body is not valid JSON or does not contain expected fields.

        Args:
            error_response (Response): The HTTP response object returned by the `requests` library.

        Returns:
            str: A human-readable error message in the format: "<HTTP Status Phrase>: <Error Message>"
        """
        error_message = "Unknown error"

        try:
            error_json = error_response.json()
            logger.debug(json.dumps(error_json, indent=4))
        except json.JSONDecodeError as exc:
            logger.debug("Failed to decode JSON response. %s", exc)
            logger.debug("Error text: %s", error_response.text)
        else:
            # Since the return error response is not consistent from backend,
            # we are guessing the error message here.
            if "message" in error_json:
                error_message = error_json.get("message")
            elif "error_description" in error_json:
                error_message = error_json.get("error_description")
            elif isinstance(error_dict := error_json.get("error"), dict):
                error_message = error_dict.get("message", "Unknown error")
            elif isinstance(error_text := error_json.get("error"), str):
                error_message = error_text

        return {"success": False, "message": error_message.capitalize().rstrip("."), "code": error_response.status_code}

    def _response(self, response):
        if 200 <= response.status_code < 300:
            try:
                res = response.json()
            except json.JSONDecodeError:
                res = {"success": True, "message": response.text}
            return res, False
        else:
            return self._error_message(response), True

    def request(self, url, method="get", *args, **kwargs):
        try:
            method = method.lower()
            if method == "post":
                res = self._session.post(url, *args, **kwargs)
            elif method == "put":
                res = self._session.put(url, *args, **kwargs)
            elif method == "delete":
                res = self._session.delete(url, *args, **kwargs)
            elif method == "patch":
                res = self._session.patch(url, *args, **kwargs)
            else:
                res = self._session.get(url, **kwargs)
            return self._response(res)
        except requests.exceptions.HTTPError as e:
            logger.debug(f"HTTP Error: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"Connection Error: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.debug(f"Timeout Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.debug(f"Request Exception: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.debug(f"JSON Decode Exception: {e}")
            raise

    def user_info(self):
        if self._access_key:
            # TODO: get user info for personal access key
            return {}
        else:
            self.token_provider.user_info()
            
    def get_user_schema(self):
        user_info, err = self.token_provider.get_user_info()
        if err:
            return None
        
        return user_info.get("schema_name")

    def model(self, service_name=None, *args, **kwargs):
        if self._access_key:
            # AIWB Personal access key
            auth_token = f"{self._access_key}"
        else:
            # OIDC Device flow
            token = self.load_auth_token()
            # for AIWB Service, using id token
            auth_token = f"{token.get('id_token')}"
        service_model = None
        for cls in ServiceModel.__subclasses__():
            if cls.is_service(service_name):
                service_model = cls
        self._session.cookies.set("access-token", auth_token)
        if service_model is not None:
            return service_model(client=self, *args, **kwargs)
