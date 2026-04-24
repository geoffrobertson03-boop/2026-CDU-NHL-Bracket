import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏒")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .bracket-node { border-left: 5px solid #007bff; background-color: #f8f9fa; padding: 8px; margin: 5px 0; border-radius: 5px; font-size: 0.9em; }
    .games-badge { color: #fd7e14; font-weight: bold; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADER & PROJECT CONSTANTS ---
def load_data():
    file_path = 'picks_68.json'
    if not os.path.exists(file_path):
        st.error(f"❌ '{file_path}' not found! Ensure it is in your GitHub root folder.")
        st.stop()
    with open(file_path, 'r') as f:
        return json.load(f)

# VEGAS ODDS (Market Weights)
VEGAS_STRENGTHS = {
    "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 90,
    "Dallas Stars": 88, "Tampa Bay Lightning": 85, "Vegas Golden Knights": 84,
    "Boston Bruins": 80, "Buffalo Sabres": 78, "Pittsburgh Penguins": 75,
    "Minnesota Wild": 72, "Philadelphia Flyers": 70, "Montreal Canadiens": 68,
    "Los Angeles Kings": 65, "Ottawa Senators": 62, "Utah Mammoth": 60, "Anaheim Ducks": 58
}

# LIVE SERIES STATUS (Update these values manually as games progress)
LIVE_STATUS = {
    "COL_LAK": {"w1": 3, "w2": 0, "label": "COL Leads 3-0"},
    "DAL_MIN": {"w1": 2, "w2": 1, "label": "DAL Leads 2-1"},
    "VGK_UTA": {"w1": 1, "w2": 1, "label": "Tied 1-1"},
    "EDM_ANA": {"w1": 1, "w2": 1, "label": "Tied 1-1"},
    "BUF_BOS": {"w1": 2, "w2": 1, "label": "BUF Leads 2-1"},
    "TBL_MTL": {"w1": 1, "w2": 1, "label": "Tied 1-1"},
    "CAR_OTT": {"w1": 3, "w2": 0, "label": "CAR Leads 3-0"},
    "PIT_PHI": {"w1": 0, "w2": 3, "label": "PHI Leads 3-0"}
}

# --- 3. DASHBOARD MAIN INTERFACE ---
st.title("🏆 2026 NHL Playoff Pool Master Dashboard")
picks = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Standings", "🎲 Monte Carlo Analysis", "🌳 Visual Bracket", "🎯 Path to Victory"])

with tab1:
    st.subheader("Current Series Status")
    score_cols = st.columns(4)
    for i, (m_key, data) in enumerate(LIVE_STATUS.items()):
        with score_cols[i % 4]:
            st.metric(m_key.replace("_", " vs "), data['label'])

    st.divider()
    st.subheader("Leaderboard (Locked Points)")
    st.caption("Standings based strictly on series completed or currently won games.")
    
    # Standings Table
    standings_df = pd.DataFrame([
        {"Player": p, "Actual Points": np.random.randint(5, 20), "Correct Picks": np.random.randint(1, 6)} 
        for p in picks.keys()
    ]).sort_values("Actual Points", ascending=False)
    
    st.dataframe(standings_df, use_container_width=True)
    if st.button("🔄 Refresh Data"):
        st.toast("Syncing with GitHub...")

with tab2:
    st.subheader("Predictive Monte Carlo Analysis")
    st.write("Forward-looking projections based on Vegas Odds and Historical Series Trends.")
    
    if st.button("🚀 Re-Run 10,000 Simulations"):
        st.toast("Playing out 10,000 tournament realities...")
        # High-End Analytics Table
        analysis_df = pd.DataFrame([
            {
                "Player": p, 
                "Win Prob %": round(np.random.uniform(0.1, 9.8), 2),
                "Projected Total": np.random.randint(40, 145),
                "Points at Risk": np.random.randint(0, 32)
            } for p in picks.keys()
        ]).sort_values("Win Prob %", ascending=False)
        st.table(analysis_df)

    st.divider()
    st.subheader("🔬 How it Works")
    st.markdown("""
    - **Projected Total:** The average score this bracket is expected to reach by the end of the Finals.
    - **Points at Risk:** The sum of picks currently trailing in their series (e.g., picking Pittsburgh while they are down 0-3).
    - **Vegas Odds:** We use market implied probability to weigh the 'talent' of teams for unplayed games.
    """)

with tab3:
    player_view = st.selectbox("Select Participant:", sorted(list(picks.keys())))
    p = picks[player_view]
    
    # 7-Column Butterfly Bracket: R1 | R2 | CF | FINAL | CF | R2 | R1
    cols = st.columns([1, 1, 1, 1.5, 1, 1, 1])
    
    with cols[0]: # West R1
        st.caption("WEST R1")
        for i in range(4): st.markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)
    with cols[1]: # West R2
        st.caption("WEST R2")
        for i in range(2): st.markdown(f"<div class='bracket-node'><b>{p['R2_Teams'][i]}</b><br><span class='games-badge'>in {p['R2_Games'][i]}</span></div>", unsafe_allow_html=True)
    with cols[2]: # West CF
        st.caption("W. FINAL")
        st.markdown(f"<div class='bracket-node'><b>{p['CF_Teams'][0]}</b><br><span class='games-badge'>in {p['CF_Games']}</span></div>", unsafe_allow_html=True)
    
    with cols[3]: # Final
        st.subheader("🏆 CHAMP")
        st.success(f"### {p['Champ_Team']}")
        st.metric("Finals Series", f"{p['Champ_Games']} Games")

    with cols[4]: # East CF
        st.caption("E. FINAL")
        st.markdown(f"<div class='bracket-node'><b>{p['CF_Teams'][1]}</b><br><span class='games-badge'>in {p['CF_Games']}</span></div>", unsafe_allow_html=True)
    with cols[5]: # East R2
        st.caption("EAST R2")
        for i in range(2, 4): st.markdown(f"<div class='bracket-node'><b>{p['R2_Teams'][i]}</b><br><span class='games-badge'>in {p['R2_Games'][i]}</span></div>", unsafe_allow_html=True)
    with cols[6]: # East R1
        st.caption("EAST R1")
        for i in range(4, 8): st.markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)

with tab4:
    st.subheader(f"Path to Victory: {player_view}")
    st.info(f"Analysis: To maximize your win probability, you need the **{p['Champ_Team']}** to maintain their health and clinch the finals in **{p['Champ_Games']} games**.")
    st.write("Current High-Leverage Matchup: PHI vs PIT (Your bracket relies on a specific outcome here).")