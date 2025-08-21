from dataclasses import dataclass, field
from deltalake import Field, Schema
from polars.datatypes import DataType

from polta.enums import TableQuality
from polta.maps import Maps
from polta.schemas.table import failed_test


@dataclass
class TableSchema:
  """Contains a schema with parameters indicating when the schema is effective
  
  Positional Args:
    raw_deltalake (Schema): the schema of the table (without metadata fields)
    quality (TableQuality): the quality of the table
  
  Initialized Fields:
    raw_polars (dict[str, DataType]): the raw schema as a polars dict
    metadata_fields (list[Field]): the table metadata fields based on quality
    metadata_columns (list[str]): the names of the metadata fields
    deltalake (Schema): the full table schema as a deltalake Schema
    polars (dict[str, DataType]): the full table schema as a polars dict
    raw_columns (list[str]): the names of the raw fields
    columns (list[str]): the names of the full table fields
  """
  raw_deltalake: Schema
  quality: TableQuality

  raw_polars: dict[str, DataType] = field(init=False)
  metadata_fields: list[Field] = field(init=False)
  deltalake: Schema = field(init=False)
  polars: dict[str, DataType] = field(init=False)
  quarantine: Schema = field(init=False)
  raw_columns: list[str] = field(init=False)
  metadata_columns: list[str] = field(init=False)
  columns: list[str] = field(init=False)
  failure_column: str = field(init=False)

  def __post_init__(self) -> None:
    # Create the schemas
    self.raw_polars: dict[str, DataType] = Maps \
      .deltalake_schema_to_polars_schema(self.raw_deltalake)
    self.metadata_fields: list[Field] = Maps \
      .quality_to_metadata_columns(self.quality)
    self.deltalake: Schema = Schema(
      self.metadata_fields + self.raw_deltalake.fields
    )
    self.polars: dict[str, DataType] = Maps \
      .deltalake_schema_to_polars_schema(self.deltalake)
    self.quarantine: dict[str, DataType] = Maps \
      .deltalake_schema_to_polars_schema(
        Schema(self.deltalake.fields + failed_test.fields)
      )
    self.failure_column: str = Maps.quality_to_failure_column(self.quality)

    # Store the columns
    self.raw_columns: list[str] = list(self.raw_polars.keys())
    self.metadata_columns: list[str] = list([f.name for f in self.metadata_fields])
    self.columns: list[str] = list(self.polars.keys())
