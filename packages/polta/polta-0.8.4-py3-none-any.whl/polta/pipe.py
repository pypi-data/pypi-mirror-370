from dataclasses import dataclass, field
from datetime import datetime, UTC
from polars import DataFrame
from typing import Optional, Union

from polta.enums import WriteLogic
from polta.exceptions import (
  EmptyPipe,
  WriteLogicNotRecognized
)
from polta.exporter import Exporter
from polta.ingester import Ingester
from polta.table import Table
from polta.transformer import Transformer


@dataclass
class Pipe:
  """Changes and moves data in the metastore
  
  Positional Args:
    logic (Union[Ingester, Exporter, Transformer]): the pipe logic to handle data
  
  Initialized fields:
    id (str): the unique ID of the pipe for the pipeline
    table (Table): the destination Table
    write_logic (Optional[WriteLogic]): how the data should be placed in target table
  """
  logic: Union[Exporter, Ingester, Transformer]

  id: str = field(init=False)
  table: Table = field(init=False)
  write_logic: Optional[WriteLogic] = field(init=False)

  def __post_init__(self) -> None:
    self.id: str = '.'.join([
      'pp',
      self.logic.pipe_type.value,
      self.logic.table.id
    ])
    self.table: Table = self.logic.table
    self.write_logic = self.logic.write_logic

  def execute(self, dfs: dict[str, DataFrame] = {}, in_memory: bool = False,
              strict: bool = False) -> tuple[DataFrame, DataFrame, DataFrame]:
    """Executes the pipe

    Args:
      dfs (dict[str, DataFrame]): if applicable, source DataFrames (default {})
      in_memory (bool): indicates whether to run without saving (default False)
      strict (bool): indicates whether to fail on empty result (default False)

    Returns:
      passed, failed, quarantined (tuple[DataFrame, DataFrame, DataFrame]): the resulting DataFrames
    """
    print(f'Executing pipe {self.id}')
    
    # Record when the execution began
    execution_start: datetime = datetime.now(UTC)

    # Load in any extra data before transformation
    dfs.update(self.logic.get_dfs())

    # For in-memory exports, just carry over the table data
    # Otherwise, run the transformation/pre-load steps
    if isinstance(self.logic, Exporter) and in_memory:
      df: DataFrame = dfs[self.table.id]
    else:
      df: DataFrame = self.logic.transform(dfs)
      df: DataFrame = self.table.add_metadata_columns(df)
      df: DataFrame = self.table.conform_schema(df)

    # Run any tests and return the three data results
    passed, failed, quarantined = self.table.apply_tests(df)

    # Handle any quarantined records
    if not quarantined.is_empty():
      self.table.quarantine(quarantined)

    # If strict mode is enabled and dataset is empty, raise EmptyPipe
    succeeded: bool = (not strict) or (not passed.is_empty())

    # For standard runs and non-exports, save the passed data
    if isinstance(self.logic, (Ingester, Transformer)) and not in_memory:
      self.save(passed)
    
    # For exports, export the data
    if isinstance(self.logic, Exporter):
      self.logic.export(passed)

    # Print results
    print(f'  - Records passed: {passed.shape[0]}')
    print(f'  - Records failed: {failed.shape[0]}')
    print(f'  - Records quarantined: {quarantined.shape[0]}')

    # Log the pipe execution in the system table
    self.table.metastore.write_pipe_history(
      pipe_id=self.id,
      execution_start_ts=execution_start,
      strict=strict,
      succeeded=succeeded,
      in_memory=in_memory,
      passed_count=passed.shape[0],
      failed_count=failed.shape[0],
      quarantined_count=quarantined.shape[0]
    )

    # If the pipe failed, raise the EmptyPipe exception
    if not succeeded:
      raise EmptyPipe()
    # Otherwise, return remaining passed records
    return passed, failed, quarantined
  
  def save(self, df: DataFrame) -> None:
    """Saves a DataFrame into the target Delta Table
    
    Args:
      df (DataFrame): the DataFrame to load
    """
    self.table.create_if_not_exists(
      table_path=self.table.table_path,
      schema=self.table.schema.deltalake
    )
    print(f'Loading {df.shape[0]} record(s) into {self.table.table_path}')

    if self.write_logic.value == WriteLogic.APPEND.value:
      self.table.append(df)
    elif self.write_logic.value == WriteLogic.OVERWRITE.value:
      self.table.overwrite(df)
    elif self.write_logic.value == WriteLogic.UPSERT.value:
      self.table.upsert(df)
    else:
      raise WriteLogicNotRecognized(self.write_logic)
