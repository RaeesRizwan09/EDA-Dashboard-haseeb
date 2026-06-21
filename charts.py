"""
charts.py — All chart functions for the Big Mac Index Dashboard
Aesthetic: Editorial black, warm gold, restrained monochrome
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO

# ── THEME ─────────────────────────────────────────────────────────────────────
BG      = "#0a0a0a"
CARD    = "#0f0f0f"
GOLD    = "#c8a96e"
GOLD_LT = "#e0c99a"
GOLD_DK = "#9a7a48"
TEXT    = "#e8e0d4"
MUTED   = "#555555"
GRID    = "#1a1a1a"
GREEN   = "#6fcf97"
RED     = "#eb5757"
BLUE    = "#5b9cf6"
PURPLE  = "#9f7aea"

PALETTE_GOLD = [
    "#c8a96e", "#b8935a", "#a07d44", "#8a6830",
    "#ddbf8e", "#eeddb0", "#f5ebcf",
]
GRADIENT = ["#1a0a00", "#3d2000", "#7a4800", "#b87000", "#c8a96e", "#e0c99a", "#f5ebcf"]


def _setup_ax(ax, fig):
    """Apply global dark theme to a single axes."""
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID, linewidth=0.5, alpha=0.6)
    ax.grid(axis="x", color=GRID, linewidth=0.5, alpha=0.6)


def _new(w=10, h=5.5):
    fig, ax = plt.subplots(figsize=(w, h))
    _setup_ax(ax, fig)
    return fig, ax


def _font(ax, title=None, xlabel=None, ylabel=None, title_size=13):
    if title:
        ax.set_title(title, fontsize=title_size, color=TEXT, fontweight="bold",
                     pad=14, loc="left")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=MUTED, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10, color=MUTED, labelpad=8)


# ── 1. BAR — current prices ───────────────────────────────────────────────────
def bar_current_prices(df: pd.DataFrame, top_n: int = 15) -> plt.Figure:
    if df.empty:
        return None
    latest = df[df["year"] == df["year"].max()]
    avg = latest.groupby("name")["dollar_price"].mean().nlargest(top_n).sort_values()

    fig, ax = _new(9, max(4, len(avg) * 0.42))

    colors = [GOLD if v == avg.max() else "#2a2a2a" for v in avg.values]
    bars = ax.barh(avg.index, avg.values, color=colors, height=0.7, edgecolor="none")

    # value labels
    for bar, val in zip(bars, avg.values):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                f"${val:.2f}", va="center", fontsize=8.5,
                color=GOLD if val == avg.max() else MUTED,
                fontfamily="monospace")

    # US reference line
    us_price = df[(df["year"] == df["year"].max()) & (df["name"] == "United States")]["dollar_price"].mean()
    if not np.isnan(us_price):
        ax.axvline(us_price, color=MUTED, linewidth=1, linestyle="--", alpha=0.5)
        ax.text(us_price + 0.05, len(avg) - 0.5, f"US ${us_price:.2f}",
                color=MUTED, fontsize=8, fontfamily="monospace", va="top")

    ax.set_xlim(0, avg.max() * 1.22)
    ax.grid(axis="x", color=GRID, linewidth=0.4)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}"))
    _font(ax, xlabel="Price (USD)")
    fig.tight_layout()
    return fig


# ── 2. LOLLIPOP — over/under-valued ──────────────────────────────────────────
def lollipop_overunder(df: pd.DataFrame, val_col: str = "usd_raw", top_n: int = 20) -> plt.Figure:
    if df.empty or val_col not in df.columns:
        return None
    latest = df[df["year"] == df["year"].max()]
    avg = latest.groupby("name")[val_col].mean().dropna()
    avg = avg.reindex(avg.abs().nlargest(top_n).index).sort_values()

    fig, ax = _new(8, max(4, len(avg) * 0.42))
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)

    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)

    for i, (country, val) in enumerate(avg.items()):
        col = GREEN if val > 0 else RED
        ax.hlines(i, 0, val, color=col, linewidth=1.5, alpha=0.7)
        ax.scatter(val, i, color=col, s=40, zorder=5, edgecolors="none")

    ax.axvline(0, color=MUTED, linewidth=0.8, linestyle="-", alpha=0.4)
    ax.set_yticks(range(len(avg)))
    ax.set_yticklabels(avg.index, fontsize=8.5, color=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=0.4, alpha=0.5)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    _font(ax, xlabel="Over- / Under-Valued vs USD (%)")
    fig.tight_layout()
    return fig


# ── 3. LINE — global average trend ───────────────────────────────────────────
def line_global_avg(df: pd.DataFrame) -> plt.Figure:
    if df.empty:
        return None
    trend = df.groupby("year")["dollar_price"].agg(["mean", "median", "std"]).reset_index()

    fig, ax = _new(9, 5)
    ax.fill_between(
        trend["year"],
        trend["mean"] - trend["std"],
        trend["mean"] + trend["std"],
        color=GOLD, alpha=0.08, label="±1 std dev"
    )
    ax.plot(trend["year"], trend["median"], color=MUTED, linewidth=1,
            linestyle="--", label="Median", zorder=3)
    ax.plot(trend["year"], trend["mean"], color=GOLD, linewidth=2.5,
            label="Mean", zorder=4)
    ax.scatter(trend["year"], trend["mean"], color=GOLD, s=50,
               zorder=5, edgecolors=CARD, linewidth=1.5)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.2f}"))
    ax.set_xticks(trend["year"].unique()[::2])
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=9, framealpha=0, labelcolor=MUTED)
    _font(ax, ylabel="Price (USD)")
    fig.tight_layout()
    return fig


# ── 4. RIDGELINE — price distribution per year ───────────────────────────────
def ridgeline_years(df: pd.DataFrame) -> plt.Figure:
    if df.empty:
        return None
    years = sorted(df["year"].unique())
    n = len(years)
    fig, axes = plt.subplots(n, 1, figsize=(8, max(5, n * 0.65)), sharex=True)
    fig.patch.set_facecolor(CARD)
    if n == 1:
        axes = [axes]

    for i, (ax, yr) in enumerate(zip(axes, years)):
        data = df[df["year"] == yr]["dollar_price"].dropna()
        if len(data) < 2:
            continue
        ax.set_facecolor(CARD)
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        alpha_val = 0.3 + 0.7 * (i / max(n - 1, 1))
        color = GOLD
        try:
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(data)
            xs  = np.linspace(data.min(), data.max(), 200)
            ys  = kde(xs)
            ax.fill_between(xs, ys, color=color, alpha=alpha_val * 0.5)
            ax.plot(xs, ys, color=color, linewidth=1, alpha=alpha_val)
        except Exception:
            ax.hist(data, bins=15, color=color, alpha=0.4, density=True)

        ax.text(ax.get_xlim()[0] if i == 0 else df["dollar_price"].min(),
                ax.get_ylim()[1] * 0.5 if ax.get_ylim()[1] > 0 else 0.5,
                str(yr), fontsize=8, color=MUTED, fontfamily="monospace", va="center")
        ax.set_xlim(df["dollar_price"].min() - 0.5, df["dollar_price"].max() + 0.5)

    axes[-1].tick_params(colors=MUTED, labelsize=8)
    axes[-1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}"))
    fig.text(0.5, -0.01, "Price (USD)", ha="center", fontsize=9, color=MUTED)
    fig.subplots_adjust(hspace=-0.3)
    fig.tight_layout()
    return fig


# ── 5. HEATMAP — country × year ──────────────────────────────────────────────
def heatmap_country_year(df: pd.DataFrame, top_n: int = 15) -> plt.Figure:
    if df.empty:
        return None
    top_countries = df.groupby("name")["dollar_price"].mean().nlargest(top_n).index
    subset = df[df["name"].isin(top_countries)]
    pivot  = subset.pivot_table(index="name", columns="year",
                                values="dollar_price", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(14, max(5, len(pivot) * 0.5)))
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "bm_gold", ["#0f0f0f", "#3a2400", GOLD_DK, GOLD, GOLD_LT], N=256
    )
    sns.heatmap(pivot, cmap=cmap, ax=ax, linewidths=0.3,
                linecolor="#111", cbar_kws={"shrink": 0.6, "pad": 0.01},
                fmt=".1f", annot=len(pivot.columns) <= 15,
                annot_kws={"size": 7.5, "color": BG})

    ax.tick_params(colors=MUTED, labelsize=9)
    ax.set_xlabel("Year", fontsize=9, color=MUTED, labelpad=6)
    ax.set_ylabel("", fontsize=9)
    ax.tick_params(axis="x", rotation=45)

    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.set_tick_params(color=MUTED, labelsize=8)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=MUTED)
    cbar.set_label("Avg Price (USD)", color=MUTED, fontsize=8)

    fig.tight_layout()
    return fig


# ── 6. SCATTER — raw vs GDP-adjusted ─────────────────────────────────────────
def scatter_raw_vs_adj(df: pd.DataFrame) -> plt.Figure:
    if df.empty or "usd_raw" not in df.columns or "usd_adjusted" not in df.columns:
        return None
    latest = df[df["year"] == df["year"].max()].dropna(subset=["usd_raw", "usd_adjusted"])

    fig, ax = _new(8, 6)
    ax.scatter(latest["usd_raw"], latest["usd_adjusted"],
               color=GOLD, alpha=0.7, s=55, edgecolors=CARD, linewidth=0.8, zorder=4)

    # Labels for extreme points
    extremes = pd.concat([
        latest.nlargest(4, "usd_raw"),
        latest.nsmallest(4, "usd_raw"),
    ]).drop_duplicates()
    for _, row in extremes.iterrows():
        ax.annotate(row["name"],
                    (row["usd_raw"], row["usd_adjusted"]),
                    fontsize=7.5, color=MUTED, fontfamily="monospace",
                    xytext=(5, 5), textcoords="offset points")

    ax.axhline(0, color=MUTED, linewidth=0.7, linestyle="--", alpha=0.4)
    ax.axvline(0, color=MUTED, linewidth=0.7, linestyle="--", alpha=0.4)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    _font(ax, xlabel="Raw Index (%)", ylabel="GDP-Adjusted Index (%)")
    fig.tight_layout()
    return fig


# ── 7. AREA — top N countries price trajectory ────────────────────────────────
def area_top_countries(df: pd.DataFrame, top_n: int = 8) -> plt.Figure:
    if df.empty:
        return None
    top_c = df.groupby("name")["dollar_price"].mean().nlargest(min(top_n, 8)).index
    subset = df[df["name"].isin(top_c)]
    trend  = subset.groupby(["year", "name"])["dollar_price"].mean().reset_index()

    fig, ax = _new(11, 5.5)
    colors = plt.cm.get_cmap("YlOrBr", len(top_c))
    for i, country in enumerate(top_c):
        cdata = trend[trend["name"] == country].sort_values("year")
        col = mcolors.to_hex(colors(i / max(len(top_c) - 1, 1)))
        ax.plot(cdata["year"], cdata["dollar_price"], color=col,
                linewidth=2, label=country, zorder=4)
        ax.fill_between(cdata["year"], cdata["dollar_price"],
                        color=col, alpha=0.06)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.2f}"))
    ax.set_xticks(trend["year"].unique()[::2])
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=8, framealpha=0, labelcolor=MUTED,
              loc="upper left", ncol=2)
    _font(ax, ylabel="Price (USD)")
    fig.tight_layout()
    return fig


# ── 8. VIOLIN — price by region ──────────────────────────────────────────────
REGION_MAP = {
    "United States": "North America", "Canada": "North America", "Mexico": "Latin America",
    "Brazil": "Latin America", "Argentina": "Latin America", "Chile": "Latin America",
    "Colombia": "Latin America", "Peru": "Latin America", "Venezuela": "Latin America",
    "United Kingdom": "Europe", "Euro area": "Europe", "Norway": "Europe",
    "Sweden": "Europe", "Denmark": "Europe", "Switzerland": "Europe",
    "Poland": "Europe", "Czech Republic": "Europe", "Hungary": "Europe",
    "Russia": "Europe", "Turkey": "Europe", "Ukraine": "Europe",
    "China": "Asia-Pacific", "Japan": "Asia-Pacific", "South Korea": "Asia-Pacific",
    "Australia": "Asia-Pacific", "New Zealand": "Asia-Pacific",
    "Indonesia": "Asia-Pacific", "Malaysia": "Asia-Pacific",
    "Philippines": "Asia-Pacific", "Thailand": "Asia-Pacific", "India": "Asia-Pacific",
    "Pakistan": "Asia-Pacific", "Sri Lanka": "Asia-Pacific", "Taiwan": "Asia-Pacific",
    "Hong Kong": "Asia-Pacific", "Singapore": "Asia-Pacific",
    "South Africa": "Africa & ME", "Egypt": "Africa & ME",
    "Saudi Arabia": "Africa & ME", "Israel": "Africa & ME", "UAE": "Africa & ME",
}

def violin_regions(df: pd.DataFrame) -> plt.Figure:
    if df.empty:
        return None
    df2 = df.copy()
    df2["region"] = df2["name"].map(REGION_MAP).fillna("Other")

    fig, ax = _new(9, 5.5)
    order = df2.groupby("region")["dollar_price"].median().sort_values(ascending=False).index.tolist()
    pal   = {r: GOLD if i == 0 else f"#{max(0x1a, 0x60 - i*0x08):02x}{max(0x10, 0x40 - i*0x06):02x}{max(0x00, 0x00):02x}"
             for i, r in enumerate(order)}

    sns.violinplot(data=df2, x="region", y="dollar_price", order=order,
                   hue="region", palette=pal, legend=False,
                   inner="quartile", ax=ax, cut=0, linewidth=0.8)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.2f}"))
    ax.grid(axis="y", color=GRID, linewidth=0.4)
    ax.grid(axis="x", visible=False)
    _font(ax, ylabel="Price (USD)")
    fig.tight_layout()
    return fig


# ── 9. HORIZONTAL BAR — biggest movers ───────────────────────────────────────
def bar_most_changed(df: pd.DataFrame, top_n: int = 15) -> plt.Figure:
    if df.empty:
        return None
    first_yr = df["year"].min()
    last_yr  = df["year"].max()
    first = df[df["year"] == first_yr].groupby("name")["dollar_price"].mean()
    last  = df[df["year"] == last_yr].groupby("name")["dollar_price"].mean()
    change = ((last - first) / first * 100).dropna().sort_values()
    change = pd.concat([change.head(8), change.tail(8)]).drop_duplicates()

    fig, ax = _new(9, max(4, len(change) * 0.48))
    colors = [GREEN if v > 0 else RED for v in change.values]
    ax.barh(change.index, change.values, color=colors, height=0.65,
            alpha=0.85, edgecolor="none")
    ax.axvline(0, color=MUTED, linewidth=0.8, alpha=0.4)
    for val, y in zip(change.values, range(len(change))):
        ax.text(val + (1 if val > 0 else -1), y,
                f"{val:+.0f}%", va="center", fontsize=8,
                color=GREEN if val > 0 else RED, fontfamily="monospace")
    ax.set_xlim(change.min() * 1.25, change.max() * 1.25)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.grid(axis="x", color=GRID, linewidth=0.4)
    ax.grid(axis="y", visible=False)
    _font(ax, xlabel=f"Price Change {first_yr}→{last_yr}")
    fig.tight_layout()
    return fig


# ── 10. HISTOGRAM — global price dist ────────────────────────────────────────
def hist_price_dist(df: pd.DataFrame) -> plt.Figure:
    if df.empty:
        return None
    fig, ax = _new(8, 5)
    prices = df["dollar_price"].dropna()

    n, bins, patches = ax.hist(prices, bins=40, color=GOLD, alpha=0.75,
                                edgecolor=CARD, linewidth=0.5)
    # Color the tallest bar gold, rest darker
    max_n = n.max()
    for patch, h in zip(patches, n):
        patch.set_facecolor(GOLD if h == max_n else GOLD_DK)
        patch.set_alpha(0.6 + 0.4 * (h / max_n))

    ax.axvline(prices.mean(), color=TEXT, linewidth=1.5, linestyle="--",
               label=f"Mean ${prices.mean():.2f}", zorder=5)
    ax.axvline(prices.median(), color=MUTED, linewidth=1, linestyle=":",
               label=f"Median ${prices.median():.2f}", zorder=5)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}"))
    ax.legend(fontsize=9, framealpha=0, labelcolor=MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.4)
    ax.grid(axis="x", visible=False)
    _font(ax, xlabel="Price (USD)", ylabel="Frequency")
    fig.tight_layout()
    return fig


# ── 11. BOX — per year ───────────────────────────────────────────────────────
def box_by_year(df: pd.DataFrame) -> plt.Figure:
    if df.empty:
        return None
    years = sorted(df["year"].unique())
    fig, ax = _new(12, 5)

    cmap   = plt.cm.get_cmap("YlOrBr", len(years))
    colors = [mcolors.to_hex(cmap(i / max(len(years) - 1, 1))) for i in range(len(years))]

    data_by_year = [df[df["year"] == yr]["dollar_price"].dropna().values for yr in years]
    bp = ax.boxplot(data_by_year, patch_artist=True, vert=True,
                    medianprops=dict(color=TEXT, linewidth=1.5),
                    whiskerprops=dict(color=MUTED, linewidth=0.8),
                    capprops=dict(color=MUTED, linewidth=0.8),
                    flierprops=dict(marker=".", color=MUTED, alpha=0.3, markersize=3))

    for patch, col in zip(bp["boxes"], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)
        patch.set_edgecolor(GRID)

    ax.set_xticks(range(1, len(years) + 1))
    ax.set_xticklabels(years, rotation=45, fontsize=8.5, color=MUTED)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.2f}"))
    ax.grid(axis="y", color=GRID, linewidth=0.4)
    ax.grid(axis="x", visible=False)
    _font(ax, ylabel="Price (USD)")
    fig.tight_layout()
    return fig


# ── 12. BUBBLE — country summary ─────────────────────────────────────────────
def bubble_country_summary(df: pd.DataFrame, val_col: str = "usd_raw") -> plt.Figure:
    if df.empty:
        return None
    agg = (
        df.groupby("name")
        .agg(
            avg_price=("dollar_price", "mean"),
            index_val=(val_col, "mean"),
            obs=("dollar_price", "count"),
        )
        .dropna()
        .reset_index()
    )

    fig, ax = _new(11, 7)
    scatter = ax.scatter(
        agg["avg_price"], agg["index_val"],
        s=agg["obs"] * 4,
        c=agg["avg_price"],
        cmap=mcolors.LinearSegmentedColormap.from_list(
            "bm", [CARD, GOLD_DK, GOLD, GOLD_LT], N=256),
        alpha=0.75,
        edgecolors=GRID, linewidth=0.5,
        zorder=4,
    )

    # Label the most interesting ones
    for _, row in agg.nlargest(5, "avg_price").iterrows():
        ax.annotate(row["name"], (row["avg_price"], row["index_val"]),
                    fontsize=7.5, color=MUTED, fontfamily="monospace",
                    xytext=(6, 3), textcoords="offset points")
    for _, row in agg.nsmallest(5, "avg_price").iterrows():
        ax.annotate(row["name"], (row["avg_price"], row["index_val"]),
                    fontsize=7.5, color=MUTED, fontfamily="monospace",
                    xytext=(6, 3), textcoords="offset points")

    cbar = plt.colorbar(scatter, ax=ax, shrink=0.7, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=MUTED, labelsize=8)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=MUTED)
    cbar.set_label("Avg Price (USD)", color=MUTED, fontsize=8)
    cbar.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.2f}"))

    ax.axhline(0, color=MUTED, linewidth=0.7, linestyle="--", alpha=0.3)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.2f}"))
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    _font(ax, xlabel="Average Price (USD)", ylabel=f"{val_col.replace('_',' ').title()} (%)")

    # Bubble size legend
    for sz in [5, 10, 20]:
        ax.scatter([], [], s=sz * 4, color=GOLD, alpha=0.5,
                   label=f"{sz} obs", edgecolors=GRID, linewidth=0.5)
    ax.legend(title="Observations", fontsize=8, framealpha=0,
              labelcolor=MUTED, title_fontsize=8)

    fig.tight_layout()
    return fig
