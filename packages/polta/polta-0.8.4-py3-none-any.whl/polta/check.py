from dataclasses import dataclass, field
from inspect import signature


@dataclass
class Check:
  """Contains check metadata and a function to generate results
  
  Args:
    name (str): the name of the check
    description (str): the description of the check
    function (callable): the polars transformation code to run the check
  
  Initialized Fields:
    simple_function (bool): indicates whether the arguments are simple (i.e., df, column)
  """
  name: str
  description: str
  function: callable

  simple_function: bool = field(init=False)

  def __post_init__(self) -> None:
    self.simple_function: bool = len(signature(self.function).parameters) == 2

  def build_result_column(self, column: str) -> str:
    """Builds the result column name based on an input column
    
    Args:
      column (str): the column that was checked
    
    Returns:
      result_column (str): the result column name
    """
    return f'__{column}__{self.name}__'
