from sempy.fabric import evaluate_dax as _evaluate_dax
from sempy_labs.tom import connect_semantic_model as _connect_tom
from .base import BaseSource
from typing import Any


class _SemanticModelConnection:
    """Context-manager exposing `.query(dax) -> DataFrame`."""

    def __init__(self, dataset: str, workspace: str | None) -> None:
        self._dataset = dataset
        self._workspace = workspace

    # context-manager protocol 
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # nothing to close – evaluate_dax is stateless
        return False

    # public API 
    def query(self, dax: str, *_, **__) -> Any:
        # Fabric returns a FabricDataFrame (sub-class of pd.DataFrame)
        df = _evaluate_dax(
             dataset=self._dataset,
             dax_string=dax,
             workspace=self._workspace,
         )
        # strip the XMLA brackets so templates can use {Sales}, not {[Sales]}
        df.columns = [
            c[1:-1] if isinstance(c, str) and c.startswith("[") and c.endswith("]") else c
            for c in df.columns
        ]
        return df


class SemanticModelSource(BaseSource):
    """Fabric semantic-model datasource.

    • connect()       run DAX queries (read-only)  
    • connect_tom()  obtain a TOM wrapper (read-only by default, set
                    ``readonly=False`` for write mode)
    """

    # DAX / query context
    def connect(self) -> _SemanticModelConnection:
        return _SemanticModelConnection(
            dataset=self.artifact_id_or_name,
            workspace=self.workspace_id_or_name,
        )

    # TOM context
    def connect_tom(self, *, readonly: bool = True) -> Any:
        """
        Return a TOM connection.

        Example
        -------
        >>> with src.connect_tom(readonly=False) as tom:
        ...     tom.model.Tables.add(...)
        """
        return _connect_tom(
            dataset=self.artifact_id_or_name,
            workspace=self.workspace_id_or_name,
            readonly=readonly,
        )
