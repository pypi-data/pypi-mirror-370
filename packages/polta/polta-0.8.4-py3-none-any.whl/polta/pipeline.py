from dataclasses import dataclass, field
from polars import DataFrame

from polta.pipe import Pipe


@dataclass
class Pipeline:
  """Simple dataclass for executing chains of pipes for an end product

  The pipe execution order:
    1. Raw
    2. Conformed
    3. Standard
    4. Canonical
    5. Export
  
  Optional Args:
    raw_pipes (list[Pipe]): the raw pipes in the pipeline
    conformed_pipes (list[Pipe]): the conformed pipes in the pipeline
    standard_pipes (list[Pipe]): the standard pipes in the pipeline
    canonical_pipes (list[Pipe]): the canonical pipes in the pipeline
    export_pipes (list[Pipe]): the export pipes in the pipeline
  """
  raw_pipes: list[Pipe] = field(default_factory=lambda: [])
  conformed_pipes: list[Pipe] = field(default_factory=lambda: [])
  standard_pipes: list[Pipe] = field(default_factory=lambda: [])
  canonical_pipes: list[Pipe] = field(default_factory=lambda: [])
  export_pipes: list[Pipe] = field(default_factory=lambda: [])

  def execute(self, in_memory: bool = False, skip_exports: bool = False) -> None:
    """Executes all available pipes in order of layer
    
    Args:
      in_memory (bool): indicates whether to run without saving (default False)
      skip_exports (bool): indicates whether to skip the export layer (default False)
    """
    if in_memory:
      self._in_memory_execute(skip_exports)
    else:
      self._standard_execute(skip_exports)

  def _standard_execute(self, skip_exports: bool = False) -> None:
    """Executes all available pipes in order of layer and saves results
    
    Args:
      skip_exports (bool): indicates whether to skip the export layer (default False)
    """
    for pipe in self.raw_pipes:
      pipe.execute()
    for pipe in self.conformed_pipes:
      pipe.execute()
    for pipe in self.standard_pipes:
      pipe.execute()
    for pipe in self.canonical_pipes:
      pipe.execute()
    if not skip_exports:
      for pipe in self.export_pipes:
        pipe.execute()

  def _in_memory_execute(self, skip_exports: bool = False) -> None:
    """Executes all available pipes in order of layer without saving to the metastore

    Args:
      skip_exports (bool): indicates whether to skip the export layer (default False)    
    """
    dfs: dict[str, DataFrame] = {}

    for pipe in self.raw_pipes:
      passed, _, _ = pipe.execute(dfs, in_memory=True)
      dfs[pipe.table.id] = passed
    for pipe in self.conformed_pipes:
      passed, _, _ = pipe.execute(dfs, in_memory=True)
      dfs[pipe.table.id] = passed
    for pipe in self.standard_pipes:
      passed, _, _ = pipe.execute(dfs, in_memory=True)
      dfs[pipe.table.id] = pipe
    for pipe in self.canonical_pipes:
      passed, _, _ = pipe.execute(dfs, in_memory=True)
      dfs[pipe.table.id] = passed
    if not skip_exports:
      for pipe in self.export_pipes:
        passed, _, _ = pipe.execute(dfs, in_memory=True)
        dfs[pipe.table.id] = passed
