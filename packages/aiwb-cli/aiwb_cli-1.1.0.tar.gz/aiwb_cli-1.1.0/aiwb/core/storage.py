import logging
import os

from aiwb.utils.console import show_loading_status

import boto3
from azure.storage.blob import ContainerClient
from botocore.exceptions import ClientError

from .client import Client
from .model import ServiceModel

logger = logging.getLogger(__name__)


class Storage(ServiceModel):
    service_name = "storage"
    azure_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
    previous_level = azure_logger.level
    azure_logger.setLevel(logging.WARNING)

    def __init__(self, client: Client | None = None, output: str | None = "json"):
        super().__init__(client, output)
        self._organization_name = self.get_organization_name()
        if "localhost" in self._url and not self._cloud in ("azure", "aws"):
            self.stderr(
                f"AIWB_CLOUD environment variable is required when AIWB_URL=`{self._url}`. Please set AIWB_CLOUD to one of 'aws' or 'azure'."
            )

    def _get_azure_container_client(self, env, container_name, credentials):
        """
        Helper to initialize and return an Azure ContainerClient using the given parameters.
        """
        storage_account_name = f"aiwbwuiazjpe{env}orgsa"
        account_url = f"https://{storage_account_name}.blob.core.windows.net/"
        return ContainerClient(
            account_url=account_url,
            container_name=container_name,
            credential=credentials,
        )

    def _get_s3_client(self, credentials):
        """
        Helper to initialize and return a boto3 S3 client using the given credentials.
        """
        return boto3.client(
            "s3",
            aws_access_key_id=credentials.get("AccessKeyId"),
            aws_secret_access_key=credentials.get("SecretAccessKey"),
            aws_session_token=credentials.get("SessionToken"),
        )

    def get_object_storage_name(self, organization_name):
        if self._url:
            url_lower = self._url.lower()
            if "localhost" in url_lower:
                return f"aiwb-{organization_name.lower()}-ud-local"
        return f"aiwb-{organization_name.lower()}-ud"

    def get_temporary_credentials(self, cloud: str):
        """
        Get temporary credentials for the specified organization and cloud type.
        """
        if cloud == "aws":
            params = {
                "bucket_name": self.get_object_storage_name(self._organization_name),
                "schema_name": self._organization_name,
            }
            response, error = self._client.request(
                f"{self._url}/api/auth/sts-token", "GET", params=params
            )
            if error:
                self.stderr(f"Error getting temporary credentials: {response}")
            credentials = response.get("credentials", {})
            if not credentials:
                self.stderr("No credentials found in the response")
            return credentials
        if cloud == "azure":
            params = {
                "container_name": self.get_object_storage_name(self._organization_name),
                "expiry_hours": "1",  # Set the expiry time for the SAS token 1h
                "file_name": "",
                "permissions": "rwdl",  # Read, Write, Delete, List
                "sa_type": "org",  # Storage Account type
            }
            response, error = self._client.request(
                f"{self._url}/api/auth/sas-token", "GET", params=params
            )
            if error:
                self.stderr(f"Error getting temporary credentials: {response}")
            credentials = response.get("sas_token", {})
            if not credentials:
                self.stderr("No credentials found in the response")
            return credentials

    def list(self):
        cloud = self._cloud
        organization_name = self._organization_name
        object_storage_name = self.get_object_storage_name(organization_name)
        credentials = self.get_temporary_credentials(cloud)
        print(f"Object storage name: {object_storage_name}")
        with show_loading_status("Retrieving object store details..."):
            if cloud == "aws":
                s3 = self._get_s3_client(credentials)
                try:
                    response = s3.list_objects_v2(Bucket=object_storage_name)
                    if "Contents" in response:
                        objects = response["Contents"]
                        print(f"Objects in org storage: '{object_storage_name}':")

                        for obj in objects:
                            print(
                                f" - {obj['Key']} (Size: {obj['Size']} bytes, Last Modified: {obj['LastModified']})"
                            )

                    else:
                        print(f"No objects found in bucket '{object_storage_name}'.")
                except ClientError as e:
                    self.stderr(
                        f"Error listing objects in bucket '{object_storage_name}': {e}"
                    )
            elif cloud == "azure":
                env = self._env
                container_name = self.get_object_storage_name(organization_name)
                container_client = self._get_azure_container_client(
                    env, container_name, credentials
                )
                blobs_list = container_client.list_blobs()
                blobs_list = list(blobs_list)
                if blobs_list is None or len(blobs_list) == 0:
                    print(f"No blobs found in container '{container_name}'.")
                for blob in blobs_list:
                    print(
                        f" - {blob.name} (Size: {blob.size} bytes, Last Modified: {blob.last_modified.isoformat()})"
                    )

    def push(self, directory, file):
        organization_name = self._organization_name
        object_storage_name = self.get_object_storage_name(organization_name)
        credentials = self.get_temporary_credentials(self._cloud)
        if self._cloud == "aws":
            s3 = self._get_s3_client(credentials)
            with show_loading_status("Uploading..."):
                if directory:
                    for root, _, files in os.walk(directory):
                        for file in files:
                            local_path = os.path.join(root, file)
                            relative_path = os.path.relpath(local_path, directory)
                            s3_key = relative_path.replace("\\", "/")
                            try:
                                s3.upload_file(local_path, object_storage_name, s3_key)
                                print(
                                    f"Uploaded {s3_key} to object storage '{object_storage_name}' (overwritten if existed)"
                                )
                            except ClientError as e:
                                self.stderr(
                                    f"Error uploading {s3_key} to object storage '{object_storage_name}': {e}"
                                )
                elif file:
                    s3.upload_file(file, object_storage_name, os.path.basename(file))
                    print(f"Uploaded {file} to object storage '{object_storage_name}'")
        elif self._cloud == "azure":
            env = self._env
            container_name = self.get_object_storage_name(organization_name)
            container_client = self._get_azure_container_client(
                env, container_name, credentials
            )
            with show_loading_status("Uploading..."):
                if directory:
                    for root, _, files in os.walk(directory):
                        for file in files:
                            local_path = os.path.join(root, file)
                            relative_path = os.path.relpath(local_path, directory)
                            blob_name = relative_path.replace("\\", "/")
                            with open(local_path, "rb") as data:
                                container_client.upload_blob(
                                    name=blob_name, data=data, overwrite=True
                                )
                                print(
                                    f"Uploaded {local_path} to object storage '{object_storage_name}'"
                                )
                elif file:
                    with open(file, "rb") as data:
                        blob_name = os.path.basename(file)
                        container_client.upload_blob(
                            name=blob_name, data=data, overwrite=True
                        )
                        print(
                            f"Uploaded {file} to object storage '{object_storage_name}'"
                        )

    def diff(self, directory):
        organization_name = self._organization_name
        object_storage_name = self.get_object_storage_name(organization_name)
        credentials = self.get_temporary_credentials(self._cloud)
        if self._cloud == "aws":
            s3 = self._get_s3_client(credentials)
            with show_loading_status("Comparing..."):
                if directory:
                    try:
                        response = s3.list_objects_v2(Bucket=object_storage_name)
                    except ClientError as e:
                        self.stderr(
                            f"Error listing objects in bucket '{object_storage_name}': {e}"
                        )
                        return
                    if "Contents" in response:
                        s3_keys = set(obj["Key"] for obj in response["Contents"])
                        for obj in response["Contents"]:
                            s3_key = obj["Key"]
                            local_path = os.path.join(directory, s3_key)
                            if not os.path.exists(local_path):
                                print(f"File {s3_key} exists in S3 but not locally.")
                            else:
                                local_mtime = os.path.getmtime(local_path)
                                s3_mtime = obj["LastModified"].timestamp()
                                if local_mtime < s3_mtime:
                                    print(
                                        f"Local file {local_path} is older than S3 object {s3_key}."
                                    )
                                elif local_mtime > s3_mtime:
                                    print(
                                        f"Local file {local_path} is newer than S3 object {s3_key}."
                                    )
                                else:
                                    print(
                                        f"Local file {local_path} is the same as S3 object {s3_key}."
                                    )
                    else:
                        print(f"No objects found in bucket '{object_storage_name}'.")
        elif self._cloud == "azure":
            with show_loading_status("Comparing..."):
                env = self._env
                storage_account_name = f"aiwbwuiazjpe{env}orgsa"
                account_url = f"https://{storage_account_name}.blob.core.windows.net/"
                container_name = self.get_object_storage_name(organization_name)

                container_client = ContainerClient(
                    account_url=account_url,
                    container_name=container_name,
                    credential=credentials,
                )
                blobs_list = container_client.list_blobs()
                blobs_list = list(blobs_list)
                if blobs_list is None or len(blobs_list) == 0:
                    print(f"No blobs found in container '{container_name}'.")
                for blob in blobs_list:
                    blob_info = {
                        "name": blob.name,
                        "size": blob.size,
                        "last_modified": blob.last_modified.isoformat(),
                    }
                    local_path = os.path.join(directory, blob.name)
                    if not os.path.exists(local_path):
                        print(f"Blob {blob.name} exists in Azure but not locally.")
                    else:
                        local_mtime = os.path.getmtime(local_path)
                        if local_mtime < blob.last_modified.timestamp():
                            print(
                                f"Local file {local_path} is older than blob {blob.name} in object storage."
                            )
                        elif local_mtime > blob.last_modified.timestamp():
                            print(
                                f"Local file {local_path} is newer than blob {blob.name}in object storage."
                            )
                        else:
                            print(
                                f"Local file {local_path} is the same as blob {blob.name}in object storage."
                            )

    def pull(self, directory, file):
        organization_name = self._organization_name
        object_storage_name = self.get_object_storage_name(organization_name)
        credentials = self.get_temporary_credentials(self._cloud)
        if self._cloud == "aws":
            s3 = self._get_s3_client(credentials)
            with show_loading_status("Downloading..."):
                if directory:
                    response = s3.list_objects_v2(Bucket=object_storage_name)
                    if "Contents" in response:
                        for obj in response["Contents"]:
                            s3_key = obj["Key"]
                            local_path = os.path.join(directory, s3_key)
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            s3.download_file(object_storage_name, s3_key, local_path)
                            print(f"Downloaded {s3_key} to {local_path}")
                    else:
                        print(f"No objects found in bucket '{object_storage_name}'.")

                elif file:
                    local_path = os.path.join(directory, os.path.basename(file))
                    s3.download_file(object_storage_name, file, local_path)
                    print(f"Downloaded {file} to {local_path}")
        elif self._cloud == "azure":
            env = self._env
            container_name = self.get_object_storage_name(organization_name)
            container_client = self._get_azure_container_client(
                env, container_name, credentials
            )
            with show_loading_status("Downloading..."):
                if directory:
                    blobs_list = container_client.list_blobs()
                    blobs_list = list(blobs_list)

                    if blobs_list is None or len(blobs_list) == 0:
                        print(f"No blobs found in container '{container_name}'.")
                    for blob in blobs_list:
                        blob_info = {
                            "name": blob.name,
                            "size": blob.size,
                            "last_modified": blob.last_modified.isoformat(),
                        }
                        local_path = os.path.join(directory, blob.name)
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        with open(local_path, "wb") as data:
                            data.write(
                                container_client.download_blob(blob.name).readall()
                            )
                            print(f"Downloaded {blob.name} to {local_path}")
                elif file:
                    blob_name = os.path.basename(file)
                    local_path = os.path.join(directory, blob_name)
                    with open(local_path, "wb") as f:
                        blob_data = container_client.download_blob(blob_name)
                        f.write(blob_data.readall())
                        print(
                            f"Downloaded '{blob_name}' from object storage '{object_storage_name}' to '{local_path}'"
                        )
