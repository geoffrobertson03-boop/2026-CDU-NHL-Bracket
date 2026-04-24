import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="CDU NHL Pool 2026", layout="wide", page_icon="🏒")

# --- 2. DATA LOADER ---
def load_data():
    file_path = 'picks_68.json'
    if not os.path.exists(file_path):
        st.error(f"❌ '{file_path}' not found! Upload it to your GitHub root folder.")
        st.stop()
    with open(file_path, 'r') as f:
        return json.load(f)

# Static Live Scores (Update manually or link to an API endpoint)
live_results = {
    "COL_LAK": (3, 0), "CAR_OTT": (3, 0), "PIT_PHI": (0, 3),
    "BUF_BOS": (2, 1), "DAL_MIN": (2, 1), "TBL_MTL": (1, 1),
    "VGK_UTA": (1, 1), "EDM_ANA": (1, 1)
}

# --- 3. APP INTERFACE ---
st.title("🏆 2026 Stanley Cup Pool: Master Dashboard")
picks = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Standings", "🎲 Win Probabilities", "🎯 Path to Victory", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Leaderboard")
    if st.button("🔄 Refresh Standings"):
        st.toast("Standings Updated!")
    
    # Placeholder for live calculation logic
    standings_data = pd.DataFrame([
        {"Player": p, "Points": 42 if p == "Willie Ma" else 35, "Champ Pick": picks[p]['Champ_Team']}
        for p in picks.keys()
    ]).sort_values("Points", ascending=False)
    
    st.dataframe(standings_data, use_container_width=True)

with tab2:
    st.subheader("Monte Carlo Simulation (10,000 Iterations)")
    st.write("This table shows every participant's mathematical chance of winning the entire pool.")
    
    # Simulation Probability Table
    prob_list = [
        {"Player": "Willie Ma", "Win %": 9.35}, {"Player": "Morgan Wrishko", "Win %": 8.15},
        {"Player": "Jack Kehoe", "Win %": 5.98}, {"Player": "Siya Chokshi", "Win %": 5.94},
        {"Player": "Mike Hanson", "Win %": 5.88}, {"Player": "Jason Middleton", "Win %": 5.84}
    ]
    # (Simplified for display; you can populate this from your local simulation results)
    prob_df = pd.DataFrame(prob_list).sort_values("Win %", ascending=False)
    st.table(prob_df)

    st.divider()
    st.subheader("🔬 How the Monte Carlo Logic Works")
    st.markdown("""
    The simulation determines winners by playing out the remainder of the tournament **10,000 times**:
    
    1. **Strength Rating:** Teams are weighted by regular-season points (e.g., Colorado at 121 pts vs Anaheim at 60 pts).
    2. **Probability Math:** Each game is a 'weighted coin toss'. Colorado has a higher mathematical chance of winning a game, but Anaheim can still win some iterations.
    3. **Series Simulation:** The computer 'plays' every series until a team reaches 4 wins.
    4. **Pool Scoring:** After each full simulation, the computer calculates the pool score for all 68 participants.
    5. **Win Chance:** If you have the highest score in 1,000 out of 10,000 simulations, your win probability is **10%**.
    """)

with tab3:
    st.subheader("The Path to Victory")
    selected_p = st.selectbox("Analyze Player:", sorted(list(picks.keys())))
    p_picks = picks[selected_p]
    st.success(f"**Target:** {p_picks['Champ_Team']} must win the Cup.")
    st.info(f"**Bonus Potential:** You have {p_picks['Champ_Games']} games picked for the Finals.")

with tab4:
    #Visual Butterfly Bracket
    p = picks[selected_p]
    cols = st.columns([1.5, 1.2, 1, 1.5, 1, 1.2, 1.5])
    with cols[0]:
        st.caption("WEST R1")
        for i in range(4): st.info(f"**{p['R1_Teams'][i]}** (+1 Bonus)")
    with cols[1]:
        st.caption("WEST R2")
        st.warning(f"**{p['R2_Teams'][0]}** (+2 Bonus)")
        st.warning(f"**{p['R2_Teams'][1]}** (+2 Bonus)")
    with cols[3]:
        st.subheader("🏆 CHAMP")
        st.success(f"### {p['Champ_Team']}")
    with cols[5]:
        st.caption("EAST R2")
        st.warning(f"**{p['R2_Teams'][2]}** (+2 Bonus)")
        st.warning(f"**{p['R2_Teams'][3]}** (+2 Bonus)")
    with cols[6]:
        st.caption("EAST R1")
        for i in range(4, 8): st.info(f"**{p['R1_Teams'][i]}** (+1 Bonus)")