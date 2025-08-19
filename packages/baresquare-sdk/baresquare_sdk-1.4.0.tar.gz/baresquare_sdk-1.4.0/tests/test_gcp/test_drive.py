from unittest.mock import MagicMock, patch

from baresquare_sdk.gcp.clients import GCPClients
from baresquare_sdk.gcp.drive import Drive


class TestDrive__init__:
    def test_init_with_gcpclients_uses_injected_client(self):
        mock_drive_client = MagicMock()

        class DummyClients(GCPClients):
            pass

        mock_clients = object.__new__(DummyClients)
        mock_clients.drive = MagicMock(return_value=mock_drive_client)

        drive = Drive(source=mock_clients)

        assert drive._client is mock_drive_client
        mock_clients.drive.assert_called_once_with()

    @patch("baresquare_sdk.gcp.drive.gbuild")
    def test_init_with_credentialprovider_builds_client(self, mock_gbuild):
        mock_credentials = MagicMock()
        mock_client = MagicMock()
        mock_gbuild.return_value = mock_client

        class DummyCreds:
            def get_credentials(self, scopes=None):  # noqa: D401 - simple provider for tests
                return mock_credentials

        drive = Drive(source=DummyCreds())

        assert drive._client is mock_client
        mock_gbuild.assert_called_once_with(
            "drive",
            "v3",
            credentials=mock_credentials,
            cache_discovery=False,
        )


class TestDrive__list_files:
    @patch("baresquare_sdk.gcp.drive.PageIterator")
    def test_list_files_builds_request_and_returns_page_iterator(self, mock_page_iterator_cls):
        # Arrange client chain: files().list(...)
        mock_request = MagicMock()
        mock_files = MagicMock()
        mock_files.list.return_value = mock_request
        mock_client = MagicMock()
        mock_client.files.return_value = mock_files

        # PageIterator should be constructed and returned
        sentinel_iter = iter([{"id": "1"}])
        mock_page_iterator_cls.return_value = sentinel_iter

        drive = object.__new__(Drive)
        drive._client = mock_client

        # Act
        result_iter = Drive.list_files(drive, q="name contains 'report'", page_size=55)

        # Assert client call chain
        mock_client.files.assert_called_once_with()
        mock_files.list.assert_called_once_with(
            q="name contains 'report'",
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, webViewLink, owners, permissions, parents)",
            pageSize=55,
        )

        # Assert PageIterator constructed correctly and returned
        mock_page_iterator_cls.assert_called_once_with(mock_client, mock_request, "files", "nextPageToken")
        assert result_iter is sentinel_iter


class TestDrive__get_file_metadata:
    def test_get_file_metadata_calls_api_with_expected_fields(self):
        # Arrange client chain: files().get(...).execute()
        expected_response = {"id": "abc", "name": "foo"}
        mock_get = MagicMock()
        mock_get.execute.return_value = expected_response
        mock_files = MagicMock()
        mock_files.get.return_value = mock_get
        mock_client = MagicMock()
        mock_client.files.return_value = mock_files

        drive = object.__new__(Drive)
        drive._client = mock_client

        # Act
        result = Drive.get_file_metadata(drive, file_id="abc")

        # Assert call chain and fields
        mock_client.files.assert_called_once_with()
        mock_files.get.assert_called_once_with(
            fileId="abc",
            fields="id, name, driveId, mimeType, createdTime, modifiedTime, webViewLink, parents, owners, permissions",
        )
        mock_get.execute.assert_called_once_with()
        assert result == expected_response
