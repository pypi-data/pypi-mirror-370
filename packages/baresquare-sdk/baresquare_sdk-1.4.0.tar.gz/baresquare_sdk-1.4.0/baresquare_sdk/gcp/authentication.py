from typing import Optional, Protocol, runtime_checkable

import google.auth
from google.auth.credentials import Credentials
from google.oauth2 import service_account


@runtime_checkable
class CredentialProvider(Protocol):
    """Create a protocol for credential providers."""

    def get_credentials(self, scopes: list[str] | None = None) -> Credentials:
        """Return (possibly scoped) credentials ready for google clients."""


class ServiceAccountProvider(CredentialProvider):
    """Use a service account key file to authenticate."""

    def __init__(self, key_path: str | None = None, info: dict | None = None, subject: Optional[str] = None):
        self._key_path = key_path
        self._info = info
        self._subject = subject

    def get_credentials(self, scopes: list[str] | None = None):
        if self._info:
            creds = service_account.Credentials.from_service_account_info(self._info)
        else:
            if not self._key_path:
                raise ValueError("key_path or info required")
            creds = service_account.Credentials.from_service_account_file(self._key_path)
        if self._subject:
            creds = creds.with_subject(self._subject)  # domain-wide delegation
        return creds.with_scopes(scopes or [])


class ADCProvider(CredentialProvider):
    """Use Google's Application Default Credentials (ADC) to authenticate.

    Simplify authentication by automatically finding credentials in a
    well-defined order:
    1. GOOGLE_APPLICATION_CREDENTIALS environment variable.
    2. User credentials set up via the gcloud CLI.
    3. The attached service account, when running on Google Cloud Platform (GCP).
    """

    def get_credentials(self, scopes: list[str] | None = None):
        creds, _ = google.auth.default(scopes=scopes or [])
        return creds


class GoogleAuth(CredentialProvider):
    """Authenticate using a service account key file or ADC.

    If a service account key file is provided, it will be used to authenticate.
    Else, ADC (Application Default Credentials) will be used.
    - Check for GOOGLE_APPLICATION_CREDENTIALS environment variable.
    - Check for user credentials set up via the gcloud CLI.
    - Check for the attached service account, when running on Google Cloud Platform (GCP).
    """

    def __init__(self, service_account_path: str | None = None):
        if service_account_path:
            self._provider = ServiceAccountProvider(key_path=service_account_path)
        else:
            self._provider = ADCProvider()

    def get_credentials(self, scopes: list[str] | None = None):
        return self._provider.get_credentials(scopes)
