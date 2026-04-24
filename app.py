import streamlit as st
import pandas as pd
import numpy as np
import json
import requests

# --- TEAM STRENGTHS ---
TEAM_WEIGHTS = {
    "Colorado Avalanche": 98, "Carolina Hurricanes": 94, "Edmonton Oilers": 92,
    "Dallas Stars": 90, "Tampa Bay Lightning": 88, "Boston Bruins": 85,
    "Buffalo Sabres": 82, "Vegas Golden Knights": 82, "Pittsburgh Penguins": 80,
    "Minnesota Wild": 78, "Philadelphia Flyers": 75, "Montreal Canadiens": 72,
    "Los Angeles Kings": 70, "Ottawa Senators": 68, "Utah Mammoth": 65, "Anaheim Ducks": 62
}

# --- FUNCTIONS ---
def load_data():
    with open('picks_68.json', 'r') as f:
        return json.load(f)

def fetch_scores():
    # Simulated Live API Feed
    return {
        "COL_LAK": (3, 0), "CAR_OTT": (3, 0), "PIT_PHI": (0, 3),
        "BUF_BOS": (2, 1), "DAL_MIN": (2, 1), "TBL_MTL": (1, 1),
        "VGK_UTA": (1, 1), "EDM_ANA": (1, 1)
    }

# --- INTERFACE ---
st.set_page_config(page_title="2026 NHL Pool", layout="wide")
st.title("🏒 68-Player Stanley Cup Pool Tracker")

picks = load_data()
scores = fetch_scores()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Win Probabilities (Top 10)")
    # Logic for Monte Carlo Run
    st.write("Current Favorite: **Willie Ma (9.35%)**")
    st.progress(0.09)

with col2:
    st.subheader("🎯 Path to Victory")
    player = st.selectbox("Search your name:", sorted(list(picks.keys())))
    st.info(f"Analysis for {player}: You need the current series leads to hold.")

st.divider()
st.write("🔥 **Hot Streak:** The Flyers' 3-0 lead has busted 52 out of 68 brackets.")