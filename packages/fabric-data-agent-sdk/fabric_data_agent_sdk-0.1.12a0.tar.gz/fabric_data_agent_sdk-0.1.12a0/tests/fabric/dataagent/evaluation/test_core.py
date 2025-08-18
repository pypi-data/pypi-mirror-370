"""
Unit tests for fabric.dataagent.evaluation.core
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from datetime import datetime
import uuid

from fabric.dataagent.evaluation.core import evaluate_data_agent
from fabric.dataagent.evaluation._models import EvaluationResult, RunSteps


@pytest.fixture
def mock_evaluate_row():
    """Mock the _evaluate_row function."""
    with patch('fabric.dataagent.evaluation.core._evaluate_row') as mock:
        mock.return_value = (
            EvaluationResult(
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
            ),
            RunSteps(
                thread_id=str(uuid.uuid4()),
                run_id=str(uuid.uuid4()),
                function_names="function1,function2",
                function_queries="query1,query2",
                function_outputs="output1,output2",
                sql_steps="SELECT * FROM table",
                dax_steps="EVALUATE table",
                kql_steps="table | where x > 10"
            )
        )
        yield mock


@patch('fabric.dataagent.evaluation.core._save_output')
@patch('fabric.dataagent.evaluation.core._add_data_agent_details')
@patch('fabric.dataagent.evaluation.core.FabricDataAgentManagement')
def test_evaluate_data_agent_basic(
    mock_data_agent_cls, mock_add_data_agent_details, mock_save_output, mock_evaluate_row, sample_evaluation_df
):
    """Test basic functionality of evaluate_data_agent."""
    # Setup
    mock_data_agent = mock_data_agent_cls.return_value
    mock_add_data_agent_details.return_value = sample_evaluation_df
    
    # Execute
    result = evaluate_data_agent(
        df=sample_evaluation_df,
        data_agent_name="test-agent"
    )
    
    # Assert
    assert isinstance(result, str)  # Should return eval_id
    assert len(result) > 0
    
    # Verify mocks were called correctly
    mock_data_agent_cls.assert_called_once_with("test-agent", None)
    assert mock_evaluate_row.call_count == len(sample_evaluation_df)
    mock_add_data_agent_details.assert_called_once()
    assert mock_save_output.call_count == 2  # Once for results, once for steps


@patch('fabric.dataagent.evaluation.core._save_output')
@patch('fabric.dataagent.evaluation.core._add_data_agent_details')
@patch('fabric.dataagent.evaluation.core.FabricDataAgentManagement')
def test_evaluate_data_agent_with_options(
    mock_data_agent_cls, mock_add_data_agent_details, mock_save_output, mock_evaluate_row, sample_evaluation_df
):
    """Test evaluate_data_agent with all optional parameters."""
    # Setup
    mock_data_agent = mock_data_agent_cls.return_value
    mock_add_data_agent_details.return_value = sample_evaluation_df
    
    # Execute
    result = evaluate_data_agent(
        df=sample_evaluation_df,
        data_agent_name="test-agent",
        workspace_name="test-workspace",
        table_name="custom_table",
        critic_prompt="Custom critic prompt",
        data_agent_stage="sandbox",
        max_workers=3,
        num_query_repeats=2
    )
    
    # Assert
    assert isinstance(result, str)  # Should return eval_id
    
    # Verify mocks were called correctly
    mock_data_agent_cls.assert_called_once_with("test-agent", "test-workspace")
    assert mock_evaluate_row.call_count == len(sample_evaluation_df) * 2  # Due to num_query_repeats=2
    mock_add_data_agent_details.assert_called_once()
    assert mock_save_output.call_count == 2  # Once for results, once for steps


@patch('fabric.dataagent.evaluation.core._save_output')
@patch('fabric.dataagent.evaluation.core._add_data_agent_details')
@patch('fabric.dataagent.evaluation.core.FabricDataAgentManagement')
@patch('fabric.dataagent.evaluation.core.display')
def test_evaluate_data_agent_with_failed_evaluation(
    mock_display, mock_data_agent_cls, mock_add_data_agent_details, mock_save_output, sample_evaluation_df
):
    """Test evaluate_data_agent with a failed evaluation."""
    # Setup
    mock_data_agent = mock_data_agent_cls.return_value
    mock_add_data_agent_details.return_value = sample_evaluation_df

    # Patch display to return a mock with an update method
    mock_display_handle = MagicMock()
    mock_display.return_value = mock_display_handle

    # Create a mock for _evaluate_row that returns a failed evaluation
    with patch('fabric.dataagent.evaluation.core._evaluate_row') as mock_evaluate_row:
        # First call: successful evaluation
        # Second call: failed evaluation
        mock_evaluate_row.side_effect = [
            (
                EvaluationResult(
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
                ),
                RunSteps(
                    thread_id=str(uuid.uuid4()),
                    run_id=str(uuid.uuid4()),
                    function_names="function1",
                    function_queries="query1",
                    function_outputs="output1",
                    sql_steps="SELECT * FROM table",
                    dax_steps="",
                    kql_steps=""
                )
            ),
            (
                EvaluationResult(
                    id=str(uuid.uuid4()),
                    evaluation_id=str(uuid.uuid4()),
                    thread_id=str(uuid.uuid4()),
                    run_timestamp=datetime.now(),
                    question="What is the revenue?",
                    expected_answer="Total revenue: $5000",
                    actual_answer="The revenue is $4000",
                    execution_time_sec=1.2,
                    status="Completed",
                    thread_url="https://example.com/thread2",
                    evaluation_judgement=False,  # Failed evaluation
                    evaluation_message="The answer is incorrect",
                    evaluation_status="Failed",
                    evaluation_thread_url="https://example.com/eval_thread2"
                ),
                RunSteps(
                    thread_id=str(uuid.uuid4()),
                    run_id=str(uuid.uuid4()),
                    function_names="function2",
                    function_queries="query2",
                    function_outputs="output2",
                    sql_steps="SELECT * FROM sales",
                    dax_steps="",
                    kql_steps=""
                )
            )
        ]

        # Execute
        result = evaluate_data_agent(
            df=sample_evaluation_df,
            data_agent_name="test-agent"
        )

        # Assert
        assert isinstance(result, str)  # Should return eval_id
        assert mock_evaluate_row.call_count == len(sample_evaluation_df)

        # Verify that the required functions were called
        mock_add_data_agent_details.assert_called_once()
        assert mock_save_output.call_count == 2
