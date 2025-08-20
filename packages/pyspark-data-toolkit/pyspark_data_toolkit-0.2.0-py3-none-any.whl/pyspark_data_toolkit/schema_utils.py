from typing import List, Dict, Optional, Any
import re
import logging
from pyspark.sql import DataFrame, functions as F
from logging_metrics import configure_basic_logging

__all__ = [
    "apply_schema",
    "cast_columns_types_by_schema",
    "validate_dataframe_schema",
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()


def apply_schema(df: DataFrame, schema: Dict[str, Any], log: Optional[logging.Logger] = None) -> DataFrame:
    """Applies a schema by selecting and casting columns.

    This function:
      1. Selects only columns defined in `schema["columns"]`.
      2. Casts column types as defined in schema.

    Args:
        df (DataFrame): Input Spark DataFrame.
        schema (Dict[str, Any]): Dictionary with "columns" key containing a list of:
            - "column_name": Name of the column.
            - "data_type": Target type (string, int, date, etc.).

    Returns:
        DataFrame: DataFrame with selected and casted columns.
    """
    logger = log or get_logger()
    logger.info("Applying schema to DataFrame.")

    columns = [col["column_name"] for col in schema["columns"]]
    df = df.select(*columns)

    return cast_columns_types_by_schema(
        df,
        schema_list=schema["columns"],
        empty_to_null=True,
        logger=logger
    )


def cast_columns_types_by_schema(
    df: DataFrame,
    schema_list: List[Dict[str, str]],
    empty_to_null: bool = False,
    truncate_strings: bool = False,
    max_string_length: int = 16382,
    logger: Optional[logging.Logger] = None,
    default_value: Any = None,
    strict_mode: bool = False,
) -> DataFrame:
    """Casts DataFrame columns to the types specified in the schema list.

    Args:
        df (DataFrame): Input Spark DataFrame.
        schema_list (List[Dict[str, str]]): List of dicts with:
            - "column_name": Column name.
            - "data_type": Target Spark type.
        empty_to_null (bool): Replace empty strings with null (if applicable).
        truncate_strings (bool): Truncate strings longer than `max_string_length`.
        max_string_length (int): Max length for string columns.
        logger (Optional[logging.Logger]): Logger instance (default: new logger).
        default_value (Any): Value to fill for missing columns if not strict.
        strict_mode (bool): If True, raises exception on missing columns.

    Returns:
        DataFrame: DataFrame with type-casted columns.
    """
    log = logger or get_logger()
    log.info("Casting columns based on schema.")

    for col_def in schema_list:
        name = col_def["column_name"]
        dtype = col_def["data_type"].lower()

        if name not in df.columns:
            if strict_mode:
                raise ValueError(f"Column '{name}' not found in DataFrame.")
            log.warning(f"Column '{name}' not found. Filling with default value.")
            df = df.withColumn(name, F.lit(default_value))
            continue

        try:
            col_expr = F.col(name)

            if re.fullmatch(r"int(eger)?", dtype):
                col_expr = col_expr.cast("int")
            elif "bool" in dtype:
                col_expr = col_expr.cast("boolean")
            elif any(t in dtype for t in ["numeric", "decimal", "double", "float", "real", "money"]):
                col_expr = col_expr.cast("double")
            elif dtype == "date":
                col_expr = F.to_date(col_expr)
            elif dtype in ["datetime", "timestamp"]:
                col_expr = F.coalesce(
                    F.to_timestamp(col_expr, "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"),
                    F.to_timestamp(col_expr, "yyyy-MM-dd HH:mm:ss.SSS"),
                    F.to_timestamp(col_expr, "yyyy-MM-dd HH:mm:ss"),
                    F.to_timestamp(col_expr)
                )
            else:
                col_expr = col_expr.cast("string")

            if truncate_strings and dtype == "string":
                col_expr = F.substring(col_expr, 1, max_string_length)

            if empty_to_null and dtype in ["string", "date", "timestamp"]:
                col_expr = F.when(F.trim(col_expr) == "", None).otherwise(col_expr)

            df = df.withColumn(name, col_expr)

        except Exception as e:
            log.error(f"Error casting column '{name}' to {dtype}: {e}")

    return df


def validate_dataframe_schema(df: DataFrame, schema: Dict[str, Any]) -> bool:
    """Validates that all columns defined in the schema exist in the DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        schema (Dict[str, Any]): Dictionary with "columns" key and list of:
            - "column_name": Column to validate.

    Returns:
        bool: True if all schema columns exist in DataFrame, False otherwise.
    """
    expected_cols = {col["column_name"] for col in schema.get("columns", [])}
    actual_cols = set(df.columns)
    return expected_cols.issubset(actual_cols)
