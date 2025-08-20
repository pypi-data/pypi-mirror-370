from unittest.mock import MagicMock, patch

import pytest
from google.auth.credentials import Credentials

from baresquare_sdk.gcp.authentication import ADCProvider, GoogleAuth, ServiceAccountProvider


class TestServiceAccountProvider:
    def test_get_credentials_with_key_path(self):
        with patch(
            "baresquare_sdk.gcp.authentication.service_account.Credentials.from_service_account_file",
        ) as mock_from_file:
            mock_creds = MagicMock()
            mock_from_file.return_value = mock_creds

            provider = ServiceAccountProvider(key_path="/path/to/key.json")
            creds = provider.get_credentials(scopes=["https://www.googleapis.com/auth/cloud-platform"])

            mock_from_file.assert_called_once_with("/path/to/key.json")
            mock_creds.with_scopes.assert_called_once_with(["https://www.googleapis.com/auth/cloud-platform"])
            assert creds == mock_creds.with_scopes.return_value

    def test_get_credentials_with_info(self):
        info = {"client_email": "test@example.com"}
        with patch(
            "baresquare_sdk.gcp.authentication.service_account.Credentials.from_service_account_info",
        ) as mock_from_info:
            mock_creds = MagicMock()
            mock_from_info.return_value = mock_creds

            provider = ServiceAccountProvider(info=info)
            creds = provider.get_credentials(scopes=["https://www.googleapis.com/auth/devstorage.read_only"])

            mock_from_info.assert_called_once_with(info)
            mock_creds.with_scopes.assert_called_once_with(["https://www.googleapis.com/auth/devstorage.read_only"])
            assert creds == mock_creds.with_scopes.return_value

    def test_get_credentials_with_subject(self):
        with patch(
            "baresquare_sdk.gcp.authentication.service_account.Credentials.from_service_account_file",
        ) as mock_from_file:
            mock_creds = MagicMock()
            mock_from_file.return_value = mock_creds

            provider = ServiceAccountProvider(key_path="/path/to/key.json", subject="user@example.com")
            creds = provider.get_credentials()

            mock_from_file.assert_called_once_with("/path/to/key.json")
            mock_creds.with_subject.assert_called_once_with("user@example.com")
            # with_scopes is not called when no scopes are provided
            mock_creds.with_subject.return_value.with_scopes.assert_not_called()
            assert creds == mock_creds.with_subject.return_value

    def test_get_credentials_with_subject_and_scopes(self):
        with patch(
            "baresquare_sdk.gcp.authentication.service_account.Credentials.from_service_account_file",
        ) as mock_from_file:
            mock_creds = MagicMock()
            mock_from_file.return_value = mock_creds

            provider = ServiceAccountProvider(key_path="/path/to/key.json", subject="user@example.com")
            creds = provider.get_credentials(scopes=["https://www.googleapis.com/auth/cloud-platform"])

            mock_from_file.assert_called_once_with("/path/to/key.json")
            mock_creds.with_subject.assert_called_once_with("user@example.com")
            mock_creds.with_subject.return_value.with_scopes.assert_called_once_with([
                "https://www.googleapis.com/auth/cloud-platform"
            ])
            assert creds == mock_creds.with_subject.return_value.with_scopes.return_value

    def test_get_credentials_no_key_or_info(self):
        provider = ServiceAccountProvider()
        with pytest.raises(ValueError, match="key_path or info required"):
            provider.get_credentials()


class TestADCProvider:
    def test_get_credentials(self):
        with patch("baresquare_sdk.gcp.authentication.google.auth.default") as mock_auth_default:
            mock_creds = MagicMock(spec=Credentials)
            mock_auth_default.return_value = (mock_creds, "test-project")

            provider = ADCProvider()
            creds = provider.get_credentials(scopes=["https://www.googleapis.com/auth/bigquery"])

            mock_auth_default.assert_called_once_with(scopes=["https://www.googleapis.com/auth/bigquery"])
            assert creds == mock_creds

    def test_get_credentials_no_scopes(self):
        with patch("baresquare_sdk.gcp.authentication.google.auth.default") as mock_auth_default:
            mock_creds = MagicMock(spec=Credentials)
            mock_auth_default.return_value = (mock_creds, "test-project")

            provider = ADCProvider()
            creds = provider.get_credentials()

            mock_auth_default.assert_called_once_with(scopes=[])
            assert creds == mock_creds


class TestGoogleAuth:
    @patch("baresquare_sdk.gcp.authentication.ServiceAccountProvider")
    def test_get_credentials_uses_service_account_provider_when_path_given(self, mock_sa_provider_cls):
        mock_sa_provider = MagicMock()
        mock_creds = MagicMock(spec=Credentials)
        mock_sa_provider.get_credentials.return_value = mock_creds
        mock_sa_provider_cls.return_value = mock_sa_provider

        auth = GoogleAuth(service_account_path="/key.json")
        creds = auth.get_credentials(scopes=["scope-a"])

        mock_sa_provider_cls.assert_called_once_with(key_path="/key.json")
        mock_sa_provider.get_credentials.assert_called_once_with(["scope-a"])
        assert creds == mock_creds

    @patch("baresquare_sdk.gcp.authentication.ServiceAccountProvider")
    def test_get_credentials_uses_service_account_provider_when_info_given(self, mock_sa_provider_cls):
        mock_sa_provider = MagicMock()
        mock_creds = MagicMock(spec=Credentials)
        mock_sa_provider.get_credentials.return_value = mock_creds
        mock_sa_provider_cls.return_value = mock_sa_provider

        auth = GoogleAuth(service_account_info={"client_email": "test@example.com"})
        creds = auth.get_credentials(scopes=["scope-b"])

        mock_sa_provider_cls.assert_called_once_with(info={"client_email": "test@example.com"})
        mock_sa_provider.get_credentials.assert_called_once_with(["scope-b"])
        assert creds == mock_creds

    @patch("baresquare_sdk.gcp.authentication.ADCProvider")
    def test_get_credentials_uses_adc_provider_when_no_path(self, mock_adc_provider_cls):
        mock_adc_provider = MagicMock()
        mock_creds = MagicMock(spec=Credentials)
        mock_adc_provider.get_credentials.return_value = mock_creds
        mock_adc_provider_cls.return_value = mock_adc_provider

        auth = GoogleAuth()
        creds = auth.get_credentials(scopes=["scope-b"])

        mock_adc_provider_cls.assert_called_once_with()
        mock_adc_provider.get_credentials.assert_called_once_with(["scope-b"])
        assert creds == mock_creds
