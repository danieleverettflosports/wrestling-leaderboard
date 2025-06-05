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

# Inject FlowWrestling‐style CSS
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

/* Style the subheader text */
.subheader {
    font-size: 1rem !important;
    color: #4F4F4F !important;
    margin-top: -0.5rem;
    margin-bottom: 1.25rem;
}

/* Customize the Selectbox (filters) */
[data-testid="stSelectbox"] .css-1wrcr25 {
    background-color: #F1F3F5 !important;
    color: #2A2A2A !important;
    border-radius: 0.5rem !important;
    border: 1px solid #E0E0E0 !important;
    padding: 0.5rem 0.75rem !important;
}
[data-testid="stSelectbox"] .css-1wrcr25:focus-within {
    border: 1px solid #E63946 !important;
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
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """
    Loads the wrestling CSV and does initial cleanup:
    - Strips whitespace from column names.
    - Builds a "Classification" column from "leagues" (e.g. "Class 1A, Zinc County" → "Class 1A").
    """
    df = pd.read_csv(path)
    # 2.1) Strip whitespace from all column names
    df.columns = [c.strip() for c in df.columns]

    # 2.2) Create "Classification" from "leagues" (splitting off after any comma)
    if "leagues" in df.columns:
        df["Classification"] = (
            df["leagues"].astype(str).apply(lambda x: x.split(",")[0].strip())
        )
    else:
        df["Classification"] = ""

    # 2.3) Drop the original "leagues" column so it doesn’t show up later
    df = df.drop(columns=["leagues"], errors="ignore")

    return df


DATA_PATH = "IA_quality_rankings_v7.csv"
try:
    df_all = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"""
        ❗️ Could not find “{DATA_PATH}” in the same directory as this script.
        Please make sure you have a CSV named `{DATA_PATH}` (or change DATA_PATH
        to point to your actual file), then re-run.
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
    "then toggle between the “Pound-for-Pound” tab and the “By Weight Class” tab below."
    "</div>",
    unsafe_allow_html=True,
)

# --- Build lists for each filter --- #
# 3a) Classification (League)
if "Classification" in df_all.columns:
    unique_leagues = sorted(df_all["Classification"].dropna().unique().tolist())
    all_leagues = ["(All)"] + unique_leagues
else:
    all_leagues = ["(All)"]

# 3b) Metro
if "Metro" in df_all.columns:
    unique_metros = sorted(df_all["Metro"].dropna().unique().tolist())
    all_metros = ["(All)"] + unique_metros
else:
    all_metros = ["(All)"]

# 3c) Grade (only 9–12, no “.0”)
if "grade" in df_all.columns:
    grade_vals = sorted(df_all["grade"].dropna().unique().astype(int).tolist())
    grade_vals = [g for g in grade_vals if g in [9, 10, 11, 12]]
    all_grades = ["(All)"] + [str(g) for g in grade_vals]
else:
    all_grades = ["(All)"]

# --- Display the three filters side-by-side --- #
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

# 4a) Filter by Classification
if selected_league != "(All)" and "Classification" in dff.columns:
    dff = dff[dff["Classification"] == selected_league]

# 4b) Filter by Metro
if selected_metro != "(All)" and "Metro" in dff.columns:
    dff = dff[dff["Metro"] == selected_metro]

# 4c) Filter by Grade
if selected_grade != "(All)" and "grade" in dff.columns:
    try:
        grade_int = int(selected_grade)
        dff = dff[dff["grade"] == grade_int]
    except ValueError:
        pass


# -------------------------------------------------------
# 5) TABS: Pound-for-Pound vs. By Weight Class
# -------------------------------------------------------
tab1, tab2 = st.tabs(["🏅 Pound-for-Pound Rankings", "⚖️ By Weight Class"])


# ---------------------
# 5-A) POUND-FOR-POUND TAB
# ---------------------
with tab1:
    st.markdown("### Pound-for-Pound Rankings")
    if dff.shape[0] == 0:
        st.write("No data available for the current filters.")
    else:
        # 1) Sort by global_score descending
        df_p4p = dff.copy().sort_values(by="global_score", ascending=False).reset_index(drop=True)

        # 2) Assign dynamic P4P Rank = 1..N
        df_p4p["P4P Rank"] = df_p4p.index + 1

        # 3) Round global_score to 2 decimal places
        df_p4p["FloWrestling Score"] = df_p4p["global_score"].apply(
            lambda x: f"{x:.2f}"
        )

        # 4) Build display DataFrame with desired columns in the requested order:
        #    P4P Rank → FloWrestling Score → Weight → Wrestler Name → Team Name → Grade
        display_p4p = df_p4p[[
            "P4P Rank",
            "FloWrestling Score",
            "weight",
            "wrestler_name",
            "team_name",
            "grade",
        ]].copy()

        # 5) Rename columns for nicer headers
        display_p4p = display_p4p.rename(
            columns={
                "weight": "Weight",
                "wrestler_name": "Wrestler Name",
                "team_name": "Team Name",
                "grade": "Grade",
            }
        )

        # 6) Convert Grade → int (drop any .0)
        display_p4p["Grade"] = display_p4p["Grade"].astype(int)

        # 7) Show the DataFrame (hide pandas index)
        st.dataframe(display_p4p, use_container_width=True, hide_index=True)


# ---------------------
# 5-B) BY WEIGHT CLASS TAB
# ---------------------
with tab2:
    st.markdown("### By Weight Class")
    if "weight" not in dff.columns:
        st.error("❗️ Your data must include a column named “weight” (the weight class).")
    else:
        # 5.B.i) Build sorted list of available weights after filtering
        weight_list = sorted(dff["weight"].dropna().unique().tolist())
        if len(weight_list) == 0:
            st.write("No weight-class data available for the current filters.")
        else:
            # 5.B.ii) Render a horizontal radio button group for weights
            selected_weight = st.radio(
                label="Select Weight Class:",
                options=weight_list,
                index=0,
                horizontal=True,
                key="weight_radio",
            )

            # 5.B.iii) Filter to that single weight class
            df_w = dff[dff["weight"] == selected_weight].copy()
            if df_w.shape[0] == 0:
                st.write(f"No wrestlers found at {selected_weight} for the current filters.")
            else:
                # 1) Sort by original “rank” (if present) ascending; otherwise by Win_Pct desc
                if "rank" in df_w.columns:
                    df_w = df_w.sort_values(by="rank", ascending=True).reset_index(drop=True)
                else:
                    if "Win_Pct" in df_w.columns:
                        df_w = df_w.sort_values(by="Win_Pct", ascending=False).reset_index(drop=True)
                    else:
                        # Fallback: sort by FloWrestling Score
                        df_w = df_w.sort_values(by="global_score", ascending=False).reset_index(drop=True)

                # 2) Assign dynamic “Rank” = 1..N
                df_w["Rank"] = df_w.index + 1

                # 3) Round FloWrestling Score to 2 decimals
                df_w["FloWrestling Score"] = df_w["global_score"].apply(
                    lambda x: f"{x:.2f}"
                )

                # 4) Drop unwanted columns
                drop_cols = [
                    "Classification",
                    "Metro",
                    "rank",        # original static rank
                    # “leagues” was already dropped in load_data
                ]
                df_display = df_w.drop(columns=drop_cols, errors="ignore").copy()

                # 5) Re-format “Win %” as a string (if present)
                if "Win_Pct" in df_w.columns:
                    df_display["Win %"] = df_w["Win_Pct"].apply(
                        lambda x: f"{x * 100:.1f}%" if pd.notnull(x) else "—"
                    )
                else:
                    # If only Wins/Losses, compute Win % on the fly
                    def _calc_win_pct(r):
                        total = r["Wins"] + r["Losses"]
                        if total == 0:
                            return "—"
                        return f"{r['Wins'] / total * 100:.1f}%"
                    df_display["Win %"] = df_w.apply(_calc_win_pct, axis=1)

                # 6) Compute “Bonus Pt %”
                def _calc_bonus_pct(r):
                    total_matches = r["Wins"] + r["Losses"]
                    if total_matches == 0:
                        return "—"
                    bonus_pts = r["Pins"] + r["Tech_Falls"] + r["Major_Decisions"]
                    return f"{bonus_pts / total_matches * 100:.1f}%"
                df_display["Bonus Pt %"] = df_w.apply(_calc_bonus_pct, axis=1)

                # 7) Build the final column order:
                #    Rank → FloWrestling Score → Wrestler Name → Team Name → Grade → Wins → Losses → Win % → Bonus Pt % → Pins → Tech Falls → Major Decisions
                desired_order = [
                    "Rank",
                    "FloWrestling Score",
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

                # 8) Rename for nicer headers
                df_display = df_display.rename(
                    columns={
                        "wrestler_name": "Wrestler Name",
                        "team_name": "Team Name",
                        "grade": "Grade",
                        "Tech_Falls": "Tech Falls",
                        "Major_Decisions": "Major Decisions",
                        # Note: “FloWrestling Score” is already named
                    }
                )

                # 9) Convert Grade → int (drop any .0)
                if "Grade" in df_display.columns:
                    df_display["Grade"] = df_display["Grade"].astype(int)

                # 10) Finally, show it (hiding the pandas index)
                st.dataframe(df_display, use_container_width=True, hide_index=True)


# -------------------------------------------------------
# 6) OPTIONAL FOOTER / DEPLOY LINK
# -------------------------------------------------------
st.markdown(
    """
    <div style="text-align:right; margin-top: 1rem;">
      <a href="https://share.streamlit.io/your-username/your-repo-name/main/streamlit_app.py" target="_blank">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit" style="height:32px;">
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)
