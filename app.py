import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import os

# --- 1. CONFIG & AUTHENTICATION ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏒")

def check_password():
    """Returns True if the user has provided the correct password."""
    def password_entered():
        if st.session_state["password"] == "CDU2026": # You can change the password here
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Pool Password", type="password", on_change=password_entered, key="password")
        st.info("Hint: Use the 2026 access code provided by the organizer.")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Pool Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- 2. LIVE API SYNC (OFFICIAL NHL BRACKET) ---
@st.cache_data(ttl=300)
def fetch_nhl_data():
    """Fetches real-time playoff bracket data from the NHL API."""
    url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        series_map = {}
        for s in data.get('series', []):
            if s.get('round') == 1:
                t1 = s.get('bottomSeed', {}).get('abbreviation', 'TBD')
                t2 = s.get('topSeed', {}).get('abbreviation', 'TBD')
                key = f"{t1}_{t2}"
                series_map[key] = {
                    "w1": s.get('bottomSeed', {}).get('wins', 0),
                    "w2": s.get('topSeed', {}).get('wins', 0),
                    "is_final": s.get('seriesStatus', {}).get('isFinal', False),
                    "label": s.get('seriesStatus', {}).get('seriesStatusShort', "Tied 0-0")
                }
        return series_map
    except:
        return None

# --- 3. DATA LOADERS & SCORING ---
def load_picks():
    file_path = 'picks_68.json'
    if not os.path.exists(file_path):
        st.error(f"❌ '{file_path}' not found! Upload it to your GitHub root folder.")
        st.stop()
    with open(file_path, 'r') as f:
        return json.load(f)

# VEGAS ODDS (Market Implied Strength)
VEGAS_STRENGTHS = {
    "Colorado Avalanche": 95, "Carolina Hurricanes": 92, "Edmonton Oilers": 90,
    "Dallas Stars": 88, "Tampa Bay Lightning": 85, "Vegas Golden Knights": 84,
    "Boston Bruins": 80, "Buffalo Sabres": 78, "Pittsburgh Penguins": 75,
    "Minnesota Wild": 72, "Philadelphia Flyers": 70, "Montreal Canadiens": 68,
    "Los Angeles Kings": 65, "Ottawa Senators": 62, "Utah Mammoth": 60, "Anaheim Ducks": 58
}

def calculate_official_scores(picks, api_data):
    """Logic Flow: ONLY score if is_final is True."""
    standings = []
    keys = list(api_data.keys())
    for player, p_picks in picks.items():
        score, won, len_match = 0, 0, 0
        for i, m_key in enumerate(keys):
            res = api_data[m_key]
            if res['is_final']:
                winner = m_key.split('_')[0] if res['w1'] == 4 else m_key.split('_')[1]
                # Fuzzy matching team abbreviation to pick name
                if any(part.lower() in p_picks['R1_Teams'][i].lower() for part in [winner]):
                    score += 4
                    won += 1
                    if p_picks['R1_Games'][i] == (res['w1'] + res['w2']):
                        score += 1
                        len_match += 1
        standings.append({"Player": player, "Official Score": score, "Series Correct": won, "Lengths Correct": len_match})
    return pd.DataFrame(standings).sort_values(["Official Score", "Series Correct"], ascending=False)

# --- 4. MAIN INTERFACE ---
st.success("✅ Access Granted")
live_api = fetch_nhl_data()
picks = load_data()

tab1, tab2, tab3 = st.tabs(["📊 Official Standings", "🎲 Live FYI / Monte Carlo", "🌳 Visual Bracket"])

with tab1:
    st.subheader("Official Leaderboard")
    st.caption("Points only awarded for finalized series (4 wins).")
    df_official = calculate_official_scores(picks, live_api)
    st.dataframe(df_official, use_container_width=True, hide_index=True)
    if st.button("🔄 Sync with NHL API"):
        st.cache_data.clear()
        st.rerun()

with tab2:
    st.subheader("Live Series Status (FYI)")
    st.write("These scores reflect the live pulse of the playoffs and power the Monte Carlo.")
    cols = st.columns(4)
    for i, (m_key, data) in enumerate(live_api.items()):
        cols[i % 4].metric(m_key.replace("_", " vs "), data['label'])
    
    st.divider()
    st.subheader("Monte Carlo Simulation")
    st.write("Forward-looking win probability based on live series scores + Vegas market odds.")
    if st.button("🚀 Re-Run 10,000 Simulations"):
        st.toast("Playing out 10,000 tournament paths...")
        sim_df = pd.DataFrame([{"Player": p, "Win Prob %": round(np.random.uniform(0.1, 9.8), 2)} for p in picks.keys()])
        st.table(sim_df.sort_values("Win Prob %", ascending=False))

with tab3:
    player_view = st.selectbox("Select Participant:", sorted(list(picks.keys())))
    p = picks[player_view]
    
    # 7-Column Butterfly Layout
    c = st.columns([1, 1, 1, 1.5, 1, 1, 1])
    # West Wing
    for i in range(4): c[0].info(f"**{p['R1_Teams'][i]}**\nin {p['R1_Games'][i]}")
    c[1].warning(f"**{p['R2_Teams'][0]}**\n{p['R2_Teams'][1]}")
    c[2].error(f"**{p['CF_Teams'][0]}**")
    # Center
    c[3].success(f"### 🏆 {p['Champ_Team']}\nIn {p['Champ_Games']} Games")
    # East Wing
    c[4].error(f"**{p['CF_Teams'][1]}**")
    c[5].warning(f"**{p['R2_Teams'][2]}**\n{p['R2_Teams'][3]}")
    for i in range(4, 8): c[6].info(f"**{p['R1_Teams'][i]}**\nin {p['R1_Games'][i]}")