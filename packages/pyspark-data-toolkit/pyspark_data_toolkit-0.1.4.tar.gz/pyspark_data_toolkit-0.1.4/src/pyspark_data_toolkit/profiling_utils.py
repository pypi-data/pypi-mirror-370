from typing import List, Dict, Optional, Any, Literal
from pyspark.sql import DataFrame, functions as F
from pyspark.sql import DataFrame
import sys

__all__ = [
    "profile_nulls",
    "profile_dataframe",
    "profile_schema_changes",
    "profile_value_distribution",
    "profile_numeric_stats",
    "detect_outliers",
    "detect_skewed_columns",
    "profile_correlations",
    "profile_sample",
    "profile_memory_usage",
    "profile_cardinality",
    "profile_duplicates",
]

def profile_nulls(df: DataFrame, threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Returns columns with null percentage greater than or equal to the given threshold.

    Args:
        df (DataFrame): Input Spark DataFrame.
        threshold (float): Minimum null fraction (0 to 1) to include column. Default is 0.5.

    Returns:
        List[Dict[str, Any]]: List of dictionaries with:
            - "column": Column name.
            - "null_pct": Percentage of nulls.
    """
    total = df.count()
    results = []
    for c in df.columns:
        null_count = df.filter(F.col(c).isNull()).count()
        pct = null_count / total if total > 0 else 0.0
        if pct >= threshold:
            results.append({"column": c, "null_pct": pct})
    return results

def profile_dataframe(
    df: DataFrame,
    output_format: Literal["list", "spark"] = "list",
    include_min_max: bool = True
) -> Any:
    """
    Generates a profiling summary of the DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        output_format (Literal["list", "spark"]): Output format. Default is "list".
        include_min_max (bool): Whether to include min/max for numeric and date columns.

    Returns:
        list[dict] | pd.DataFrame | DataFrame: Summary of profiling depending on output_format.
    """
    total = df.count()
    dtypes = dict(df.dtypes)
    results: List[Dict[str, Any]] = []

    for c in df.columns:
        distinct_count = df.select(c).distinct().count()
        null_count = df.filter(F.col(c).isNull()).count()

        info = {
            "column": c,
            "data_type": dtypes[c],
            "total_rows": total,
            "distinct_count": float(distinct_count),
            "distinct_pct": float(distinct_count) / total if total > 0 else 0.0,
            "null_count": float(null_count),
            "null_pct": float(null_count) / total if total > 0 else 0.0
        }

        if include_min_max and any(
            t in dtypes[c] for t in ["int", "double", "float", "bigint", "date", "timestamp"]
        ):
            agg = df.agg(F.min(c).alias("min"), F.max(c).alias("max")).first()
            info["min"] = float(agg["min"]) if agg["min"] is not None else None
            info["max"] = float(agg["max"]) if agg["max"] is not None else None

        results.append(info)

    if output_format == "list":
        return results
    elif output_format == "spark":
        for row in results:
            for k, v in row.items():
                if isinstance(v, int):
                    row[k] = float(v)
        return df.sql_ctx.createDataFrame(results)
    else:
        raise ValueError("output_format must be 'list' or 'spark'")


def profile_schema_changes(df1: DataFrame, df2: DataFrame) -> Dict[str, Any]:
    """Compares the schema of two DataFrames and returns differences.

    Args:
        df1 (DataFrame): First DataFrame.
        df2 (DataFrame): Second DataFrame.

    Returns:
        Dict[str, Any]: Dictionary with:
        - "added": columns only in df2
        - "removed": columns only in df1
        - "type_changes": columns present in both with different types
    """
    s1 = dict(df1.dtypes)
    s2 = dict(df2.dtypes)
    added = [c for c in s2 if c not in s1]
    removed = [c for c in s1 if c not in s2]
    type_changes = [c for c in s1 if c in s2 and s1[c] != s2[c]]
    return {"added": added, "removed": removed, "type_changes": type_changes}


def profile_value_distribution(
    df: DataFrame,
    columns: List[str],
    top_n: int = 10
) -> Dict[str, List[Any]]:
    """
    Gets the distribution of values (Top N) for categorical columns.

    Args:
        df (DataFrame): Input DataFrame.
        columns (List[str]): List of categorical columns.
        top_n (int): Number of most frequent values to return. Defaults to 10.

    Returns:
        Dict[str, List[Any]]: Column mapping to a list of rows of (value, count).
    """
    result: Dict[str, List[Any]] = {}
    for c in columns:
        result[c] = (
            df.groupBy(c)
              .count()
              .orderBy(F.desc("count"))
              .limit(top_n)
              .collect()
        )
    return result


def profile_numeric_stats(
    df: DataFrame,
    columns: Optional[List[str]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Computes descriptive statistics for numeric columns.

    Args:
        df (DataFrame): Input DataFrame.
        columns (List[str], optional): Numeric columns to compute. If None, auto-detects.

    Returns:
        Dict[str, Dict[str, Any]]: Column mapping for statistics {min, max, mean, median, stddev}.
    """
    numeric_cols = columns or [c for c, t in df.dtypes if t in ["int", "double", "bigint", "float"]]
    stats: Dict[str, Dict[str, Any]] = {}
    for c in numeric_cols:
        row = df.select(
            F.min(c).alias("min"),
            F.max(c).alias("max"),
            F.mean(c).alias("mean"),
            F.expr(f"percentile_approx({c}, 0.5)").alias("median"),
            F.stddev(c).alias("stddev")
        ).first()
        stats[c] = row.asDict()
    return stats


def detect_outliers(
    df: DataFrame,
    columns: List[str],
    factor: float = 1.5
) -> Dict[str, DataFrame]:
    """Detecta outliers usando IQR (Interquartile Range).

    Args:
        df (DataFrame): DataFrame de entrada.
        columns (List[str]): Colunas numéricas para verificar.
        factor (float): Multiplicador do IQR para limites. Defaults to 1.5.

    Returns:
        Dict[str, DataFrame]: Mapeamento de coluna para DataFrame de outliers.
    """
    outliers: Dict[str, DataFrame] = {}
    for c in columns:
        stats = df.select(F.expr(f"percentile_approx({c}, array(0.25,0.5,0.75))")).first()[0]
        q1, _, q3 = stats
        iqr = q3 - q1
        lower, upper = q1 - factor * iqr, q3 + factor * iqr
        outliers[c] = df.filter((F.col(c) < lower) | (F.col(c) > upper))
    return outliers


def detect_skewed_columns(df: DataFrame, threshold: float = 0.95) -> List[str]:
    """
    Identifies columns where a single value dominates >= threshold of records.

    Args:
        df (DataFrame): Input DataFrame.
        threshold (float): Minimum fraction to consider skew. Defaults to 0.95.

    Returns:
        List[str]: List of skewed columns.
    """
    skewed: List[str] = []
    total = df.count()
    for c in df.columns:
        top = df.groupBy(c).count().orderBy(F.desc("count")).first()
        if top and top["count"] / total >= threshold:
            skewed.append(c)
    return skewed


def profile_correlations(
    df: DataFrame,
    columns: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Calculates the Pearson correlation matrix between numeric columns.

    Args:
        df (DataFrame): Input DataFrame.
        columns (List[str], optional): Numeric columns to correlate. If None, automatically detects.

    Returns:
        Dict[str, Dict[str, float]]: Correlations {col1: {col2: value}}.
    """
    cols = columns or [c for c, t in df.dtypes if t in ["int", "double", "bigint", "float"]]
    corrs: Dict[str, Dict[str, float]] = {}
    for i, c1 in enumerate(cols):
        corrs[c1] = {}
        for c2 in cols[i+1:]:
            corrs[c1][c2] = df.stat.corr(c1, c2)
    return corrs


def profile_sample(df: DataFrame, n: int = 10) -> List[Any]:
    """Returns a sample of the first n records.

    Args:
        df (DataFrame): Input DataFrame.
        n (int): Number of records to sample. Defaults to 10.

    Returns:
        List[Any]: List of Rows.
    """
    return df.limit(n).collect()

def profile_memory_usage(df: DataFrame, sample_size: int = 1000) -> Dict[str, float]:
    """
    Estimate memory usage per column (in MB) based on a Spark sample.

    Args:
        df (DataFrame): Input Spark DataFrame.
        sample_size (int): Number of rows to sample. Defaults to 1000.

    Returns:
        Dict[str, float]: Mapping of column name to estimated memory usage in MB.
    """
    sampled = df.limit(sample_size).collect()
    usage_bytes = {col: 0 for col in df.columns}

    for row in sampled:
        for col in df.columns:
            value = row[col]
            if value is not None:
                try:
                    usage_bytes[col] += sys.getsizeof(value)
                except Exception:
                    usage_bytes[col] += 0  # fallback if object doesn't support sizeof

    row_count = df.count()
    scaling_factor = row_count / sample_size if sample_size > 0 else 1

    usage_mb = {
        col: (total_bytes * scaling_factor) / (1024 ** 2)
        for col, total_bytes in usage_bytes.items()
    }

    return usage_mb

def profile_cardinality(df: DataFrame) -> Dict[str, int]:
    """
    Counts distinct values per column.

    Args:
        df (DataFrame): Input DataFrame.

    Returns:
        Dict[str, int]: Mapping from column to number of distinct values.
    """
    return {c: df.select(c).distinct().count() for c in df.columns}


def profile_duplicates(df: DataFrame, keys: Optional[List[str]] = None) -> int:
    """Counts duplicate records in the DataFrame.

    Args:
        df (DataFrame): Input DataFrame.
        keys (List[str], optional): Columns to identify duplicates.
        If None, considers all columns.

    Returns:
        int: Number of duplicate records.
    """
    if keys:
        return df.count() - df.select(keys).dropDuplicates().count()
    return df.count() - df.dropDuplicates().count()
