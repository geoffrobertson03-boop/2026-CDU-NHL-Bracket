import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. CONFIG & AUTHENTICATION ---
st.set_page_config(page_title="CDU 2026 NHL BRACKET", layout="wide", page_icon="🏒")

if "auth" not in st.session_state: st.session_state.auth = False

# Pre-populated Matchups (Admin can change these if seeds shift)
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

# Vegas Strengths (Pre-populated)
if "strengths" not in st.session_state:
    st.session_state.strengths = {
        "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 88, 
        "Tampa Bay Lightning": 85, "Vegas Golden Knights": 82, "Dallas Stars": 80, 
        "Buffalo Sabres": 75, "Boston Bruins": 70, "Pittsburgh Penguins": 65, 
        "Minnesota Wild": 62, "Los Angeles Kings": 58, "Montreal Canadiens": 55, 
        "Ottawa Senators": 50, "Utah Mammoth": 45, "Anaheim Ducks": 40, "Philadelphia Flyers": 35
    }

# --- 2. THE LOGIN GATE ---
if not st.session_state.auth:
    st.title("🏒 CDU 2026 NHL BRACKET")
    pwd = st.text_input("Enter Pool Password", type="password")
    if st.button("Access Dashboard"):
        if pwd == "CDU2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Incorrect password.")
    st.stop()

# --- 3. DATA LOADING ---
@st.cache_data
def load_picks():
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: return json.load(f)
    return None

picks = load_picks()
if not picks:
    st.error("Missing picks_68.json file on GitHub root."); st.stop()

# --- 4. CSS STYLING ---
st.markdown("""
    <style>
    .b-card { background: white; padding: 12px; border-left: 5px solid #007bff; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .g-badge { font-size: 0.8rem; font-weight: bold; background: #e9ecef; padding: 2px 6px; border-radius: 4px; color: #444; }
    .champ-box { background: linear-gradient(135deg, #FFD700 0%, #FFB900 100%); padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #DAA520; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings", "🌳 Butterfly Bracket", "🎲 Monte Carlo", "🔐 Admin"])

# --- TAB 1: LEADERBOARD ---
with tab1:
    st.subheader("Current Leaderboard")
    leaderboard = []
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
                # Live Lead Bonus
                if res["h_wins"] > res["a_wins"] and res["home"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
                elif res["a_wins"] > res["h_wins"] and res["away"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
        leaderboard.append({"Player": player, "Total Points": round(score, 1), "Series Won": wins})
    
    st.dataframe(pd.DataFrame(leaderboard).sort_values("Total Points", ascending=False), use_container_width=True, hide_index=True)

# --- TAB 2: BUTTERFLY BRACKET ---
with tab2:
    sel = st.selectbox("Select Participant:", sorted(picks.keys()))
    p = picks[sel]
    def safe_g(key, i): 
        try: return f"{p[key][i]} G"
        except: return "—"

    c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1, 1.4, 1, 1, 1])
    with c1: # West R1
        for i in range(4): st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br><span class='g-badge'>{p['R1_Games'][i]} G</span></div>", unsafe_allow_html=True)
    with c2: # West R2
        st.markdown(f"<div class='b-card' style='margin-top:40px;'><b>{p['R2_Teams'][0]}</b><br><span class='g-badge'>{safe_g('R2_Games', 0)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:80px;'><b>{p['R2_Teams'][1]}</b><br><span class='g-badge'>{safe_g('R2_Games', 1)}</span></div>", unsafe_allow_html=True)
    with c3: # West Final
        st.markdown(f"<div class='b-card' style='margin-top:100px;'><b>{p['CF_Teams'][0]}</b><br><span class='g-badge'>{safe_g('CF_Games', 0)}</span></div>", unsafe_allow_html=True)
    with c4: # Champion
        st.markdown(f"<div class='champ-box' style='margin-top:85px;'>🏆<h3>{p['Champ_Team']}</h3>in {p['Champ_Games']}</div>", unsafe_allow_html=True)
    with c5: # East Final
        st.markdown(f"<div class='b-card' style='margin-top:100px;'><b>{p['CF_Teams'][1]}</b><br><span class='g-badge'>{safe_g('CF_Games', 1)}</span></div>", unsafe_allow_html=True)
    with c6: # East R2
        st.markdown(f"<div class='b-card' style='margin-top:40px;'><b>{p['R2_Teams'][2]}</b><br><span class='g-badge'>{safe_g('R2_Games', 2)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:80px;'><b>{p['R2_Teams'][3]}</b><br><span class='g-badge'>{safe_g('R2_Games', 3)}</span></div>", unsafe_allow_html=True)
    with c7: # East R1
        for i in range(4, 8): st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br><span class='g-badge'>{p['R1_Games'][i]} G</span></div>", unsafe_allow_html=True)

# --- TAB 3: MONTE CARLO ---
with tab3:
    if st.button("Run 1,000 Simulations"):
        win_sims = {name: 0 for name in picks.keys()}
        for _ in range(1000):
            sim_winners = []
            for i in range(1, 9):
                res = st.session_state.results[f"S{i}"]
                h_str, a_str = st.session_state.strengths[res["home"]], st.session_state.strengths[res["away"]]
                sim_winners.append(np.random.choice([res["home"], res["away"]], p=[h_str/(h_str+a_str), a_str/(h_str+a_str)]))
            p_scores = {n: sum(4 for idx, t in enumerate(sim_winners) if t.lower() in picks[n]["R1_Teams"][idx].lower()) for n in picks.keys()}
            win_sims[max(p_scores, key=p_scores.get)] += 1
        st.table(pd.DataFrame([{"Player": k, "Win %": f"{v/10}%"} for k, v in win_sims.items()]).sort_values("Win %", ascending=False).head(10))

# --- TAB 4: ADMIN ---
with tab4:
    if st.text_input("Admin Password", type="password") == "admin123":
        for i in range(1, 9):
            res = st.session_state.results[f"S{i}"]
            st.write(f"**Series {i}: {res['home']} vs {res['away']}**")
            c1, c2, c3 = st.columns(3)
            res["h_wins"] = c1.number_input(f"{res['home']} Wins", 0, 4, res["h_wins"], key=f"h{i}")
            res["a_wins"] = c2.number_input(f"{res['away']} Wins", 0, 4, res["a_wins"], key=f"a{i}")
            res["final"] = c3.checkbox("Series Final", res["final"], key=f"f{i}")
            if res["final"]:
                res["winner"] = st.selectbox("Select Winner", [res["home"], res["away"]], key=f"w{i}")
                res["games"] = res["h_wins"] + res["a_wins"]