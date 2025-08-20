import types
from datetime import date, datetime, time, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from baresquare_sdk.gcp.bigquery import BQ
from baresquare_sdk.gcp.clients import GCPClients


class TestBQ__init__:
    def test_init_with_gcpclients_uses_injected_client(self):
        mock_bq_client = MagicMock()

        class DummyClients(GCPClients):
            pass

        mock_clients = object.__new__(DummyClients)
        mock_clients.bigquery = MagicMock(return_value=mock_bq_client)

        bq = BQ(source=mock_clients)

        assert bq._client is mock_bq_client
        mock_clients.bigquery.assert_called_once_with()

    @patch("baresquare_sdk.gcp.bigquery.GoogleAuth")
    @patch("baresquare_sdk.gcp.bigquery.Client")
    def test_init_with_credentialprovider_and_no_quota_uses_project_id(self, mock_client_cls, mock_google_auth):
        mock_credentials = MagicMock()
        mock_credentials.project_id = "test-project"

        # Pass an object that implements get_credentials directly
        class DummyCreds:
            def get_credentials(self, scopes=None):
                return mock_credentials

        bq = BQ(source=DummyCreds())

        mock_client_cls.assert_called_once_with(credentials=mock_credentials, project="test-project")
        assert isinstance(bq, BQ)

    @patch("baresquare_sdk.gcp.bigquery.Client")
    def test_init_with_quota_project_overrides_credentials_project(self, mock_client_cls):
        mock_credentials = types.SimpleNamespace(project_id="creds-project")

        class DummyCreds:
            def get_credentials(self, scopes=None):
                return mock_credentials

        _ = BQ(source=DummyCreds(), quota_project="explicit-project")

        mock_client_cls.assert_called_once_with(credentials=mock_credentials, project="explicit-project")

    @patch("baresquare_sdk.gcp.bigquery.Client")
    def test_init_without_provider_defaults_to_googleauth(self, mock_client_cls):
        # Passing a non-credential, non-GCPClients object triggers default GoogleAuth()
        with patch("baresquare_sdk.gcp.bigquery.GoogleAuth") as mock_google_auth:
            mock_credentials = MagicMock(project_id=None)
            mock_google_auth.return_value.get_credentials.return_value = mock_credentials

            _ = BQ(source=object())

            mock_google_auth.assert_called_once_with()
            mock_client_cls.assert_called_once_with(credentials=mock_credentials, project=None)


class TestBQ__infer_bq_type:
    @pytest.mark.parametrize(
        "value,expected",
        [
            (False, "BOOL"),
            (True, "BOOL"),
            (123, "INT64"),
            (123.45, "FLOAT64"),
            (Decimal("1.23"), "NUMERIC"),
            ("abc", "STRING"),
            (b"bytes", "BYTES"),
            (datetime.now(timezone.utc), "TIMESTAMP"),
            (date.today(), "DATE"),
            (time(1, 2, 3), "TIME"),
        ],
    )
    def test_infer_bq_type_supported(self, value, expected):
        bq = object.__new__(BQ)  # bypass __init__
        assert BQ._infer_bq_type(bq, value) == expected

    def test_infer_bq_type_unsupported_raises(self):
        bq = object.__new__(BQ)
        with pytest.raises(TypeError):
            BQ._infer_bq_type(bq, object())


class TestBQ__query:
    @patch("baresquare_sdk.gcp.bigquery.QueryJobConfig")
    @patch("baresquare_sdk.gcp.bigquery.ScalarQueryParameter")
    def test_query_builds_parameters_and_returns_dataframe(self, mock_param_cls, mock_job_cfg_cls):
        # Arrange client and job chain
        mock_df = pd.DataFrame({"a": [1]})
        mock_job = MagicMock()
        mock_job.result.return_value.to_dataframe.return_value = mock_df
        mock_client = MagicMock()
        mock_client.query.return_value = mock_job

        bq = object.__new__(BQ)
        bq._client = mock_client

        params = {
            "p1": 1,
            "p2": ("STRING", "abc"),
            "p3": Decimal("1.2"),
        }

        # Act
        result = BQ.query(bq, sql="SELECT 1", params=params, timeout=99)

        # Assert
        assert result.equals(mock_df)
        # Should build three ScalarQueryParameter instances
        assert mock_param_cls.call_count == 3
        # Should create QueryJobConfig with those parameters
        mock_job_cfg_cls.assert_called_once()
        mock_client.query.assert_called_once()
        mock_job.result.assert_called_once_with(timeout=99)
        mock_job.result.return_value.to_dataframe.assert_called_once_with(create_bqstorage_client=True)

    def test_query_with_none_param_raises(self):
        bq = object.__new__(BQ)
        bq._client = MagicMock()

        with pytest.raises(ValueError) as exc:
            BQ.query(bq, sql="SELECT @x", params={"x": None})
        assert "please pass an explicit (type_, value) tuple" in str(exc.value)

    @patch("baresquare_sdk.gcp.bigquery.QueryJobConfig")
    def test_query_without_params(self, mock_job_cfg_cls):
        mock_df = pd.DataFrame({"a": [1]})
        mock_job = MagicMock()
        mock_job.result.return_value.to_dataframe.return_value = mock_df
        mock_client = MagicMock()
        mock_client.query.return_value = mock_job

        bq = object.__new__(BQ)
        bq._client = mock_client

        result = BQ.query(bq, sql="SELECT 1", params=None)

        assert result.equals(mock_df)
        mock_job_cfg_cls.assert_not_called()
        mock_client.query.assert_called_once_with("SELECT 1", job_config=None)
