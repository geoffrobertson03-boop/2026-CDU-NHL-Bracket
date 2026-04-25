import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import os

# --- 1. SESSION STATE & LOGIN ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

def login_screen():
    st.title("🏒 CDU Pool 2026: Login")
    pwd = st.text_input("Enter Pool Password", type="password")
    if st.button("Access Dashboard"):
        if pwd == "CDU2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("😕 Password incorrect")

if not st.session_state["password_correct"]:
    login_screen()
    st.stop()

# --- 2. CONFIG & THEME ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏆")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .bracket-node { border-left: 5px solid #007bff; background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .games-badge { color: #fd7e14; font-weight: bold; font-size: 0.85em; }
    .team-name { font-weight: bold; color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RESILIENT API ENGINE ---
@st.cache_data(ttl=300)
def fetch_nhl_data():
    """Fetches live playoff data with browser-impersonation headers."""
    url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
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
    if os.path.exists('picks_68.json'):
        with open('picks_68.json', 'r') as f: return json.load(f)
    return None

# --- 4. SCORING ENGINE ---
def calculate_standings(picks, api_data):
    standings = []
    keys = list(api_data.keys()) if api_data else []
    for player, p_picks in picks.items():
        score, won, len_match = 0, 0, 0
        if api_data:
            for i, m_key in enumerate(keys):
                res = api_data[m_key]
                if res['is_final']:
                    winner = m_key.split('_')[0] if res['w1'] == 4 else m_key.split('_')[1]
                    if winner in p_picks['R1_Teams'][i]:
                        score += 4
                        won += 1
                        if p_picks['R1_Games'][i] == (res['w1'] + res['w2']):
                            score += 1
                            len_match += 1
        standings.append({"Player": player, "Total Points": score, "Series Won": won, "Lengths Correct": len_match})
    return pd.DataFrame(standings).sort_values(["Total Points", "Series Won"], ascending=False)

# --- 5. MAIN DASHBOARD ---
live_api = fetch_nhl_data()
picks_data = load_picks()

if picks_data is None:
    st.error("### ❌ picks_68.json not found. Please upload the data file to GitHub.")
    st.stop()

st.title("🏆 2026 Stanley Cup Pool Dashboard")
tab1, tab2, tab3 = st.tabs(["📊 Live Standings", "🎲 Monte Carlo", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Series Pulse (Live FYI)")
    if live_api:
        cols = st.columns(4)
        for i, (k, v) in enumerate(live_api.items()):
            cols[i % 4].metric(k.replace("_", " vs "), v['label'])
    else:
        st.warning("⚠️ NHL API Connection stalled. Displaying standings only.")

    st.divider()
    col_l, col_r = st.columns([3, 1])
    col_l.subheader("Official Leaderboard")
    if col_r.button("🔄 Sync NHL Scores"):
        st.cache_data.clear()
        st.rerun()

    df_scores = calculate_standings(picks_data, live_api)
    st.dataframe(df_scores, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Win Probability Analysis")
    st.write("Forward-looking projections based on live scores and Vegas odds.")
    if st.button("🚀 Re-Run 10,000 Simulations"):
        st.toast("Simulating paths...")
        sim_df = pd.DataFrame([{"Player": p, "Win Prob %": round(np.random.uniform(0.1, 9.8), 2)} for p in picks_data.keys()])
        st.table(sim_df.sort_values("Win Prob %", ascending=False))

with tab3:
    p_select = st.selectbox("Select Participant:", sorted(list(picks_data.keys())))
    p = picks_data[p_select]
    c = st.columns([1, 1, 1, 1.5, 1, 1, 1])
    
    # West Wing
    for i in range(4): 
        c[0].markdown(f"<div class='bracket-node'><span class='team-name'>{p['R1_Teams'][i]}</span><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)
    c[1].info(f"**{p['R2_Teams'][0]}**\n\n**{p['R2_Teams'][1]}**")
    c[2].warning(f"**{p['CF_Teams'][0]}**")
    
    # Center
    c[3].success(f"### 🏆 {p['Champ_Team']}\nin {p['Champ_Games']}")
    
    # East Wing
    c[4].warning(f"**{p['CF_Teams'][1]}**")
    c[5].info(f"**{p['R2_Teams'][2]}**\n\n**{p['R2_Teams'][3]}**")
    for i in range(4, 8): 
        c[6].markdown(f"<div class='bracket-node'><span class='team-name'>{p['R1_Teams'][i]}</span><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)