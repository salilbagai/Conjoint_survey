import streamlit as st
import pandas as pd
import random
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. YOUR 14 PROFILES ---
# Update this list with your final 14 profile descriptions
PROFILES = [
    {"id": 1, "desc": "EVM, 8500, Speaker: Yes, Height Adj: Yes, 100Hz"},
    {"id": 2, "desc": "Zebronics, 9500, Speaker: No, Height Adj: No, 144Hz"},
    {"id": 3, "desc": "BenQ, 7500, Speaker: No, Height Adj: Yes, 75Hz"},
    {"id": 4, "desc": "Lenovo, 8000, Speaker: Yes, Height Adj: No, 100Hz"},
    # ... ADD THE REST OF YOUR 14 PROFILES HERE ...
]

# --- 2. SETUP ---
st.set_page_config(page_title="Monitor Preference Survey", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

if 'round' not in st.session_state:
    st.session_state.round = 1
    st.session_state.user_info_submitted = False
    st.session_state.choices = []
    st.session_state.current_options = random.sample(PROFILES, 3)

# --- 3. USER INFO ---
if not st.session_state.user_info_submitted:
    st.title("Welcome to the Monitor Selection Survey")
    st.write("Please enter your details to begin.")
    with st.form("user_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        if st.form_submit_button("Start Survey"):
            if name and email:
                st.session_state.user_name = name
                st.session_state.user_email = email
                st.session_state.user_info_submitted = True
                st.rerun()
            else:
                st.error("Please fill in all fields.")

# --- 4. SURVEY ROUNDS ---
elif st.session_state.round <= 10:
    st.title(f"Round {st.session_state.round} of 10")
    st.write("Rank these 3 monitors from **Best (1)** to **Worst (3)**.")
    
    opts = st.session_state.current_options
    
    cols = st.columns(3)
    for i, opt in enumerate(opts):
        cols[i].info(f"**Option {chr(65+i)}**\n\n{opt['desc']}")

    with st.form(f"round_{st.session_state.round}"):
        r1 = st.selectbox("1st Choice (Best)", ["Option A", "Option B", "Option C"], index=0)
        r2 = st.selectbox("2nd Choice", ["Option A", "Option B", "Option C"], index=1)
        r3 = st.selectbox("3rd Choice (Worst)", ["Option A", "Option B", "Option C"], index=2)
        
        if st.form_submit_button("Submit Round"):
            if len({r1, r2, r3}) < 3:
                st.error("Please pick a different option for each rank.")
            else:
                # Prepare data row
                new_row = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "User_Name": st.session_state.user_name,
                    "User_Email": st.session_state.user_email,
                    "Round": st.session_state.round,
                    "Option_A_ID": opts[0]['id'],
                    "Option_B_ID": opts[1]['id'],
                    "Option_C_ID": opts[2]['id'],
                    "Rank_1": r1, "Rank_2": r2, "Rank_3": r3
                }
                
                # Save to Google Sheets
                existing_data = conn.read(worksheet="Responses")
                updated_df = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)
                conn.update(worksheet="Responses", data=updated_df)
                
                # Move to next round
                st.session_state.round += 1
                st.session_state.current_options = random.sample(PROFILES, 3)
                st.rerun()

# --- 5. THANK YOU ---
else:
    st.title("Survey Complete!")
    st.success("Thank you for your time. Your preferences have been recorded.")
    st.write("You can now close this window.")
