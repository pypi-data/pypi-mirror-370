import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.express.colors import qualitative as qqual

def _hist_plotly(
    df_hist,
    absolute_values=True,
    percentage_values=False,
    alpha=0.5,
    col_spacing=None,
    **plotly_args
):
    must_have = {"ColumnName", "MinValue", "MaxValue"}
    if absolute_values: must_have.add("CountOfValues")
    if percentage_values: must_have.add("Bin_Percent")
    missing = must_have - set(df_hist.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if not (absolute_values or percentage_values):
        raise ValueError("At least one of absolute_values or percentage_values must be True.")

    idx = df_hist.columns.get_loc("ColumnName")
    group_cols = list(df_hist.columns[:idx])

    df = df_hist.sort_values(["ColumnName", "MinValue", "MaxValue"]).copy()
    df["_x"] = (df["MinValue"] + df["MaxValue"]) / 2.0
    df["_w"] = (df["MaxValue"] - df["MinValue"]).abs()

    if group_cols:
        df["_gkey"] = list(df[group_cols].itertuples(index=False, name=None))
        key_list = (
            df.drop_duplicates(["_gkey", "ColumnName", "MinValue", "MaxValue"])
              .groupby("_gkey", dropna=False).size()
              .sort_values(ascending=False).index.tolist()
        )
        palette = (qqual.Plotly + qqual.D3 + qqual.Set3 + qqual.Dark24)
        color_map = {k: palette[i % len(palette)] for i, k in enumerate(key_list)}
    else:
        df["_gkey"] = [("__all__",)] * len(df)
        color_map = {("__all__",): qqual.Plotly[0]}

    colnames = list(pd.unique(df["ColumnName"]))
    n_cols = (1 if (absolute_values ^ percentage_values) else 2)
    if col_spacing is None:
        col_spacing = 0.16 if n_cols == 2 else 0.08

    titles = []
    for c in colnames:
        if absolute_values: titles.append(f"{c} — Count")
        if percentage_values: titles.append(f"{c} — Percent")

    fig = make_subplots(
        rows=len(colnames),
        cols=n_cols,
        subplot_titles=titles,
        horizontal_spacing=col_spacing,
        vertical_spacing=0.08,
        shared_xaxes=False,
        shared_yaxes=False,
    )

    legend_seen = set()
    show_any_legend = bool(group_cols)

    def _name_from_key(key_tuple):
        if not group_cols: return None
        return ", ".join(f"{c}={v}" for c, v in zip(group_cols, key_tuple))

    def _add_metric_traces(subdf, metric, row, col):
        ycol = "CountOfValues" if metric == "count" else "Bin_Percent"
        ytitle = "Count" if metric == "count" else "Percent"
        xmin, xmax = subdf["MinValue"].min(), subdf["MaxValue"].max()

        for gkey, g in subdf.groupby("_gkey", dropna=False):
            name = _name_from_key(gkey)
            first_legend = (gkey not in legend_seen) and show_any_legend
            if show_any_legend: legend_seen.add(gkey)

            fig.add_trace(
                go.Bar(
                    x=g["_x"], y=g[ycol], width=g["_w"],
                    name=name if show_any_legend else None,
                    legendgroup=str(gkey) if show_any_legend else None,
                    showlegend=first_legend if show_any_legend else False,
                    opacity=alpha,
                    marker_color=color_map[gkey],
                    marker_line_width=0,
                    hovertemplate=(
                        "bin: [%{customdata[1]}, %{customdata[2]})"
                        "<br>center: %{x}"
                        "<br>width: %{customdata[0]:.6g}"
                        f"<br>{ytitle}: "+"%{y}<extra></extra>"
                    ),
                    customdata=g[["_w", "MinValue", "MaxValue"]],
                ),
                row=row, col=col
            )

        fig.update_xaxes(range=[xmin, xmax], title_text=subdf["ColumnName"].iloc[0], row=row, col=col)
        fig.update_yaxes(title_text=ytitle, row=row, col=col)

    for i, c in enumerate(colnames, start=1):
        sub = df[df["ColumnName"] == c]
        j = 1
        if absolute_values:
            _add_metric_traces(sub, "count", i, j); j += (1 if n_cols == 2 else 0)
        if percentage_values:
            _add_metric_traces(sub, "percent", i, j if n_cols == 2 else 1)

    base_layout = dict(
        barmode="overlay",
        bargap=0.0,
        bargroupgap=0.0,
        height=max(280, 260 * len(colnames)),
        template="plotly_white",
    )
    if show_any_legend:
        base_layout["legend"] = dict(
            title="Groups",
            groupclick="togglegroup",
            itemclick="toggle",
        )
    fig.update_layout(**{**base_layout, **plotly_args})
    return fig


def _hist_seaborn(
        df_hist,
        absolute_values=True,
        percentage_values=False,
        alpha=0.5,
        col_spacing=None,  # similar to plotly's horizontal_spacing
        palette=None,
        figsize=None,
        style="whitegrid",
        **mpl_kwargs  # forwarded to plt.subplots (e.g., constrained_layout=True)
):
    # validations
    if not (absolute_values or percentage_values):
        raise ValueError("At least one of absolute_values or percentage_values must be True.")
    must_have = {"ColumnName", "MinValue", "MaxValue"}
    if absolute_values: must_have.add("CountOfValues")
    if percentage_values: must_have.add("Bin_Percent")
    missing = must_have - set(df_hist.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # grouping columns: all columns left of ColumnName
    idx = df_hist.columns.get_loc("ColumnName")
    group_cols = list(df_hist.columns[:idx])

    # prepare
    df = df_hist.sort_values(["ColumnName", "MinValue", "MaxValue"]).copy()
    df["_x"] = (df["MinValue"] + df["MaxValue"]) / 2.0
    df["_w"] = (df["MaxValue"] - df["MinValue"]).abs()

    # distinct group keys for stable colors
    if group_cols:
        df["_gkey"] = list(df[group_cols].itertuples(index=False, name=None))
        key_list = (
            df.drop_duplicates(["_gkey", "ColumnName", "MinValue", "MaxValue"])
            .groupby("_gkey", dropna=False).size()
            .sort_values(ascending=False).index.tolist()
        )
    else:
        df["_gkey"] = [("__all__",)] * len(df)
        key_list = [("__all__",)]

    # palette
    pal = sns.color_palette(palette or "tab10", n_colors=max(1, len(key_list)))
    color_map = {k: pal[i % len(pal)] for i, k in enumerate(key_list)}

    # layout
    colnames = list(pd.unique(df["ColumnName"]))
    n_rows = max(1, len(colnames))
    n_cols = 1 if (absolute_values ^ percentage_values) else 2
    if figsize is None:
        figsize = (10 if n_cols == 1 else 16, max(3.2 * n_rows, 3.2))
    if col_spacing is None:
        col_spacing = 0.30 if n_cols == 2 else 0.15

    sns.set_theme(style=style)
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=figsize,
        sharex=False, sharey=False,
        gridspec_kw=dict(wspace=col_spacing, hspace=0.45),
        **mpl_kwargs
    )

    # normalize axes indexing
    if n_rows == 1 and n_cols == 1:
        axes = [[axes]]
    elif n_rows == 1:
        axes = [axes]
    elif n_cols == 1:
        axes = [[ax] for ax in axes]

    def _name_from_key(key_tuple):
        if not group_cols: return None
        return ", ".join(f"{c}={v}" for c, v in zip(group_cols, key_tuple))

    # build one shared legend (only if groups exist)
    added_labels = set()
    legend_handles = []
    legend_labels = []

    def _draw_metric(ax, subdf, metric):
        ycol = "CountOfValues" if metric == "count" else "Bin_Percent"
        ytitle = "Count" if metric == "count" else "Percent"
        xmin, xmax = subdf["MinValue"].min(), subdf["MaxValue"].max()

        for gkey, g in subdf.groupby("_gkey", dropna=False):
            label = _name_from_key(gkey)
            bars = ax.bar(
                g["_x"].to_numpy(),
                g[ycol].to_numpy(),
                width=g["_w"].to_numpy(),
                color=color_map[gkey],
                alpha=alpha,
                align="center",
                edgecolor="none",
                label=(label if (label and label not in added_labels) else None),
            )
            if label and label not in added_labels:
                added_labels.add(label)
                legend_handles.append(bars[0])
                legend_labels.append(label)

        ax.set_xlim(xmin, xmax)
        ax.set_ylabel(ytitle)

    # draw grid
    for r, cname in enumerate(colnames):
        sub = df[df["ColumnName"] == cname]
        c = 0
        if absolute_values:
            _draw_metric(axes[r][c], sub, "count")
            axes[r][c].set_title(f"{cname} — Count")
            c += (1 if n_cols == 2 else 0)
        if percentage_values:
            _draw_metric(axes[r][c if n_cols == 2 else 0], sub, "percent")
            axes[r][c if n_cols == 2 else 0].set_title(f"{cname} — Percent")

        # x-labels on bottom row
        if r == n_rows - 1:
            if n_cols == 2:
                axes[r][0].set_xlabel(cname)
                axes[r][1].set_xlabel(cname)
            else:
                axes[r][0].set_xlabel(cname)

    # legend on top if groups exist
    if group_cols and legend_handles:
        fig.legend(
            handles=legend_handles,
            labels=legend_labels,
            loc="upper center",
            ncol=min(len(legend_handles), 4),
            frameon=True,
            bbox_to_anchor=(0.5, 1.02)
        )

    return fig  # , axes


def _hist(
    df_hist,
    library="plotly",
    absolute_values=True,
    percentage_values=False,
    alpha=0.5,
    col_spacing=None,
    **kwargs
):
    lib = str(library).lower()
    if lib in ("plotly", "pl"):
        return _hist_plotly(
            df_hist,
            absolute_values=absolute_values,
            percentage_values=percentage_values,
            alpha=alpha,
            col_spacing=col_spacing,
            **kwargs
        )
    elif lib in ("seaborn", "sns", "matplotlib", "mpl"):
        return _hist_seaborn(
            df_hist,
            absolute_values=absolute_values,
            percentage_values=percentage_values,
            alpha=alpha,
            col_spacing=col_spacing,
            **kwargs
        )
    else:
        raise ValueError("library must be 'plotly' or 'seaborn'")
