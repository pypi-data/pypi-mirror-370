from json import load as json_load, loads
from typing import Any


def file_path_to_payload(file_path: str) -> str:
  """UDF to load a file as a string using open().read()
  
  Args:
    file_path (str): the path to the file
  
  Returns:
    payload (str): the resulting payload
  """
  return open(file_path, 'r').read()

def file_path_to_json(file_path: str) -> list[dict[str, Any]]:
  """UDF to load a file as a struct using json.load
  
  Args:
    file_path (str): the path to the file
  
  Returns:
    json (list[dict[str, Any]]): the file as a list of dict objects
  """
  return json_load(open(file_path, 'r'))

def string_to_struct(value: str) -> dict[str, Any]:
  """UDF to convert a string value to a struct value using json.loads
  
  Args:
    value (str): the value to convert
  
  Returns:
    struct (dict[str, Any]): the resulting struct"""
  return loads(value)
