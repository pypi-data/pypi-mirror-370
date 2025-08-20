# Google Sheets

This document outlines how to use Google Sheets with the `baresquare_sdk`.

## Initialize

```python
from dotenv import load_dotenv

from baresquare_sdk.gcp.authentication import GoogleAuth
from baresquare_sdk.gcp.clients import GCPClients
from baresquare_sdk.gcp.sheets import Sheets

load_dotenv()

sheets = Sheets(GCPClients(GoogleAuth()))
```

## Sheet/tab-level methods

### List sheets

```python
print(sheets.list_sheets("<file_id>"))
```

### Add sheet

```python
print(sheets.add_sheet("<file_id>", "<sheet_name>"))
```

### Delete sheet

```python
print(sheets.delete_sheet("<file_id>", "<sheet_id>"))
```

### Rename sheet

```python
print(sheets.rename_sheet("<file_id>", "<sheet_id>", "<new_name>"))
```

### Duplicate sheet

```python
print(sheets.duplicate_sheet("<file_id>", "<sheet_id>"))
```

## Value-level methods

### Get values

```python
print(sheets.get_values("<file_id>", "<sheet_id>", "<range>"))
```

### Set values

```python
print(sheets.set_values("<file_id>", "<sheet_id>", "<range>", "<values>"))
```

### Append row

```python
rows = [["Hello", "World", "!"]]
print(sheets.append_row("<file_id>", "<sheet_id>", rows))
```

### Clear values

```python
print(sheets.clear_values("<file_id>", "<sheet_id>", "<range>"))
```
