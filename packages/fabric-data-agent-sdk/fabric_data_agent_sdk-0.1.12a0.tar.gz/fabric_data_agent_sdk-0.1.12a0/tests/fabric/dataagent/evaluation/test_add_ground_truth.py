"""
Unit-tests for ground_truth.update_ground_truth

They avoid heavy dependencies (deltalake, sempy_labs, Spark, HTTP) by
registering minimal stub modules in ``sys.modules`` **before** the code
under test is imported.
"""

from __future__ import annotations

import sys
import types
import pandas as pd
import pytest
import string
import importlib

def _ensure(name: str) -> types.ModuleType:
    """
    Return the real module if importable, otherwise create a dummy one.
    """
    if name in sys.modules:
        return sys.modules[name]
    try:
        return importlib.import_module(name)          # real package present
    except ModuleNotFoundError:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

# ── only the packages required by kustodb.py and semantic_model.py ─────
for path in (
    "sempy",
    "sempy_labs.tom",
    "azure.kusto",
    "azure.kusto.data",
    "azure.kusto.data.helpers",
    "azure.kusto.data.exceptions",
    "synapse.ml.fabric.token_utils",
    "synapse.ml.fabric.service_discovery",
):
    parts = path.split(".")
    for i in range(1, len(parts) + 1):
        _ensure(".".join(parts[:i]))

# minimal attributes for kustodb
az_data = _ensure("azure.kusto.data")
exc_mod = sys.modules["azure.kusto.data.exceptions"]
exc_mod.KustoServiceError = type("KustoServiceError", (), {})
exc_mod.KustoClientError  = type("KustoClientError",  (), {})
az_data.ClientRequestProperties = type(
    "ClientRequestProperties", (), {"set_option": lambda *_, **__: None}
)
az_data.KustoConnectionStringBuilder = type(
    "KustoConnectionStringBuilder",
    (),
    {"with_token_provider": staticmethod(lambda *_, **__: None)},
)
az_data.KustoClient = type(
    "KustoClient",
    (),
    {"execute": lambda *_, **__: types.SimpleNamespace(primary_results=[pd.DataFrame()])},
)
sys.modules["azure.kusto.data.helpers"].dataframe_from_result_table = (
    lambda *_: pd.DataFrame()
)

_ensure("synapse.ml.fabric.token_utils").TokenUtils = type(
    "TokenUtils",
    (),
    {
        "get_access_token": lambda *_, **__: "token",
        "get_aad_token": lambda *_, **__: "aad-token",
    },
)

_ensure("synapse.ml.fabric.service_discovery").get_fabric_env_config = (
    lambda *_a, **_kw: {}
)       


# 1.  Stub external libraries so evaluator_api imports cleanly
def _register_stub(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


# create parent & sub-modules (deltalake, deltalake.writer, sempy_labs)
for missing in ("deltalake", "deltalake.writer", "sempy_labs"):
    parts = missing.split(".")
    for i in range(1, len(parts) + 1):
        _register_stub(".".join(parts[:i]))

# give the required attribute so `from deltalake.writer import write_deltalake` works
sys.modules["deltalake.writer"].write_deltalake = lambda *_, **__: None

sempy = _ensure("sempy")
sempy.evaluate_dax = lambda **_: pd.DataFrame({"v": [1]})  # always 1-row df

def _fake_connect_semantic_model(**_):
    class _Iterator:
        def __enter__(self): return self
        def __exit__(self, *a): pass
    return _Iterator()

_ensure("sempy_labs.tom").connect_semantic_model = _fake_connect_semantic_model


# 2.  Import module under test
from fabric.dataagent.evaluation import ground_truth


# 3.  Helpers
def _dummy_sql(df: pd.DataFrame):
    """Mimic labs.ConnectX context manager with a .query() method returning *df*."""

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def query(self, _):
            return df

    return _Ctx()


# Patch the ground_truth module to use our dummy SQL connection
def _patch(monkeypatch, df: pd.DataFrame):
    # force a lakehouse source and dummy connection
    monkeypatch.setattr(
        ground_truth,
        "_get_source",
        lambda *_: types.SimpleNamespace(connect=lambda: _dummy_sql(df)),
    )


# 4.  Tests
def test_single_scalar_named_placeholder(monkeypatch):
    """Single column, named placeholder is rendered correctly."""
    _patch(monkeypatch, pd.DataFrame({"total": [42]}))

    out = ground_truth.add_ground_truth(
        question="Total sales?",
        answer_template="Total sales: {total}",
        datasource_id_or_name="Any",
        query="dummy",
        data_agent=None,
    )
    assert out["expected_answer"].iloc[0] == "Total sales: 42"


def test_single_row_multi_column(monkeypatch):
    """Several columns with matching named placeholders."""
    _patch(monkeypatch, pd.DataFrame({"country": ["US"], "sales": [123]}))

    out = ground_truth.add_ground_truth(
        "By country",
        "{country} sold {sales}",
        "Any",
        "dummy",
        data_agent=None,
    )
    assert out["expected_answer"].iloc[0] == "US sold 123"


def test_error_positional_placeholder(monkeypatch):
    """Positional '{}' is now forbidden."""
    _patch(monkeypatch, pd.DataFrame({"x": [1]}))

    with pytest.raises(ValueError, match="Positional"):
        ground_truth.add_ground_truth(
            "Bad",
            "Answer is {}",
            "Any",
            "dummy",
            data_agent=None,
        )


def test_error_multiple_rows(monkeypatch):
    """Multiple query rows should raise."""
    _patch(monkeypatch, pd.DataFrame({"id": [1, 2]}))

    with pytest.raises(ValueError, match="multiple rows"):
        ground_truth.add_ground_truth(
            "Bad",
            "{id}",
            "Any",
            "dummy",
            data_agent=None,
        )

# 5.  _extract_placeholders() edge-cases coverage
@pytest.mark.parametrize(
    "template, expected",
    [
        ("Value is {amount:.2f}", {"amount"}),          # format-spec
        ("Balance {{USD}} {balance}", {"balance"}),     # escaped braces
        ("Repeated {a}-{a}-{b}", {"a", "b"}),           # duplicates collapse
        ("No placeholders here", set()),                # no placeholders
    ],
)
def test_extract_placeholders_edge_cases(template, expected):
    assert ground_truth._extract_placeholders(template) == expected

def test_add_ground_truth_batch(monkeypatch):
    """add_ground_truth_batch returns one output row per input row."""
    df_single = pd.DataFrame({"val": [1]})            # 1-row result for every query
    _patch(monkeypatch, df_single)

    batch_in = pd.DataFrame(
        [
            dict(question="q1", answer_template="v={val}", query="dummy"),
            dict(question="q2", answer_template="v={val}", query="dummy"),
        ]
    )

    out = ground_truth.add_ground_truth_batch(batch_in, "Any", data_agent=None)

    assert len(out) == 2
    assert list(out["question"]) == ["q1", "q2"]
    assert list(out["expected_answer"]) == ["v=1", "v=1"]

@pytest.mark.parametrize("verbose", [True, False])
def test_add_ground_truth_verbose(monkeypatch, verbose):
    # Covers verbose branch and _display_styled_html
    import types
    import pandas as pd
    from unittest.mock import patch
    # Patch _get_source to return a dummy connection
    class DummyCtx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def query(self, _): return pd.DataFrame({"x": [1]})
    dummy_source = types.SimpleNamespace(connect=lambda: DummyCtx())
    monkeypatch.setattr(
        "fabric.dataagent.evaluation.ground_truth._get_source",
        lambda *_a, **_kw: dummy_source,
    )
    # Patch _display_styled_html in the ground_truth namespace
    from fabric.dataagent.evaluation import ground_truth as gt_mod
    with patch.object(gt_mod, "_display_styled_html") as mock_disp:
        out = gt_mod.add_ground_truth(
            question="Q?",
            answer_template="{x}",
            datasource_id_or_name="ds",
            query="q",
            data_agent=None,
            verbose=verbose
        )
        if verbose:
            assert mock_disp.called, "Expected '_display_styled_html' to have been called."
        else:
            assert not mock_disp.called
        assert out["expected_answer"].iloc[0] == "1"

@pytest.mark.parametrize("verbose", [True, False])
def test_add_ground_truth_batch_verbose(monkeypatch, verbose):
    import types
    import pandas as pd
    from unittest.mock import patch
    # Patch _get_source to return a dummy connection
    class DummyCtx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def query(self, _): return pd.DataFrame({"x": [1]})
    dummy_source = types.SimpleNamespace(connect=lambda: DummyCtx())
    monkeypatch.setattr(
        "fabric.dataagent.evaluation.ground_truth._get_source",
        lambda *_a, **_kw: dummy_source,
    )
    from fabric.dataagent.evaluation import ground_truth as gt_mod
    with patch.object(gt_mod, "_display_styled_html") as mock_disp:
        batch_in = pd.DataFrame([
            dict(question="q1", answer_template="{x}", query="q"),
            dict(question="q2", answer_template="{x}", query="q"),
        ])
        out = gt_mod.add_ground_truth_batch(
            batch_in, "ds", data_agent=None, verbose=verbose
        )
        if verbose:
            assert mock_disp.called, "Expected '_display_styled_html' to have been called."
        else:
            assert not mock_disp.called
        assert len(out) == 2
        assert set(out["expected_answer"]) == {"1"}


def test_add_ground_truth_exec_ctx(monkeypatch):
    # Covers exec_ctx branch
    import types
    import pandas as pd
    class DummyExec:
        def query(self, _):
            return pd.DataFrame({"y": [5]})
    dummy_source = types.SimpleNamespace(connect=lambda: None)
    monkeypatch.setattr(
        "fabric.dataagent.evaluation.ground_truth._get_source",
        lambda *_a, **_kw: dummy_source,
    )
    out = __import__("fabric.dataagent.evaluation.ground_truth", fromlist=["add_ground_truth"]).add_ground_truth(
        question="Q?",
        answer_template="{y}",
        datasource_id_or_name="ds",
        query="q",
        data_agent=None,
        exec_ctx=DummyExec(),
        verbose=False
    )
    assert out["expected_answer"].iloc[0] == "5"


def test_add_ground_truth_missing(monkeypatch):
    # Covers missing column error
    import types
    import pandas as pd
    class DummyCtx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def query(self, _): return pd.DataFrame({"z": [1]})
    dummy_source = types.SimpleNamespace(connect=lambda: DummyCtx())
    monkeypatch.setattr(
        "fabric.dataagent.evaluation.ground_truth._get_source",
        lambda *_a, **_kw: dummy_source,
    )
    with pytest.raises(ValueError, match="Missing columns"):
        __import__("fabric.dataagent.evaluation.ground_truth", fromlist=["add_ground_truth"]).add_ground_truth(
            question="Q?",
            answer_template="{notfound}",
            datasource_id_or_name="ds",
            query="q",
            data_agent=None,
            verbose=False
        )


def test_add_ground_truth_empty(monkeypatch):
    # Should raise ValueError if query returns no rows
    import types
    import pandas as pd
    class DummyCtx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def query(self, _): return pd.DataFrame({"x": []})
    dummy_source = types.SimpleNamespace(connect=lambda: DummyCtx())
    monkeypatch.setattr(
        "fabric.dataagent.evaluation.ground_truth._get_source",
        lambda *_a, **_kw: dummy_source,
    )
    from fabric.dataagent.evaluation import ground_truth as gt_mod
    with pytest.raises(ValueError, match="no rows"):
        gt_mod.add_ground_truth(
            question="Q?",
            answer_template="{x}",
            datasource_id_or_name="ds",
            query="q",
            data_agent=None,
            verbose=False
        )


def test_add_ground_truth_template_formatting_error(monkeypatch):
    # Should raise ValueError if template formatting fails
    import types
    import pandas as pd
    class DummyCtx:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def query(self, _): return pd.DataFrame({"x": [1]})
    dummy_source = types.SimpleNamespace(connect=lambda: DummyCtx())
    monkeypatch.setattr(
        "fabric.dataagent.evaluation.ground_truth._get_source",
        lambda *_a, **_kw: dummy_source,
    )
    from fabric.dataagent.evaluation import ground_truth as gt_mod
    # This template will cause a formatting error (invalid format spec)
    with pytest.raises(ValueError, match="Template formatting failed"):
        gt_mod.add_ground_truth(
            question="Q?",
            answer_template="{x:badformat}",
            datasource_id_or_name="ds",
            query="q",
            data_agent=None,
            verbose=False
        )


def test_get_source_not_found(monkeypatch):
    # Should raise ValueError if datasource is not found
    from fabric.dataagent.evaluation import ground_truth as gt_mod
    class DummyAgent:
        def get_datasources(self):
            return []
    # Patch resolve_workspace_name_and_id to avoid UUID parsing
    monkeypatch.setattr(gt_mod, "resolve_workspace_name_and_id", lambda ws: (ws, ws))
    with pytest.raises(ValueError) as excinfo:
        gt_mod._get_source("notfound", DummyAgent())
    assert "Datasource 'notfound'" in str(excinfo.value)


def test_get_source_workspace(monkeypatch):
    # Should call resolve_workspace_name_and_id and make_source
    from fabric.dataagent.evaluation import ground_truth as gt_mod
    called = {}
    def fake_resolve(ws):
        called['ws'] = ws
        return 'wsname', 'wsid'
    def fake_make_source(cfg):
        called['cfg'] = cfg
        return 'source_obj'
    class DummyDS:
        def get_configuration(self):
            return {"id": "id1", "display_name": "ds1"}
    class DummyAgent:
        def get_datasources(self):
            return [DummyDS()]
    monkeypatch.setattr(gt_mod, "resolve_workspace_name_and_id", fake_resolve)
    monkeypatch.setattr(gt_mod, "make_source", fake_make_source)
    result = gt_mod._get_source("id1", DummyAgent(), workspace_id_or_name="wsid")
    assert result == 'source_obj'
    assert called['ws'] == 'wsid'
    assert called['cfg']['workspace_name'] == 'wsname'
