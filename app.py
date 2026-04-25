import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. CONFIG & AUTHENTICATION ---
st.set_page_config(page_title="CDU 2026 NHL BRACKET", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

# PRE-POPULATED 2026 MATCHUPS
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

if "strengths" not in st.session_state:
    st.session_state.strengths = {t: 50 for t in ["Colorado Avalanche", "Los Angeles Kings", "Dallas Stars", "Minnesota Wild", "Vegas Golden Knights", "Utah Mammoth", "Edmonton Oilers", "Anaheim Ducks", "Buffalo Sabres", "Boston Bruins", "Tampa Bay Lightning", "Montreal Canadiens", "Carolina Hurricanes", "Ottawa Senators", "Pittsburgh Penguins", "Philadelphia Flyers"]}

# --- 2. LOGIN ---
if not st.session_state.auth:
    st.title("🏒 CDU 2026 NHL BRACKET")
    if st.text_input("Password", type="password") == "CDU2026":
        if st.button("Login"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. DATA LOADING ---
def load_picks():
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: return json.load(f)
    return None

picks = load_picks()
if not picks:
    st.error("Missing picks_68.json"); st.stop()

# --- 4. TABS ---
t1, t2, t3, t4 = st.tabs(["📊 Standings", "🌳 Butterfly Bracket", "🎲 Monte Carlo", "🔐 Admin"])

# --- TAB 4: ADMIN (THE CONTROLLER) ---
with t4:
    st.header("⚙️ Admin Dashboard")
    if st.text_input("Admin Password", type="password") == "admin123":
        mode = st.radio("Action:", ["Update R1 Scores", "Setup Future Matchups (R2/CF)", "Set Team Strengths"])
        
        if mode == "Update R1 Scores":
            cols = st.columns(2)
            for i in range(1, 9):
                with cols[(i-1)%2]:
                    res = st.session_state.results[f"S1"] # Placeholder logic
                    res = st.session_state.results[f"S{i}"]
                    st.write(f"**{res['home']} vs {res['away']}**")
                    c1, c2, c3 = st.columns(3)
                    res["h_wins"] = c1.number_input(f"{res['home']} Wins", 0, 4, res["h_wins"], key=f"h{i}")
                    res["a_wins"] = c2.number_input(f"{res['away']} Wins", 0, 4, res["a_wins"], key=f"a{i}")
                    res["final"] = c3.checkbox("Series Final", res["final"], key=f"f{i}")
                    if res["final"]:
                        res["winner"] = st.selectbox(f"Winner S{i}", [res["home"], res["away"]], key=f"w{i}")
                        res["games"] = res["h_wins"] + res["a_wins"]

        elif mode == "Setup Future Matchups (R2/CF)":
            st.info("When Round 1 ends, enter the teams that advanced to Round 2.")
            # This would store state for the next rounds to show in the Butterfly Bracket

        elif mode == "Set Team Strengths":
            for t, s in st.session_state.strengths.items():
                st.session_state.strengths[t] = st.slider(t, 0, 100, s)

# --- TAB 1 & 2 logic would follow the session_state.results truth ---
with t1:
    st.write("Leaderboard updating based on Admin Scores...")
    # (Scoring logic here)