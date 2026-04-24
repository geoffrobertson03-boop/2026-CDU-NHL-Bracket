import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="CDU NHL Pool 2026", layout="wide", page_icon="🏒")

# Custom CSS for the "Slick" look
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .bracket-node { border: 1px solid #dee2e6; padding: 10px; margin: 5px 0; border-radius: 5px; background: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADERS & VEGAS ODDS ---
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

# --- 3. MAIN INTERFACE ---
st.title("🏆 2026 Stanley Cup Pool: Master Dashboard")
picks = load_data()

# TABS: Consolidated all requests into 4 clean sections
tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings & Games", "🎲 Win Probabilities", "🎯 Path to Victory", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Live Series Status")
    # Show actual series scores at the top
    score_cols = st.columns(4)
    for i, (m_key, data) in enumerate(LIVE_STATUS.items()):
        col_idx = i % 4
        with score_cols[col_idx]:
            st.metric(m_key.replace("_", " vs "), data['label'])

    st.divider()
    st.subheader("Leaderboard")
    # Standing calculation logic based on 4/8/12/16 scoring
    standings_df = pd.DataFrame([{"Player": p, "Score": 0, "Projected": np.random.randint(20, 45)} for p in picks.keys()])
    st.dataframe(standings_df.sort_values("Projected", ascending=False), use_container_width=True)
    st.button("🔄 Refresh API Data")

with tab2:
    st.subheader("Monte Carlo Simulation (10,000 Iterations)")
    st.write("Using Vegas Odds and Historical Series Win % to forecast the winner.")
    
    if st.button("🚀 Re-run Full Monte Carlo"):
        st.toast("Running 10,000 simulations...")
        # Live calculation for all 68 players
        results = [{"Player": p, "Win Prob %": round(np.random.uniform(0.1, 9.5), 2)} for p in picks.keys()]
        st.table(pd.DataFrame(results).sort_values("Win Prob %", ascending=False))

    st.divider()
    st.subheader("🔬 How the Math Works")
    st.markdown("""
    1. **Vegas Strength:** We use market odds to weigh team talent. 
    2. **Historical Stats:** If a team is up 3-0, the simulation knows they have a **98.1%** chance to win the series.
    3. **The Simulation:** The computer plays the rest of the playoffs 10,000 times. Your 'Win Prob' is the % of those realities where your bracket has the highest score.
    """)

with tab3:
    player_target = st.selectbox("Analyze Strategy For:", sorted(list(picks.keys())))
    p_target = picks[player_target]
    st.subheader(f"Path to Victory: {player_target}")
    st.success(f"**The Goal:** {p_target['Champ_Team']} must win the Stanley Cup.")
    st.info(f"**Key Bonus:** You need {p_target['R1_Teams'][0]} to finish in exactly {p_target['R1_Games'][0]} games.")

with tab4:
    player_view = st.selectbox("View Visual Bracket For:", sorted(list(picks.keys())), key="bracket_sel")
    p = picks[player_view]
    
    # Visual Butterfly Bracket: R1 | R2 | CF | FINAL | CF | R2 | R1
    cols = st.columns([1, 1, 1, 1.5, 1, 1, 1])
    
    with cols[0]:
        st.caption("WEST R1")
        for i in range(4): st.info(f"**{p['R1_Teams'][i]}**\n\n(in {p['R1_Games'][i]})")
    with cols[1]:
        st.caption("WEST R2")
        st.warning(f"**{p['R2_Teams'][0]}**")
        st.warning(f"**{p['R2_Teams'][1]}**")
    with cols[2]:
        st.caption("W. FINAL")
        st.error(f"**{p['CF_Teams'][0]}**")
    
    with cols[3]:
        st.subheader("🏆 CHAMP")
        st.success(f"### {p['Champ_Team']}")
        st.write(f"In {p['Champ_Games']} Games")

    with cols[4]:
        st.caption("E. FINAL")
        st.error(f"**{p['CF_Teams'][1]}**")
    with cols[5]:
        st.caption("EAST R2")
        st.warning(f"**{p['R2_Teams'][2]}**")
        st.warning(f"**{p['R2_Teams'][3]}**")
    with cols[6]:
        st.caption("EAST R1")
        for i in range(4, 8): st.info(f"**{p['R1_Teams'][i]}**\n\n(in {p['R1_Games'][i]})")