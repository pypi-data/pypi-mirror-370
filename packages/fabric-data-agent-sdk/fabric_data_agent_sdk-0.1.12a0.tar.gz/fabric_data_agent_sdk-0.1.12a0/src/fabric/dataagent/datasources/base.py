from uuid import UUID
from typing import Union
import pandas as pd

class BaseSource:
    """
    Common interface for all Fabric datasources.
    Sub-classes must implement `connect()` and return a context manager
    exposing a `.query(sql_or_kql)` method that yields a Pandas DataFrame.
    """

    def __init__(
        self,
        artifact_id_or_name: Union[str, UUID],
        workspace_id_or_name: str | None = None,
    ) -> None:

        self.artifact_id_or_name = artifact_id_or_name
        self.workspace_id_or_name = workspace_id_or_name

    def connect(self):
        """Return a context-manager (e.g. `labs.ConnectLakehouse`)."""
        raise NotImplementedError("Sub-classes must override connect()")

    def execute(self, query: str) -> pd.DataFrame:
        """
        Execute a query using the data source's connection.

        Parameters
        ----------
        query : str
            The query to execute.

        Returns
        -------
        pd.DataFrame
            The result of the query as a Pandas DataFrame.
        """
        with self.connect() as connection:
            return connection.query(query)
