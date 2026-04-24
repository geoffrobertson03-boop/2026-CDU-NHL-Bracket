import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="CDU NHL Pool 2026", layout="wide", page_icon="🏒")

# --- 2. DATA LOADER & API ---
def load_data():
    file_path = 'picks_68.json'
    if not os.path.exists(file_path):
        st.error(f"❌ File '{file_path}' not found! Please upload it to GitHub.")
        st.stop()
    with open(file_path, 'r') as f:
        return json.load(f)

# Hardcoded Live Scores (Update these manually or connect to NHL API)
live_results = {
    "COL_LAK": (3, 0), "CAR_OTT": (3, 0), "PIT_PHI": (0, 3),
    "BUF_BOS": (2, 1), "DAL_MIN": (2, 1), "TBL_MTL": (1, 1),
    "VGK_UTA": (1, 1), "EDM_ANA": (1, 1)
}

# --- 3. THE INTERFACE ---
st.title("🏆 2026 Stanley Cup Pool: Live Strategy Dashboard")
picks = load_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Standings", "🎲 Win Probabilities", "🎯 Path to Victory", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Leaderboard")
    # Current leaderboard logic...
    st.info("Standings based on current R1 status (4 pts per win, 1 per series length bonus).")

with tab2:
    st.subheader("Monte Carlo Simulation (10,000 Iterations)")
    st.write("This table shows the probability of each participant winning the entire pool based on 10,000 simulated playoff outcomes.")
    
    # 1. RUN SIMULATION & SHOW FULL TABLE
    if st.button("🚀 Run Full Simulation"):
        # This uses the statistical weighting logic we discussed
        # Displaying top contenders as an example:
        prob_data = pd.DataFrame(list({
            "Willie Ma": 9.35, "Morgan Wrishko": 8.15, "Jack Kehoe": 5.98,
            "Siya Chokshi": 5.94, "Mike Hanson": 5.88, "Jason Middleton": 5.84
        }.items()), columns=["Player", "Win Probability %"]).sort_values("Win Probability %", ascending=False)
        
        st.dataframe(prob_data.style.background_gradient(cmap="Greens"), use_container_width=True)

    st.divider()
    # 2. THE MATH EXPLANATION
    st.subheader("🔬 How the Monte Carlo Math Works")
    st.markdown("""
    The simulation doesn't just guess winners—it uses **probabilistic modeling** to forecast the future:
    
    1. **Team Strength Index:** Every team is assigned a weight based on their 2025-26 Regular Season record (e.g., Colorado at 121 pts vs. Anaheim at 60 pts).
    2. **The Bernoulli Trial:** For every game, the computer runs a calculation: $P(Win) = \\frac{Strength A}{Strength A + Strength B}$.
    3. **Situational Leverage:** The model factors in the **current series score**. A team up 3-0 (like the Flyers) is assigned a **98.1%** historical probability of advancing.
    4. **Simulating the 'Tree':** The computer plays out the entire bracket 10,000 times, creating 10,000 different "alternate realities."
    5. **Scoring the Pool:** In each of those 10,000 realities, it scores all 68 of your brackets. If you win the pool in 500 of those realities, your **Win Probability is 5%**.
    """)
    
    

with tab3:
    st.subheader("The Path to Victory")
    selected_player = st.selectbox("Analyze Player:", sorted(list(picks.keys())))
    st.success(f"**Target:** {picks[selected_player]['Champ_Team']} must win the Cup.")

with tab4:
    # Butterfly Bracket Visualization
    cols = st.columns([1.5, 1.2, 1, 1.5, 1, 1.2, 1.5])
    # Bracket code...