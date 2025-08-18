from .lakehouse import LakehouseSource
from .warehouse import WarehouseSource
from .kustodb import KustoDBSource
from .semantic_model import SemanticModelSource 
from .base import BaseSource

_TYPE_MAP = {
    "lakehouse_tables": LakehouseSource,
    "data_warehouse": WarehouseSource,  
    "semantic_model":  SemanticModelSource,
    "kusto": KustoDBSource,
}


def make_source(cfg: dict) -> BaseSource:
    """
    Build a concrete Source object from a Fabric datasource configuration.
    `cfg` must have at least keys: 'type', 'display_name'.
    """
    if "type" not in cfg or "display_name" not in cfg:
        raise ValueError("cfg must contain 'type' and 'display_name'")

    try:
        cls = _TYPE_MAP[cfg["type"]]
    except KeyError as exc:
        raise ValueError(f"Unsupported datasource type '{cfg['type']}'") from exc

    # Kusto needs the full JSON (contains "endpoint" and "database_name")
    if cfg["type"] == "kusto":
        return cls(cfg)                               # pass everything

    # lakehouse / warehouse keep the lean constructor for now
    return cls(
        artifact_id_or_name = cfg.get("id") or cfg["display_name"],
        workspace_id_or_name=cfg.get("workspace_id") or cfg.get("workspace_name"),
    )