import sempy_labs as labs
from .base import BaseSource


class WarehouseSource(BaseSource):
    """Data-warehouse implementation of BaseSource."""

    def connect(self):
        return labs.ConnectWarehouse(
            warehouse=self.artifact_id_or_name, workspace=self.workspace_id_or_name
        )
