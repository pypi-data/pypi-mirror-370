from __future__ import annotations

from typing import Any, Optional


class OlyptikError(Exception):
    """Base SDK error."""


class ApiError(OlyptikError):
    def __init__(self, status_code: int, message: str, data: Optional[Any] = None) -> None:
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.data = data


