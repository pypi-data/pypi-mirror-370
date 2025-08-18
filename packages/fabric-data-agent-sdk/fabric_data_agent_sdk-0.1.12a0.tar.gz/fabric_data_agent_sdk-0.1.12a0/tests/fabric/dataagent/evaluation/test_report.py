"""
Unit tests for fabric.dataagent.evaluation.report
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from fabric.dataagent.evaluation.report import (
    get_evaluation_details, get_evaluation_summary, get_evaluation_summary_per_question
)

def check_percentage_column(result):
    # Percentage column might be float or string type
    assert "%" in result.columns  # Percentage column
    # Additionally, check if the values in the '%' column are in expected range
    if result["%"].dtype == float:
        assert result["%"].notna().all()  # No NaN values
        assert (result["%"] >= 0).all()  # No negative values
    elif result["%"].dtype == object:
        # If the column is of object type, they might be strings
        assert all(
            pd.to_numeric(result["%"].str.replace(',', '.'), errors='coerce').notna()
        )  # Convert to numeric and check for NaN
        assert (result["%"].str.replace(',', '.').astype(float) >= 0).all()  # No negative values


@pytest.fixture
def sample_evaluation_output():
    """Sample evaluation output DataFrame."""
    return pd.DataFrame({
        "evaluation_id": ["eval1", "eval1", "eval1", "eval2", "eval2"],
        "question": ["Q1", "Q2", "Q3", "Q1", "Q2"],
        "expected_answer": ["A1", "A2", "A3", "A1", "A2"],
        "actual_answer": ["A1", "Wrong", "A3", "A1", "A2"],
        "evaluation_judgement": [True, False, True, True, True],
        "thread_id": ["t1", "t2", "t3", "t4", "t5"],
        "thread_url": ["url1", "url2", "url3", "url4", "url5"]
    })


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_details_all_rows(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_details with get_all_rows=True."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_details(
        evaluation_id="eval1", 
        get_all_rows=True,
        verbose=False
    )
    
    # Assert
    assert len(result) == 3  # All rows for eval1
    assert all(result["evaluation_id"] == "eval1")
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_details_failed_rows(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_details with get_all_rows=False (only failed rows)."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_details(
        evaluation_id="eval1", 
        get_all_rows=False,
        verbose=False
    )
    
    # Assert
    assert len(result) == 1  # Only the failed row for eval1
    assert result.iloc[0]["question"] == "Q2"
    assert result.iloc[0]["evaluation_judgement"] == False
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_details_no_data(mock_get_data):
    """Test get_evaluation_details when no data is available."""
    # Setup
    mock_get_data.return_value = None
    
    # Execute
    result = get_evaluation_details(
        evaluation_id="eval1", 
        verbose=False
    )
    
    # Assert
    assert result is None
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_details_custom_table(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_details with custom table name."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_details(
        evaluation_id="eval1", 
        table_name="custom_table",
        verbose=False
    )
    
    # Assert
    mock_get_data.assert_called_once_with("custom_table")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_summary."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_summary(verbose=False)
    
    # Assert
    assert len(result) == 2  # Two evaluation_ids
    assert set(result.index) == {0, 1}
    assert "T" in result.columns  # True column
    assert "F" in result.columns  # False column
    def check_percentage_column(result):
        # Percentage column might be float or string type
        assert "%" in result.columns  # Percentage column
        # Additionally, check if the values in the '%' column are in expected range
        if result["%"].dtype == float:
            assert result["%"].notna().all()  # No NaN values
            assert (result["%"] >= 0).all()  # No negative values
        elif result["%"].dtype == object:
            # If the column is of object type, they might be strings
            assert all(
                pd.to_numeric(result["%"].str.replace(',', '.'), errors='coerce').notna()
            )  # Convert to numeric and check for NaN
            assert (result["%"].str.replace(',', '.').astype(float) >= 0).all()  # No negative values
    check_percentage_column(result)
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_no_data(mock_get_data):
    """Test get_evaluation_summary when no data is available."""
    # Setup
    mock_get_data.return_value = None
    
    # Execute
    result = get_evaluation_summary(verbose=False)
    
    # Assert
    assert result is None
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_custom_table(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_summary with custom table name."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_summary(
        table_name="custom_table",
        verbose=False
    )
    
    # Assert
    mock_get_data.assert_called_once_with("custom_table")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_summary_per_question."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_summary_per_question(
        evaluation_id="eval1",
        verbose=False
    )
    
    # Assert
    assert len(result) == 3  # Three questions for eval1
    assert set(result["question"]) == {"Q1", "Q2", "Q3"}
    assert "T" in result.columns  # True column
    assert "F" in result.columns  # False column
    check_percentage_column(result)
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_all_evaluations(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_summary_per_question with no evaluation_id (all evaluations)."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_summary_per_question(
        evaluation_id=None,
        verbose=False
    )
    
    # Assert
    assert len(result) == 3  # Three unique questions across all evaluations
    assert set(result["question"]) == {"Q1", "Q2", "Q3"}
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_no_data(mock_get_data):
    """Test get_evaluation_summary_per_question when no data is available."""
    # Setup
    mock_get_data.return_value = None
    
    # Execute
    result = get_evaluation_summary_per_question(
        evaluation_id="eval1",
        verbose=False
    )
    
    # Assert
    assert result is None
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_no_matching_eval(mock_get_data, sample_evaluation_output):
    """Test get_evaluation_summary_per_question with non-existing evaluation_id."""
    # Setup
    mock_get_data.return_value = sample_evaluation_output
    
    # Execute
    result = get_evaluation_summary_per_question(
        evaluation_id="non_existing_eval",
        verbose=False
    )
    
    # Assert
    assert result is None  # No matching data
    mock_get_data.assert_called_once_with("evaluation_output")


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_details_all_success(mock_get_data):
    # All rows are successful for eval1
    df = pd.DataFrame({
        "evaluation_id": ["eval1", "eval1"],
        "question": ["Q1", "Q2"],
        "expected_answer": ["A1", "A2"],
        "actual_answer": ["A1", "A2"],
        "evaluation_judgement": [True, True],
        "thread_id": ["t1", "t2"],
        "thread_url": ["url1", "url2"]
    })
    mock_get_data.return_value = df
    result = get_evaluation_details(evaluation_id="eval1", get_all_rows=False, verbose=False)
    assert result.empty is True or len(result) == 0


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_all_success(mock_get_data):
    # All rows are successful for eval1
    df = pd.DataFrame({
        "evaluation_id": ["eval1", "eval1"],
        "question": ["Q1", "Q2"],
        "expected_answer": ["A1", "A2"],
        "actual_answer": ["A1", "A2"],
        "evaluation_judgement": [True, True],
        "thread_id": ["t1", "t2"],
        "thread_url": ["url1", "url2"]
    })
    mock_get_data.return_value = df
    result = get_evaluation_summary_per_question(evaluation_id="eval1", verbose=False)
    assert set(result['question']) == {"Q1", "Q2"}
    assert all(result['F'] == 0)
    assert all(result['%'] == 100.0)


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_nan_judgement(mock_get_data):
    # Some rows have NaN for evaluation_judgement
    df = pd.DataFrame({
        "evaluation_id": ["eval1", "eval1"],
        "question": ["Q1", "Q2"],
        "expected_answer": ["A1", "A2"],
        "actual_answer": ["A1", "A2"],
        "evaluation_judgement": [float('nan'), False],
        "thread_id": ["t1", "t2"],
        "thread_url": ["url1", "url2"]
    })
    mock_get_data.return_value = df
    result = get_evaluation_summary_per_question(evaluation_id="eval1", verbose=False)
    assert set(result['question']) == {"Q1", "Q2"}
    assert any(result['?'] > 0)


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_empty_failed_records(mock_get_data):
    # No failed records for any question
    df = pd.DataFrame({
        "evaluation_id": ["eval1"],
        "question": ["Q1"],
        "expected_answer": ["A1"],
        "actual_answer": ["A1"],
        "evaluation_judgement": [True],
        "thread_id": ["t1"],
        "thread_url": ["url1"]
    })
    mock_get_data.return_value = df
    result = get_evaluation_summary_per_question(evaluation_id="eval1", verbose=False)
    assert 'failed_thread_urls' in result.columns
    assert pd.isna(result['failed_thread_urls'].iloc[0])


@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_details_column_name_preserved(mock_get_data):
    # Check that columns.name is set to 'index'
    df = pd.DataFrame({
        "evaluation_id": ["eval1"],
        "question": ["Q1"],
        "expected_answer": ["A1"],
        "actual_answer": ["A1"],
        "evaluation_judgement": [True],
        "thread_id": ["t1"],
        "thread_url": ["url1"]
    })
    mock_get_data.return_value = df
    result = get_evaluation_details(evaluation_id="eval1", get_all_rows=True, verbose=False)
    assert hasattr(result.columns, 'name')
    assert result.columns.name == 'index'


@patch('fabric.dataagent.evaluation.report._get_data')
@patch('fabric.dataagent.evaluation.report.display')
@patch('fabric.dataagent.evaluation.report.HTML')
@patch('fabric.dataagent.evaluation.report._display_styled_html')
def test_get_evaluation_details_verbose_with_failed(mock_display_styled, mock_html, mock_display, mock_get_data, sample_evaluation_output):
    # There is a failed row for eval1
    mock_get_data.return_value = sample_evaluation_output
    result = get_evaluation_details(
        evaluation_id="eval1",
        get_all_rows=False,
        verbose=True
    )
    mock_display_styled.assert_called()
    assert not result.empty

@patch('fabric.dataagent.evaluation.report._get_data')
@patch('fabric.dataagent.evaluation.report.display')
@patch('fabric.dataagent.evaluation.report.HTML')
@patch('fabric.dataagent.evaluation.report._display_styled_html')
def test_get_evaluation_details_verbose_no_failed(mock_display_styled, mock_html, mock_display, mock_get_data, sample_evaluation_output):
    # All rows are successful for eval2
    mock_get_data.return_value = sample_evaluation_output
    result = get_evaluation_details(
        evaluation_id="eval2",
        get_all_rows=False,
        verbose=True
    )
    mock_display.assert_called()
    # The result should be empty, as there are no failed rows for eval2
    assert result.empty

@patch('fabric.dataagent.evaluation.report._get_data')
@patch('fabric.dataagent.evaluation.report.display')
@patch('fabric.dataagent.evaluation.report.HTML')
@patch('fabric.dataagent.evaluation.report._display_styled_html')
def test_get_evaluation_summary_verbose(mock_display_styled, mock_html, mock_display, mock_get_data, sample_evaluation_output):
    mock_get_data.return_value = sample_evaluation_output
    result = get_evaluation_summary(verbose=True)
    mock_display.assert_called()
    mock_display_styled.assert_called()
    assert not result.empty

@patch('fabric.dataagent.evaluation.report._get_data')
@patch('fabric.dataagent.evaluation.report.display')
@patch('fabric.dataagent.evaluation.report.HTML')
@patch('fabric.dataagent.evaluation.report._display_styled_html')
def test_get_evaluation_summary_per_question_verbose(mock_display_styled, mock_html, mock_display, mock_get_data, sample_evaluation_output):
    mock_get_data.return_value = sample_evaluation_output
    result = get_evaluation_summary_per_question(evaluation_id="eval1", verbose=True)
    mock_display.assert_called()
    mock_display_styled.assert_called()
    assert not result.empty

@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_missing_question_col(mock_get_data):
    df = pd.DataFrame({"evaluation_id": ["eval1"], "evaluation_judgement": [True]})
    mock_get_data.return_value = df
    result = get_evaluation_summary_per_question(evaluation_id="eval1", verbose=False)
    assert result is None

@patch('fabric.dataagent.evaluation.report._get_data')
def test_get_evaluation_summary_per_question_empty_df(mock_get_data):
    df = pd.DataFrame({"evaluation_id": [], "question": [], "evaluation_judgement": []})
    mock_get_data.return_value = df
    result = get_evaluation_summary_per_question(evaluation_id="eval1", verbose=False)
    assert result is None
