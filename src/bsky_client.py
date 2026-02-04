from __future__ import annotations

import time
from typing import Optional

from atproto import Client


class BlueskyClient:
    def __init__(self, handle: str, app_password: str) -> None:
        self.handle = handle
        self.app_password = app_password
        self.client: Optional[Client] = None

    def login(self) -> None:
        if self.client is None:
            self.client = Client()
        self.client.login(self.handle, self.app_password)

    def post(self, text: str, max_retries: int = 3) -> str:
        if self.client is None:
            self.login()

        attempt = 0
        while True:
            try:
                response = self.client.send_post(text)
                return response.uri
            except Exception:  # pragma: no cover - network-dependent
                attempt += 1
                if attempt >= max_retries:
                    raise
                sleep_for = 2 ** attempt
                time.sleep(sleep_for)
