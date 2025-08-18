"""
Unit tests for fabric.dataagent.evaluation._utils
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from fabric.dataagent.evaluation._utils import _add_data_agent_details
from sempy.fabric.exceptions import FabricHTTPException


def test_add_data_agent_details_basic(mock_data_agent):
    """Test adding data agent details to DataFrame."""
    # Setup
    df = pd.DataFrame({
        "question": ["How many sales?", "What is the revenue?"],
        "expected_answer": ["Total sales: 100", "Total revenue: $5000"]
    })
    
    # Execute
    result = _add_data_agent_details(df, mock_data_agent)
    
    # Assert
    assert len(result) == len(df)
    assert "data_agent_configuration" in result.columns
    assert "data_sources" in result.columns
    assert "data_agent_version" in result.columns
    assert "data_agent_etag" in result.columns
    assert "data_agent_last_updated" in result.columns
    
    # Check values
    assert result["data_agent_version"].iloc[0] == "1.0"
    assert result["data_agent_etag"].iloc[0] == "test-etag"
    assert result["data_agent_last_updated"].iloc[0] == "2023-01-01T00:00:00Z"
    assert all(pd.notna(result["data_sources"]))


def test_add_data_agent_details_none():
    """Test adding data agent details when data_agent is None."""
    # Setup
    df = pd.DataFrame({
        "question": ["How many sales?", "What is the revenue?"],
        "expected_answer": ["Total sales: 100", "Total revenue: $5000"]
    })
    
    # Execute
    result = _add_data_agent_details(df, None)
    
    # Assert
    assert result is df  # Should return the original DataFrame unchanged


def test_add_data_agent_details_with_http_exception(mock_data_agent):
    """Test adding data agent details when FabricHTTPException is raised."""
    import pandas as pd
    from sempy.fabric.exceptions import FabricHTTPException

    # Setup
    df = pd.DataFrame({
        "question": ["How many sales?", "What is the revenue?"],
        "expected_answer": ["Total sales: 100", "Total revenue: $5000"]
    })

    # Patch get_publishing_info to raise a FabricHTTPException with a .reason attribute
    class ReasonObj:
        def __init__(self, reason):
            self.reason = reason
            self.text = reason
            self.status_code = 404
            self.headers = {}
            self.url = "http://example.com"
    reason_obj = ReasonObj("Not published")
    exc = FabricHTTPException(reason_obj)
    mock_data_agent._client.get_publishing_info.side_effect = exc

    # Execute
    result = _add_data_agent_details(df, mock_data_agent)

    # Assert
    assert len(result) == len(df)
    assert "data_agent_configuration" in result.columns
    assert "data_sources" in result.columns
    # Check that version-related columns exist but are None
    assert "data_agent_version" in result.columns
    assert "data_agent_etag" in result.columns
    assert "data_agent_last_updated" in result.columns
    assert all(pd.isna(result["data_agent_version"]))
    assert all(pd.isna(result["data_agent_etag"]))
    assert all(pd.isna(result["data_agent_last_updated"]))
