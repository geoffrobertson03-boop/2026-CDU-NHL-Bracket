import streamlit as st
import pandas as pd
import numpy as np
import json
import requests

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="CDU NHL Pool 2026", layout="wide", page_icon="🏒")

st.markdown("""
    <style>
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .bracket-win { color: #28a745; font-weight: bold; }
    .bracket-loss { color: #dc3545; text-decoration: line-through; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADERS ---
@st.cache_data
def load_pool_data():
    with open('picks_68.json', 'r') as f:
        return json.load(f)

def get_live_scores():
    # In production, replace with: requests.get("https://api-web.nhle.com/v1/playoff-series").json()
    return {
        "COL_LAK": {"score": (3, 0), "status": "COL Lead 3-0"},
        "DAL_MIN": {"score": (2, 1), "status": "DAL Lead 2-1"},
        "VGK_UTA": {"score": (1, 1), "status": "Tied 1-1"},
        "EDM_ANA": {"score": (1, 1), "status": "Tied 1-1"},
        "BUF_BOS": {"score": (2, 1), "status": "BUF Lead 2-1"},
        "TBL_MTL": {"score": (1, 1), "status": "Tied 1-1"},
        "CAR_OTT": {"score": (3, 0), "status": "CAR Lead 3-0"},
        "PIT_PHI": {"score": (0, 3), "status": "PHI Lead 3-0"}
    }

# --- 3. MAIN DASHBOARD ---
st.title("🏆 CDU Stanley Cup Pool 2026")
picks = load_pool_data()
live_results = get_live_scores()

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📊 Standings & Brackets", "🎲 Monte Carlo Probs", "🔬 Sensitivity Analysis"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Leaderboard")
        # Placeholder for live calculation logic
        standings_df = pd.DataFrame({
            "Player": ["Willie Ma", "Morgan Wrishko", "Jack Kehoe"],
            "Score": [45, 42, 38],
            "R1 Bonus": [5, 2, 4]
        })
        st.table(standings_df)

    with col2:
        st.subheader("Participant Bracket Viewer")
        selected_player = st.selectbox("View Bracket For:", sorted(list(picks.keys())))
        
        # Displaying the bracket in a "Slick" way
        p_picks = picks[selected_player]
        st.write(f"**Predicted Champion:** {p_picks['Champ']}")
        
        # Display Round 1 matchups with live status
        r1_cols = st.columns(2)
        for i, team in enumerate(p_picks['R1']):
            col_idx = 0 if i < 4 else 1
            with r1_cols[col_idx]:
                st.write(f"Series {i+1}: **{team}**")

with tab2:
    st.subheader("Win Probabilities (10k Simulations)")
    if st.button("🔄 Recalculate Odds"):
        st.toast("Running Monte Carlo...")
        # (Insert the simulation logic provided in previous steps here)
        st.success("Willie Ma is the current statistical favorite (9.35%)")

with tab3:
    st.subheader("Sensitivity: 'The Path to Victory'")
    st.write("This shows how much your win % changes based on tonight's games.")
    
    # Sensitivity Chart Placeholder
    chart_data = pd.DataFrame(
        np.random.randn(5, 3),
        columns=['If COL Wins', 'If EDM Wins', 'If PHI Wins'],
        index=["Willie Ma", "Jack Kehoe", "Kira Wasylak", "Jason M.", "Cam W."]
    )
    st.bar_chart(chart_data)