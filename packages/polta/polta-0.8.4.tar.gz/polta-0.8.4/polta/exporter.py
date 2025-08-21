from dataclasses import dataclass, field
from datetime import datetime, UTC
from json import dumps
from os import makedirs, path
from polars import DataFrame
from typing import Optional

from polta.enums import ExportFormat, PipeType, WriteLogic
from polta.serializers import json
from polta.table import Table


@dataclass
class Exporter:
  """Executes an export of a Table
  
  Positional Args:
    table (Table): the main table for the export
    export_format (ExportFormat): how to save the data
  
  Optional Args:
    export_directory (str): where to save the data (default export volume)

  Initialized Fields:
    pipe_type (PipeType): what kind of pipe this is (i.e., EXPORTER)
    write_logic (Optional[WriteLogic]): how to save the data (i.e., None)
    exported_files (list[str]): the path of the exported files
  """
  table: Table
  export_format: ExportFormat
  export_directory: str = field(default_factory=lambda: '')

  pipe_type: PipeType = field(init=False)
  write_logic: Optional[WriteLogic] = field(init=False)
  exported_files: list[str] = field(init=False)

  def __post_init__(self) -> None:
    self.export_directory: str = self.export_directory or path.join(
      self.table.metastore.exports_directory,
      self.table.domain,
      self.table.quality.value,
      self.table.name
    )
    makedirs(self.export_directory, exist_ok=True)
    self.pipe_type: PipeType = PipeType.EXPORTER
    self.write_logic = None
    self.exported_files: list[str] = []

  def get_dfs(self) -> dict[str, DataFrame]:
    """Retrieves the base DataFrame if possible, or it returns nothing

    Returns:
      dfs (dict[str, DataFrame]): the base DataFrame in a dict
    """
    df: DataFrame = self.table.get()
    return {} if df.is_empty() else {self.table.id: df}

  def transform(self, dfs: dict[str, DataFrame]) -> DataFrame:
    """Returns the target table DataFrame from dfs
    
    Args:
      dfs (dict[str, DataFrame]): the DataFrames to transform
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    return dfs[self.table.id]

  def export(self, df: DataFrame) -> Optional[str]:
    """Exports the DataFrame to file storage

    Args:
      df (DataFrame): the DataFrame to export
    
    Returns:
      file_path (Optional[str]): if applicable, the resulting file_path
    """
    ts: str = datetime.now(UTC).strftime('%Y%m%d%H%M%S')
    file_name: str = f'{self.table.name}.{ts}.{self.export_format.value}'
    file_path: str = path.join(self.export_directory, file_name)
    if self.export_format.value == ExportFormat.CSV.value:
      self._to_csv(df, file_path)
    elif self.export_format.value == ExportFormat.JSON.value:
      self._to_json(df, file_path)
    else:
      raise NotImplementedError(f'Error: export format not implemented: {self.export_format.value}')
    self.exported_files.append(file_path)
    return file_path

  def _to_csv(self, df: DataFrame, file_path: str) -> None:
    """Exports the DataFrame to a CSV format

    Args:
      df (DataFrame): the DataFrame to export
      file_path (str): the target path of the file
    """
    df.write_csv(file_path)
  
  def _to_json(self, df: DataFrame, file_path: str) -> None:
    """Exports the DataFrame to a JSON format

    Args:
      df (DataFrame): the DataFrame to export
      file_path (str): the target path of the file
    """
    content: str = dumps(df.to_dicts(), default=json)
    open(file_path, 'w').write(content)
