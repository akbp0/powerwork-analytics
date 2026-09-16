from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Generic, TypeVar

TRecord = TypeVar("TRecord")
TResult = TypeVar("TResult")


class BaseExtractor(ABC, Generic[TRecord]):
    """Turns a source file into a list of intermediate records."""

    @abstractmethod
    def extract(self, path: Path) -> list[TRecord]:
        ...


class BaseTransformer(ABC, Generic[TRecord, TResult]):
    """Turns extracted records into warehouse-ready dimension/fact rows."""

    @abstractmethod
    def transform(self, records: list[TRecord]) -> TResult:
        ...


class BaseLoader(ABC):
    """Persists data (raw or transformed) into a target store."""

    @abstractmethod
    def load(self, *args: Any, **kwargs: Any) -> None:
        ...
