import streamlit as st
import pandas as pd
import json
import os
import urllib.request

# --- 1. THE REPAIRED SCORING ENGINE ---
def calculate_leaderboard(picks, live_data):
    standings = []
    # If API fails or is empty, we still want to show the players
    if not live_data:
        return pd.DataFrame([{"Player": p, "Points": 0.0, "Status": "Syncing..."} for p in picks.keys()])
    
    series_keys = list(live_data.keys())
    for player, p_picks in picks.items():
        points = 0.0
        series_won = 0
        
        # Check Round 1 Picks
        for i, key in enumerate(series_keys):
            if i >= len(p_picks.get('R1_Teams', [])): break
            
            res = live_data[key]
            # Official Points
            if res['is_final']:
                winner_abbr = key.split('_')[0] if res['w1'] == 4 else key.split('_')[1]
                if winner_abbr.lower() in p_picks['R1_Teams'][i].lower():
                    points += 4
                    series_won += 1
                    if p_picks['R1_Games'][i] == (res['w1'] + res['w2']):
                        points += 1
            # Live Projected Points (0.1 for leading)
            else:
                if res['w1'] > res['w2'] and key.split('_')[0].lower() in p_picks['R1_Teams'][i].lower():
                    points += 0.1
                elif res['w2'] > res['w1'] and key.split('_')[1].lower() in p_picks['R1_Teams'][i].lower():
                    points += 0.1

        standings.append({
            "Player": player, 
            "Points": round(points, 1), 
            "Official Wins": series_won
        })
    
    return pd.DataFrame(standings).sort_values("Points", ascending=False)

# --- 2. TAB 2: BUTTERFLY WITH SAFETY CHECKS ---
def draw_butterfly(p):
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1, 1, 1.4, 1, 1, 1])
    
    # Function to safely get game counts
    def get_g(list_name, idx):
        try: return p.get(list_name, [])[idx]
        except: return "?"

    with c1:
        st.markdown("<div class='wing-header'>West R1</div>", unsafe_allow_html=True)
        for i in range(4):
            st.markdown(f"<div class='bracket-card'><b>{p['R1_Teams'][i]}</b><br><small>in {p['R1_Games'][i]} games</small></div>", unsafe_allow_html=True)
            
    with c2:
        st.markdown("<div class='wing-header'>West R2</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bracket-card' style='margin-top:45px;'><b>{p['R2_Teams'][0]}</b><br><small>in {get_g('R2_Games', 0)} games</small></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bracket-card' style='margin-top:85px;'><b>{p['R2_Teams'][1]}</b><br><small>in {get_g('R2_Games', 1)} games</small></div>", unsafe_allow_html=True)

    # ... (Repeat safety check for c3, c5, c6 using get_g)