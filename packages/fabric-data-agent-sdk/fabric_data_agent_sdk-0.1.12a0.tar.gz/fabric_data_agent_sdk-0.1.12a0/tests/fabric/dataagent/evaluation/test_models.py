"""
Unit tests for fabric.dataagent.evaluation._models
"""
import pytest
from datetime import datetime
import uuid

from fabric.dataagent.evaluation._models import (
    CommandOutput, EvaluationContext, RunSteps, EvaluationResult
)


def test_command_output_creation():
    """Test creating a CommandOutput instance."""
    # Test with all fields
    cmd_output = CommandOutput(
        sql="SELECT * FROM table",
        dax="EVALUATE table",
        kql="table | where x > 10"
    )
    assert cmd_output.sql == "SELECT * FROM table"
    assert cmd_output.dax == "EVALUATE table"
    assert cmd_output.kql == "table | where x > 10"
    
    # Test with partial fields
    cmd_output = CommandOutput(sql="SELECT * FROM table")
    assert cmd_output.sql == "SELECT * FROM table"
    assert cmd_output.dax is None
    assert cmd_output.kql is None
    
    # Test with no fields
    cmd_output = CommandOutput()
    assert cmd_output.sql is None
    assert cmd_output.dax is None
    assert cmd_output.kql is None


def test_evaluation_context_creation():
    """Test creating an EvaluationContext instance."""
    # Required fields
    eval_id = str(uuid.uuid4())
    timestamp = datetime.now()
    
    context = EvaluationContext(
        row={"question": "How many sales?", "expected_answer": "100"},
        data_agent_name="test-agent",
        data_agent_stage="production",
        eval_id=eval_id,
        run_timestamp=timestamp
    )
    
    # Check required fields
    assert context.row == {"question": "How many sales?", "expected_answer": "100"}
    assert context.data_agent_name == "test-agent"
    assert context.data_agent_stage == "production"
    assert context.eval_id == eval_id
    assert context.run_timestamp == timestamp
    
    # Check default values
    assert context.workspace_name is None
    assert context.table_name == 'evaluation_output'
    assert context.critic_prompt is None
    assert context.max_workers == 5
    assert context.num_query_repeats == 1
    
    # Test with all fields
    context = EvaluationContext(
        row={"question": "How many sales?", "expected_answer": "100"},
        data_agent_name="test-agent",
        workspace_name="test-workspace",
        table_name="custom_table",
        critic_prompt="Custom critic prompt",
        data_agent_stage="sandbox",
        max_workers=3,
        num_query_repeats=2,
        eval_id=eval_id,
        run_timestamp=timestamp
    )
    
    assert context.workspace_name == "test-workspace"
    assert context.table_name == "custom_table"
    assert context.critic_prompt == "Custom critic prompt"
    assert context.data_agent_stage == "sandbox"
    assert context.max_workers == 3
    assert context.num_query_repeats == 2


def test_evaluation_context_copy():
    """Test copying an EvaluationContext with updates."""
    eval_id = str(uuid.uuid4())
    timestamp = datetime.now()
    
    original = EvaluationContext(
        row={"question": "How many sales?", "expected_answer": "100"},
        data_agent_name="test-agent",
        data_agent_stage="production",
        eval_id=eval_id,
        run_timestamp=timestamp
    )
    
    # Test copying with update
    updated = original.copy(update={
        "row": {"question": "New question", "expected_answer": "New answer"},
        "max_workers": 10
    })
    
    # Original should be unchanged
    assert original.row == {"question": "How many sales?", "expected_answer": "100"}
    assert original.max_workers == 5
    
    # Updated should have new values
    assert updated.row == {"question": "New question", "expected_answer": "New answer"}
    assert updated.max_workers == 10
    
    # Other fields should be the same
    assert updated.data_agent_name == original.data_agent_name
    assert updated.eval_id == original.eval_id
    assert updated.run_timestamp == original.run_timestamp


def test_run_steps_creation():
    """Test creating a RunSteps instance."""
    run_steps = RunSteps(
        thread_id="thread-123",
        run_id="run-456",
        function_names="function1,function2",
        function_queries="query1,query2",
        function_outputs="output1,output2",
        sql_steps="SELECT * FROM table",
        dax_steps="EVALUATE table",
        kql_steps="table | where x > 10"
    )
    
    assert run_steps.thread_id == "thread-123"
    assert run_steps.run_id == "run-456"
    assert run_steps.function_names == "function1,function2"
    assert run_steps.function_queries == "query1,query2"
    assert run_steps.function_outputs == "output1,output2"
    assert run_steps.sql_steps == "SELECT * FROM table"
    assert run_steps.dax_steps == "EVALUATE table"
    assert run_steps.kql_steps == "table | where x > 10"
    
    # id field is optional
    assert run_steps.id is None
    
    # Test with id
    run_steps = RunSteps(
        id="id-789",
        thread_id="thread-123",
        run_id="run-456",
        function_names="function1,function2",
        function_queries="query1,query2",
        function_outputs="output1,output2",
        sql_steps="SELECT * FROM table",
        dax_steps="EVALUATE table",
        kql_steps="table | where x > 10"
    )
    
    assert run_steps.id == "id-789"


def test_evaluation_result_creation():
    """Test creating an EvaluationResult instance."""
    eval_result = EvaluationResult(
        id="result-123",
        evaluation_id="eval-456",
        thread_id="thread-789",
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
    
    assert eval_result.id == "result-123"
    assert eval_result.evaluation_id == "eval-456"
    assert eval_result.thread_id == "thread-789"
    assert isinstance(eval_result.run_timestamp, datetime)
    assert eval_result.question == "How many sales?"
    assert eval_result.expected_answer == "Total sales: 100"
    assert eval_result.actual_answer == "The total sales are 100"
    assert eval_result.execution_time_sec == 1.5
    assert eval_result.status == "Completed"
    assert eval_result.thread_url == "https://example.com/thread"
    assert eval_result.evaluation_judgement is True
    assert eval_result.evaluation_message == "The answer is correct"
    assert eval_result.evaluation_status == "Success"
    assert eval_result.evaluation_thread_url == "https://example.com/eval_thread"
    
    # Test with optional fields set to None
    eval_result = EvaluationResult(
        id="result-123",
        evaluation_id="eval-456",
        thread_id="thread-789",
        run_timestamp=datetime.now(),
        question="How many sales?",
        expected_answer="Total sales: 100",
        actual_answer="The total sales are 100",
        execution_time_sec=1.5,
        status="Completed",
        thread_url="https://example.com/thread",
        evaluation_judgement=None,  # Optional
        evaluation_message="No evaluation yet",
        evaluation_status="Pending",
        evaluation_thread_url=""
    )
    
    assert eval_result.evaluation_judgement is None
