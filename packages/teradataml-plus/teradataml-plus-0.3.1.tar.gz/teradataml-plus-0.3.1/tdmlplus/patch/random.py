from .. import tdml
from typing import Union, List, Optional
import numpy as np
import pandas as pd


def randn(num_rows=1000, num_cols=10, colnames=None, row_id=False):
    """
    Generate a Teradata DataFrame with random standard (Mean=0, VAR=SD=1) normally distributed columns.

    Parameters
    ----------
    num_rows : int, optional, default = 100
        Number of rows to generate.

    num_cols : int, optional, default = 1
        Number of random normal columns (ignored if `colnames` is provided).

    colnames : list of str, optional
        Custom column names. If given, overrides `num_cols`.

    row_id : bool, optional, default = False
        Whether to include a unique row ID ("row_id" )column using TD_FillRowID.

    Returns
    -------
    teradataml DataFrame
        A DataFrame with normally distributed random columns (and optional row ID).
    """
    if colnames:
        cols = colnames
    else:
        cols = [f"x_{i}" for i in range(num_cols)]

    gen_exprs = []
    for col in cols:
        expr = (
            "SQRT(-2.0 * LN(CAST((RANDOM(-2147483648, 2147483647)+2147483648) AS FLOAT)/4294967295))"
            "* COS(2.0 * 3.14159265358979323846 * CAST((RANDOM(-2147483648, 2147483647)+2147483648) AS FLOAT)/4294967295)"
        )
        gen_exprs.append(f"{expr} AS {col}")

    gen_exprs = '\n, '.join(gen_exprs)
    inner_query = f"SELECT myone FROM (SELECT 1 as myone) t SAMPLE WITH REPLACEMENT {num_rows}"
    main_query = f"SELECT \n{gen_exprs} \nFROM ({inner_query}) t"

    if row_id:
        final_query = f'''
        SELECT row_id, {", ".join(cols)}  FROM TD_FillRowID (
            ON ({main_query}) AS InputTable
            USING RowIDColumnName ('row_id')
        ) AS dt
        '''
    else:
        final_query = main_query

    return tdml.DataFrame.from_query(final_query)




def _generate_sql_for_correlated_normals(
    correlation_matrix: Union[np.ndarray, pd.DataFrame],
    n_rows: int,
    column_names: Optional[List[str]] = None
) -> str:
    """
    Generate a SQL query to simulate correlated normal variables based on a given correlation matrix.

    Args:
        correlation_matrix (np.ndarray or pd.DataFrame): Correlation matrix specifying relationships.
        n_rows (int): Number of rows to generate.
        column_names (List[str], optional): Names of the output columns. Required if correlation_matrix is a NumPy array.

    Returns:
        str: A SQL query string that generates the correlated normal data.
    """
    if isinstance(correlation_matrix, pd.DataFrame):
        column_names = correlation_matrix.columns
        correlation_matrix = correlation_matrix.values
    else:
        assert column_names is not None, "column_names must be provided when using a NumPy array"

    # Cholesky decomposition
    L = np.linalg.cholesky(correlation_matrix)
    n = L.shape[0]

    # SQL for independent standard normal variables (Box-Muller method)
    independent_vars_sql = ",\n        ".join([
        f"sqrt(-2.0*ln(CAST((RANDOM(-2147483648, 2147483647)+2147483648) AS FLOAT)/4294967295))"
        f"*cos(2.0*3.14159265358979323846*CAST((RANDOM(-2147483648, 2147483647)+2147483648) AS FLOAT)/4294967295) AS z_{i+1}_normal"
        for i in range(n)
    ])

    # SQL for correlated variables via linear combination
    sql_queries = []
    for i in range(n):
        terms = [f"{L[i, j]:.6f} * z_{j+1}_normal" for j in range(n)]
        sql_queries.append(f"({ ' + '.join(terms) }) AS {column_names[i]}")

    select_clause = ",\n       ".join(sql_queries)

    full_sql = f"""
SELECT
       {select_clause}
FROM
    (SELECT 
        {independent_vars_sql}
    FROM
        (
        SELECT myone
        FROM (SELECT 1 AS myone) t
        SAMPLE WITH REPLACEMENT {n_rows}
        ) t
    ) t"""

    return full_sql


def correlated_normals(
    DF_base: tdml.DataFrame,
    num_rows: int = 100000
) -> tdml.DataFrame:
    """
    Generate a synthetic DataFrame with multivariate normal data that matches
    the correlation structure of the input DataFrame.

    Args:
        DF_base (tdml.DataFrame): Base DataFrame whose correlation structure will be mimicked.
        num_rows (int, optional): Number of synthetic rows to generate. Default is 100000.

    Returns:
        tdml.DataFrame: A new DataFrame with simulated correlated normal variables.
    """
    df_corr = DF_base.corr().sort("rownum").to_pandas().reset_index()
    df_corr_sql = df_corr.drop(columns=["rownum"]).set_index("rowname")
    myquery = _generate_sql_for_correlated_normals(df_corr_sql, num_rows)
    DF_synth = tdml.DataFrame.from_query(myquery)
    return DF_synth