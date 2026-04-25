import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. CONFIG & AUTH ---
st.set_page_config(page_title="CDU 2026 NHL BRACKET", layout="wide", page_icon="🏒")

if "auth" not in st.session_state: st.session_state.auth = False
if "admin" not in st.session_state: st.session_state.admin = False

TEAMS = ["Anaheim Ducks", "Boston Bruins", "Buffalo Sabres", "Carolina Hurricanes", 
         "Colorado Avalanche", "Dallas Stars", "Edmonton Oilers", "Los Angeles Kings", 
         "Minnesota Wild", "Montreal Canadiens", "Ottawa Senators", "Philadelphia Flyers", 
         "Pittsburgh Penguins", "Tampa Bay Lightning", "Utah Mammoth", "Vegas Golden Knights"]

# Initializing the Admin Truth (Matchups and Scores)
if "results" not in st.session_state:
    st.session_state.results = {
        f"S{i}": {"home": "HOME", "away": "AWAY", "h_wins": 0, "a_wins": 0, "final": False, "winner": "", "games": 0} 
        for i in range(1, 9)
    }
if "strengths" not in st.session_state:
    st.session_state.strengths = {team: 50 for team in TEAMS}

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .b-card { background: #fefefe; padding: 12px; border-left: 5px solid #007bff; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .g-badge { color: #555; font-size: 0.8rem; font-weight: bold; background: #e9ecef; padding: 2px 6px; border-radius: 4px; }
    .wing-title { color: #666; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px; text-align: center; text-transform: uppercase; }
    .champ-card { background: linear-gradient(135deg, #FFD700 0%, #FFB900 100%); padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #DAA520; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if not st.session_state.auth:
    st.title("🏒 CDU 2026 NHL BRACKET")
    pwd = st.text_input("Pool Password", type="password")
    if st.button("Enter Dashboard"):
        if pwd == "CDU2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Incorrect password.")
    st.stop()

# --- 4. DATA LOADER ---
def load_picks():
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: return json.load(f)
    return None

picks = load_picks()
if not picks:
    st.error("Missing picks_68.json on GitHub.")
    st.stop()

# --- 5. TABS ---
t1, t2, t3, t4 = st.tabs(["📊 Standings", "🌳 Butterfly Bracket", "🎲 Monte Carlo", "🔐 Admin"])

# --- TAB 1: STANDINGS ---
with t1:
    st.subheader("Leaderboard")
    standings = []
    for player, p in picks.items():
        score = 0.0
        series_won = 0
        for i in range(1, 9):
            res = st.session_state.results[f"S{i}"]
            # Official Points
            if res["final"]:
                if any(res["winner"].lower() in t.lower() for t in [p["R1_Teams"][i-1]]):
                    score += 4
                    series_won += 1
                    if p["R1_Games"][i-1] == res["games"]: score += 1
            # Live Projected (0.1 for leading)
            else:
                if res["h_wins"] > res["a_wins"] and res["home"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
                elif res["a_wins"] > res["h_wins"] and res["away"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
        
        standings.append({"Player": player, "Points": round(score, 1), "Series ✅": series_won})
    
    df_standings = pd.DataFrame(standings).sort_values("Points", ascending=False)
    st.dataframe(df_standings, use_container_width=True, hide_index=True)
    st.caption("Fractional points (0.1) indicate you are currently leading an active series.")

# --- TAB 2: BUTTERFLY BRACKET ---
with t2:
    st.subheader("The Butterfly Bracket")
    player_sel = st.selectbox("Select Participant:", sorted(picks.keys()))
    p = picks[player_sel]
    
    def get_g(key, idx):
        try: return p.get(key, [])[idx]
        except: return "?"

    c1, c2, c3, c4, c5, c6, c7 = st.columns([1.1, 1, 1, 1.4, 1, 1, 1.1])
    with c1:
        st.markdown("<div class='wing-title'>West R1</div>", unsafe_allow_html=True)
        for i in range(4): st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br><span class='g-badge'>{p['R1_Games'][i]} Games</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='wing-title'>West R2</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:45px;'><b>{get_g('R2_Teams', 0)}</b><br><span class='g-badge'>{get_g('R2_Games', 0)} G</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:85px;'><b>{get_p('R2_Teams', 1)}</b><br><span class='g-badge'>{get_g('R2_Games', 1)} G</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='wing-title'>West Final</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:115px;'><b>{get_g('CF_Teams', 0)}</b><br><span class='g-badge'>{get_g('CF_Games', 0)} G</span></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='wing-title'>2026 Champion</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='champ-card' style='margin-top:90px;'><h3>{p['Champ_Team']}</h3>🏆 in {p['Champ_Games']}</div>", unsafe_allow_html=True)
    with c5:
        st.markdown("<div class='wing-title'>East Final</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:115px;'><b>{get_g('CF_Teams', 1)}</b><br><span class='g-badge'>{get_g('CF_Games', 1)} G</span></div>", unsafe_allow_html=True)
    with c6:
        st.markdown("<div class='wing-title'>East R2</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:45px;'><b>{get_g('R2_Teams', 2)}</b><br><span class='g-badge'>{get_g('R2_Games', 2)} G</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:85px;'><b>{get_p('R2_Teams', 3)}</b><br><span class='g-badge'>{get_g('R2_Games', 3)} G</span></div>", unsafe_allow_html=True)
    with c7:
        st.markdown("<div class='wing-title'>East R1</div>", unsafe_allow_html=True)
        for i in range(4, 8): st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br><span class='g-badge'>{p['R1_Games'][i]} Games</span></div>", unsafe_allow_html=True)

# --- TAB 3: MONTE CARLO ---
with t3:
    st.subheader("Monte Carlo Simulation")
    if st.button("Run 10,000 Simulations"):
        results_list = []
        for player, data in picks.items():
            win_pct = np.random.uniform(0.1, 15.0) # Placeholder logic for the simulation hook
            results_list.append({"Player": player, "Win Probability": f"{round(win_pct, 2)}%"})
        st.table(pd.DataFrame(results_list).sort_values("Win Probability", ascending=False))

# --- TAB 4: ADMIN ---
with t4:
    admin_pwd = st.text_input("Admin Password", type="password")
    if admin_pwd == "admin123":
        st.session_state.admin = True
        sub1, sub2, sub3 = st.tabs(["Matchup Setup", "Scores", "Strengths"])
        with sub1:
            for i in range(1, 9):
                c_a, c_b = st.columns(2)
                st.session_state.results[f"S{i}"]["home"] = c_a.text_input(f"S{i} Home", st.session_state.results[f"S{i}"]["home"])
                st.session_state.results[f"S{i}"]["away"] = c_b.text_input(f"S{i} Away", st.session_state.results[f"S{i}"]["away"])
        with sub2:
            for i in range(1, 9):
                key = f"S{i}"
                res = st.session_state.results[key]
                st.write(f"**Series {i}: {res['home']} vs {res['away']}**")
                c1, c2, c3 = st.columns(3)
                res["h_wins"] = c1.number_input(f"{res['home']} Wins", 0, 4, res["h_wins"], key=f"h{i}")
                res["a_wins"] = c2.number_input(f"{res['away']} Wins", 0, 4, res["a_wins"], key=f"a{i}")
                res["final"] = c3.checkbox("Final", res["final"], key=f"f{i}")
                if res["final"]:
                    res["winner"] = st.selectbox(f"Winner S{i}", [res["home"], res["away"]], key=f"w{i}")
                    res["games"] = res["h_wins"] + res["a_wins"]
        with sub3:
            for team in TEAMS:
                st.session_state.strengths[team] = st.slider(team, 0, 100, st.session_state.strengths[team])