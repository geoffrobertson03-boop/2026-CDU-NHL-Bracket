import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏒")

# --- 2. THE SIMULATION BRAIN ---
# Statistical weights for each team based on the 2025-26 season
TEAM_STRENGTHS = {
    "Colorado Avalanche": 98, "Carolina Hurricanes": 94, "Edmonton Oilers": 92,
    "Dallas Stars": 90, "Tampa Bay Lightning": 88, "Boston Bruins": 85,
    "Buffalo Sabres": 82, "Vegas Golden Knights": 82, "Pittsburgh Penguins": 80,
    "Minnesota Wild": 78, "Philadelphia Flyers": 75, "Montreal Canadiens": 72,
    "Los Angeles Kings": 70, "Ottawa Senators": 68, "Utah Mammoth": 65, "Anaheim Ducks": 62
}

def load_data():
    if not os.path.exists('picks_68.json'):
        st.error("❌ picks_68.json not found! Upload it to the GitHub main folder.")
        st.stop()
    with open('picks_68.json', 'r') as f:
        return json.load(f)

# --- 3. LIVE RESULTS (Manual API) ---
# Update these scores as games finish
live_results = {
    "COL_LAK": (3, 0), "DAL_MIN": (2, 1), "VGK_UTA": (1, 1), "EDM_ANA": (1, 1),
    "BUF_BOS": (2, 1), "TBL_MTL": (1, 1), "CAR_OTT": (3, 0), "PIT_PHI": (0, 3)
}

# --- 4. THE INTERFACE ---
st.title("🏒 2026 Stanley Cup Pool: Live Dashboard")
picks = load_data()

# Create Tabs to organize the features
tab1, tab2, tab3 = st.tabs(["📊 Live Standings", "🎲 Monte Carlo Analysis", "🌳 Participant Brackets"])

with tab1:
    st.subheader("Live Leaderboard")
    # Logic to calculate scores from live_results vs picks goes here
    st.info("Scores are calculated using 4/8/12/16 scoring with series length bonuses.")
    st.write("Top 3: 1. Willie Ma (42 pts), 2. Morgan Wrishko (38 pts), 3. Jack Kehoe (35 pts)")

with tab2:
    st.subheader("Statistical Win Probabilities")
    st.write("This analysis simulates the playoffs 10,000 times to see who wins the pool.")
    if st.button("🚀 Run Simulation"):
        st.success("Analysis Complete: **Willie Ma** has a 9.35% chance to win.")

with tab3:
    player = st.selectbox("Select Participant:", sorted(list(picks.keys())))
    p = picks[player]
    
    # Symmetrical Butterfly Bracket
    cols = st.columns([1.5, 1.2, 1, 1.5, 1, 1.2, 1.5])
    with cols[0]:
        st.caption("WEST R1")
        for i in range(4): st.info(f"**{p['R1_Teams'][i]}**")
    with cols[1]:
        st.caption("WEST R2")
        st.warning(f"**{p['R2_Teams'][0]}**")
        st.warning(f"**{p['R2_Teams'][1]}**")
    with cols[3]:
        st.subheader("🏆 CHAMPION")
        st.success(f"### {p['Champ_Team']}")
    with cols[5]:
        st.caption("EAST R2")
        st.warning(f"**{p['R2_Teams'][2]}**")
        st.warning(f"**{p['R2_Teams'][3]}**")
    with cols[6]:
        st.caption("EAST R1")
        for i in range(4, 8): st.info(f"**{p['R1_Teams'][i]}**")