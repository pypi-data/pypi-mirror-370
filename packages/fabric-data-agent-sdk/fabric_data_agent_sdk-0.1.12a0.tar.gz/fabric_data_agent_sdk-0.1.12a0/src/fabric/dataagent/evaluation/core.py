"""
Core evaluation functionality for data agents.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from IPython.display import display, Markdown
from tqdm import tqdm
from typing import Optional

from fabric.dataagent.client import FabricDataAgentManagement
from fabric.dataagent.evaluation._storage import _save_output
from fabric.dataagent.evaluation._evaluation_runner import _evaluate_row
from fabric.dataagent.evaluation._utils import _add_data_agent_details
from fabric.dataagent.evaluation._models import EvaluationResult, RunSteps, EvaluationContext

import pandas as pd
import uuid

# Constants
DATA_AGENT_STAGE = "production"


def evaluate_data_agent(
    df: pd.DataFrame,
    data_agent_name: str,
    workspace_name: Optional[str] = None,
    table_name: str = 'evaluation_output',
    critic_prompt: Optional[str] = None,
    data_agent_stage: str = DATA_AGENT_STAGE,
    max_workers: int = 5,
    num_query_repeats: int = 1
):
    """
    API to evaluate the Data Agent. Returns the unique id for the evaluation run.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with question and expected_answer list.
    data_agent_name : str
        Name of the Data Agent.
    workspace_name : str, optional
        Workspace Name if Data Agent is in different workspace. Default to None.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.
    data_agent_stage : str, optional
        Data Agent stage ie., sandbox or production. Default to production.
    max_workers: int, optional
        Maximun worker nodes that need to run parallely. Default to 5.
    num_query_repeats: int, optional
        Number of times to evaluate each question. Default is 1.

    Returns
    -------
    str
        Unique id for the evaluation run.
    """

    output_rows = []
    output_steps = []
    run_timestamp = datetime.now().replace(tzinfo=None)
    # Unique id for each evaluation
    eval_id = str(uuid.uuid4())

    # Create Data Agent management
    data_agent = FabricDataAgentManagement(data_agent_name, workspace_name)

    # Prepare arguments for each row
    rows = df.to_dict(orient="records")
    futures = []
    failed_urls = []
    display_handle = display(Markdown(""), display_id=True)

    # Create an EvaluationContext instance
    eval_context = EvaluationContext(
        row={},  # Placeholder, will be updated for each row
        data_agent_name=data_agent_name,
        workspace_name=workspace_name,
        table_name=table_name,
        critic_prompt=critic_prompt,
        data_agent_stage=data_agent_stage,
        max_workers=max_workers,
        num_query_repeats=num_query_repeats,
        eval_id=eval_id,
        run_timestamp=run_timestamp
    )

    with ThreadPoolExecutor(max_workers=eval_context.max_workers) as executor:
        for row in rows:
            for _ in range(eval_context.num_query_repeats):
                # Create a copy of the evaluation context with the current row
                row_eval_context = eval_context.copy(update={"row": row})
                futures.append(
                    executor.submit(
                        _evaluate_row,
                        row_eval_context
                    )
                )
        for row in tqdm(as_completed(futures), total=len(futures)):
            output_row, output_step = row.result()
            output_rows.append(output_row.dict())
            output_steps.append(output_step.dict())
            if (
                pd.isna(output_row.evaluation_judgement)
                or output_row.evaluation_judgement is False
            ) and output_row.thread_url:
                failed_urls.append((output_row.thread_url, output_row.thread_id))
                bullet_list = "\n".join([
                    f"- [{thread_id}]({url})" if thread_id else f"- [{url}]({url})"
                    for url, thread_id in failed_urls
                ])
                if failed_urls:
                    display_handle.update(Markdown(f"**🔗Failed Thread(s):**\n{bullet_list}"))
                else:
                    display_handle.update(Markdown(""))

    # Sort output_rows so all variations for a question are together and in order
    df = pd.DataFrame(output_rows)
    df = df.sort_values(['question']).reset_index(drop=True)
    df['evaluation_judgement'] = df['evaluation_judgement'].astype('boolean')

    # Add configuration and data sources to the DataFrame
    df_data_agent = _add_data_agent_details(df, data_agent)

    # Saving the evaluation output to a file
    _save_output(df_data_agent, table_name)
    # Saving the evaluation output steps to a file
    _save_output(pd.DataFrame(output_steps), f"{table_name}_steps")

    return eval_id