import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. CONFIG & INITIALIZATION ---
st.set_page_config(page_title="CDU 2026 NHL BRACKET", layout="wide", page_icon="🏒")

if "auth" not in st.session_state: st.session_state.auth = False

# Pre-populated Round 1 Matchups
if "results" not in st.session_state:
    st.session_state.results = {
        "S1": {"home": "Colorado Avalanche", "away": "Los Angeles Kings", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0},
        "S2": {"home": "Dallas Stars", "away": "Minnesota Wild", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0},
        "S3": {"home": "Vegas Golden Knights", "away": "Utah Mammoth", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0},
        "S4": {"home": "Edmonton Oilers", "away": "Anaheim Ducks", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0},
        "S5": {"home": "Buffalo Sabres", "away": "Boston Bruins", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0},
        "S6": {"home": "Tampa Bay Lightning", "away": "Montreal Canadiens", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0},
        "S7": {"home": "Carolina Hurricanes", "away": "Ottawa Senators", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0},
        "S8": {"home": "Pittsburgh Penguins", "away": "Philadelphia Flyers", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0}
    }

# Vegas-Based Strength Odds (Admin can override)
if "strengths" not in st.session_state:
    st.session_state.strengths = {
        "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 88, 
        "Tampa Bay Lightning": 85, "Vegas Golden Knights": 82, "Dallas Stars": 80, 
        "Buffalo Sabres": 75, "Boston Bruins": 70, "Pittsburgh Penguins": 65, 
        "Minnesota Wild": 62, "Los Angeles Kings": 58, "Montreal Canadiens": 55, 
        "Ottawa Senators": 50, "Utah Mammoth": 45, "Anaheim Ducks": 40, "Philadelphia Flyers": 35
    }

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .b-card { background: white; padding: 12px; border-left: 5px solid #007bff; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .g-badge { font-size: 0.8rem; font-weight: bold; background: #f0f2f6; padding: 2px 6px; border-radius: 4px; color: #333; }
    .champ-card { background: linear-gradient(135deg, #FFD700 0%, #FFB900 100%); padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #DAA520; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if not st.session_state.auth:
    st.title("🏒 CDU 2026 NHL BRACKET")
    with st.container(border=True):
        pwd = st.text_input("Pool Password", type="password")
        if st.button("Access Dashboard"):
            if pwd == "CDU2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Incorrect password.")
    st.stop()

# --- 4. DATA LOADING ---
@st.cache_data
def load_picks():
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: return json.load(f)
    return None

picks = load_picks()
if not picks:
    st.error("Missing picks_68.json on GitHub root."); st.stop()

# --- 5. TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings", "🌳 Butterfly Bracket", "🎲 Monte Carlo", "🔐 Admin"])

# --- TAB 1: STANDINGS ---
with tab1:
    st.subheader("Leaderboard")
    standings = []
    for player, p in picks.items():
        score, wins = 0.0, 0
        for i in range(1, 9):
            res = st.session_state.results[f"S{i}"]
            if res["final"]:
                if res["winner"].lower() in p["R1_Teams"][i-1].lower():
                    score += 4
                    wins += 1
                    if p["R1_Games"][i-1] == res["games"]: score += 1
            else:
                if res["h_wins"] > res["a_wins"] and res["home"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
                elif res["a_wins"] > res["h_wins"] and res["away"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
        standings.append({"Player": player, "Points": round(score, 1), "Series Won": wins})
    
    st.dataframe(pd.DataFrame(standings).sort_values("Points", ascending=False), use_container_width=True, hide_index=True)

# --- TAB 2: BUTTERFLY BRACKET ---
with tab2:
    st.subheader("Visual Bracket")
    selected = st.selectbox("Select Participant:", sorted(picks.keys()))
    p = picks[selected]
    
    def get_game_pick(round_key, index):
        try:
            val = p.get(round_key, [])[index]