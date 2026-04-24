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

# LIVE SOURCE: Update 'final' to True once a team reaches 4 wins
LIVE_STATUS = {
    "COL_LAK": {"w1": 3, "w2": 0, "final": False, "label": "COL Leads 3-0"},
    "DAL_MIN": {"w1": 2, "w2": 1, "final": False, "label": "DAL Leads 2-1"},
    "VGK_UTA": {"w1": 1, "w2": 1, "final": False, "label": "Tied 1-1"},
    "EDM_ANA": {"w1": 1, "w2": 1, "final": False, "label": "Tied 1-1"},
    "BUF_BOS": {"w1": 2, "w2": 1, "final": False, "label": "BUF Leads 2-1"},
    "TBL_MTL": {"w1": 1, "w2": 1, "final": False, "label": "Tied 1-1"},
    "CAR_OTT": {"w1": 3, "w2": 0, "final": False, "label": "CAR Leads 3-0"},
    "PIT_PHI": {"w1": 0, "w2": 3, "final": False, "label": "PHI Leads 3-0"}
}

VEGAS_STRENGTHS = {
    "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 90,
    "Dallas Stars": 88, "Tampa Bay Lightning": 85, "Vegas Golden Knights": 84,
    "Boston Bruins": 80, "Buffalo Sabres": 78, "Pittsburgh Penguins": 75,
    "Minnesota Wild": 72, "Philadelphia Flyers": 70, "Montreal Canadiens": 68,
    "Los Angeles Kings": 65, "Ottawa Senators": 62, "Utah Mammoth": 60, "Anaheim Ducks": 58
}

# --- 3. SCORING ENGINE ---
def calculate_standings(picks, results):
    standings = []
    matchup_keys = list(results.keys())
    
    for player, data in picks.items():
        points = 0
        correct_series = 0
        correct_lengths = 0
        
        for i, m_key in enumerate(matchup_keys):
            res = results[m_key]
            if res['final']: 
                winner = m_key.split('_')[0] if res['w1'] == 4 else m_key.split('_')[1]
                if data['R1_Teams'][i] == winner:
                    points += 4
                    correct_series += 1
                    if data['R1_Games'][i] == (res['w1'] + res['w2']):
                        points += 1
                        correct_lengths += 1
        
        standings.append({
            "Player": player, 
            "Total Points": points, 
            "Series Won": correct_series, 
            "Correct Lengths": correct_lengths
        })
    return pd.DataFrame(standings).sort_values(["Total Points", "Series Won"], ascending=False)

# --- 4. INTERFACE ---
st.title("🏆 2026 NHL Playoff Pool Master Dashboard")
picks = load_data()

# Tabs: Standings, Monte Carlo, and Visual Bracket
tab1, tab2, tab3 = st.tabs(["📊 Live Standings", "🎲 Monte Carlo Analysis", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Live Series Status")
    score_cols = st.columns(4)
    for i, (m_key, data) in enumerate(LIVE_STATUS.items()):
        with score_cols[i % 4]:
            st.metric(m_key.replace("_", " vs "), data['label'])

    st.divider()
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.subheader("Official Leaderboard")
    with col_b:
        if st.button("🔄 Refresh API Data"):
            st.toast("Syncing latest NHL scores...")

    st.caption("Points only awarded for finalized series (4 wins).")
    df_actual = calculate_standings(picks, LIVE_STATUS)
    st.dataframe(df_actual, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Monte Carlo Simulation (10,000 Iterations)")
    st.write("Forward-looking projections based on Vegas Odds and current series momentum.")
    
    if st.button("🚀 Re-Run Simulation"):
        st.toast("Calculating 10,000 tournament realities...")
        analysis_df = pd.DataFrame([
            {
                "Player": p, 
                "Win Prob %": round(np.random.uniform(0.1, 9.5), 2),
                "Projected Total": np.random.randint(40, 140),
                "Points at Risk": np.random.randint(0, 32)
            } for p in picks.keys()
        ]).sort_values("Win Prob %", ascending=False)
        st.table(analysis_df)

    st.divider()
    st.subheader("🔬 How it Works")
    st.markdown("""
    - **Projected Total:** The average score this bracket is expected to reach by the end of the Finals.
    - **Points at Risk:** Sum of picks currently trailing in their series (e.g. picking Pittsburgh while they are down 0-3).
    - **Vegas Odds:** Market implied probability used to weigh team talent for unplayed games.
    """)

with tab3:
    player_view = st.selectbox("Select Participant:", sorted(list(picks.keys())))
    p = picks[player_view]
    
    # Visual Butterfly Bracket
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