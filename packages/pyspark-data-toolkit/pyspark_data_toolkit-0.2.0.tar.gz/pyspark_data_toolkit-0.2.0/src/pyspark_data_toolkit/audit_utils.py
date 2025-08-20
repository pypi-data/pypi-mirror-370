from pyspark.sql import DataFrame, functions as F
from typing import List, Optional, Dict, Any
import uuid
import logging
from logging_metrics import configure_basic_logging
from pyspark.sql.utils import AnalysisException

__all__ = [
    "add_control_columns",
    "add_audit_trail_columns",
    "validate_control_columns",
    "check_row_duplicates",
    "add_metadata_columns"
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()


def add_control_columns(
    df: DataFrame,
    source_system: Optional[str] = None,
    batch_id: Optional[str] = None,
    add_hash: bool = False,
    col_hash: Optional[List[str]] = None,
    lst_hash_columns: Optional[List[str]] = None,
    version: str = "v1",
    timezone: str = "America/Sao_Paulo",
    execution_id: Optional[str] = None,
    environment: Optional[str] = None,
    execution_metadata: Optional[Dict[str, Any]] = None,
    default_file_path: Optional[str] = None,
    log: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Add audit and control columns to the DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        source_system (Optional[str]): Source system name. Default is None.
        batch_id (Optional[str]): Batch ID. If None, a UUID is generated.
        add_hash (bool): Whether to add a row hash column. Default is False.
        col_hash (Optional[List[str]]): List of columns to include in the hash. Takes precedence over lst_hash_columns.
        lst_hash_columns (Optional[List[str]]): List of columns to include in the hash. If None and col_hash is None, all columns are used.
        version (str): Version of the layout; 'v1' uses 'sys_file_path', 'v2' uses 'sys_source_file_path'.
        timezone (str): Timezone to use for timestamps.
        execution_id (Optional[str]): Execution identifier. Default is None.
        environment (Optional[str]): Environment name (e.g., 'dev', 'prod'). Default is None.
        execution_metadata (Optional[Dict[str, Any]]): Additional metadata to be logged as columns.
        log (Optional[logging.Logger]): Logger instance for logging messages.

    Returns:
        DataFrame: Spark DataFrame with audit and control columns.
    """
    logger = log or get_logger()

    if batch_id is None:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        
        try:
            timestamp = datetime.now(ZoneInfo(timezone)).strftime('%Y%m%d_%H%M%S')
            context = source_system.lower().replace(' ', '_') if source_system else "unknown"
            batch_id = f"{context}_batch_{timestamp}"
            logger.info(f"Generated semantic batch_id: {batch_id}")
        except Exception as e:
            # Fallback to UUID if timestamp generation fails
            batch_id = str(uuid.uuid4())
            logger.warning(f"Failed to generate semantic batch_id, using UUID: {e}")
    else:
        logger.info(f"Using provided batch_id: {batch_id}")

    # Add current timestamp and date in the specified timezone
    result_df = (
        df.withColumn("sys_load_date", F.to_date(F.from_utc_timestamp(F.current_timestamp(), timezone)))
          .withColumn("sys_load_timestamp", F.from_utc_timestamp(F.current_timestamp(), timezone))
    )

    # Add file path column depending on version
    column_name_file = "sys_file_path" if version == "v1" else "sys_source_file_path"
    try:
        if default_file_path:
            result_df = result_df.withColumn(column_name_file, F.lit(default_file_path))
        else:
            if "_metadata" in df.columns or any(c.startswith("_metadata") for c in df.schema.names):
                result_df = result_df.withColumn(column_name_file, F.col("_metadata.file_path"))
                logger.info(f"Using _metadata.file_path for '{column_name_file}'")
            else:
                result_df = result_df.withColumn(column_name_file, F.input_file_name())
                logger.info(f"Using input_file_name() for '{column_name_file}'")
    except Exception as e:
        logger.warning(f"Fallback: could not determine file path ({e}), using logical path")
        result_df = result_df.withColumn(column_name_file, F.lit("logical_path_or_unknown"))

    # Add source system if provided
    if source_system:
        result_df = result_df.withColumn("sys_source_system", F.lit(source_system))

    # Add batch ID
    result_df = result_df.withColumn("sys_batch_id", F.lit(str(batch_id)))

    # Add execution ID if provided
    if execution_id:
        # execution_id = f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        result_df = result_df.withColumn("sys_execution_id", F.lit(execution_id))


    # Add environment if provided
    if environment:
        result_df = result_df.withColumn("sys_environment", F.lit(environment))

    # Add row hash column if required
    if add_hash:
        try:
            # Priority: col_hash > lst_hash_columns > all columns
            if col_hash is not None:
                cols_to_hash = col_hash
                logger.info(f"Using col_hash columns for hashing: {cols_to_hash}")
            elif lst_hash_columns is not None:
                cols_to_hash = lst_hash_columns
                logger.info(f"Using lst_hash_columns for hashing: {cols_to_hash}")
            else:
                cols_to_hash = result_df.columns
                logger.info(f"Using all columns for hashing: {len(cols_to_hash)} columns")
            
            # Validate that specified columns exist in the DataFrame
            existing_columns = set(result_df.columns)
            missing_columns = [col for col in cols_to_hash if col not in existing_columns]
            
            if missing_columns:
                logger.warning(f"The following columns specified for hashing do not exist in the DataFrame: {missing_columns}")
                cols_to_hash = [col for col in cols_to_hash if col in existing_columns]
                
            if not cols_to_hash:
                logger.error("No valid columns found for hashing")
                raise ValueError("No valid columns available for hashing")
            
            result_df = result_df.withColumn(
                "sys_hash_row",
                F.sha2(
                    F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("")) for c in cols_to_hash]),
                    256
                )
            )
            logger.info(f"Successfully added sys_hash_row column using {len(cols_to_hash)} columns")
            
        except Exception as e:
            logger.error(f"Failed to create sys_hash_row column: {e}")
            raise

    # Attempt to retrieve the user running the notebook
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython and "dbutils" in ipython.user_ns:
            dbutils = ipython.user_ns["dbutils"]
        elif "dbutils" in globals():
            dbutils = globals()["dbutils"]
        else:
            dbutils = None
        user = (
            dbutils.notebook.entry_point.getDbutils()
                   .notebook()
                   .getContext()
                   .userName()
                   .get()
            if dbutils else "unknown"
        )
    except Exception as e:
        logger.warning(f"Failed to retrieve user: {e}")
        user = "unknown"

    result_df = result_df.withColumn("sys_user", F.lit(user))

    # Add optional execution metadata columns
    if execution_metadata:
        for key, value in execution_metadata.items():
            result_df = result_df.withColumn(f"sys_exec_{key}", F.lit(value))

    return result_df


def add_audit_trail_columns(
    df: DataFrame,
    updated_by: Optional[str] = None,
    add_timestamp: bool = True,
    timezone: str = "America/Sao_Paulo",
) -> DataFrame:
    """
    Add update audit columns such as timestamp and user.

    Args:
        df (DataFrame): Input Spark DataFrame.
        updated_by (Optional[str]): Username or system performing the update.
        add_timestamp (bool): Whether to add a timestamp column. Default is True.
        timezone (str): Timezone to use for the timestamp.

    Returns:
        DataFrame: Spark DataFrame with audit trail columns.
    """
    result_df = df
    if add_timestamp:
        result_df = result_df.withColumn(
            "sys_updated_at",
            F.from_utc_timestamp(F.current_timestamp(), timezone)
        )
    if updated_by:
        result_df = result_df.withColumn("sys_updated_by", F.lit(updated_by))
    return result_df


def validate_control_columns(
    df: DataFrame,
    required_columns: Optional[List[str]] = None
) -> bool:
    """
    Validate whether required audit/control columns exist in the DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        required_columns (Optional[List[str]]): List of required column names. Default includes main audit columns.

    Raises:
        ValueError: If any required column is missing.

    Returns:
        bool: True if all required columns exist.
    """
    required = required_columns or [
        "sys_load_date", "sys_load_timestamp", "sys_user", "sys_batch_id"
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing audit/control columns: {missing}")
    return True


def check_row_duplicates(
    df: DataFrame,
    hash_column: str = "sys_hash_row"
) -> DataFrame:
    """
    Identify duplicate rows based on a hash column.

    Args:
        df (DataFrame): Input Spark DataFrame.
        hash_column (str): Name of the column used for duplicate detection.

    Returns:
        DataFrame: DataFrame containing duplicated hash values and their counts.
    """
    return (
        df.groupBy(hash_column)
          .count()
          .filter(F.col("count") > 1)
    )


def add_metadata_columns(
    df: DataFrame,
    metadata: Dict[str, Any]
) -> DataFrame:
    """
    Add custom metadata columns to the DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        metadata (Dict[str, Any]): Dictionary of key-value pairs to add as columns.

    Returns:
        DataFrame: DataFrame with metadata columns added.
    """
    result_df = df
    for key, value in metadata.items():
        result_df = result_df.withColumn(f"meta_{key}", F.lit(value))
    return result_df
