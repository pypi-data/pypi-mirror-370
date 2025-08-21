import polars as pl

from dataclasses import dataclass, field
from datetime import datetime, UTC
from deltalake import Schema
from os import listdir, path
from polars import DataFrame
from polars.datatypes import DataType, List, String, Struct
from typing import Optional
from uuid import uuid4

from polta.enums import DirectoryType, PipeType, RawFileType, WriteLogic
from polta.exceptions import DirectoryTypeNotRecognized
from polta.maps import Maps
from polta.schemas.ingester import payload
from polta.table import Table
from polta.types import ExcelSpreadsheetEngine, RawMetadata
from polta.udfs import file_path_to_json, file_path_to_payload


@dataclass
class Ingester:
  """Dataclass for ingesting files into the target table
  
  Positional Args:
    table (Table): the target table for ingestion
    directory_type (DirectoryType): the kind of source directory to ingest
    raw_file_type (RawFileType): the format of the source files
  
  Optional Args:
    write_logic (WriteLogic): how to save the data (default APPEND)
  
  Initialized Fields:
    pipe_type (PipeType): what kind of pipe this is (i.e., INGESTER)
    simple_payload (bool): indicates whether the load is simple
    payload_schema (dict[str, DataType]): the polars fields for a simple ingestion
  """
  table: Table
  directory_type: DirectoryType
  raw_file_type: RawFileType
  write_logic: WriteLogic = field(default_factory=lambda: WriteLogic.APPEND)

  pipe_type: PipeType = field(init=False)
  simple_payload: bool = field(init=False)
  payload_schema: dict[str, DataType] = field(init=False)
  excel_engine: ExcelSpreadsheetEngine = field(default_factory=lambda: 'openpyxl')

  def __post_init__(self) -> None:
    self.pipe_type: PipeType = PipeType.INGESTER
    self.simple_payload: bool = self.table.schema.raw_deltalake.fields == payload.fields
    self.payload_schema: dict[str, DataType] = Maps.deltalake_schema_to_polars_schema(
      schema=Schema(self.table.schema.metadata_fields + payload.fields)
    )

  def get_dfs(self) -> dict[str, DataFrame]:
    """Ingests new files as DataFrames in a dict object
    
    Returns:
      dfs (dict[str, DataFrame]): the new DataFrames
    """
    df: DataFrame = self._get_metadata()
    df = self._filter_by_history(df)

    if df.is_empty():
      return {self.table.id: DataFrame([], self.table.schema.polars)}
    else:
      return {self.table.id: self._ingest_files(df)}

  def transform(self, dfs: dict[str, DataFrame]) -> DataFrame:
    """Returns the target table DataFrame from dfs
    
    Args:
      dfs (dict[str, DataFrame]): the DataFrames to transform
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    return dfs[self.table.id]

  def export(self, df: DataFrame) -> Optional[str]:
    """Exports the DataFrame in a desired format

    This method is unused for ingesters

    Args:
      df (DataFrame): the DataFrame to export
    """
    return None

  def _get_file_paths(self) -> list[str]:
    """Retrieves a list of file paths based on ingestion parameters
        
    Returns:
      file_paths (list[str]): the resulting applicable file paths
    """
    if self.directory_type.value == DirectoryType.SHALLOW.value:
      return [
        path.join(self.table.ingestion_zone_path, f)
        for f in listdir(self.table.ingestion_zone_path)
      ]
    elif self.directory_type.value == DirectoryType.DATED.value:
      file_paths: list[str] = []
      for date_str in listdir(self.table.ingestion_zone_path):
        file_paths.extend([
          path.join(self.table.ingestion_zone_path, date_str, f)
          for f in listdir(path.join(self.table.ingestion_zone_path, date_str))
        ])
      return file_paths
    else:
      raise DirectoryTypeNotRecognized(self.directory_type)

  def _get_metadata(self) -> DataFrame:
    """Retrieves source file metadata as a DataFrame
        
    Returns:
      df (DataFrame): the metadata DataFrame
    """
    file_paths: list[str] = self._get_file_paths()
    metadata: list[RawMetadata] = [self._get_file_metadata(p) for p in file_paths]
    return DataFrame(metadata, schema=self.payload_schema)

  def _filter_by_history(self, metadata: list[RawMetadata]) -> DataFrame:
    """Removes files from ingestion attempt that have already been ingested
    
    Args:
      metadata (list[RawMetadata]): the file metadata to ingest
    
    Returns:
      file_paths (DataFrame): the resulting DataFrame object with the filtered paths
    """
    # Convert the file_paths field into a DataFrame
    paths: DataFrame = DataFrame(metadata, schema=self.payload_schema)

    # Retrieve the history from the target table
    hx: DataFrame = self.table.metastore.get_file_history(self.table.id)

    # Filter the paths by the temporary history DataFrame
    return (paths
      .join(hx, '_file_path', 'left')
      .filter(
        (pl.col('_file_mod_ts') > pl.col('_file_mod_ts_right')) |
        (pl.col('_file_mod_ts_right').is_null())
      )
      .drop('_file_mod_ts_right')
    )

  def _ingest_files(self, df: DataFrame) -> DataFrame:
    """Ingests files in the DataFrame according to file type / desired output
    
    Args:
      df (DataFrame): the files to load
    
    Returns:
      df (DataFrame): the ingested files
    """
    if self.simple_payload:
      df: DataFrame = self._run_simple_load(df)
    elif self.raw_file_type.value == RawFileType.CSV.value:
      df: DataFrame = self._run_csv_load(df)
    elif self.raw_file_type.value == RawFileType.JSON.value:
      df: DataFrame = self._run_json_load(df)
    elif self.raw_file_type.value == RawFileType.EXCEL.value:
      df: DataFrame = self._run_excel_load(df)
    else:
      raise NotImplementedError(self.raw_file_type)

    # Save the ingestion history
    self.table.metastore.write_file_history(self.table.id, df)

    return df

  def _get_file_metadata(self, file_path: str) -> RawMetadata:
    """Retrieves file metadata from a file

    Args:
      file_path (str): the path to the file
    
    Returns:
      raw_metadata (RawMetadata): the resulting raw metadata of the file
    """
    if not path.exists(file_path):
      raise FileNotFoundError()

    return RawMetadata(
      _raw_id=str(uuid4()),
      _ingested_ts=datetime.now(UTC),
      _file_path=file_path,
      _file_name=path.basename(file_path),
      _file_mod_ts=datetime.fromtimestamp(path.getmtime(file_path), tz=UTC)
    )

  def _run_simple_load(self, df: DataFrame) -> DataFrame:
    """Retrieves the payload from the file path for each row
    
    Args:
      df (DataFrame): the data with metadata to load
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    return (df
      .with_columns([
        pl.col('_file_path')
          .map_elements(file_path_to_payload, return_dtype=String)
          .alias('payload')
      ])
    )

  def _run_json_load(self, df: DataFrame) -> DataFrame:
    """Retrieves the payload values from the file path for each row
    
    Args:
      df (DataFrame): the data with metadata to load
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    df: DataFrame = (df
      .with_columns([
        pl.col('_file_path')
          .map_elements(
            function=file_path_to_json,
            return_dtype=List(Struct(self.table.schema.raw_polars))
          )
          .alias('payload')
      ])
      .explode('payload')
      .with_columns([
        pl.col('payload').struct.field(f).alias(f)
        for f in self.table.schema.raw_polars.keys()
      ])
      .drop('payload')
    )
    return df
  
  def _run_csv_load(self, df: DataFrame) -> DataFrame:
    """Executes a CSV load against applicable files

    Args:
      df (DataFrame): the data with metadata to load

    Returns:
      df (DataFrame): the resulting DataFrame
    """
    out_df: Optional[DataFrame] = None
    for file_path in [r['_file_path'] for r in df.select('_file_path').to_dicts()]:
      csv_df: DataFrame = (pl
        .read_csv(
          source=file_path,
          schema=self.table.schema.raw_polars,
          try_parse_dates=True
        )
        .with_columns([pl.lit(file_path).alias('_file_path')])
      )
      if out_df is None:
        out_df: DataFrame = csv_df
      else:
        out_df: DataFrame = pl.concat([out_df, csv_df])
    out_df: DataFrame = out_df.join(df, '_file_path', 'inner')
    return out_df

  def _run_excel_load(self, df: DataFrame) -> DataFrame:
    """Executes an Excel load against applicable files

    Args:
      df (DataFrame): the data with metadata to load
    
    Returns:
      df (DataFrame): the resulting DataFrame
    """
    return (pl
      .read_excel(
        source=[r['_file_path'] for r in df.select('_file_path').to_dicts()],
        sheet_id=1,
        has_header=True,
        engine=self.excel_engine,
        include_file_paths='_file_path',
        drop_empty_rows=True,
        schema_overrides=self.table.schema.raw_polars
      )
      .join(df, '_file_path', 'inner')
    )
