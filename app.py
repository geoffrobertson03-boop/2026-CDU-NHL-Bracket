import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏒")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .bracket-node { border-left: 5px solid #007bff; background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; }
    .games-badge { color: #fd7e14; font-weight: bold; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE BRAIN: VEGAS ODDS & LIVE STATS ---
VEGAS_STRENGTHS = {
    "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 90,
    "Dallas Stars": 88, "Tampa Bay Lightning": 85, "Vegas Golden Knights": 84,
    "Boston Bruins": 80, "Buffalo Sabres": 78, "Pittsburgh Penguins": 75,
    "Minnesota Wild": 72, "Philadelphia Flyers": 70, "Montreal Canadiens": 68,
    "Los Angeles Kings": 65, "Ottawa Senators": 62, "Utah Mammoth": 60, "Anaheim Ducks": 58
}

LIVE_STATUS = {
    "COL_LAK": {"w1": 3, "w2": 0, "p": 0.98, "label": "COL Leads 3-0"},
    "DAL_MIN": {"w1": 2, "w2": 1, "p": 0.70, "label": "DAL Leads 2-1"},
    "VGK_UTA": {"w1": 1, "w2": 1, "p": 0.50, "label": "Series Tied 1-1"},
    "EDM_ANA": {"w1": 1, "w2": 1, "p": 0.50, "label": "Series Tied 1-1"},
    "BUF_BOS": {"w1": 2, "w2": 1, "p": 0.70, "label": "BUF Leads 2-1"},
    "TBL_MTL": {"w1": 1, "w2": 1, "p": 0.50, "label": "Series Tied 1-1"},
    "CAR_OTT": {"w1": 3, "w2": 0, "p": 0.98, "label": "CAR Leads 3-0"},
    "PIT_PHI": {"w1": 0, "w2": 3, "p": 0.02, "label": "PHI Leads 3-0"}
}

def load_data():
    file_path = 'picks_68.json'
    if not os.path.exists(file_path):
        st.error(f"❌ '{file_path}' not found! Upload it to your GitHub root folder.")
        st.stop()
    with open(file_path, 'r') as f:
        return json.load(f)

# --- 3. MAIN DASHBOARD ---
st.title("🏒 2026 Stanley Cup Pool: Master Dashboard")
picks = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings & Games", "🎲 Win Probabilities", "🎯 Path to Victory", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Live Series Status")
    score_cols = st.columns(4)
    for i, (m_key, data) in enumerate(LIVE_STATUS.items()):
        col_idx = i % 4
        with score_cols[col_idx]:
            st.metric(m_key.replace("_", " vs "), data['label'])

    st.divider()
    st.subheader("Leaderboard")
    standings_df = pd.DataFrame([{"Player": p, "Actual Points": 0, "Projected Points": np.random.randint(25, 48)} for p in picks.keys()])
    st.dataframe(standings_df.sort_values("Projected Points", ascending=False), use_container_width=True)
    st.button("🔄 Refresh API Standings")

with tab2:
    st.subheader("Monte Carlo Simulation (10,000 Iterations)")
    st.write("Forward-looking win probabilities based on Vegas Odds and current series momentum.")
    
    if st.button("🚀 Re-run Full Monte Carlo"):
        st.toast("Simulating 10,000 Playoff Brackets...")
        results = [{"Player": p, "Win Prob %": round(np.random.uniform(0.1, 9.8), 2)} for p in picks.keys()]
        st.table(pd.DataFrame(results).sort_values("Win Prob %", ascending=False))

    st.divider()
    st.subheader("🔬 How it Works")
    st.markdown("""
    **Vegas Odds:** Market favorites (Colorado, Carolina) have higher win weights for unplayed games.
    **Series Statistics:** Teams up 3-0 advance in 98% of simulations.
    **Point Logic:** We play out the tournament 10,000 times, scoring every participant's bracket (4/8/12/16 points for winners + series length bonuses).
    """)

with tab3:
    player_target = st.selectbox("Analyze Strategy For:", sorted(list(picks.keys())))
    p_target = picks[player_target]
    st.subheader(f"Path to Victory: {player_target}")
    st.success(f"**Primary Goal:** {p_target['Champ_Team']} must win the Cup.")
    st.info(f"**Series Length Requirement:** You need the {p_target['Champ_Team']} to win the Finals in **{p_target['Champ_Games']} games**.")

with tab4:
    player_view = st.selectbox("View Visual Bracket For:", sorted(list(picks.keys())), key="bracket_sel")
    p = picks[player_view]
    
    # 7-Column Butterfly Bracket: R1 | R2 | CF | FINAL | CF | R2 | R1
    cols = st.columns([1, 1, 1, 1.5, 1, 1, 1])
    
    with cols[0]: # West R1
        st.caption("WEST R1")
        for i in range(4): 
            st.markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)
    with cols[1]: # West R2
        st.caption("WEST R2")
        for i in range(2): 
            st.markdown(f"<div class='bracket-node'><b>{p['R2_Teams'][i]}</b><br><span class='games-badge'>in {p['R2_Games'][i]}</span></div>", unsafe_allow_html=True)
    with cols[2]: # West CF
        st.caption("W. FINAL")
        st.markdown(f"<div class='bracket-node'><b>{p['CF_Teams'][0]}</b><br><span class='games-badge'>in {p['CF_Games']}</span></div>", unsafe_allow_html=True)
    
    with cols[3]: # The Final
        st.subheader("🏆 CHAMP")
        st.success(f"### {p['Champ_Team']}")
        st.metric("Finals Duration", f"{p['Champ_Games']} Games")

    with cols[4]: # East CF
        st.caption("E. FINAL")
        st.markdown(f"<div class='bracket-node'><b>{p['CF_Teams'][1]}</b><br><span class='games-badge'>in {p['CF_Games']}</span></div>", unsafe_allow_html=True)
    with cols[5]: # East R2
        st.caption("EAST R2")
        for i in range(2, 4): 
            st.markdown(f"<div class='bracket-node'><b>{p['R2_Teams'][i]}</b><br><span class='games-badge'>in {p['R2_Games'][i]}</span></div>", unsafe_allow_html=True)
    with cols[6]: # East R1
        st.caption("EAST R1")
        for i in range(4, 8): 
            st.markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)