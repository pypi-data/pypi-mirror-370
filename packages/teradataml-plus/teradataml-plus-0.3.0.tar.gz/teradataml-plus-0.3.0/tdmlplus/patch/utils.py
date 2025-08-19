import sqlparse

def prettyprint_sql(query: str) -> None:
    """
    Pretty-print a SQL query with indentation and uppercase keywords.

    Args:
        query (str): The raw SQL query string to format and print.

    Returns:
        None
    """
    print(sqlparse.format(
        query,
        reindent=True,
        keyword_case='upper'
    ))
