from typing import Any


class Sheets:
    def __init__(self, clients):
        self._svc = clients.sheets()
        self._drive = clients.drive()

    # === Sheet/tab-level methods ===

    def list_sheets(self, spreadsheet_id: str) -> list[dict[str, Any]]:
        """List the sheets in the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.

        Returns:
            A list of dictionaries containing the properties of the sheets.
        """
        meta = self._svc.spreadsheets().get(spreadsheetId=spreadsheet_id, fields="sheets(properties)").execute()
        return [s["properties"] for s in meta.get("sheets", [])]

    def add_sheet(self, spreadsheet_id: str, title: str, rows: int = 1000, cols: int = 26) -> int:
        """Add a sheet to the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            title: The title of the sheet.
            rows: The number of rows in the sheet.
            cols: The number of columns in the sheet.

        Returns:
            The ID of the new sheet.
        """
        body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {"title": title, "gridProperties": {"rowCount": rows, "columnCount": cols}}
                    }
                }
            ]
        }
        updates = self._svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        return updates["replies"][0]["addSheet"]["properties"]["sheetId"]

    def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> None:
        """Delete a sheet from the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            sheet_id: The ID of the sheet to delete.
        """
        body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}
        self._svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def rename_sheet(self, spreadsheet_id: str, sheet_id: int, new_title: str) -> None:
        """Rename a sheet in the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            sheet_id: The ID of the sheet to rename.
            new_title: The new title of the sheet.
        """
        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "title": new_title,
                        },
                        "fields": "title",
                    }
                }
            ]
        }
        self._svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def duplicate_sheet(self, spreadsheet_id: str, sheet_id: int) -> None:
        """Duplicate a sheet within the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            sheet_id: The ID of the source sheet to duplicate.
        """
        body = {
            "requests": [
                {
                    "duplicateSheet": {
                        "sourceSheetId": sheet_id,
                    }
                }
            ]
        }
        self._svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    # === Cell-level methods ===

    def get_values(self, spreadsheet_id: str, sheet_id: int, range: str) -> list[list[Any]]:
        """Get the values of a range of cells in the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            sheet_id: The ID of the sheet.
            range: The range of cells to get the values of.
        """
        # Find the sheet title from the provided sheet_id
        title: str | None = None
        for props in self.list_sheets(spreadsheet_id):
            if props.get("sheetId") == sheet_id:
                title = props.get("title")
                break
        if not title:
            raise ValueError(f"Sheet with id {sheet_id} not found in spreadsheet {spreadsheet_id}")

        a1_range = f"'{title}'!{range}"
        resp = self._svc.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=a1_range).execute()
        return resp.get("values", [])

    def set_values(self, spreadsheet_id: str, sheet_id: int, range: str, values: list[list[Any]]) -> None:
        """Set the values of a range of cells in the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            sheet_id: The ID of the sheet.
            range: The range of cells to set the values of.
            values: The values to set in the cells.
        """
        title: str | None = None
        for props in self.list_sheets(spreadsheet_id):
            if props.get("sheetId") == sheet_id:
                title = props.get("title")
                break
        if not title:
            raise ValueError(f"Sheet with id {sheet_id} not found in spreadsheet {spreadsheet_id}")

        a1_range = f"'{title}'!{range}"
        body = {"values": values}
        self._svc.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=a1_range,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def append_row(
        self, spreadsheet_id: str, sheet_id: int, rows: list[list[Any]], input_option: str = "USER_ENTERED"
    ) -> None:
        """Append a row to the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            sheet_id: The ID of the sheet.
            rows: The rows to append to the sheet.
            input_option: The input option to use for the values.
        """
        title: str | None = None
        for props in self.list_sheets(spreadsheet_id):
            if props.get("sheetId") == sheet_id:
                title = props.get("title")
                break
        if not title:
            raise ValueError(f"Sheet with id {sheet_id} not found in spreadsheet {spreadsheet_id}")

        a1_range = f"'{title}'!A1:C10"
        body = {"values": rows}
        self._svc.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=a1_range,
            valueInputOption=input_option,
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    def clear_values(self, spreadsheet_id: str, sheet_id: int, range: str) -> None:
        """Clear the values of a range of cells in the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet.
            sheet_id: The ID of the sheet.
            range: The range of cells to clear the values of.
        """
        title: str | None = None
        for props in self.list_sheets(spreadsheet_id):
            if props.get("sheetId") == sheet_id:
                title = props.get("title")
                break
        if not title:
            raise ValueError(f"Sheet with id {sheet_id} not found in spreadsheet {spreadsheet_id}")

        a1_range = f"'{title}'!{range}"
        self._svc.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=a1_range,
        ).execute()
