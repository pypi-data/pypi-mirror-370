"""
Unit tests for fabric.dataagent.evaluation._evaluation_runner
"""
import pytest
import pandas as pd
from datetime import datetime
import uuid
from unittest.mock import patch, MagicMock

from fabric.dataagent.evaluation._evaluation_runner import (
    _evaluate_row, _generate_answer, STAGE_MAP
)


@pytest.fixture(autouse=True)
def patch_fabric_context():
    """Patch get_fabric_context to always return a dummy host."""
    with patch('synapse.ml.internal_utils.session_utils.get_fabric_context', return_value={"spark.trident.pbiHost": "dummy-host"}):
        yield


@pytest.fixture
def mock_fabric_open_ai():
    """Create a mock FabricOpenAI instance."""
    fabric_client = MagicMock()
    
    # Mock thread and message related methods
    thread = MagicMock(id="thread-123")
    fabric_client.get_or_create_thread.return_value = thread
    
    # Mock assistant creation
    assistant = MagicMock(id="assistant-123")
    fabric_client.beta.assistants.create.return_value = assistant
    
    # Mock run creation and polling
    run = MagicMock(
        id="run-123",
        status="completed",
        last_error=None
    )
    fabric_client.beta.threads.runs.create_and_poll.return_value = run
    
    # Mock messages list
    message = MagicMock()
    message.content = [MagicMock(text=MagicMock(value="The total sales are 100"))]  # <-- updated value
    fabric_client.beta.threads.messages.list.return_value = [message]
    
    # Mock run steps
    step = MagicMock()
    step.step_details.type = "tool_calls"
    tool_call = MagicMock()
    tool_call.type = "function"
    tool_call.function.name = "test_function"
    tool_call.function.arguments = '{"query": "SELECT * FROM table"}'
    tool_call.function.output = '```sql\nSELECT * FROM table\n```'
    step.step_details.tool_calls = [tool_call]
    fabric_client.beta.threads.runs.steps.list.return_value = [step]
    
    return fabric_client


@patch('fabric.dataagent.evaluation._evaluation_runner.FabricOpenAI')
@patch('fabric.dataagent.evaluation._evaluation_runner.FabricDataAgentManagement')
@patch('fabric.dataagent.evaluation._evaluation_runner._generate_answer')
def test_evaluate_row(mock_generate_answer, mock_data_agent_cls, mock_fabric_open_ai_cls, sample_evaluation_context):
    """Test _evaluate_row function."""
    # Setup
    mock_fabric_open_ai = mock_fabric_open_ai_cls.return_value
    mock_data_agent = mock_data_agent_cls.return_value
    mock_data_agent.host = "https://dummy-host"

    eval_result = MagicMock()
    run_steps = MagicMock()
    mock_generate_answer.return_value = (eval_result, run_steps)
    
    # Execute
    result = _evaluate_row(sample_evaluation_context)
    
    # Assert
    assert result == (eval_result, run_steps)
    
    # Check that FabricOpenAI was created with the right parameters
    mock_fabric_open_ai_cls.assert_called_once_with(
        artifact_name=sample_evaluation_context.data_agent_name,
        workspace_name=sample_evaluation_context.workspace_name,
        ai_skill_stage='production'  # Default stage
    )
    
    # Check that _generate_answer was called with the right parameters
    mock_generate_answer.assert_called_once_with(
        sample_evaluation_context.row["question"],
        mock_fabric_open_ai,
        mock_data_agent,  # Corrected: was incorrectly using mock_data_agent.return_value
        sample_evaluation_context.row["expected_answer"],
        sample_evaluation_context.critic_prompt,
        sample_evaluation_context.eval_id,
        sample_evaluation_context.run_timestamp
    )


@patch('fabric.dataagent.evaluation._evaluation_runner.FabricOpenAI')
@patch('fabric.dataagent.evaluation._evaluation_runner.FabricDataAgentManagement')
@patch('fabric.dataagent.evaluation._evaluation_runner._generate_answer')
def test_evaluate_row_with_sandbox_stage(
    mock_generate_answer, mock_data_agent_cls, mock_fabric_open_ai_cls, sample_evaluation_context
):
    """Test _evaluate_row function with sandbox stage."""
    # Setup
    sample_evaluation_context.data_agent_stage = "sandbox"
    mock_fabric_open_ai = mock_fabric_open_ai_cls.return_value
    mock_data_agent = mock_data_agent_cls.return_value
    mock_data_agent.host = "https://dummy-host"
    
    eval_result = MagicMock()
    run_steps = MagicMock()
    mock_generate_answer.return_value = (eval_result, run_steps)
    
    # Execute
    result = _evaluate_row(sample_evaluation_context)
    
    # Assert
    assert result == (eval_result, run_steps)
    
    # Check that FabricOpenAI was created with the right parameters
    mock_fabric_open_ai_cls.assert_called_once_with(
        artifact_name=sample_evaluation_context.data_agent_name,
        workspace_name=sample_evaluation_context.workspace_name,
        ai_skill_stage='sandbox'  # Sandbox stage
    )


@patch('fabric.dataagent.evaluation._evaluation_runner._get_message')
@patch('fabric.dataagent.evaluation._thread._get_thread_url')
@patch('fabric.dataagent.evaluation._thread._get_steps')
@patch('fabric.dataagent.evaluation._thread._generate_prompt')
def test_generate_answer(
    mock_generate_prompt, mock_get_steps, mock_get_thread_url, mock_get_message, 
    mock_fabric_open_ai, mock_data_agent
):
    """Test _generate_answer function."""
    # Setup
    query = "How many sales?"
    expected_answer = "Total sales: 100"
    critic_prompt = "Custom critic prompt"
    eval_id = str(uuid.uuid4())
    run_timestamp = datetime.now()
    
    # Mock the thread creation
    thread_id = "thread-123"
    mock_fabric_open_ai.get_or_create_thread.return_value.id = thread_id
    
    # Argument-matching side_effect for _get_message
    def get_message_side_effect(fabric_client, thread_id, query):
        if query == "How many sales?":
            return ("The total sales are 100", MagicMock(id="run-123", status="completed"))
        elif query == "Custom critic prompt":
            return ("Yes", MagicMock(id="run-456", status="completed"))
        else:
            return ("Unknown", MagicMock(id="run-000", status="completed"))
    mock_get_message.side_effect = get_message_side_effect
    
    # Mock the thread URL
    thread_url = "https://example.com/thread"
    mock_get_thread_url.return_value = thread_url
    
    # Mock the run steps
    run_steps = MagicMock()
    mock_get_steps.return_value = run_steps
    
    # Mock the prompt generation
    prompt = "Evaluation prompt"
    mock_generate_prompt.return_value = prompt
    
    # Execute
    eval_result, result_run_steps = _generate_answer(
        query, mock_fabric_open_ai, mock_data_agent, expected_answer, critic_prompt, eval_id, run_timestamp
    )
    
    # Assert
    assert isinstance(eval_result.id, str)
    assert eval_result.evaluation_id == eval_id
    assert eval_result.thread_id == thread_id
    assert eval_result.run_timestamp == run_timestamp
    assert eval_result.question == query
    assert eval_result.expected_answer == expected_answer
    assert eval_result.actual_answer == "The total sales are 100"
    assert isinstance(eval_result.execution_time_sec, float)
    assert eval_result.status == "completed"
    assert eval_result.thread_url is not None
    assert eval_result.evaluation_judgement is True  # 'Yes' should evaluate to True
    assert eval_result.evaluation_message.strip().lower() == "yes"
    assert eval_result.evaluation_status == "completed"
    assert eval_result.evaluation_thread_url is not None
    
    assert result_run_steps == run_steps
    
    # Check that the methods were called correctly
    mock_fabric_open_ai.get_or_create_thread.assert_called_once()
    assert mock_get_steps.call_count == 1


@patch('fabric.dataagent.evaluation._thread._get_message')
@patch('fabric.dataagent.evaluation._thread._get_thread_url')
@patch('fabric.dataagent.evaluation._thread._get_steps')
@patch('fabric.dataagent.evaluation._thread._generate_prompt')
def test_generate_answer_with_no_judgement(
    mock_generate_prompt, mock_get_steps, mock_get_thread_url, mock_get_message, 
    mock_fabric_open_ai, mock_data_agent
):
    """Test _generate_answer function with 'Unclear' evaluation."""
    # Setup
    query = "How many sales?"
    expected_answer = "Total sales: 100"
    critic_prompt = None
    eval_id = str(uuid.uuid4())
    run_timestamp = datetime.now()
    
    # Mock the thread creation
    thread_id = "thread-123"
    mock_fabric_open_ai.get_or_create_thread.return_value.id = thread_id
    
    # Mock the first message (answer)
    mock_get_message.side_effect = [
        ("The total sales are 100", MagicMock(id="run-123", status="completed")),  # First call: answer
        ("Unclear", MagicMock(id="run-456", status="completed"))  # Second call: evaluation
    ]
    
    # Mock the thread URL
    thread_url = "https://example.com/thread"
    mock_get_thread_url.return_value = thread_url
    
    # Mock the run steps
    run_steps = MagicMock()
    mock_get_steps.return_value = run_steps
    
    # Mock the prompt generation
    prompt = "Evaluation prompt"
    mock_generate_prompt.return_value = prompt
    
    # Execute
    eval_result, _ = _generate_answer(
        query, mock_fabric_open_ai, mock_data_agent, expected_answer, critic_prompt, eval_id, run_timestamp
    )
    
    # Assert
    assert eval_result.evaluation_judgement is None  # "Unclear" should evaluate to None


def test_stage_map():
    """Test the STAGE_MAP constant."""
    assert STAGE_MAP['draft'] == 'sandbox'
    assert STAGE_MAP['sandbox'] == 'sandbox'
    assert STAGE_MAP['publishing'] == 'production'
    assert STAGE_MAP['production'] == 'production'
