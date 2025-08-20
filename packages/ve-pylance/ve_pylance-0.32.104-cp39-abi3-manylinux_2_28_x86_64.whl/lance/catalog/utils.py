# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Lance Authors

import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Type, Union, List

import pyarrow as pa

Identifier = Tuple[str, ...]
TableIdentifier = Union[str, Identifier]


@dataclass
class FieldColumn:
    column_name: str
    column_type: str
    column_desc: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "ColumnName": self.column_name,
            "ColumnType": self.column_type,
            "ColumnDesc": self.column_desc,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FieldColumn":
        return cls(
            column_name=data["ColumnName"],
            column_type=data["ColumnType"],
            column_desc=data.get("ColumnDesc"),
        )


class Utils:
    @staticmethod
    def identifier_to_database(
        identifier: TableIdentifier,
        err: Union[Type[ValueError], Type[Exception]] = ValueError,
    ) -> str:
        tuple_identifier = Utils.identifier_to_tuple(identifier)
        if len(tuple_identifier) != 1:
            raise err("Invalid database, hierarchical namespaces are not supported")
        return tuple_identifier[0]

    @staticmethod
    def identifier_to_tuple(identifier: TableIdentifier) -> Identifier:
        """Parse an identifier to a tuple.

        If the identifier is a string, it is split into a tuple
         on '.'. If it is a tuple, it is used as-is.

        Args:
            identifier (str | Identifier): an identifier,
            either a string or tuple of strings.

        Returns:
            Identifier: a tuple of strings.
        """
        return (
            identifier
            if isinstance(identifier, tuple)
            else tuple(str.split(identifier, "."))
        )

    @staticmethod
    def identifier_to_database_and_table(
        identifier: TableIdentifier,
    ) -> Tuple[str, str]:
        """
        Convert an identifier to a tuple containing the database name and table name.

        This method takes an identifier and
         raises ValueError if the identifier format is invalid.

        Args:
            identifier (TableIdentifier): The identifier to convert.

        Returns:
            Tuple[str, str]: A tuple containing the database name and table name.

        Raises:
            ValueError: If the identifier format is invalid
        """
        # Convert the identifier to a tuple
        tuple_identifier = Utils.identifier_to_tuple(identifier)
        # Check if the tuple has exactly two elements
        if len(tuple_identifier) != 2:
            # Raise an error if the tuple does not have exactly two elements
            raise ValueError(
                f"Invalid identifier format, expected [database].[table]: {identifier}"
            )
        # Return the database name and table name as a tuple
        return tuple_identifier[0], tuple_identifier[1]

    @staticmethod
    def rename_scheme(location):
        if not location:  # Handle None or empty strings
            return location

        # Replace protocol prefix by priority
        for prefix in ["s3a://", "tos://"]:
            if location.startswith(prefix):
                return "s3://" + location[len(prefix) :]

        return location

    @staticmethod
    def dataframe_to_field_columns(df) -> list:
        """Convert DataFrame to a list of FieldColumn (lazy load pandas)"""
        # Lazy load pandas and validate input type
        import pandas as pd

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas.DataFrame, got {type(df)}")

        return [
            FieldColumn(column_name=column, column_type=str(dtype))
            for column, dtype in df.dtypes.items()
        ]

    @staticmethod
    def get_schema_from_source(data_obj: any) -> List["FieldColumn"]:
        if isinstance(data_obj, pa.Table):
            return Utils.arrow_table_to_field_columns(data_obj)
        elif isinstance(data_obj, pa.RecordBatch):
            return Utils.arrow_table_to_field_columns(pa.Table.from_batches([data_obj]))
        elif isinstance(data_obj, pa.RecordBatchReader):
            return Utils.arrow_table_to_field_columns(data_obj.read_all())
        else:
            logging.info(
                "schema cannot be inferred for this source type,"
                " current only supports pyarrow"
            )
            return None

    @staticmethod
    def arrow_table_to_field_columns(table: pa.Table) -> [FieldColumn]:
        schema = table.schema
        field_columns = []
        for field in schema:
            column_name = field.name
            # Use arrow_to_hive_type function to get Hive type
            arrow_type_instance = field.type
            hive_type = Utils.arrow_to_hive_type(arrow_type_instance)
            column_type = hive_type

            column_desc = None
            if field.metadata and b"description" in field.metadata:
                column_desc = field.metadata[b"description"].decode("utf-8")

            field_columns.append(
                FieldColumn(
                    column_name=column_name,
                    column_type=column_type,
                    column_desc=column_desc,
                )
            )

        return field_columns

    @staticmethod
    def arrow_to_hive_type(arrow_type):
        # Basic type mapping (removed fixed mapping for decimal)
        type_mapping = {
            pa.int8(): "tinyint",
            pa.int16(): "smallint",
            pa.int32(): "int",
            pa.int64(): "bigint",
            pa.float32(): "float",
            pa.float64(): "double",
            pa.bool_(): "boolean",
            pa.string(): "string",
            pa.binary(): "binary",
            pa.date32(): "date",
            pa.timestamp("ms"): "timestamp",
        }

        # process decimal
        if isinstance(arrow_type, (pa.Decimal128Type, pa.Decimal256Type)):
            precision = arrow_type.precision
            scale = arrow_type.scale
            return f"decimal({precision},{scale})"

        if isinstance(arrow_type, pa.StructType):
            return Utils._map_struct_type(arrow_type)

        if pa.types.is_timestamp(arrow_type):
            return "timestamp"

        if pa.types.is_list(arrow_type):
            element_type = Utils.arrow_to_hive_type(arrow_type.value_type)
            return f"array<{element_type}>"

        # default as string
        return type_mapping.get(arrow_type, "string")

    @staticmethod
    def _map_struct_type(struct_type: pa.StructType) -> str:
        """Process nested struct type"""
        fields = [
            f"{field.name}:{Utils.arrow_to_hive_type(field.type)}"
            for field in struct_type
        ]
        return f"struct<{','.join(fields)}>"
