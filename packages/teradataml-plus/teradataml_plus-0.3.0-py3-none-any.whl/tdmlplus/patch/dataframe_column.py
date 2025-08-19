from sqlalchemy import func
import re
from typing import Optional, Union, Tuple
from teradatasqlalchemy import INTEGER as tdml_INTEGER
from sqlalchemy import literal_column
from .. import tdml
from sklearn.preprocessing import PowerTransformer
import numpy as np

from ._plotting_utils import _hist

def trycast(self, type_= None) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Apply a TRYCAST expression to the DataFrame column using the given type.

    This function parses a Python type expression (e.g., teradataml types like
    Integer(), Decimal(precision=6, scale=4)) and constructs the equivalent
    SQL TRYCAST operation to apply to the column.

    Args:
        type_ (Any): A teradataml type object to cast the column to.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new DataFrame Column with the TRYCAST expression applied.
    """
    typestr = type_.__repr__()
    match = re.match(r'(\w+)\((.*?)\)', typestr)
    if match:
        typename, params = match.groups()
        params = params.strip()
        if params:
            values = [v.strip() for v in re.findall(r'=\s*([^,]+)', params)]
            typestr = f"{typename}({', '.join(values)})"
        else:
            typestr = typename
    else:
        typestr = typestr

    new_expression = f"TRYCAST({self.name} AS {typestr})"
    return type(self)(new_expression, type=type_)

def hashbin(
    self,
    num_buckets: int = 100,
    salt: Optional[str] = None
) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Compute a hash bin value for the column expression, optionally salted.

    Args:
        num_buckets (int): Number of buckets to hash into.
        salt (str, optional): Salt to append to the input before hashing.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new expression representing the hash bin.
    """
    if not salt:
        hash_input = self.expression
    else:
        hash_input = func.CONCAT(self.expression, salt)

    new_expression = func.ABS(
        func.FROM_BYTES(
            func.HASHROW(hash_input), "base10"
        ).cast(type_=tdml_INTEGER)
    ) % num_buckets

    return type(self)(new_expression, type=tdml_INTEGER())




def _power_transform_get_lambda(
    self,
    method: str = 'yeo-johnson'
) -> Tuple[str, float]:
    """
    Estimate the lambda parameter for a power transform (Yeo-Johnson or Box-Cox)
    using a sample of data from the column.

    Args:
        method (str, optional): The power transform method. Must be either
            'yeo-johnson' or 'box-cox'. Default is 'yeo-johnson'.

    Returns:
        Tuple[str, float]: The method name and the estimated lambda value.
    """

    assert method in ['yeo-johnson', 'box-cox'], "method must be 'yeo-johnson' or 'box-cox'"

    # Get table, schema, and column information
    table = self.table
    column_name = self.name
    schema_expr = f"{table.schema}." if table.schema is not None else ""

    # Sample up to 10,000 rows to estimate lambda
    res = tdml.execute_sql(
        f"SELECT {column_name} FROM {schema_expr}{table.name} SAMPLE 10000"
    ).fetchall()
    res = np.array(res)

    # Calculate lambda using sklearn's PowerTransformer
    pt = PowerTransformer(method=method, standardize=False)
    if method == "box-cox":
        res = res[res > 0].reshape(-1, 1)
    pt.fit(res)

    def _truncate_float(x):
        RESOLUTION = 6
        return float(format(x, f'.{RESOLUTION}e'))

    pt_lambda = _truncate_float(pt.lambdas_[0])

    return method, pt_lambda



def power_transform(
    self,
    method: str,
    pt_lambda: float
) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Apply a power transformation (Yeo-Johnson or Box-Cox) to the column
    using a pre-estimated lambda value.

    Args:
        method (str): The transformation method, must be 'yeo-johnson' or 'box-cox'.
        pt_lambda (float): The lambda value for the transformation.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new expression representing the transformed column.
    """

    assert method in ['yeo-johnson', 'box-cox'], "method must be 'yeo-johnson' or 'box-cox'"

    colname = self.name

    def power_transform_yeojohnson(colname: str, lambda_: float) -> str:
        if lambda_ == 0:
            lt0 = f"-(POWER(-{colname} + 1, 2 - {lambda_}) - 1) / (2 - {lambda_})"
            gte0 = f"LN({colname} + 1)"
        elif lambda_ == 2:
            lt0 = f"-LN(-{colname} + 1)"
            gte0 = f"(POWER({colname} + 1, {lambda_}) - 1) / {lambda_}"
        else:
            lt0 = f"-(POWER(-{colname} + 1, 2 - {lambda_}) - 1) / (2 - {lambda_})"
            gte0 = f"(POWER({colname} + 1, {lambda_}) - 1) / {lambda_}"
        return f"CASE WHEN {colname} >= 0.0 THEN {gte0} ELSE {lt0} END"

    def power_transform_boxcox(colname: str, lambda_: float) -> str:
        if lambda_ == 0:
            formula = f"LN({colname})"
        else:
            formula = f"(POWER({colname}, {lambda_}) - 1) / {lambda_}"
        return f"CASE WHEN {colname} > 0.0 THEN {formula} ELSE NULL END"

    if method == "yeo-johnson":
        formula = power_transform_yeojohnson(colname, pt_lambda)
    else:
        formula = power_transform_boxcox(colname, pt_lambda)

    new_expression = literal_column(formula, type_=tdml.FLOAT())
    return type(self)(new_expression, type=tdml.FLOAT())


def power_fit_transform(
    self,
    method: str = 'yeo-johnson'
) -> 'tdml.dataframe.sql._SQLColumnExpression':
    """
    Estimate lambda and apply a power transformation (Yeo-Johnson or Box-Cox)
    to the column in a single step.

    Args:
        method (str, optional): The transformation method, must be 'yeo-johnson' or 'box-cox'.
                                Defaults to 'yeo-johnson'.

    Returns:
        tdml.dataframe.sql._SQLColumnExpression: A new expression with the transformation applied.
    """
    _, pt_lambda = self._power_transform_get_lambda(method)
    new_expr = self.power_transform(method, pt_lambda)
    return new_expr

def _column_histogram(self, bins: int = 10) -> tdml.DataFrame:
    """
    Build an equal-width histogram for this column.

    Validates the column's Teradata type as numeric and computes a histogram
    using `tdml.Histogram`.

    Args:
        bins (int): Number of bins. Default 10.

    Returns:
        tdml.DataFrame: Histogram result.

    Raises:
        AssertionError: If `bins` is not a positive integer.
        ValueError: If the column's tdtype is not numeric.
    """
    assert isinstance(bins, int) and bins > 0, "`bins` must be a positive integer"

    # Type check
    tdtype = self.type.__repr__().split("(")[0].upper()
    allowed_tdtypes = {
        "BYTEINT", "SMALLINT", "INTEGER", "BIGINT",
        "DECIMAL", "NUMERIC", "FLOAT", "REAL", "DOUBLE"
    }
    if tdtype not in allowed_tdtypes:
        raise ValueError(
            f"Column '{self.name}' has non-numeric tdtype '{tdtype}'. "
            f"Allowed: {sorted(allowed_tdtypes)}"
        )

    # Build histogram
    table = self.table
    column_name = self.name
    schema_expr = f"{table.schema}." if table.schema is not None else ""
    hist_obj = tdml.Histogram(
        data=tdml.DataFrame.from_query(
            f"SELECT {column_name} FROM {schema_expr}{table.name}"
        ),
        target_columns=[column_name],
        method_type="EQUAL-WIDTH",
        nbins=bins,
    )
    return hist_obj.result


from typing import Any, Literal

def _column_plot_hist(
    self,
    bins: int = 10,
    library: Literal["plotly", "seaborn"] = "plotly",
    absolute_values: bool = True,
    percentage_values: bool = False
) -> Any:
    """
    Plot an equal-width histogram for this column.

    Uses `_column_histogram()` to compute bin counts, converts to pandas, and renders
    with the selected plotting backend.

    Args:
        bins (int): Number of bins. Default 10.
        library ("plotly" | "seaborn"): Plotting backend. Default "plotly".
        absolute_values (bool): Show absolute bin counts. Default True.
        percentage_values (bool): Show percentages. Default False.

    Returns:
        Any: Figure/axes object from the chosen library.

    Raises:
        AssertionError: If `bins` is not positive or `library` is unsupported.
        ValueError: If both `absolute_values` and `percentage_values` are False.
        ValueError: If the column tdtype is non-numeric (raised by `_column_histogram`).
    """
    assert isinstance(bins, int) and bins > 0, "`bins` must be a positive integer"
    assert library in {"plotly", "seaborn"}, "Unsupported library"
    if not (absolute_values or percentage_values):
        raise ValueError("Enable at least one of `absolute_values` or `percentage_values`.")

    DF_hist = self.histogram(bins=bins)
    df_hist = DF_hist.to_pandas()

    return _hist(
        df_hist,
        library=library,
        absolute_values=absolute_values,
        percentage_values=percentage_values,
    )

from typing import Any, Mapping, Optional, Union

def _map(
    self,
    value_map: Mapping[Union[str, int, float, bool, None], Union[str, int, float, bool, None]],
    keep_original: bool = True,
    default_else_value: Optional[Union[str, int, float, bool]] = None,
    output_type: Optional[Any] = None,
) -> Any:
    """
    Map discrete values of this column using a SQL CASE expression.

    If `keep_original` is True and no mapping matches, the original value is preserved.
    Otherwise, `default_else_value` is used (or NULL if not provided). The output type
    can be provided explicitly via `output_type`; if omitted and `keep_original` is False,
    it is inferred from `value_map` and `default_else_value`.

    Args:
        value_map (Mapping): Keys/values to map from/to. Supported scalars: str, int,
            float, bool, None.
        keep_original (bool): Preserve original value for non-matching rows. Default True.
        default_else_value: Fallback value when no mapping matches and `keep_original` is False.
        output_type: Explicit SQLAlchemy/tdml type for the resulting expression.

    Returns:
        Any: A new column expression of the same kind as `self`.

    Raises:
        ValueError: If `value_map` is empty.
    """
    if not value_map:
        raise ValueError("`value_map` must not be empty.")

    def _lit(v: Union[str, int, float, bool, None]) -> str:
        if v is None:
            return "NULL"
        if isinstance(v, bool):
            return "1" if v else "0"
        if isinstance(v, (int, float)):
            return str(v)
        s = str(v).replace("'", "''")
        return f"'{s}'"

    def _case_when_map_str(
        col_name: str,
        value_map_local: Mapping[Union[str, int, float, bool, None], Union[str, int, float, bool, None]],
        keep_orig: bool = True,
        default_else: Optional[Union[str, int, float, bool]] = None,
    ) -> str:
        parts = ["CASE"]
        for k, v in value_map_local.items():
            if k is None:
                parts.append(f" WHEN {col_name} IS NULL THEN {_lit(v)}")
            else:
                parts.append(f" WHEN {col_name} = {_lit(k)} THEN {_lit(v)}")
        if keep_orig:
            parts.append(f" ELSE {col_name}")
        elif default_else is not None:
            parts.append(f" ELSE {_lit(default_else)}")
        else:
            parts.append(" ELSE NULL")
        parts.append(" END")
        return "".join(parts)

    def _infer_output_dtype(
        value_map_local: Mapping[Union[str, int, float, bool, None], Union[str, int, float, bool, None]],
        default_else: Optional[Union[str, int, float, bool]] = None,
    ) -> Any:
        vals = list(value_map_local.values()) + ([] if default_else is None else [default_else])
        non_null = [v for v in vals if v is not None]
        if not non_null:
            return tdml.VARCHAR(1024)
        if any(isinstance(v, str) for v in non_null):
            varcharlength = max(1024, int(1.2 * max(len(s) for s in non_null if isinstance(s, str))))
            return tdml.VARCHAR(varcharlength)
        if any(isinstance(v, float) for v in non_null):
            return tdml.FLOAT()
        if any(isinstance(v, bool) for v in non_null):
            return tdml.BYTEINT()
        if all(isinstance(v, int) for v in non_null):
            return tdml.INTEGER()
        return tdml.VARCHAR(1024)

    if output_type is None:
        output_type = self.type if keep_original else _infer_output_dtype(value_map, default_else_value)

    new_expression = _case_when_map_str(self.name, value_map, keep_original, default_else_value)
    return type(self)(new_expression, type=output_type)
