import polars as pl

from dataclasses import dataclass, field
from datetime import datetime, UTC
from deltalake import DeltaTable, Schema, TableFeatures
from os import getcwd, listdir, makedirs, path
from polars import DataFrame
from typing import Any

from polta.enums import TableQuality
from polta.exceptions import DomainDoesNotExist
from polta.schemas.system import file_history, pipe_history


@dataclass
class Metastore:
  """Dataclass for managing Polta metastores
  
  Optional Args:
    main_path (str): the directory of the metastore (default CWD + 'metastore')

  Initialized Fields:
    tables_directory (str): the path to the tables
    volumes_directory (str): the path to the volumes
  """
  main_path: str = field(default_factory=lambda: path.join(getcwd(), 'metastore'))

  tables_directory: str = field(init=False)
  volumes_directory: str = field(init=False)
  file_history_path: str = field(init=False)
  pipe_history_path: str = field(init=False)

  def __post_init__(self) -> None:
    self.tables_directory: str = path.join(self.main_path, 'tables')
    self.volumes_directory: str = path.join(self.main_path, 'volumes')
    self.exports_directory: str = path.join(self.volumes_directory, 'exports')
    self.quarantine_directory: str = path.join(self.volumes_directory, 'quarantine')
    self.ingestion_directory: str = path.join(self.volumes_directory, 'ingestion')
    self.sys_directory: str = path.join(self.volumes_directory, 'system')
    self.file_history_path: str = path.join(self.sys_directory, 'file_history')
    self.pipe_history_path: str = path.join(self.sys_directory, 'pipe_history')
    self.initialize_if_not_exists()

  def initialize_if_not_exists(self) -> None:
    """Initializes the metastore if it does not exist"""
    # Initialize the directories
    makedirs(self.main_path, exist_ok=True)
    makedirs(self.tables_directory, exist_ok=True)
    makedirs(self.volumes_directory, exist_ok=True)
    makedirs(self.exports_directory, exist_ok=True)
    makedirs(self.quarantine_directory, exist_ok=True)
    makedirs(self.ingestion_directory, exist_ok=True)

    # Initialize the system tables
    self.create_table_if_not_exists(
      table_path=self.file_history_path,
      schema=file_history,
      partition_by=['table_id']
    )
    self.create_table_if_not_exists(
      table_path=self.pipe_history_path,
      schema=pipe_history,
      partition_by=['pipe_id']
    )

  @staticmethod
  def create_table_if_not_exists(table_path: str, schema: Schema,
                                 partition_by: list[str] = []) -> None:
    """Creates a Delta Table if it does not exist

    Args:
        table_path (str): the path of the Delta Table
        schema (Schema): the table schema, in case the Delta Table needs to be created
        partition_by (list[str]): if applicable, the list of keys by which to partition
    """
    if not isinstance(table_path, str):
      raise TypeError('Error: table_path must be of type <str>')
    if not isinstance(schema, Schema):
      raise TypeError('Error: schema must be of type <Schema>')
    if not isinstance(partition_by, list):
      raise TypeError('Error: partition_by must be of type <list>')
    if not all(isinstance(k, str) for k in partition_by):
      raise TypeError('Error: all values in partition_by must be of type <str>')

    # If it exists already, return
    if DeltaTable.is_deltatable(table_path):
      return

    dt: DeltaTable = DeltaTable.create(
      table_uri=table_path,
      schema=schema,
      mode='ignore',
      partition_by=partition_by or None
    )
    dt.alter.add_feature(
      feature=TableFeatures.TimestampWithoutTimezone,
      allow_protocol_versions_increase=True
    )

  def list_domains(self) -> list[str]:
    """Retrieves the directories and names of available domains
    
    Returns:
      domains (list[str]): the available qualities
    """
    return listdir(self.tables_directory)

  def list_qualities(self, domain: str) -> list[TableQuality]:
    """Retrieves the available table qualities for a domain
    
    Args:
      domain (str): the domain to check
    
    Returns:
      qualities (list[TableQuality]): the available qualities for that domain
    """
    qualities_path: str = path.join(self.tables_directory, domain)
    if not path.exists(qualities_path):
      raise DomainDoesNotExist(domain)
    return [TableQuality(q) for q in listdir(qualities_path)]

  def domain_exists(self, domain: str) -> bool:
    """Indicates whether the domain exists
    
    Args:
      domain (str): the domain to check
    
    Returns:
      domain_exists (bool): indicates whether the domain exists
    """
    return path.exists(path.join(self.tables_directory, domain))

  def quality_exists(self, domain: str, quality: TableQuality) -> bool:
    """Indicates whether the quality exists under a given domain
    
    Args:
      domain (str): the domain containing the quality to check
      quality (TableQuality): the quality to check
    
    Returns:
      quality_exists (bool): indicates whether the quality exists
    """
    return path.exists(path.join(self.tables_directory, domain, quality.value))

  def get_file_history(self, table_id: str) -> DataFrame:
    """Retrieves a file_history DataFrame for a table by id

    Args:
      table_id (str): the unique ID of the table
    
    Returns:
      df (DataFrame): the resulting file history DataFrame
    """
    return (pl
      .read_delta(self.file_history_path)
      .filter(pl.col('table_id').eq(table_id))
      .select('_file_path', '_file_mod_ts')
      .unique()
      .group_by('_file_path')
      .agg(pl.col('_file_mod_ts').max())
    )

  def write_file_history(self, table_id: str, df: DataFrame) -> None:
    """Writes the file history into the system table
    
    Args:
      table_id (str): the unique ID of the table
      df (DataFrame): the DataFrame containing history information
    """
    df: DataFrame = (df
      .select(
        pl.lit(table_id).alias('table_id'),
        pl.col('_file_path'),
        pl.col('_file_mod_ts'),
        pl.col('_ingested_ts')
      )
    )
    df.write_delta(
      target=self.file_history_path,
      mode='append'
    )

  def clear_file_history(self, table_id: str) -> None:
    """Removes the file history of a table, typically after truncation
    
    Args:
      table_id (str): the unique ID of the table
    """
    DeltaTable(self.file_history_path).delete(f'table_id = \'{table_id}\'')

  def write_pipe_history(self, pipe_id: str, execution_start_ts: datetime, strict: bool,
                         succeeded: bool, in_memory: bool, passed_count: int,
                         failed_count: int, quarantined_count: int) -> None:
    """Writes a record to the pipe_history system table

    Args:
      pipe_id (str): the unique ID of the pipe
      execution_start_ts (datetime): when the pipe began
      strict (bool): indicates whether the pipe ran in strict mode
      succeeded (bool): indicates whether the pipe succeeded
      in_memory (bool): indicates whether the pipe ran in-memory
      passed_count (int): the number of records that passed
      failed_count (int): the number of records that failed
      quarantined_count (int): the number of records that got quarantined
    """
    now: datetime = datetime.now(UTC)
    record: dict[str, Any] = {
      'pipe_id': pipe_id,
      'execution_start_ts': execution_start_ts,
      'execution_end_ts': now,
      'execution_duration': (now - execution_start_ts).total_seconds(),
      'strict': strict,
      'succeeded': succeeded,
      'in_memory': in_memory,
      'total_count': passed_count + failed_count + quarantined_count,
      'passed_count': passed_count,
      'failed_count': failed_count,
      'quarantined_count': quarantined_count
    }
    DataFrame([record]).write_delta(
      target=self.pipe_history_path,
      mode='append'
    )

  def get_pipe_history(self, pipe_id: str = '') -> DataFrame:
    """Retrieves the pipe_history system table
    
    Args:
      pipe_id (str): if applicable, the unique ID of the pipe
    
    Returns:
      df (DataFrame): the pipe_history DataFrame
    """
    df: DataFrame = pl.read_delta(self.pipe_history_path)
    if pipe_id:
      df: DataFrame = df.filter(pl.col('pipe_id').eq(pipe_id))
    return df
