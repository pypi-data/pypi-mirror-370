from typing import Any


class DataTypeNotRecognized(Exception):
  """Raise when the data type is not recognized by system"""
  def __init__(self, data_type: str) -> None:
    self.message: str = data_type
    super().__init__(self.message)

class DirectoryTypeNotRecognized(Exception):
  """Raise when the directory type is not recognized by system"""
  def __init__(self, directory_type: Any) -> None:
    self.message: str = directory_type
    super().__init__(self.message)

class DomainDoesNotExist(Exception):
  """Raise when a domain retrieval is attempted but it does not exist"""
  def __init__(self, domain: str) -> None:
    self.message: str = f'Unrecognized domain {domain}'
    super().__init__(self.message)

class EmptyPipe(Exception):
  """Raise when the pipe should load data but did not"""
  def __init__(self) -> None:
    self.message: str = 'Pipe executed in strict mode but did not load data'
    super().__init__(self.message)

class IncompatibleTransformLogic(Exception):
  """Raise when the transform logic is not compatible with system"""
  def __init__(self, transform_logic: Any) -> None:
    self.message: str = f'Incompatible transform logic of type {type(transform_logic)}'
    super().__init__(self.message)

class PoltaDataFormatNotRecognized(Exception):
  """Raise when the Polta data format is not recognized by system"""
  def __init__(self, format: type) -> None:
    self.message: str = f'Unrecognized instance type {format}'
    super().__init__(self.message)

class TableQualityNotRecognized(Exception):
  """Raise when the table quality is not recognized by system"""
  def __init__(self, quality: Any) -> None:
    self.message: str = f'Unrecognized table quality {quality}'
    super().__init__(self.message)

class WriteLogicNotRecognized(Exception):
  """Raise when the write logic is not recognized by system"""
  def __init__(self, write_logic: Any) -> None:
    self.message: str = f'Unrecognized write logic {str(write_logic)}'
    super().__init__(self.message)
