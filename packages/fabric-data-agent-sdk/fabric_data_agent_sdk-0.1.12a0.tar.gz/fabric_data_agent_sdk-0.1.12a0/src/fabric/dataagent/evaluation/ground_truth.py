"""
Functions for managing ground truth data for evaluations.
"""

import string
import pandas as pd
from typing import Optional, Any
from tqdm import tqdm
from fabric.dataagent.client import FabricDataAgentManagement
from fabric.dataagent.datasources.base import BaseSource
from fabric.dataagent.client._util import resolve_workspace_name_and_id
from fabric.dataagent.datasources import make_source

from fabric.dataagent.evaluation._display import _markdown_formatter, _sql_formatter, _display_styled_html


def add_ground_truth(
    question: str,
    answer_template: str,
    datasource_id_or_name: str,
    query: str,
    data_agent: FabricDataAgentManagement,
    exec_ctx: Optional[Any] = None,
    *,
    source: Optional[BaseSource] = None,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Update ground-truth for one query / answer pair.
    Works with Lakehouse, Warehouse and Kusto datasources.

    The SQL query must return exactly one row.
    The answer template must use **named** placeholders that match the
    column names of that row, e.g.  "Total {sales} in {country}".

    Parameters
    ----------
    question : str
        Question from the input DataFrame.
    answer_template : str
        Template for the expected answer.
    datasource_id_or_name : str
        Name of the data source.
    query : str
        Query to get the expected answer.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    exec_ctx : Any, optional
        Execution context to reuse an open connection. Default is None, which creates a new connection.
    source : BaseSource, optional
        A datasource object to reuse. If not provided, it will be fetched using `datasource_id_or_name` and `data_agent`.
    verbose : bool, optional
        Flag to print verbose output. Default is False.

    Returns
    -------
    pd.DataFrame
        DataFrame with updated ground truth.
    """
    # get or reuse the datasource
    if source is None:
        source = _get_source(datasource_id_or_name, data_agent)


    # check connection and execute query
    if exec_ctx is None:
        with source.connect() as ctx:
            df_res = ctx.query(query)
    else:
        df_res = exec_ctx.query(query)

    # check if the query returned exactly one row
    if df_res.empty:
        raise ValueError("Query returned no rows; cannot fill template")

    if len(df_res) > 1:
        raise ValueError(
            "Query returned multiple rows. " "add_ground_truth expects exactly one row."
        )

    if "{}" in answer_template:
        raise ValueError("Positional '{}' is not supported; use named placeholders")

    placeholders = _extract_placeholders(answer_template)

    missing = placeholders.difference(df_res.columns)
    if missing:
        raise ValueError(f"Missing columns in answer template: {', '.join(missing)}")
    
    # check if the answer template can be formatted with the row
    try:
        rendered = answer_template.format(**df_res.iloc[0].to_dict())
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Template formatting failed: {exc}") from exc


    ground_truth_df = pd.DataFrame(
        {
            "question": [question],
            "expected_answer": [rendered],
            "datasource_id_or_name": [datasource_id_or_name],
            "query": [query],
        }
    )

    if verbose:
        styled_df = ground_truth_df.style.format(
            {
                "question": _markdown_formatter,
                "expected_answer": _markdown_formatter,
                "query": _sql_formatter
            },
            escape="html"
        )
        _display_styled_html(styled_df)

    return ground_truth_df


def add_ground_truth_batch(
    df: pd.DataFrame,  # cols: question, answer_template, query
    datasource_id_or_name: str,
    data_agent: FabricDataAgentManagement,
    verbose: bool = False,
) -> pd.DataFrame:
    """ Add ground truth for a batch of queries and answer templates.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: question, answer_template, query.
    datasource_id_or_name : str
        Name or ID of the data source.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    verbose : bool, optional
        Flag to print verbose output. Default is False.

    Returns
    -------
    pd.DataFrame
        DataFrame with the ground truth added.
    """
    source = _get_source(datasource_id_or_name, data_agent)
    out = []
    with source.connect() as ctx:
        for r in tqdm(
            df.itertuples(index=False), total=df.shape[0], desc="ground-truth batch"
        ):
            out.append(                
                add_ground_truth(
                    str(r.question),
                    str(r.answer_template),
                    datasource_id_or_name,
                    str(r.query),
                    data_agent,
                    exec_ctx=ctx,  # reuse open connection
                    source=source,     # reuse datasource object
                )
            )
    ground_truth_df = pd.concat(out, ignore_index=True)
    ground_truth_df.columns.name = 'index'

    if verbose:
        styled_df = ground_truth_df.style.format(
            {
                "question": _markdown_formatter,
                "expected_answer": _markdown_formatter,
                "query": _sql_formatter
            },
            escape="html"
        )
        _display_styled_html(styled_df)

    return ground_truth_df

def _extract_placeholders(template: str) -> set[str]:
    """
    Return all *named* placeholders in a str.format template.
    """
    fmt = string.Formatter()
    # correct tuple order: literal_text, field_name, format_spec, conversion
    return {
        field_name
        for _lit, field_name, _spec, _conv in fmt.parse(template)
        if field_name
    }


def _get_source(
    datasource_id_or_name: str,  # name **or** id
    data_agent: FabricDataAgentManagement,
    workspace_id_or_name: str | None = None,  # optional
) -> BaseSource:
    """
    Return the datasource's type or raise if not found.
    Parameters
    ----------
    datasource_id_or_name : str
        The name or ID of the datasource.
    workspace_id_or_name : str, optional
        The workspace name or ID. Defaults to None. If `workspace_id_or_name` is supplied the search is performed in that
    workspace; otherwise the current workspace is used.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    Returns
    -------
    Return a concrete datasource wrapper (BaseSource subclass), looking in the supplied workspace when given.

    Raises
    -------
    ValueError
        If the data source is not found.
    """
    # Normalize workspace
    ws_name, _ = resolve_workspace_name_and_id(workspace_id_or_name)

    # 2. fetch all datasources visible to the agent (may span workspaces)
    # pick the matching datasource from the agent list
    for ds in data_agent.get_datasources():
        cfg = ds.get_configuration()
        if cfg.get("id") == datasource_id_or_name or cfg.get("display_name") == datasource_id_or_name:
            # inject workspace name so connectors can use it
            cfg["workspace_name"] = ws_name
            return make_source(cfg)

    raise ValueError(
        f"Datasource '{datasource_id_or_name}' (workspace={workspace_id_or_name}) not found"
    )
