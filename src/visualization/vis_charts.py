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
    ax.grid(axis='y', alpha=0.3)
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
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

