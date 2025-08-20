import re
import pandas as pd

import sqlparse
import teradataml as tdml

def query_change_case(query, case):
    """
    Change the case of alternate segments of a query string split by single quotes.

    Parameters:
    query (str): The input query string to be processed.
    case (str): The case to change the segments to. Should be 'lower' or 'upper'.

    Returns:
    str: The query string with alternate segments in the specified case.

    Raises:
    ValueError: If 'case' is not 'lower' or 'upper'.
    """
    # Split the query string by single quotes
    splitted_query = query.split("'")

    # Check the case parameter and apply the case change accordingly
    if case == 'lower':
        # Convert every alternate segment to lowercase
        splitted_query = [c.lower() if i % 2 == 0 else c for i, c in enumerate(splitted_query)]
    elif case == 'upper':
        # Convert every alternate segment to uppercase
        splitted_query = [c.upper() if i % 2 == 0 else c for i, c in enumerate(splitted_query)]
    else:
        # Raise an error if the case parameter is invalid
        raise ValueError("Invalid case argument. Use 'lower' or 'upper'.")

    # Join the segments back together with single quotes and return the result
    return "'".join(splitted_query)


def query_replace(query, word, substitute):
    """
    Replace occurrences of a specific word in alternating segments of a query string, delimited by single quotes.

    Parameters:
    query (str): The input query string to be processed.
    word (str): The word to be replaced within the segments.
    substitute (str): The word to substitute in place of the 'word' parameter.

    Returns:
    str: The query string with occurrences of 'word' replaced by 'substitute' in alternating segments.

    Raises:
    ValueError: If either 'query', 'word', or 'substitute' is not a string.
    """

    # Split the query string by single quotes
    splitted_query = query.split("'")

    # Replace the word in alternate segments
    splitted_query = [c.replace(word, substitute) if i % 2 == 0 else c for i, c in enumerate(splitted_query)]

    # Join the segments back together with single quotes and return the result
    return "'".join(splitted_query)


def _analyze_sql_query(sql_query):
    """
    Analyzes a SQL query and extracts table and view names categorized as 'source' and 'target'.

    This function takes a SQL query as input, removes comments from the query, and then identifies
    tables and views mentioned in various SQL components such as CREATE TABLE, INSERT INTO, CREATE VIEW,
    and SELECT statements. The identified table and view names are categorized into 'source' and 'target',
    representing the tables/views that are being referenced and the ones that are being created or inserted into.

    Args:
        sql_query (str): The SQL query to be analyzed.

    Returns:
        dict: A dictionary containing two lists - 'source' and 'target', where 'source' contains the
        table and view names being referenced in the query, and 'target' contains the table and view names
        being created or inserted into in the query. The names are normalized with double quotes for
        consistency and may include schema references.
    """

    def find_in_with_statement(sql_text):
        """
        Extracts terms from a SQL text that are followed by 'AS ('.

        Args:
            sql_text (str): The SQL text to be searched.

        Returns:
            list: A list of terms that are followed by 'AS ('
        """
        # Regex pattern to find ', term AS ('
        # It looks for a comma, optional whitespace, captures a word (term), followed by optional whitespace, 'AS', whitespace, and an opening parenthesis
        pattern = r'WITH\s*(\w+)\s+AS\s+\('

        # Find all occurrences of the pattern
        terms = re.findall(pattern, sql_text, re.IGNORECASE)

        pattern = r',\s*(\w+)\s+AS\s+\('

        # Find all occurrences of the pattern
        terms = terms + re.findall(pattern, sql_text, re.IGNORECASE)

        terms = [t.split(' ')[0] for t in terms]
        return terms

    def remove_sql_comments(sql_query):
        # Remove single line comments
        sql_query = re.sub(r'--.*', '', sql_query)

        # Remove multi-line comments
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)

        return sql_query

    # we remove the comments from the query
    sql_query = remove_sql_comments(sql_query)

    # Regular expression patterns for different SQL components
    create_table_pattern = r'CREATE\s+TABLE\s+([\w\s\.\"]+?)\s+AS'
    insert_into_pattern = r'INSERT\s+INTO\s+([\w\s\.\"]+?)'
    create_view_pattern = r'(CREATE|REPLACE)\s+VIEW\s+([\w\s\.\"]+?)\s+AS'
    #select_pattern = r'(FROM|JOIN|LEFT\sJOIN|RIGHT\sJOIN)\s+([\w\s\.\"]+?)(?=\s*(,|\s+GROUP|$|WHERE|PIVOT|UNPIVOT|UNION|ON|\)|\s+AS))'
    select_pattern = r'(\bFROM\b|LEFT\s+JOIN|RIGHT\s+JOIN|\bJOIN\b)\s+([\w\s\.\"]+?)(?=\s*(,|\bUNION\b|\bFULL\b|\bJOIN\b|\bLEFT\b|\bRIGHT\b|\bGROUP\b|\bQUALIFY\b|\bQUALIFY\b|\bWHERE\b|\bPIVOT\b|\bUNPIVOT\b|\bUNION\b|\bON\b|\bAS\b|$|\)))'
    select_pattern = r'(\bFROM\b|CROSS\s+JOIN|FULL\sOUTER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|\bJOIN\b)\s+([\w\s\.\"]+?)(?=\s*(,|\bUNION\b|\bFULL\b|\bJOIN\b|\bLEFT\b|\bRIGHT\b|\bGROUP\s+BY\b|\bQUALIFY\b|\bHAVING\b|\bWHERE\b|\bPIVOT\b|\bUNPIVOT\b|\bUNION\b|\bUNION\s+ALL\b|\bINTERSECT\b|\bMINUS\b|\bEXCEPT\b|\bON\b|\bAS\b|$|\)))'
    select_pattern = r'(\bFROM\b|\bON\b|CROSS\s+JOIN|FULL\sOUTER\s+JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|\bJOIN\b)\s+([\w\s\.\"]+?)(?=\s*(,|\bUNION\b|\bINNER\b|\bCROSS\b|\bFULL\b|\bJOIN\b|\bLEFT\b|\bRIGHT\b|\bGROUP\s+BY\b|\bQUALIFY\b|\bHAVING\b|\bWHERE\b|\bPIVOT\b|\bUNPIVOT\b|\bUNION\b|\bUNION\s+ALL\b|\bINTERSECT\b|\bMINUS\b|\bEXCEPT\b|\bON\b|\bAS\b|$|\)))'

    # select_pattern2 =  r'(FROM|JOIN)\s+([\w\s\.\"]+?)(?=\s*(,|group|$|where|pivot|unpivot|\)|AS))'



    # Find all matches in the SQL query for each pattern
    create_table_matches = re.findall(create_table_pattern, sql_query, re.IGNORECASE)
    insert_into_matches = re.findall(insert_into_pattern, sql_query, re.IGNORECASE)
    create_view_matches = re.findall(create_view_pattern, sql_query, re.IGNORECASE)
    select_matches = re.findall(select_pattern, sql_query, re.IGNORECASE)

    # select_matches2 = re.findall(select_pattern2, sql_query, re.IGNORECASE)

    # Extract the actual table or view name from the match tuples
    create_table_matches = [match[0] if match[0] else match[1] for match in create_table_matches]
    insert_into_matches = [match[0] if match[0] else match[1] for match in insert_into_matches]
    create_view_matches = [match[1] if match[0] else match[1] for match in create_view_matches]
    with_matches = [x.lower() for x in find_in_with_statement(sql_query)]
    select_matches = [match[1] for match in select_matches]
    # select_matches2 = [match[0] for match in select_matches2]

    table_names = {
        'source': [],
        'target': []
    }

    # Categorize the matched tables and views into 'source' or 'target'
    table_names['target'].extend(create_table_matches)
    table_names['target'].extend(insert_into_matches)
    table_names['target'].extend(create_view_matches)
    table_names['source'].extend(select_matches)
    # table_names['source'].extend(select_matches2)

    # Remove duplicate table and view names
    table_names['source'] = list(set(table_names['source']))
    table_names['target'] = list(set(table_names['target']))

    correct_source = []
    for target in table_names['source']:
        if '"' not in target:
            if ' ' in target:
                target = target.split(' ')[0]
            if target.lower() not in with_matches:
                correct_source.append('.'.join(['"' + t + '"' for t in target.split('.')]))
        else:
            if target.lower() not in with_matches:
                correct_source.append(target)

    correct_target = []
    for target in table_names['target']:
        if '"' not in target:
            if ' ' in target:
                target = target.split(' ')[0]
            if target.lower() not in with_matches:
                correct_target.append('.'.join(['"' + t + '"' for t in target.split('.')]))
        else:
            if target.lower() not in with_matches:
                correct_target.append(target)

    table_names['source'] = [c.split(' ')[0] for c in correct_source]
    table_names['target'] = [c.split(' ')[0] for c in correct_target]

    return table_names


def analyze_sql_query(sql_query, df=None, target=None, root_name='ml__', node_info=None):
    """
    Analyzes a SQL query and its relationships to target tables/views.

    This function takes a SQL query as input and extracts source tables/views mentioned in the query.
    It also allows for recursively analyzing TeradataML (tdml) views to identify relationships and dependencies
    between the source tables/views and target tables/views. The analysis results are accumulated in a TeradataML
    DataFrame (df) and a list of node information (node_info) to capture target, columns, and query details.

    Args:
        sql_query (str): The SQL query to be analyzed.
        df (teradataml.DataFrame, optional): An existing TeradataML DataFrame to append the analysis results to.
            Default is None.
        target (str, optional): The target table/view where the query is directed. Default is None.
        root_name (str, optional): A root name identifier for filtering TeradataML views. Default is 'ml__'.
        node_info (list, optional): A list of dictionaries containing node information. Default is None.

    Returns:
        tuple: A tuple containing the analysis results - a TeradataML DataFrame (df) containing source and target
        table/view relationships, and a list of node information (node_info) capturing details about each node
        in the analysis.

    Note:
        - The 'target' parameter should be specified when analyzing queries directed at a specific table/view.
        - When analyzing TeradataML views, the function recursively extracts and analyzes the view's definition.

    Example:
        To analyze a SQL query:
        >>> result_df, result_node_info = analyze_sql_query(sql_query)

        To analyze a SQL query with a specific target table/view:
        >>> result_df, result_node_info = analyze_sql_query(sql_query, target='my_target_table')

        To analyze a SQL query and append results to an existing TeradataML DataFrame:
        >>> existing_df = teradataml.DataFrame()
        >>> result_df, result_node_info = analyze_sql_query(sql_query, df=existing_df)

    """

    # Extract source and potential target tables/views from the provided SQL query
    table_name = _analyze_sql_query(sql_query)


    # Extract node informations
    if node_info is None and target is None:
        node_info = [{'target': target, 'columns': tdml.DataFrame.from_query(sql_query).columns, 'query': sql_query}]
    elif node_info is None:
        if '"' not in target:
            target = '.'.join(['"' + t + '"' for t in target.split('.')])

        node_info = [{'target': target, 'columns': tdml.DataFrame(target).columns, 'query': sql_query}]
    else:
        if '"' not in target:
            target = '.'.join(['"' + t + '"' for t in target.split('.')])

        node_info = node_info + [{'target': target, 'columns': tdml.DataFrame(target).columns, 'query': sql_query}]

    # If df is not provided, initialize it; else append to the existing df
    table_name['target'] = [target] * len(table_name['source'])
    if df is None:
        df = pd.DataFrame(table_name)
    else:
        df = pd.concat([df, pd.DataFrame(table_name)], ignore_index=True)

    # Check for teradataml views in the source and recursively analyze them
    for obj in table_name['source']:
        if root_name == None or root_name.lower() in obj.lower():

            # It's a teradataml view. Fetch its definition.
            try:
                sql_query_ = tdml.execute_sql(f"SHOW VIEW {obj}").fetchall()[0][0].replace('\r', '\n').replace('\t', '\n')
            except Exception as e:
                pass
            try:
                # Recursively analyze the view definition to get its relationships
                df, node_info = analyze_sql_query(
                    sql_query_,
                    df,
                    target    = obj,
                    node_info = node_info,
                    root_name = root_name
                )

            except:
                pass

        else:
            pass

    return df, node_info

def replace_case_insensitive(query, old_name, new_name):
    """Replace column or table name in SQL query using case-insensitive matching."""
    pattern = r'\b' + re.escape(old_name) + r'\b'
    return re.sub(pattern, new_name, query, flags=re.IGNORECASE)
