import streamlit as st
import pandas as pd
import json
import os
import urllib.request

# --- 1. CONFIG & LOGIN ---
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

# --- 2. THE BULLETPROOF API ENGINE ---
@st.cache_data(ttl=300)
def fetch_scores_safe():
    """
    Tries multiple sources to get playoff scores. 
    If all APIs fail, it uses the 'Safe Fallback' data below.
    """
    # FALLBACK DATA: Update these numbers if the API stays blocked
    fallback_data = {
        "COL_LAK": {"w1": 3, "w2": 0, "is_final": False, "label": "COL Leads 3-0"},
        "DAL_MIN": {"w1": 2, "w2": 1, "is_final": False, "label": "DAL Leads 2-1"},
        "VGK_UTA": {"w1": 1, "w2": 2, "is_final": False, "label": "UTA Leads 2-1"},
        "EDM_ANA": {"w1": 1, "w2": 2, "is_final": False, "label": "ANA Leads 2-1"},
        "BUF_BOS": {"w1": 2, "w2": 1, "is_final": False, "label": "BUF Leads 2-1"},
        "TBL_MTL": {"w1": 1, "w2": 2, "is_final": False, "label": "MTL Leads 2-1"},
        "CAR_OTT": {"w1": 3, "w2": 0, "is_final": False, "label": "CAR Leads 3-0"},
        "PIT_PHI": {"w1": 0, "w2": 3, "is_final": False, "label": "PHI Leads 3-0"}
    }
    
    url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            series_map = {}
            for s in data.get('series', []):
                if s.get('round') == 1:
                    t1 = s.get('bottomSeed', {}).get('abbreviation', 'T1')
                    t2 = s.get('topSeed', {}).get('abbreviation', 'T2')
                    series_map[f"{t1}_{t2}"] = {
                        "w1": s.get('bottomSeed', {}).get('wins', 0),
                        "w2": s.get('topSeed', {}).get('wins', 0),
                        "is_final": s.get('seriesStatus', {}).get('isFinal', False),
                        "label": s.get('seriesStatus', {}).get('seriesStatusShort', "Tied 0-0")
                    }
            return series_map
    except:
        # If API fails, return the fallback data so the screen isn't blank
        return fallback_data

def calculate_leaderboard(picks, live_data):
    standings = []
    series_keys = list(live_data.keys())
    for player, p_picks in picks.items():
        score, won_s, won_l = 0, 0, 0
        for i, key in enumerate(series_keys):
            res = live_data[key]
            if res['is_final']:
                winner_abbr = key.split('_')[0] if res['w1'] == 4 else key.split('_')[1]
                if winner_abbr in p_picks['R1_Teams'][i]:
                    score += 4
                    won_s += 1
                    if p_picks['R1_Games'][i] == (res['w1'] + res['w2']):
                        score += 1
                        won_l += 1
        standings.append({"Player": player, "Total Points": score, "Series": won_s, "Length": won_l})
    return pd.DataFrame(standings).sort_values(["Total Points", "Series"], ascending=False)

# --- 3. MAIN FLOW ---
if not st.session_state["authenticated"]:
    login()
else:
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: picks = json.load(f)
        
        st.title("🏆 CDU 2026 NHL BRACKET")
        live_data = fetch_scores_safe()
        
        tab1, tab2 = st.tabs(["📊 Standings & Pulse", "🌳 Visual Bracket"])
        
        with tab1:
            st.subheader("Live Series Pulse (FYI)")
            cols = st.columns(4)
            for i, (key, info) in enumerate(live_data.items()):
                cols[i % 4].metric(key.replace("_", " vs "), info['label'])

            st.divider()
            st.subheader("Official Leaderboard")
            df_lead = calculate_leaderboard(picks, live_data)
            st.dataframe(df_lead, use_container_width=True, hide_index=True)
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
            
        with tab2:
            st.info("Stage 3: Butterfly Bracket pending.")
    else:
        st.error("Data File Missing (picks_68.json).")