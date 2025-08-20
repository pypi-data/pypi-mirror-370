# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Lance Authors
from typing import Any, Dict, Iterable, List

import pyarrow as pa

from .catalog import Catalog
from .utils import TableIdentifier


class DummyCatalog(Catalog):
    """No-op catalog for testing and local development，
    also for skip catalog operation"""

    def create_database(self, database: str, location: str) -> None:
        pass

    def drop_database(self, database: str) -> None:
        pass

    def convert_table_to_dataset_uri(self, identifier: TableIdentifier) -> str:
        return f"dummy://{identifier}"

    def register_lance_table(self, identifier: TableIdentifier, schema: Any) -> None:
        pass

    def list_tables(self, database: str) -> List[str]:
        return []

    def get_table(self, identifier: TableIdentifier) -> None:
        return None

    def table_exists(self, identifier: TableIdentifier) -> bool:
        return False

    def drop_table(self, identifier: TableIdentifier) -> None:
        pass

    def add_table_columns(
        self, identifier: TableIdentifier, fields: List[pa.Field]
    ) -> None:
        pass

    def drop_table_columns(self, identifier: TableIdentifier, columns: List[str]):
        pass

    def alter_table_columns(
        self, identifier: TableIdentifier, alter_columns: Iterable[Dict]
    ):
        pass

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "DummyCatalog":
        return cls()
