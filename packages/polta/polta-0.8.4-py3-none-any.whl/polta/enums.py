from enum import Enum


class CheckAction(Enum):
  """What to do if a check fails"""
  FAIL = 'fail'
  QUARANTINE = 'quarantine'

class DirectoryType(Enum):
  """Ingestion type"""
  SHALLOW = 'shallow'
  DATED = 'dated'

class ExportFormat(Enum):
  """Format of export files"""
  CSV = 'csv'
  JSON = 'json'

class PipeType(Enum):
  """Type of Polta Pipe logic"""
  EXPORTER = 'exporter'
  INGESTER = 'ingester'
  TRANSFORMER = 'transformer'

class RawFileType(Enum):
  """Format of raw files"""
  CSV = 'csv'
  EXCEL = 'xlsx'
  JSON = 'json'

class TableQuality(Enum):
  """The quality of the Delta Table"""
  RAW = 'raw'
  CONFORMED = 'conformed'
  CANONICAL = 'canonical'
  STANDARD = 'standard'

class WriteLogic(Enum):
  """The method of saving data to a Delta Table"""
  APPEND = 'append'
  OVERWRITE = 'overwrite'
  UPSERT = 'upsert'
