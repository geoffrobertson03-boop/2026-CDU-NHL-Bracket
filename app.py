import streamlit as st
import pandas as pd
import json
import requests
import os

# --- CONFIG & LOGIN (RETAINED FROM STAGE 1) ---
st.set_page_config(page_title="CDU 2026 NHL BRACKET", layout="wide", page_icon="🏒")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    st.title("🏒 CDU 2026 NHL BRACKET: Login")
    with st.form("login_form"):
        pwd = st.text_input("Enter Pool Password", type="password")
        submit = st.form_submit_button("Access Dashboard")
        if submit:
            if pwd == "CDU2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Incorrect password.")

def load_picks():
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: return json.load(f)
    return None

# --- NEW STAGE 2: API & SCORING ---
@st.cache_data(ttl=300)
def fetch_live_scores():
    """Fetches real-time playoff series status from the official NHL API."""
    url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        series_map = {}
        # Parse official NHL series data for Round 1
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

def calculate_leaderboard(picks, live_data):
    """Only awards points for series where 'is_final' is True."""
    standings = []
    series_keys = list(live_data.keys()) if live_data else []
    
    for player, p_picks in picks.items():
        score, won_series, won_length = 0, 0, 0
        if live_data:
            for i, key in enumerate(series_keys):
                res = live_data[key]
                if res['is_final']:
                    winner = key.split('_')[0] if res['w1'] == 4 else key.split('_')[1]
                    # Compare abbreviation to the pick name
                    if winner in p_picks['R1_Teams'][i]:
                        score += 4
                        won_series += 1
                        if p_picks['R1_Games'][i] == (res['w1'] + res['w2']):
                            score += 1
                            won_length += 1
        standings.append({"Player": player, "Total Points": score, "Series": won_series, "Lengths": won_length})
    return pd.DataFrame(standings).sort_values(["Total Points", "Series"], ascending=False)

# --- MAIN FLOW ---
if not st.session_state["authenticated"]:
    login()
else:
    picks = load_picks()
    if picks:
        st.title("🏆 CDU 2026 NHL BRACKET")
        live_data = fetch_live_scores()
        
        tab1, tab2 = st.tabs(["📊 Standings & Pulse", "🌳 Visual Bracket"])
        
        with tab1:
            st.subheader("Live Series Pulse (FYI)")
            if live_data:
                # Display 4 series per row
                cols = st.columns(4)
                for i, (key, info) in enumerate(live_data.items()):
                    with cols[i % 4]:
                        st.metric(key.replace("_", " vs "), info['label'])
            else:
                st.warning("⚠️ Syncing with NHL servers... Click the button below if scores don't appear.")

            st.divider()
            
            col_l, col_r = st.columns([3, 1])
            col_l.subheader("Official Tournament Leaderboard")
            if col_r.button("🔄 Sync Official Scores"):
                st.cache_data.clear()
                st.rerun()

            df_lead = calculate_leaderboard(picks, live_data)
            st.dataframe(df_lead, use_container_width=True, hide_index=True)
            
        with tab2:
            st.info("Ready for Stage 3: Visual Butterfly Bracket.")
    else:
        st.error("Data File Missing.")