import streamlit as st
import base64
import os
import re
import requests # NEW: Needed to send messages over the internet

# Set page configuration
st.set_page_config(page_title="Book your Bikes - Pondicherry", page_icon="🚲", layout="centered")

# --- TELEGRAM CONFIGURATION ---
# Replace these with the actual values you got from Telegram!
TELEGRAM_BOT_TOKEN = "8985808876:AAEBCR8oCG1on8UANmABB2sUKbNG_St9wAo"
TELEGRAM_CHAT_ID = "6464722140"

# 1. Bulletproof Image Path Resolution
current_directory = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_directory, "image_0.png")

# 2. Helper function to read the images safely for HTML
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return "" 

# 3. Get the base64 string
logo_base64 = get_image_base64(logo_path)

# Apply Theme and CSS Styling
st.markdown(f"""
    <style>
    /* Darker "Painted" Yellow to White Gradient Background */
    .stApp {{
        background: linear-gradient(135deg, #F57F17 0%, #FBC02D 30%, #FFFDE7 80%, #FFFFFF 100%);
    }}
    
    /* DETAILS CONTAINER WITH BLACK BORDER */
    .main .block-container {{
        background-color: #FFFFFF;
        border: 3px solid #000000;
        border-radius: 12px;
        padding: 40px;
        margin-top: 50px;
        margin-bottom: 50px;
        box-shadow: 6px 6px 0px rgba(0, 0, 0, 0.8);
    }}
    
    /* Finish Button */
    div[data-testid="stFormSubmitButton"] button {{
        background-color: #0056b3 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        width: 100%;
        border: 2px solid #000000 !important;
        letter-spacing: 2px;
        border-radius: 6px;
        padding: 12px;
        transition: all 0.3s ease;
    }}
    div[data-testid="stFormSubmitButton"] button:hover {{
        background-color: #003d82 !important;
        transform: translateY(-2px);
    }}
    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# 4. Render the Main Logo and Title
if logo_base64:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 3px solid #000; box-shadow: 4px 4px 0px rgba(0,0,0,0.8);" alt="Logo">
            <h1 style="color: #000000; font-family: 'Pacifico', cursive; font-size: 3.5rem; margin: 0;">Book your Bikes</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.error(f"Could not find the logo image at: {logo_path}")

# --- Main Booking Form ---
with st.container():
    st.markdown("### Your Perfect Pondy Ride Awaits! 🌴")
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
        with col2:
            last_name = st.text_input("Last Name")
            
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        
        col3, col4 = st.columns(2)
        with col3:
            from_date = st.date_input("From Date")
            from_time = st.time_input("From Time")
        with col4:
            to_date = st.date_input("To Date")
            to_time = st.time_input("To Time")
            
        col5, col6 = st.columns(2)
        with col5:
            bike_type = st.radio("Bike Type", options=["Gear", "Non-Gear", "Both"], horizontal=True)
        with col6:
            num_bikes = st.number_input("Number of Bikes", min_value=1, value=1, step=1)
        
        submitted = st.form_submit_button("< FINISH >")
        
        # --- VALIDATION & TELEGRAM LOGIC ---
        if submitted:
            if not first_name or not phone or not email:
                st.warning("Please fill in your First Name, Email, and Phone number.")
            elif not phone.isdigit():
                st.error("Invalid Phone Number: Please enter numbers only (no letters, spaces, or symbols).")
            elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                st.error("Invalid Email: Please enter a correct email format (e.g., name@domain.com).")
            else:
                # 1. Format the message clearly for your phone
                telegram_message = (
                    f"🚲 NEW BIKE BOOKING! 🚲\n\n"
                    f"Name: {first_name} {last_name}\n"
                    f"Phone: {phone}\n"
                    f"Email: {email}\n\n"
                    f"REQUIREMENTS:\n"
                    f"Type: {bike_type}\n"
                    f"Count: {num_bikes} Bike(s)\n"
                    f"From: {from_date} at {from_time}\n"
                    f"To: {to_date} at {to_time}"
                )
                
                # 2. Send the request to Telegram
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": telegram_message
                }
                
                try:
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.success("Team will be contacting you via phone or Whatsapp. Happy Vacation :)")
                        st.balloons() # A fun little animation to celebrate a successful booking!
                    else:
                        st.error("Booking received, but there was an error notifying the team.")
                except Exception as e:
                    st.error("Network error. Could not send the booking notification.")
