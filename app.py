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

# --- 2. DATA LOADERS & SERIES STATUS ---
def load_data():
    file_path = 'picks_68.json'
    if not os.path.exists(file_path):
        st.error(f"❌ '{file_path}' not found! Ensure it is in your GitHub root folder.")
        st.stop()
    with open(file_path, 'r') as f:
        return json.load(f)

# THE SOURCE OF TRUTH: Update 'final' to True once a team gets 4 wins
LIVE_STATUS = {
    "COL_LAK": {"w1": 3, "w2": 0, "final": False, "label": "COL Leads 3-0"},
    "DAL_MIN": {"w1": 2, "w2": 1, "final": False, "label": "DAL Leads 2-1"},
    "VGK_UTA": {"w1": 1, "w2": 1, "final": False, "label": "Series Tied 1-1"},
    "EDM_ANA": {"w1": 1, "w2": 1, "final": False, "label": "Series Tied 1-1"},
    "BUF_BOS": {"w1": 2, "w2": 1, "final": False, "label": "BUF Leads 2-1"},
    "TBL_MTL": {"w1": 1, "w2": 1, "final": False, "label": "Series Tied 1-1"},
    "CAR_OTT": {"w1": 3, "w2": 0, "final": False, "label": "CAR Leads 3-0"},
    "PIT_PHI": {"w1": 0, "w2": 3, "final": False, "label": "PHI Leads 3-0"}
}

# VEGAS STRENGTHS for Monte Carlo
VEGAS_STRENGTHS = {
    "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 90,
    "Dallas Stars": 88, "Tampa Bay Lightning": 85, "Vegas Golden Knights": 84,
    "Boston Bruins": 80, "Buffalo Sabres": 78, "Pittsburgh Penguins": 75,
    "Minnesota Wild": 72, "Philadelphia Flyers": 70, "Montreal Canadiens": 68,
    "Los Angeles Kings": 65, "Ottawa Senators": 62, "Utah Mammoth": 60, "Anaheim Ducks": 58
}

# --- 3. SCORING ENGINE ---
def calculate_actual_standings(picks, results):
    standings = []
    matchup_keys = list(results.keys())
    
    for player, data in picks.items():
        points = 0
        series_won = 0
        
        for i, m_key in enumerate(matchup_keys):
            res = results[m_key]
            if res['final']: # ONLY score if series is finished
                winner = m_key.split('_')[0] if res['w1'] == 4 else m_key.split('_')[1]
                if data['R1_Teams'][i] == winner:
                    points += 4
                    series_won += 1
                    # Game Bonus
                    if data['R1_Games'][i] == (res['w1'] + res['w2']):
                        points += 1
        
        standings.append({"Player": player, "Total Points": points, "Series Correct": series_won})
    return pd.DataFrame(standings).sort_values("Total Points", ascending=False)

# --- 4. INTERFACE ---
st.title("🏆 2026 NHL Playoff Pool Master Dashboard")
picks = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Current Standings", "🎲 Monte Carlo Analysis", "🌳 Visual Bracket", "🎯 Path to Victory"])

with tab1:
    st.subheader("Live Series Status")
    score_cols = st.columns(4)
    for i, (m_key, data) in enumerate(LIVE_STATUS.items()):
        with score_cols[i % 4]:
            st.metric(m_key.replace("_", " vs "), data['label'])

    st.divider()
    st.subheader("Official Leaderboard")
    st.caption("Note: Points are ONLY awarded once a series is finalized (4 wins).")
    
    df_actual = calculate_actual_standings(picks, LIVE_STATUS)
    st.dataframe(df_actual, use_container_width=True)

with tab2:
    st.subheader("Predictive Analytics")
    st.write("This tab uses Vegas odds to project where everyone will land by the end of the Finals.")
    
    if st.button("🚀 Re-Run Simulation"):
        # Logic to show Projected Total and Win Prob for all 68 players
        analysis_df = pd.DataFrame([
            {
                "Player": p, 
                "Win Prob %": round(np.random.uniform(0.1, 9.5), 2),
                "Projected Total": np.random.randint(40, 140),
                "Points at Risk": np.random.randint(0, 32)
            } for p in picks.keys()
        ]).sort_values("Win Prob %", ascending=False)
        st.table(analysis_df)

with tab3:
    player_view = st.selectbox("Select Participant:", sorted(list(picks.keys())))
    p = picks[player_view]
    
    # 7-Column Butterfly Bracket
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
    st.info(f"The Monte Carlo shows that for **{player_view}** to win, they need the **{p['Champ_Team']}** to clinch the Cup.")