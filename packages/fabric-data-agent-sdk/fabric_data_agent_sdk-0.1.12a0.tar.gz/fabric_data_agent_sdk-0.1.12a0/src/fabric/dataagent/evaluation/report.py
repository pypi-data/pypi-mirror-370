"""
Reporting and analysis functions for evaluation results.
"""
from IPython.display import display, HTML
from pandas.io.formats.style import Styler
from typing import Optional
import pandas as pd
import numpy as np

from fabric.dataagent.evaluation._storage import _get_data
from fabric.dataagent.evaluation._display import _display_styled_html, _extract_failed_thread_info, _markdown_formatter


def get_evaluation_details(
    evaluation_id: str,
    table_name: str = 'evaluation_output',
    get_all_rows: bool = False,
    verbose: bool = False,
):
    """
    Get evaluation details of a single run.

    Parameters
    ----------
    evaluation_id : str
        Unique id for the evaluation run.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    get_all_rows : bool, optional
        Flag to get all the rows for an evaluation. Default to False, which returns only failed evaluation rows.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with single evaluation details.
    """

    # Get the delta table
    df = _get_data(table_name)

    # Return if table is not found
    if df is None:
        return None

    df = df.sort_values(['question']).reset_index(drop=True)

    filtered_df = df[df["evaluation_id"] == evaluation_id]
    # Filter for only failed rows if get_all_rows is False
    if not get_all_rows:
        filtered_df = filtered_df[(filtered_df["evaluation_judgement"] == False) | (pd.isna(filtered_df["evaluation_judgement"]))]

    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.columns.name = 'index'
    if verbose:
        if filtered_df.empty:
            display(HTML('<b>There are no failed evaluation rows.</b> Use <i>get_all_rows</i> parameter as <i>True</i> to display all the evaluation rows.'))
            return filtered_df
        
        selected_cols_df = filtered_df[
            [
                "question",
                "expected_answer",
                "actual_answer",
                "evaluation_judgement",
                "thread_id",
                "thread_url"
            ]
        ]

        thread_urls = []
        for index, row in selected_cols_df.iterrows():
            thread_urls.append(
                f'[{row["thread_id"]}]({row["thread_url"]})'
            )

        # Make a copy once
        selected_cols_df = selected_cols_df.copy()

        # Assign columns in a vectorized way
        selected_cols_df['thread_url'] = thread_urls
        selected_cols_df['evaluation_judgement'] = selected_cols_df['evaluation_judgement'].fillna("Unclear")
        selected_cols_df = selected_cols_df.drop(columns=['thread_id'])
        styled_cols_df = selected_cols_df.style.format(
            {
                "question": _markdown_formatter,
                "expected_answer": _markdown_formatter,
                "actual_answer": _markdown_formatter,
                "thread_url": _markdown_formatter
            },
            escape="html"
        )

        _display_styled_html(styled_cols_df)

    return filtered_df


def get_evaluation_summary(
    table_name: str = 'evaluation_output', verbose: bool = False
):
    """
    Overall summary of an evaluation stored in the delta table.

    Parameters
    ----------
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with summary details.
    """

    # Get the delta table
    df = _get_data(table_name)

    # Return if table is not found
    if df is None:
        return None

    # Calculate the percentage of True values in the DataFrame
    eval_percentage = (df['evaluation_judgement'].mean()) * 100

    # Group by timestamp and count the occurrences of True, False, and None in the 'evaluation_judgement' column
    grouped_df = (
        df.groupby('evaluation_id')['evaluation_judgement']
        .value_counts(dropna=False)
        .unstack(fill_value=0)
    )

    # Reindex to ensure True, False, None columns are included even if their count is zero
    grouped_df = grouped_df.reindex(columns=[True, False, np.nan], fill_value=0)

    # Calculate the percentage of True values per evaluation
    grouped_df['%'] = ((grouped_df[True] / grouped_df.sum(axis=1)) * 100).round(1)

    # Reset index and rename the columns in the DataFrame
    grouped_df = grouped_df.reset_index().rename(
        columns={True: "T", False: "F", np.nan: "?"}
    )

    grouped_df.columns.name = 'index'

    if verbose:
        eval_string = f"<h5>Evaluation judgement in percentage: {int(eval_percentage) if eval_percentage.is_integer() else round(eval_percentage, 1)}%</h5>"
        display(HTML(eval_string))
        styled_df = grouped_df.style.format(
            {
                '%': '{:.1f}'
            },
            escape="html"
        )
        _display_styled_html(styled_df)

    return grouped_df


def get_evaluation_summary_per_question(
    evaluation_id: Optional[str] = None,
    table_name: str = 'evaluation_output',
    verbose: bool = False
):
    """
    Summary of evaluation results per question for a specific evaluation_id, showing the percentage of True for each question based on all its variations.

    Parameters
    ----------
    evaluation_id : str, optional
        Unique id for the evaluation run. If None, it returns the summary for all evaluations.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with summary details per question for the given evaluation_id.
    """
    df = _get_data(table_name)
    if df is None or 'question' not in df.columns:
        return None
    
    if evaluation_id is not None:
        df = df[df['evaluation_id'] == evaluation_id]
    
    if df.empty:
        return None
    
    # Group by question and count the occurrences of True, False, and None in the 'evaluation_judgement' column
    # and calculate the percentage of True values per question
    grouped_df = (
        df.groupby('question')['evaluation_judgement']
        .value_counts(dropna=False)
        .unstack(fill_value=0)
    )
    grouped_df = grouped_df.reindex(columns=[True, False, np.nan], fill_value=0)
    grouped_df['%'] = ((grouped_df[True] / grouped_df.sum(axis=1)) * 100).round(1)
    grouped_df = grouped_df.reset_index().rename(
        columns={True: "T", False: "F", np.nan: "?"}
    )

    # Extract failed records for each question
    # and format the thread URLs
    failed_records = (
        df[(df["evaluation_judgement"] == False) | (pd.isna(df["evaluation_judgement"]))]
        .groupby("question")
        .apply(lambda x: x.to_dict(orient="records"))
    )

    if failed_records.empty:
        failed_records = pd.DataFrame({"question": [], "failed_threads": [], "failed_thread_urls": []})
    else:
        failed_records = (
            failed_records
            .reset_index()
            .rename(columns={0: "failed_records"})
        )

        failed_records[["failed_threads", "failed_thread_urls"]] = failed_records["failed_records"].apply(
            _extract_failed_thread_info
        ).apply(pd.Series)

    merged_df = grouped_df.merge(failed_records, on="question", how="left")
    merged_df['failed_threads'] = merged_df['failed_threads'].fillna("No failed records")
    merged_df.columns.name = 'index'

    if verbose:
        display(HTML(f"<h5>Evaluation summary per question:</h5>"))
        display_cols = ['T', 'F', '?', '%', 'failed_threads', 'question']
        styled_df = merged_df[display_cols].style.format(
            {
                'question': _markdown_formatter,
                'failed_threads': _markdown_formatter,
                '%': '{:.1f}'
            },
            escape="html"
        )
        _display_styled_html(styled_df)

    df_cols = ['T', 'F', '?', '%', 'failed_thread_urls', 'question']
    df = merged_df[df_cols]
    return df
