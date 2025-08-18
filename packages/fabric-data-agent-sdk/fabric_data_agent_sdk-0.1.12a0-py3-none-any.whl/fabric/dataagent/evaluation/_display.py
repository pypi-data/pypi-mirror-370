"""
Functions for formatting and displaying evaluation results.
"""
import pandas as pd
from pandas.io.formats.style import Styler
from IPython.display import display


def _markdown_formatter(text):
    """ Convert text to HTML using markdown2.
    Parameters 
    ----------
    text : str
        The text to convert.
    """
    import markdown2

    if pd.isna(text):
        return ""
    return markdown2.markdown(text)


def _sql_formatter(text):
    """ Convert SQL text to HTML using markdown2 with fenced code blocks.
    Parameters
    ----------
    text : str
        The SQL text to convert.
    """
    import markdown2

    if pd.isna(text):
        return ""
    return markdown2.markdown(f"```sql\n{text}\n```", extras=["fenced-code-blocks"])


def _display_styled_html(styler: Styler):
    """
    Display styled html of a Dataframe.

    Parameters
    ----------
    styler : Styler
        A pandas Styler object to style.
    """

    # Convert DataFrame to HTML and add inline CSS to enforce left alignment
    styled_html = styler \
        .set_properties(**{'text-align': 'left'}) \
        .set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'left')]}]
        )

    display(styled_html)


def _extract_failed_thread_info(records):
    """
    Extracts and formats thread URLs from a list of record dictionaries.
    Iterates over the provided records, checks for the presence of a non-null "thread_url" key,
    and constructs an HTML string of numbered links as well as a list of the URLs.
    
    Parameters
    ----------
    records: list of dict
        A list of dictionaries, each potentially containing a "thread_url" key.

    Returns
    -------
    tuple:
        hrefs: str
            An HTML string with numbered anchor tags linking to each thread URL.
        urls: list of str
            A list of thread URLs extracted from the records.
    """
    hrefs = ""
    urls = []
    for i, rec in enumerate(records):
        if pd.notna(rec.get("thread_url")):
            hrefs += f'[{i+1}]({rec["thread_url"]}) '
            urls.append(rec["thread_url"])

    return hrefs, urls
