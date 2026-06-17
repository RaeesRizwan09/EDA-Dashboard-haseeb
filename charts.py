import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
import base64
import charts
import filters

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Big Mac Index · Global Purchasing Power",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ─── Base ─── */
html, body, .stApp {
    background: #0a0a0a !important;
    font-family: 'DM Sans', sans-serif;
    color: #e8e0d4;
}
.block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1500px;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: #0f0f0f !important;
    border-right: 1px solid #1e1e1e;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    color: #666 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {
    background: #c8a96e !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div > div {
    background: #c8a96e !important;
    border: 2px solid #0f0f0f;
}

/* ─── Dividers ─── */
hr {
    border-color: #1e1e1e !important;
}

/* ─── Header ─── */
.hero-wrap {
    position: relative;
    overflow: hidden;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    background: #0f0f0f;
    padding: 48px 52px 40px;
    margin-bottom: 36px;
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse 70% 60% at 80% 50%, rgba(200,169,110,0.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: #c8a96e;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.hero-eyebrow::after {
    content: '';
    flex: 1;
    max-width: 60px;
    height: 1px;
    background: #c8a96e;
    opacity: 0.4;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 56px;
    font-weight: 900;
    color: #e8e0d4;
    line-height: 1.05;
    letter-spacing: -1.5px;
    margin: 0 0 6px;
}
.hero-title em {
    font-style: italic;
    color: #c8a96e;
}
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    color: #555;
    margin-top: 16px;
    max-width: 560px;
    line-height: 1.7;
    font-weight: 300;
}
.hero-tag-row {
    display: flex;
    gap: 8px;
    margin-top: 28px;
    flex-wrap: wrap;
}
.hero-tag {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    color: #444;
    border: 1px solid #222;
    border-radius: 2px;
    padding: 5px 10px;
    text-transform: uppercase;
}

/* ─── Section headings ─── */
.sec-head {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin: 40px 0 24px;
    border-bottom: 1px solid #1a1a1a;
    padding-bottom: 14px;
}
.sec-num {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #c8a96e;
    letter-spacing: 2px;
    opacity: 0.7;
}
.sec-title {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 700;
    color: #e8e0d4;
    letter-spacing: -0.3px;
    margin: 0;
}

/* ─── KPI / Stat cards ─── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #1a1a1a;
    border: 1px solid #1a1a1a;
    margin-bottom: 28px;
}
.kpi-card {
    background: #0f0f0f;
    padding: 28px 24px;
    position: relative;
    overflow: hidden;
    transition: background 0.3s;
}
.kpi-card:hover { background: #141414; }
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 24px; right: 24px;
    height: 2px;
    background: linear-gradient(90deg, #c8a96e, transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.kpi-card:hover::after { opacity: 1; }
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    color: #444;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    color: #c8a96e;
    line-height: 1;
    letter-spacing: -1px;
}
.kpi-delta {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #555;
    margin-top: 6px;
}
.kpi-delta.up { color: #6fcf97; }
.kpi-delta.down { color: #eb5757; }

/* ─── Chart wrapper ─── */
.chart-shell {
    background: #0f0f0f;
    border: 1px solid #1a1a1a;
    border-radius: 3px;
    padding: 0;
    margin-bottom: 16px;
    overflow: hidden;
    position: relative;
}
.chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 22px 14px;
    border-bottom: 1px solid #1a1a1a;
}
.chart-title {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    color: #555;
    text-transform: uppercase;
}
.chart-body {
    padding: 0;
}
.chart-body img {
    width: 100%;
    height: auto;
    display: block;
}
.dl-btn {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    color: #333;
    border: 1px solid #222;
    border-radius: 2px;
    padding: 4px 10px;
    text-decoration: none;
    text-transform: uppercase;
    transition: all 0.2s;
}
.dl-btn:hover {
    color: #c8a96e;
    border-color: #c8a96e;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1a1a1a !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #444 !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 24px !important;
    border-radius: 0 !important;
    transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #888 !important;
}
.stTabs [aria-selected="true"] {
    color: #c8a96e !important;
    border-bottom: 2px solid #c8a96e !important;
    background: transparent !important;
}

/* ─── Data table ─── */
[data-testid="stDataFrame"] {
    border: 1px solid #1a1a1a !important;
    border-radius: 3px !important;
}

/* ─── Buttons ─── */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    background: transparent !important;
    color: #c8a96e !important;
    border: 1px solid #c8a96e !important;
    border-radius: 2px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(200,169,110,0.1) !important;
}

/* ─── Download button ─── */
.stDownloadButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    background: transparent !important;
    color: #555 !important;
    border: 1px solid #222 !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    color: #c8a96e !important;
    border-color: #c8a96e !important;
}

/* ─── Filter badge ─── */
.fbadge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    color: #c8a96e;
    background: rgba(200,169,110,0.08);
    border: 1px solid rgba(200,169,110,0.2);
    border-radius: 2px;
    padding: 4px 10px;
    margin: 3px;
}

/* ─── Insight callout ─── */
.insight-box {
    background: #0f0f0f;
    border-left: 3px solid #c8a96e;
    padding: 18px 22px;
    margin: 12px 0 24px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: #888;
    line-height: 1.7;
    font-weight: 300;
}
.insight-box strong {
    color: #e8e0d4;
    font-weight: 500;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #333; }

/* ─── Multiselect & selectbox ─── */
[data-baseweb="select"] > div:first-child {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 2px !important;
}

/* ─── Alert ─── */
[data-testid="stAlert"] {
    background: #0f0f0f !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 3px !important;
    color: #555 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["dollar_price"] = pd.to_numeric(df["dollar_price"], errors="coerce")
    df["usd_raw"] = pd.to_numeric(df["usd_raw"], errors="coerce")
    df["usd_adjusted"] = pd.to_numeric(df["usd_adjusted"], errors="coerce")
    df.dropna(subset=["dollar_price"], inplace=True)
    return df


DATA_PATH = os.path.join("data", "big-mac.csv")

if not os.path.exists(DATA_PATH):
    st.markdown("""
    <div style="padding:80px 40px;text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:3px;color:#c8a96e;margin-bottom:20px;">
            DATA NOT FOUND
        </div>
        <div style="font-family:'Playfair Display',serif;font-size:36px;color:#e8e0d4;margin-bottom:16px;">
            Place <em style="color:#c8a96e;">big-mac.csv</em> in the data/ folder
        </div>
        <div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#555;max-width:500px;margin:0 auto;">
            Download from:<br>
            <code style="color:#888;font-size:12px;">
            https://github.com/rfordatascience/tidytuesday/blob/main/data/2020/2020-12-22/big-mac.csv
            </code>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df = load_data(DATA_PATH)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 0 8px;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:3px;color:#c8a96e;text-transform:uppercase;">
            Controls
        </div>
        <div style="font-family:'Playfair Display',serif;font-size:20px;color:#e8e0d4;margin-top:6px;">
            Filter & Explore
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    all_countries = sorted(df["name"].dropna().unique().tolist())

    if "reset" not in st.session_state:
        st.session_state.reset = False

    sfx = "_r" if st.session_state.reset else ""

    selected_years = st.sidebar.slider(
        "Year Range",
        min_value=min_year, max_value=max_year,
        value=(min_year, max_year), key=f"yr{sfx}"
    )
    selected_countries = st.sidebar.multiselect(
        "Countries",
        options=all_countries, default=[],
        key=f"cc{sfx}", help="Leave blank for all countries"
    )
    val_type = st.sidebar.radio(
        "Price Metric",
        ["Raw USD Index", "GDP-Adjusted Index"],
        key=f"vm{sfx}"
    )
    top_n = st.sidebar.slider(
        "Top N Countries in Charts", 5, 30, 15, key=f"tn{sfx}"
    )

    st.divider()
    if st.button("↺  Reset Filters"):
        st.session_state.reset = not st.session_state.reset
        st.rerun()

    if st.session_state.reset:
        st.session_state.reset = False

    st.markdown("""
    <div style="padding:20px 0 0;font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;color:#2a2a2a;line-height:2;">
        SOURCE · The Economist<br>
        DATASET · TidyTuesday 2020<br>
        VIZ · Big Mac Index Dashboard
    </div>
    """, unsafe_allow_html=True)


# ── FILTER DATA ───────────────────────────────────────────────────────────────
filtered = filters.apply_filters(df, selected_years, selected_countries)
val_col = "usd_raw" if val_type == "Raw USD Index" else "usd_adjusted"

# ── HERO HEADER ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">The Economist · Big Mac Index</div>
    <div class="hero-title">The World Through a<br><em>Single Burger</em></div>
    <div class="hero-sub">
        Purchasing power parity, visualised through the world's most iconic fast-food item.
        Tracking {df['name'].nunique()} countries from {min_year} to {max_year}.
    </div>
    <div class="hero-tag-row">
        <span class="hero-tag">PPP Analysis</span>
        <span class="hero-tag">{len(df):,} Observations</span>
        <span class="hero-tag">{df['name'].nunique()} Countries</span>
        <span class="hero-tag">{max_year - min_year + 1} Years</span>
        <span class="hero-tag">The Economist Dataset</span>
    </div>
</div>
""", unsafe_allow_html=True)

# active filter badges
active = []
if selected_years != (min_year, max_year):
    active.append(f"Years {selected_years[0]}–{selected_years[1]}")
if selected_countries:
    active.append(f"{len(selected_countries)} countries selected")
if active:
    badges = "".join(f'<span class="fbadge">◈ {a}</span>' for a in active)
    st.markdown(f'<div style="margin-bottom:20px;">{badges}</div>', unsafe_allow_html=True)


if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()


# ── KPI CARDS ────────────────────────────────────────────────────────────────
latest_year = filtered["year"].max()
latest = filtered[filtered["year"] == latest_year]
prev_year = latest_year - 1
prev = filtered[filtered["year"] == prev_year]

avg_price_now  = latest["dollar_price"].mean()
avg_price_prev = prev["dollar_price"].mean() if not prev.empty else avg_price_now
price_chg      = ((avg_price_now - avg_price_prev) / avg_price_prev * 100) if avg_price_prev else 0

most_expensive = latest.loc[latest["dollar_price"].idxmax(), "name"] if not latest.empty else "N/A"
cheapest       = latest.loc[latest["dollar_price"].idxmin(), "name"] if not latest.empty else "N/A"
spread         = latest["dollar_price"].max() - latest["dollar_price"].min() if not latest.empty else 0
n_countries    = filtered["name"].nunique()

delta_class = "up" if price_chg >= 0 else "down"
delta_arrow = "↑" if price_chg >= 0 else "↓"

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Avg. Big Mac Price ({latest_year})</div>
        <div class="kpi-value">${avg_price_now:.2f}</div>
        <div class="kpi-delta {delta_class}">{delta_arrow} {abs(price_chg):.1f}% vs {prev_year}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Most Expensive ({latest_year})</div>
        <div class="kpi-value" style="font-size:28px;">{most_expensive}</div>
        <div class="kpi-delta">${latest.loc[latest['dollar_price'].idxmax(),'dollar_price']:.2f} USD</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Most Affordable ({latest_year})</div>
        <div class="kpi-value" style="font-size:28px;">{cheapest}</div>
        <div class="kpi-delta">${latest.loc[latest['dollar_price'].idxmin(),'dollar_price']:.2f} USD</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Countries Tracked</div>
        <div class="kpi-value">{n_countries}</div>
        <div class="kpi-delta">Price spread: ${spread:.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── RENDER CHART HELPER ───────────────────────────────────────────────────────
def render_chart(fig, title: str, fname: str):
    if fig is None:
        return
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.markdown(f"""
    <div class="chart-shell">
        <div class="chart-header">
            <span class="chart-title">{title}</span>
            <a class="dl-btn" href="data:image/png;base64,{b64}" download="{fname}_{ts}.png">↓ Export</a>
        </div>
        <div class="chart-body">
            <img src="data:image/png;base64,{b64}" alt="{title}" />
        </div>
    </div>
    """, unsafe_allow_html=True)
    plt.close(fig)


# ════════════════════════════════════════════════════════════════════════════
#  SECTION A · PRICE LANDSCAPE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head">
    <span class="sec-num">01 ——</span>
    <span class="sec-title">Price Landscape</span>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([3, 2])
with c1:
    fig = charts.bar_current_prices(filtered, top_n)
    render_chart(fig, "BIG MAC PRICE BY COUNTRY · LATEST YEAR (USD)", "price_ranking")
with c2:
    fig = charts.lollipop_overunder(filtered, val_col, top_n)
    render_chart(fig, f"OVER / UNDER-VALUED vs USD · {val_type.upper()}", "over_under_valued")

st.markdown("""
<div class="insight-box">
    <strong>Reading this:</strong> The lollipop chart shows each currency's valuation relative to the US dollar.
    Bars extending right indicate an <strong>over-valued</strong> currency; bars left indicate <strong>under-valued</strong>.
    A Big Mac costing less than in the US implies the local currency has more purchasing power per dollar.
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  SECTION B · TIME EVOLUTION
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head">
    <span class="sec-num">02 ——</span>
    <span class="sec-title">Price Evolution Over Time</span>
</div>
""", unsafe_allow_html=True)

c3, c4 = st.columns(2)
with c3:
    fig = charts.line_global_avg(filtered)
    render_chart(fig, "GLOBAL AVERAGE PRICE TREND · ALL COUNTRIES", "global_avg_trend")
with c4:
    fig = charts.ridgeline_years(filtered)
    render_chart(fig, "PRICE DISTRIBUTION · EACH YEAR", "distribution_years")

fig = charts.heatmap_country_year(filtered, top_n)
render_chart(fig, f"PRICE HEATMAP · TOP {top_n} COUNTRIES × YEAR (USD)", "heatmap_country_year")


# ════════════════════════════════════════════════════════════════════════════
#  SECTION C · VALUATION ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head">
    <span class="sec-num">03 ——</span>
    <span class="sec-title">Valuation & PPP Analysis</span>
</div>
""", unsafe_allow_html=True)

c5, c6 = st.columns([2, 3])
with c5:
    fig = charts.scatter_raw_vs_adj(filtered)
    render_chart(fig, "RAW vs GDP-ADJUSTED INDEX", "raw_vs_adjusted")
with c6:
    fig = charts.area_top_countries(filtered, top_n)
    render_chart(fig, f"PRICE TRAJECTORIES · TOP {top_n} COUNTRIES", "top_countries_area")

c7, c8 = st.columns(2)
with c7:
    fig = charts.violin_regions(filtered)
    render_chart(fig, "PRICE SPREAD BY REGION", "violin_regions")
with c8:
    fig = charts.bar_most_changed(filtered)
    render_chart(fig, "BIGGEST PRICE MOVERS (FIRST→LAST YEAR)", "biggest_movers")


# ════════════════════════════════════════════════════════════════════════════
#  SECTION D · STATISTICAL DEEP DIVE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head">
    <span class="sec-num">04 ——</span>
    <span class="sec-title">Statistical Deep Dive</span>
</div>
""", unsafe_allow_html=True)

c9, c10 = st.columns(2)
with c9:
    fig = charts.hist_price_dist(filtered)
    render_chart(fig, "GLOBAL PRICE DISTRIBUTION (USD)", "price_distribution")
with c10:
    fig = charts.box_by_year(filtered)
    render_chart(fig, "PRICE SPREAD PER YEAR · BOX PLOT", "box_per_year")

fig = charts.bubble_country_summary(filtered, val_col)
render_chart(fig, "COUNTRY SUMMARY · PRICE × INDEX × OBSERVATIONS (BUBBLE SIZE)", "country_bubble")


# ════════════════════════════════════════════════════════════════════════════
#  SECTION E · DATA TABLE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head">
    <span class="sec-num">05 ——</span>
    <span class="sec-title">Data Explorer</span>
</div>
""", unsafe_allow_html=True)

tab_summary, tab_raw = st.tabs(["Country Summary", "Raw Data"])

with tab_summary:
    summary = (
        filtered.groupby("name")
        .agg(
            avg_price=("dollar_price", "mean"),
            min_price=("dollar_price", "min"),
            max_price=("dollar_price", "max"),
            avg_raw_index=("usd_raw", "mean"),
            avg_adj_index=("usd_adjusted", "mean"),
            observations=("dollar_price", "count"),
        )
        .round(3)
        .sort_values("avg_price", ascending=False)
        .reset_index()
    )
    summary.columns = ["Country", "Avg Price ($)", "Min Price ($)", "Max Price ($)",
                        "Avg Raw Index", "Avg Adj Index", "Observations"]
    st.dataframe(summary, width='stretch', height=400)
    st.download_button(
        "↓ Download Country Summary",
        summary.to_csv(index=False),
        file_name=f"bigmac_country_summary_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab_raw:
    disp_cols = ["date", "name", "iso_a3", "dollar_price", "usd_raw", "usd_adjusted", "year"]
    avail = [c for c in disp_cols if c in filtered.columns]
    st.dataframe(
        filtered[avail].sort_values("date", ascending=False),
        width='stretch', height=400
    )
    st.download_button(
        "↓ Download Filtered Data",
        filtered[avail].to_csv(index=False),
        file_name=f"bigmac_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:60px;padding:32px 0 12px;border-top:1px solid #141414;
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
    <div style="font-family:'Playfair Display',serif;font-size:18px;color:#2a2a2a;font-style:italic;">
        Big Mac Index Dashboard
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2px;color:#2a2a2a;text-transform:uppercase;">
        Data: The Economist · TidyTuesday 2020 · Built with Streamlit
    </div>
</div>
""", unsafe_allow_html=True)
