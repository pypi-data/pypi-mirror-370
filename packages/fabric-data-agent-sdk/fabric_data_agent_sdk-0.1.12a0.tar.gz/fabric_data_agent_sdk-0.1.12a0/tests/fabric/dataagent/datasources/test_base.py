import pytest
import pandas as pd
from uuid import uuid4
from src.fabric.dataagent.datasources.base import BaseSource

class DummySource(BaseSource):
    def __init__(self, artifact_id_or_name, workspace_id_or_name=None, should_fail=False):
        super().__init__(artifact_id_or_name, workspace_id_or_name)
        self.should_fail = should_fail
    def connect(self):
        if self.should_fail:
            raise RuntimeError("Connection failed!")
        class Conn:
            def __enter__(self): return self
            def __exit__(self, exc_type, exc, tb): pass
            def query(self, q): return pd.DataFrame({"a": [1], "b": [2]})
        return Conn()

def test_basesource_execute_success():
    src = DummySource("id")
    df = src.execute("SELECT * FROM t")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["a", "b"]

def test_basesource_execute_connect_fail():
    src = DummySource("id", should_fail=True)
    with pytest.raises(RuntimeError, match="Connection failed!"):
        src.execute("SELECT 1")

def test_basesource_init_uuid():
    u = uuid4()
    src = DummySource(u, workspace_id_or_name="ws")
    assert src.artifact_id_or_name == u
    assert src.workspace_id_or_name == "ws"

def test_basesource_connect_not_implemented():
    class NoConnect(BaseSource):
        pass
    src = NoConnect("id")
    with pytest.raises(NotImplementedError):
        src.connect()
