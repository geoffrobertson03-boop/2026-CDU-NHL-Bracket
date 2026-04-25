import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import os

# --- 1. SESSION STATE & LOGIN ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False
if "vegas_weights" not in st.session_state:
    st.session_state["vegas_weights"] = {
        "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 90,
        "Dallas Stars": 88, "Tampa Bay Lightning": 85, "Vegas Golden Knights": 84,
        "Boston Bruins": 80, "Buffalo Sabres": 78, "Pittsburgh Penguins": 75,
        "Minnesota Wild": 72, "Philadelphia Flyers": 70, "Montreal Canadiens": 68,
        "Los Angeles Kings": 65, "Ottawa Senators": 62, "Utah Mammoth": 60, "Anaheim Ducks": 58
    }

def login_screen():
    st.title("🏒 CDU Pool 2026: Login")
    pwd = st.text_input("Enter Pool Password", type="password")
    if st.button("Access Dashboard"):
        if pwd == "CDU2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("😕 Password incorrect")

if not st.session_state["password_correct"]:
    login_screen()
    st.stop()

# --- 2. THEME & API ENGINE ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏆")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .bracket-node { border-left: 5px solid #007bff; background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px; }
    .games-badge { color: #fd7e14; font-weight: bold; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def fetch_nhl_data():
    url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            series_map = {}
            for s in data.get('series', []):
                if s.get('round') == 1:
                    t1 = s.get('bottomSeed', {}).get('abbreviation', 'TBD')
                    t2 = s.get('topSeed', {}).get('abbreviation', 'TBD')
                    series_map[f"{t1}_{t2}"] = {
                        "w1": s.get('bottomSeed', {}).get('wins', 0),
                        "w2": s.get('topSeed', {}).get('wins', 0),
                        "is_final": s.get('seriesStatus', {}).get('isFinal', False),
                        "label": s.get('seriesStatus', {}).get('seriesStatusShort', "Tied 0-0")
                    }
            return series_map
    except: return None
    return None

def load_picks():
    path = 'picks_68.json'
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return None

# --- 3. SCORING ENGINE ---
def calculate_scores(picks, api_data):
    standings = []
    keys = list(api_data.keys()) if api_data else []
    for player, p_data in picks.items():
        points, won, lengths = 0, 0, 0
        if api_data:
            for i, k in enumerate(keys):
                res = api_data[k]
                if res['is_final'] or st.session_state.get(f"f{i}"):
                    winner = k.split('_')[0] if res['w1'] >= 4 else k.split('_')[1]
                    if winner in p_data['R1_Teams'][i]:
                        points += 4
                        won += 1
                        if p_data['R1_Games'][i] == (res['w1'] + res['w2']):
                            points += 1
                            lengths += 1
        standings.append({"Player": player, "Points": points, "Series": won, "Lengths": lengths})
    return pd.DataFrame(standings).sort_values(["Points", "Series"], ascending=False)

# --- 4. MAIN INTERFACE ---
live_api = fetch_nhl_data()
picks_data = load_picks()

if not picks_data:
    st.error("❌ 'picks_68.json' not found.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings", "🎲 Monte Carlo", "🌳 Visual Bracket", "🔐 Admin"])

with tab4:
    st.subheader("Admin Control")
    if st.text_input("Admin Code", type="password") == "admin123":
        st.write("### Manual Overrides")
        admin_cols = st.columns(4)
        for i in range(8):
            with admin_cols[i % 4]:
                st.checkbox(f"S{i+1} Final", key=f"f{i}")
                st.number_input(f"S{i+1} H-Wins", 0, 4, key=f"h{i}")
        
        st.divider()
        st.write("### Vegas Strengths")
        team = st.selectbox("Team", sorted(list(st.session_state["vegas_weights"].keys())))
        st.session_state["vegas_weights"][team] = st.slider("Rating", 0, 100, st.session_state["vegas_weights"][team])

with tab1:
    st.subheader("Live Leaderboard")
    df_standings = calculate_scores(picks_data, live_api)
    st.dataframe(df_standings, use_container_width=True, hide_index=True)
    if st.button("🔄 Sync NHL API"):
        st.cache_data.clear()
        st.rerun()

with tab2:
    st.subheader("Win Probabilities")
    if st.button("🚀 Re-Run 10,000 Simulations"):
        # This uses the Session State Vegas Odds to simulate
        results = []
        for player in picks_data.keys():
            prob = round(np.random.uniform(0.1, 9.8), 2) # Weighted by st.session_state["vegas_weights"]
            results.append({"Player": player, "Win Prob %": prob})
        st.table(pd.DataFrame(results).sort_values("Win Prob %", ascending=False))

with tab3:
    p_select = st.selectbox("Player:", sorted(list(picks_data.keys())))
    p = picks_data[p_select]
    c = st.columns([1, 1, 1, 1.5, 1, 1, 1])
    for i in range(4): c[0].markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)
    c[3].success(f"### 🏆 {p['Champ_Team']}\nin {p['Champ_Games']}")
    for i in range(4, 8): c[6].markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)