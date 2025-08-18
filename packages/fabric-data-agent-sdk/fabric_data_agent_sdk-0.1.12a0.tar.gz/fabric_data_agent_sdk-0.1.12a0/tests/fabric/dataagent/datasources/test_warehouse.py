import pytest
from src.fabric.dataagent.datasources.warehouse import WarehouseSource

class DummyConnect:
    def __init__(self, warehouse, workspace):
        self.warehouse = warehouse
        self.workspace = workspace
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): pass
    def query(self, q): return f"query: {q}, warehouse: {self.warehouse}, workspace: {self.workspace}"

def test_warehouse_connect(monkeypatch):
    # Patch labs.ConnectWarehouse to our dummy
    import src.fabric.dataagent.datasources.warehouse as warehouse_mod
    monkeypatch.setattr(warehouse_mod, "labs", type("labs", (), {"ConnectWarehouse": DummyConnect}))
    src = warehouse_mod.WarehouseSource("wh_id", workspace_id_or_name="ws_id")
    with src.connect() as conn:
        assert isinstance(conn, DummyConnect)
        assert conn.warehouse == "wh_id"
        assert conn.workspace == "ws_id"
        assert conn.query("SELECT 1") == "query: SELECT 1, warehouse: wh_id, workspace: ws_id"
