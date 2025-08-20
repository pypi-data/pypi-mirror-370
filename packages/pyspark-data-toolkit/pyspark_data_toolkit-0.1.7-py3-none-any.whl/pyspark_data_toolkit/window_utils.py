from typing import List, Optional
import logging
from pyspark.sql import DataFrame, Window, functions as F
from logging_metrics import configure_basic_logging

__all__ = [
    "get_latest_records",
    "drop_duplicates_keep_latest",
]


def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()


def get_latest_records(
    df: DataFrame,
    primary_key_columns: List[str],
    order_by_columns: List[str],
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """Returns the latest record for each primary key group based on ordering columns.

    Uses a window partitioned by the primary key columns and ordered in descending order
    by the specified `order_by_columns`, keeping only the first record per group.

    Args:
        df (DataFrame): Input Spark DataFrame.
        primary_key_columns (List[str]): Columns defining the primary key group.
        order_by_columns (List[str]): Columns used to determine the latest record (in descending order).
        logger (Optional[logging.Logger]): Optional logger for auditing. Uses `get_logger()` if None.

    Returns:
        DataFrame: DataFrame containing only the most recent records per primary key.
    """
    log = logger or get_logger()

    # Define window spec: partitioned by PK, ordered by descending criteria
    window_spec = Window.partitionBy(*primary_key_columns) \
                        .orderBy(*[F.col(col).desc() for col in order_by_columns])

    # Assign row numbers, keep only the first row per partition
    result = (
        df.withColumn("row_num", F.row_number().over(window_spec))
          .filter(F.col("row_num") == 1)
          .drop("row_num")
    )

    log.info(f"get_latest_records: kept latest records grouped by {primary_key_columns}")
    return result


def drop_duplicates_keep_latest(
    df: DataFrame,
    keys: List[str],
    order_col: str
) -> DataFrame:
    """Removes duplicate records by keeping the latest one per key group.

    A convenience wrapper around `get_latest_records` for a single ordering column.

    Args:
        df (DataFrame): Input Spark DataFrame.
        keys (List[str]): Columns that define the group key.
        order_col (str): Column used to determine the latest record (in descending order).

    Returns:
        DataFrame: Deduplicated DataFrame with only the latest records kept.
    """
    return get_latest_records(df, keys, [order_col])
