from typing import List, Dict, Any, Optional
import re
import logging
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
from pyspark.sql.types import StringType, StructType
from logging_metrics import configure_basic_logging

__all__ = [
    "extract_json_fields",
    "flatten_json_columns",
    "infer_json_schema",
    "extract_field_with_transform",
    "extract_field_with_explode",
    ""
]

def get_logger() -> logging.Logger:
    """Inicializa e retorna um logger configurado para escrita em arquivo.

    Args:
        logger (Optional[logging.Logger]): Logger já existente.
        name (str): Nome do logger. Defaults to __name__.

    Returns:
        logging.Logger: Logger configurado com rotação de arquivos.
    """
    return configure_basic_logging()


def extract_json_fields(
    df: DataFrame,
    json_mappings: List[Dict[str, Any]],
    logger: Optional[logging.Logger] = None,
    sanitize_strings=True
) -> DataFrame:
    """Extrai campos de colunas JSON (string) com base em mapeamentos.

    Cada mapeamento deve ser um dict com:
      - 'column_origem': nome da coluna JSON de entrada
      - 'column_destinations': lista de dicts, cada um com:
          * 'alias_name': nome da coluna de saída
          * 'path_key': expressão JSONPath para extração
          * 'data_type': tipo de dado alvo (ex: 'int', 'boolean', 'double', 'date', 'timestamp', etc.)

    Args:
        df (DataFrame): DataFrame de entrada contendo colunas JSON em string.
        json_mappings (List[Dict[str, Any]]): Lista de mapeamentos para extração.
        logger (logging.Logger, optional): Logger para auditoria. Se None, usa `get_logger()`.

    Returns:
        DataFrame: DataFrame com as novas colunas extraídas e corretamente convertidas.
    """
    log = logger or get_logger()
    result_df = df

    if not json_mappings:
        return df

    for mapping in json_mappings:
        src = mapping["column_origem"]
        if src not in result_df.columns:
            log.warning(f"Coluna JSON de origem '{src}' não encontrada, pulando.")
            continue

        for dest in mapping["column_destinations"]:
            alias = dest["alias_name"]
            path = dest["path_key"]
            dtype = dest["data_type"].lower()
            log.debug(f"Extraindo '{path}' de '{src}' para '{alias}' como {dtype}")

            result_df = result_df.withColumn(alias, F.get_json_object(F.col(src), path))

            if re.fullmatch(r"int(eger)?", dtype):
                result_df = result_df.withColumn(alias, F.col(alias).cast("int"))
            elif "bool" in dtype:
                result_df = result_df.withColumn(alias, F.col(alias).cast("boolean"))
            elif any(t in dtype for t in ["numeric", "decimal", "double", "float", "real", "money"]):
                result_df = result_df.withColumn(alias, F.col(alias).cast("double"))
            elif dtype == "date":
                result_df = result_df.withColumn(alias, F.to_date(F.col(alias)))
            elif dtype in ["datetime", "timestamp"]:
                result_df = result_df.withColumn(alias, F.to_timestamp(F.col(alias)))
            else:
                if sanitize_strings:
                    result_df = result_df.withColumn(
                        alias,
                        F.trim(
                            F.regexp_replace(
                                F.regexp_replace(F.col(alias).cast("string"), r"[\r\n]+", " "),
                                r"\s+", " "
                            )
                        )
                    )
                else:
                    result_df = result_df.withColumn(alias, F.col(alias).cast("string"))

    return result_df

def flatten_json_columns(df: DataFrame, parent: str = "", drop_structs: bool = True) -> DataFrame:
    """
    Desaninha recursivamente colunas StructType em colunas planas.

    Para cada coluna do tipo StructType no DataFrame, expande seus campos como colunas
    com prefixo `<parent><field>_<subfield>` e remove as structs originais a menos que drop_structs=False.

    Args:
        df (DataFrame): DataFrame de entrada possivelmente com colunas aninhadas.
        parent (str): Prefixo para colunas aninhadas (usado na recursão).
        drop_structs: se True, remove os structs após expandir.

    Returns:
        DataFrame: DataFrame com todas as colunas StructType desaninhadas.
    """
    
    def get_all_paths(schema, prefix=""):
        """Recursivamente encontra todos os caminhos para campos não-struct"""
        paths = []
        
        for field in schema.fields:
            field_name = field.name
            field_type = field.dataType
            
            # Constrói o caminho completo
            if prefix:
                current_path = f"{prefix}.{field_name}"
            else:
                current_path = field_name
            
            if isinstance(field_type, StructType):
                # Se é struct, recursivamente processa os subcampos
                paths.extend(get_all_paths(field_type, current_path))
            else:
                # Se é campo primitivo, adiciona à lista
                paths.append(current_path)
        
        return paths
    
    # Pega todos os caminhos de campos primitivos
    all_paths = get_all_paths(df.schema)
    
    # Se não há campos aninhados, retorna o DataFrame original
    if not any('.' in path for path in all_paths):
        return df
    
    # Constrói as expressões de seleção
    select_expressions = []
    
    for path in all_paths:
        if '.' in path:
            # Campo aninhado - cria alias flatten
            if parent:
                alias = f"{parent}{path.replace('.', '_')}"
            else:
                alias = path.replace('.', '_')
            select_expressions.append(F.col(path).alias(alias))
        else:
            # Campo de nível superior
            if not drop_structs or not any(field.name == path and isinstance(field.dataType, StructType) 
                                         for field in df.schema.fields):
                select_expressions.append(F.col(path))
    
    # Se drop_structs=False, mantém também as colunas struct originais
    if not drop_structs:
        for field in df.schema.fields:
            if isinstance(field.dataType, StructType):
                select_expressions.append(F.col(field.name))
    
    return df.select(select_expressions)

def extract_field_with_transform(df, json_column, field_name, output_column):
    """
    Extrai um campo específico de uma lista de JSONs usando funções nativas do Spark.
    
    Parâmetros:
        df: DataFrame do Spark
        json_column (str): Nome da coluna que contém a lista de objetos JSON
        field_name (str): Nome do campo a ser extraído
        output_column (str): Nome da coluna de saída
    
    Retorna:
        DataFrame com a nova coluna contendo os valores extraídos separados por vírgula
    """
    return df.withColumn(
        output_column,
        F.when(
            F.size(F.col(json_column)) > 0,
            F.concat_ws(
                ",",
                F.transform(
                    F.col(json_column),
                    lambda x: F.col(x)[field_name].cast(StringType())
                )
            )
        ).otherwise(F.lit(None))
    )


def infer_json_schema(df: DataFrame, json_col: str) -> DataFrame:
    """Converte uma coluna JSON string em StructType inferido automaticamente.

    Utiliza o RDD do DataFrame para inferir o schema e aplica `from_json`.

    Args:
        df (DataFrame): DataFrame contendo coluna JSON em string.
        json_col (str): Nome da coluna a ser convertida.

    Returns:
        DataFrame: DataFrame com a coluna `json_col` transformada em struct.
    """
    spark = df.sparkSession
    schema = spark.read.json(df.rdd.map(lambda row: row[json_col])).schema
    return df.withColumn(json_col, F.from_json(F.col(json_col), schema))

def extract_field_with_explode(df, json_column, field_name, output_column, id_columns=None):
    """
    Extrai campo usando explode e depois reagrupa.
    Útil quando você precisa de mais controle sobre a transformação.
    
    Parâmetros:
        df: DataFrame do Spark
        json_column (str): Nome da coluna que contém a lista de objetos JSON
        field_name (str): Nome do campo a ser extraído
        output_column (str): Nome da coluna de saída
        id_columns (list): Lista de colunas para usar como chave de agrupamento
    """
    if id_columns is None:
        # Se não tiver colunas de ID, cria um ID temporário
        df_with_id = df.withColumn("temp_id", F.monotonically_increasing_id())
        id_columns = ["temp_id"]
        temp_id_created = True
    else:
        df_with_id = df
        temp_id_created = False
    
    # Explode a lista de JSON
    exploded_df = df_with_id.select(
        *id_columns,
        F.explode(F.col(json_column)).alias("json_item")
    )
    
    # Extrai o campo específico
    extracted_df = exploded_df.select(
        *id_columns,
        F.col(f"json_item.{field_name}").cast(StringType()).alias("extracted_value")
    ).filter(F.col("extracted_value").isNotNull())
    
    # Reagrupa e concatena com vírgulas
    result_df = extracted_df.groupBy(*id_columns).agg(
        F.concat_ws(",", F.collect_list("extracted_value")).alias(output_column)
    )
    
    # Faz join de volta com o DataFrame original
    final_df = df_with_id.join(result_df, id_columns, "left")
    
    # Remove o ID temporário se foi criado
    if temp_id_created:
        final_df = final_df.drop("temp_id")
    
    return final_df
