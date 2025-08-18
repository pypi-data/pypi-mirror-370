
import json
import re
from typing import List, Dict, Tuple, Any
from pandas import DataFrame
from fabric.dataagent.evaluation._models import FewShotCase, FewShotEvalResult

# Default model name for Fabric inbuilt LLM
FABRIC_DEFAULT_MODEL = "gpt-4o"


def build_batch_prompt_fewshot_validation(examples: List[Dict[str, str]]) -> str:
    """Build a prompt to evaluate multiple examples in a single LLM call"""
    prompt = """
    You will be given multiple few-shot examples, each consisting of a natural language question and its corresponding SQL query.
    Your task is to determine if each is a good quality example for teaching a model how to translate natural language to SQL.

    A good quality example must have the following properties:
    1. The natural language question must be clear.
    2. The natural language question and the SQL query must be closely related, meaning that the SQL query should accurately reflect the intent of the natural language question.
    3. All the literals in the natural language question should be mapped to some literals in the SQL query. It should be straightforward to identify this mapping. Evaluate when there is a mapping of all the literals. Do not judge mappings based on the names of the columns the filter is applied on.

    Think step-by-step for each example and explain your reasoning. Return JSON in the form:
    {
        "evaluations": [
            {
                "example_id": 1,
                "reasoning": "Explanation of answer for example 1.",
                "quality": "yes" if the example is a good quality example, otherwise "no",
                "reasoning_details": {
                    "clarity": "yes" or "no",
                    "mapping": "yes" or "no",
                    "relatedness": "yes" or "no"
                }
            }
            // Add more example evaluations as needed
        ]
    }

    Here are the examples to evaluate:
    """
    for i, example in enumerate(examples, 1):
        prompt += f"\nExample {i}:\n"
        prompt += f"Natural language: {example['natural language']}\n"
        prompt += f"SQL: {example['sql']}\n"
    return prompt


def sanitize_llm_json(raw: str) -> str:
    """
    Cleans up LLM-generated 'almost-JSON' strings so they can be safely passed to json.loads.
    - Removes ```json or ``` wrappers
    - Fixes illegal escape sequences
    - Escaped single quotes to normal quotes
    - Escapes control characters in string values
    - Handles unterminated strings and other batch response issues
    - Fixes missing commas and malformed JSON structure
    - Strips prefixes
    Returns a cleaned JSON string.
    """
    s = raw.strip()
    s = re.sub(r'^\w+:\s*', '', s, count=1)
    if s.startswith("```"):
        s = re.sub(r'^```[a-zA-Z]*\n?', '', s)
        s = re.sub(r'\n?```$', '', s).strip()
    s = s.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    s = re.sub(r'\s+', ' ', s)
    s = s.replace("\\'", "'")
    s = s.replace("\\\\n", "\\n")
    s = s.replace("\\\\r", "\\r")
    s = s.replace("\\\\t", "\\t")
    s = s.replace("\\\n", " ")
    s = s.replace("\\n", " ")
    s = s.replace("\\r", " ")
    # Safer function to fix missing commas between JSON objects
    def fix_missing_commas(text):
        corrected = []
        in_string = False
        i = 0
        while i < len(text):
            char = text[i]
            if char == '"':
                in_string = not in_string
            if not in_string and char == '}':
                # Look ahead for opening brace
                j = i + 1
                while j < len(text) and text[j].isspace():
                    j += 1
                if j < len(text) and text[j] == '{':
                    corrected.append('}, {')
                    i = j  # Skip to opening brace
                    continue
            corrected.append(char)
            i += 1
        return ''.join(corrected)

    s = fix_missing_commas(s)
    s = re.sub(r'}\s*]', '} ]', s)
    s = re.sub(r'"\s*"([^"]+)":', '", "$1":', s)
    def fix_string_termination(text):
        result = []
        in_string = False
        escaped = False
        for char in text:
            if escaped:
                result.append(char)
                escaped = False
                continue
            if char == '\\' and in_string:
                result.append(char)
                escaped = True
                continue
            if char == '"':
                if not in_string:
                    in_string = True
                    result.append(char)
                else:
                    in_string = False
                    result.append(char)
            else:
                result.append(char)
        if in_string:
            result.append('"')
        return ''.join(result)
    s = fix_string_termination(s)
    def fix_quotes_in_strings(text):
        patterns = [
            r'"reasoning":\s*"([^"]*)"',
            r'"quality":\s*"([^"]*)"'
        ]
        for pattern in patterns:
            def fix_content(match):
                field_name = match.group(0).split(':')[0]
                content = match.group(1)
                content = re.sub(r'(?<!\\)"', '\\"', content)
                return f'{field_name}: "{content}"'
            text = re.sub(pattern, fix_content, text)
        return text
    s = fix_quotes_in_strings(s)
    s = re.sub(r'}\s*{\s*"example_id"', '}, { "example_id"', s)
    open_braces = s.count('{')
    close_braces = s.count('}')
    if open_braces > close_braces:
        s += '}' * (open_braces - close_braces)
    open_brackets = s.count('[')
    close_brackets = s.count(']')
    if open_brackets > close_brackets:
        s += ']' * (open_brackets - close_brackets)
    return s


def evaluate_few_shot_examples(
    examples: List[Dict[str, str]],
    llm_client: Any = None,
    model_name: str = None,
    batch_size: int = 10,
    use_fabric_llm: bool = True
) -> FewShotEvalResult:
    """
    Evaluate few-shot examples using an LLM model.

    Args:
        examples: List of dicts with 'natural language' and 'sql' keys.
        llm_client: LLM client instance (should have .chat.completions.create) if not using Fabric inbuilt LLM.
        model_name: Name of the LLM model to use. If None and use_fabric_llm is True, will use default Fabric model.
        batch_size: Number of examples per batch.
        use_fabric_llm: If True, use Fabric inbuilt LLM endpoint. If False, use provided llm_client.

    Returns:
        FewShotEvalResult: NamedTuple with fields:
            - success_cases: List[FewShotCase]
            - failure_cases: List[FewShotCase]
            - success_count: int
            - total: int
            - success_rate: float

    Example:
        >>> result = evaluate_few_shot_examples(examples, use_fabric_llm=True)
        >>> df = cases_to_dataframe(result.success_cases)
        >>> print(result.success_rate)
    """
    # Parameter validation
    if not isinstance(examples, list) or not examples:
        raise ValueError("'examples' must be a non-empty list of dicts.")
    for ex in examples:
        if not isinstance(ex, dict) or 'natural language' not in ex or 'sql' not in ex:
            raise ValueError("Each example must be a dict with 'natural language' and 'sql' keys.")

    if use_fabric_llm:
        try:
            import openai
        except ImportError:
            raise ImportError("Fabric inbuilt LLM requires the 'openai' package available in the environment.")
        llm_client = openai
        if model_name is None:
            model_name = FABRIC_DEFAULT_MODEL
    elif llm_client is None or model_name is None:
        raise ValueError("If use_fabric_llm is False, you must provide both llm_client and model_name.")

    all_success_cases = []
    all_failure_cases = []
    total_success_count = 0
    total = len(examples)
    for i in range(0, total, batch_size):
        batch = examples[i:min(i+batch_size, total)]
        prompt = build_batch_prompt_fewshot_validation(batch)
        response = llm_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content.strip()
        result = sanitize_llm_json(result)
        try:
            result_json = json.loads(result)
        except Exception as e:
            raise RuntimeError(f"Failed to parse LLM output as JSON: {e}\nRaw output: {result}")
        success_cases = []
        failure_cases = []
        success_count = 0
        evaluations = result_json.get("evaluations", [])
        for eval_result in evaluations:
            example_id = int(eval_result.get("example_id", 0)) - 1
            if 0 <= example_id < len(batch):
                example = batch[example_id]
                quality = eval_result.get("quality", "").strip().lower()
                reasoning = eval_result.get("reasoning", "No reasoning provided")
                case: FewShotCase = {
                    "example": example,
                    "reasoning": reasoning,
                    "quality": quality,
                    "reasoning_details": eval_result.get("reasoning_details", {})
                }
                if quality == "yes":
                    success_count += 1
                    success_cases.append(case)
                else:
                    failure_cases.append(case)
        all_success_cases.extend(success_cases)
        all_failure_cases.extend(failure_cases)
        total_success_count += success_count
    success_rate = (total_success_count / total) * 100 if total > 0 else 0
    # TODO: Add conflict detection here if needed in the future
    return FewShotEvalResult(
        success_cases=all_success_cases,
        failure_cases=all_failure_cases,
        success_count=total_success_count,
        total=total,
        success_rate=success_rate
    )


def cases_to_dataframe(cases: List[Dict]) -> DataFrame:
    return DataFrame([
        {
            "Few-shot question": case["example"]["natural language"],
            "Query (answer)": case["example"]["sql"],
            "Quality score": case.get("quality", ""),
            "Feedback (Reasoning)": case.get("reasoning", "")
        }
        for case in cases
    ])
