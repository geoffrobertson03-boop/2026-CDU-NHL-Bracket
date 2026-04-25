def calculate_leaderboard(picks, live_data):
    standings = []
    if not live_data: 
        return pd.DataFrame([{"Player": p, "Points": 0, "Status": "Awaiting Data"} for p in picks.keys()])
    
    series_keys = list(live_data.keys())
    for player, p_picks in picks.items():
        points = 0
        correct_picks = 0
        
        for i, key in enumerate(series_keys):
            res = live_data[key]
            # Official Scoring (Series is over)
            if res['is_final']:
                winner_abbr = key.split('_')[0] if res['w1'] == 4 else key.split('_')[1]
                if winner_abbr.lower() in p_picks['R1_Teams'][i].lower():
                    points += 4
                    correct_picks += 1
                    if p_picks['R1_Games'][i] == (res['w1'] + res['w2']):
                        points += 1
            
            # Live "Bonus" Scoring (Just for fun while games are on)
            else:
                current_leader = None
                if res['w1'] > res['w2']: current_leader = key.split('_')[0]
                elif res['w2'] > res['w1']: current_leader = key.split('_')[1]
                
                if current_leader and current_leader.lower() in p_picks['R1_Teams'][i].lower():
                    # We'll give 0.1 points just to show they are 'leading' on the leaderboard
                    points += 0.1 

        standings.append({
            "Player": player, 
            "Score": round(points, 1), 
            "Series Final": correct_picks
        })
    
    return pd.DataFrame(standings).sort_values("Score", ascending=False)

# --- TAB 1 RE-BUILD ---
with tab1:
    st.subheader("Live Series Pulse")
    if live_data:
        cols = st.columns(4)
        for i, (key, info) in enumerate(live_data.items()):
            cols[i % 4].metric(key.replace("_", " vs "), info['label'])
    
    st.divider()
    
    col_l, col_r = st.columns([3, 1])
    col_l.subheader("Projected Leaderboard")
    if col_r.button("🔄 Sync NHL Scores"):
        st.cache_data.clear()
        st.rerun()

    df_lead = calculate_leaderboard(picks, live_data)
    
    # Custom Styling for the Table
    st.dataframe(
        df_lead, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Score": st.column_config.NumberColumn("Points", help="Includes 0.1 bonus for currently leading a series"),
            "Series Final": st.column_config.NumberColumn("Series Won ✅")
        }
    )
    st.caption("Note: You earn 4 points for a series win and 1 point for correct length. Fractional points indicate you are currently leading an active series.")