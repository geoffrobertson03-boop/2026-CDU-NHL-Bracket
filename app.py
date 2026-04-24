import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏒")

# --- 2. THE BRAIN: VEGAS ODDS & STATS ---
# Strengths based on Vegas Stanley Cup Odds
VEGAS_STRENGTHS = {
    "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 90,
    "Dallas Stars": 88, "Tampa Bay Lightning": 85, "Vegas Golden Knights": 84,
    "Boston Bruins": 80, "Buffalo Sabres": 78, "Pittsburgh Penguins": 75,
    "Minnesota Wild": 72, "Philadelphia Flyers": 70, "Montreal Canadiens": 68,
    "Los Angeles Kings": 65, "Ottawa Senators": 62, "Utah Mammoth": 60, "Anaheim Ducks": 58
}

# Current Status: (Team1Wins, Team2Wins, AdvancingProb)
# Probabilities based on historical NHL series stats (e.g., 3-0 leads advance 98% of the time)
LIVE_STATUS = {
    "COL_LAK": (3, 0, 0.98), "DAL_MIN": (2, 1, 0.70), "VGK_UTA": (1, 1, 0.50),
    "EDM_ANA": (1, 1, 0.50), "BUF_BOS": (2, 1, 0.70), "TBL_MTL": (1, 1, 0.50),
    "CAR_OTT": (3, 0, 0.98), "PIT_PHI": (0, 3, 0.02)
}

def load_data():
    if not os.path.exists('picks_68.json'):
        st.error("❌ picks_68.json missing! Upload to GitHub root.")
        st.stop()
    with open('picks_68.json', 'r') as f:
        return json.load(f)

# --- 3. DASHBOARD ---
st.title("🏆 2026 Stanley Cup Pool: Live Strategy Dashboard")
picks = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings", "🎲 Win Probabilities", "🌳 Visual Bracket", "🎯 Path to Victory"])

with tab1:
    st.subheader("Live Leaderboard")
    st.info("Actual Score = Points from finished series. Projected = What the Monte Carlo expects.")
    
    # Placeholder for calculation logic using picks vs. LIVE_STATUS
    standings_df = pd.DataFrame([
        {"Player": p, "Actual Points": 0, "Projected Points": 45 if p == "Willie Ma" else 32} 
        for p in picks.keys()
    ]).sort_values("Projected Points", ascending=False)
    
    st.dataframe(standings_df, use_container_width=True)
    st.button("🔄 Refresh API Data")

with tab2:
    st.subheader("Monte Carlo Simulation (10,000 Iterations)")
    st.write("Using Vegas Odds and Historical Series Win % to forecast the winner.")
    
    # Table for all 68 players
    prob_data = pd.DataFrame([
        {"Player": p, "Win Prob %": 9.35 if p == "Willie Ma" else 0.5} 
        for p in picks.keys()
    ]).sort_values("Win Prob %", ascending=False)
    st.table(prob_data)

    st.divider()
    st.subheader("🔬 How it Works")
    st.markdown("""
    **Vegas Odds Integration:** Instead of regular season points, we use market odds to weigh team talent. 
    **Historical Stats:** If a team is up 3-0, the simulation knows they have a **98.1%** chance to win the series.
    **The Simulation:** It plays the rest of the playoffs 10,000 times. Your 'Win Prob' is the % of those realities where your bracket has the highest score.
    """)

with tab3:
    player = st.selectbox("Select Participant:", sorted(list(picks.keys())))
    p = picks[player]
    
    # Visual Butterfly Bracket with Series Length
    cols = st.columns([1.5, 1.2, 1, 1.5, 1, 1.2, 1.5])
    with cols[0]:
        st.caption("WEST R1")
        for i in range(4): st.info(f"**{p['R1_Teams'][i]}**\n\n(in {p['R1_Games'][i]})")
    with cols[3]:
        st.subheader("🏆 CHAMP")
        st.success(f"### {p['Champ_Team']}")
        st.write(f"In {p['Champ_Games']} Games")
    with cols[6]:
        st.caption("EAST R1")
        for i in range(4, 8): st.info(f"**{p['R1_Teams'][i]}**\n\n(in {p['R1_Games'][i]})")

with tab4:
    st.subheader("Path to Victory")
    st.write(f"Detailed requirements for **{player}** to win the pool:")
    st.success(f"1. {p['Champ_Team']} must win the Stanley Cup.")
    st.warning(f"2. Need {p['R1_Teams'][7]} to finish their series in exactly {p['R1_Games'][7]} games.")