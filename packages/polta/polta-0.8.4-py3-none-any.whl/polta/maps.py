from deltalake import Field, Schema
from deltalake.schema import ArrayType
from json import loads
from polars.datatypes import (
  Boolean,
  DataType as plDataType,
  Date,
  Datetime,
  Float32,
  Float64,
  Int32,
  Int64,
  List,
  String
)
from typing import Optional, Union

from polta.enums import TableQuality
from polta.exceptions import DataTypeNotRecognized
from polta.schemas.table import (
  raw_metadata,
  conformed_metadata,
  canonical_metadata,
  standard_metadata
)


class Maps:
  """Contains various mapper fields and methods for Polta operations"""
  DELTALAKE_TO_POLARS_FIELD: dict[str, plDataType] = {
    'boolean': Boolean,
    'date': Date,
    'double': Float64,
    'float': Float32,
    'integer': Int32,
    'long': Int64,
    'string': String,
    'timestamp': Datetime(time_zone='UTC')
  }
  POLARS_TO_DELTALAKE_FIELD: dict[plDataType, str] = {
    Boolean: 'boolean',
    Date: 'date',
    Float64: 'double',
    Float32: 'float',
    Int32: 'integer',
    Int64: 'long',
    String: 'string',
    Datetime(time_zone='UTC'): 'timestamp'
  }
  QUALITY_TO_METADATA_COLUMNS: dict[str, list[Field]] = {
    TableQuality.RAW.value: raw_metadata.fields,
    TableQuality.CONFORMED.value: conformed_metadata.fields,
    TableQuality.CANONICAL.value: canonical_metadata.fields,
    TableQuality.STANDARD.value: standard_metadata.fields
  }
  QUALITY_TO_FAILURE_COLUMN: dict[str, str] = {
    TableQuality.RAW.value: '_raw_id',
    TableQuality.CONFORMED.value: '_conformed_id',
    TableQuality.CANONICAL.value: '_canonicalized_id',
    TableQuality.STANDARD.value: '_id'
  }

  @staticmethod
  def deltalake_field_to_polars_field(delta_field: Union[dict, str]) -> plDataType:
    """Maps an individual Delta field to a Polars data type
    
    Args:
      delta_field (str): the field name (e.g., 'boolean', 'date')
    
    Returns:
      dt (DataType): the resulting Polars data type
    """
    wrap_in_list: bool = False
    if isinstance(delta_field, dict) and delta_field.get('type') == 'array':
      delta_field: str = delta_field.get('elementType')
      wrap_in_list: bool = True
    if not isinstance(delta_field, str):
      raise TypeError('Error: delta_field must be of type <str> or <dict>')
    dt: Union[plDataType, str] = Maps.DELTALAKE_TO_POLARS_FIELD.get(delta_field, '')
    if isinstance(dt, str):
      raise DataTypeNotRecognized(dt)
    return List(dt) if wrap_in_list else dt

  @staticmethod
  def deltalake_schema_to_polars_schema(schema: Schema) -> dict[str, plDataType]:
    """Converts the existing Delta Lake schema and returns it as a dict compatible to Polars DataFrames

    Args:
      schema (Schema): the original deltalake schema
    
    Returns:
      schema.polars (dict[str, DataType]): the schema as a dict, compatible with Polars DataFrames
    """
    polars_schema: dict[str, plDataType] = {}

    for field in loads(schema.to_json())['fields']:
      polars_schema[field['name']] = Maps.deltalake_field_to_polars_field(field['type'])
      if field['type'] == 'timestamp':
        polars_schema[field['name']]
      
    return polars_schema  

  @staticmethod
  def polars_field_to_deltalake_field(column: str, data_type: plDataType) -> Field:
    """Converts a polars field to a deltalake field
    
    Args:
      column (str): the name of the column
      data_type (DataType): polars DataType
    
    Returns:
      field (Field): the resulting deltalake field
    """
    try:
      if isinstance(data_type, List):
        dt: Optional[str] = Maps.POLARS_TO_DELTALAKE_FIELD[data_type.inner]
        return Field(column, ArrayType(dt))
      else:
        dt: Optional[str] = Maps.POLARS_TO_DELTALAKE_FIELD[data_type]
        return Field(column, dt)
    except KeyError:
      raise DataTypeNotRecognized(data_type)
  
  @staticmethod
  def polars_schema_to_deltalake_schema(schema: dict[str, plDataType]) -> Schema:
    """Converts a polars schema to a deltalake schema
    
    Args:
      schema (dict[str, DataType]): the original polars schema
    
    Returns:
      schema (Schema): the resulting deltalake schema
    """
    fields: list[plDataType] = []
    for column, data_type in schema.items():
      fields.append(Maps.polars_field_to_deltalake_field(column, data_type))
    return Schema(fields)

  @staticmethod
  def quality_to_failure_column(quality: TableQuality) -> str:
    """Converts a table quality to the failure column
    
    Args:
      quality (TableQuality): the quality of the table
    
    Returns:
      failure_column (str): the name of the failure column for that quality
    """
    return Maps.QUALITY_TO_FAILURE_COLUMN[quality.value]

  @staticmethod
  def quality_to_metadata_columns(quality: TableQuality) -> list[Field]:
    """Converts a table quality to metadata columns for that quality
  
    Args:
      quality (TableQuality): the quality of the table
    
    Returns:
      metadata_columns(list[Field]): the metadata columns for that quality
    """
    return Maps.QUALITY_TO_METADATA_COLUMNS[quality.value]
