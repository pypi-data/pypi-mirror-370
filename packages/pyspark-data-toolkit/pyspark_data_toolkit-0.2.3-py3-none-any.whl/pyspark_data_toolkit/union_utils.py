from typing import List, Union
from functools import reduce
from pyspark.sql import DataFrame, functions as F

__all__ = [
    "union_all_with_schema",
    "union_all"
]

def union_all_with_schema(df_list: List[DataFrame]) -> DataFrame:
    """Unifies multiple Spark DataFrames by aligning all columns.

    Ensures all columns from any DataFrame are included, filling missing ones with nulls,
    before applying `unionByName`.

    Args:
        df_list (List[DataFrame]): List of Spark DataFrames to be unified.

    Returns:
        DataFrame: Resulting DataFrame with unified schema and data.

    Raises:
        ValueError: If `df_list` is empty.
    """
    if not df_list:
        raise ValueError("The list of DataFrames passed to union_all_with_schema cannot be empty.")

    # Collect all unique column names across all DataFrames
    all_columns = list({col for df in df_list for col in df.columns})

    # Align columns in each DataFrame (fill missing with nulls)
    aligned_dfs = [
        df.select(*[F.col(c) if c in df.columns else F.lit(None).alias(c) for c in all_columns])
        for df in df_list
    ]

    # Use reduce to union all DataFrames by name
    return reduce(lambda a, b: a.unionByName(b), aligned_dfs)


def union_all(items: List[Union[DataFrame, dict, list]]) -> Union[DataFrame, list]:
    """Unifies a list of items, which can be Spark DataFrames or JSON (dict/list).

    - If all items are Spark DataFrames: calls `union_all_with_schema`.
    - If all items are JSON (dict or list): merges into a single list.
    - Mixed types are not supported.

    Args:
        items (List[Union[DataFrame, dict, list]]): List of items to merge.

    Returns:
        Union[DataFrame, list]: A unified DataFrame or a merged list.

    Raises:
        ValueError: If `items` is empty or contains mixed types.
    """
    if not items:
        raise ValueError("No items provided to union_all.")

    # All items are JSON-like (dicts or lists)
    if all(isinstance(x, (dict, list)) for x in items):
        merged: List[dict] = []
        for x in items:
            if isinstance(x, dict):
                merged.append(x)
            else:  # list of dicts
                merged.extend(x)
        return merged

    # All items are Spark DataFrames
    if all(isinstance(x, DataFrame) for x in items):
        return union_all_with_schema(items)  # type: ignore

    raise ValueError("All items must be either Spark DataFrames or JSON (dict/list), not mixed.")
