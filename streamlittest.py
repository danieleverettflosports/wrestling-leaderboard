# streamlit_app.py

import streamlit as st
import pandas as pd

# -------------------------------------------------------
# 1) PAGE CONFIG & GLOBAL CSS
# -------------------------------------------------------
st.set_page_config(
    page_title="Iowa Wrestling Leaderboard",
    layout="wide",
)

# Inject a bit of CSS to mimic FlowWrestling’s font + color scheme
# (Close approximation of Flow’s “headline-3” look.)
_FLOW_CSS = """
<style>
/* Use a clean sans-serif almost identical to Flow’s “headline-3” look */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
    color: #2A2A2A !important;
}

/* Style the main header (trophy + “Iowa Wrestling Leaderboard”) */
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
    border: 1px solid #E63946 !important;  /* highlight in a Flow-style red when focused */
    box-shadow: none !important;
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
    - Creates a new "Classification" column from "leagues" (e.g. "Class 1A, Zinc County" → "Class 1A").
    """
    df = pd.read_csv(path)

    # 2.1) Standardize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # 2.2) Create a unified "Classification" column from the existing "leagues" column
    if "leagues" in df.columns:
        df["Classification"] = (
            df["leagues"].astype(str).apply(lambda x: x.split(",")[0].strip())
        )
    else:
        # If there's no "leagues" column, create an empty Classification
        df["Classification"] = ""

    # 2.3) We can drop "leagues" entirely so it doesn’t clutter the table later
    df = df.drop(columns=["leagues"], errors="ignore")

    return df


# Make sure this CSV is in the same folder
DATA_PATH = "IA_quality_rankings_v7.csv"
try:
    df_all = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"""
        ❗️ Could not find “{DATA_PATH}” in the same directory as this script.
        Please make sure you have a CSV named `{DATA_PATH}` (or change DATA_PATH to point to your actual file), 
        then re‐run.
        """
    )
    st.stop()


# -------------------------------------------------------
# 3) PAGE HEADER + FILTERS
# -------------------------------------------------------
st.markdown("## 🏆 Iowa Wrestling Leaderboard")
st.markdown(
    '<div class="subheader">'
    "Use the filters below to narrow by "
    "<span style='font-weight:600;'>Classification (League)</span>, "
    "<span style='font-weight:600;'>Metro</span>, or "
    "<span style='font-weight:600;'>Grade</span>, "
    "then toggle between the “Pound-for-Pound” tab or “By Weight Class” tab below."
    "</div>",
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
# 5) TABS: P4P vs. By Weight Class
# -------------------------------------------------------
tab1, tab2 = st.tabs(["🏅 Pound-for-Pound Rankings", "⚖️ By Weight Class"])


# ---------------------
# 5-A) P4P TAB
# ---------------------
with tab1:
    st.markdown("### Pound-for-Pound Rankings")
    if dff.shape[0] == 0:
        st.write("No data available for the current filters.")
    else:
        # Sort by global_score descending
        df_p4p = dff.copy()
        df_p4p = df_p4p.sort_values(by="global_score", ascending=False).reset_index(drop=True)

        # Assign dynamic P4P rank = 1..N
        df_p4p["P4P Rank"] = df_p4p.index + 1

        # Build a display DataFrame with only the desired columns:
        #    P4P Rank, weight, wrestler_name, team_name, grade, FloWrestling Score
        display_p4p = df_p4p[[
            "P4P Rank",
            "weight",
            "wrestler_name",
            "team_name",
            "grade",
            "global_score",
        ]].copy()

        # Rename columns
        display_p4p = display_p4p.rename(
            columns={
                "weight": "Weight",
                "wrestler_name": "Wrestler Name",
                "team_name": "Team Name",
                "grade": "Grade",
                "global_score": "FloWrestling Score",
            }
        )

        # Convert Grade to int (drop .0)
        display_p4p["Grade"] = display_p4p["Grade"].astype(int)

        # Show as a Streamlit dataframe (hide_index=True removes the pandas index)
        st.dataframe(display_p4p, use_container_width=True, hide_index=True)


# ---------------------
# 5-B) BY WEIGHT CLASS TAB
# ---------------------
with tab2:
    st.markdown("### By Weight Class")
    if "weight" not in dff.columns:
        st.error("❗️ Your data must include a column named “weight” (the weight class).")
    else:
        # 5.B.i) Build a sorted list of weights that remain after filtering
        weight_list = sorted(dff["weight"].dropna().unique().tolist())
        if len(weight_list) == 0:
            st.write("No weight‐class data available for the current filters.")
        else:
            # 5.B.ii) Let the user click a weight (radio) instead of a dropdown
            selected_weight = st.radio(
                label="Select Weight Class:",
                options=weight_list,
                index=0,
                horizontal=True,  # renders radio options horizontally if space allows
                key="weight_radio",
            )

            # 5.B.iii) Filter the data to that single weight class
            df_w = dff[dff["weight"] == selected_weight].copy()
            if df_w.shape[0] == 0:
                st.write(f"No wrestlers found at {selected_weight} for the current filters.")
            else:
                # 1) Sort by original “rank” ascending (if exists), else by Win_Pct descending
                if "rank" in df_w.columns:
                    df_w = df_w.sort_values(by="rank", ascending=True).reset_index(drop=True)
                else:
                    if "Win_Pct" in df_w.columns:
                        df_w = df_w.sort_values(by="Win_Pct", ascending=False).reset_index(drop=True)
                    else:
                        # If no Win_Pct, just sort by global_score descending
                        df_w = df_w.sort_values(by="global_score", ascending=False).reset_index(drop=True)

                # 2) Assign a dynamic weight‐class rank = 1..N
                df_w["Rank"] = df_w.index + 1

                # 3) Drop columns we do NOT want to show
                drop_cols = [
                    "Classification",
                    "Metro",
                    "rank",        # original static rank
                    "leagues"      # we already dropped it in load_data, but just in case
                ]
                df_display = df_w.drop(columns=drop_cols, errors="ignore").copy()

                # 4) Re‐format “Win %” (if present) as a string
                if "Win_Pct" in df_w.columns:
                    df_display["Win %"] = df_w["Win_Pct"].apply(
                        lambda x: f"{x * 100:.1f}%" if pd.notnull(x) else "—"
                    )
                else:
                    # If you only have Wins/Losses, compute Win % on the fly
                    def _calc_win_pct(r):
                        total = r["Wins"] + r["Losses"]
                        if total == 0:
                            return "—"
                        return f"{r['Wins'] / total * 100:.1f}%"
                    df_display["Win %"] = df_w.apply(_calc_win_pct, axis=1)

                # 5) Compute “Bonus Pt %” = (Pins + Tech_Falls + Major_Decisions) / (Wins + Losses)
                def _calc_bonus_pct(r):
                    total_matches = r["Wins"] + r["Losses"]
                    if total_matches == 0:
                        return "—"
                    bonus_pts = r["Pins"] + r["Tech_Falls"] + r["Major_Decisions"]
                    return f"{bonus_pts / total_matches * 100:.1f}%"
                df_display["Bonus Pt %"] = df_w.apply(_calc_bonus_pct, axis=1)

                # 6) Build the final column order we want to show
                desired_order = [
                    "Rank",
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
                    "global_score",
                ]
                cols_to_show = [c for c in desired_order if c in df_display.columns]
                df_display = df_display[cols_to_show]

                # 7) Rename columns for nicer headers
                df_display = df_display.rename(
                    columns={
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
                        "global_score": "FloWrestling Score",
                    }
                )

                # 8) Convert Grade to int (drop any “.0”)
                if "Grade" in df_display.columns:
                    df_display["Grade"] = df_display["Grade"].astype(int)

                # 9) Reset pandas index so we don’t see “0,1,2…” on the far left
                df_display = df_display.reset_index(drop=True)

                # 10) Finally, show it with st.dataframe (hide_index=True removes pandas index column)
                st.dataframe(df_display, use_container_width=True, hide_index=True)


# -------------------------------------------------------
# 6) OPTIONAL FOOTER / DEPLOY LINK
# -------------------------------------------------------
st.markdown(
    """
    <div style="text-align:right; margin-top: 1rem;">
      <a href="https://share.streamlit.io/your‐username/your‐repo‐name/main/streamlit_app.py" target="_blank">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit" style="height:32px;">
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)
