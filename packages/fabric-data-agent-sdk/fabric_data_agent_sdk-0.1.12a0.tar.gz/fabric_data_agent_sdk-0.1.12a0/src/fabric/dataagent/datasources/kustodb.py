import pandas as pd
from typing import Any, Dict, Optional
from azure.kusto.data import (
    ClientRequestProperties,
    KustoClient,
    KustoConnectionStringBuilder,
)
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.data.exceptions import KustoServiceError, KustoClientError
from synapse.ml.fabric.token_utils import TokenUtils

from .base import BaseSource

# One TokenUtils instance per module → avoids recreating it for every token request
_token_utils = TokenUtils()

class _KustoConnection:
    """Lightweight wrapper that executes readonly KQL queries."""

    def __init__(self, cluster: str, database: str):
        kcsb = KustoConnectionStringBuilder.with_token_provider(
            cluster,
            lambda: _token_utils.get_access_token("kusto", _token_utils.get_aad_token()),
        )
        self._client = KustoClient(kcsb)
        self._database = database

    def query(
        self,
        kql: str,
        *,
        max_rows: int = 100,
        request_options: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """Run a readonly KQL query and return a DataFrame.

        request_options – optional extra options passed to ClientRequestProperties.
        """
        props = ClientRequestProperties()
        props.set_option("query_take_max_records", max_rows)
        props.set_option("truncation_max_records", max_rows)
        props.set_option("request_readonly", True)

        # allow callers to add/override options
        if request_options:
            for k, v in request_options.items():
                props.set_option(k, v)

        try:
            response = self._client.execute(self._database, kql, properties=props)
            return dataframe_from_result_table(response.primary_results[0])
        except KustoServiceError as kse:
            raise RuntimeError(f"Kusto service error: {kse}") from kse
        except KustoClientError as kce:
            raise RuntimeError(f"Kusto client error: {kce}") from kce
        except Exception as exc:
            raise RuntimeError(f"Unexpected Kusto query failure: {exc}") from exc
        
    


    # Context-management
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # KustoClient currently has no public close(), but handle future SDKs safely.
        close_fn = getattr(self._client, "close", None)
        if callable(close_fn):
            close_fn()
        return False  


class KustoDBSource(BaseSource):
    """Kusto (Azure Data Explorer) implementation of BaseSource."""
    def __init__(self, cfg: dict[str, Any]) -> None:
        # store full dict locally
        self._cfg = cfg
        # promote the fields that BaseSource expects
        super().__init__(
            artifact_id_or_name=cfg.get("database_name") or cfg.get("display_name"),
            workspace_id_or_name=cfg.get("workspace_id"),
        )

    def connect(self):
        # Prefer explicit endpoint (full URI). Fallback to workspace GUID.
        cfg = self._cfg                       # full JSON
        cluster = cfg.get("endpoint") or cfg["workspace_id"]
        if not str(cluster).startswith(("http://", "https://")):
            cluster = f"https://{cluster}"
        return _KustoConnection(cluster=cluster, database=cfg["database_name"])