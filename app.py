import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIG & LOGIN (RETAINED) ---
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

# --- 2. DATA LOADERS ---
def load_picks():
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: return json.load(f)
    return None

@st.cache_data(ttl=300)
def fetch_live_scores():
    try:
        import requests
        url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
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
    except Exception as e:
        # Instead of crashing, we return None so the UI can handle it gracefully
        return None

# --- 3. MAIN FLOW ---
if not st.session_state["authenticated"]:
    login()
else:
    picks = load_picks()
    if picks:
        st.title("🏆 CDU 2026 NHL BRACKET")
        
        # Load API data
        live_data = fetch_live_scores()
        
        tab1, tab2 = st.tabs(["📊 Standings & Pulse", "🌳 Visual Bracket"])
        
        with tab1:
            st.subheader("Live Series Pulse (FYI)")
            if live_data:
                cols = st.columns(4)
                for i, (key, info) in enumerate(live_data.items()):
                    cols[i % 4].metric(key.replace("_", " vs "), info['label'])
            else:
                st.warning("⚠️ API Offline: Could not fetch live scores. Check requirements.txt or internet connection.")

            st.divider()
            st.subheader("Official Leaderboard")
            # Leaderboard table will go here next...
            st.info("Leaderboard will populate once 'requests' is successfully installed.")
            
        with tab2:
            st.info("Stage 3: Butterfly Bracket pending.")
    else:
        st.error("Data File (picks_68.json) Missing.")