
import pytest
from fabric.dataagent.evaluation.few_shot_validation import evaluate_few_shot_examples, FewShotEvalResult

# Module-level dummy LLM classes for mocking
class DummyChoices:
    def __init__(self, content):
        self.message = type("msg", (), {"content": content})
class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoices(content)]
class DummyChat:
    def __init__(self, content):
        self.completions = type("comp", (), {"create": lambda *args, **kwargs: DummyResponse(content)})
class DummyLLM:
    def __init__(self, content):
        self.chat = DummyChat(content)

def test_evaluate_few_shot_examples_validation():
    dummy_examples = [
        {"natural language": "What is the sum of sales?", "sql": "SELECT SUM(sales) FROM table;"},
        {"natural language": "How many users?", "sql": "SELECT COUNT(*) FROM users;"}
    ]
    # Should raise error if examples is empty
    with pytest.raises(ValueError):
        evaluate_few_shot_examples([])
    # Should raise error if example is missing keys
    with pytest.raises(ValueError):
        evaluate_few_shot_examples([{"foo": "bar"}])
    # Note: For real LLM test, mock llm_client or use use_fabric_llm=True in a Fabric environment
    # This test only checks input validation
    # Should raise error if examples is not a list
    with pytest.raises(ValueError):
        evaluate_few_shot_examples("not a list")
    with pytest.raises(ValueError):
        evaluate_few_shot_examples({"natural language": "foo", "sql": "bar"})

def test_evaluate_few_shot_examples_valid(monkeypatch):
    # Simulate a valid LLM JSON response
    llm_content = '{"evaluations": [{"example_id": 1, "reasoning": "Good mapping.", "quality": "yes", "reasoning_details": {"clarity": "yes", "mapping": "yes", "relatedness": "yes"}}, {"example_id": 2, "reasoning": "Clear question.", "quality": "no", "reasoning_details": {"clarity": "yes", "mapping": "no", "relatedness": "yes"}}]}'
    dummy_llm = DummyLLM(llm_content)
    examples = [
        {"natural language": "What is the sum of sales?", "sql": "SELECT SUM(sales) FROM table;"},
        {"natural language": "How many users?", "sql": "SELECT COUNT(*) FROM users;"}
    ]
    result = evaluate_few_shot_examples(examples, llm_client=dummy_llm, model_name="dummy", use_fabric_llm=False)
    assert isinstance(result, FewShotEvalResult)
    assert result.total == 2
    assert result.success_count == 1
    assert result.success_rate == 50.0
    assert len(result.success_cases) == 1
    assert len(result.failure_cases) == 1

def test_evaluate_few_shot_examples_duplicates(monkeypatch):
    # Simulate LLM response for duplicates
    llm_content = '{"evaluations": [{"example_id": 1, "reasoning": "Duplicate example.", "quality": "yes", "reasoning_details": {"clarity": "yes", "mapping": "yes", "relatedness": "yes"}}, {"example_id": 2, "reasoning": "Duplicate example.", "quality": "yes", "reasoning_details": {"clarity": "yes", "mapping": "yes", "relatedness": "yes"}}]}'
    dummy_llm = DummyLLM(llm_content)
    examples = [
        {"natural language": "What is the sum of sales?", "sql": "SELECT SUM(sales) FROM table;"},
        {"natural language": "What is the sum of sales?", "sql": "SELECT SUM(sales) FROM table;"}
    ]
    result = evaluate_few_shot_examples(examples, llm_client=dummy_llm, model_name="dummy", use_fabric_llm=False)
    assert result.success_count == 2

def test_evaluate_few_shot_examples_empty_strings(monkeypatch):
    llm_content = '{"evaluations": [{"example_id": 1, "reasoning": "Empty question.", "quality": "no", "reasoning_details": {"clarity": "no", "mapping": "no", "relatedness": "no"}}]}'
    dummy_llm = DummyLLM(llm_content)
    examples = [
        {"natural language": "", "sql": ""}
    ]
    result = evaluate_few_shot_examples(examples, llm_client=dummy_llm, model_name="dummy", use_fabric_llm=False)
    assert result.success_count == 0
    assert result.success_rate == 0.0

def test_evaluate_few_shot_examples_missing_nl_or_sql():
    # Missing 'natural language' key
    with pytest.raises(ValueError):
        evaluate_few_shot_examples([{"sql": "SELECT 1;"}])
    # Missing 'sql' key
    with pytest.raises(ValueError):
        evaluate_few_shot_examples([{"natural language": "foo"}])

def test_evaluate_few_shot_examples_large_batch(monkeypatch):
    # Simulate LLM response for large batch
    batch_size = 50
    llm_content = '{"evaluations": [' + ','.join([
        '{"example_id": %d, "reasoning": "ok", "quality": "yes", "reasoning_details": {"clarity": "yes", "mapping": "yes", "relatedness": "yes"}}' % (i+1)
        for i in range(batch_size)
    ]) + ']}'
    dummy_llm = DummyLLM(llm_content)
    examples = [
        {"natural language": f"Q{i}", "sql": f"SELECT {i};"} for i in range(batch_size)
    ]
    result = evaluate_few_shot_examples(examples, llm_client=dummy_llm, model_name="dummy", use_fabric_llm=False)
    assert result.success_count == batch_size
    assert result.success_rate == 100.0
