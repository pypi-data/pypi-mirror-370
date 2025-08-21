import polars as pl

from polta.check import Check


check_value_in: Check = Check(
  name='value_in',
  description='Checks whether a column value is in a list',
  function=lambda df, column, values: (df
    .with_columns([
      pl.when(pl.col(column).is_in(values))
        .then(pl.lit(0))
        .otherwise(pl.lit(1))
        .alias(f'__{column}__value_in__')
    ])
  )
)
