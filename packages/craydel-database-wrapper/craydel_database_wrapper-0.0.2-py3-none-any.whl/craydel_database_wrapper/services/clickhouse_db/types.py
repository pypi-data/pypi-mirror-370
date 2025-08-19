from __future__ import annotations
from typing import Any, Protocol, Sequence, Mapping, Optional, List

class QueryResult(Protocol):
    result_rows: List[Sequence[Any]]
    column_names: Optional[List[str]]

class ClickhouseHelper(Protocol):
    def insert(self, table: str, rows: Sequence[Sequence[Any]], column_names: Sequence[str]) -> None: ...
    def query(self, sql: str, parameters: Optional[Mapping[str, Any]] = None) -> QueryResult: ...
    def command(self, sql: str, parameters: Optional[Mapping[str, Any]] = None) -> None: ...

class SearchServiceClickhouseHelper(ClickhouseHelper, Protocol):
    """Alias Protocol for search service DBs."""
    ...
