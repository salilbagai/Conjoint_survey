import streamlit as st
import pandas as pd
import random
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. THE 14 PROFILES (Generated from your attributes) ---
PROFILES = [
    {"id": 1, "desc": "Brand: EVM | Price: 8500 | Speaker: Yes | Height Adj: Yes | Refresh: 100Hz"},
    {"id": 2, "desc": "Brand: Zebronics | Price: 9500 | Speaker: No | Height Adj: No | Refresh: 144Hz"},
    {"id": 3, "desc": "Brand: BenQ | Price: 7500 | Speaker: No | Height Adj: Yes | Refresh: 75Hz"},
    {"id": 4, "desc": "Brand: Lenovo | Price: 8000 | Speaker: Yes | Height Adj: No | Refresh: 100Hz"},
    {"id": 5, "desc": "Brand: EVM | Price: 9500 | Speaker: No | Height Adj: Yes | Refresh: 144Hz"},
    {"id": 6, "desc": "Brand: Zebronics | Price: 7500 | Speaker: Yes | Height Adj: No | Refresh: 75Hz"},
    {"id": 7, "desc": "Brand: BenQ | Price: 8500 | Speaker: Yes | Height Adj: No | Refresh: 100Hz"},
    {"id": 8, "desc": "Brand: Lenovo | Price: 9500 | Speaker: No | Height Adj: Yes | Refresh: 144Hz"},
    {"id": 9, "desc": "Brand: EVM | Price: 7500 | Speaker: No | Height Adj: No | Refresh: 75Hz"},
    {"id": 10, "desc": "Brand: Zebronics | Price: 8500 | Speaker: Yes | Height Adj: Yes | Refresh: 100Hz"},
    {"id": 11, "desc": "Brand: BenQ | Price: 9500 | Speaker: Yes | Height Adj: No | Refresh: 144Hz"},
    {"id": 12, "desc": "Brand: Lenovo | Price: 7500 | Speaker: No | Height Adj: Yes | Refresh: 75Hz"},
    {"id": 13, "desc": "Brand: EVM | Price: 8000 | Speaker: No | Height Adj: No | Refresh: 100Hz"},
    {"id": 14, "desc": "Brand: Zebronics | Price: 8000 | Speaker: Yes | Height Adj: Yes | Refresh: 144Hz"}
]

# --- 2. CONFIG & CONNECTION ---
st.set_page_config(page_title="Monitor Choice Survey", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# Initialize Session State
if 'round' not in st.session_state:
    st.session_state.round = 1
    st.session_state.user_submitted = False
    st.session_state.current_options = random.sample(PROFILES, 3)

# --- 3. WELCOME SCREEN ---
if not st.session_state.user_submitted:
    st.title("Monitor Preference Survey")
    st.write("Welcome! Please help us understand your preferences.")
    with st.form("user_info"):
        name = st.text_input("Name")
        email = st.text_input("Email/WhatsApp (Optional)")
        if st.form_submit_button("Start Survey"):
            if name:
                st.session_state.user_name = name
                st.session_state.user_email = email
                st.session_state.user_submitted = True
                st.rerun()
            else:
                st.error("Please enter your name.")

# --- 4. THE SURVEY ROUNDS ---
elif st.session_state.round <= 10:
    st.title(f"Round {st.session_state.round} of 10")
    st.subheader("Please rank these 3 monitors:")
    
    opts = st.session_state.current_options
    cols = st.columns(3)
    
    # Display Options
    for i, opt in enumerate(opts):
        with cols[i]:
            st.info(f"### Option {chr(65+i)}\n{opt['desc']}")

    # Selection Form
    with st.form(f"ranking_round_{st.session_state.round}"):
        r1 = st.selectbox("1st Choice (Most Preferred)", ["Option A", "Option B", "Option C"], index=0)
        r2 = st.selectbox("2nd Choice", ["Option A", "Option B", "Option C"], index=1)
        r3 = st.selectbox("3rd Choice (Least Preferred)", ["Option A", "Option B", "Option C"], index=2)
        
        if st.form_submit_button("Submit & Next"):
            if len({r1, r2, r3}) < 3:
                st.error("Please select a different option for each rank.")
            else:
                # Map selections to Profile IDs
                mapping = {"Option A": opts[0]['id'], "Option B": opts[1]['id'], "Option C": opts[2]['id']}
                
                # Prepare data row
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "User_Name": st.session_state.user_name,
                    "User_Email": st.session_state.user_email,
                    "Round": st.session_state.round,
                    "Option_A_ID": opts[0]['id'],
                    "Option_B_ID": opts[1]['id'],
                    "Option_C_ID": opts[2]['id'],
                    "Rank_1": mapping[r1],
                    "Rank_2": mapping[r2],
                    "Rank_3": mapping[r3]
                }])
                
                # Save to Google Sheets
                try:
                    existing_data = conn.read(worksheet="Responses")
                    updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                    conn.update(worksheet="Responses", data=updated_df)
                except:
                    # If sheet is empty, write with headers
                    conn.update(worksheet="Responses", data=new_row)
                
                # Move to next round
                st.session_state.round += 1
                st.session_state.current_options = random.sample(PROFILES, 3)
                st.rerun()

# --- 5. THANK YOU ---
else:
    st.title("Survey Complete!")
    st.success("Thank you! Your preferences have been recorded.")
    st.balloons()
