import streamlit as st
import json
import os

# 1. Page Config
st.set_page_config(page_title="CDU Pool 2026", layout="wide")

# 2. Secure Login Logic
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    st.title("🏒 2026 NHL Pool Login")
    # Using a form helps prevent "flickering" or accidental state loss
    with st.form("login_form"):
        pwd = st.text_input("Enter Pool Password", type="password")
        submit = st.form_submit_button("Access Dashboard")
        if submit:
            if pwd == "CDU2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password. Please check with the pool admin.")

# 3. Data Loading Logic
def load_picks():
    # We look for the file exactly as named on your GitHub
    file_path = "picks_68.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error parsing JSON file: {e}")
            return None
    return None

# --- Main Flow Control ---
if not st.session_state["authenticated"]:
    login()
else:
    # Sidebar Logout Option
    if st.sidebar.button("Log Out"):
        st.session_state["authenticated"] = False
        st.rerun()

    picks = load_picks()
    
    if picks is None:
        st.error("### ❌ Critical Error: picks_68.json not found!")
        st.markdown("""
        **Troubleshooting Steps:**
        1. Ensure your file is named exactly `picks_68.json` (all lowercase, underscore used).
        2. Ensure the file is in the **root folder** of your GitHub repository.
        3. Check if the file uploaded correctly and isn't empty.
        """)
    else:
        st.title("🏆 CDU Stanley Cup Dashboard")
        st.success(f"Successfully connected! Loaded data for **{len(picks)}** participants.")
        
        # Skeleton for Stage 2
        tab1, tab2 = st.tabs(["📊 Standings & Pulse", "🌳 Visual Bracket"])
        with tab1:
            st.info("Stage 1 complete. Ready to build the Leaderboard and API Pulse.")
        with tab2:
            st.info("Stage 1 complete. Ready to build the Butterfly Bracket visualization.")