from pyspark.sql import DataFrame, SparkSession
from delta.tables import DeltaTable
from typing import Dict, Tuple, List, Any, Optional, Union
import logging
from logging_metrics import configure_basic_logging
import os

__all__ = [
    "optimize_and_vacuum_table",
    "optimize_and_zorder_table",
    "optimize_zorder_and_vacuum_table",
    "create_delta_table",
    "write_delta_table",
    "replace_delta_table",
    "merge_delta_table"
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()

def build_replace_where_clause(filters: Union[str, Dict[str, Any]]) -> str:
    """
    Builds WHERE clause for replaceWhere in an intelligent way.
    
    Args:
        filters: Can be:
            - SQL string: "region = 'BR' AND date >= '2024-01-01'"
            - Simple dict: {"region": "BR", "date": "2024-01-01"}
            - Dict with operators: {"date": {">=": "2024-01-01"}, "status": ["active", "pending"]}
    
    Returns:
        str: Formatted WHERE clause
    
    Examples:
        # Direct string
        >>> build_replace_where_clause("region = 'BR' AND date >= '2024-01-01'")
        "region = 'BR' AND date >= '2024-01-01'"
        
        # Simple dict (equality)
        >>> build_replace_where_clause({"region": "BR", "year": 2024})
        "region = 'BR' AND year = 2024"
        
        # Dict with list (IN)
        >>> build_replace_where_clause({"region": ["BR", "US"], "year": 2024})
        "region IN ('BR', 'US') AND year = 2024"
        
        # Dict with operators
        >>> build_replace_where_clause({
        ...     "date": {">=": "2024-01-01"},
        ...     "score": {"between": [80, 100]},
        ...     "status": {"in": ["active", "pending"]}
        ... })
        "date >= '2024-01-01' AND score BETWEEN 80 AND 100 AND status IN ('active', 'pending')"
    """
    if isinstance(filters, str):
        return filters
    
    if not isinstance(filters, dict):
        raise ValueError(f"filters must be str or dict, received: {type(filters)}")
    
    clauses = []
    
    for column, condition in filters.items():
        if isinstance(condition, list):
            # List of values -> IN
            if len(condition) == 1:
                clauses.append(f"{column} = {repr(condition[0])}")
            else:
                formatted_values = [repr(v) for v in condition]
                clauses.append(f"{column} IN ({', '.join(formatted_values)})")
        
        elif isinstance(condition, dict):
            # Dict with operators
            for operator, value in condition.items():
                op_lower = operator.lower()
                
                if op_lower == "between" and isinstance(value, list) and len(value) == 2:
                    clauses.append(f"{column} BETWEEN {repr(value[0])} AND {repr(value[1])}")
                
                elif op_lower == "in" and isinstance(value, list):
                    if len(value) == 1:
                        clauses.append(f"{column} = {repr(value[0])}")
                    else:
                        formatted_values = [repr(v) for v in value]
                        clauses.append(f"{column} IN ({', '.join(formatted_values)})")
                
                elif op_lower in ["is", "is not"]:
                    # For NULL values
                    clauses.append(f"{column} {operator.upper()} {value}")
                
                else:
                    # Normal operators: =, >, <, >=, <=, !=, <>
                    clauses.append(f"{column} {operator} {repr(value)}")
        
        else:
            # Simple value -> equality
            clauses.append(f"{column} = {repr(condition)}")
    
    return " AND ".join(clauses)

def optimize_and_vacuum_table(
    spark: SparkSession,
    table_full_name: str,
    vacuum_retention_hours: int = 168,
    log: Optional[logging.Logger] = None
) -> None:
    """
    Runs OPTIMIZE and VACUUM operations on a Delta table.

    Args:
        spark (SparkSession): Active Spark session.
        table_full_name (str): Full name of the Delta table (e.g., 'silver.my_table').
        vacuum_retention_hours (int, optional): Retention period in hours for the VACUUM command.
            Defaults to 168 (7 days).
        log (Optional[logging.Logger], optional): Logger instance. If None, a default logger will be used.

    Raises:
        Exception: Any error during OPTIMIZE or VACUUM will be logged and re-raised.
    """
    log = log or get_logger()
    try:
        log.info(f"Running OPTIMIZE on table: {table_full_name}")
        spark.sql(f"OPTIMIZE {table_full_name}")

        log.info(f"Running VACUUM on table: {table_full_name} with retention {vacuum_retention_hours} hours")
        spark.sql(f"VACUUM {table_full_name} RETAIN {vacuum_retention_hours} HOURS")

    except Exception as e:
        log.error(f"Failed to optimize and vacuum table {table_full_name}: {e}", exc_info=True)
        raise

def optimize_and_zorder_table(
    spark: SparkSession,
    table_full_name: str,
    zorder_cols: Optional[List[str]] = None,
    log: Optional[logging.Logger] = None
) -> None:
    """
    Runs OPTIMIZE on a Delta table, with optional ZORDER BY columns.

    Args:
        spark (SparkSession): Active Spark session.
        table_full_name (str): Full name of the Delta table (e.g., 'silver.my_table').
        zorder_cols (Optional[List[str]], optional): List of columns to apply ZORDER BY.
            If not provided, standard OPTIMIZE is executed.
        log (Optional[logging.Logger], optional): Logger instance. If None, a default logger will be used.

    Raises:
        Exception: Any error during OPTIMIZE will be logged and re-raised.
    """
    log = log or get_logger()
    try:
        if zorder_cols:
            zorder_expr = ", ".join(zorder_cols)
            log.info(f"Running OPTIMIZE with ZORDER BY ({zorder_expr}) on table: {table_full_name}")
            spark.sql(f"OPTIMIZE {table_full_name} ZORDER BY ({zorder_expr})")
        else:
            log.info(f"Running OPTIMIZE without ZORDER on table: {table_full_name}")
            spark.sql(f"OPTIMIZE {table_full_name}")
    except Exception as e:
        log.error(f"Failed to optimize table {table_full_name}: {e}", exc_info=True)
        raise

def optimize_zorder_and_vacuum_table(
    spark: SparkSession,
    table_full_name: str,
    zorder_cols: Optional[List[str]] = None,
    vacuum_retention_hours: int = 168,
    log: Optional[logging.Logger] = None
) -> None:
    """
    Runs OPTIMIZE with optional ZORDER BY and then VACUUM on a Delta table.

    Args:
        spark (SparkSession): Active Spark session.
        table_full_name (str): Full name of the Delta table (e.g., 'silver.my_table').
        zorder_cols (Optional[List[str]], optional): Columns to use for ZORDER BY.
        vacuum_retention_hours (int, optional): Retention period in hours for the VACUUM command.
            Defaults to 168 (7 days).
        log (Optional[logging.Logger], optional): Logger instance. If None, a default logger will be used.

    Raises:
        Exception: Any error during optimization or vacuuming will be logged and re-raised.
    """
    log = log or get_logger()
    try:
        optimize_and_zorder_table(spark, table_full_name, zorder_cols, log)
        log.info(f"Running VACUUM on table: {table_full_name} with retention {vacuum_retention_hours} hours")
        spark.sql(f"VACUUM {table_full_name} RETAIN {vacuum_retention_hours} HOURS")
    except Exception as e:
        log.error(f"Failed to optimize and vacuum table {table_full_name}: {e}", exc_info=True)
        raise

def create_delta_table(
    spark: SparkSession,
    df: DataFrame,
    table_full_name: str,
    target_full_path: str = "/temporary/",
    partition_cols: Tuple[str, ...] = (),
    log: Optional[logging.Logger] = None
) -> None:
    """
    Creates a new Delta table with or without partitioning.

    Args:
        spark (SparkSession): Active Spark session.
        df (DataFrame): DataFrame to be saved as a Delta table.
        table_full_name (str): Full name of the table in the metastore.
        target_full_path (str, optional): Filesystem path for the Delta table. Defaults to "/temporary/".
        partition_cols (Tuple[str, ...], optional): Columns to use for partitioning. Defaults to empty.
        log (Optional[logging.Logger], optional): Logger instance. If None, a default logger will be used.

    Raises:
        Exception: Any error during creation will be logged and re-raised.
    """
    logger = log or get_logger()
    try:
        os.makedirs(target_full_path, exist_ok=True)

        if DeltaTable.isDeltaTable(spark, target_full_path):
            logger.warning(f"Table already exists: {table_full_name}")
            return

        writer = (
            df.write.format("delta")
            .mode("overwrite")
            .option("mergeSchema", "true")
            .option("path", target_full_path)
        )

        if partition_cols:
            logger.info(f"Creating partitioned table: {table_full_name}")
            writer.partitionBy(*partition_cols)

        logger.info(f"Saving Delta table: {table_full_name}")
        writer.saveAsTable(table_full_name)

        spark.sql(f"""
        ALTER TABLE {table_full_name}
        SET TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact'  = 'true'
        )
        """)
    except Exception as e:
        logger.error(f"Failed to create Delta table {table_full_name}: {e}", exc_info=True)
        raise

def write_delta_table(
    spark: SparkSession,
    df: DataFrame,
    table_full_name: str,
    target_full_path: str = "/temporary/",
    arq_format: str = "delta",
    mode: str = "overwrite",
    partition_cols: Tuple[str, ...] = (),
    replace_where: Optional[Dict[str, Any]] = None,
    merge_cols: Optional[Tuple[str, ...]] = None,
    log: Optional[logging.Logger] = None
) -> None:
    """
    Writes a DataFrame to a Delta table using the specified write mode.

    Args:
        spark (SparkSession): Active Spark session.
        df (DataFrame): DataFrame to be written.
        table_full_name (str): Full name of the Delta table.
        target_full_path (str, optional): Filesystem path for the Delta table.
        arq_format (str, optional): Format for writing. Default is 'delta'.
        mode (str, optional): Write mode: 'overwrite', 'append', 'merge', or 'replace'.
        partition_cols (Tuple[str, ...], optional): Columns to partition by.
        replace_where (Optional[Dict[str, Any]]): Filter for replaceWhere.
        merge_cols (Optional[Tuple[str, ...]]): Columns used for merge condition.
        log (Optional[logging.Logger]): Logger instance.

    Raises:
        ValueError: If required parameters for mode 'merge' or 'replace' are missing.
        Exception: Any Spark error during write is logged and re-raised.
    """
    logger = log or get_logger()

    valid_modes = {"overwrite", "append", "merge", "replace"}
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

    try:
        os.makedirs(target_full_path, exist_ok=True)

        if mode == "overwrite":
            writer = (
                df.write.format(arq_format)
                .mode("overwrite")
                .option("mergeSchema", "true")
                .option("path", target_full_path)
            )
            if partition_cols:
                writer = writer.partitionBy(*partition_cols)
            writer.saveAsTable(table_full_name)

        elif mode == "append":
            writer = (
                df.write.format(arq_format)
                .mode("append")
                .option("mergeSchema", "true")
                .option("path", target_full_path)
            )
            if partition_cols:
                writer = writer.partitionBy(*partition_cols)
            writer.saveAsTable(table_full_name)

        elif mode == "merge":
            if not merge_cols:
                raise ValueError("Parameter 'merge_cols' is required for mode 'merge'")
            logger.info(f"Executing merge on table {table_full_name}")
            merge_delta_table(spark, df, table_full_name, target_full_path, merge_cols, logger)

        elif mode == "replace":
            if not replace_where:
                raise ValueError("Parameter 'replace_filter' is required for mode 'replace'")
            logger.info(f"Executing replace on table {table_full_name}")
            replace_delta_table(spark, df, target_full_path, table_full_name, arq_format, replace_where, logger=logger)

    except Exception as e:
        logger.error(f"Error writing Delta table {table_full_name} in mode '{mode}': {e}", exc_info=True)
        raise

def replace_delta_table(
    spark: SparkSession,
    df: DataFrame,
    target_full_path: str,
    table_full_name: str,
    partition_filters: Union[str, Dict[str, Any]],
    file_format: str = 'delta',
    optimize_after: bool = False,
    log: Optional[logging.Logger] = None
) -> None:
    """
    Replaces partitions in a Delta table using the replaceWhere option.

    Args:
        spark (SparkSession): Active Spark session.
        df (DataFrame): DataFrame with rows to replace.
        target_full_path (str): Filesystem path of the Delta table.
        table_full_name (str): Full name of the Delta table.
        file_format (str): Format to write (e.g., 'delta').
        partition_filters (Union[str, Dict[str, Any]]): Filters for replaceWhere logic.
            Can be:
            - String: "region = 'BR' AND date >= '2024-01-01'"
            - Dict: {"region": "BR", "date": {">=": "2024-01-01"}}
        optimize_after (bool, optional): Whether to run OPTIMIZE after write.
        log (Optional[logging.Logger], optional): Logger instance.

    Examples:
        # Direct SQL string
        replace_delta_table(spark, df, path, table, "delta", 
                          "region = 'BR' AND year = 2024")
        
        # Simple dict
        replace_delta_table(spark, df, path, table, "delta", 
                          {"region": "BR", "year": 2024})
        
        # Dict with operators
        replace_delta_table(spark, df, path, table, "delta", {
            "region": ["BR", "US"],
            "date": {">=": "2024-01-01"},
            "score": {"between": [80, 100]}
        })

    Raises:
        Exception: Any error during write or optimize is logged and re-raised.
    """
    logger = log or logging.getLogger(__name__)
    
    try:
        os.makedirs(target_full_path, exist_ok=True)

        # Build replaceWhere clause
        replace_where = build_replace_where_clause(partition_filters)
        logger.info(f"Generated replaceWhere: {replace_where}")

        if DeltaTable.isDeltaTable(spark, target_full_path):
            (
                df.write.format(file_format)
                .mode("overwrite")
                .option("replaceWhere", replace_where)
                .option("path", target_full_path)
                .saveAsTable(table_full_name)
            )
            if optimize_after:
                logger.info(f"Running OPTIMIZE on {table_full_name}")
                spark.sql(f"OPTIMIZE {table_full_name}")
        else:
            logger.warning(f"Delta table does not exist at {target_full_path}")

    except Exception as e:
        logger.error(f"Failed to replace Delta table {table_full_name}: {e}", exc_info=True)
        raise


def merge_delta_table(
    spark: SparkSession,
    df: DataFrame,
    table_full_name: str,
    target_full_path: str,
    merge_cols: Tuple[str, ...],
    log: Optional[logging.Logger] = None,
    optimize_after: bool = False,
) -> None:
    """
    Performs a Delta MERGE operation: updates existing records or inserts new ones,
    based on business key columns. Runs OPTIMIZE optionally after merge.

    Args:
        spark (SparkSession): Active Spark session.
        df (DataFrame): Source DataFrame to merge.
        table_full_name (str): Full name of the Delta table in the metastore.
        target_full_path (str): Filesystem path of the Delta table.
        merge_cols (Tuple[str, ...]): Columns used for matching records (business key).
        log (Optional[logging.Logger], optional): Logger instance. Defaults to internal logger if not provided.
        optimize_after (bool, optional): Whether to run OPTIMIZE after merge. Defaults to False.

    Raises:
        ValueError: If merge_cols is empty.
        Exception: If the merge operation fails.
    """
    logger = log or get_logger()

    if not merge_cols:
        raise ValueError("Parameter 'merge_cols' must not be empty")

    try:
        record_count = df.count()
        logger.info(f"Preparing to merge {record_count} records into table: {table_full_name}")

        if DeltaTable.isDeltaTable(spark, target_full_path):
            logger.info(f"Merging into existing Delta table: {table_full_name}")
            delta_table = DeltaTable.forPath(spark, target_full_path)

            merge_condition = " AND ".join([f"target.{col} = source.{col}" for col in merge_cols])

            (
                delta_table.alias("target")
                .merge(
                    source=df.alias("source"),
                    condition=merge_condition
                )
                .whenMatchedUpdateAll()
                .whenNotMatchedInsertAll()
                .execute()
            )

            logger.info(f"Merge completed successfully on table: {table_full_name}")

            if optimize_after:
                logger.info(f"Running OPTIMIZE after merge on table: {table_full_name}")
                spark.sql(f"OPTIMIZE {table_full_name}")

        else:
            logger.warning(f"Delta table does not exist at path: {target_full_path}")

    except Exception as e:
        logger.error(f"Failed to merge data into Delta table {table_full_name}: {e}", exc_info=True)
        raise

