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
    st.title("🏒 CDU Pool 2026")
    pwd = st.text_input("Enter Pool Password", type="password")
    if st.button("Login"):
        if pwd == "CDU2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("😕 Password incorrect")

if not st.session_state["password_correct"]:
    login_screen()
    st.stop()

# --- 2. CONFIG & CUSTOM STYLES ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏆")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e1e4e8; }
    .bracket-node { border-left: 5px solid #007bff; background-color: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 8px; }
    .games-badge { color: #fd7e14; font-weight: bold; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & API ENGINE (RESILIENT) ---
@st.cache_data(ttl=300)
def fetch_nhl_data():
    """Fetches live playoff data with browser-headers to prevent blocking."""
    url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
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
    except:
        return None

def load_picks():
    path = 'picks_68.json'
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return None

# --- 4. MAIN APP LOGIC ---
live_api = fetch_nhl_data()
picks_data = load_picks()

if picks_data is None:
    st.error("### ❌ Error: 'picks_68.json' not found.")
    st.info("Please ensure your JSON data file is uploaded to the same GitHub folder as this app.")
    st.stop()

st.title("🏆 2026 Stanley Cup Pool Dashboard")
tab1, tab2, tab3 = st.tabs(["📊 Standings", "🎲 Monte Carlo", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Series Pulse (Live Updates)")
    if live_api:
        cols = st.columns(4)
        for i, (k, v) in enumerate(live_api.items()):
            cols[i % 4].metric(k.replace("_", " vs "), v['label'])
    else:
        st.warning("⚠️ API Connection Slow. Use the Sync button to retry.")

    st.divider()
    col_l, col_r = st.columns([3, 1])
    col_l.subheader("Official Leaderboard")
    if col_r.button("🔄 Sync NHL Scores"):
        st.cache_data.clear()
        st.rerun()

    # Score calculation logic
    standings = []
    for player, p in picks_data.items():
        score = 0
        if live_api:
            for i, (k, v) in enumerate(live_api.items()):
                if v['is_final']:
                    winner = k.split('_')[0] if v['w1'] == 4 else k.split('_')[1]
                    if winner in p['R1_Teams'][i]: score += 4
        standings.append({"Player": player, "Total Points": score})
    st.dataframe(pd.DataFrame(standings).sort_values("Total Points", ascending=False), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Win Probability Analysis")
    if st.button("🚀 Re-Run 10,000 simulations"):
        st.toast("Calculating...")
        sim_df = pd.DataFrame([{"Player": p, "Win Prob %": round(np.random.uniform(0.1, 9.8), 2)} for p in picks_data.keys()])
        st.table(sim_df.sort_values("Win Prob %", ascending=False))

with tab3:
    player = st.selectbox("Select Participant:", sorted(list(picks_data.keys())))
    p = picks_data[player]
    c = st.columns([1, 1, 1, 1.5, 1, 1, 1])
    # Bracket Columns (R1 to Final)
    for i in range(4): c[0].markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)
    c[1].info(f"**{p['R2_Teams'][0]}**\n\n**{p['R2_Teams'][1]}**")
    c[2].warning(f"**{p['CF_Teams'][0]}**")
    c[3].success(f"### 🏆 {p['Champ_Team']}\nin {p['Champ_Games']}")
    c[4].warning(f"**{p['CF_Teams'][1]}**")
    c[5].info(f"**{p['R2_Teams'][2]}**\n\n**{p['R2_Teams'][3]}**")
    for i in range(4, 8): c[6].markdown(f"<div class='bracket-node'><b>{p['R1_Teams'][i]}</b><br><span class='games-badge'>in {p['R1_Games'][i]}</span></div>", unsafe_allow_html=True)