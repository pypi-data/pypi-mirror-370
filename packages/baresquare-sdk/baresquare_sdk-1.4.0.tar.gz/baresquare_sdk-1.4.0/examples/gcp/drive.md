# Google Drive

This document outlines how to use (Google) Drive with the `baresquare_sdk`.

## Initialize

```python
from dotenv import load_dotenv

from baresquare_sdk.gcp.authentication import GoogleAuth
from baresquare_sdk.gcp.drive import Drive

load_dotenv()

drive = Drive(GoogleAuth())
```

Alternatively, you can pass in a `GCPClients` instance instead of a `CredentialProvider`.
```python
from dotenv import load_dotenv

from baresquare_sdk.gcp.authentication import GoogleAuth
from baresquare_sdk.gcp.clients import GCPClients
from baresquare_sdk.gcp.drive import Drive

load_dotenv()

gcp = GCPClients(GoogleAuth())
drive = Drive(gcp)
```

## List files

Use the `list_files` method to list files in the Drive. using `q` to filter the files.

```python
# Search by file type
for f in drive.list_files(q="mimeType='application/vnd.google-apps.spreadsheet'"):
    print(f["id"], f["name"], f["mimeType"], f["webViewLink"])
# Search by partial name
for f in drive.list_files(q="name contains 'partnerships'"):
    print(f["id"], f["name"])
# Search by author
for f in drive.list_files(q="'example@domain.com' in owners"):
    print(f["id"], f["name"])
# Get all files
for f in drive.list_files(q=""):
    print(f["id"])
```


## Get file metadata

If you know the file ID, you can get the metadata of the file using the `get_file_metadata` method.

```python
import json

print(json.dumps(drive.get_file_metadata("your-file-id"), indent=4))
# {
#     "owners": [
#         {
#             "displayName": "example.user",
#             "kind": "drive#user",
#             "me": false,
#             "permissionId": "06031940402791602308",
#             "emailAddress": "example.user@domain.com",
#             "photoLink": "https://lh3.googleusercontent.com/a-/example-user-photo-id=s64"
#         }
#     ],
#     "id": "example-file-id",
#     "name": "example-file-name",
#     "mimeType": "application/vnd.google-apps.spreadsheet",
#     "webViewLink": "https://docs.google.com/spreadsheets/d/example-file-id/edit?usp=drivesdk",
#     "modifiedTime": "2025-08-18T07:49:16.434Z"
# }
```