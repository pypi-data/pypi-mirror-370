from unittest.mock import MagicMock, patch

import pytest

from baresquare_sdk.gcp.sheets import Sheets


class TestSheets__init__:
    def test_init_uses_injected_clients(self):
        mock_svc = MagicMock()
        mock_drive = MagicMock()

        class DummyClients:
            def sheets(self):
                return mock_svc

            def drive(self):
                return mock_drive

        clients = DummyClients()

        sheets = Sheets(clients)

        assert sheets._svc is mock_svc
        assert sheets._drive is mock_drive


class TestSheets__list_sheets:
    def test_list_sheets__returns_properties(self):
        # Arrange
        svc = MagicMock()
        spreadsheets = svc.spreadsheets.return_value
        spreadsheets.get.return_value.execute.return_value = {
            "sheets": [
                {"properties": {"sheetId": 1, "title": "One"}},
                {"properties": {"sheetId": 2, "title": "Two"}},
            ],
        }
        s = object.__new__(Sheets)
        s._svc = svc

        # Act
        result = Sheets.list_sheets(s, spreadsheet_id="sp-123")

        # Assert
        assert result == [
            {"sheetId": 1, "title": "One"},
            {"sheetId": 2, "title": "Two"},
        ]
        spreadsheets.get.assert_called_once_with(
            spreadsheetId="sp-123",
            fields="sheets(properties)",
        )

    def test_list_sheets__returns_empty_when_absent(self):
        svc = MagicMock()
        svc.spreadsheets().get().execute.return_value = {}
        s = object.__new__(Sheets)
        s._svc = svc

        result = Sheets.list_sheets(s, spreadsheet_id="sp-123")

        assert result == []


class TestSheets__add_sheet:
    def test_add_sheet__creates_and_returns_id(self):
        svc = MagicMock()
        spreadsheets = svc.spreadsheets.return_value
        spreadsheets.batchUpdate.return_value.execute.return_value = {
            "replies": [
                {"addSheet": {"properties": {"sheetId": 42}}},
            ],
        }
        s = object.__new__(Sheets)
        s._svc = svc

        new_id = Sheets.add_sheet(s, spreadsheet_id="sp-1", title="NewTab", rows=10, cols=5)

        assert new_id == 42
        spreadsheets.batchUpdate.assert_called_once()
        called_kwargs = spreadsheets.batchUpdate.call_args.kwargs
        assert called_kwargs["spreadsheetId"] == "sp-1"
        assert called_kwargs["body"]["requests"][0]["addSheet"]["properties"] == {
            "title": "NewTab",
            "gridProperties": {"rowCount": 10, "columnCount": 5},
        }


class TestSheets__delete_sheet:
    def test_delete_sheet__sends_request(self):
        svc = MagicMock()
        s = object.__new__(Sheets)
        s._svc = svc

        Sheets.delete_sheet(s, spreadsheet_id="sp-1", sheet_id=7)

        svc.spreadsheets().batchUpdate.assert_called_once_with(
            spreadsheetId="sp-1",
            body={"requests": [{"deleteSheet": {"sheetId": 7}}]},
        )


class TestSheets__rename_sheet:
    def test_rename_sheet__sends_request(self):
        svc = MagicMock()
        s = object.__new__(Sheets)
        s._svc = svc

        Sheets.rename_sheet(s, spreadsheet_id="sp-1", sheet_id=7, new_title="Renamed")

        svc.spreadsheets().batchUpdate.assert_called_once()
        body = svc.spreadsheets().batchUpdate.call_args.kwargs["body"]
        req = body["requests"][0]["updateSheetProperties"]
        assert req["properties"] == {"sheetId": 7, "title": "Renamed"}
        assert req["fields"] == "title"


class TestSheets__duplicate_sheet:
    def test_duplicate_sheet__sends_request(self):
        svc = MagicMock()
        s = object.__new__(Sheets)
        s._svc = svc

        Sheets.duplicate_sheet(s, spreadsheet_id="sp-1", sheet_id=9)

        svc.spreadsheets().batchUpdate.assert_called_once_with(
            spreadsheetId="sp-1",
            body={"requests": [{"duplicateSheet": {"sourceSheetId": 9}}]},
        )


class TestSheets__get_values:
    def test_get_values__builds_a1_and_returns_values(self):
        svc = MagicMock()
        values_api = svc.spreadsheets.return_value.values.return_value
        values_api.get.return_value.execute.return_value = {
            "values": [["A", "B"], [1, 2]],
        }
        s = object.__new__(Sheets)
        s._svc = svc
        with patch.object(Sheets, "list_sheets", return_value=[{"sheetId": 11, "title": "Tab"}]):
            values = Sheets.get_values(s, spreadsheet_id="sp-1", sheet_id=11, range="A1:B2")

        assert values == [["A", "B"], [1, 2]]
        values_api.get.assert_called_once_with(
            spreadsheetId="sp-1",
            range="'Tab'!A1:B2",
        )

    def test_get_values__unknown_sheet_raises(self):
        s = object.__new__(Sheets)
        s._svc = MagicMock()
        with (
            patch.object(Sheets, "list_sheets", return_value=[{"sheetId": 1, "title": "Tab"}]),
            pytest.raises(ValueError),
        ):
            Sheets.get_values(s, spreadsheet_id="sp-1", sheet_id=2, range="A1:A1")


class TestSheets__set_values:
    def test_set_values__updates_range(self):
        svc = MagicMock()
        s = object.__new__(Sheets)
        s._svc = svc
        with patch.object(Sheets, "list_sheets", return_value=[{"sheetId": 5, "title": "TabX"}]):
            Sheets.set_values(
                s,
                spreadsheet_id="sp-1",
                sheet_id=5,
                range="C3:D4",
                values=[["x", "y"], [3, 4]],
            )

        svc.spreadsheets().values().update.assert_called_once_with(
            spreadsheetId="sp-1",
            range="'TabX'!C3:D4",
            valueInputOption="USER_ENTERED",
            body={"values": [["x", "y"], [3, 4]]},
        )


class TestSheets__append_row:
    def test_append_row__appends_with_insert_rows(self):
        svc = MagicMock()
        s = object.__new__(Sheets)
        s._svc = svc
        with patch.object(Sheets, "list_sheets", return_value=[{"sheetId": 3, "title": "Data"}]):
            Sheets.append_row(
                s,
                spreadsheet_id="sp-1",
                sheet_id=3,
                rows=[[1, 2, 3]],
                input_option="RAW",
            )

        svc.spreadsheets().values().append.assert_called_once_with(
            spreadsheetId="sp-1",
            range="'Data'!A1:C10",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [[1, 2, 3]]},
        )


class TestSheets__clear_values:
    def test_clear_values__clears_range(self):
        svc = MagicMock()
        s = object.__new__(Sheets)
        s._svc = svc
        with patch.object(Sheets, "list_sheets", return_value=[{"sheetId": 8, "title": "ClearMe"}]):
            Sheets.clear_values(s, spreadsheet_id="sp-1", sheet_id=8, range="A1:D9")

        svc.spreadsheets().values().clear.assert_called_once_with(
            spreadsheetId="sp-1",
            range="'ClearMe'!A1:D9",
        )
