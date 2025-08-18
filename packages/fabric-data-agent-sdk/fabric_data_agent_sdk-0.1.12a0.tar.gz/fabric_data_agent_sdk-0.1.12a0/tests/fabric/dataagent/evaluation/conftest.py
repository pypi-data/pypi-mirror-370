"""
Common fixtures for evaluation tests.
"""
import pytest
import pandas as pd
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch
from fabric.dataagent.client import FabricDataAgentManagement
from fabric.dataagent.evaluation._models import EvaluationResult, RunSteps, EvaluationContext


@pytest.fixture(autouse=True)
def patch_markdown():
    with patch('IPython.display.Markdown', return_value=''):
        yield


@pytest.fixture
def mock_data_agent():
    """Return a mocked FabricDataAgentManagement instance."""
    data_agent = MagicMock(spec=FabricDataAgentManagement)
    data_agent.get_configuration.return_value = {"name": "test-agent", "description": "Test Agent"}
    data_agent.get_datasources.return_value = [
        MagicMock(get_configuration=lambda: {"id": "test-datasource", "display_name": "Test Datasource"})
    ]
    data_agent._client = MagicMock()
    data_agent._client.get_publishing_info.return_value = MagicMock(
        etag="test-etag",
        value={"currentVersion": "1.0", "lastUpdated": "2023-01-01T00:00:00Z"}
    )
    data_agent.host = "https://dummy-host"
    return data_agent


@pytest.fixture
def sample_evaluation_df():
    """Return a sample DataFrame for evaluation."""
    return pd.DataFrame({
        "question": ["How many sales?", "What is the revenue?"],
        "expected_answer": ["Total sales: 100", "Total revenue: $5000"]
    })


@pytest.fixture
def sample_evaluation_result():
    """Return a sample EvaluationResult."""
    return EvaluationResult(
        id=str(uuid.uuid4()),
        evaluation_id=str(uuid.uuid4()),
        thread_id=str(uuid.uuid4()),
        run_timestamp=datetime.now(),
        question="How many sales?",
        expected_answer="Total sales: 100",
        actual_answer="The total sales are 100",
        execution_time_sec=1.5,
        status="Completed",
        thread_url="https://example.com/thread",
        evaluation_judgement=True,
        evaluation_message="The answer is correct",
        evaluation_status="Success",
        evaluation_thread_url="https://example.com/eval_thread"
    )


@pytest.fixture
def sample_run_steps():
    """Return a sample RunSteps."""
    return RunSteps(
        thread_id=str(uuid.uuid4()),
        run_id=str(uuid.uuid4()),
        function_names="function1,function2",
        function_queries="query1,query2",
        function_outputs="output1,output2",
        sql_steps="SELECT * FROM table",
        dax_steps="EVALUATE table",
        kql_steps="table | where x > 10"
    )


@pytest.fixture
def sample_evaluation_context():
    """Return a sample EvaluationContext."""
    return EvaluationContext(
        row={"question": "How many sales?", "expected_answer": "Total sales: 100"},
        data_agent_name="test-agent",
        workspace_name="test-workspace",
        table_name="evaluation_output",
        data_agent_stage="production",
        eval_id=str(uuid.uuid4()),
        run_timestamp=datetime.now()
    )
