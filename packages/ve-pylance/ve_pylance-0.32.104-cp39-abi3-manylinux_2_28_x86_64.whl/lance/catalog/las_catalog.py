# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Lance Authors
import copy
import logging
import os
from functools import wraps
from typing import Any, Dict, Iterable, List, Optional, TypeVar

import pyarrow as pa

# Importing classes from a hypothetical LAS REST library
from las.catalog.core.catalog_client import CatalogClient
from las.catalog.core.entity.database_builder import DatabaseBuilder
from las.catalog.core.entity.table import FieldColumn, FileFormat, PartitionType, Table
from las.catalog.core.entity.table_builder import TableBuilder

from .catalog import Catalog
from .utils import TableIdentifier, Utils

# Setting up the logging configuration
T = TypeVar("T")

# Configure basic logging format and level
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get logger instance
logger = logging.getLogger(__name__)

# Various constants used for setting up the catalog and managing tables
LIST_ALL_TABLES = "list-all-tables"
LIST_ALL_TABLES_DEFAULT = "false"
TABLE_TYPE_PROP = "table_type"
LANCE_DATASET_TYPE_VALUE = "lance"
TABLE_STORAGE_OPTIONS_PROP = "table_storage"
HMS_TABLE_OWNER = "hive.metastore.table.owner"
HMS_DB_OWNER_TYPE = "hive.metastore.database.owner-type"
HMS_DB_OWNER = "hive.metastore.database.owner"
STORAGE_OPTIONS_AK = "access_key_id"
STORAGE_OPTIONS_SK = "secret_access_key"
STORAGE_OPTIONS_ENDPOINT = "aws_endpoint"
STORAGE_OPTIONS_VIRTUAL_HOSTED = "virtual_hosted_style_request"


def future_feature(message="altering lance table is not supported yet in LAS Catalog"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


class LasCatalog(Catalog):
    """
    A class to manage the LAS Catalog, including creating namespaces, listing catalogs,
    and integrating with AWS services via CatalogClient.
    """

    def __init__(
        self,
        access_key=None,
        secret_key=None,
        sts_token=None,
        region=None,
        catalog_name=None,
        env="online",
        storage_config: dict = None,
    ):
        """
        Initializes the LasCatalog object either from individual parameters
        or a dictionary storing all configurations.

        Parameters:
            access_key (str): Access key for authentication
            secret_key (str): Secret key for authentication
            sts_token (str): Optional STS token for temporary access.
            region (str): The region where the catalog is hosted.
            catalog_name (str): The name of the catalog.
            env (str): Environment setting, default is "online".
            storage_config (dict): Dictionary containing configurations.
        """

        def get_param(config_dict, keys, default=None):
            if config_dict:
                for key in [k for k in keys if k in config_dict]:
                    return config_dict[key]
            return default

        # Initialize configuration parameters
        self.access_key = get_param(
            storage_config, ["access_key", "access_key_id"], access_key
        )
        self.secret_key = get_param(
            storage_config, ["secret_key", "secret_access_key"], secret_key
        )
        self.region = get_param(storage_config, ["region", "aws_region"], region)

        # Directly initialized parameters
        self.sts_token = get_param(storage_config, ["sts_token"], sts_token)
        self.catalog_name = get_param(storage_config, ["catalog_name"], catalog_name)
        self.env = get_param(storage_config, ["env"], env)
        self.catalog_properties = {}

        if not all([self.access_key, self.secret_key, self.region, self.catalog_name]):
            raise ValueError(
                "Missing required parameters: access_key/access_key_id, "
                "secret_key/secret_access_key, region/aws_region, catalog_name"
            )

        # Initialize environment variables and CatalogClient
        # for interacting with the LAS catalog
        os.environ["CATALOG_ENVIRONMENT"] = self.env
        self.las_catalog_client = CatalogClient(
            self.access_key,
            self.secret_key,
            self.sts_token,
            self.region,
            self.catalog_name,
        )

    @classmethod
    def from_config(cls, config: dict):
        """
        Class method to create an instance of LasCatalog
        from a configuration dictionary directly.

        Parameters:
            config (dict): Dictionary containing
            all configurations for the LasCatalog.

        Returns:
            LasCatalog: An instance of LasCatalog.
        """
        return cls(storage_config=config)

    def set_catalog(self, catalog_name: str):
        """
        Sets the catalog name and updates the underlying catalog client.

        Parameters:
            catalog_name (str): Name of the catalog to set.
        """
        self.catalog_name = catalog_name
        self.las_catalog_client.catalog_name = (
            catalog_name  # Assuming CatalogClient has an attribute `catalog_name`
        )

    def list_catalogs(self):
        """
        Retrieves a list of all catalogs available in the LAS  environment.

        This method uses the `las_catalog_client`
        to make the API call and returns the list of catalogs.

        Returns:
            list: A list of catalog names.

        Example:
            >>> # Assuming 'las_catalog' is an instance of LasCatalog
            >>> catalogs = self.las_catalog_client.list_catalogs()
            >>> print(catalogs)
            ['catalog1', 'catalog2', 'catalog3']
        """
        catalog_list = self.las_catalog_client.list_catalogs()
        return catalog_list

    def list_databases(self, catalog_name: str):
        """
        List all databases in a given catalog.

        This method takes a catalog name and
        returns a list of all databases in that catalog.

        Args:
            catalog_name (str): The name of the catalog.

        Returns:
            list: A list of database names.

        Raises:
            Exception: If an error occurs while retrieving the databases.
        """
        try:
            # Try to get all databases from the LAS catalog client
            database_names = self.las_catalog_client.get_all_databases(catalog_name)
            # Return the list of database names
            return database_names
        except Exception as e:
            # Log an error message if the catalog does not exist
            logger.error("catalog does not exist: %s", e)

    def list_tables(self, database: str) -> list[str]:
        """
        List all tables in a given database.

        This method takes a database name and
        returns a list of all tables in that database.

        Args:
            database (str): The name of the database.

        Returns:
            list: A list of dataset names.

        Raises:
            Exception: If an error occurs while retrieving the tables.
        """
        try:
            # Try to get all tables from the LAS catalog client
            tbl_names = self.las_catalog_client.get_all_tables(
                database, self.catalog_name
            )
            # Return the list of table names
            return tbl_names
        except Exception as e:
            # Log an error message if the database does not exist
            logger.error("Database does not exist: %s", e)
            return []

    def create_database(self, database_name, location):
        database = (
            DatabaseBuilder(
                name=database_name, location=location, catalog_name=self.catalog_name
            )
            .with_description("lance database")
            .build()
        )

        try:
            self.las_catalog_client.create_database(database)
        except Exception as e:
            logger.error("Database %s already exists", database_name)
            raise e
        return database_name

    def drop_database(self, database_name: str) -> None:
        """Drop a namespace.

        Args:
            database_name: Namespace identifier.

        Raises:
            NoSuchNamespaceError: If a namespace with the name does not exist,
             or the identifier is invalid.
            NamespaceNotEmptyError: If the namespace is not empty.
        """
        try:
            self.las_catalog_client.drop_database(database_name, self.catalog_name)
        except Exception as e:
            raise Exception(f"Database {database_name} is not empty") from e

    def drop_table(self, identifier: TableIdentifier, purge=False):
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        try:
            self.las_catalog_client.drop_table(self.catalog_name, db_name, tbl_name)
            if purge:
                self.purge_data(identifier)

            logger.info("Dropped table: %s", identifier)
            return True

        except Exception:
            logger.info("Skipping drop, table does not exist")
            return False

    def purge_data(self, identifier: TableIdentifier):
        # Example function to delete data given location
        # Implementation depends on data storage details
        pass

    def list_namespaces(self):
        """List namespaces from the given namespace.
        If not given, list top-level namespaces from the catalog.

        Returns:
            List[Identifier]: a List of namespace identifiers.
        """
        # Hierarchical namespace is not supported. Return an empty list
        return self.las_catalog_client.get_all_databases()

    def get_table(self, identifier: TableIdentifier) -> Optional[Table]:
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        try:
            return self.las_catalog_client.get_table(
                tbl_name, db_name, self.catalog_name
            )
        except Exception as e:
            logger.debug("Table not found", exc_info=e)
            return None

    def table_exists(self, identifier: TableIdentifier) -> bool:
        """
        Check if a table exists in the LAS catalog.

        This method takes a table identifier
        and returns True if the table exists, False otherwise.

        Args:
            identifier (TableIdentifier): The identifier for the table,
             which can be a string or a tuple of strings.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        # Convert the identifier to database and table names
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        try:
            # Try to get the table from the LAS catalog client
            table = self.las_catalog_client.get_table(
                tbl_name, db_name, self.catalog_name
            )
            # If the table is not None, return True
            if table is not None:
                return True
            # If the table is None, return False
            else:
                return False
        except Exception as e:
            # Log a debug message if the table is not found
            logger.debug("Table not found ", exc_info=e)
            # Return False if an exception occurs
            return False

    def convert_table_to_dataset_uri(self, identifier: TableIdentifier) -> str:
        """
        Convert a table identifier to a dataset URI.

        This method takes a table identifier
        and returns the location of the table as a dataset URI.

        Args:
            identifier (TableIdentifier): The identifier for the table,
            which can be a string or a tuple of strings.

        Returns:
            str: The location of the table as a dataset URI.

        Raises:
            RuntimeError: If the table is not found.
        """
        try:
            # Load the table using the provided identifier
            table = self.get_table(identifier)
            # Return the location of the table as the dataset URI
            return table.location
        except Exception as e:
            # Log an error message if the table is not found
            logger.error("Table not found", exc_info=e)
            # Raise a RuntimeError with the original exception
            raise RuntimeError(e)

    def register_lance_table(self, identifier: TableIdentifier, field_columns=None):
        """
        Register a LAS catalog table under a specific database.

        This method takes an identifier and optional field columns
        to register a table in the LAS catalog.
        The table will be located under the specified database.

        Args:
            identifier (TableIdentifier): The identifier for the table,
             which can be a string or a tuple of strings.
            field_columns (List[FieldColumn], optional):
             A list of FieldColumn objects defining the table schema. Defaults to None.

        Returns:
            Table: The newly registered table.

        Raises:
            NoSuchTableError: If the identifier is invalid or does not exist.
            TableAlreadyExistsError: If the table already exists.
        """
        # Convert the identifier to database and table names
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)

        # Get the database object from the LAS catalog client
        db = self.las_catalog_client.get_database(db_name, self.catalog_name)

        # Construct the table location
        tbl_location = db.location + "/" + tbl_name + ".lance"

        # Register the table with the constructed location and field columns
        return self.register_lance_table_location(
            identifier, tbl_location, field_columns
        )

    @future_feature("altering lance table is not supported yet in LAS Catalog")
    def add_table_columns(self, identifier: TableIdentifier, fields: List[pa.Field]):
        columns = [
            FieldColumn(
                column_name=field.name,
                column_type=Utils.arrow_to_hive_type(field.type),
                column_desc="Added from Lance by add_columns",
            )
            for field in fields
        ]

        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        table = self.las_catalog_client.get_table(tbl_name, db_name, self.catalog_name)
        table.field_columns.extend(columns)
        # call alter table to add columns
        result = self.las_catalog_client.alter_table(table)
        if not result:
            logger.warning(
                "Skipping calling altering lance table as "
                "this is currently not supported in LAS Catalog"
            )

    @future_feature("altering lance table is not supported yet in LAS Catalog")
    def drop_table_columns(self, identifier: TableIdentifier, columns: List[str]):
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        table = self.las_catalog_client.get_table(tbl_name, db_name, self.catalog_name)
        table.field_columns = [
            col for col in table.field_columns if col.column_name not in columns
        ]
        # call alter table to drop columns
        result = self.las_catalog_client.alter_table(table)
        if not result:
            logger.warning(
                "Skipping calling altering lance table "
                "as this is currently not supported in LAS Catalog"
            )

    @future_feature("altering lance table is not supported yet in LAS Catalog")
    def alter_table_columns(
        self, identifier: TableIdentifier, alter_columns: Iterable[Dict]
    ):
        """Alter column definitions in LAS catalog

        Parameters
        ----------
        identifier : TableIdentifier
            The table identifier to alter
        alter_columns : Iterable[Dict]
            A sequence of alteration instructions where each dict contains:
            - "path" (str): Column path to modify
            - "name" (str, optional): New column name
            - "data_type" (DataType, optional): New column data type
        """
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        try:
            table = self.las_catalog_client.get_table(
                tbl_name, db_name, self.catalog_name
            )

            column_map = {col.column_name: col for col in table.field_columns}

            update_gen = (
                self._process_column_alter(alter, column_map, db_name, tbl_name)
                for alter in alter_columns
            )
            updated_columns = [uc for uc in update_gen if uc is not None]

            new_field_columns = []
            for orig_col in table.field_columns:
                modified = next(
                    (uc[1] for uc in updated_columns if uc[0] == orig_col.column_name),
                    None,
                )
                new_field_columns.append(modified or orig_col)

            table.field_columns = new_field_columns
            self.las_catalog_client.alter_table(table)

            logging.info(
                "Altered %d columns in LAS table %s.%s",
                len(updated_columns),
                db_name,
                tbl_name,
            )

        except Exception as e:
            logging.exception(
                "Skipping as not supported in LAS Catalog for %s.%s: %s",
                db_name,
                tbl_name,
                str(e),
            )

    def _process_column_alter(
        self, alter: Dict[str, Any], column_map: dict, db_name: str, tbl_name: str
    ) -> tuple:
        """Process a single column alteration request (new helper method)"""
        col_path = alter.get("path")
        if not col_path:
            logging.warning("Missing 'path' in alteration: %s", alter)
            return None

        target_col = column_map.get(col_path)
        if not target_col:
            logging.warning("Column %s not found in %s.%s", col_path, db_name, tbl_name)
            return None

        new_col = copy.copy(target_col)
        if "name" in alter:
            new_col.column_name = alter["name"]
        if "data_type" in alter:
            new_col.column_type = Utils.arrow_to_hive_type(alter["data_type"])

        return (col_path, new_col)

    def register_lance_table_location(
        self, identifier: TableIdentifier, tbl_location, field_columns=None
    ):
        """
        Register a new table in the LAS catalog.

        This method takes an identifier, a table location,
        and optional field columns to create a new table in the LAS catalog.
        If field columns are not provided,
        a default schema with a single column "_rowid" is used.

        Args:
            identifier (TableIdentifier): The identifier for the table,
            which can be a string or a tuple of strings.
            tbl_location (str): The location where the table data will be stored.
            field_columns (List[FieldColumn], optional):
            A list of FieldColumn objects defining the table schema. Defaults to None.

        Raises:
            NoSuchTableError: If the identifier is invalid or does not exist.
            Exception: If there is an error creating the table in the Hive Metastore.

        Returns:
            None
        """
        db_name, tbl_name = Utils.identifier_to_database_and_table(identifier)
        if field_columns is None:
            field_columns = [
                FieldColumn(
                    "_rowid",
                    "bigint",
                    "default lance schema when no schema is provided",
                )
            ]
        partition_columns = []
        tbl_property = {TABLE_TYPE_PROP: LANCE_DATASET_TYPE_VALUE}
        try:
            tbl = (
                TableBuilder()
                .with_catalog_name(self.catalog_name)  # Required
                .with_database_name(db_name)  # Required
                .with_table_name(tbl_name)  # Required
                .with_partition_type(PartitionType.NON_PARTITION)
                .with_field_columns(field_columns)  # Required
                .with_partition_columns(partition_columns)
                .with_file_format(FileFormat.LANCE)  # Required
                .with_table_properties(tbl_property)
                .with_table_comment("Lance Catalog Table")
                .with_location(tbl_location)
                .build()
            )

            self.las_catalog_client.create_table(tbl)
        except Exception as e:
            logging.error(
                "Failed to create table %s in Hive Metastore: %s", tbl_name, e
            )
            raise
