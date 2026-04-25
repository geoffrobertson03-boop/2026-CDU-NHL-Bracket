import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import os

# --- 1. INITIALIZE SESSION STATE ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

# --- 2. AUTHENTICATION FUNCTION ---
def login_screen():
    """Displays the login screen and handles password logic."""
    st.title("🔒 CDU Pool Access")
    pwd = st.text_input("Enter Pool Password", type="password")
    if st.button("Login"):
        if pwd == "CDU2026":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("😕 Password incorrect")

# Only show the app if authenticated
if not st.session_state["password_correct"]:
    login_screen()
    st.stop()

# --- 3. THE REST OF THE APP (ONLY RUNS AFTER LOGIN) ---
st.set_page_config(page_title="2026 NHL Pool Master", layout="wide", page_icon="🏒")
st.success("✅ Access Granted")

# --- 4. DATA LOADERS ---
@st.cache_data(ttl=300)
def fetch_nhl_data():
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

def load_picks():
    with open('picks_68.json', 'r') as f:
        return json.load(f)

# (Insert the calculate_standings, Tab Layout, and Butterfly Bracket code here)
# ... [Keeping the same Tab/Bracket logic from the previous final master]