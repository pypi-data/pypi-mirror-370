import sempy_labs as labs
from .base import BaseSource


class LakehouseSource(BaseSource):
    """Lakehouse implementation of BaseSource."""

    def connect(self):
        # inherits artifact_id_or_name from BaseSource
        return labs.ConnectLakehouse(
            lakehouse=self.artifact_id_or_name, workspace=self.workspace_id_or_name
        )