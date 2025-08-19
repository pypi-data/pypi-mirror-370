import teradataml as tdml
from teradataml.options.display import display
import pandas as pd
import networkx as nx
from ._dataframe_lineage_utils import (analyze_sql_query, query_replace, query_change_case)
from collections import OrderedDict
from typing import Optional, Union, List, Iterable
from ._plotting_utils  import _hist
def corr(self, method: str = 'pearson') -> tdml.DataFrame:
    """
    Compute the correlation matrix of the DataFrame using VAL.

    Currently, only Pearson correlation is supported. Requires
    `val_install_location` to be set in `tdml.configure`.

    Args:
        method (str, optional): Correlation method. Must be 'pearson'.

    Returns:
        tdml.DataFrame: A DataFrame containing the correlation matrix.
    """
    assert method == "pearson", "only pearson is currently supported"
    assert tdml.configure.val_install_location not in ["", None], \
        "set val install location, e.g. `tdml.configure.val_install_location = 'val'`"

    DF_corrmatrix = tdml.valib.Matrix(
        data=self,
        columns=list(self.columns),
        type="COR"
    ).result

    return DF_corrmatrix



def show_CTE_query(self) -> str:
    """
    Generate a single CTE (Common Table Expression) SQL query
    representing the lineage of a teradataml DataFrame.

    Consolidates all intermediate transformations
    into a single SQL statement for deployment.

    Returns:
        str: Full SQL query with all transformations inlined as CTEs.
    """
    tddf = self
    view_name = "pipeline"
    tddf_columns = tddf.columns

    tddf._DataFrame__execute_node_and_set_table_name(tddf._nodeid, tddf._metaexpr)

    tddf_graph_, _ = analyze_sql_query(tddf.show_query(), target=tddf._table_name)

    tddf_graph = pd.DataFrame(
        [(s, t) for s, t in zip(tddf_graph_['source'], tddf_graph_['target']) if s != t],
        columns=['source', 'target']
    )

    dependency_graph = nx.DiGraph()
    dependency_graph.add_edges_from(zip(tddf_graph['source'], tddf_graph['target']))
    sorted_nodes = list(nx.topological_sort(dependency_graph))

    targets = []
    for x in sorted_nodes:
        parts = x.split('.')
        if len(parts) > 1 and (parts[1].upper().startswith('ML__') or parts[1].upper().startswith('"ML__')):
            targets.append(x)

    if len(targets) > 1:
        mapping = OrderedDict({n: f"{view_name}_step_{i}" for i, n in enumerate(targets)})
    elif len(targets) == 1:
        mapping = {tddf_graph['target'].values[0]: view_name}
    else:
        mapping = {tddf._table_name: view_name}

    all_queries = []
    for old_name, new_name in mapping.items():
        raw_query = tdml.execute_sql(f"SHOW VIEW {old_name}").fetchall()[0][0].replace('\r', '\n')
        query = query_change_case(raw_query, 'lower')
        query = query_replace(query, ' create view ', '')
        for old_sub, new_sub in mapping.items():
            query = query_change_case(query, 'upper').replace(old_sub.upper(), new_sub.upper())
        query = query.replace(" AS ", " AS (\n", 1) + "\n)"
        all_queries.append(query)

    combined_ctes = "\n\n,".join(all_queries)
    final_query = f"WITH {combined_ctes}\n\nSELECT * FROM {new_name}"
    return final_query


def deploy_CTE_view(
    self,
    view_name: str,
    schema_name: str = None,
    return_view_df: bool = False
) -> Optional[tdml.DataFrame]:
    """
    Deploy the DataFrame as a SQL view by materializing all transformations
    into a single CTE-based view.

    Args:
        view_name (str): Name of the resulting view.
        schema_name (str, optional): Schema to place the view in.
        return_view_df (bool, optional): If True, return a DataFrame backed by the created view.

    Returns:
        Optional[tdml.DataFrame]: A new DataFrame referencing the view if return_view_df is True, else None.
    """
    assert view_name is not None
    my_CTE_query = self.show_CTE_query()
    full_obj_name = f"{schema_name}.{view_name}" if schema_name else view_name

    tdml.execute_sql(f"CREATE VIEW {full_obj_name} AS {my_CTE_query}")

    if return_view_df:
        return tdml.DataFrame.from_query(f"SELECT * FROM {full_obj_name}")

def easyjoin(
    self,
    other: tdml.DataFrame,
    on: Union[str, List[str]] = None,
    how: str = 'left',
    lsuffix: Optional[str] = None,
    rsuffix: Optional[str] = None
) -> tdml.DataFrame:
    """
    Perform a simplified join on identical column names with optional suffixes.

    This is a convenience wrapper around the standard join, assuming identity
    join columns and optional suffixes. One of lsuffix or rsuffix must remain None
    to identify which side's duplicate columns to drop post-join.

    Args:
        other (tdml.DataFrame): The other DataFrame to join with.
        on (str or List[str]): Column(s) to join on.
        how (str, optional): Type of join - 'left', 'right', 'inner', etc. Default is 'left'.
        lsuffix (str, optional): Suffix to apply to overlapping columns from the left DataFrame.
        rsuffix (str, optional): Suffix to apply to overlapping columns from the right DataFrame.

    Returns:
        tdml.DataFrame: The result of the join with duplicate join columns dropped.
    """
    assert isinstance(on, (str, list)), "`on` must be str or list of str"
    assert any(x is None for x in [lsuffix, rsuffix]), "Only one suffix should be set"

    drop_suffix = ""
    if all(x is None for x in [lsuffix, rsuffix]):
        if how == "right":
            lsuffix = "lt"
            drop_suffix = lsuffix
        else:
            rsuffix = "rt"
            drop_suffix = rsuffix

    join_cols = [on] if isinstance(on, str) else on
    columns_to_be_dropped = [f"{c}_{drop_suffix}" for c in join_cols]

    DF_result = self.join(other, on, how, lsuffix=lsuffix, rsuffix=rsuffix
                         ).drop(columns=columns_to_be_dropped)

    return DF_result

from typing import Optional

def top(self, n: int = 10, percentage: Optional[float] = None) -> tdml.DataFrame:
    """
    Return the first N rows or the top percentage of rows using Teradata's TOP clause.

    Leverages Teradata SQL `TOP`/`TOP ... PERCENT` for efficient limiting of result sets.

    References:
        - https://docs.teradata.com/r/Enterprise_IntelliFlex_VMware/SQL-Data-Manipulation-Language/SELECT-Statements/Select-List-Syntax/TOP-Clause
        - https://docs.teradata.com/r/Enterprise_IntelliFlex_VMware/SQL-Data-Manipulation-Language/Performance-Considerations/TOP-n-Row

    Args:
        n (int): Number of rows to return when `percentage` is None. Default is 10.
        percentage (float, optional): If provided, returns this percentage of rows
            where 0 < percentage <= 100. When set, `n` is ignored.

    Returns:
        tdml.DataFrame: A new DataFrame limited to the requested number or percentage of rows.
            If `percentage` is None, the metadata `_n_rows` is set to `n`.

    Raises:
        AssertionError: If `percentage` is not in the range (0, 100].
    """
    self._DataFrame__execute_node_and_set_table_name(self._nodeid, self._metaexpr)
    this_query = self.show_query()

    if percentage is None:
        new_prefix = f"select top {n} "
    else:
        assert 0.0 < percentage <= 100.0, "`percentage` must satisfy 0 < percentage ≤ 100"
        new_prefix = f"select top {percentage:.6f} percent "

    if this_query.lower().startswith("select "):
        new_query = new_prefix + this_query[7:]
    else:
        new_query = f"{new_prefix} * from ({this_query}) prev_query"

    new_DF = tdml.DataFrame.from_query(new_query)

    if percentage is None:
        new_DF._metaexpr._n_rows = n

    return new_DF


def new_head(self, n: int = display.max_rows, sort_index: bool = False) -> tdml.DataFrame:
    """
    Return the first `n` rows, optionally sorting by index.

    Delegates to `top(n)` for a fast limit when `sort_index` is False; otherwise
    delegates to `_head(n)` (slower, original `head()`, with sorting).

    Args:
        n (int): Number of rows to return. Defaults to `display.max_rows`.
        sort_index (bool): If True, return the head after sorting by index; if False,
            use a fast TOP-based limit.

    Returns:
        tdml.DataFrame: A DataFrame limited to the first `n` rows.

    Raises:
        AssertionError: If `n` is not a positive integer.
    """
    assert isinstance(n, int) and n > 0, "`n` must be a positive integer"
    return self.top(n) if not sort_index else self._head(n)


from typing import Iterable, Optional

def select_dtypes(
    self,
    include: Optional[Iterable[str]] = None,
    exclude: Optional[Iterable[str]] = None,
) -> tdml.DataFrame:
    """
    Return a view of the DataFrame with columns filtered by their dtypes.

    Allowed dtype labels:
    {'str', 'decimal.Decimal', 'datetime.date', 'datetime.datetime', 'bytes', 'int', 'float'}

    If both `include` and `exclude` are provided, columns must match `include`
    and will then be filtered out if they match `exclude`. Column order is preserved.

    Args:
        include (Iterable[str], optional): Dtype labels to include.
        exclude (Iterable[str], optional): Dtype labels to exclude.

    Returns:
        tdml.DataFrame: DataFrame containing only the selected columns.

    Raises:
        ValueError: If both `include` and `exclude` are None.
        AssertionError: If an unknown dtype label is supplied.
    """
    allowed = {
        'str', 'decimal.Decimal', 'datetime.date', 'datetime.datetime', 'bytes', 'int', 'float'
    }

    if include is None and exclude is None:
        raise ValueError("Provide at least one of `include` or `exclude`.")

    include_set = set(include) if include is not None else None
    exclude_set = set(exclude) if exclude is not None else None

    if include_set is not None:
        assert include_set.issubset(allowed), "Unknown dtype in `include`."
    if exclude_set is not None:
        assert exclude_set.issubset(allowed), "Unknown dtype in `exclude`."

    final_cols = []
    for col_name, dtype in self._column_names_and_types:
        if include_set is not None and dtype not in include_set:
            continue
        if exclude_set is not None and dtype in exclude_set:
            continue
        final_cols.append(col_name)

    return self.select(final_cols)

def select_tdtypes(
    self,
    include: Optional[Iterable[str]] = None,
    exclude: Optional[Iterable[str]] = None,
) -> tdml.DataFrame:
    """
    Return a view of the DataFrame with columns filtered by their Teradata types (tdtypes).

    Allowed tdtypes:
    {'BIGINT','BLOB','BYTE','BYTEINT','CHAR','CLOB','DATE','DECIMAL','FLOAT','INTEGER',
     'INTERVAL_DAY','INTERVAL_DAY_TO_HOUR','INTERVAL_DAY_TO_MINUTE','INTERVAL_DAY_TO_SECOND',
     'INTERVAL_HOUR','INTERVAL_HOUR_TO_MINUTE','INTERVAL_HOUR_TO_SECOND','INTERVAL_MINUTE',
     'INTERVAL_MINUTE_TO_SECOND','INTERVAL_MONTH','INTERVAL_SECOND','INTERVAL_YEAR',
     'INTERVAL_YEAR_TO_MONTH','JSON','NUMBER','PERIOD_DATE','PERIOD_TIMESTAMP','SMALLINT',
     'TIME','TIMESTAMP','VARBYTE','VARCHAR','XML'}

    If both `include` and `exclude` are provided, columns must match `include`
    and will then be filtered out if they match `exclude`. Column order is preserved.

    Args:
        include (Iterable[str], optional): tdtypes to include (case-insensitive).
        exclude (Iterable[str], optional): tdtypes to exclude (case-insensitive).

    Returns:
        tdml.DataFrame: DataFrame containing only the selected columns.

    Raises:
        ValueError: If both `include` and `exclude` are None.
        AssertionError: If an unknown tdtype label is supplied.
    """
    allowed = {
        'BIGINT','BLOB','BYTE','BYTEINT','CHAR','CLOB','DATE','DECIMAL','FLOAT','INTEGER',
        'INTERVAL_DAY','INTERVAL_DAY_TO_HOUR','INTERVAL_DAY_TO_MINUTE','INTERVAL_DAY_TO_SECOND',
        'INTERVAL_HOUR','INTERVAL_HOUR_TO_MINUTE','INTERVAL_HOUR_TO_SECOND','INTERVAL_MINUTE',
        'INTERVAL_MINUTE_TO_SECOND','INTERVAL_MONTH','INTERVAL_SECOND','INTERVAL_YEAR',
        'INTERVAL_YEAR_TO_MONTH','JSON','NUMBER','PERIOD_DATE','PERIOD_TIMESTAMP','SMALLINT',
        'TIME','TIMESTAMP','VARBYTE','VARCHAR','XML'
    }

    if include is None and exclude is None:
        raise ValueError("Provide at least one of `include` or `exclude`.")

    include_set = {t.upper() for t in include} if include is not None else None
    exclude_set = {t.upper() for t in exclude} if exclude is not None else None

    if include_set is not None:
        assert include_set.issubset(allowed), "Unknown tdtype in `include`."
    if exclude_set is not None:
        assert exclude_set.issubset(allowed), "Unknown tdtype in `exclude`."

    colnames_tdtypes = [
        (column.name, repr(column.type).split("(")[0].upper())
        for column in self._metaexpr.c
    ]

    final_cols = []
    for col_name, tdtype in colnames_tdtypes:
        if include_set is not None and tdtype not in include_set:
            continue
        if exclude_set is not None and tdtype in exclude_set:
            continue
        final_cols.append(col_name)

    return self.select(final_cols)


def histogram(
    self,
    bins: int = 10,
    exclude_index: bool = True,
    target_columns: Optional[Union[str, Iterable[str]]] = None,
    groupby_columns: Optional[Union[str, Iterable[str]]] = None,
) -> tdml.DataFrame:
    """
    Build equal-width histograms for numeric columns.

    Filters candidate columns to numeric Teradata types and optionally excludes
    index and group-by columns before computing histograms.

    Args:
        bins (int): Number of bins per histogram. Default is 10.
        exclude_index (bool): Exclude index columns from targets. Default is True.
        target_columns (str | Iterable[str], optional): Columns to consider.
            If None, all columns are considered.
        groupby_columns (str | Iterable[str], optional): Columns to group by
            before histogramming.

    Returns:
        tdml.DataFrame: Histogram result DataFrame.

    Raises:
        AssertionError: If `bins` is not a positive integer.
        ValueError: If no eligible numeric columns remain after filtering.
    """
    assert isinstance(bins, int) and bins > 0, "`bins` must be a positive integer"

    allowed_tdtypes = {
        "BYTEINT", "SMALLINT", "INTEGER", "BIGINT",
        "DECIMAL", "NUMERIC", "FLOAT", "REAL", "DOUBLE"
    }

    colnames_tdtypes = [
        (column.name, repr(column.type).split("(")[0].upper())
        for column in self._metaexpr.c
    ]
    possible_columns = [
        colname for (colname, tdtype) in colnames_tdtypes if tdtype in allowed_tdtypes
    ]

    if target_columns is None:
        final_target_columns = list(self.columns)
    else:
        if isinstance(target_columns, str):
            final_target_columns = [target_columns]
        else:
            final_target_columns = list(target_columns)

    if exclude_index and getattr(self, "index", None):
        final_target_columns = [c for c in final_target_columns if c not in self.index]

    final_target_columns = [c for c in final_target_columns if c in possible_columns]

    final_gb_columns: Optional[list[str]]
    if groupby_columns is None:
        final_gb_columns = None
    else:
        if isinstance(groupby_columns, str):
            final_gb_columns = [groupby_columns]
        else:
            final_gb_columns = list(groupby_columns)
        final_target_columns = [c for c in final_target_columns if c not in final_gb_columns]

    if not final_target_columns:
        raise ValueError("No eligible numeric columns found for histogram.")

    hist_obj = tdml.Histogram(
        data=self,
        target_columns=final_target_columns,
        groupby_columns=final_gb_columns,
        method_type="EQUAL-WIDTH",
        nbins=bins,
    )
    return hist_obj.result


from typing import Any, Iterable, Optional, Union, Literal

def plot_hist(
    self,
    bins: int = 10,
    exclude_index: bool = True,
    target_columns: Optional[Union[str, Iterable[str]]] = None,
    groupby_columns: Optional[Union[str, Iterable[str]]] = None,
    library: Literal["plotly", "seaborn"] = "plotly",
    absolute_values: bool = True,
    percentage_values: bool = False,
) -> Any:
    """
    Plot equal-width histograms for numeric columns.

    Uses `histogram()` to compute bin counts, converts to pandas, and renders
    with the chosen library.

    Args:
        bins (int): Number of bins per histogram. Default 10.
        exclude_index (bool): Exclude index columns from targets. Default True.
        target_columns (str | Iterable[str], optional): Columns to include. If None, all.
        groupby_columns (str | Iterable[str], optional): Grouping columns for faceting.
        library ("plotly" | "seaborn"): Backend to render the plot. Default "plotly".
        absolute_values (bool): Show absolute bin counts. Default True.
        percentage_values (bool): Show percentages. Default False.

    Returns:
        Any: A figure/axes object from the selected library.

    Raises:
        AssertionError: If `bins` is not positive or `library` is unknown.
        ValueError: If both `absolute_values` and `percentage_values` are False.
    """
    assert isinstance(bins, int) and bins > 0, "`bins` must be a positive integer"
    assert library in {"plotly", "seaborn"}, "Unsupported library"
    if not (absolute_values or percentage_values):
        raise ValueError("Enable at least one of `absolute_values` or `percentage_values`.")

    DF_hist = self.histogram(
        bins=bins,
        exclude_index=exclude_index,
        target_columns=target_columns,
        groupby_columns=groupby_columns,
    )
    df_hist = DF_hist.to_pandas()

    return _hist(
        df_hist,
        library=library,
        absolute_values=absolute_values,
        percentage_values=percentage_values,
    )

from typing import Iterable, Optional, Union

def categorical_summary(
    self,
    target_columns: Optional[Union[str, Iterable[str]]] = None,
    exclude_index: bool = True,
    include_percentages: bool = False,
) -> tdml.DataFrame:
    """
    Summarize categorical (CHAR/VARCHAR) columns.

    Filters to allowed Teradata types, optionally excludes index columns, and
    computes categorical summaries. If `include_percentages=True`, appends
    `DistinctValuePercentage` computed within each column.

    Args:
        target_columns (str | Iterable[str], optional): Columns to summarize.
            If None, consider all columns.
        exclude_index (bool): Exclude index columns from targets. Default True.
        include_percentages (bool): Add per-column percentage metric. Default False.

    Returns:
        tdml.DataFrame: Categorical summary; includes `DistinctValuePercentage`
        when requested.

    Raises:
        ValueError: If no eligible categorical columns remain after filtering.
    """
    allowed_tdtypes = {"CHAR", "VARCHAR"}

    colnames_tdtypes = [
        (column.name, repr(column.type).split("(")[0].upper())
        for column in self._metaexpr.c
    ]
    possible_columns = [
        colname for (colname, tdtype) in colnames_tdtypes if tdtype in allowed_tdtypes
    ]

    if target_columns is None:
        final_target_columns = list(self.columns)
    else:
        final_target_columns = (
            [target_columns] if isinstance(target_columns, str) else list(target_columns)
        )

    if exclude_index and getattr(self, "index", None):
        final_target_columns = [c for c in final_target_columns if c not in self.index]

    final_target_columns = [c for c in final_target_columns if c in possible_columns]

    if not final_target_columns:
        raise ValueError("No eligible categorical columns found for summary.")

    DF_Catsum = tdml.CategoricalSummary(
        data=self, target_columns=final_target_columns
    ).result

    if not include_percentages:
        return DF_Catsum

    DF_new = DF_Catsum.assign(
        DistinctValuePercentage=(
            DF_Catsum.DistinctValueCount
            / (DF_Catsum.DistinctValueCount.window(partition_columns="ColumnName").sum() * 1.0)
        ).round(4)
    )
    return DF_new


from typing import Iterable, Optional, Union

def column_summary(
    self,
    target_columns: Optional[Union[str, Iterable[str]]] = None,
    exclude_index: bool = True,
) -> tdml.DataFrame:
    """
    Summarize columns for the given selection.

    Builds a per-column summary using `tdml.ColumnSummary`. Optionally limits
    to `target_columns` and excludes index columns.

    Args:
        target_columns (str | Iterable[str], optional): Columns to summarize.
            If None, all columns are considered.
        exclude_index (bool): Exclude index columns from targets. Default True.

    Returns:
        tdml.DataFrame: Summary metrics per column.

    Raises:
        ValueError: If no columns remain after filtering.
    """
    colnames_tdtypes = [
        (column.name, repr(column.type).split("(")[0]) for column in self._metaexpr.c
    ]
    possible_columns = [colname for (colname, _tdtype) in colnames_tdtypes]

    if target_columns is None:
        final_target_columns = list(self.columns)
    else:
        final_target_columns = (
            [target_columns] if isinstance(target_columns, str) else list(target_columns)
        )

    if exclude_index and getattr(self, "index", None):
        final_target_columns = [c for c in final_target_columns if c not in self.index]

    final_target_columns = [c for c in final_target_columns if c in possible_columns]

    if not final_target_columns:
        raise ValueError("No columns available for summary after filtering.")

    DF_Colsum = tdml.ColumnSummary(
        data=self, target_columns=final_target_columns
    ).result
    return DF_Colsum

def fill_RowId(self, rowid_columnname: str = "row_id") -> tdml.DataFrame:
    """
    Add a sequential row identifier column.

    Uses `tdml.FillRowId` to append a monotonically increasing row-id column.

    Args:
        rowid_columnname (str): Name of the row-id column to create. Default "row_id".

    Returns:
        tdml.DataFrame: New DataFrame with the row-id column added.

    Raises:
        AssertionError: If `rowid_columnname` is empty.
        ValueError: If `rowid_columnname` already exists in the DataFrame.
    """
    assert isinstance(rowid_columnname, str) and rowid_columnname.strip(), "`rowid_columnname` must be a non-empty string"

    if rowid_columnname in getattr(self, "columns", []):
        raise ValueError(f"Column '{rowid_columnname}' already exists.")

    new_DF = tdml.FillRowId(data=self, row_id_column=rowid_columnname).result
    return new_DF

