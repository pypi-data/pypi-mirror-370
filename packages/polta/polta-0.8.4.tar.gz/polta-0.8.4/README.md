# Polta
_Data engineering tool combining Polars transformations with Delta tables/lakes._

![PyTest](https://github.com/JoshTG/polta/actions/workflows/run-pytest.yml/badge.svg) [![PyPI version](https://img.shields.io/pypi/v/polta.svg)](https://pypi.org/project/polta/)

# Core Concepts

The `polta` package allows you to declare simple building blocks that interact with each other to form small-to-medium-scale data pipelines.

In the Python ecosystem broadly, the existing `polars` and `delta` packages make a great team, but they can be tricky to interact with at times. The `polta` package aims to provide a unified wrapper for them, along with some custom homebrewed tools and objects, so that moving and managing data across layers of abstraction is intuitive and resilient.

## At a Glance

* A `Metastore` manages data in a uniform and consistent manner for `Pipelines`.
* A `Pipeline` connects `Pipes` together into a uniform execution plan.
* Each `Pipe` takes data from one location, transforms it, and saves it into another location. It does so in one of three ways:
  * By ingesting source data via an `Ingester`.
  * By transforming data across layers via a `Transformer`.
  * By exporting the data in a desired format via an `Exporter`.
* The data are managed in `Tables`, which use `deltalake` and `polars` under the hood.
* Each `Table` contains a `TableSchema` which wraps the polars and deltalake schemas depending on user need.

## Terminology

Throughout this README and in the repository's `sample` pipelines, various objects are aliased in a consistent manner when imported. Below is a table of such aliases for convenience.

| Object        | Alias                               | Example            |
| ------------- | ----------------------------------  | ------------------ |
| `Table`       | tab_<quality-prefix\>_<table-name\> | tab_raw_activity   |
| `Exporter`    | exp_<quality-prefix\>_<table-name\> | exp_can_user       | 
| `Ingester`    | ing_<quality-prefix\>_<table-name\> | ing_raw_activity   |
| `Transformer` | tra_<quality-prefix\>_<table-name\> | tra_con_user       |
| `Pipe`        | pip_<quality-prefix\>_<table-name\> | pip_std_category   |
| `Pipeline`    | ppl_<domain\>_<table-name\>         | ppl_standard_user  |

To illustrate, a `Table` is initially declared like this:

```python
# raw_table.py
from polta.enums import TableQuality
from polta.table import Table


table: Table = Table(
  domain='standard',
  quality=TableQuality.RAW,
  name='test'
)
```

And another like this:

```python
# conformed_table.py
from polta.enums import TableQuality
from polta.table import Table


table: Table = Table(
  domain='standard',
  quality=TableQuality.CONFORMED,
  name='test'
)
```

Then, whenever they are imported from another file, they are aliased like this:
```python
# other-file.py
from .raw_table import table as tab_raw_test
from .conformed_table import table as tab_con_test

...
```

The naming conventions are designed this way for the following reasons:
1. It keeps initial declarations simple.
2. It allows importing multiple objects (e.g., `Table` and `Pipe` objects) while avoiding variable collisions.
3. It adds consistent and descriptive identifiers to the objects throughout the codebase.

> Feel free to name and organize your objects however you wish in your own repository. However, make sure you understand how this repository works to make the most sense out of the documentation and samples.

## Metastore

Every `polta` integration should have a dedicated metastore for preserving data and logs. This is automatically created and managed by `polta` before executing any reads or writes.

There are two main aspects of a `Metastore`:

1. *Tables*: Contains every table across all layers.
2. *Volumes*: Contains file storage systems needed for transformations.

This structure is inspired by `deltalake` and follows similar metastore paradigms. It loosely follows the modern [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture) language for organizing the data layers, with these naming conventions for each layer:

1. *Raw*: Source data as a payload string.
2. *Conformed*: Source data already conformed to a schema.
3. *Standard*: Non-source, static data.
4. *Canonical*: Business-level data, built from *Raw*, *Conformed*, and/or *Standard* data.
5. *Export*: Cleaned, formatted export data.

The basic way to think about these layers is to think of three different data paths:

1. *raw* -> *conformed* -> *canonical*
2. *standard*
3. *raw/conformed/standard/canonical* -> *export* 

If you have complicated source data that will need to be unpacked, it should be brought into the *raw* or *canonical* layer and then cleaned into *canonical*.

If you have a simple table, like a crosswalk, it should be brought into the *standard* layer.

If you want to save data in different formats for external use, it should be exported via the *export* layer.

## Table

The `Table` is the primary way to read and write data.

It stores data using `deltalake`, and it transforms data using `polars`.

Because `Table` integrates two modules together, it has many fields and methods for communicating seamlessly to and fro. Most importantly, every `Table` has readily available a `TableSchema` object, contained in the `schema` field, which contains the `polars` and `deltalake` versions of the schema that you can use how you wish.

Each raw `Table` has a dedicated ingestion zone located in the `Metastore` to store sources files ready to be loaded into the raw layer.

## Pipe

The `Pipe` is the primary way to transform data from one location to another in a new format.

Currently, there are three kinds of supported pipes, each described below.

### Ingester

The `Ingester` is the primary way to load source files into the raw layer.

It currently supports ingesting these formats:

1. JSON
2. Excel
3. CSV
4. String payload

An instance can get passed into a `Pipe` to ingest data into a `Table`.

### Transformer

The `Transformer` reads one or more `Table` objects from a layer, applies transformation logic, and writes the output into a target `Table`.

This object accepts as the transformation logic either a custom function or a SQL query.

The custom function may look like this:

```python
from polars import DataFrame


def transform(dfs: dict[str, DataFrame]) -> DataFrame:
  """Applies a simple join between name and activity

  Args:
    dfs (dict[str, DataFrame]): the input DataFrames
  
  Returns:
    df (DataFrame): the resulting DataFrame
  """
  return dfs['name'].join(dfs['activity'], 'id', 'inner')
```

Alternatively, a SQL query might look like this:

```python
transform: str = '''
  SELECT
      n.*
    , a.active_ind
  FROM
    name n
  INNER JOIN activity a
  ON n.id = a.id
'''
```

### Exporter

The `Exporter` reads a `Table` and exports it in a desired format usually into an export directory within the `Metastore`.

It currently supports exporting these formats:
1. JSON
2. CSV

## Pipeline

The `Pipeline` is the primary way to link `Pipes` together to create a unified data pipeline.

It takes in a list of raw, conformed, canonical, and export `Pipes` and executes them sequentially.

There are two kinds of pipelines you can build:

1. `Standard`: each step in the pipeline saves to `Table` objects in the metastore. During execution, pipes typically retrieve the current state of each of those `Table` objects and saves the output in the target `Table`. This allows a full end-to-end-pipeline that preserves all pipe outputs into the metastore for future usage.
2. `In Memory`: each step in the pipeline preserves the `DataFrames` across layers and loads them into each subsequent pipe. This allows a full end-to-end pipeline that can export the results without reling on preserving the intermediate data in the metastore. 

If you need to store each run over time, you should use a `Standard` pipeline. However, if you simply want to load a dataset, transform it, and export it into a format, just wanting to preserve that export, then you should use an `In Memory` pipeline. The `sample` directory contains pipelines for both kinds.

# Installation

## Installing to a Project
This project exists in `PyPI` and can be installed this way:

```sh
pip install polta
```

## Initializing the Repository

To use the code from the repository itself, either for testing or contributing, follow these steps:

1. Clone the repository to your local machine.
2. Create a virtual environment, preferably using `venv`, that runs `Python 3.13`. 
3. Ensure you have `poetry` installed (installation instructions [here](https://python-poetry.org/docs/#installation)).
4. Make `poetry` use the virtual environment using `poetry env use .venv/path/to/python`.
5. Download dependencies by executing `poetry install`.
6. Building a wheel file by executing `poetry build`.

# Testing

This project uses `pytest` for its tests, all of which exist in the `tests` directory. Below are recommended testing options.

## Run Tests via VS Code

There is a `Testing` tab in the left-most menu by default that allows you to run `pytest` tests in bulk or individually.

## Run Tests via Poetry
To execute tests using `poetry`, run this command in your terminal at the top-level directory:

```sh
poetry run pytest tests/ -vv -s
```

##  Check Test Coverage

To check the overall test coverage, use the `pytest-cov` package by running this command in your terminal at the top-level directory:

```sh
poetry run pytest --cov=polta tests/ -vv -s
```

If you do not have 100% coverage, you can see which lines of code are not covered by running this command:

```sh
poetry run coverage report -m
```

## Linting

This repository uses `ruff` as its linter.

To lint the code, run the following command in your terminal at the top-level directory:

```sh
poetry run ruff check
```

# Usage

Below are sample code snippets to show basic usage. For full sample pipelines, consult the `sample` directory in the repository. These tables, pipes, and pipeline get used in the unit test which is located in the `tests/test_pipeline.py` pytest file.

## Sample Metastore

The creation of a new metastore is simple. Below is a sample metastore that can be passed into the initialization of any `Table` to ensure the table writes to the metastore.

```python
from polta.metastore import Metastore


metastore: Metastore = Metastore('path/to/desired/store')
```

## Sample Ingester Pipe

This sample code illustrates a simple raw ingestion pipe.

A pipe file typically contains a `Table` and a `Pipe`, and a raw table might have an additional `Ingester`.

```python
from deltalake import Field, Schema

from polta.enums import (
  DirectoryType,
  RawFileType,
  TableQuality
)
from polta.ingester import Ingester
from polta.pipe import Pipe
from polta.table import Table

from .metastore import metastore


table: Table = Table(
  domain='sample',
  quality=TableQuality.RAW,
  name='table',
  raw_schema=Schema([
    Field('payload', 'string')
  ]),
  metastore=metastore
)

ingester: Ingester = Ingester(
  table=table,
  directory_type=DirectoryType.SHALLOW,
  raw_file_type=RawFileType.JSON
)

pipe: Pipe = Pipe(ingester)
```

By making `table.raw_schema` a simple payload, that signals to the ingester that the transformation is a simple file read.

This code is all that is needed to execute a load of all data from the ingestion zone to a raw table. To do so, execute `pipe.execute()`.

If you want to read the data, execute `table.get()`.

## Sample Transformer Pipe

For instances where transformation logic is required, you should use the `Transformer` class to transform data from one layer to another.

```python
from deltalake import Field, Schema
from polars import col, DataFrame
from polars.datatypes import DataType, List, Struct

from polta.enums import TableQuality, WriteLogic
from polta.maps import Maps
from polta.pipe import Pipe
from polta.table import Table
from polta.transformer import Transformer
from polta.udfs import string_to_struct
from sample.standard.table import \
  table as tab_raw_table

from .metastore import metastore


table: Table = Table(
  domain='test',
  quality=TableQuality.CONFORMED,
  name='table',
  raw_schema=Schema([
    Field('id', 'string'),
    Field('active_ind', 'boolean')
  ]),
  metastore=metastore
)

def get_dfs() -> dict[str, DataFrame]:
  """Basic load logic:
    1. Get raw table data as a DataFrame
    2. Anti join against conformed layer to get net-new records
  
  Returns:
    dfs (dict[str, DataFrame]): The resulting data as 'table'
  """
  conformed_ids: DataFrame = table.get(select=['_raw_id'], unique=True)
  df: DataFrame = (tab_raw_table
    .get()
    .join(conformed_ids, '_raw_id', 'anti')
  )
  return {'table': df}

def transform(dfs: dict[str, DataFrame]) -> DataFrame:
  """Basic transformation logic:
    1. Retrieve the raw table DataFrame
    2. Convert 'payload' into a struct
    3. Explode the struct
    4. Convert the struct key-value pairs into column-cell values

  Returns:
    df (DataFrame): the resulting DataFrame
  """
  df: DataFrame = dfs['table']
  raw_polars_schema: dict[str, DataType] = Maps \
      .deltalake_schema_to_polars_schema(table.raw_schema)

  return (df
    .with_columns([
      col('payload')
        .map_elements(string_to_struct, return_dtype=List(Struct(raw_polars_schema)))
    ])
    .explode('payload')
    .with_columns([
      col('payload').struct.field(f).alias(f)
      for f in [n.name for n in table.raw_schema.fields]
    ])
    .drop('payload')
  )

transformer: Transformer = Transformer(
  table=table,
  load_logic=get_dfs,
  transform_logic=transform,
  write_logic=WriteLogic.APPEND
)

pipe: Pipe = Pipe(transformer)
```

This `Transformer` instance receives the raw data from the previous example, explodes the data, and extracts the proper fields into a proper conformed DataFrame.

This one file contains every object in a modular format, which means you can import in another file any part of the pipe as needed.

> This modular design also allows you to create integration and unit tests around your `load_logic` and `transform_logic` easily, as illustrated in the `tests/` directory.

You can execute the `Pipe` by running `pipe.execute()` wherever you want, and any new raw files will get transformed and loaded into the conformed layer.

## Sample Pipeline

To connect the above pipes together, you can create a `Pipeline`, as sampled below.

```python
from polta.pipeline import Pipeline

from sample.standard.raw.table import \
  pipe as pip_raw_sample
from sample.standard.conformed.table import \
  pipe as pip_con_sample


pipeline: Pipeline = Pipeline(
  raw_pipes=[pip_raw_sample],
  conformed_pipes=[pip_con_sample]
)
```

You can then execute your pipeline by running `pipeline.execute()`.

# License

This project exists under the `MIT License`.

## Acknowledgements

The `polta` project uses third-party dependencies that use the following permissive open-source licenses:

1. `Apache Software License (Apache-2.0)`
2. `BSD-3-Clause License`
3. `MIT License`

Below are the top-level packages with their licenses.

| Package | Version | Purpose | License |
| ------- | ------- | ------- | ------- |
| [deltalake](https://github.com/delta-io/delta-rs) | >=0.25.5, <1.0.0 | Stores and reads data | Apache Software License (Apache-2.0) |
| [ipykernel](https://github.com/ipython/ipykernel) | >=6.29.5, <6.30.0 | Creates Jupyter notebooks for ad hoc analytics | BSD-3-Clause License |
| [openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) | >=3.1.5, <3.2.0 | The underlying engine for pl.read_excel() | MIT License |
| [pip](https://github.com/pypa/pip) | >=25.1.1, <25.2.0 | Installs Python packages for the virtual environment | MIT License |
| [polars](https://github.com/pola-rs/polars) | >=1.30.0, <1.31.0 | Executes DataFrame transformation | MIT License |
| [pytest](https://github.com/pytest-dev/pytest) | >=8.3.5, <8.4.0 | Runs test cases for unit testing | MIT License |
| [pytest-cov](https://github.com/pytest-dev/pytest-cov) | >=6.2.1, <6.3.0 | Applies test coverage to pytest runs | MIT License |
| [ruff](https://github.com/astral-sh/ruff) | >=0.12.3, <0.13.0 | Executes linting checks in the repository | MIT License |
| [ruff-action](https://github.com/astral-sh/ruff-action) | latest | Executes a ruff check in the GitHub workflow | Apache Software License (Apache-2.0) |
| [tzdata](https://github.com/python/tzdata) | >=2025.2, <2026.1 | Contains timezone information for Datetime objects | Apache Software License (Apache-2.0) |

# Contributing

Because this project is open-source, contributions are most welcome by following these steps:

1. Submit the contribution request to the [issues page](https://github.com/JoshTG/polta/issues).
2. Await signoff/feedback from a repository administrator.
3. Clone the repository into your local machine.
4. Create a descriptive feature branch.
5. Make the desired changes.
6. Fully test the desired changes using `test` directory. Ensure you have 100% `pytest` test coverage and the code passes a `ruff check`.
7. Uptick the `poetry` project version appropriately using standard semantic versioning.
8. Create a merge request into the `main` branch of the official `polta` project and assign it initially to @JoshTG.
9. Once the merge request is approved and merged, an administrator will schedule a release cycle and deploy the changes using a new release tag.

# Contact

You may contact the main contributor, [JoshTG](https://github.com/JoshTG), by sending an email to this address: jgillilanddata@gmail.com.
