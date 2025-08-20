from typing import Callable, Iterator


class PageIterator:
    """Generic iterator for Google API list endpoints with page tokens.

    Example:
        req = drive.files().list(q="name contains 'report'")
        for file in PageIterator(drive, req, "files", "nextPageToken"):
            print(file["id"], file["name"])
    """

    def __init__(
        self,
        service: object,
        request: object,
        item_field: str,
        token_field: str,
        page_size: int | None = None,
        transform: Callable[[dict], dict] | None = None,
    ):
        self._service = service
        self._request = request
        self._item_field = item_field
        self._token_field = token_field
        self._page_size = page_size
        self._transform = transform

    def __iter__(self) -> Iterator[dict]:
        page_token: str | None = None
        while True:
            if self._page_size:
                self._request.uri += f"&pageSize={self._page_size}"
            if page_token:
                self._request.uri += f"&pageToken={page_token}"

            resp: dict = self._request.execute()
            items = resp.get(self._item_field, [])
            if self._transform:
                items = [self._transform(it) for it in items]

            for it in items:
                yield it

            page_token = resp.get(self._token_field)
            if not page_token:
                break
