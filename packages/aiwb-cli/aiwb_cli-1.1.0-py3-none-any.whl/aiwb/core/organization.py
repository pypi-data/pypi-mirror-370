import json
import logging
from .client import Client

from .model import ServiceModel
from aiwb.utils.console import show_loading_status

logger = logging.getLogger(__name__)


class Organization(ServiceModel):
    service_name = "organization"

    def __init__(self, client: Client | None = None, output: str | None = "json"):
        super().__init__(client, output)

    def list(self):
        with show_loading_status("Fetching organization list..."):
            response, error = self._client.request(
                f"{self._url}/api/org/list-organization",
            )

        if error:
            self.stderr(response)
        else:
            self.stdout(response)

    def describe(self, organization_name):
        with show_loading_status("Retrieving organization details..."):
            response, error = self._client.request(
                f"{self._url}/api/org/{organization_name}/detail",
            )

        if error:
            self.stderr(response)
        else:
            self.stdout(response)

    def create(self, payload: dict, logo_file=None):
        logo_file_path = None
        if logo_file:
            logo_file_path = logo_file.name
            files = {"logo": (logo_file_path, logo_file)}
        else:
            files = None

        res, err = self._client.request(f"{self._url}/api/users/get-users-from-azure")

        if err:
            self.stderr(res)

        ad_users = res.get("data", [])
        if len(ad_users) == 0:
            self.stderr("No AD users retrieved from workbench")

        users = []
        if payload.get("admin_oid"):
            users = [u for u in ad_users if u.get("id") == payload.get("admin_oid")]
        elif payload.get("email"):
            users = [u for u in ad_users if u.get("email") == payload.get("email")]
        elif payload.get("user_principal_name"):
            users = [u for u in ad_users if u.get("user_principal_name") == payload.get("user_principal_name")]

        if len(users) == 0:
            self.stderr("Admin user not found, exit.")
            
        target_user = users[0]
        payload["first_name"] = target_user.get("first_name")
        payload["last_name"] = target_user.get("last_name")
        payload["email"] = target_user.get("email")
        payload["user_principal_name"] = target_user.get("user_principal_name")
        payload["admin_oid"] = target_user.get("id")
        payload["region"] = "Japan East"

        with show_loading_status("Creating organization..."):
            response, error = self._client.request(
                f"{self._url}/api/org/create-organization",
                "POST",
                data={"data": json.dumps(payload)},
                files=files,
            )

        if error:
            self.stderr(response)
        else:
            self.stdout(response)

    def update(self, organization_name, payload: dict, logo_file=None, delete_logo=False):
        logo_file_path = None
        if logo_file:
            logo_file_path = logo_file.name
            files = {"logo": (logo_file_path, logo_file)}
        else:
            files = None

        if delete_logo:
            payload["delete_logo"] = True

        with show_loading_status("Updating organization..."):
            response, error = self._client.request(
                f"{self._url}/api/org/{organization_name}/update",
                "PATCH",
                data={"data": json.dumps(payload)},
                files=files,
            )

        if error:
            self.stderr(response)
        else:
            self.stdout(response)

    def delete(self, organization_name):
        with show_loading_status("Deleting organization..."):
            response, error = self._client.request(f"{self._url}/api/org/{organization_name}/delete", "DELETE")

        if error:
            self.stderr(response)
        else:
            self.stdout(response)
