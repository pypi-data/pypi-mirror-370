import json
import os
import sys
from abc import ABCMeta

from aiwb.utils.console import console, err_console

from rich.pretty import Pretty


class ServiceModel(metaclass=ABCMeta):
    service_name = None

    def __init__(self, client, output):
        self._client = client
        self._url = os.getenv("AIWB_URL", "https://ai.aws.renesasworkbench.com")
        self._cloud = self._get_cloud()
        self._env = self._derive_env_from_url(self._url)
        if not self._url:
            self._url = f"https://ai.{self._cloud}.renesasworkbench.com"
        self.output = output

    def get_organization_name(self):
        user_schema = self._client.get_user_schema()
        if not user_schema:
            self.stderr("Unable to retrieve user's organization name")

        return user_schema

    def _get_cloud(self):
        """
        Get the cloud type from the client configuration.
        """
        if self._url:
            url_lower = self._url.lower()
            if "aws" in url_lower:
                return "aws"
            if "azure" in url_lower:
                return "azure"
            if "localhost" in url_lower:
                return os.getenv("AIWB_CLOUD", "").lower()

            raise ValueError(f"Unknown cloud type in URL `{self._url}`")
        raise ValueError(
            "URL not provided, please set the AIWB_URL environment variable"
        )

    @staticmethod
    def _derive_env_from_url(url):
        """
        Derive the environment from the URL.
        """
        url_lower = url.lower()
        if "ai-d." in url_lower or "localhost" in url_lower:
            return "dev"
        if "ai-t." in url_lower:
            return "test"
        if "ai-s." in url_lower:
            return "stag"
        if "ai." in url_lower:
            return "prod"
        raise ValueError("Environment not specified in URL")

    @staticmethod
    def _console(data, output="text", stderr=False, pretty=True):
        _console = console
        if stderr:
            _console = err_console
            pretty = False
            if isinstance(data, dict) and output != "json":
                data = data.get("message")
        if output == "json":
            try:
                data = json.dumps(data)
            except (TypeError, ValueError):
                _console = _console.print
                data = Pretty(data, indent_guides=False, expand_all=True)
            else:
                _console = _console.print_json
        elif output == "text":
            _console = _console.out
            pretty = False
        else:
            _console = _console.print
            if pretty:
                data = Pretty(data, indent_guides=False, expand_all=True)
        _console(data)

    def stdout(self, data):
        self._console(data, self.output)
        sys.exit(0)

    def stderr(self, data):
        self._console(data, self.output, stderr=True)
        sys.exit(1)

    def process(self, path, method="GET", **kwargs):
        res, err = self._client.request(f"{self._url}/{path}", method, **kwargs)
        if err:
            self.stderr(res)
        self.stdout(res)

    @classmethod
    def is_service(cls, service_name):
        if not cls.service_name:
            raise TypeError(
                "Subclass of ServiceModel needs to have the `service_name` class attribute."
            )
        return service_name == cls.service_name
