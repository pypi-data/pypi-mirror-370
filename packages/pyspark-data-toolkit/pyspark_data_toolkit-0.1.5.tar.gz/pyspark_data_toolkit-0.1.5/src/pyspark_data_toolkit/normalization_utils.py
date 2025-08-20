from typing import List, Union, Optional, Dict, Any
from pyspark.sql import DataFrame, Column, functions as F
import re
import logging
import unicodedata
import collections
from logging_metrics import configure_basic_logging

__all__ = [
    "get_logger",
    "normalize_strings",
    "normalize_strings_simple",
    "normalize_column_names",
    "safe_string_to_double_spark",
    "fill_null_values",
    "fill_null_values_advanced"
]

accent_replacements = {
    '[àáâãäå]': 'a',
    '[èéêë]': 'e',
    '[ìíîï]': 'i',
    '[òóôõöø]': 'o',
    '[ùúûü]': 'u',
    '[ýÿ]': 'y',
    '[ñ]': 'n',
    '[ç]': 'c',
    '[ß]': 'ss',
    '[æ]': 'ae',
    '[œ]': 'oe',
    '[ÀÁÂÃÄÅ]': 'A',
    '[ÈÉÊË]': 'E',
    '[ÌÍÎÏ]': 'I',
    '[ÒÓÔÕÖØ]': 'O',
    '[ÙÚÛÜ]': 'U',
    '[ÝŸ]': 'Y',
    '[Ñ]': 'N',
    '[Ç]': 'C'
}

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()


def _apply_replacements(column: Column, replacements: dict) -> Column:
    """
    Applies a series of regex replacements to a Spark column.

    Args:
        column (Column): Spark column to modify.
        replacements (dict): Dictionary of regex pattern -> replacement string.

    Returns:
        Column: Modified Spark column.
    """
    for pattern, replacement in replacements.items():
        column = F.regexp_replace(column, pattern, replacement)
    return column


def normalize_strings(
    df: DataFrame,
    columns: List[str],
    new_suffix: str = "_norm",
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Normalizes strings in specified columns by removing accents, punctuation, extra spaces, and converting to lowercase.

    Args:
        df (DataFrame): Input DataFrame.
        columns (List[str]): List of columns to normalize.
        new_suffix (str): Suffix to add to new normalized columns.
        logger (Optional[logging.Logger]): Logger for auditing.

    Returns:
        DataFrame: DataFrame with normalized string columns added.
    """
    log = logger or get_logger()
    result_df = df

    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in DataFrame.")

        cleaned = F.trim(F.col(col).cast("string"))
        cleaned = _apply_replacements(cleaned, accent_replacements)
        cleaned = F.lower(cleaned)
        cleaned = F.regexp_replace(cleaned, r"[^\w\s]", "")
        cleaned = F.regexp_replace(cleaned, r"\s+", " ")
        cleaned = F.when(F.col(col).isNull() | (F.col(col) == ""), None).otherwise(cleaned)

        out_col = f"{col}{new_suffix}"
        result_df = result_df.withColumn(out_col, cleaned)
        log.info(f"normalize_strings: column '{col}' normalized to '{out_col}'")

    return result_df


def normalize_strings_simple(
    df: DataFrame,
    columns: List[str],
    new_suffix: str = "_norm",
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Simplified string normalization using translate() to remove accents and special characters.

    Args:
        df (DataFrame): Input DataFrame.
        columns (List[str]): List of columns to normalize.
        new_suffix (str): Suffix for normalized columns.
        logger (Optional[logging.Logger]): Logger instance.

    Returns:
        DataFrame: DataFrame with normalized string columns.
    """
    log = logger or get_logger()
    result_df = df

    accent_map = "áàäâãéèëêíìïîóòöôõúùüûçñ"
    clean_map  = "aaaaaeeeeiiiiooooouuuucn"

    for col in columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in DataFrame.")

        cleaned = (
            F.when(F.col(col).isNull() | (F.col(col) == ""), None)
            .otherwise(
                F.regexp_replace(
                    F.regexp_replace(
                        F.lower(
                            F.translate(F.trim(F.col(col).cast("string")), accent_map, clean_map)
                        ),
                        r"[^\w\s]", ""
                    ),
                    r"\s+", " "
                )
            )
        )
        out_col = f"{col}{new_suffix}"
        result_df = result_df.withColumn(out_col, cleaned)
        log.info(f"normalize_strings_simple: column '{col}' normalized to '{out_col}'")

    return result_df


def normalize_column_names(df: DataFrame) -> DataFrame:
    """
    Normalizes column names by removing accents and replacing special characters with underscores.

    Args:
        df (DataFrame): Input DataFrame.

    Returns:
        DataFrame: DataFrame with normalized column names.
    """
    temp_names = [f"tmp_col_{i}" for i in range(len(df.columns))]
    df_temp = df.toDF(*temp_names)

    def remove_accents(text: str) -> str:
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

    base_names = []
    for old_name in df.columns:
        new_name = remove_accents(old_name)
        new_name = re.sub(r"[^0-9a-zA-Z_]", "_", new_name.lower())
        base_names.append(new_name)

    # Ensure unique names
    name_count = collections.defaultdict(int)
    final_names = []
    for name in base_names:
        name_count[name] += 1
        suffix = f"_{name_count[name]}" if name_count[name] > 1 else ""
        final_names.append(f"{name}{suffix}")

    cols_aliased = [F.col(tmp).alias(new) for tmp, new in zip(temp_names, final_names)]
    return df_temp.select(*cols_aliased)


def safe_string_to_double_spark(
    df: DataFrame,
    columns: Union[str, List[str]] = None,
    return_none_if_error: bool = True
) -> DataFrame:
    """
    Converts string columns containing numbers to double in a robust way.

    Args:
        df (DataFrame): Input DataFrame.
        columns (Union[str, List[str]]): Columns to convert. If None, all columns.
        return_none_if_error (bool): Whether to return None or 0.0 on parse errors.

    Returns:
        DataFrame: DataFrame with double columns.
    """
    if columns is None:
        cols = df.columns
    elif isinstance(columns, str):
        cols = [columns]
    else:
        cols = columns

    result_df = df
    error_value = None if return_none_if_error else F.lit(0.0)

    for col_name in [c for c in cols if c in df.columns]:
        col_ref = F.col(col_name)
        cleaned_expr = (
            F.when(col_ref.isNull(), None)
            .when(col_ref == "", error_value)
            .when(
                col_ref.rlike(r"^\s*-?\d{1,3}(\.\d{3})*,\d+\s*$"),
                F.regexp_replace(F.regexp_replace(col_ref, r"\.", ""), ",", ".").cast("double")
            )
            .when(
                col_ref.rlike(r"^\s*-?\d+,\d+\s*$"),
                F.regexp_replace(col_ref, ",", ".").cast("double")
            )
            .when(
                col_ref.rlike(r"^\s*-?\d{1,3}(,\d{3})*\.\d+\s*$"),
                F.regexp_replace(col_ref, ",", "").cast("double")
            )
            .when(
                col_ref.rlike(r"^\s*-?\d+\.?\d*\s*$"),
                col_ref.cast("double")
            )
            .otherwise(
                F.when(
                    F.regexp_replace(F.regexp_replace(col_ref, r"[^\d,.-]", ""), ",", ".").cast("double").isNotNull(),
                    F.regexp_replace(F.regexp_replace(col_ref, r"[^\d,.-]", ""), ",", ".").cast("double")
                ).otherwise(error_value)
            )
        )
        result_df = result_df.withColumn(col_name, cleaned_expr)

    return result_df


def fill_null_values(
    df: DataFrame,
    columns: Union[str, List[str]],
    fill_value: Union[str, int, float, bool] = "",
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Replaces null, NaN, and common empty string values with a specified value.

    Args:
        df (DataFrame): Input DataFrame.
        columns (Union[str, List[str]]): Column(s) to clean.
        fill_value (Any): Value to replace nulls with.
        logger (Optional[logging.Logger]): Logger instance.

    Returns:
        DataFrame: Cleaned DataFrame.
    """
    log = logger or get_logger()
    cols = [columns] if isinstance(columns, str) else columns

    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    null_like = [
        "null", "NULL", "Null", "n/a", "N/A", "n.a.", "N.A.",
        "nan", "NaN", "NAN", "none", "None", "NONE",
        "#N/A", "#NULL!", "#DIV/0!", "", "  ", "   "
    ]

    result_df = df
    for col_name in cols:
        col_ref = F.col(col_name)
        condition = col_ref.isNull() | F.isnan(col_ref)
        for val in null_like:
            condition = condition | (F.trim(col_ref) == val)
        result_df = result_df.withColumn(col_name, F.when(condition, F.lit(fill_value)).otherwise(col_ref))
        log.info(f"fill_null_values: column '{col_name}' filled with '{fill_value}'")

    return result_df


def fill_null_values_advanced(
    df: DataFrame,
    column_fill_map: Dict[str, Any],
    logger: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Replaces null/NaN/empty values with custom fill values per column.

    Args:
        df (DataFrame): Input DataFrame.
        column_fill_map (Dict[str, Any]): Column name -> fill value.
        logger (Optional[logging.Logger]): Logger instance.

    Returns:
        DataFrame: Cleaned DataFrame.
    """
    log = logger or get_logger()
    missing_cols = [col for col in column_fill_map if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in DataFrame: {missing_cols}")

    result_df = df
    for col, value in column_fill_map.items():
        result_df = fill_null_values(result_df, [col], value, logger=log)
    log.info(f"fill_null_values_advanced: filled {len(column_fill_map)} columns.")
    return result_df
