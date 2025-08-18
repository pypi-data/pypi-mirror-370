"""
Unit tests for fabric.dataagent.evaluation._display
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pandas.io.formats.style import Styler

from fabric.dataagent.evaluation._display import (
    _markdown_formatter, _sql_formatter, _extract_failed_thread_info, _display_styled_html
)


def test_markdown_formatter():
    """Test _markdown_formatter function."""
    # Test with basic markdown
    result = _markdown_formatter("**Bold** and *italic*")
    assert "<strong>Bold</strong>" in result
    assert "<em>italic</em>" in result
    
    # Test with code
    result = _markdown_formatter("`code`")
    assert "<code>code</code>" in result
    
    # Test with link
    result = _markdown_formatter("[Link](https://example.com)")
    assert '<a href="https://example.com">Link</a>' in result
    
    # Test with None/NaN
    result = _markdown_formatter(pd.NA)
    assert result in ("", "<p></p>\n")
    
    # Test with empty string
    result = _markdown_formatter("")
    assert result in ("", "<p></p>\n")


def test_sql_formatter():
    """Test _sql_formatter function."""
    sql = "SELECT * FROM table WHERE id = 1"
    with patch("markdown2.markdown", side_effect=lambda x, **kwargs: x):
        result = _sql_formatter(sql)
        assert "```sql" in result
        assert sql in result

    # Test with None/NaN
    with patch("markdown2.markdown", return_value=""):
        result = _sql_formatter(pd.NA)
        assert result == ""

    # Test with empty string
    with patch("markdown2.markdown", return_value=""):
        result = _sql_formatter("")
        assert result == ""
        

def test_extract_failed_thread_info():
    """Test _extract_failed_thread_info function."""
    # Test with records containing thread_url
    records = [
        {"thread_url": "https://example.com/thread1", "other": "data"},
        {"thread_url": "https://example.com/thread2", "other": "data"}
    ]
    
    hrefs, urls = _extract_failed_thread_info(records)
    
    # Check hrefs
    assert "[1](https://example.com/thread1)" in hrefs
    assert "[2](https://example.com/thread2)" in hrefs
    
    # Check urls
    assert urls == ["https://example.com/thread1", "https://example.com/thread2"]
    
    # Test with some records missing thread_url
    records = [
        {"thread_url": "https://example.com/thread1", "other": "data"},
        {"other": "data"},  # No thread_url
        {"thread_url": None, "other": "data"},  # None thread_url
        {"thread_url": pd.NA, "other": "data"}  # NA thread_url
    ]
    
    hrefs, urls = _extract_failed_thread_info(records)
    
    # Check hrefs - should only have one item
    assert "[1](https://example.com/thread1)" in hrefs
    assert len(urls) == 1
    
    # Test with empty records
    hrefs, urls = _extract_failed_thread_info([])
    assert hrefs == ""
    assert urls == []
