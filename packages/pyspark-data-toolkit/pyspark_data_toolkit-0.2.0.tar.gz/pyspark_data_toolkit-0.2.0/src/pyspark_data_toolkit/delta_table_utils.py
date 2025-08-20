from pyspark.sql import DataFrame, SparkSession
from delta.tables import DeltaTable
from typing import Dict, List, Any, Optional, Union
import logging
from logging_metrics import configure_basic_logging
import os

__all__ = [
    "create_delta_table",
    "append_to_delta_table", 
    "overwrite_delta_table",
    "replace_delta_partitions",
    "merge_delta_table",
    "optimize_delta_table",
    "vacuum_delta_table"
]

def get_logger() -> logging.Logger:
    """Retorna um logger configurado."""
    return configure_basic_logging()

def _build_where_clause(filters: Union[str, Dict[str, Any]]) -> str:
    """
    Constrói uma cláusula WHERE de forma inteligente.
    
    Args:
        filters: Pode ser:
            - String SQL: "region = 'BR' AND date >= '2024-01-01'"
            - Dict simples: {"region": "BR", "date": "2024-01-01"}
            - Dict com operadores: {"date": {">=": "2024-01-01"}, "status": ["active", "pending"]}
    
    Returns:
        str: Cláusula WHERE formatada
    """
    if isinstance(filters, str):
        return filters
    
    if not isinstance(filters, dict):
        raise ValueError(f"filters deve ser str ou dict, recebido: {type(filters)}")
    
    clauses = []
    
    for column, condition in filters.items():
        if isinstance(condition, list):
            # Lista de valores -> IN
            if len(condition) == 1:
                clauses.append(f"{column} = {repr(condition[0])}")
            else:
                formatted_values = [repr(v) for v in condition]
                clauses.append(f"{column} IN ({', '.join(formatted_values)})")
        
        elif isinstance(condition, dict):
            # Dict com operadores
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
                    clauses.append(f"{column} {operator.upper()} {value}")
                else:
                    clauses.append(f"{column} {operator} {repr(value)}")
        else:
            # Valor simples -> igualdade
            clauses.append(f"{column} = {repr(condition)}")
    
    return " AND ".join(clauses)

def _ensure_path_exists(path: str) -> None:
    """Garante que o diretório existe."""
    os.makedirs(path, exist_ok=True)

def _set_table_properties(spark: SparkSession, table_name: str) -> None:
    """Define propriedades padrão para otimização automática."""
    spark.sql(f"""
        ALTER TABLE {table_name}
        SET TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact'  = 'true'
        )
    """)

# =============================================================================
# FUNÇÕES DE ESCRITA
# =============================================================================

def create_delta_table(
    df: DataFrame,
    table_name: str,
    table_path: str,
    partition_cols: Optional[List[str]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Cria uma nova tabela Delta.
    
    Args:
        df: DataFrame a ser salvo
        table_name: Nome completo da tabela (ex: 'silver.my_table')
        table_path: Caminho no filesystem onde salvar
        partition_cols: Colunas para particionamento
        logger: Logger para uso (opcional)
    """
    logger = logger or get_logger()
    
    try:
        _ensure_path_exists(table_path)
        
        # Verifica se já existe
        if DeltaTable.isDeltaTable(df.sparkSession, table_path):
            logger.warning(f"Tabela já existe: {table_name}")
            return
        
        writer = (
            df.write
            .format("delta")
            .mode("overwrite")
            .option("mergeSchema", "true")
            .option("path", table_path)
        )
        
        if partition_cols:
            logger.info(f"Criando tabela particionada por: {partition_cols}")
            writer = writer.partitionBy(*partition_cols)
        
        logger.info(f"Criando tabela Delta: {table_name}")
        writer.saveAsTable(table_name)
        
        _set_table_properties(df.sparkSession, table_name)
        logger.info(f"Tabela criada com sucesso: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro ao criar tabela {table_name}: {e}", exc_info=True)
        raise

def append_to_delta_table(
    df: DataFrame,
    table_name: str,
    table_path: str,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Adiciona dados a uma tabela Delta existente.
    
    Args:
        df: DataFrame com novos dados
        table_name: Nome completo da tabela
        table_path: Caminho da tabela
        logger: Logger para uso (opcional)
    """
    logger = logger or get_logger()
    
    try:
        _ensure_path_exists(table_path)
        
        logger.info(f"Adicionando {df.count()} registros à tabela: {table_name}")
        
        (
            df.write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .option("path", table_path)
            .saveAsTable(table_name)
        )
        
        logger.info(f"Dados adicionados com sucesso: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro ao adicionar dados à tabela {table_name}: {e}", exc_info=True)
        raise

def overwrite_delta_table(
    df: DataFrame,
    table_name: str,
    table_path: str,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Substitui completamente os dados de uma tabela Delta.
    
    Args:
        df: DataFrame com os novos dados
        table_name: Nome completo da tabela
        table_path: Caminho da tabela
        logger: Logger para uso (opcional)
    """
    logger = logger or get_logger()
    
    try:
        _ensure_path_exists(table_path)
        
        logger.info(f"Substituindo dados da tabela: {table_name}")
        
        (
            df.write
            .format("delta")
            .mode("overwrite")
            .option("mergeSchema", "true")
            .option("path", table_path)
            .saveAsTable(table_name)
        )
        
        logger.info(f"Tabela substituída com sucesso: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro ao substituir tabela {table_name}: {e}", exc_info=True)
        raise

def replace_delta_partitions(
    df: DataFrame,
    table_name: str,
    table_path: str,
    partition_filter: Union[str, Dict[str, Any]],
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Substitui apenas partições específicas de uma tabela Delta.
    
    Args:
        df: DataFrame com os novos dados
        table_name: Nome completo da tabela
        table_path: Caminho da tabela
        partition_filter: Filtro para as partições a serem substituídas
        logger: Logger para uso (opcional)
    
    Exemplos:
        # String SQL
        replace_delta_partitions(df, "my_table", "/path", "year = 2024 AND region = 'BR'")
        
        # Dict simples
        replace_delta_partitions(df, "my_table", "/path", {"year": 2024, "region": "BR"})
        
        # Dict com operadores
        replace_delta_partitions(df, "my_table", "/path", {
            "year": 2024,
            "region": ["BR", "US"],
            "date": {">=": "2024-01-01"}
        })
    """
    logger = logger or get_logger()
    
    try:
        _ensure_path_exists(table_path)
        
        where_clause = _build_where_clause(partition_filter)
        logger.info(f"Substituindo partições com filtro: {where_clause}")
        
        (
            df.write
            .format("delta")
            .mode("overwrite")
            .option("replaceWhere", where_clause)
            .option("path", table_path)
            .saveAsTable(table_name)
        )
        
        logger.info(f"Partições substituídas com sucesso: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro ao substituir partições da tabela {table_name}: {e}", exc_info=True)
        raise

def merge_delta_table(
    df: DataFrame,
    table_name: str,
    table_path: str,
    merge_keys: List[str],
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Executa operação MERGE: atualiza registros existentes ou insere novos.
    
    Args:
        df: DataFrame fonte para o merge
        table_name: Nome completo da tabela
        table_path: Caminho da tabela
        merge_keys: Colunas usadas para identificar registros (chave de negócio)
        logger: Logger para uso (opcional)
    """
    logger = logger or get_logger()
    
    if not merge_keys:
        raise ValueError("merge_keys não pode estar vazio")
    
    try:
        if not DeltaTable.isDeltaTable(df.sparkSession, table_path):
            logger.error(f"Tabela Delta não existe em: {table_path}")
            raise ValueError(f"Tabela Delta não existe em: {table_path}")
        
        record_count = df.count()
        logger.info(f"Executando merge de {record_count} registros na tabela: {table_name}")
        
        delta_table = DeltaTable.forPath(df.sparkSession, table_path)
        merge_condition = " AND ".join([f"target.{col} = source.{col}" for col in merge_keys])
        
        logger.info(f"Condição de merge: {merge_condition}")
        
        (
            delta_table.alias("target")
            .merge(df.alias("source"), merge_condition)
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
        
        logger.info(f"Merge executado com sucesso: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro ao executar merge na tabela {table_name}: {e}", exc_info=True)
        raise

# =============================================================================
# FUNÇÕES DE MANUTENÇÃO
# =============================================================================

def optimize_delta_table(
    spark: SparkSession,
    table_name: str,
    zorder_cols: Optional[List[str]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Executa OPTIMIZE em uma tabela Delta, opcionalmente com ZORDER.
    
    Args:
        spark: Sessão Spark ativa
        table_name: Nome completo da tabela
        zorder_cols: Colunas para ZORDER BY (opcional)
        logger: Logger para uso (opcional)
    """
    logger = logger or get_logger()
    
    try:
        if zorder_cols:
            zorder_expr = ", ".join(zorder_cols)
            logger.info(f"Executando OPTIMIZE com ZORDER BY ({zorder_expr}) na tabela: {table_name}")
            spark.sql(f"OPTIMIZE {table_name} ZORDER BY ({zorder_expr})")
        else:
            logger.info(f"Executando OPTIMIZE na tabela: {table_name}")
            spark.sql(f"OPTIMIZE {table_name}")
            
        logger.info(f"OPTIMIZE executado com sucesso: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro ao otimizar tabela {table_name}: {e}", exc_info=True)
        raise

def vacuum_delta_table(
    spark: SparkSession,
    table_name: str,
    retention_hours: int = 168,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Executa VACUUM em uma tabela Delta para limpeza de arquivos antigos.
    
    Args:
        spark: Sessão Spark ativa
        table_name: Nome completo da tabela
        retention_hours: Período de retenção em horas (padrão: 168 = 7 dias)
        logger: Logger para uso (opcional)
    """
    logger = logger or get_logger()
    
    try:
        logger.info(f"Executando VACUUM na tabela: {table_name} (retenção: {retention_hours}h)")
        spark.sql(f"VACUUM {table_name} RETAIN {retention_hours} HOURS")
        logger.info(f"VACUUM executado com sucesso: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro ao executar VACUUM na tabela {table_name}: {e}", exc_info=True)
        raise

# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def optimize_and_vacuum_delta_table(
    spark: SparkSession,
    table_name: str,
    zorder_cols: Optional[List[str]] = None,
    retention_hours: int = 168,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Executa OPTIMIZE seguido de VACUUM em uma tabela Delta.
    
    Args:
        spark: Sessão Spark ativa
        table_name: Nome completo da tabela
        zorder_cols: Colunas para ZORDER BY (opcional)
        retention_hours: Período de retenção para VACUUM (padrão: 168h = 7 dias)
        logger: Logger para uso (opcional)
    """
    logger = logger or get_logger()
    
    try:
        logger.info(f"Iniciando otimização completa da tabela: {table_name}")
        optimize_delta_table(spark, table_name, zorder_cols, logger)
        vacuum_delta_table(spark, table_name, retention_hours, logger)
        logger.info(f"Otimização completa finalizada: {table_name}")
        
    except Exception as e:
        logger.error(f"Erro na otimização completa da tabela {table_name}: {e}", exc_info=True)
        raise