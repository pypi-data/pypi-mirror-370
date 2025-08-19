import logging

from .model import ServiceModel
from .client import Client

from aiwb.utils import can_launch_browser, open_page_in_browser


logger = logging.getLogger(__name__)


class IDE(ServiceModel):
    def __init__(
        self,
        client: Client | None = None,
        workbench_id: int | None = None,
        output: str | None = "json",
    ):
        self._workbench_id = workbench_id
        super().__init__(client, output)

    @classmethod
    def is_service(cls, service_name):
        return service_name == "ide"

    def status(self):
        self.process(f"/api/workbench/{self._workbench_id}/ide/status/", "GET")

    def launch(self):
        res, err = self._client.request(f"{self._url}/api/workbench/{self._workbench_id}/ide/launch/", "POST")
        if err:
            self.stderr(res)
        if can_launch_browser():
            data = res.get("data", {})
            if data.get("power_state") == "Running":
                open_page_in_browser(data.get("url"))
        self.stdout(res)

    def delete(self):
        self.process(f"/api/workbench/{self._workbench_id}/ide/", "DELETE")

    def stop(self):
        self.process(f"/api/workbench/{self._workbench_id}/ide/stop/", "POST")

    def list(self, filters):
        res, err = self._client.request(f"{self._url}/api/ide/", "GET")
        if err:
            self.stderr(res)
        if filters and (isinstance(filters, list) or isinstance(filters, tuple)):
            res = [r for f in filters for r in res if r.get(f[0]) == f[1]]
        self.stdout(res)
