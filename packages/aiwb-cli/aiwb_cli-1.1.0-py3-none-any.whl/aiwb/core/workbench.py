import logging
import functools

from .model import ServiceModel
from .client import Client

logger = logging.getLogger(__name__)

IDE_SIZE_MAP = {"4c8g": "4 Core 8GB", "8c16g": "8 Core 16GB"}


class Workbench(ServiceModel):
    service_name = "workbench"

    def __init__(self, client: Client | None = None, output: str | None = "json"):
        super().__init__(client, output)

    @classmethod
    def is_service(cls, service_name):
        return service_name == "workbench"

    @staticmethod
    def _parse_size(res):
        if res.get("cpu") and res.get("memory"):
            return f"{res.get('cpu')}c{res.get('memory').replace('Gi','')}g"
        name = res.get("name").strip().replace(" ", "")
        name = name.replace(" Core ", "c")
        name = name.replace("GB", "g")
        return name

    @functools.cached_property
    def instance_size(self):
        instance_res, err = self._client.request(f"{self._url}/api/workbench/sizes/")
        result = {}
        if err:
            self.stderr(instance_res)
        for i in instance_res:
            name = i.get("name")
            if name:
                result[self._parse_size(i)] = name
        return result

    @functools.cached_property
    def sdk_info(self):
        sdk_res, err = self._client.request(f"{self._url}/api/sdk-version/")
        sdk_info = {
            i.get("sdk_version"): {
                "board_family": i.get("board_family"),
                "is_active": i.get("is_active"),
            }
            for i in sdk_res
            if i.get("sdk_version")
        }
        return sdk_info if not err else {}

    def list(self, filters=None):
        res, err = self._client.request(f"{self._url}/api/workbench/")
        if err:
            self.stderr(res)
        if filters and (isinstance(filters, list) or isinstance(filters, tuple)):
            res = [r for f in filters for r in res if r.get(f[0]) == f[1]]
        self.stdout(res)

    def create(self, name, size, sdk_version, description="", storage_size=20):
        if sdk_version not in self.sdk_info or not self.sdk_info[sdk_version].get("is_active", False):
            self.stderr("sdk version is not support")
            return
        data = {
            "workbench_name": name,
            "ide_preference": "Visual Studio Code",  # hard coded storage type since we only have one storage type
            "storage": {
                "type": "persistent",  # hard coded storage type since we only have one storage type
                "size": storage_size,
            },
            "sdk_version": sdk_version,
            "ide_size": self.instance_size.get(size, "4 Core 8GB"),
            "board_family": self.sdk_info[sdk_version],
            "description": description,
        }
        self.process("/api/workbench/", "POST", json=data)

    def delete(self, ids):
        res, err = self._client.request(f"{self._url}/api/workbench/{ids}/", "DELETE")
        if not err:
            self.stdout(f"Workbench {ids} is deleted")
        self.stderr(res)
