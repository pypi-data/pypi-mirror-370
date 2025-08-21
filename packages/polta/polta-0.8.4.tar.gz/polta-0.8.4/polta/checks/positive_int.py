import polars as pl

from polta.check import Check


check_positive_int: Check = Check(
  name='positive_int',
  description='Checks whether column values are positive integers',
  function=lambda df, column: (df
    .with_columns([
      pl.when(pl.col(column) >= 0)
        .then(pl.lit(1))
        .otherwise(pl.lit(0))
        .alias(f'__{column}__positive_int__')
    ])
  )
)
