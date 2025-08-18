"""
Functions for executing evaluations of data agents.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pandas as pd
import time
from tqdm import tqdm
from typing import Optional, Tuple, Any
import uuid

from fabric.dataagent.client import FabricDataAgentManagement, FabricOpenAI
from fabric.dataagent.evaluation._thread import (
    _get_message, _get_thread_url, _generate_prompt
)
from fabric.dataagent.evaluation._models import EvaluationResult, RunSteps, EvaluationContext

# Map user-friendly stage names to internal values
STAGE_MAP = {
    'draft': 'sandbox',
    'sandbox': 'sandbox',
    'publishing': 'production',
    'production': 'production'
}

def _evaluate_row(
    params: EvaluationContext
) -> Tuple[EvaluationResult, RunSteps]:
    """
    Evaluate a single row of input DataFrame.
    
    Parameters
    ----------
    params : EvaluationContext
        Evaluation parameters including the row data, data agent details, and evaluation settings.
    
    Returns
    -------
    tuple[EvaluationResult, RunSteps]
        Formatted response of the Data Agent and run steps.
    """
    # Normalize input and get the internal stage value
    data_agent_stage_internal = STAGE_MAP.get(str(params.data_agent_stage).lower(), 'production')
    
    fabric_client = FabricOpenAI(
        artifact_name=params.data_agent_name,
        workspace_name=params.workspace_name,
        ai_skill_stage=data_agent_stage_internal
    )
    data_agent = FabricDataAgentManagement(params.data_agent_name, params.workspace_name)
    query: str = str(params.row['question'])
    expected_answer: str = str(params.row['expected_answer'])

    # Generate the response for the query
    output_row, run_steps = _generate_answer(
        query, 
        fabric_client, 
        data_agent, 
        expected_answer, 
        params.critic_prompt,
        params.eval_id,
        params.run_timestamp
    )

    return output_row, run_steps


def _generate_answer(
    query: str,
    fabric_client: FabricOpenAI, 
    data_agent: FabricDataAgentManagement, 
    expected_answer: str, 
    critic_prompt: Optional[str],
    eval_id: str,
    run_timestamp: datetime
) -> Tuple[EvaluationResult, RunSteps]:
    """
    Generates the response for input query.

    Parameters
    ----------
    query : str
        Question from the input DataFrame.
    fabric_client: FabricOpenAI
        An instance of the fabric client to interact with Data Agent.
    data_agent: FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    expected_answer : str
        Expected answer from the input DataFrame.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.
    eval_id : str
        Unique id for the evaluation run.
    run_timestamp : datetime
        Timestamp indicating when the evaluation run started.

    Returns
    -------
    tuple[EvaluationResult, RunSteps]
        Formatted response of the Data Agent and run steps.
    """
    from fabric.dataagent.evaluation._thread import _get_steps

    # Unique id for each row in input dataset
    unique_id = str(uuid.uuid4())
    start_time = time.time()

    # Create thread with custom tag (uuid)
    thread = fabric_client.get_or_create_thread(unique_id)
    thread_id = thread.id

    # Generate answer for the input query
    message, run = _get_message(fabric_client, thread_id, query)

    # Construct the thread URL
    thread_url = _get_thread_url(thread_id, data_agent)

    run_steps = _get_steps(fabric_client, thread_id, run.id, unique_id)

    # Generate the prompt for evaluating the actual answer
    prompt = _generate_prompt(query, expected_answer, critic_prompt)

    # Generate answer for the evaluation prompt
    eval_message, eval_run = _get_message(fabric_client, thread_id, prompt)
    eval_message_low = eval_message.lower()
    score = False if "no" in eval_message_low else True if "yes" in eval_message_low else None
    
    end_time = time.time()
 
    evaluation_result = EvaluationResult(
        id=unique_id,
        evaluation_id=eval_id,
        thread_id=thread_id,
        run_timestamp=run_timestamp,
        question=query,
        expected_answer=expected_answer,
        actual_answer=message,
        execution_time_sec=round(end_time - start_time, 2),
        status=run.status,
        thread_url=thread_url,
        evaluation_judgement=score,
        evaluation_message=eval_message,
        evaluation_status=eval_run.status,
        evaluation_thread_url=thread_url
    )

    return evaluation_result, run_steps
