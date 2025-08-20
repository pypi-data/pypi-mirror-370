"""
teradataml-plus
============================
Python Package that extends the functionality of the popular [teradataml](https://pypi.org/project/teradataml/) package through [monkey-patching](https://en.wikipedia.org/wiki/Monkey_patch).
This is to use field-developed assets more naturally with the existing interface.
"""

__author__ = """Martin Hillebrand"""
__email__ = 'martin.hillebrand@teradata.com'
__version__ = '0.3.0'



# Public monkey-patched API provided by tdmlplus
__all__ = [
    #v0.1.0
    "teradataml.DataFrame.corr",
    "teradataml.random.randn",
    "teradataml.dba.get_amps_count",
    #v0.2.0
    "teradataml.prettyprint_sql",
    "teradataml.DataFrame.show_CTE_query",
    "teradataml.DataFrame.deploy_CTE_view",
    "teradataml.DataFrame.easyjoin",
    "teradataml.dataframe.sql._SQLColumnExpression.trycast",
    "teradataml.dataframe.sql._SQLColumnExpression.hashbin",
    "teradataml.dataframe.sql._SQLColumnExpression._power_transform_get_lambda",
    "teradataml.dataframe.sql._SQLColumnExpression.power_transform",
    "teradataml.dataframe.sql._SQLColumnExpression.power_fit_transform",
    "teradataml.random._generate_sql_for_correlated_normals",
    "teradataml.random.correlated_normals",
    "teradataml.widgets.tab_dfs",
    # v0.3.0
    "teradataml.DataFrame.top",
    "teradataml.DataFrame.head", # overwritten
    "teradataml.DataFrame.select_dtypes",
    "teradataml.DataFrame.select_tdtypes",
    "teradataml.DataFrame.histogram",
    "teradataml.DataFrame.plot_hist",
    "teradataml.DataFrame.hist",
    "teradataml.DataFrame.categorical_summary",
    "teradataml.DataFrame.column_summary",
    "teradataml.DataFrame.fill_RowId",
    "teradataml.DataFrame.reset_index",
    "teradataml.dataframe.sql._SQLColumnExpression.histogram",
    "teradataml.dataframe.sql._SQLColumnExpression.plot_hist",
    "teradataml.dataframe.sql._SQLColumnExpression.hist",
    "teradataml.dataframe.sql._SQLColumnExpression.map",

]


import teradataml as tdml
try:
    tdml.display.enable_ui = False
except:
    pass

#v0.1.0
# --- patch: DataFrame.corr ---
from .patch.dataframe import corr
if not hasattr(tdml.DataFrame, "corr"):
    tdml.DataFrame.corr = corr

# --- patch: tdml.random.randn ---
from .patch import random as _random
if not hasattr(tdml, "random"):
    tdml.random = type("random", (), {})()
if not hasattr(tdml.random, "randn"):
    tdml.random.randn = _random.randn

# --- patch: tdml.dba.get_amps_count ---
from .patch import dba as _dba
if not hasattr(tdml, "dba"):
    tdml.dba = type("dba", (), {})()
if not hasattr(tdml.dba, "get_amps_count"):
    tdml.dba.get_amps_count = _dba.get_amps_count

#v0.2.0
# --- patch: tdml.prettyprint_sql ---
from .patch import utils as _utils
if not hasattr(tdml, "prettyprint_sql"):
    tdml.prettyprint_sql = _utils.prettyprint_sql

# --- patch: DataFrame.show_CTE_query ---
from .patch.dataframe import show_CTE_query
if not hasattr(tdml.DataFrame, "show_CTE_query"):
    tdml.DataFrame.show_CTE_query = show_CTE_query

# --- patch: DataFrame.deploy_CTE_view ---
from .patch.dataframe import deploy_CTE_view
if not hasattr(tdml.DataFrame, "deploy_CTE_view"):
    tdml.DataFrame.deploy_CTE_view = deploy_CTE_view

# --- patch: DataFrame.deploy_CTE_view ---
from .patch.dataframe import easyjoin
if not hasattr(tdml.DataFrame, "easyjoin"):
    tdml.DataFrame.easyjoin = easyjoin

# --- patch: _SQLColumnExpression.trycast ---
from .patch.dataframe_column import trycast
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "trycast"):
    tdml.dataframe.sql._SQLColumnExpression.trycast = trycast

# --- patch: _SQLColumnExpression.hashbin ---
from .patch.dataframe_column import hashbin
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "hashbin"):
    tdml.dataframe.sql._SQLColumnExpression.hashbin = hashbin

# --- patch: _SQLColumnExpression._power_transform_get_lambda ---
from .patch.dataframe_column import _power_transform_get_lambda
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "_power_transform_get_lambda"):
    tdml.dataframe.sql._SQLColumnExpression._power_transform_get_lambda = _power_transform_get_lambda

# --- patch: _SQLColumnExpression.power_transform ---
from .patch.dataframe_column import power_transform
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "power_transform"):
    tdml.dataframe.sql._SQLColumnExpression.power_transform = power_transform

# --- patch: _SQLColumnExpression.power_fit_transform ---
from .patch.dataframe_column import power_fit_transform
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "power_fit_transform"):
    tdml.dataframe.sql._SQLColumnExpression.power_fit_transform = power_fit_transform

# --- patch: tdml.random._generate_sql_for_correlated_normals ---
from .patch import random as _random
if not hasattr(tdml.random, "_generate_sql_for_correlated_normals"):
    tdml.random._generate_sql_for_correlated_normals = _random._generate_sql_for_correlated_normals

# --- patch: tdml.random.correlated_normals ---
from .patch import random as _random
if not hasattr(tdml.random, "correlated_normals"):
    tdml.random.correlated_normals = _random.correlated_normals

# --- patch: tdml.widgets.tab_dfs ---
from .patch import widgets as _widgets
if not hasattr(tdml, "widgets"):
    tdml.widgets = type("widgets", (), {})()
if not hasattr(tdml.widgets, "tab_dfs"):
    tdml.widgets.tab_dfs = _widgets.tab_dfs



#v0.3.0
# --- DataFrame methods ---
from .patch.dataframe import (
    top,
    new_head,
    select_dtypes,
    select_tdtypes,
    histogram,
    plot_hist,
    categorical_summary,
    column_summary,
    fill_RowId,
)

# top
if not hasattr(tdml.DataFrame, "top"):
    tdml.DataFrame.top = top

# head override (special case): preserve original as _head if not present, then override
if not hasattr(tdml.DataFrame, "_head"):
    tdml.DataFrame._head = tdml.DataFrame.head
tdml.DataFrame.head = new_head

# select_dtypes / select_tdtypes
if not hasattr(tdml.DataFrame, "select_dtypes"):
    tdml.DataFrame.select_dtypes = select_dtypes
if not hasattr(tdml.DataFrame, "select_tdtypes"):
    tdml.DataFrame.select_tdtypes = select_tdtypes

# histogram + plotting
if not hasattr(tdml.DataFrame, "histogram"):
    tdml.DataFrame.histogram = histogram
if not hasattr(tdml.DataFrame, "plot_hist"):
    tdml.DataFrame.plot_hist = plot_hist
if not hasattr(tdml.DataFrame, "hist"):
    tdml.DataFrame.hist = tdml.DataFrame.plot_hist

# categorical / column summaries
if not hasattr(tdml.DataFrame, "categorical_summary"):
    tdml.DataFrame.categorical_summary = categorical_summary
if not hasattr(tdml.DataFrame, "column_summary"):
    tdml.DataFrame.column_summary = column_summary

# fill_RowId + reset_index alias
if not hasattr(tdml.DataFrame, "fill_RowId"):
    tdml.DataFrame.fill_RowId = fill_RowId
if not hasattr(tdml.DataFrame, "reset_index"):
    tdml.DataFrame.reset_index = fill_RowId

# --- _SQLColumnExpression methods ---
from .patch.dataframe_column import (
    _column_histogram,
    _column_plot_hist,
    _map as _col_map,
)

if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "histogram"):
    tdml.dataframe.sql._SQLColumnExpression.histogram = _column_histogram
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "plot_hist"):
    tdml.dataframe.sql._SQLColumnExpression.plot_hist = _column_plot_hist
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "hist"):
    tdml.dataframe.sql._SQLColumnExpression.hist = _column_plot_hist
if not hasattr(tdml.dataframe.sql._SQLColumnExpression, "map"):
    tdml.dataframe.sql._SQLColumnExpression.map = _col_map

