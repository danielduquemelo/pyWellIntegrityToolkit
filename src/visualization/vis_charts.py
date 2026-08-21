from matplotlib import pyplot as plt


REGIME_ORDER = ["yield", "plastic", "transition", "elastic"]
REGIME_COLORS = {
    "yield":      "#e07b54",
    "plastic":    "#5b8db8",
    "transition": "#6abf69",
    "elastic":    "#b07cc6",
}


def _add_histogram_to_axes(ax, dataset, color='steelblue', edgecolor='white', alpha=0.85):
    n, bins, patches = ax.hist(
        dataset,
        bins=30,
        color=color,
        edgecolor=edgecolor,
        linewidth=0.6,
        alpha=alpha,
    )
    ax.axvline(dataset.mean(), color='tomato', linestyle='--', linewidth=1.4,
               label=f'Mean: {dataset.mean():.1f}')
    ax.axvline(dataset.median(), color='gold', linestyle='--', linewidth=1.4,
               label=f'Median: {dataset.median():.1f}')
    return n, bins, patches


def plot_histogram(dataset, xlabel='X', title='Distribution'):

    fig, ax = plt.subplots(figsize=(10, 5))
    _add_histogram_to_axes(ax, dataset)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.legend()
    ax.set_ylim(top=divmod(ax.get_ylim()[1], 5)[0]*5 + 5)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_boxplot_by_group(df, group_col, value_col, title='Distribution by Group',
                          xlabel='Group', ylabel='Value', ascending=False):
    """Boxplot of value_col split by group_col, annotated with min/median/max and mean/std.

    Parameters
    ----------
    df : pd.DataFrame
        Source data.
    group_col : str
        Column to group by (one box per unique value).
    value_col : str
        Column of numeric values to summarize.
    title, xlabel, ylabel : str
        Chart labels.
    ascending : bool
        Sort order of the groups along the x-axis.
    """
    groups = sorted(df[group_col].dropna().unique(), reverse=not ascending)
    data = [df.loc[df[group_col] == g, value_col].dropna() for g in groups]
    labels = [str(g) for g in groups]

    fig, ax = plt.subplots(figsize=(max(8, len(groups) * 1.3), 6))
    ax.boxplot(
        data,
        labels=labels,
        showmeans=True,
        meanline=True,
        patch_artist=True,
        whis=(0, 100),  # extend whiskers to the true min/max instead of 1.5*IQR outlier cutoff
        boxprops=dict(facecolor='steelblue', alpha=0.6, edgecolor='black'),
        medianprops=dict(color='gold', linewidth=1.6),
        meanprops=dict(color='tomato', linewidth=1.6, linestyle='--'),
        whiskerprops=dict(color='black'),
        capprops=dict(color='black'),
        flierprops=dict(marker='o', markersize=4, markerfacecolor='gray', alpha=0.5),
    )

    for i, series in enumerate(data, start=1):
        if series.empty:
            continue
        vmin, vmedian, vmax = series.min(), series.median(), series.max()
        vmean, vstd = series.mean(), series.std()

        ax.annotate(f'max: {vmax:.2f}', xy=(i, vmax), xytext=(0, 8),
                    textcoords='offset points', ha='center', fontsize=8)
        ax.annotate(f'min: {vmin:.2f}', xy=(i, vmin), xytext=(0, -14),
                    textcoords='offset points', ha='center', fontsize=8)
        ax.annotate(f'median: {vmedian:.2f}', xy=(i, vmin), xytext=(0, -28),
                    textcoords='offset points', ha='center', fontsize=8,
                    color='darkgoldenrod', fontweight='bold')
        ax.annotate(f'μ={vmean:.2f}, σ={vstd:.2f}', xy=(i, vmin), xytext=(0, -42),
                    textcoords='offset points', ha='center', fontsize=8, color='tomato')

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.grid(axis='y', alpha=0.3)
    ax.margins(y=0.2)
    plt.tight_layout()
    plt.show()


def plot_bar_chart(dataset, xlabel='Category', title='Count by Category',
                   order=None, colors=None):
    """Bar chart of value counts for a categorical Series.

    Parameters
    ----------
    dataset : pd.Series
        Categorical data to count and plot.
    xlabel : str
        X-axis label.
    title : str
        Chart title.
    order : list[str] | None
        Category order for the bars. Unrecognised values are appended.
    colors : dict[str, str] | None
        Mapping of category name to bar colour.
    """
    counts = dataset.value_counts()

    if order is not None:
        ordered = [c for c in order if c in counts.index]
        ordered += [c for c in counts.index if c not in order]
        counts = counts.reindex(ordered)

    bar_colors = [
        (colors or {}).get(cat, "steelblue")
        for cat in counts.index
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(counts.index, counts.values, color=bar_colors,
                  edgecolor='white', linewidth=0.6, alpha=0.88)

    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha='center', va='bottom', fontsize=11)

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.set_ylim(top=divmod(ax.get_ylim()[1], 5)[0]*5 + 5)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

