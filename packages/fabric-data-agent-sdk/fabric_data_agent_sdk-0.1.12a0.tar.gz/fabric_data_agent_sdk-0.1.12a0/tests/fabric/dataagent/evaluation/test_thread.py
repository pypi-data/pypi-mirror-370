"""
Unit tests for fabric.dataagent.evaluation._thread
"""
import pytest
import json
from unittest.mock import patch, MagicMock

from fabric.dataagent.evaluation._thread import (
    _get_message, _get_steps, _get_commands, _generate_prompt, _get_thread_url, _get_fabric_host
)
from fabric.dataagent.evaluation._models import CommandOutput, RunSteps


@pytest.fixture
def mock_fabric_open_ai():
    """Create a mock FabricOpenAI instance."""
    fabric_client = MagicMock()
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
    message.content = [MagicMock(text=MagicMock(value="This is the answer"))]
    fabric_client.beta.threads.messages.list.return_value = [message]
    return fabric_client


def test_get_message(mock_fabric_open_ai):
    """Test _get_message function."""
    # Execute
    result, run = _get_message(mock_fabric_open_ai, "thread-123", "How many sales?")
    
    # Assert
    assert result == "This is the answer"
    assert run.status == "completed"
    
    # Verify that the expected methods were called
    mock_fabric_open_ai.beta.assistants.create.assert_called_once()
    mock_fabric_open_ai.beta.threads.messages.create.assert_called_once_with(
        thread_id="thread-123", role="user", content="How many sales?"
    )
    mock_fabric_open_ai.beta.threads.runs.create_and_poll.assert_called_once_with(
        thread_id="thread-123", assistant_id="assistant-123"
    )
    mock_fabric_open_ai.beta.threads.messages.list.assert_called_once_with(
        thread_id="thread-123", order="desc"
    )


def test_get_message_no_client():
    """Test _get_message function with no client."""
    with pytest.raises(RuntimeError, match="Fabric client is None"):
        _get_message(None, "thread-123", "How many sales?")


def test_get_message_failed_run(mock_fabric_open_ai):
    """Test _get_message function with a failed run."""
    # Setup
    mock_fabric_open_ai.beta.threads.runs.create_and_poll.return_value.status = "failed"
    mock_fabric_open_ai.beta.threads.runs.create_and_poll.return_value.last_error = MagicMock(
        code="error_code",
        message="Error message"
    )
    
    # Execute
    result, run = _get_message(mock_fabric_open_ai, "thread-123", "How many sales?")
    
    # Assert
    assert result == "Error (error_code): Error message"
    assert run.status == "failed"


def test_get_message_not_found_error():
    """Test _get_message function with NotFoundError."""
    from fabric.dataagent.evaluation._thread import _get_message, NotFoundError
    from unittest.mock import MagicMock

    # Setup the mock client and assistant
    fabric_client = MagicMock()
    assistant_mock = MagicMock()
    assistant_mock.id = "assistant-123"
    fabric_client.beta.assistants.create.return_value = assistant_mock

    # Patch the correct method in the chain
    mock_response = MagicMock()
    mock_response.request = MagicMock()
    error_instance = NotFoundError(message="Not found", response=mock_response, body=None)

    fabric_client.beta.threads.runs.create_and_poll.side_effect = error_instance

    result, run = _get_message(fabric_client, "thread-123", "How many sales?")
    # The code should return a tuple with an error message if the outer block catches the exception
    assert "Unexpected error" in result or "Invalid input for data_agent_stage" in result


def test_get_message_no_messages(mock_fabric_open_ai):
    """Test _get_message function with no messages."""
    # Setup
    mock_fabric_open_ai.beta.threads.messages.list.return_value = []
    
    # Execute
    result, run = _get_message(mock_fabric_open_ai, "thread-123", "How many sales?")
    
    # Assert
    assert result == "No answer returned from Data Agent"


def test_get_steps(mock_fabric_open_ai):
    """Test _get_steps function."""
    # Setup
    thread_id = "thread-123"
    run_id = "run-456"
    unique_id = "id-789"
    
    # Mock run steps
    step1 = MagicMock()
    step1.step_details.type = "tool_calls"
    tool_call1 = MagicMock()
    tool_call1.type = "function"
    tool_call1.function.name = "function1"
    tool_call1.function.arguments = json.dumps({"query": "SELECT * FROM table1"})
    tool_call1.function.output = '```sql\nSELECT * FROM table1\n```'
    step1.step_details.tool_calls = [tool_call1]
    
    step2 = MagicMock()
    step2.step_details.type = "tool_calls"
    tool_call2 = MagicMock()
    tool_call2.type = "function"
    tool_call2.function.name = "function2"
    tool_call2.function.arguments = json.dumps({"natural_language_query": "How many sales?"})
    tool_call2.function.output = '```dax\nEVALUATE Sales\n```'
    step2.step_details.tool_calls = [tool_call2]
    
    mock_fabric_open_ai.beta.threads.runs.steps.list.return_value = [step1, step2]
    
    # Execute
    result = _get_steps(mock_fabric_open_ai, thread_id, run_id, unique_id)
    
    # Assert
    assert isinstance(result, RunSteps)
    assert result.id == unique_id
    assert result.thread_id == thread_id
    assert result.run_id == run_id
    assert "function1" in result.function_names
    assert "function2" in result.function_names
    assert "SELECT * FROM table1" in result.function_queries
    assert "How many sales?" in result.function_queries


def test_get_steps_no_client():
    """Test _get_steps function with no client."""
    with pytest.raises(RuntimeError, match="Fabric client is None"):
        _get_steps(None, "thread-123", "run-456")


def test_get_commands():
    """Test _get_commands function."""
    # Test with SQL command
    output = "```sql\nSELECT * FROM table\n```"
    result = _get_commands(output)
    assert isinstance(result, CommandOutput)
    assert result.sql == "SELECT * FROM table\n"
    assert result.dax is None
    assert result.kql is None
    
    # Test with DAX command
    output = "```dax\nEVALUATE table\n```"
    result = _get_commands(output)
    assert result.sql is None
    assert result.dax == "EVALUATE table\n"
    assert result.kql is None
    
    # Test with KQL command
    output = "```kql\ntable | where x > 10\n```"
    result = _get_commands(output)
    assert result.sql is None
    assert result.dax is None
    assert result.kql == "table | where x > 10\n"
    
    # Test with multiple commands
    output = "```sql\nSELECT * FROM table\n```\n```dax\nEVALUATE table\n```"
    result = _get_commands(output)
    assert result.sql == "SELECT * FROM table\n"
    assert result.dax == "EVALUATE table\n"
    assert result.kql is None
    
    # Test with no commands
    output = "No commands here"
    result = _get_commands(output)
    assert result.sql is None
    assert result.dax is None
    assert result.kql is None
    
    # Test with None
    result = _get_commands(None)
    assert result.sql is None
    assert result.dax is None
    assert result.kql is None


def test_generate_prompt():
    """Test _generate_prompt function."""
    # Test with default prompt
    query = "How many sales?"
    expected_answer = "Total sales: 100"
    result = _generate_prompt(query, expected_answer)
    assert query in result
    assert expected_answer in result
    assert "determine if the most recent answer is equivalent" in result
    
    # Test with custom prompt
    custom_prompt = "Custom prompt with {query} and {expected_answer}"
    result = _generate_prompt(query, expected_answer, custom_prompt)
    assert result == "Custom prompt with How many sales? and Total sales: 100"


@patch('fabric.dataagent.evaluation._thread._get_fabric_host')
def test_get_thread_url(mock_get_fabric_host):
    """Test _get_thread_url function."""
    # Setup
    thread_id = "thread-123"
    data_agent = MagicMock()
    data_agent._client.data_agent_id = "data-agent-456"
    mock_get_fabric_host.return_value = "fabric.example.com"
    
    # Execute
    result = _get_thread_url(thread_id, data_agent)
    
    # Assert
    assert result == "https://fabric.example.com/workloads/de-ds/dataagents/data-agent-456/externalThread?debug.aiSkillThreadIdOverride=thread-123&debug.aiSkillViewPublishedOverride=0"


@patch('synapse.ml.internal_utils.session_utils.get_fabric_context')
def test_get_fabric_host(mock_get_fabric_context):
    """Test _get_fabric_host function."""
    # Setup
    mock_get_fabric_context.return_value = {
        'spark.trident.pbiHost': 'api.fabric.example.com'
    }
    
    # Execute
    result = _get_fabric_host()
    
    # Assert
    assert result == ".fabric.example.com"  # 'api' should be removed


@patch('synapse.ml.internal_utils.session_utils.get_fabric_context')
def test_get_fabric_host_no_host(mock_get_fabric_context):
    """Test _get_fabric_host function when host is None."""
    # Setup
    mock_get_fabric_context.return_value = {}
    
    # Execute and Assert
    with pytest.raises(RuntimeError, match="Fabric Host address is empty"):
        _get_fabric_host()  


def test_get_steps_run_steps_exception(monkeypatch, mock_fabric_open_ai):
    # Patch steps.list to raise
    mock_fabric_open_ai.beta.threads.runs.steps.list.side_effect = Exception("fail")
    result = _get_steps(mock_fabric_open_ai, "thread", "run")
    assert isinstance(result, RunSteps)
    assert result.thread_id == "thread"
    assert result.run_id == "run"


def test_get_steps_tool_call_arguments_not_json(mock_fabric_open_ai):
    # Setup a tool_call with invalid JSON arguments
    step = MagicMock()
    step.step_details.type = "tool_calls"
    tool_call = MagicMock()
    tool_call.type = "function"
    tool_call.function.name = "func"
    tool_call.function.arguments = "not-json"
    tool_call.function.output = ""
    step.step_details.tool_calls = [tool_call]
    mock_fabric_open_ai.beta.threads.runs.steps.list.return_value = [step]
    result = _get_steps(mock_fabric_open_ai, "thread", "run")
    assert "not-json" in result.function_queries


def test_get_commands_regex_exception(monkeypatch):
    import fabric.dataagent.evaluation._thread as thread_mod
    monkeypatch.setattr(thread_mod.re, "findall", lambda *a, **k: (_ for _ in ()).throw(Exception("regex fail")))
    result = thread_mod._get_commands("```sql\nSELECT * FROM t\n```")
    assert isinstance(result, CommandOutput)
    assert result.sql is None and result.dax is None and result.kql is None

def test_get_message_outer_exception(monkeypatch, mock_fabric_open_ai):
    # Patch assistants.create to raise an exception
    mock_fabric_open_ai.beta.assistants.create.side_effect = Exception("outer fail")
    result, run = _get_message(mock_fabric_open_ai, "thread-123", "How many sales?")
    assert "Unexpected error" in result
    assert run.status == "failed"

def test_get_message_inner_message_exception(monkeypatch, mock_fabric_open_ai):
    # Patch messages.list to raise an exception
    def raise_exc(*a, **k):
        raise Exception("inner fail")
    mock_fabric_open_ai.beta.threads.messages.list.side_effect = raise_exc
    result, run = _get_message(mock_fabric_open_ai, "thread-123", "How many sales?")
    assert "Error retrieving message" in result
