"""
General utility functions for data agent evaluation.
"""
import logging
import numpy as np
import pandas as pd
from IPython.display import HTML, display, Markdown
from fabric.dataagent.client import FabricDataAgentManagement
from sempy.fabric.exceptions import FabricHTTPException


def _add_data_agent_details(df: pd.DataFrame, data_agent: FabricDataAgentManagement):
    """
    Add Data Agent details to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with processed output rows.
    data_agent: FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.

    Returns
    -------
    pd.DataFrame
        Updated dataframe with Data Agent details.
    """

    # Return unmodified DataFrame if data agent is None
    if data_agent is None:
        return df

    df['data_agent_version'] = pd.Series(None, dtype='string')
    df['data_agent_etag'] = pd.Series(None, dtype='string')
    df['data_agent_last_updated'] = pd.Series(None, dtype='string')

    # Add the Data Agent details to DataFrame
    df['data_agent_configuration'] = str(data_agent.get_configuration())
    try:
        # Fetch the publish info of DataAgent
        publishing_info = data_agent._client.get_publishing_info()
        df['data_agent_version'] = publishing_info.value['currentVersion']
        df['data_agent_etag'] = publishing_info.etag
        df['data_agent_last_updated'] = publishing_info.value['lastUpdated']
    except FabricHTTPException:
        # Skipping the publish info as DataAgent is not published
        pass
    data_sources = str(data_agent.get_datasources())
    df['data_sources'] = [data_sources] * len(df)

    return df
