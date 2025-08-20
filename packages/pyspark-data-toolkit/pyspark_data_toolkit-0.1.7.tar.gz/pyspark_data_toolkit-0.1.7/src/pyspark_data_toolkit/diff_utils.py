from typing import List, Dict, Any, Optional
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
import logging
from logging_metrics import configure_basic_logging

__all__ = [
    "diff_dataframes",
    "diff_schemas",
    "summarize_diff",
    "tag_row_changes"
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()

def diff_dataframes(df1: DataFrame, df2: DataFrame, keys: List[str]) -> DataFrame:
    """
    Identifies differences between two DataFrames based on primary keys.

    Args:
        df1 (DataFrame): Original DataFrame.
        df2 (DataFrame): New DataFrame to compare.
        keys (List[str]): Primary key columns used for comparison.

    Returns:
        DataFrame: Combined DataFrame of inserted and deleted rows, tagged with '_change'.
    """
    removed = (
        df1.join(df2, keys, how="left_anti")
           .withColumn("_change", F.lit("deleted"))
    )
    inserted = (
        df2.join(df1, keys, how="left_anti")
           .withColumn("_change", F.lit("inserted"))
    )
    return removed.unionByName(inserted)


def diff_schemas(df1: DataFrame, df2: DataFrame) -> Dict[str, Any]:
    """
    Compares the schemas of two DataFrames.

    Args:
        df1 (DataFrame): First DataFrame.
        df2 (DataFrame): Second DataFrame.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - only_in_df1: columns only present in df1
            - only_in_df2: columns only present in df2
            - type_mismatches: columns present in both with different data types
    """
    s1 = {f.name: f.dataType for f in df1.schema.fields}
    s2 = {f.name: f.dataType for f in df2.schema.fields}

    only1 = set(s1) - set(s2)
    only2 = set(s2) - set(s1)
    mismatches = {
        col: (s1[col], s2[col])
        for col in set(s1).intersection(s2)
        if s1[col] != s2[col]
    }

    return {
        "only_in_df1": list(only1),
        "only_in_df2": list(only2),
        "type_mismatches": mismatches
    }


def summarize_diff(df1: DataFrame, df2: DataFrame, keys: List[str], log: Optional[logging.Logger] = None) -> Dict[str, int]:
    """
    Summarizes differences between two DataFrames (inserted, deleted, updated rows).

    Args:
        df1 (DataFrame): Original DataFrame.
        df2 (DataFrame): New DataFrame.
        keys (List[str]): Primary key columns used for matching.

    Returns:
        Dict[str, int]: Dictionary containing counts of inserted, deleted, and updated rows.
    """
    logger = log or get_logger()

    try:
        removed_df = df1.join(df2, keys, how="left_anti")
        inserted_df = df2.join(df1, keys, how="left_anti")

        non_keys = [c for c in df1.columns if c not in keys]
        df1_ren = df1
        df2_ren = df2
        for col in non_keys:
            df1_ren = df1_ren.withColumnRenamed(col, f"{col}_1")
            df2_ren = df2_ren.withColumnRenamed(col, f"{col}_2")

        common = df1_ren.join(df2_ren, keys, how="inner")

        cond = None
        for col in non_keys:
            diff = F.col(f"{col}_1") != F.col(f"{col}_2")
            cond = diff if cond is None else cond | diff

        updated_df = common.filter(cond) if cond is not None else common.limit(0)

        return {
            "inserted": inserted_df.count(),
            "deleted": removed_df.count(),
            "updated": updated_df.count()
        }
    except Exception as e:
        logger.exception(f"Error in summarize_diff: {e}")
        raise


def tag_row_changes(
    df1: DataFrame,
    df2: DataFrame,
    keys: List[str],
    hash_cols: Optional[List[str]] = None,
    tag_col: str = "change_type",
    log: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Compares rows from two DataFrames and tags changes as 'inserted', 'deleted', 'updated', or 'unchanged'.

    Args:
        df1 (DataFrame): Original DataFrame.
        df2 (DataFrame): New DataFrame.
        keys (List[str]): Key columns to match rows.
        hash_cols (Optional[List[str]]): Columns to compute hash comparison. If None, uses all columns from df2.
        tag_col (str): Name of the change type column. Default is 'change_type'.

    Returns:
        DataFrame: DataFrame from df2 with a column indicating the change type.
    """
    logger = log or get_logger()

    try:
        cols = hash_cols if hash_cols is not None else df2.columns

        # Generate temporary column names
        df1_tmp_cols = [f"tmp1_{i}" for i in range(len(df1.columns))]
        df2_tmp_cols = [f"tmp2_{i}" for i in range(len(df2.columns))]
        df1_temp = df1.toDF(*df1_tmp_cols)
        df2_temp = df2.toDF(*df2_tmp_cols)

        # Create column mappings
        df1_colmap = dict(zip(df1.columns, df1_tmp_cols))
        df2_colmap = dict(zip(df2.columns, df2_tmp_cols))

        # Add hash columns
        df1_temp = df1_temp.withColumn(
            "__hash_1", F.sha2(F.concat_ws("||", *[F.col(df1_colmap[c]) for c in cols]), 256)
        )
        df2_temp = df2_temp.withColumn(
            "__hash_2", F.sha2(F.concat_ws("||", *[F.col(df2_colmap[c]) for c in cols]), 256)
        )

        # Join on key columns
        join_cond = [df1_temp[df1_colmap[k]] == df2_temp[df2_colmap[k]] for k in keys]
        joined = df1_temp.join(df2_temp, join_cond, how="full_outer")

        # Define change types
        is_insert = F.col(df2_colmap[keys[0]]).isNotNull() & F.col(df1_colmap[keys[0]]).isNull()
        is_delete = F.col(df1_colmap[keys[0]]).isNotNull() & F.col(df2_colmap[keys[0]]).isNull()
        is_update = (
            (F.col("__hash_1") != F.col("__hash_2")) &
            F.col("__hash_1").isNotNull() & F.col("__hash_2").isNotNull()
        )
        is_unchanged = (
            (F.col("__hash_1") == F.col("__hash_2")) &
            F.col("__hash_1").isNotNull()
        )

        # Assign change type
        result = joined.withColumn(
            tag_col,
            F.when(is_insert, F.lit("inserted"))
             .when(is_delete, F.lit("deleted"))
             .when(is_update, F.lit("updated"))
             .when(is_unchanged, F.lit("unchanged"))
        )

        # Select final columns with original names + change type
        select_cols = [F.col(df2_colmap[c]).alias(c) for c in df2.columns] + [F.col(tag_col)]
        return result.select(*select_cols)
    except Exception as e:
        logger.exception(f"Error in tag_row_changes: {e}")
        raise
