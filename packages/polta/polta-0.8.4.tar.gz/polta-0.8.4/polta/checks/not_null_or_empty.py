import polars as pl

from polta.check import Check


check_not_null_or_empty: Check = Check(
  name='not_null_or_empty',
  description='Checks whether column values are not null or empty',
  function=lambda df, column: (df
    .with_columns([
      pl.when(pl.col(column).is_not_null(), pl.col(column) != '')
        .then(pl.lit(1))
        .otherwise(pl.lit(0))
        .alias(f'__{column}__not_null_or_empty__')
    ])
  )
)
