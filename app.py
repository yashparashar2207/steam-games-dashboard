"""Interactive dashboard for the Steam games dataset."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Steam Games Explorer", page_icon="🎮", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink:#eef6ff; --muted:#91a9bb; --line:rgba(102,192,244,.16); --panel:#101d2a; --steam:#66c0f4; --cyan:#35d0e8; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:radial-gradient(ellipse at 14% 0%,rgba(28,105,151,.25),transparent 36%),radial-gradient(ellipse at 86% 8%,rgba(18,151,184,.12),transparent 29%),linear-gradient(145deg,#07111d 0%,#081522 52%,#07101b 100%); color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(8,13,24,.72); }
    [data-testid="stAppViewContainer"] > .main .block-container { max-width:1580px; padding-top:2.1rem; padding-bottom:4rem; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#0e1b28 0%,#0a1521 100%); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { font-family:'Space Grotesk',sans-serif; letter-spacing:-.02em; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#aeb8cd; }
    [data-testid="stSidebar"] label { color:#d7deef !important; font-size:.88rem !important; }
    [data-testid="stSidebar"] [data-baseweb="input"], [data-testid="stSidebar"] [data-baseweb="select"] > div { background:#081522; border-color:rgba(102,192,244,.2); border-radius:9px; }
    [data-testid="stSidebar"] input[type="range"] { accent-color:#35b9ef; }
    .steam-nav { display:flex; align-items:center; gap:25px; min-height:48px; margin:0 0 13px; padding:0 7px; color:#91a9bb; font-size:.78rem; letter-spacing:.05em; text-transform:uppercase; }
    .steam-brand { display:flex; align-items:center; gap:9px; margin-right:8px; color:#e9f6ff; font:700 .96rem 'Space Grotesk',sans-serif; letter-spacing:.08em; }
    .steam-mark { display:grid; place-items:center; width:27px; height:27px; border-radius:50%; background:linear-gradient(145deg,#66c0f4,#168ac5); color:#071522; font-size:.87rem; box-shadow:0 0 18px rgba(42,175,232,.28); }
    .steam-nav .nav-current { color:#dff5ff; }
    .steam-live { margin-left:auto; padding:6px 10px; border:1px solid rgba(79,202,230,.24); border-radius:999px; color:#8ee6f1; background:rgba(30,159,191,.09); font-size:.66rem; font-weight:700; letter-spacing:.12em; }
    .hero { position:relative; overflow:hidden; padding:29px 33px 31px; margin:4px 0 22px; border:1px solid rgba(102,192,244,.28); border-radius:18px; background:linear-gradient(112deg,rgba(17,53,78,.97),rgba(13,39,59,.94) 55%,rgba(8,65,81,.87)); box-shadow:0 18px 55px rgba(0,0,0,.25),inset 0 1px rgba(255,255,255,.04); }
    .hero:after { content:''; position:absolute; width:360px; height:360px; right:-72px; top:-170px; border-radius:50%; background:rgba(61,195,226,.16); filter:blur(5px); }
    .hero:before { content:'STEAM  /  DATA'; position:absolute; right:34px; top:27px; color:rgba(181,226,250,.12); font:700 1.4rem 'Space Grotesk',sans-serif; letter-spacing:.14em; transform:rotate(90deg) translateX(100%); transform-origin:top right; }
    .hero-kicker { display:inline-flex; align-items:center; gap:8px; padding:6px 10px; border-radius:5px; background:rgba(102,192,244,.12); border:1px solid rgba(102,192,244,.27); color:#a9e2ff; font-size:.69rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }
    .hero h1 { margin:14px 0 6px; color:#f7f8ff; font:700 clamp(2rem,3.2vw,3.05rem)/1.08 'Space Grotesk',sans-serif; letter-spacing:-.055em; }
    .hero p { max-width:760px; margin:0; color:#b7c3dc; font-size:1rem; }
    .hero-note { position:absolute; right:28px; bottom:27px; z-index:1; color:#9be6f0; font-size:.78rem; letter-spacing:.04em; }
    [data-testid="stMetric"] { min-height:120px; padding:19px 21px; border:1px solid var(--line); border-radius:13px; background:linear-gradient(145deg,rgba(17,37,55,.97),rgba(12,27,42,.95)); box-shadow:0 12px 32px rgba(0,0,0,.19); }
    [data-testid="stMetricLabel"] p { color:#9fb8ca !important; font-size:.82rem !important; font-weight:600 !important; }
    [data-testid="stMetricValue"] { color:#f5f6ff !important; font:600 clamp(1.45rem,2vw,2rem)/1.2 'Space Grotesk',sans-serif !important; }
    [data-testid="stMetricDelta"] { color:#7bdcc9 !important; }
    [data-testid="stTabs"] { margin-top:14px; }
    [data-testid="stTabs"] [role="tablist"] { gap:8px; border-bottom:1px solid var(--line); }
    [data-testid="stTabs"] button[role="tab"] { padding:12px 17px; border-radius:11px 11px 0 0; color:#9eabc4; font-weight:600; }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color:#dff5ff; background:rgba(44,164,218,.12); box-shadow:inset 0 -2px #46c4ec; }
    [data-testid="stTabs"] button[role="tab"]:hover { color:#fff; }
    [data-testid="stPlotlyChart"] { margin:8px 0 15px; padding:11px 12px 4px; border:1px solid var(--line); border-radius:13px; background:linear-gradient(145deg,rgba(13,31,47,.91),rgba(9,23,36,.89)); box-shadow:0 12px 34px rgba(0,0,0,.17); }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
    h2, h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.025em; }
    [data-testid="stDownloadButton"] button { border:1px solid rgba(102,192,244,.42); border-radius:8px; background:rgba(35,151,206,.15); color:#dff5ff; font-weight:600; }
    [data-testid="stDownloadButton"] button:hover { border-color:#66c0f4; background:rgba(35,151,206,.26); color:white; }
    @media (max-width:800px) { .hero { padding:22px; } .hero-note { position:static; display:block; margin-top:13px; } [data-testid="stMetric"] { min-height:100px; padding:15px; } }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_ZIP = Path(
    r"C:\Users\Yash\OneDrive\Desktop\BCA\Sem 3\Descriptive Analytics\stem games mk 2.zip"
)
DEFAULT_CSV = Path(__file__).with_name("games.csv")
USE_COLS = [
    "AppID", "Name", "Release date", "Peak CCU", "Price", "Windows", "Mac", "Linux",
    "Positive", "Negative", "Recommendations", "Developers", "Publishers", "Genres",
]
CSV_COLUMNS = [
    "AppID", "Name", "Release date", "Estimated owners", "Peak CCU", "Required age",
    "Price", "DiscountDLC count", "About the game", "Supported languages",
    "Full audio languages", "Reviews", "Header image", "Website", "Support url",
    "Support email", "Windows", "Mac", "Linux", "Metacritic score", "Metacritic url",
    "User score", "Positive", "Negative", "Score rank", "Achievements",
    "Recommendations", "Notes", "Average playtime forever", "Average playtime two weeks",
    "Median playtime forever", "Median playtime two weeks", "Developers", "Publishers",
    "Categories", "Genres", "Tags", "Screenshots", "Movies",
]
# The supplied CSV has an extra, unnamed field immediately after DiscountDLC count.
# Name it explicitly so fields later in each row stay aligned with their real headers.
CSV_READ_COLUMNS = CSV_COLUMNS[:8] + ["_extra_source_field"] + CSV_COLUMNS[8:]


@st.cache_data(show_spinner="Loading the Steam games dataset…")
def load_games(data_path: str, modified: float) -> pd.DataFrame:
    """Read dashboard fields from the original CSV or from the CSV inside the source ZIP."""
    del modified  # included in the cache key so a replaced archive reloads
    source = Path(data_path)
    if source.suffix.lower() == ".csv":
        # The original source CSV has one extra, unnamed field after DiscountDLC
        # count. Supply an explicit shifted header so later values remain aligned.
        data = pd.read_csv(
            source, header=0, names=CSV_READ_COLUMNS,
            usecols=lambda col: col in USE_COLS,
            index_col=False, low_memory=False,
        )
    else:
        with zipfile.ZipFile(source) as archive:
            entry = "games.csv" if "games.csv" in archive.namelist() else next(
                (n for n in archive.namelist() if n.lower().endswith(".csv")), None
            )
            if entry is None:
                raise ValueError("The ZIP archive does not contain a CSV file.")
            with archive.open(entry) as csv_file:
                data = pd.read_csv(
                    csv_file, header=0, names=CSV_READ_COLUMNS,
                    usecols=lambda col: col in USE_COLS,
                    index_col=False, low_memory=False,
                )

    data["Price"] = pd.to_numeric(data["Price"], errors="coerce").fillna(0)
    for col in ["Peak CCU", "Positive", "Negative", "Recommendations"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    data["Release date"] = pd.to_datetime(data["Release date"], errors="coerce")
    data["Review count"] = data["Positive"] + data["Negative"]
    data["Positive review share"] = (
        data["Positive"] / data["Review count"].replace(0, pd.NA) * 100
    ).fillna(0)
    data["Review label"] = "No reviews"
    reviewed = data["Review count"] > 0
    data.loc[reviewed & (data["Positive review share"] >= 80), "Review label"] = "Very positive (80%+)"
    data.loc[reviewed & (data["Positive review share"] >= 70) & (data["Positive review share"] < 80), "Review label"] = "Mostly positive (70–79%)"
    data.loc[reviewed & (data["Positive review share"] >= 40) & (data["Positive review share"] < 70), "Review label"] = "Mixed (40–69%)"
    data.loc[reviewed & (data["Positive review share"] < 40), "Review label"] = "Mostly negative (<40%)"
    return data


def explode_values(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    result = frame[[column, "Name", "Price", "Positive", "Negative", "Peak CCU"]].copy()
    result[column] = result[column].fillna("").astype(str).str.split(",")
    result = result.explode(column)
    result[column] = result[column].str.strip()
    return result[result[column].ne("")]


def polish_chart(fig):
    """Apply a consistent, quiet dark theme to every interactive chart."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans, sans-serif", "color": "#aeb9d0", "size": 12},
        title={"font": {"family": "Space Grotesk, sans-serif", "size": 17, "color": "#edf0ff"}, "x": 0.025},
        margin={"l": 18, "r": 18, "t": 58, "b": 22},
        hoverlabel={"bgcolor": "#172239", "bordercolor": "#596783", "font": {"color": "#f4f6ff", "family": "DM Sans, sans-serif"}},
    )
    fig.update_xaxes(gridcolor="rgba(157,174,210,.12)", zerolinecolor="rgba(157,174,210,.20)", linecolor="rgba(157,174,210,.18)")
    fig.update_yaxes(gridcolor="rgba(157,174,210,.12)", zerolinecolor="rgba(157,174,210,.20)", linecolor="rgba(157,174,210,.18)")
    return fig


st.markdown(
    """
    <div class="steam-nav">
      <span class="steam-brand"><span class="steam-mark">⚙</span> STEAM INSIGHTS</span>
      <span class="nav-current">STORE ANALYTICS&nbsp; / &nbsp;PLAYER TRENDS&nbsp; / &nbsp;REVIEWS</span>
      <span class="steam-live">● LIVE CATALOG</span>
    </div>
    <section class="hero">
      <span class="hero-kicker">✦ PC GAMING · CATALOG INTELLIGENCE</span>
      <h1>Steam Games Explorer</h1>
      <p>Find your next favorite, track player momentum, and explore the Steam catalog from indie releases to blockbuster hits.</p>
      <span class="hero-note">125K+ games&nbsp;&nbsp; / &nbsp;&nbsp; reviews, trends & player stats</span>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Dataset")
    if DEFAULT_CSV.is_file():
        data_path = DEFAULT_CSV
        st.success("Full source dataset loaded")
        st.caption("Loaded from the original games.csv beside app.py.")
    else:
        zip_text = st.text_input("Path to source ZIP", value=str(DEFAULT_ZIP))
        uploaded = st.file_uploader("Or select the source ZIP", type="zip")
        if uploaded is not None:
            import tempfile
            temporary = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
            temporary.write(uploaded.getbuffer())
            temporary.close()
            zip_text = temporary.name
        st.caption("The ZIP should contain games.csv. The large JSON copy is not needed.")
        data_path = Path(zip_text).expanduser()

if not data_path.is_file():
    st.info("Add the original **games.csv** beside app.py, or enter the local source ZIP path in the sidebar.")
    st.stop()

try:
    games = load_games(str(data_path.resolve()), data_path.stat().st_mtime)
except Exception as exc:
    st.error(f"Could not read this dataset: {exc}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    years = games["Release date"].dt.year.dropna()
    if not years.empty:
        lo, hi = int(years.min()), int(years.max())
        if lo < hi:
            year_range = st.slider("Release year", lo, hi, (lo, hi))
        else:
            year_range = (lo, hi)
    else:
        year_range = (0, 9999)
    price_limit = float(games["Price"].max()) if len(games) else 0
    price_max = st.slider("Maximum price", 0.0, max(1.0, price_limit), max(1.0, price_limit), step=1.0)
    reviews_only = st.checkbox("Only games with reviews", value=False)
    platforms = st.multiselect("Platforms", ["Windows", "Mac", "Linux"])
    genres_available = sorted({g.strip() for s in games["Genres"].dropna().astype(str) for g in s.split(",") if g.strip()})
    genres = st.multiselect("Genres", genres_available)

filtered = games[games["Price"].le(price_max)].copy()
filtered = filtered[filtered["Release date"].dt.year.between(*year_range) | filtered["Release date"].isna()]
if reviews_only:
    filtered = filtered[filtered["Review count"] > 0]
for platform in platforms:
    filtered = filtered[filtered[platform].astype(str).str.lower().isin(["true", "1"])]
if genres:
    filtered = filtered[filtered["Genres"].fillna("").apply(lambda value: any(g in value.split(",") for g in genres))]

if filtered.empty:
    st.warning("No games match the selected filters. Adjust the filters in the sidebar.")
    st.stop()

games_n = len(filtered)
avg_price = filtered["Price"].mean()
positive_games = filtered.loc[filtered["Review count"] > 0, "Positive review share"]
avg_positive = positive_games.mean() if not positive_games.empty else 0
total_ccu = int(filtered["Peak CCU"].sum())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Games in view", f"{games_n:,}")
k2.metric("Average price", f"${avg_price:,.2f}")
k3.metric("Average positive reviews", f"{avg_positive:.1f}%")
k4.metric("Combined peak CCU", f"{total_ccu:,}")

tab_overview, tab_genres, tab_catalog = st.tabs(["Overview", "Genres & platforms", "Game catalog"])

with tab_overview:
    left, right = st.columns(2)
    with left:
        price_data = filtered[filtered["Price"].le(filtered["Price"].quantile(.99))]
        fig = px.histogram(price_data, x="Price", nbins=35, title="Game price distribution (USD)",
                           labels={"Price": "Price (USD)", "count": "Games"}, color_discrete_sequence=["#1b9fff"])
        fig.update_layout(yaxis_title="Games", xaxis_title="Price (USD)", bargap=.08)
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        by_year = (filtered.dropna(subset=["Release date"]).assign(Year=lambda d: d["Release date"].dt.year)
                   .groupby("Year", as_index=False).size().rename(columns={"size": "Games"}))
        fig = px.line(by_year, x="Year", y="Games", markers=True, title="Games released by year",
                      color_discrete_sequence=["#06b6d4"])
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    left, right = st.columns(2)
    with left:
        rating = filtered[filtered["Review count"] >= 10]
        fig = px.scatter(rating, x="Positive review share", y="Review count", color="Price",
                         hover_name="Name", hover_data={"Positive review share": ":.1f", "Price": ":.2f"},
                         title="Review volume and positive share (games with 10+ reviews)",
                         color_continuous_scale="Viridis", log_y=True)
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        label_order = ["Very positive (80%+)", "Mostly positive (70–79%)", "Mixed (40–69%)", "Mostly negative (<40%)", "No reviews"]
        labels = filtered["Review label"].value_counts().reindex(label_order, fill_value=0).rename_axis("Review label").reset_index(name="Games")
        fig = px.bar(labels, x="Review label", y="Games", title="Review sentiment mix",
                     color="Review label", category_orders={"Review label": label_order},
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(showlegend=False, xaxis_title="", xaxis_tickangle=-15)
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

with tab_genres:
    left, right = st.columns(2)
    with left:
        genre_data = explode_values(filtered, "Genres")
        top_genres = genre_data.groupby("Genres", as_index=False).agg(Games=("Name", "nunique"), **{"Average price": ("Price", "mean")})
        top_genres = top_genres.nlargest(18, "Games").sort_values("Games")
        fig = px.bar(top_genres, x="Games", y="Genres", orientation="h", color="Average price",
                     title="Most common genres", color_continuous_scale="Blues",
                     hover_data={"Average price": ":.2f"})
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        platform_counts = pd.DataFrame({"Platform": ["Windows", "Mac", "Linux"],
                                        "Games": [int(filtered[p].astype(str).str.lower().isin(["true", "1"]).sum()) for p in ["Windows", "Mac", "Linux"]]})
        fig = px.bar(platform_counts, x="Platform", y="Games", title="Platform availability",
                     color="Platform", color_discrete_sequence=["#8b5cf6", "#06b6d4", "#f59e0b"])
        fig.update_layout(showlegend=False)
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Top publishers by catalog size")
    pub = explode_values(filtered, "Publishers")
    pub = pub.groupby("Publishers", as_index=False).agg(
        Games=("Name", "nunique"), Positive=("Positive", "sum"), Negative=("Negative", "sum")
    )
    pub["Average positive reviews"] = (
        pub["Positive"] / (pub["Positive"] + pub["Negative"]).replace(0, pd.NA) * 100
    ).fillna(0)
    pub = pub.drop(columns=["Positive", "Negative"]).rename(columns={"Average positive reviews": "Positive review share (%)"})
    st.dataframe(pub.nlargest(15, "Games"), use_container_width=True, hide_index=True)

with tab_catalog:
    st.subheader("Game catalog")
    search = st.text_input("Search by game name", placeholder="Type a title…")
    catalog = filtered.copy()
    if search:
        catalog = catalog[catalog["Name"].fillna("").str.contains(search, case=False, na=False)]
    sort_col = st.selectbox("Sort by", ["Peak CCU", "Review count", "Recommendations", "Positive review share", "Price", "Release date"])
    catalog = catalog.sort_values(sort_col, ascending=False, na_position="last")
    display_cols = ["Name", "Release date", "Price", "Review label", "Positive review share", "Review count", "Peak CCU", "Recommendations", "Genres", "Developers"]
    st.dataframe(catalog[display_cols].rename(columns={"Positive review share": "Positive reviews (%)", "Review count": "Reviews"}),
                 use_container_width=True, hide_index=True, height=520,
                 column_config={"Release date": st.column_config.DateColumn("Release date"),
                                "Price": st.column_config.NumberColumn("Price (USD)", format="$%.2f"),
                                "Positive reviews (%)": st.column_config.NumberColumn(format="%.1f%%")})
    st.download_button("Download filtered catalog (CSV)", catalog[display_cols].to_csv(index=False).encode("utf-8-sig"),
                       file_name="steam_games_filtered.csv", mime="text/csv")

st.caption("Source: games.csv from the provided Steam games ZIP. Missing release dates and missing review data are retained and shown as such.")
