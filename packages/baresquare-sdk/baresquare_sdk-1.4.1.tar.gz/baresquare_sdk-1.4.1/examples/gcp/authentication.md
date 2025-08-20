# Authentication with GCP

This document outlines how to authenticate with Google Cloud Platform (GCP) using the `baresquare_sdk`. The authentication module provides different methods to suit various use cases.

## `GoogleAuth`

The main entry point for authentication is the `GoogleAuth` class. It uses Google's Application Default Credentials (ADC) by default, or a service account if you provide a key file path.

```python
from baresquare_sdk.gcp.authentication import GoogleAuth

# ADC by default (checks GOOGLE_APPLICATION_CREDENTIALS, gcloud, or attached SA)
auth = GoogleAuth()

# Or use a specific service account key file
auth = GoogleAuth(service_account_path="path/to/your/service_account.json")

# Or if you have loaded the service account info from a file, you can use it directly
auth = GoogleAuth(service_account_info=service_account_info)
```

If you are on a local environment and you use `.env` to store your credentials (e.g. `GOOGLE_APPLICATION_CREDENTIALS`), make sure to load the environment variables before using the `GoogleAuth` class.
```python
from dotenv import load_dotenv

load_dotenv()

auth = GoogleAuth()
```

## Credential Providers

Advanced: You can also use credential providers directly when you need finer control (e.g., domain-wide delegation). In most cases, prefer `GoogleAuth` above.

### 1. Application Default Credentials (ADC)

The `ADCProvider` uses Google's Application Default Credentials (ADC) to authenticate. This is the simplest method and is recommended for most cases. It automatically finds credentials in the following order:

1.  `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
2.  User credentials set up via the `gcloud` CLI (`gcloud auth application-default login`).
3.  The attached service account, when running on Google Cloud Platform (GCP).

**Usage:**

```python
from baresquare_sdk.gcp.authentication import ADCProvider

credentials = ADCProvider().get_credentials()
print(f"Authenticated with project: {credentials.project_id}")
```

To use ADC, you might need to set up your environment. For local development, you can authenticate using:
```bash
gcloud auth application-default login
```

### 2. Service Account

The `ServiceAccountProvider` uses a service account key file (JSON) to authenticate. This is useful for applications running outside of GCP or when you need to use a specific service account.

You can provide the path to the key file or the key file contents as a dictionary.

**Usage:**

```python
from baresquare_sdk.gcp.authentication import ServiceAccountProvider

# Using a key file path
credentials = ServiceAccountProvider(key_path="path/to/your/service_account.json").get_credentials()
print(f"Authenticated with project: {credentials.project_id}")

# Using key file info from a dictionary
import json

with open("path/to/your/service_account.json") as f:
    key_info = json.load(f)

credentials = ServiceAccountProvider(info=key_info).get_credentials()
print(f"Authenticated with project: {credentials.project_id}")
```

### Domain-Wide Delegation

If you need to impersonate a user with a service account (domain-wide delegation), you can specify the `subject` email address.

```python
from baresquare_sdk.gcp.authentication import ServiceAccountProvider

credentials = ServiceAccountProvider(
    key_path="path/to/your/service_account.json",
    subject="user.to.impersonate@example.com",
).get_credentials()
```
