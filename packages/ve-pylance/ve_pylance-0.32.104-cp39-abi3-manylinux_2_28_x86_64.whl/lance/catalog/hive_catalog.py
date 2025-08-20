# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Lance Authors

import logging
import re
from typing import Any, Dict, Iterable, List, Optional, Union

import pyarrow as pa
from hive_metastore_client import HiveMetastoreClient
from hive_metastore_client.builders import (
    ColumnBuilder,
    SerDeInfoBuilder,
    StorageDescriptorBuilder,
    TableBuilder,
)
from thrift_files.libraries.thrift_hive_metastore_client.ttypes import (
    Database as HiveDatabase,
)
from thrift_files.libraries.thrift_hive_metastore_client.ttypes import (
    FieldSchema,
)
from thrift_files.libraries.thrift_hive_metastore_client.ttypes import (
    Table as HiveTable,
)

from .catalog import Catalog
from .exceptions import NoSuchDatabaseError, NoSuchTableError
from .utils import TableIdentifier, Utils

# Type aliases

# Logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Configuration constants
LIST_ALL_TABLES = "list-all-tables"
LIST_ALL_TABLES_DEFAULT = "false"
TABLE_TYPE_PROP = "table_type"
TABLE_STORAGE_OPTIONS_PROP = "table_storage"
LANCE_TABLE_TYPE_VALUE = "lance"
HIVE_METASTORE_URIS = "hive.metastore.uris"


class HiveCatalog(Catalog):
    """Hive Catalog Manager implementing database-table paradigm."""

    _URI_PATTERN = re.compile(r"^thrift://([\w.-]+):(\d+)$")  # Domain/IP validation

    def __init__(self, metastore_host: str, metastore_port: int = 9083):
        """
        Initialize Hive Metastore connection.

        Args:
            metastore_host: Hive Metastore service host
            metastore_port: Thrift service port (default: 9083)
        """
        self.client = HiveMetastoreClient(metastore_host, metastore_port)
        self._verify_connection()

    @classmethod
    def from_config(cls, config: Dict[str, Union[str, List[str]]]) -> "HiveCatalog":
        uris = config.get(HIVE_METASTORE_URIS) or config.get("hive_metastore_uris")
        if not uris:
            raise ValueError(f"Configuration key '{HIVE_METASTORE_URIS}' is required")

        candidates = [uris] if isinstance(uris, str) else uris

        for uri in candidates[:1]:  # Process first element only
            stripped_uri = str(uri).strip()
            if match := cls._URI_PATTERN.match(stripped_uri):
                host, port_str = match.groups()
                if 0 < (port := int(port_str)) <= 65535:
                    return cls(host, port)
                raise ValueError(f"Invalid port range: {port}")

        raise RuntimeError(
            f"No valid Thrift URI found in: {uris}\n"
            "Expected format: thrift://<host>:<port>"
        )

    def _verify_connection(self) -> None:
        """Validate metastore connection."""
        try:
            with self.client as cli:
                cli.get_all_databases()
        except Exception as e:
            logging.error("Metastore connection failed: %s", str(e))
            raise RuntimeError("Hive Metastore connection failure") from e

    # Database operations -----------------------------------------------------
    def create_database(
        self,
        database_name: str,
        location: str,
    ):
        """
        Create new database.

        Args:
            database_name: Name of database to create
            location: Storage location URI

        Returns:
            Created database object
        """
        db = HiveDatabase(
            name=database_name,
            locationUri=location,
            description="lance database",
            parameters={},
        )

        try:
            with self.client as cli:
                cli.create_database(db)
                logging.info("Created database: %s", database_name)
                return db
        except Exception as e:
            if "already exists" in str(e):
                logging.warning("Database %s already exists", database_name)
                return self.get_database(database_name)
            raise RuntimeError(f"Database creation failed: {str(e)}") from e

    def drop_database(self, database_name: str, cascade: bool = False) -> None:
        """Drop existing database."""
        try:
            with self.client as cli:
                cli.drop_database(database_name, cascade, False)
                logging.info("Dropped database: %s", database_name)
        except Exception as e:
            if "No such database" in str(e):
                raise NoSuchDatabaseError(f"Database {database_name} not found") from e
            raise RuntimeError(f"Database deletion failed: {str(e)}") from e

    def list_databases(self) -> List[str]:
        """List all databases."""
        with self.client as cli:
            return cli.get_all_databases()

    def get_database(self, database_name: str) -> HiveDatabase:
        """Retrieve database metadata."""
        with self.client as cli:
            try:
                return cli.get_database(database_name)
            except Exception as e:
                raise NoSuchDatabaseError(f"Database {database_name} not found") from e

    # Table operations --------------------------------------------------------
    def register_lance_table_location(
        self,
        database_name: str,
        table_name: str,
        schema: List[Dict[str, str]],
        location: str,
    ) -> HiveTable:
        """
        Create new table.

        Args:
            database_name: Target database name
            table_name: Table name to create
            schema: List of column definitions
            location: Storage location URI
            file_format: File format (PARQUET/ORC/TEXTFILE)

        Returns:
            Created table object
        """

        # mock with parquet format
        file_format: str = "LANCE"

        columns = [
            ColumnBuilder(
                name=field_column.column_name,
                type=field_column.column_type,
                comment=field_column.column_desc,
            ).build()
            for field_column in schema
        ]

        serde_info = SerDeInfoBuilder(
            serialization_lib=self._get_serde_lib(file_format)
        ).build()

        storage_desc = StorageDescriptorBuilder(
            columns=columns,
            location=location,
            input_format=self._get_input_format(file_format),
            output_format=self._get_output_format(file_format),
            serde_info=serde_info,
        ).build()

        table = TableBuilder(
            table_name=table_name,
            db_name=database_name,
            storage_descriptor=storage_desc,
            parameters={TABLE_TYPE_PROP: LANCE_TABLE_TYPE_VALUE},
        ).build()

        try:
            with self.client as cli:
                cli.create_table(table)
                logging.info("Created table: %s.%s", database_name, table_name)
                return table
        except Exception as e:
            if "already exists" in str(e):
                logging.warning("Table %s.%s exists", database_name, table_name)
                return self.get_table((database_name, table_name))
            raise RuntimeError(f"Table creation failed: {str(e)}") from e

    def list_tables(self, database_name: str) -> List[str]:
        """List tables in specified database."""
        try:
            with self.client as cli:
                return cli.get_all_tables(database_name)
        except Exception as e:
            raise NoSuchDatabaseError(f"Database {database_name} not found") from e

    def table_exists(self, identifier: TableIdentifier) -> bool:
        """
        Check table existence in catalog.

        Args:
            identifier: Table identifier (str or tuple)

        Returns:
            True if table exists, False otherwise
        """
        try:
            return self.get_table(identifier) is not None
        except Exception:
            return False

    def get_table(self, identifier: TableIdentifier) -> HiveTable:
        """Retrieve table metadata."""
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        with self.client as cli:
            try:
                return cli.get_table(db_name, tbl_name)
            except Exception as e:
                raise NoSuchTableError(
                    f"Table {db_name}.{tbl_name} not found in Hive metastore"
                ) from e

    def drop_table(self, identifier: TableIdentifier) -> None:
        """Remove existing table."""
        try:
            database_name, table_name = Utils.identifier_to_database_and_table(
                identifier
            )
            with self.client as cli:
                cli.drop_table(database_name, table_name, True)
                logging.info("Dropped table: %s.%s", database_name, table_name)
        except Exception as e:
            if "No such table" in str(e):
                raise NoSuchTableError(
                    f"Table {database_name}.{table_name} not found"
                ) from e
            raise RuntimeError(f"Table deletion failed: {str(e)}") from e

    def add_table_columns(self, identifier: TableIdentifier, fields: List[pa.Field]):
        columns = [
            ColumnBuilder(
                name=field.name,
                type=Utils.arrow_to_hive_type(field.type),
                comment="Added from Lance by add_columns",
            ).build()
            for field in fields
        ]
        database_name, table_name = Utils.identifier_to_database_and_table(identifier)
        try:
            with self.client as cli:
                cli.add_columns_to_table(database_name, table_name, columns)
                logging.info("add columns to table: %s.%s", database_name, table_name)
        except Exception:
            logging.warning(
                "Failed to sync columns for table: %s.%s in hive metadata",
                database_name,
                table_name,
            )

    def drop_table_columns(self, identifier: TableIdentifier, columns: List[str]):
        database_name, table_name = Utils.identifier_to_database_and_table(identifier)
        try:
            with self.client as cli:
                cli.drop_columns_from_table(database_name, table_name, columns)
                logging.info("Dropped columns: %s.%s", database_name, table_name)
        except Exception:
            logging.warning(
                "Failed to sync columns for table: %s.%s in hive metadata",
                database_name,
                table_name,
            )

    def alter_table_columns(
        self,
        identifier: TableIdentifier,
        alterations: Iterable[Dict],  # Modified parameter type
    ):
        """Alter column definitions in Hive metastore

        Parameters
        ----------
        identifier : TableIdentifier
            The table identifier to alter
        alterations : Iterable[Dict[str, Any]]
            A sequence of dictionaries, each with the following keys:

            - "path": str
                The column path to alter. For a top-level column, this is the name.
                For a nested column, this is the dot-separated path, e.g. "a.b.c".
            - "name": str, optional
                The new name of the column. If not specified, the column name is
                not changed.
            - "nullable": bool, optional
                Whether the column should be nullable. If not specified, the column
                nullability is not changed. Only non-nullable columns can be changed
                to nullable. Currently, you cannot change a nullable column to
                non-nullable.
            - "data_type": pyarrow.DataType, optional
                The new data type to cast the column to. If not specified, the column
                data type is not changed.
        """
        database_name, table_name = Utils.identifier_to_database_and_table(identifier)
        hive_table = self.get_table(identifier)

        try:
            # Use dictionary to map paths to new columns
            path_to_new_col = {}
            for alter in alterations:
                path = alter["path"]
                # Find original column object
                original_col = next(
                    (c for c in hive_table.sd.cols if c.name == path), None
                )

                if not original_col:
                    logging.warning(
                        "Column %s not found in Hive table %s", path, table_name
                    )
                    continue

                # Deep clone original column
                new_col = FieldSchema()
                new_col.__dict__.update(
                    original_col.__dict__
                )  # Keep other attributes unchanged

                # Apply field modifications atomically
                if "name" in alter:
                    new_col.name = alter["name"]
                if "data_type" in alter:
                    new_col.type = Utils.arrow_to_hive_type(alter["data_type"])

                # Store with original path as key
                path_to_new_col[path] = new_col

            # Build new column list preserving order
            new_cols = []
            for orig_col in hive_table.sd.cols:
                # Prioritize modified column objects
                updated_col = path_to_new_col.get(orig_col.name, orig_col)
                new_cols.append(updated_col)

            # Perform metadata update
            with self.client as cli:
                hive_table.sd.cols = new_cols
                cli.alter_table(
                    dbname=database_name, tbl_name=table_name, new_tbl=hive_table
                )
                logging.info(
                    "Altered %d columns in Hive table %s.%s",
                    len(path_to_new_col),
                    database_name,
                    table_name,
                )

        except Exception as e:
            logging.exception(
                "Failed to alter columns in Hive table %s.%s: %s",
                database_name,
                table_name,
                str(e),
            )
            raise Exception(f"Hive metadata sync failed: {str(e)}") from e

    # Helper methods ----------------------------------------------------------
    @staticmethod
    def _get_serde_lib(file_format: str) -> str:
        """Get serialization library for specified file format."""
        format_map = {
            "PARQUET": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
            "ORC": "org.apache.hadoop.hive.ql.io.orc.OrcSerde",
            "TEXTFILE": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
            "LANCE": "LANCE",
        }
        return format_map.get(file_format.upper(), format_map["TEXTFILE"])

    @staticmethod
    def _get_input_format(file_format: str) -> str:
        """Get input format class."""
        format_map = {
            "PARQUET": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "ORC": "org.apache.hadoop.hive.ql.io.orc.OrcInputFormat",
            "TEXTFILE": "org.apache.hadoop.mapred.TextInputFormat",
            "LANCE": "LANCE",
        }
        return format_map.get(file_format.upper(), format_map["TEXTFILE"])

    @staticmethod
    def _get_output_format(file_format: str) -> str:
        """Get output format class."""
        format_map = {
            "PARQUET": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "ORC": "org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat",
            "TEXTFILE": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            "LANCE": "LANCE",
        }
        return format_map.get(file_format.upper(), format_map["TEXTFILE"])

    def convert_table_to_dataset_uri(self, identifier: TableIdentifier) -> str:
        """Convert table identifier to dataset URI."""
        try:
            return self.get_table(identifier).sd.location
        except Exception as e:
            logging.exception("Table not found: %s", identifier)
            raise NoSuchTableError("Table lookup failed: %s", e)

    def register_lance_table(
        self, identifier: TableIdentifier, field_columns: Optional[List[Any]] = None
    ) -> HiveTable:
        """
        Register LAS catalog table under specified database.

        Args:
            identifier: Table identifier
            field_columns: Optional schema definition

        Returns:
            Newly registered table
        """
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        db = self.get_database(db_name)
        tbl_location = f"{db.locationUri.rstrip('/')}/{tbl_name}.lance"

        return self.register_lance_table_location(
            database_name=db_name,
            table_name=tbl_name,
            schema=field_columns or [],
            location=tbl_location,
        )
