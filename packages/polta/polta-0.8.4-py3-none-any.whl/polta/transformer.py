from dataclasses import dataclass, field
from polars import DataFrame, SQLContext
from types import FunctionType
from typing import Optional, Union

from polta.enums import PipeType, WriteLogic
from polta.exceptions import IncompatibleTransformLogic
from polta.table import Table


@dataclass
class Transformer:
  """Contains transformation logic to be used in a Pipe
  
  Positional Args:
    table (Table): the target Table
    load_logic (FunctionType): a method to load the source DataFrames
    transform_logic (Union[FunctionType, str]): a method/query to transform the DataFrames
  
  Optional Args:
    write_logic (WriteLogic): how to write to a Table (default APPEND)
  
  Initialized fields:
    pipe_type (PipeType): the type of pipe this is (i.e., TRANSFORMER)
  """
  table: Table
  load_logic: FunctionType
  transform_logic: Union[FunctionType, str]
  write_logic: WriteLogic = field(default_factory=lambda: WriteLogic.APPEND)

  pipe_type: PipeType = field(init=False)

  def __post_init__(self) -> None:
    self.pipe_type: PipeType = PipeType.TRANSFORMER

  def get_dfs(self) -> dict[str, DataFrame]:
    """Executes the load_logic callable to return source DataFrames

    Returns:
      dfs (dict[str, DataFrame]): the source DataFrames
    """
    return self.load_logic()

  def transform(self, dfs: dict[str, DataFrame]) -> DataFrame:
    """Applies the transform_logic callable to the DataFrames

    Args:
      dfs (dict[str, DataFrame]): the DataFrames to transform

    Returns:
      df (DataFrame): the transformed DataFrame
    """
    if isinstance(self.transform_logic, FunctionType):
      return self.transform_logic(dfs)
    elif isinstance(self.transform_logic, str):
      return SQLContext(frames=dfs).execute(
        query=self.transform_logic,
        eager=True
      )
    else:
      raise IncompatibleTransformLogic(self.transform_logic)
  
  def export(self, df: DataFrame) -> Optional[str]:
    """Exports the DataFrame in a desired format

    This method is unused for transformers

    Args:
      df (DataFrame): the DataFrame to export
    """
    return None
