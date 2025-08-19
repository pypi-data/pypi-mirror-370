from datetime import date, datetime, time
from decimal import Decimal

from google.cloud.bigquery import Client, QueryJobConfig, ScalarQueryParameter
from pandas import DataFrame

from baresquare_sdk.gcp.authentication import CredentialProvider, GoogleAuth
from baresquare_sdk.gcp.clients import GCPClients


class BQ:
    _SCOPES = ["https://www.googleapis.com/auth/bigquery"]

    def __init__(self, source: CredentialProvider | GCPClients, quota_project: str | None = None):
        if isinstance(source, GCPClients):
            self._client: Client = source.bigquery()
            return

        creds = source if isinstance(source, CredentialProvider) else GoogleAuth()
        credentials = creds.get_credentials(self._SCOPES)

        final_quota_project = quota_project
        if not final_quota_project and hasattr(credentials, "project_id") and credentials.project_id:
            final_quota_project = credentials.project_id

        self._client: Client = Client(credentials=credentials, project=final_quota_project)

    def _infer_bq_type(self, value: object) -> str:
        if isinstance(value, bool):
            return "BOOL"
        if isinstance(value, int):
            return "INT64"
        if isinstance(value, float):
            return "FLOAT64"
        if isinstance(value, Decimal):
            return "NUMERIC"
        if isinstance(value, str):
            return "STRING"
        if isinstance(value, bytes):
            return "BYTES"
        if isinstance(value, datetime):
            return "TIMESTAMP"
        if isinstance(value, date):
            return "DATE"
        if isinstance(value, time):
            return "TIME"
        raise TypeError(f"Unsupported parameter type for value: {type(value)!r}")

    def query(self, sql: str, params: dict[str, object] | None = None, timeout: int = 120) -> DataFrame:
        """Query a BigQuery table and return a pandas DataFrame.

        Args:
            sql: The SQL query to execute.
            params: A optional dictionary of parameter names and values.
            timeout: The timeout in seconds for the query. Defaults to 120 seconds.

        Returns:
            A pandas DataFrame.
        """
        job_config = None
        if params:
            query_parameters: list[ScalarQueryParameter] = []
            for name, value in params.items():
                if isinstance(value, tuple) and len(value) == 2:
                    type_, actual_value = value
                    query_parameters.append(
                        ScalarQueryParameter(name=name, type_=type_, value=actual_value),
                    )
                else:
                    if value is None:
                        raise ValueError(
                            f"Parameter '{name}' is None; please pass an explicit (type_, value) tuple.",
                        )
                    inferred_type = self._infer_bq_type(value)
                    query_parameters.append(
                        ScalarQueryParameter(name=name, type_=inferred_type, value=value),
                    )
            job_config = QueryJobConfig(query_parameters=query_parameters)
        job = self._client.query(sql, job_config=job_config)
        return job.result(timeout=timeout).to_dataframe(create_bqstorage_client=True)
