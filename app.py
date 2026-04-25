import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# --- 1. CONFIG & INITIALIZATION ---
st.set_page_config(page_title="CDU 2026 NHL BRACKET", layout="wide", page_icon="🏒")

if "auth" not in st.session_state: st.session_state.auth = False

# Official 2026 Matchups Pre-populated
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

# Vegas-Based Strength Odds (Pre-populated)
if "strengths" not in st.session_state:
    st.session_state.strengths = {
        "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 88, 
        "Tampa Bay Lightning": 85, "Vegas Golden Knights": 82, "Dallas Stars": 80, 
        "Buffalo Sabres": 75, "Boston Bruins": 70, "Pittsburgh Penguins": 65, 
        "Minnesota Wild": 62, "Los Angeles Kings": 58, "Montreal Canadiens": 55, 
        "Ottawa Senators": 50, "Utah Mammoth": 45, "Anaheim Ducks": 40, "Philadelphia Flyers": 35
    }

# --- 2. STYLES ---
st.markdown("""
    <style>
    .b-card { background: white; padding: 12px; border-left: 5px solid #007bff; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .g-badge { font-size: 0.8rem; font-weight: bold; background: #f0f2f6; padding: 2px 6px; border-radius: 4px; color: #333; }
    .champ-card { background: linear-gradient(135deg, #FFD700 0%, #FFB900 100%); padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #DAA520; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN ---
if not st.session_state.auth:
    st.title("🏒 CDU 2026 NHL BRACKET")
    with st.container(border=True):
        pwd = st.text_input("Enter Pool Password", type="password")
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
    st.error("Missing picks_68.json on GitHub."); st.stop()

# --- 5. TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings", "🌳 Butterfly Bracket", "🎲 Monte Carlo", "🔐 Admin"])

# --- TAB 1: STANDINGS ---
with tab1:
    st.subheader("Leaderboard")
    standings = []
    for player, p in picks.items():
        score = 0.0
        series_won = 0
        for i in range(1, 9):
            res = st.session_state.results[f"S{i}"]
            if res["final"]:
                if res["winner"].lower() in p["R1_Teams"][i-1].lower():
                    score += 4
                    series_won += 1
                    if p["R1_Games"][i-1] == res["games"]: score += 1
            else:
                if res["h_wins"] > res["a_wins"] and res["home"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
                elif res["a_wins"] > res["h_wins"] and res["away"].lower() in p["R1_Teams"][i-1].lower(): score += 0.1
        standings.append({"Player": player, "Points": round(score, 1), "Series Won": series_won})
    
    st.dataframe(pd.DataFrame(standings).sort_values("Points", ascending=False), use_container_width=True, hide_index=True)
    st.caption("Fractional points (0.1) show you are currently leading an active series.")

# --- TAB 2: BUTTERFLY BRACKET ---
with tab2:
    st.subheader("Visual Bracket")
    selected = st.selectbox("Select Participant:", sorted(picks.keys()))
    p = picks[selected]
    
    # Improved helper to find game picks for future rounds
    def get_game_pick(round_key, index):
        try:
            val = p.get(round_key, [])[index]
            return f"{val} G"
        except:
            return "—" # Fallback if specific pick is missing

    # Layout: [W-R1, W-R2, W-CF, CHAMP, E-CF, E-R2, E-R1]
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1, 1.4, 1, 1, 1])
    
    with c1: # West R1
        for i in range(4): 
            st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br><span class='g-badge'>{p['R1_Games'][i]} Games</span></div>", unsafe_allow_html=True)
    
    with c2: # West R2 (Semis)
        st.markdown(f"<div class='b-card' style='margin-top:40px;'><b>{p['R2_Teams'][0]}</b><br><span class='g-badge'>{get_game_pick('R2_Games', 0)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='b-card' style='margin-top:80px;'><b>{p['R2_Teams'][1]}</b><br><span class='g-badge'>{get_game_pick('R2_Games', 1)}</span></div>", unsafe_allow_html=True)
    
    with c3: # West Final
        st.markdown(f"<div class='b-card' style='margin-top:110px;'><b>{p['CF_Teams'][0]}</b><br><span class='g-badge'>{get_game_pick('CF_Games', 0)}</span></div>", unsafe_allow_html=True)
    
    with c4: # Champion (The Centerpiece)
        st.markdown(f"""
            <div class='champ-box' style='margin-top:85px;'>
                <h1 style='margin:0;'>🏆</h1>
                <h2 style='margin:10px 0;'>{p['Champ_Team']}</h2>
                <div class='g-badge' style='background: rgba(255,255,255,0.4);'>PICKED IN {p['Champ_Games']} GAMES</div>
            </div>
        """, unsafe_allow_html=True)
    
    with c5: # East Final
        st.markdown(f"<div class='b-card' style='margin-top:110px;'><b>{p['CF_Teams'][1]}</b><br><span class='g-badge'>{get_game_pick('CF_Games', 1)}</span></div>", unsafe_allow_html=True)
    
    with c6: # East R2 (Semis)
        st.markdown(f"<div class='bracket-card' style='margin-top:40px;'><b>{p['R2_Teams'][2]}</b><br><span class='g-badge'>{get_game_pick('R2_Games', 2)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bracket-card' style='margin-top:80px;'><b>{p['R2_Teams'][3]}</b><br><span class='g-badge'>{get_game_pick('R2_Games', 3)}</span></div>", unsafe_allow_html=True)
    
    with c7: # East R1
        for i in range(4, 8): 
            st.markdown(f"<div class='b-card'><b>{p['R1_Teams'][i]}</b><br><span class='g-badge'>{p['R1_Games'][i]} Games</span></div>", unsafe_allow_html=True)

# --- TAB 3: MONTE CARLO ---
with tab3:
    st.subheader("Win Probability Simulation")
    if st.button("Run 1,000 Simulations"):
        results = {name: 0 for name in picks.keys()}
        for _ in range(1000):
            sim_winners = []
            for i in range(1, 9):
                res = st.session_state.results[f"S{i}"]
                h_s, a_s = st.session_state.strengths[res["home"]], st.session_state.strengths[res["away"]]
                winner = np.random.choice([res["home"], res["away"]], p=[h_s/(h_s+a_s), a_s/(h_s+a_s)])
                sim_winners.append(winner)
            
            p_scores = {name: sum(4 for idx, team in enumerate(sim_winners) if team.lower() in picks[name]["R1_Teams"][idx].lower()) for name in picks.keys()}
            winner_name = max(p_scores, key=p_scores.get)
            results[winner_name] += 1
        
        sim_df = pd.DataFrame([{"Player": k, "Win %": f"{(v/10)}%"} for k, v in results.items()])
        st.table(sim_df.sort_values("Win %", ascending=False).head(10))

# --- TAB 4: ADMIN ---
with tab4:
    if st.text_input("Admin Password", type="password") == "admin123":
        task = st.radio("Task:", ["Update Scores", "Adjust Strengths"])
        if task == "Update Scores":
            cols = st.columns(2)
            for i in range(1, 9):
                with cols[(i-1)%2]:
                    res = st.session_state.results[f"S{i}"]
                    st.write(f"**{res['home']} vs {res['away']}**")
                    c1, c2, c3 = st.columns(3)
                    res["h_wins"] = c1.number_input(f"Home Wins", 0, 4, res["h_wins"], key=f"h{i}")
                    res["a_wins"] = c2.number_input(f"Away Wins", 0, 4, res["a_wins"], key=f"a{i}")
                    res["final"] = c3.checkbox("Final", res["final"], key=f"f{i}")
                    if res["final"]:
                        res["winner"] = st.selectbox(f"Winner", [res["home"], res["away"]], key=f"w{i}")
                        res["games"] = res["h_wins"] + res["a_wins"]
        else:
            for t, s in st.session_state.strengths.items():
                st.session_state.strengths[t] = st.slider(t, 0, 100, s)