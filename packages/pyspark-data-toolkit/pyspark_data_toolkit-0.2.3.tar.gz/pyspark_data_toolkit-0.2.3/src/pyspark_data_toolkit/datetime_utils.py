from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import TimestampType, DateType, StringType
import logging
from typing import List, Optional
from logging_metrics import configure_basic_logging

__all__ = [
    "convert_timezone",
    "format_timestamp",
    "safe_to_date",
    "safe_to_timestamp",
    "validate_date_native",
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()

def convert_timezone(
    df: DataFrame,
    column_name: str,
    from_tz: str = "UTC",
    to_tz: str = "America/Sao_Paulo",
    new_column_name: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Converts a timestamp column from one timezone to another.

    Args:
        df (DataFrame): Input Spark DataFrame.
        column_name (str): Column name with timestamp or string values.
        from_tz (str): Source timezone (e.g., 'UTC').
        to_tz (str): Target timezone (e.g., 'America/Sao_Paulo').
        new_column_name (Optional[str]): Output column name. If None, overwrites input column.
        logger (Optional[logging.Logger]): Logger for audit. Defaults to internal logger.

    Returns:
        DataFrame: DataFrame with timezone-adjusted column.
    """
    log = logger or get_logger()
    out_col = new_column_name or column_name

    if column_name not in df.columns:
        log.error(f"Column '{column_name}' not found.")
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    try:
        col = F.col(column_name).cast("timestamp")
        if from_tz.upper() != "UTC":
            col = F.to_utc_timestamp(col, from_tz)
        result = df.withColumn(out_col, F.from_utc_timestamp(col, to_tz))
        log.info(f"convert_timezone: {column_name} → {out_col} ({from_tz} → {to_tz})")
        return result
    except Exception as e:
        log.exception(f"Failed to convert timezone for column '{column_name}': {e}")
        raise

def format_timestamp(
    df: DataFrame,
    timestamp_col: str,
    format_pattern: str = "HH:mm",
    new_column_name: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Formats a timestamp column as a string using a specified pattern.

    Args:
        df (DataFrame): Input Spark DataFrame.
        timestamp_col (str): Timestamp column name.
        format_pattern (str): Desired output format (e.g., 'yyyy-MM-dd HH:mm').
        new_column_name (Optional[str]): Output column name. Defaults to overwriting input column.
        logger (Optional[logging.Logger]): Logger for audit.

    Returns:
        DataFrame: DataFrame with formatted timestamp string column.
    """
    log = logger or get_logger()
    out_col = new_column_name or timestamp_col

    if timestamp_col not in df.columns:
        log.error(f"Column '{timestamp_col}' not found.")
        raise ValueError(f"Column '{timestamp_col}' not found in DataFrame.")

    try:
        col = F.col(timestamp_col).cast("timestamp")
        result = df.withColumn(out_col, F.date_format(col, format_pattern))
        log.info(f"format_timestamp: {timestamp_col} → {out_col} (pattern={format_pattern})")
        return result
    except Exception as e:
        log.exception(f"Failed to format timestamp '{timestamp_col}': {e}")
        raise

def safe_to_date(
    df: DataFrame,
    col_name: str,
    formats: List[str],
    new_column_name: Optional[str] = None,
    default: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Safely parses string values into DateType using multiple format patterns.

    Args:
        df (DataFrame): Input DataFrame.
        col_name (str): Column containing date strings.
        formats (List[str]): List of date formats to try.
        new_column_name (Optional[str]): Output column name.
        default (Optional[str]): Default value for invalid dates.
        logger (Optional[logging.Logger]): Logger for audit.

    Returns:
        DataFrame: DataFrame with parsed date column.
    """
    log = logger or get_logger()
    out_col = new_column_name or col_name

    if col_name not in df.columns:
        log.error(f"Column '{col_name}' not found.")
        raise ValueError(f"Column '{col_name}' not found in DataFrame.")

    try:
        expr = None
        for fmt in formats:
            parsed = F.to_date(F.col(col_name), fmt)
            expr = parsed if expr is None else F.coalesce(expr, parsed)

        if default is not None:
            expr = F.coalesce(expr, F.lit(default).cast(DateType()))

        result = df.withColumn(out_col, expr)
        log.info(f"safe_to_date: {col_name} → {out_col} using formats={formats}")
        return result
    except Exception as e:
        log.exception(f"Failed to parse date column '{col_name}': {e}")
        raise

def safe_to_timestamp(
    df: DataFrame,
    col_name: str,
    formats: List[str],
    new_column_name: Optional[str] = None,
    default: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Safely parses string values into TimestampType using multiple format patterns.

    Args:
        df (DataFrame): Input DataFrame.
        col_name (str): Column containing timestamp strings.
        formats (List[str]): List of timestamp formats to try.
        new_column_name (Optional[str]): Output column name.
        default (Optional[str]): Default value for invalid timestamps.
        logger (Optional[logging.Logger]): Logger for audit.

    Returns:
        DataFrame: DataFrame with parsed timestamp column.
    """
    log = logger or get_logger()
    out_col = new_column_name or col_name

    if col_name not in df.columns:
        log.error(f"Column '{col_name}' not found.")
        raise ValueError(f"Column '{col_name}' not found in DataFrame.")

    try:
        expr = None
        for fmt in formats:
            parsed = F.to_timestamp(F.col(col_name), fmt)
            expr = parsed if expr is None else F.coalesce(expr, parsed)

        if default is not None:
            expr = F.coalesce(expr, F.lit(default).cast(TimestampType()))

        result = df.withColumn(out_col, expr)
        log.info(f"safe_to_timestamp: {col_name} → {out_col} using formats={formats}")
        return result
    except Exception as e:
        log.exception(f"Failed to parse timestamp column '{col_name}': {e}")
        raise

def validate_date_native(
    df: DataFrame,
    col_name: str,
    format_pattern: str = "yyyy-MM-dd",
    default: str = "1900-01-01",
    new_column_name: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Validates a string date column by pattern and replaces invalid values with a default.

    Args:
        df (DataFrame): Input DataFrame.
        col_name (str): Column name to validate.
        format_pattern (str): Format pattern to apply (e.g., 'yyyy-MM-dd').
        default (str): Default value to use when validation fails.
        new_column_name (Optional[str]): Output column name.
        logger (Optional[logging.Logger]): Logger for audit.

    Returns:
        DataFrame: DataFrame with validated and formatted date column.
    """
    log = logger or get_logger()
    out_col = new_column_name or col_name

    if col_name not in df.columns:
        log.error(f"Column '{col_name}' not found.")
        raise ValueError(f"Column '{col_name}' not found in DataFrame.")

    try:
        parsed = F.to_date(F.col(col_name), format_pattern)
        result = df.withColumn(
            out_col,
            F.when(parsed.isNotNull(), F.date_format(parsed, format_pattern))
             .otherwise(F.lit(default))
        )
        log.info(f"validate_date_native: {col_name} → {out_col} with format={format_pattern}")
        return result
    except Exception as e:
        log.exception(f"Failed to validate date column '{col_name}': {e}")
        raise
