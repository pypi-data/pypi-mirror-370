from datetime import date, datetime
from typing import Any


def json(obj: Any) -> str:
  """Makes a dict serializable with the json module
  
  Args:
    obj (Any): the value in the dict to serialize
  
  Returns:
    obj (str): the safely-formatted value
  """
  if isinstance(obj, (date, datetime)):
    return obj.isoformat()
  raise TypeError(f'Error: type {type(obj)} is not serializable')
