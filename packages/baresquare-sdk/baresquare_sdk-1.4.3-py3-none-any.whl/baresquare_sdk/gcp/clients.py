from typing import Any

from google.cloud import bigquery
from googleapiclient.discovery import build as gbuild

from baresquare_sdk.gcp.authentication import CredentialProvider


class GCPClients:
    def __init__(self, creds: CredentialProvider, quota_project: str | None = None):
        self._creds = creds
        self._quota_project = self._get_quota_project(quota_project)

    def _get_quota_project(self, quota_project: str | None = None) -> str | None:
        if quota_project:
            return quota_project
        if self._creds.get_credentials().project_id:
            return self._creds.get_credentials().project_id
        return None

    def drive(self) -> Any:
        scopes = ["https://www.googleapis.com/auth/drive"]
        return gbuild("drive", "v3", credentials=self._creds.get_credentials(scopes), cache_discovery=False)

    def docs(self) -> Any:
        scopes = ["https://www.googleapis.com/auth/documents"]
        return gbuild("docs", "v1", credentials=self._creds.get_credentials(scopes), cache_discovery=False)

    def sheets(self) -> Any:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        return gbuild("sheets", "v4", credentials=self._creds.get_credentials(scopes), cache_discovery=False)

    def slides(self) -> Any:
        scopes = ["https://www.googleapis.com/auth/presentations"]
        return gbuild("slides", "v1", credentials=self._creds.get_credentials(scopes), cache_discovery=False)

    def bigquery(self) -> bigquery.Client:
        scopes = ["https://www.googleapis.com/auth/bigquery"]
        return bigquery.Client(credentials=self._creds.get_credentials(scopes), project=self._quota_project)
