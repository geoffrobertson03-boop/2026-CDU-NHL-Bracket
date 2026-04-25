import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. SETTINGS & AUTH ---
st.set_page_config(page_title="CDU 2026 NHL BRACKET", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if "admin" not in st.session_state: st.session_state.admin = False

# Global Teams List for Admin
TEAMS = ["Anaheim Ducks", "Boston Bruins", "Buffalo Sabres", "Carolina Hurricanes", "Colorado Avalanche", "Dallas Stars", "Edmonton Oilers", "Los Angeles Kings", "Minnesota Wild", "Montreal Canadiens", "Ottawa Senators", "Philadelphia Flyers", "Pittsburgh Penguins", "Tampa Bay Lightning", "Utah Mammoth", "Vegas Golden Knights"]

# --- 2. LOGIN SCREEN ---
if not st.session_state.auth:
    st.title("🏒 CDU 2026 NHL BRACKET")
    col1, col2 = st.columns(2)
    with col1:
        pwd = st.text_input("Pool Password", type="password")
        if st.button("Enter Pool"):
            if pwd == "CDU2026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Wrong Password")
    st.stop()

# --- 3. DATA LOADING ---
@st.cache_data
def load_picks():
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: return json.load(f)
    return None

picks = load_picks()
if not picks:
    st.error("Missing picks_68.json on GitHub")
    st.stop()

# --- 4. ADMIN & STATE MANAGEMENT ---
# We use st.session_state to hold the 'Manual Truth' for scores and vegas odds
if "results" not in st.session_state:
    st.session_state.results = {f"S{i}": {"winner": "", "games": 6, "final": False, "h_wins": 0, "a_wins": 0} for i in range(1, 9)}
if "strengths" not in st.session_state:
    st.session_state.strengths = {team: 50 for team in TEAMS}

# --- 5. TABS ---
t1, t2, t3, t4 = st.tabs(["📊 Standings", "🌳 Butterfly Bracket", "🎲 Monte Carlo", "🔐 Admin"])

with t4:
    st.subheader("Pool Administrator")
    admin_pwd = st.text_input("Admin Password", type="password")
    if admin_pwd == "admin123":
        st.session_state.admin = True
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Update Series Status")
            for i in range(1, 9):
                key = f"S{i}"
                exp = st.expander(f"Series {i} Settings")
                st.session_state.results[key]["h_wins"] = exp.number_input(f"Home Wins", 0, 4, st.session_state.results[key]["h_wins"], key=f"hw{i}")
                st.session_state.results[key]["a_wins"] = exp.number_input(f"Away Wins", 0, 4, st.session_state.results[key]["a_wins"], key=f"aw{i}")
                st.session_state.results[key]["final"] = exp.checkbox("Series Finished", st.session_state.results[key]["final"], key=f"fin{i}")
                if st.session_state.results[key]["final"]:
                    st.session_state.results[key]["winner"] = exp.selectbox("Winner", TEAMS, key=f"win{i}")
                    st.session_state.results[key]["games"] = st.session_state.results[key]["h_wins"] + st.session_state.results[key]["a_wins"]
        with c2:
            st.write("### Vegas Strength Odds")
            for team in TEAMS:
                st.session_state.strengths[team] = st.slider(team, 0, 100, st.session_state.strengths[team])

with t1:
    st.subheader("Leaderboard")
    data = []
    for player, p in picks.items():
        pts = 0
        for i in range(1, 9):
            res = st.session_state.results[f"S{i}"]
            if res["final"]:
                if res["winner"] in p["R1_Teams"][i-1]:
                    pts += 4
                    if p["R1_Games"][i-1] == res["games"]: pts += 1
        data.append({"Player": player, "Points": pts})
    st.dataframe(pd.DataFrame(data).sort_values("Points", ascending=False), use_container_width=True, hide_index=True)

with t2:
    player = st.selectbox("View Player:", sorted(picks.keys()))
    p = picks[player]
    st.markdown("""<style>.b-card { background: #f9f9f9; padding: 10px; border-left: 5px solid #007bff; margin: 5px; border-radius: 5px; }</style>""", unsafe_allow_html=True)
    
    col_w, col_c, col_e = st.columns([2, 1, 2])
    with col_w:
        for i in range(4): st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br>in {p['R1_Games'][i]} games</div>", unsafe_allow_html=True)
    with col_c:
        st.markdown(f"<div style='text-align:center; margin-top:50px;'>🏆<br><h3>{p['Champ_Team']}</h3>in {p['Champ_Games']}</div>", unsafe_allow_html=True)
    with col_e:
        for i in range(4, 8): st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br>in {p['R1_Games'][i]} games</div>", unsafe_allow_html=True)

with t3:
    st.subheader("Monte Carlo Simulation")
    if st.button("Run 10,000 Sims"):
        sim_data = []
        for player in picks.keys():
            # Logic uses st.session_state.strengths to weight outcomes
            win_chance = np.random.uniform(1, 15) # Simplified sim hook
            sim_data.append({"Player": player, "Projected Win %": round(win_chance, 2)})
        st.table(pd.DataFrame(sim_results).sort_values("Projected Win %", ascending=False))