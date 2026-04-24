import streamlit as st
import pandas as pd
import numpy as np
import json
import requests

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="CDU NHL Pool 2026", layout="wide", page_icon="🏒")

# --- 2. DATA LOADERS ---
def load_data():
    # Ensure this matches your GitHub filename exactly
    with open('picks_68.json', 'r') as f:
        return json.load(f)

def get_live_scores():
    # This acts as your 'Manual API' until you connect the real one
    return {
        "COL_LAK": (3, 0), "CAR_OTT": (3, 0), "PIT_PHI": (0, 3),
        "BUF_BOS": (2, 1), "DAL_MIN": (2, 1), "TBL_MTL": (1, 1),
        "VGK_UTA": (1, 1), "EDM_ANA": (1, 1)
    }

# --- 3. THE INTERFACE ---
st.title("🏆 2026 Stanley Cup Pool Dashboard")
picks = load_data()
live_data = get_live_scores()

# Main Navigation
tab1, tab2 = st.tabs(["📊 Visual Bracket & Leaderboard", "🎲 Probabilities"])

with tab1:
    player = st.selectbox("Select Participant:", sorted(list(picks.keys())))
    p = picks[player]
    
    # Visual Bracket: R1 | R2 | CF | FINAL | CF | R2 | R1
    cols = st.columns([1.5, 1.2, 1, 1.5, 1, 1.2, 1.5])

    # WEST SIDE
    with cols[0]:
        st.caption("WEST R1")
        st.info(f"**{p['R1_Teams'][0]}**")
        st.info(f"**{p['R1_Teams'][1]}**")
        st.write("---")
        st.info(f"**{p['R1_Teams'][2]}**")
        st.info(f"**{p['R1_Teams'][3]}**")
    with cols[1]:
        st.caption("WEST R2")
        st.warning(f"**{p['R2_Teams'][0]}**")
        st.write("---")
        st.warning(f"**{p['R2_Teams'][1]}**")
    with cols[2]:
        st.caption("W. FINAL")
        st.error(f"**{p['CF_Teams'][0]}**")

    # CENTER (CHAMPION)
    with cols[3]:
        st.subheader("🏆 CHAMPION")
        st.success(f"### {p['Champ_Team']}")
        st.metric("Series Length", f"{p['Champ_Games']} Games")

    # EAST SIDE
    with cols[4]:
        st.caption("E. FINAL")
        st.error(f"**{p['CF_Teams'][1]}**")
    with cols[5]:
        st.caption("EAST R2")
        st.warning(f"**{p['R2_Teams'][2]}**")
        st.write("---")
        st.warning(f"**{p['R2_Teams'][3]}**")
    with cols[6]:
        st.caption("EAST R1")
        st.info(f"**{p['R1_Teams'][4]}**")
        st.info(f"**{p['R1_Teams'][5]}**")
        st.write("---")
        st.info(f"**{p['R1_Teams'][6]}**")
        st.info(f"**{p['R1_Teams'][7]}**")

with tab2:
    st.subheader("Monte Carlo Standings")
    # Simulation and Leaderboard code...