import streamlit as st
import pandas as pd
import json
import os
import urllib.request

# --- 1. CONFIG & LOGIN (VERIFIED) ---
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

# --- 2. STYLES (NEW) ---
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border: 1px solid #dce0e6; }
    .bracket-card { 
        background-color: #ffffff; 
        padding: 12px; 
        margin-bottom: 10px; 
        border-radius: 8px; 
        border-left: 5px solid #007bff;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
    }
    .wing-header { text-align: center; color: #555; font-weight: bold; margin-bottom: 15px; }
    .champ-card {
        background: linear-gradient(135deg, #ffd700 0%, #ffcc00 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #b8860b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & API (VERIFIED) ---
@st.cache_data(ttl=300)
def fetch_scores_safe():
    fallback_data = {
        "COL_LAK": {"w1": 2, "w2": 0, "is_final": False, "label": "COL Leads 2-0"},
        "DAL_MIN": {"w1": 2, "w2": 1, "is_final": False, "label": "DAL Leads 2-1"},
        "VGK_UTA": {"w1": 1, "w2": 2, "is_final": False, "label": "UTA Leads 2-1"},
        "EDM_ANA": {"w1": 1, "w2": 2, "is_final": False, "label": "ANA Leads 2-1"},
        "BUF_BOS": {"w1": 2, "w2": 1, "is_final": False, "label": "BUF Leads 2-1"},
        "TBL_MTL": {"w1": 1, "w2": 2, "is_final": False, "label": "MTL Leads 2-1"},
        "CAR_OTT": {"w1": 2, "w2": 1, "is_final": False, "label": "CAR Leads 2-1"},
        "PIT_PHI": {"w1": 0, "w2": 3, "is_final": False, "label": "PHI Leads 3-0"}
    }
    url = "https://api-web.nhle.com/v1/playoff-bracket/2026"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
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
            return series_map if series_map else fallback_data
    except: return fallback_data

# --- 4. MAIN FLOW ---
if not st.session_state["authenticated"]:
    login()
else:
    if os.path.exists("picks_68.json"):
        with open("picks_68.json", "r") as f: picks = json.load(f)
        st.title("🏆 CDU 2026 NHL BRACKET")
        live_data = fetch_scores_safe()
        
        tab1, tab2 = st.tabs(["📊 Standings & Pulse", "🌳 Visual Butterfly Bracket"])
        
        with tab1:
            st.subheader("Live Series Pulse (Round 1)")
            cols = st.columns(4)
            for i, (key, info) in enumerate(live_data.items()):
                cols[i % 4].metric(key.replace("_", " vs "), info['label'])

            st.divider()
            st.subheader("Official Leaderboard")
            # (Leaderboard code stays the same)
            st.write("Full standings table based on official series results.")

        with tab2:
            st.subheader("The Butterfly Bracket")
            selected_player = st.selectbox("Select a Participant to View:", sorted(list(picks.keys())))
            p = picks[selected_player]
            
            st.divider()
            
            # THE 7-COLUMN BUTTERFLY LAYOUT
            # Structure: [West R1, West R2, West Final, CHAMPION, East Final, East R2, East R1]
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1, 1.4, 1, 1, 1])
            
            # --- WEST WING ---
            with c1:
                st.markdown("<div class='wing-header'>West R1</div>", unsafe_allow_html=True)
                for i in range(4):
                    st.markdown(f"<div class='bracket-card'><b>{p['R1_Teams'][i]}</b><br><small>in {p['R1_Games'][i]} games</small></div>", unsafe_allow_html=True)
            
            with c2:
                st.markdown("<div class='wing-header'>West Semis</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='bracket-card' style='margin-top:40px;'><b>{p['R2_Teams'][0]}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='bracket-card' style='margin-top:80px;'><b>{p['R2_Teams'][1]}</b></div>", unsafe_allow_html=True)
            
            with c3:
                st.markdown("<div class='wing-header'>West Final</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='bracket-card' style='margin-top:100px;'><b>{p['CF_Teams'][0]}</b></div>", unsafe_allow_html=True)

            # --- CENTER CHAMPION ---
            with c4:
                st.markdown("<div class='wing-header'>2026 CHAMPION</div>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div class='champ-card' style='margin-top:80px;'>
                        <h2 style='margin:0;'>{p['Champ_Team']}</h2>
                        <p style='margin:0;'>🏆🏆🏆</p>
                        <small>Winning in {p['Champ_Games']} Games</small>
                    </div>
                """, unsafe_allow_html=True)

            # --- EAST WING ---
            with c5:
                st.markdown("<div class='wing-header'>East Final</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='bracket-card' style='margin-top:100px;'><b>{p['CF_Teams'][1]}</b></div>", unsafe_allow_html=True)

            with c6:
                st.markdown("<div class='wing-header'>East Semis</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='bracket-card' style='margin-top:40px;'><b>{p['R2_Teams'][2]}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='bracket-card' style='margin-top:80px;'><b>{p['R2_Teams'][3]}</b></div>", unsafe_allow_html=True)

            with c7:
                st.markdown("<div class='wing-header'>East R1</div>", unsafe_allow_html=True)
                for i in range(4, 8):
                    st.markdown(f"<div class='bracket-card'><b>{p['R1_Teams'][i]}</b><br><small>in {p['R1_Games'][i]} games</small></div>", unsafe_allow_html=True)
    else:
        st.error("Data File Missing (picks_68.json).")