import os
from typing import Iterator, Literal

from googleapiclient.discovery import build as gbuild
from googleapiclient.http import MediaFileUpload

from baresquare_sdk.gcp.authentication import CredentialProvider
from baresquare_sdk.gcp.clients import GCPClients
from baresquare_sdk.gcp.pagers import PageIterator


class Drive:
    _SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, source: CredentialProvider | GCPClients):
        if isinstance(source, GCPClients):
            self._client = source.drive()
            return

        self._client = gbuild("drive", "v3", credentials=source.get_credentials(self._SCOPES), cache_discovery=False)

    def create_folder(self, name: str, parents: list[str] = []) -> str:
        """Create a folder in the Drive.

        Args:
            name: The name of the folder to create.
            parents: The parents of the folder to create.
        """
        return (
            self._client.files()
            .create(body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": parents})
            .execute()["id"]
        )

    def _share_folder(
        self, folder_id: str, body: dict, send_notification: bool = False, supports_all_drives: bool = False
    ) -> None:
        (
            self._client.permissions()
            .create(
                fileId=folder_id,
                body=body,
                sendNotificationEmail=send_notification,
                supportsAllDrives=supports_all_drives,
            )
            .execute()
        )

    def share_folder_with_domain(
        self,
        folder_id: str,
        domain: str,  # e.g., "baresquare.com"
        role: Literal["reader", "commenter", "writer", "organizer"] = "reader",  # (organizer only for Shared Drives)
        discoverable: bool = True,
        supports_all_drives: bool = False,
    ) -> None:
        body = {
            "type": "domain",
            "domain": domain,
            "role": role,
            "allowFileDiscovery": discoverable,
        }
        self._share_folder(folder_id, body, False, supports_all_drives)

    def share_folder_with_email(
        self,
        folder_id: str,
        email: str,
        email_type: Literal["user", "group"] = "user",
        role: Literal["reader", "commenter", "writer", "organizer"] = "reader",
    ) -> None:
        body = {
            "type": email_type,
            "role": role,
            "emailAddress": email,
        }
        self._share_folder(folder_id, body, False)

    def get_folder_metadata(self, folder_id: str) -> dict:
        """Get the metadata of a folder in the Drive."""
        return (
            self._client.files()
            .get(fileId=folder_id, fields="id, name, mimeType, parents, modifiedTime, webViewLink, permissions")
            .execute()
        )

    def list_files_in_folder(self, folder_id: str) -> list[dict]:
        """List the files in a folder in the Drive."""
        # TODO: Use list_files instead? :thinking:
        # This implementation returns list of files, the other returns iterator of files.
        return (
            self._client.files()
            .list(q=f"parents='{folder_id}'", fields="files(id, name, mimeType, parents, modifiedTime, webViewLink)")
            .execute()["files"]
        )

    def folder_exists(self, folder_id: str) -> bool:
        """Check if a folder exists in the Drive."""
        try:
            self.get_folder_metadata(folder_id)
            return True
        except Exception:
            return False

    def query_drive(self, query: str) -> Iterator[dict]:
        """Query the Drive."""
        return self.list_files(q=query)

    def delete_folder(self, folder_id: str) -> None:
        """Delete a folder in the Drive."""
        self._client.files().delete(fileId=folder_id).execute()

    def list_files(self, q: str, page_size: int = 100) -> Iterator[dict]:
        """List files in the Drive.

        Args:
            q: The query to filter the files.
            page_size: The number of files to return per page.

        Returns:
            An iterator of dictionaries containing the metadata of the files.
            Keys per file are id, name, mimeType, owners, modifiedTime, webViewLink.

        Examples:
            for f in drive.list_files(q="mimeType='application/vnd.google-apps.spreadsheet'"):  # Spreadsheets
                print(f["id"], f["name"], f["mimeType"], f["webViewLink"])
            for f in drive.list_files(q="name contains 'partnerships'"):   # Partial name search
                print(f["id"], f["name"])
            for f in drive.list_files(q=""):  # All files
                print(f["id"])
        """
        req = self._client.files().list(
            q=q,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, webViewLink, owners, permissions, parents)",
            pageSize=page_size,
        )
        return PageIterator(self._client, req, "files", "nextPageToken")

    def get_file_metadata(self, file_id: str) -> dict:
        """Get the metadata of a file in the Drive.

        Args:
            file_id: The ID of the file to get the metadata of.

        Returns:
            A dictionary containing the metadata of the file.
            - id: The ID of the file.
            - name: The name of the file.
            - mimeType: The MIME type of the file.
            - owners: The owners of the file.
            - modifiedTime: The last modified time of the file.
            - webViewLink: The web view link of the file.
        """
        return (
            self._client.files()
            .get(
                fileId=file_id,
                fields="id, name, driveId, mimeType, createdTime, modifiedTime, webViewLink, parents, owners, permissions",
            )
            .execute()
        )

    def file_exists(self, file_id: str) -> bool:
        """Check if a file exists in the Drive."""
        try:
            self.get_file_metadata(file_id)
            return True
        except Exception:
            return False

    def upload_file(self, file_path: str, folder_id: str) -> str:
        """Upload a file to the Drive.

        Args:
            file_path: The local path to the file to upload.
            folder_id: The ID of the folder to upload the file to.

        Returns:
            The ID of the uploaded file.

        Raises:
            FileNotFoundError: If the folder does not exist.
            FileExistsError: If the file already exists.
        """
        # check if folder exists
        if not self.folder_exists(folder_id):
            raise FileNotFoundError(f"Folder {folder_id} does not exist")

        # check if file exists
        if self.file_exists(file_path):
            raise FileExistsError(f"File {file_path} already exists")

        file_metadata = {
            "name": os.path.basename(file_path).encode("utf-8").decode("utf-8"),
            "parents": [folder_id],
        }
        media = MediaFileUpload(file_path, resumable=True)

        return (
            self._client.files()
            .create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
            )
            .execute()["id"]
        )
