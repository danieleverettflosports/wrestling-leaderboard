# streamlittest.py

import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------------------------------
# 1) PAGE CONFIG & GLOBAL CSS
# -------------------------------------------------------
st.set_page_config(
    page_title="Missouri Wrestling Leaderboard",
    layout="wide",
)

# Inject a bit of CSS to mimic FlowWrestling’s font + color scheme
# (Feel free to tweak the font‐family or colors if you have a more
#  specific .css file from Flow; this is a close approximation.)
_FLOW_CSS = """
<style>
/* Use a clean sans‐serif almost identical to Flow’s “headline-3” look */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
    color: #2A2A2A !important;
}

/* Style the main header (trophy + “Missouri Wrestling Leaderboard”) */
h1 {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    color: #2A2A2A !important;
    margin-bottom: 0.2rem;
}

/* Style the subheader text that explains the filters */
.subheader {
    font-size: 1rem !important;
    color: #4F4F4F !important;
    margin-top: -0.5rem;
    margin-bottom: 1.25rem;
}

/* Customize the Selectbox (filters) look */
[data-testid="stSelectbox"] .css-1wrcr25 {
    background-color: #F1F3F5 !important;
    color: #2A2A2A !important;
    border-radius: 0.5rem !important;
    border: 1px solid #E0E0E0 !important;
    padding: 0.5rem 0.75rem !important;
}
[data-testid="stSelectbox"] .css-1wrcr25:focus-within {
    border: 1px solid #E63946 !important;  /* highlight in a Flow‐style red when focused */
    box-shadow: none !important;
}

/* Style the expander header */
.stExpander > button {
    background-color: #FFFFFF !important;
    border: 1px solid #E0E0E0 !important;
    border-radius: 0.5rem !important;
    padding: 0.75rem 1rem !important;
    font-weight: 500 !important;
    color: #2A2A2A !important;
}
.stExpander > button:hover {
    background-color: #F8F9FA !important;
}

/* Style the expanded container background */
.stExpander[aria-expanded="true"] {
    background-color: #FAFAFA !important;
    border: 1px solid #E0E0E0 !important;
    border-top: none !important;
    border-bottom-left-radius: 0.5rem !important;
    border-bottom-right-radius: 0.5rem !important;
}

/* Style the DataFrame column headers */
.css-1d391kg th {
    background-color: #F1F3F5 !important;
    color: #2A2A2A !important;
    font-weight: 600 !important;
    text-align: left !important;
}

/* Remove the pandas index column entirely */
.css-k1vhr4.e1tzin5v0 {
    display: none !important;
}
</style>
"""
st.markdown(_FLOW_CSS, unsafe_allow_html=True)


# -------------------------------------------------------
# 2) LOAD & PREPARE DATA
# -------------------------------------------------------
@st.cache_data  # Cache so that re‐runs are faster
def load_data(path: str) -> pd.DataFrame:
    """
    Loads the wrestling CSV and does initial cleanup:
    - Strips whitespace from column names.
    - Creates a new "Classification" column based on the existing "leagues" column.
      If "leagues" contains things like "Class 1A, Zinc County", we split off at the comma
      so we just get "Class 1A".
    """
    df = pd.read_csv(path)

    # 2.1) Standardize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # 2.2) Create a unified "Classification" column from the existing "leagues" column
    if "leagues" in df.columns:
        # Convert to string just in case, then split off any comma‐suffix
        df["Classification"] = (
            df["leagues"]
            .astype(str)
            .apply(lambda x: x.split(",")[0].strip())
        )
    else:
        # If your CSV truly has no "leagues" column, we leave Classification blank,
        # so downstream code will still run—just the dropdown will show "(All)" only.
        df["Classification"] = ""

    # 2.3) Drop the original "leagues" column so it doesn’t clutter the table later on
    df = df.drop(columns=["leagues"], errors="ignore")

    return df


# Make sure to point this at your actual CSV file in the same folder
DATA_PATH = "MO_quality_rankings_v6.csv"
try:
    df_all = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"""
        ❗️ Could not find “{DATA_PATH}” in the same directory as this script.
        Please make sure you have a CSV named `{DATA_PATH}` (or change DATA_PATH
        to point to your actual file), then re‐run.
        """
    )
    st.stop()


# -------------------------------------------------------
# 3) PAGE HEADER + FILTERS
# -------------------------------------------------------
st.markdown("## 🏆 Missouri Wrestling Leaderboard")

# Combine the long description into a single triple-quoted string (no accidental concatenation gaps)
st.markdown(
    """
    <div class="subheader">
      We take every varsity match you wrestle and turn it into a single “performance score” that reflects not just wins and losses,
      but how strongly and how recently you won those matches. Beating a highly rated opponent (who themselves has beaten other top guys)
      counts more than beating someone unranked, and a pin or tech-fall earns more credit than a narrow decision. Wins in big tournaments
      (like regionals or state) matter more than wins in smaller duals, and we gradually reduce the value of older matches so that recent
      form carries the most weight.<br><br>
      Once each match has been scored this way, we average those match scores—giving extra weight to quick pins, state-bracket finishes,
      and beating top opponents—so that every wrestler in a given weight class ends up with a single number. Sorting those numbers from
      highest to lowest gives you the ranked list. In plain terms: “Beat strong opponents in important events, pin them early,
      and keep winning lately, and you’ll sit at the top of your weight.”<br><br>
      The following rankings are as of 2/18/25 for Misosuri HS (before the state tournamnet).<br><br>
      Use the filters below to narrow by
      <span style='font-weight:600;'>Classification (League)</span>,
      <span style='font-weight:600;'>Metro</span>, or
      <span style='font-weight:600;'>Grade</span>, then expand any weight class to see its full table.
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Build lists for each filter --- #

# 3a) Classification (League) dropdown
if "Classification" in df_all.columns:
    unique_leagues = sorted(df_all["Classification"].dropna().unique().tolist())
    all_leagues = ["(All)"] + unique_leagues
else:
    all_leagues = ["(All)"]

# 3b) Metro dropdown
if "Metro" in df_all.columns:
    unique_metros = sorted(df_all["Metro"].dropna().unique().tolist())
    all_metros = ["(All)"] + unique_metros
else:
    all_metros = ["(All)"]

# 3c) Grade dropdown (show only 9–12 in numeric order, no “.0”)
if "grade" in df_all.columns:
    grade_vals = sorted(df_all["grade"].dropna().unique().astype(int).tolist())
    # Only keep 9,10,11,12 if present
    grade_vals = [g for g in grade_vals if g in [9, 10, 11, 12]]
    all_grades = ["(All)"] + [str(g) for g in grade_vals]
else:
    all_grades = ["(All)"]

# --- Place the three selectboxes side by side --- #
col1, col2, col3 = st.columns([3, 3, 2], gap="large")
with col1:
    selected_league = st.selectbox(
        label="Classification (League)",
        options=all_leagues,
        index=0,
        key="league_filter",
    )
with col2:
    selected_metro = st.selectbox(
        label="Metro",
        options=all_metros,
        index=0,
        key="metro_filter",
    )
with col3:
    selected_grade = st.selectbox(
        label="Grade",
        options=all_grades,
        index=0,
        key="grade_filter",
    )

st.markdown("---")  # horizontal divider


# -------------------------------------------------------
# 4) APPLY FILTERS
# -------------------------------------------------------
dff = df_all.copy()

# 4a) Filter by Classification (if not “(All)”)
if selected_league != "(All)" and "Classification" in dff.columns:
    dff = dff[dff["Classification"] == selected_league]

# 4b) Filter by Metro (if not “(All)”)
if selected_metro != "(All)" and "Metro" in dff.columns:
    dff = dff[dff["Metro"] == selected_metro]

# 4c) Filter by Grade (if not “(All)”)
if selected_grade != "(All)" and "grade" in dff.columns:
    try:
        grade_int = int(selected_grade)
        dff = dff[dff["grade"] == grade_int]
    except ValueError:
        pass


# -------------------------------------------------------
# 5) LOOP OVER WEIGHT CLASSES & DISPLAY TABLES
# -------------------------------------------------------
if "weight" not in dff.columns:
    st.error("❗️ Your data must include a column named “weight” (the weight class).")
    st.stop()

all_weights = sorted(dff["weight"].dropna().unique().tolist())

for w in all_weights:
    df_w = dff[dff["weight"] == w].copy()
    if df_w.empty:
        continue

    # ──────────────────────────────────────────────────────────────────
    # A) Re‐compute a DYNAMIC RANK (1,2,3,…) on the filtered subset
    # ──────────────────────────────────────────────────────────────────
    if "rank" in df_w.columns:
        # Sort by the original “rank” ascending
        df_w = df_w.sort_values(by="rank", ascending=True).reset_index(drop=True)
    else:
        # If no original “rank” column, sort by Win_Pct descending
        df_w = df_w.sort_values(by="Win_Pct", ascending=False).reset_index(drop=True)

    # Now assign dynamic_rank = 1..N
    df_w["dynamic_rank"] = df_w.index + 1

    # Figure out who is #1 in this weight for the expander label:
    top_row = df_w[df_w["dynamic_rank"] == 1].iloc[0]
    top_name = top_row["wrestler_name"]
    top_team = top_row["team_name"]
    expander_label = f"{w} | {top_name} ({top_team})"
    # ──────────────────────────────────────────────────────────────────

    with st.expander(expander_label, expanded=False):
        # 5.1) Start building a display copy
        df_display = df_w.copy()

        # 5.2) Drop columns we do NOT want to show
        drop_cols = [
            "Classification",
            "Metro",
            "rank",       # original static rank
            "Win_Pct",    # we’ll re‐format this as a percentage string
        ]
        df_display = df_display.drop(columns=drop_cols, errors="ignore")

        # 5.3) Reorder & calculate new columns

        # ----- Win % as a formatted string ----- #
        if "Win_Pct" in df_w.columns:
            df_display["Win %"] = df_w["Win_Pct"].apply(
                lambda x: f"{x * 100:.1f}%" if pd.notnull(x) else "—"
            )
        else:
            # If you only have “Wins” & “Losses,” compute Win_Pct on the fly
            def _calc_win_pct(r):
                total = r["Wins"] + r["Losses"]
                if total == 0:
                    return "—"
                return f"{r['Wins'] / total * 100:.1f}%"
            df_display["Win %"] = df_w.apply(_calc_win_pct, axis=1)

        # ----- Bonus Pt % = (Pins + Tech_Falls + Major_Decisions) / (Wins + Losses) ----- #
        def calc_bonus_pct(row):
            total_matches = row["Wins"] + row["Losses"]
            if total_matches == 0:
                return "—"
            bonus_pts = row["Pins"] + row["Tech_Falls"] + row["Major_Decisions"]
            return f"{bonus_pts / total_matches * 100:.1f}%"

        df_display["Bonus Pt %"] = df_w.apply(calc_bonus_pct, axis=1)

        # 5.4) Decide on final column order:
        desired_order = [
            "dynamic_rank",
            "wrestler_name",
            "team_name",
            "grade",
            "Wins",
            "Losses",
            "Win %",
            "Bonus Pt %",
            "Pins",
            "Tech_Falls",
            "Major_Decisions",
        ]
        cols_to_show = [c for c in desired_order if c in df_display.columns]
        df_display = df_display[cols_to_show]

        # 5.5) Rename for nicer column headers
        df_display = df_display.rename(
            columns={
                "dynamic_rank": "Rank",
                "wrestler_name": "Wrestler Name",
                "team_name": "Team Name",
                "grade": "Grade",
                "Wins": "Wins",
                "Losses": "Losses",
                "Win %": "Win %",
                "Bonus Pt %": "Bonus Pt %",
                "Pins": "Pins",
                "Tech_Falls": "Tech Falls",
                "Major_Decisions": "Major Decisions",
            }
        )

        # 5.6) Convert Grade to an integer (drop any “.0”)
        if "Grade" in df_display.columns:
            df_display["Grade"] = df_display["Grade"].astype(int)

        # 5.7) Reset pandas index so we don’t see “0,1,2…” on the far left
        df_display = df_display.reset_index(drop=True)

        # 5.8) Finally, show it with st.dataframe (hide_index=True removes pandas index column)
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# -------------------------------------------------------
# 6) OPTIONAL FOOTER / DEPLOY LINK
# -------------------------------------------------------
# If you plan to deploy this to Streamlit Cloud, you can show a “Deploy” badge:
st.markdown(
    """
    <div style="text-align:right; margin-top: 1rem;">
      <a href="https://share.streamlit.io/your-username/your-repo-name/main/streamlittest.py" target="_blank">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit" style="height:32px;">
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)
