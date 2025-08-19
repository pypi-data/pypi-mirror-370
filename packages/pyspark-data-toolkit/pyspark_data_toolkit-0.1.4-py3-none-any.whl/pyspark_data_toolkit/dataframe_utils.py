from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import ArrayType, StructType, StringType
from typing import List, Dict, Optional, Any
import logging
from logging_metrics import configure_basic_logging
from typing import List, Optional, Dict, Any

__all__ = [
    "rename_columns_by_list",
    "select_columns",
    "add_columns_by_list",
    "repartition_and_cache",
    "explode_array_column",
    "transform_all_nested_key_value_columns"
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()

def rename_columns_by_list(
    df: DataFrame,
    rename_mappings: List[Dict[str, str]],
    log: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Rename columns in a DataFrame based on a list of mapping dictionaries.

    Args:
        df (DataFrame): Input Spark DataFrame.
        rename_mappings (List[Dict[str, str]]): List of mappings with keys:
            - "column_name": original column name.
            - "new_name": new column name.

    Returns:
        DataFrame: DataFrame with columns renamed.
    """
    logger = log or get_logger()
    result_df = df
    for mapping in rename_mappings:
        try:
            old = mapping["column_name"]
            new = mapping["new_name"]
            if old in result_df.columns and new and new.strip():
                result_df = result_df.withColumnRenamed(old, new)
        except Exception as e:
            logger.error(f"Failed to rename column with mapping {mapping}: {e}")
            raise
    return result_df


def select_columns(
    df: DataFrame,
    columns_to_keep: List[str]
) -> DataFrame:
    """
    Select only the specified columns from a DataFrame.

    Args:
        df (DataFrame): Input Spark DataFrame.
        columns_to_keep (List[str]): List of column names to keep.

    Returns:
        DataFrame: DataFrame containing only the specified columns.
    """
    existing = [c for c in columns_to_keep if c in df.columns]
    return df.select(*existing)


def add_columns_by_list(
    df: DataFrame,
    required_columns: List[str],
    default_value: Any = None
) -> DataFrame:
    """
    Add missing columns to the DataFrame with a default value.

    Args:
        df (DataFrame): Input Spark DataFrame.
        required_columns (List[str]): List of required column names.
        default_value (Any): Default value to assign to new columns.

    Returns:
        DataFrame: DataFrame with all required columns present.
    """
    result_df = df
    for col in required_columns:
        if col not in result_df.columns:
            result_df = result_df.withColumn(col, F.lit(default_value))
    return result_df


def repartition_and_cache(
    df: DataFrame,
    partitions: int
) -> DataFrame:
    """
    Repartition the DataFrame and cache it in memory.

    Args:
        df (DataFrame): Input Spark DataFrame.
        partitions (int): Number of partitions to create.

    Returns:
        DataFrame: Repartitioned and cached DataFrame.
    """
    return df.repartition(partitions).cache()

def get_nested_column_type(schema, col_path: str):
    """
    Navega pelo schema para encontrar o tipo de uma coluna aninhada
    
    Args:
        schema: Schema do DataFrame
        col_path: Caminho da coluna (ex: 'properties.activities.element.name')
    
    Returns:
        DataType da coluna ou None se não encontrar
    """
    if '.' not in col_path:
        # Coluna simples
        if col_path in [field.name for field in schema.fields]:
            return schema[col_path].dataType
        return None
    
    # Coluna aninhada - navegar pelo caminho
    parts = col_path.split('.')
    current_schema = schema
    
    for part in parts:
        if isinstance(current_schema, StructType):
            # Procurar o campo na estrutura atual
            field_names = [field.name for field in current_schema.fields]
            if part not in field_names:
                return None
            
            # Encontrou o campo, pegar seu tipo
            field = next(field for field in current_schema.fields if field.name == part)
            current_schema = field.dataType
        else:
            # Se chegou aqui e não é StructType, não pode continuar navegando
            return None
    
    return current_schema

def explode_array_column(
    df: DataFrame,
    col_name: str,
    drop_original: bool = False,
    log: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Explode an array column into multiple rows.
    Supports nested columns like 'properties.activities' or 'data.items.values'

    Args:
        df (DataFrame): Input Spark DataFrame.
        col_name (str): Name of the array column to explode.
        drop_original (bool): Whether to drop the original column. Default is False.
        log (Optional[logging.Logger]): Logger instance.

    Returns:
        DataFrame: DataFrame with the array column exploded.
    """
    logger = log or logging.getLogger(__name__)
    
    try:
        # Verificar se a coluna existe
        if '.' not in col_name:
            # Coluna simples
            if col_name not in df.columns:
                logger.warning(f"Column '{col_name}' not found. Skipping explode.")
                return df
            col_schema = df.schema[col_name].dataType
        else:
            # Coluna aninhada - usar navegação dinâmica
            col_schema = get_nested_column_type(df.schema, col_name)
            if col_schema is None:
                logger.warning(f"Nested column '{col_name}' not found. Skipping explode.")
                return df

        # Verificar se é ArrayType
        if not isinstance(col_schema, ArrayType):
            logger.warning(f"Column '{col_name}' is not ArrayType. Skipping explode.")
            return df

        # Fazer o explode
        # Criar nome para nova coluna (substituir pontos por underscore)
        exploded_col_name = col_name.replace('.', '_')
        exploded = df.withColumn(exploded_col_name, F.explode_outer(F.col(col_name)))
        
        # Dropar coluna original se solicitado
        if drop_original:
            if '.' not in col_name:
                # Coluna simples - pode dropar normalmente
                return exploded.drop(col_name)
            else:
                # Coluna aninhada - avisar que não pode dropar
                logger.info(f"Cannot drop nested column '{col_name}'. Keeping original structure.")
                return exploded
        
        return exploded
        
    except Exception as e:
        logger.error(f"Failed to explode array column '{col_name}': {e}")
        raise


def transform_all_nested_key_value_columns(
    df: DataFrame,
    drop_original: bool = True,
    log: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Detect and convert all nested GA4-style key-value columns (array<struct<key,value>>) to MapType.

    Args:
        df (DataFrame): Input Spark DataFrame.
        drop_original (bool): Whether to drop the original column after transformation.

    Returns:
        DataFrame: DataFrame with transformed key-value maps.
    """
    logger = log or get_logger()

    result = df
    to_drop = []

    for field in df.schema.fields:
        try:
            # Check for GA4/Firebase style structure
            if isinstance(field.dataType, ArrayType) and isinstance(field.dataType.elementType, StructType):
                names = [f.name for f in field.dataType.elementType.fields]
                if "key" in names and "value" in names:
                    orig = field.name
                    new = f"{orig}_map"

                    # Detect internal value fields
                    value_fields = [
                        f.name
                        for f in field.dataType.elementType["value"].dataType.fields
                    ]

                    # Build the map with transformed key-value
                    result = result.withColumn(
                        new,
                        F.map_from_arrays(
                            F.expr(f"transform({orig}, x -> x.key)"),
                            F.expr(
                                f"transform({orig}, x -> coalesce({', '.join([f'x.value.{f}::string' for f in value_fields])}))"
                            )
                        )
                    )
                    to_drop.append(orig)
        except Exception as e:
            logger.warning(f"Failed to transform nested key-value column '{field.name}': {e}")

    if drop_original and to_drop:
        result = result.drop(*to_drop)

    return result
