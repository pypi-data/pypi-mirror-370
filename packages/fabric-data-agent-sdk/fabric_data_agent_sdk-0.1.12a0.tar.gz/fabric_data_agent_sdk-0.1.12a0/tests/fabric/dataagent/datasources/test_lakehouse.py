import pytest
from src.fabric.dataagent.datasources.lakehouse import LakehouseSource

class DummyConnect:
    def __init__(self, lakehouse, workspace):
        self.lakehouse = lakehouse
        self.workspace = workspace
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): pass
    def query(self, q): return f"query: {q}, lakehouse: {self.lakehouse}, workspace: {self.workspace}"

def test_lakehouse_connect(monkeypatch):
    # Patch labs.ConnectLakehouse to our dummy
    import src.fabric.dataagent.datasources.lakehouse as lakehouse_mod
    monkeypatch.setattr(lakehouse_mod, "labs", type("labs", (), {"ConnectLakehouse": DummyConnect}))
    src = lakehouse_mod.LakehouseSource("lh_id", workspace_id_or_name="ws_id")
    with src.connect() as conn:
        assert isinstance(conn, DummyConnect)
        assert conn.lakehouse == "lh_id"
        assert conn.workspace == "ws_id"
        assert conn.query("SELECT 1") == "query: SELECT 1, lakehouse: lh_id, workspace: ws_id"
