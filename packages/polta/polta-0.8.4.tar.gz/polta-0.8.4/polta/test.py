from dataclasses import dataclass, field
from polars import DataFrame
from typing import Any

from polta.check import Check
from polta.enums import CheckAction


@dataclass
class Test:
  """Contains fields and actions for a Test
  
  Positional Args:
    check (Check): the base Check for the Test
    column (str): the column name to which the test applies
    check_action (CheckAction): what to do if the check fails
    kwargs (dict[str, Any]): any additional keyword arguments
  
  Initialized Fields:
    result_column (str): the expected result column
  """
  check: Check
  column: str
  check_action: CheckAction
  kwargs: dict[str, Any] = field(default_factory=lambda: {})

  result_column: str = field(init=False)

  def __post_init__(self) -> None:
    self.result_column: str = self.check.build_result_column(self.column)

  def run(self, df: DataFrame) -> DataFrame:
    if self.check.simple_function:
      return self.check.function(df, self.column)
    else:
      return self.check.function(df, self.column, **self.kwargs)
