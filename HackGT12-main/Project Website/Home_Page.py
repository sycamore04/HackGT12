import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json
import os

st.set_page_config(page_title="GO CLUBBING!", layout="wide")

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

# Initialize session state for data persistence
if 'saved_clubs' not in st.session_state:
    st.session_state.saved_clubs = []
if 'deleted_clubs' not in st.session_state:
    st.session_state.deleted_clubs = []
if 'calendar_events' not in st.session_state:
    st.session_state.calendar_events = []

# File to store user data (in production, use a proper database)
USER_DATA_FILE = "users.json"

def load_user_database():
    """Load user database from file"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            # Default users if file doesn't exist
            return {
                "admin": {"password": "password123", "email": "admin@example.com", "created": "2024-01-01"},
                "user1": {"password": "mypassword", "email": "user1@example.com", "created": "2024-01-01"},
                "demo": {"password": "demo123", "email": "demo@example.com", "created": "2024-01-01"}
            }
    except:
        # Return default if there's any error
        return {
            "admin": {"password": "password123", "email": "admin@example.com", "created": "2024-01-01"},
            "user1": {"password": "mypassword", "email": "user1@example.com", "created": "2024-01-01"},
            "demo": {"password": "demo123", "email": "demo@example.com", "created": "2024-01-01"}
        }

def save_user_database(user_db):
    """Save user database to file"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(user_db, f, indent=2)
        return True
    except:
        return False

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter"
    return True, "Password is valid"

def validate_email(email):
    """Basic email validation"""
    if '@' not in email or '.' not in email:
        return False
    if email.count('@') != 1:
        return False
    if len(email) < 5:
        return False
    return True

# Load user database
USER_DATABASE = load_user_database()

# Sidebar Authentication
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3>Account</h3>
        </div>
        """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        # Toggle between Sign In and Sign Up
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign In", use_container_width=True, 
                type="primary" if not st.session_state.show_signup else "secondary"):
                st.session_state.show_signup = False
                st.rerun()  # Added this line
        with col2:
            if st.button("Sign Up", use_container_width=True,
                type="primary" if st.session_state.show_signup else "secondary"):
                st.session_state.show_signup = True
                st.rerun()  # Added this line
        
        st.markdown("---")
        
        if not st.session_state.show_signup:
            # Sign in form
            with st.form("signin_form"):
                st.write("**Sign In to Your Account**")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                signin_button = st.form_submit_button("Sign In")
                
                if signin_button:
                    if username in USER_DATABASE and USER_DATABASE[username]["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            
            st.markdown("---")
            st.info("**Demo Credentials:**\n\nUsername: demo\nPassword: demo123")
            
        else:
            # Sign up form
            with st.form("signup_form"):
                st.write("**Create New Account**")
                new_username = st.text_input("Choose Username*")
                new_email = st.text_input("Email Address*")
                new_password = st.text_input("Choose Password*", type="password")
                confirm_password = st.text_input("Confirm Password*", type="password")
                signup_button = st.form_submit_button("Create Account")
                
                if signup_button:
                    # Validation
                    errors = []
                    
                    # Check if username is provided
                    if not new_username:
                        errors.append("Username is required")
                    elif len(new_username) < 3:
                        errors.append("Username must be at least 3 characters")
                    elif new_username in USER_DATABASE:
                        errors.append("Username already exists")
                    
                    # Check email
                    if not new_email:
                        errors.append("Email is required")
                    elif not validate_email(new_email):
                        errors.append("Please enter a valid email address")
                    else:
                        # Check if email already exists
                        existing_emails = [user_data["email"] for user_data in USER_DATABASE.values()]
                        if new_email in existing_emails:
                            errors.append("Email already registered")
                    
                    # Check password
                    if not new_password:
                        errors.append("Password is required")
                    else:
                        is_valid, message = validate_password(new_password)
                        if not is_valid:
                            errors.append(message)
                    
                    # Check password confirmation
                    if new_password != confirm_password:
                        errors.append("Passwords do not match")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Create new user
                        USER_DATABASE[new_username] = {
                            "password": new_password,
                            "email": new_email,
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Save to file
                        if save_user_database(USER_DATABASE):
                            st.success(f"Account created successfully for {new_username}!")
                            st.info("You can now sign in with your new account.")
                            st.session_state.show_signup = False
                            st.rerun()
                        else:
                            st.error("Error saving account. Please try again.")
            
            st.markdown("---")
            st.markdown("**Password Requirements:**")
            st.markdown("• At least 6 characters")
            st.markdown("• Contains at least one letter")
            st.markdown("• Contains at least one number")
        
    else:
        # User is authenticated
        st.success(f"Signed in as: **{st.session_state.username}**")
        
        # Show user info
        if st.session_state.username in USER_DATABASE:
            user_info = USER_DATABASE[st.session_state.username]
            with st.expander("Account Info"):
                st.write(f"**Email:** {user_info['email']}")
                st.write(f"**Member since:** {user_info.get('created', 'Unknown')}")
        
        if st.button("Sign Out", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.success("Signed out successfully!")
            st.rerun()

st.markdown("""
<style>
body {
    margin: 0;
    padding: 0;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    background-color: #000814;
    padding: 10px 20px;
    border-radius: 0;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 10px;
    color: white;
    font-weight: bold;
    font-size: 16px;
    padding: 0 20px;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(255, 255, 255, 0.2);
    color: #FF00FF;
    text-shadow: 0 0 10px #FF00FF;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

/* Hero section */
.hero {
    width: 100%;
    height: 100vh;
    background: linear-gradient(135deg, #000814, #001D3D, #003566, #0077B6);
    background-size: 400% 400%;
    animation: gradientMove 25s ease infinite;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    flex-direction: column;
    position: relative;
    overflow: hidden;
}
@keyframes gradientMove {
    0% {background-position: 0% 0%;}
    50% {background-position: 100% 100%;}
    100% {background-position: 0% 0%;}
}

.floating-shapes {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.shape {
    position: absolute;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    animation: float 6s ease-in-out infinite;
}

.shape-1 {
    width: 80px;
    height: 80px;
    top: 20%;
    left: 10%;
    animation-delay: 0s;
    background: rgba(0, 255, 255, 0.3);
    box-shadow: 0 0 30px #00FFFF;
}

.shape-2 {
    width: 120px;
    height: 120px;
    top: 60%;
    right: 15%;
    animation-delay: 2s;
    background: rgba(255, 0, 255, 0.3);
    box-shadow: 0 0 40px #FF00FF;
}

.shape-3 {
    width: 100px;
    height: 100px;
    bottom: 20%;
    left: 20%;
    animation-delay: 4s;
    background: rgba(0, 255, 127, 0.3);
    box-shadow: 0 0 35px #00FF7F;
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
}

.hero-title {
    font-size: 120px !important;
    background: linear-gradient(45deg, #00FFFF, #FF00FF, #00FF7F);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none !important;
    margin-bottom: 20px !important;
    animation: titleGlow 3s ease-in-out infinite;
    filter: drop-shadow(0 0 30px #00FFFF);
}

@keyframes titleGlow {
    0%, 100% { filter: drop-shadow(0 0 30px #00FFFF); }
    33% { filter: drop-shadow(0 0 30px #FF00FF); }
    66% { filter: drop-shadow(0 0 30px #00FF7F); }
}

.hero-subtitle {
    font-size: 24px;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 40px;
    animation: fadeInUp 1s ease-out;
    text-shadow: 0 0 15px #00FFFF;
}

.hero-stats {
    display: flex;
    gap: 40px;
    justify-content: center;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: white;
    animation: bounceIn 1s ease-out;
}

.stat-number {
    font-size: 48px;
    margin-bottom: 10px;
    filter: drop-shadow(0 0 15px #00FFFF);
}

.stat-label {
    font-size: 18px;
    font-weight: bold;
    color: #00FFFF;
    text-shadow: 0 0 10px #00FFFF;
}

.magic-upload-section {
    background: linear-gradient(135deg, #000814 0%, #001D3D 50%, #003566 100%);
    padding: 60px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.magic-upload-section::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(0, 255, 255, 0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.upload-header {
    position: relative;
    z-index: 2;
}

.upload-title {
    font-size: 48px;
    color: white !important;
    margin-bottom: 20px;
    text-shadow: 0 0 20px #FF00FF;
}

.upload-description {
    font-size: 20px;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 0;
    text-shadow: 0 0 10px #00FFFF;
}

.files-detected {
    text-align: center;
    margin: 40px 0;
}

.files-count {
    background: linear-gradient(135deg, #001D3D, #003566);
    color: white;
    padding: 20px;
    border-radius: 20px;
    display: inline-block;
    box-shadow: 0 0 30px #00FFFF, 0 10px 30px rgba(0,0,0,0.2);
    animation: pulse 2s infinite;
    border: 2px solid #00FFFF;
}

@keyframes pulse {
    0%, 100% { 
        transform: scale(1);
        box-shadow: 0 0 30px #00FFFF, 0 10px 30px rgba(0,0,0,0.2);
    }
    50% { 
        transform: scale(1.05);
        box-shadow: 0 0 50px #FF00FF, 0 15px 40px rgba(0,0,0,0.3);
    }
}

.file-gallery {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin: 40px 0;
}

.magical-file-card {
    background: linear-gradient(135deg, #000814, #001D3D);
    border-radius: 20px;
    padding: 25px;
    color: white;
    box-shadow: 0 0 20px #00FFFF, 0 10px 40px rgba(0,0,0,0.3);
    transform: translateY(20px);
    opacity: 0;
    animation: slideInUp 0.6s ease-out forwards;
    border: 2px solid #00FFFF;
    position: relative;
    overflow: hidden;
}

.magical-file-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.2), rgba(255, 0, 255, 0.2), transparent);
    animation: shimmer 3s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

@keyframes slideInUp {
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.file-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
}

.file-emoji {
    font-size: 32px;
    filter: drop-shadow(0 0 10px #00FFFF);
}

.file-info {
    flex: 1;
}

.file-name {
    margin: 0;
    font-size: 22px;
    color: #00FFFF;
    text-shadow: 0 0 15px #00FFFF;
}

.file-details {
    margin: 5px 0 0 0;
    color: rgba(255, 255, 255, 0.8);
    font-size: 14px;
}

.file-status {
    font-size: 24px;
    animation: sparkle 1.5s ease-in-out infinite;
    filter: drop-shadow(0 0 10px #FF00FF);
}

@keyframes sparkle {
    0%, 100% { opacity: 1; color: #FF00FF; }
    50% { opacity: 0.5; color: #00FFFF; }
}

.file-preview {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 10px;
    padding: 15px;
    border-left: 4px solid #00FFFF;
    box-shadow: inset 0 0 10px rgba(0, 255, 255, 0.1);
}

.preview-text {
    margin: 0;
    color: rgba(255, 255, 255, 0.9);
    font-style: italic;
}

.action-section {
    text-align: center;
    margin: 50px 0 30px 0;
}

.action-title {
    font-size: 36px;
    color: #00FFFF;
    margin-bottom: 10px;
    text-shadow: 0 0 20px #00FFFF;
}

.action-subtitle {
    font-size: 18px;
    color: #FF00FF;
    margin-bottom: 30px;
    text-shadow: 0 0 15px #FF00FF;
}

.success-animation, .shadow-success, .event-success {
    background: linear-gradient(135deg, #001D3D, #003566);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
    animation: successBounce 0.6s ease-out;
    border: 2px solid #00FF7F;
    box-shadow: 0 0 25px #00FF7F;
}

@keyframes successBounce {
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); opacity: 1; }
}

.auth-portal {
    background: linear-gradient(135deg, #000814, #001D3D, #003566);
    border-radius: 25px;
    padding: 50px 30px;
    text-align: center;
    margin: 40px 0;
    position: relative;
    overflow: hidden;
    border: 2px solid #FF00FF;
    box-shadow: 0 0 40px #FF00FF;
}

.auth-portal::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1), transparent);
    animation: rotate 15s linear infinite;
}

.portal-content {
    position: relative;
    z-index: 2;
}

.portal-title {
    font-size: 42px;
    color: white;
    margin-bottom: 20px;
    text-shadow: 0 0 25px #FF00FF;
}

.portal-description {
    font-size: 20px;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 30px;
    text-shadow: 0 0 10px #00FFFF;
}

.portal-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-top: 30px;
}

.feature-item {
    background: rgba(0, 0, 0, 0.3);
    padding: 15px;
    border-radius: 15px;
    color: white;
    font-weight: bold;
    border: 2px solid #00FFFF;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
}

.empty-state {
    text-align: center;
    padding: 80px 20px;
    background: linear-gradient(135deg, #000814, #001D3D);
    border-radius: 25px;
    margin: 40px 0;
    border: 2px solid #00FF7F;
    box-shadow: 0 0 30px rgba(0, 255, 127, 0.3);
}

.empty-icon {
    font-size: 80px;
    margin-bottom: 30px;
    animation: bounce 2s infinite;
    filter: drop-shadow(0 0 20px #00FFFF);
    color: white !important;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}

.empty-title {
    font-size: 36px;
    color: white !important;
    margin-bottom: 20px;
    text-shadow: 0 0 20px #00FFFF;
}

.empty-description {
    font-size: 18px;
    color: #FF00FF;
    margin-bottom: 30px;
    text-shadow: 0 0 15px #FF00FF;
}

.empty-features {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.feature-badge {
    background: linear-gradient(135deg, #001D3D, #003566);
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    font-weight: bold;
    box-shadow: 0 0 20px #00FF7F;
    border: 1px solid #00FF7F;
}

/* Content sections styling */
.content-section {
    padding: 40px 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.content-section h1 {
    color: #00FFFF;
    text-shadow: 0 0 20px #00FFFF;
    font-weight: bold;
}

.club-card {
    background: linear-gradient(135deg, #003566, #0077B6);
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    color: white;
    box-shadow: 0 0 25px #00FFFF, 0 5px 20px rgba(0,0,0,0.2);
    border: 2px solid #00FFFF;
}

.deleted-club-card {
    background: linear-gradient(135deg, #000814, #001D3D);
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    color: white;
    box-shadow: 0 0 25px #FF00FF, 0 5px 20px rgba(0,0,0,0.2);
    border: 2px solid #FF00FF;
}

.event-card {
    background: linear-gradient(135deg, #000814, #001D3D);
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    color: white;
    box-shadow: 0 0 25px #00FF7F, 0 5px 20px rgba(0,0,0,0.2);
    border: 2px solid #00FF7F;
}

.signin-required {
    background: linear-gradient(135deg, #001D3D, #003566);
    border-radius: 15px;
    padding: 30px;
    margin: 30px 0;
    color: white;
    text-align: center;
    box-shadow: 0 0 30px #FF00FF, 0 5px 20px rgba(0,0,0,0.2);
    border: 2px solid #FF00FF;
}

/* Animation utilities */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes bounceIn {
    0% {
        opacity: 0;
        transform: scale(0.3) translateY(50px);
    }
    50% {
        opacity: 1;
        transform: scale(1.05);
    }
    70% {
        transform: scale(0.9);
    }
    100% {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
</style>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs(["Homepage", "Saved Clubs", "Deleted Clubs", "Calendar"])

#Homepage
with tab1:

    st.markdown('''
    <div class="hero">
        <div class="floating-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
        </div>
        <h1 class="hero-title">GO CLUBBING!</h1>
        <p class="hero-subtitle">⋆˙⟡ Your Digital Club Universe ⋆˙⟡</p>
        <div class="hero-stats">
            <div class="stat-item">
                <span class="stat-number">≔</span>
                <span class="stat-label">Organize</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">𝄜</span>
                <span class="stat-label">Schedule</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">⁀➴</span>
                <span class="stat-label">Thrive</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

 
    st.markdown('''
    <div class="magic-upload-section">
        <div class="upload-header">
            <h2 class="upload-title">⏾⋆.˚ Drop Your Club QR Codes & Photos Here</h2>
            <p class="upload-description">Transform your files into organized club experiences</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Animated file uploader
    uploaded_files = st.file_uploader(
        "Choose your club files", 
        type=["pdf", "png", "jpg", "jpeg", "doc", "docx", "txt"],
        accept_multiple_files=True,
        help="Drag & drop supported • PDF, Images, Documents welcome"
    )
    
    if uploaded_files:
        st.markdown(f'''
        <div class="files-detected">
            <h3 class="files-count"> {len(uploaded_files)} Magical File{'s' if len(uploaded_files) > 1 else ''} Detected!</h3>
        </div>
        ''', unsafe_allow_html=True)
        
        # Beautiful file gallery
        st.markdown('<div class="file-gallery">', unsafe_allow_html=True)
        for i, uploaded_file in enumerate(uploaded_files):
            file_name = uploaded_file.name.split('.')[0].replace('_', ' ').replace('-', ' ').title()
            file_type = uploaded_file.name.split('.')[-1].upper()
            file_size_mb = round(uploaded_file.size / 1024 / 1024, 2) if uploaded_file.size > 1024*1024 else f"{round(uploaded_file.size / 1024, 1)} KB"
            
            # File type emoji
            file_emoji = "🗎" if file_type == "PDF" else "[◉°]" if file_type in ["PNG", "JPG", "JPEG"] else "🗐"
            
            st.markdown(f'''
            <div class="magical-file-card" style="animation-delay: {i*0.1}s">
                <div class="file-header">
                    <span class="file-emoji">{file_emoji}</span>
                    <div class="file-info">
                        <h4 class="file-name">{file_name}</h4>
                        <p class="file-details">{file_type} • {file_size_mb if isinstance(file_size_mb, str) else f"{file_size_mb} MB"}</p>
                    </div>
                    <div class="file-status">⋆˙⟡</div>
                </div>
                <div class="file-preview">
                    <p class="preview-text">Ready to organize!</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.authenticated:
            st.markdown('''
            <div class="action-section">
                <h3 class="action-title">✮⋆˙ Choose Your Section</h3>
                <p class="action-subtitle">Where should these files go?</p>
            </div>
            ''', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Save & Add to Calendar", type="primary", use_container_width=True):
                    for uploaded_file in uploaded_files:
                        new_club = {
                            "name": uploaded_file.name.split('.')[0].replace('_', ' ').replace('-', ' ').title(),
                            "description": f"Club data from {uploaded_file.name}",
                            "file": uploaded_file.name,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "time": "18:00",
                            "location": "Saved Clubs",
                            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "user": st.session_state.username
                        }
                        st.session_state.saved_clubs.append(new_club)
                    
                    st.markdown('''
                    <div class="success-animation">
                        <h4>ꪜ Clubs Updated!</h4>
                        <p>Your files have been saved and stored safely</p>
                    </div>
                    ''', unsafe_allow_html=True)
                    st.balloons()
                    st.rerun()
            
            with col2:
                if st.button("Delete Club", type="secondary", use_container_width=True):
                    for uploaded_file in uploaded_files:
                        new_club = {
                            "name": uploaded_file.name.split('.')[0].replace('_', ' ').replace('-', ' ').title(),
                            "description": f"Club data from {uploaded_file.name}",
                            "file": uploaded_file.name,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "time": "18:00",
                            "location": "Deleted Clubs",
                            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "user": st.session_state.username
                        }
                        st.session_state.deleted_clubs.append(new_club)
                    
                    st.markdown('''
                    <div class="shadow-success">
                        <h4>🗑 Club has been deleted!</h4>
                        <p> Files can be restored if needed </p>
                    </div>
                    ''', unsafe_allow_html=True)
                    st.rerun()
            
            with col3:
                if st.button("Calendar", use_container_width=True):
                    for uploaded_file in uploaded_files:
                        event = {
                            "title": f"{uploaded_file.name.split('.')[0].title()} Gathering",
                            "description": f"Club event taken from {uploaded_file.name}",
                            "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                            "time": "19:00",
                            "location": "Grand Assembly Hall",
                            "user": st.session_state.username
                        }
                        st.session_state.calendar_events.append(event)
                    
                    st.markdown('''
                    <div class="event-success">
                        <h4>ꪜ Events Saved!</h4>
                        <p> It has been added to the calendar</p>
                    </div>
                    ''', unsafe_allow_html=True)
                    st.rerun()
        
        else:
            st.markdown('''
            <div class="auth-portal">
                <div class="portal-content">
                    <h3 class="portal-title" style="color:white;">ꗃ You're not signed in</h3>
                    <p class="portal-description">Sign in to unlock the full power of Go Clubbing!</p>
                    <div class="portal-features">
                        <div class="feature-item">⟡ Save & Add to Calendar</div>
                        <div class="feature-item">⟡ Deleted Clubs restoration</div>
                        <div class="feature-item">⟡ Sync across all calendars</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    else:
        st.markdown('''
        <div class="empty-state">
            <div class="empty-content">
                <div class="empty-icon">˗ˏˋ ★ ˎˊ˗</div>
                <h3 class="empty-title">The Night is Young</h3>
                <p class="empty-description">Upload your first files to start the club experience</p>
                <div class="empty-features">
                    <span class="feature-badge">🗎 PDFs</span>
                    <span class="feature-badge">[◉°] Images</span>
                    <span class="feature-badge">🗐 Documents</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

# Saved Clubs Tab
with tab2:
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.title("⎙ Saved Clubs")
    
    if not st.session_state.authenticated:
        # Show sign in required message
        st.markdown('''
        <div class="signin-required">
            <h2>🔒 Please Sign In or Create an Account</h2>
            <p>Sign in or create a new account using the sidebar to access your saved clubs and manage your organization data.</p>
            <p><strong>Benefits of having an account:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Save and organize your clubs</li>
                <li>Access your calendar events</li>
                <li>Manage deleted items</li>
                <li>Sync across sessions</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    else:
        # Add new club form
        with st.expander("+ Add New Club Manually"):
            with st.form("add_club_form"):
                club_name = st.text_input("Club Name")
                club_description = st.text_area("Club Description")
                club_date = st.date_input("Event Date")
                club_time = st.time_input("Event Time")
                club_location = st.text_input("Location", placeholder="e.g., Student Center Ballroom")
                
                if st.form_submit_button("Add Club"):
                    if club_name:
                        new_club = {
                            "name": club_name,
                            "description": club_description,
                            "date": club_date.strftime("%Y-%m-%d"),
                            "time": club_time.strftime("%H:%M"),
                            "location": club_location,
                            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "user": st.session_state.username,
                            "file": "Manual Entry"
                        }
                        st.session_state.saved_clubs.append(new_club)
                        st.success(f"Added club '{club_name}' successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter a club name")
        
        # Show saved clubs for authenticated users
        if st.session_state.saved_clubs:
            user_clubs = [club for club in st.session_state.saved_clubs if club.get('user') == st.session_state.username]
            
            if user_clubs:
                st.markdown(f"### ᯓ★ You have {len(user_clubs)} saved club(s)")
                
                for i, club in enumerate(user_clubs):
                    st.markdown(f'''
                    <div class="club-card">
                        <h3>⋆ {club["name"]}</h3>
                        <p><strong>Description:</strong> {club["description"]}</p>
                        <p><strong>🗒 Date:</strong> {club.get("date", "Not set")}</p>
                        <p><strong>⏲ Time:</strong> {club.get("time", "Not set")}</p>
                        <p><strong>⚲ Location:</strong> {club.get("location", "Not set")}</p>
                        <p><strong>🗁 Source File:</strong> {club.get("file", "Unknown")}</p>
                        <p><small>⤷ Added on {club["date_added"]}</small></p>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_{i}"):
                            st.info(f"Editing functionality for {club['name']} - Feature coming soon!")
                    with col2:
                        if st.button(f"🗒 Add to Calendar", key=f"calendar_{i}"):
                            event = {
                                "title": f"{club['name']} Event",
                                "description": club["description"],
                                "date": club.get("date", datetime.now().strftime("%Y-%m-%d")),
                                "time": club.get("time", "18:00"),
                                "location": club.get("location", "TBD"),
                                "user": st.session_state.username
                            }
                            st.session_state.calendar_events.append(event)
                            st.success(f"ꪜ Added {club['name']} to calendar!")
                    with col3:
                        if st.button(f"🗑 Delete", key=f"delete_{i}"):
                            for j, full_club in enumerate(st.session_state.saved_clubs):
                                if (full_club['name'] == club['name'] and 
                                    full_club.get('user') == st.session_state.username):
                                    deleted_club = st.session_state.saved_clubs.pop(j)
                                    st.session_state.deleted_clubs.append(deleted_club)
                                    st.success(f"🗑 Moved {club['name']} to deleted clubs!")
                                    st.rerun()
                                    break
            else:
                st.info(" No clubs saved yet. Upload files on the Homepage or add clubs manually above.")
        else:
            st.info(" No clubs saved yet. Upload files on the Homepage or add clubs manually above.")

    st.markdown('</div>', unsafe_allow_html=True)

# Deleted Clubs Tab
with tab3:
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.title("🗑 Deleted Clubs")
    
    if not st.session_state.authenticated:
        # Show sign in required message
        st.markdown('''
        <div class="signin-required">
            <h2>🔒 Please Sign In or Create an Account</h2>
            <p>Sign in or create a new account using the sidebar to view and restore your deleted clubs.</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        # Show deleted clubs for authenticated users
        user_deleted_clubs = [club for club in st.session_state.deleted_clubs if club.get('user') == st.session_state.username]
        
        if user_deleted_clubs:
            for i, club in enumerate(user_deleted_clubs):
                st.markdown(f'''
                <div class="deleted-club-card">
                    <h3>{club["name"]} (Deleted)</h3>
                    <p><strong>Description:</strong> {club["description"]}</p>
                    <p><strong>File:</strong> {club["file"]}</p>
                    <p><strong>Originally Added:</strong> {club["date_added"]}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"Restore {club['name']}", key=f"restore_{i}"):
                        # Find the actual index in the full list
                        for j, full_club in enumerate(st.session_state.deleted_clubs):
                            if (full_club['name'] == club['name'] and 
                                full_club.get('user') == st.session_state.username):
                                restored_club = st.session_state.deleted_clubs.pop(j)
                                st.session_state.saved_clubs.append(restored_club)
                                st.success(f"Restored {club['name']}!")
                                st.rerun()
                                break
                with col2:
                    if st.button(f"Permanently Delete", key=f"perm_delete_{i}"):
                        # Find the actual index in the full list
                        for j, full_club in enumerate(st.session_state.deleted_clubs):
                            if (full_club['name'] == club['name'] and 
                                full_club.get('user') == st.session_state.username):
                                st.session_state.deleted_clubs.pop(j)
                                st.info(f"Permanently deleted {club['name']}")
                                st.rerun()
                                break
        else:
            st.info("No deleted clubs. Deleted clubs will appear here.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Calendar Tab
with tab4:
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.title("🗒 Calendar")
    
    if not st.session_state.authenticated:
        # Show sign in required message
        st.markdown('''
        <div class="signin-required">
            <h2>🔒 Please Sign In or Create an Account</h2>
            <p>Sign in or create a new account using the sidebar to view and manage your calendar events.</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        # Add new event form
        with st.expander("+ Add New Event Manually"):
            with st.form("add_event_form"):
                event_title = st.text_input("Event Title")
                event_description = st.text_area("Event Description")
                event_date = st.date_input("Event Date", value=datetime.now())
                event_time = st.time_input("Event Time")
                
                if st.form_submit_button("Add Event"):
                    new_event = {
                        "title": event_title,
                        "description": event_description,
                        "date": event_date.strftime("%Y-%m-%d"),
                        "time": event_time.strftime("%H:%M"),
                        "user": st.session_state.username
                    }
                    st.session_state.calendar_events.append(new_event)
                    st.success(f"Added event '{event_title}' to calendar!")
        
        # Display events for current user
        user_events = [event for event in st.session_state.calendar_events if event.get('user') == st.session_state.username]
        
        if user_events:
            st.subheader("Upcoming Events")
            
            # Sort events by date
            sorted_events = sorted(user_events, 
                                 key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
            
            for i, event in enumerate(sorted_events):
                st.markdown(f'''
                <div class="event-card">
                    <h3>🗒 {event["title"]}</h3>
                    <p><strong>Description:</strong> {event["description"]}</p>
                    <p><strong>Date:</strong> {event["date"]}</p>
                    <p><strong>Time:</strong> {event["time"]}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"Remove Event", key=f"remove_event_{i}"):
                    # Find the actual index in the full list
                    for j, full_event in enumerate(st.session_state.calendar_events):
                        if (full_event['title'] == event['title'] and 
                            full_event.get('user') == st.session_state.username and
                            full_event['date'] == event['date']):
                            st.session_state.calendar_events.pop(j)
                            st.rerun()
                            break
            
            # Calendar view (simple monthly view)
            st.subheader("Calendar View")
            
            # Create a simple calendar DataFrame
            today = datetime.now()
            start_date = today.replace(day=1)
            
            # Generate calendar for current month
            calendar_data = []
            for day in range(1, 32):
                try:
                    current_date = start_date.replace(day=day)
                    date_str = current_date.strftime("%Y-%m-%d")
                    events_today = [e for e in user_events if e["date"] == date_str]
                    calendar_data.append({
                        "Date": current_date.strftime("%d"),
                        "Day": current_date.strftime("%A"),
                        "Events": len(events_today),
                        "Event Titles": ", ".join([e["title"] for e in events_today]) if events_today else "No events"
                    })
                except ValueError:
                    break
            
            if calendar_data:
                df = pd.DataFrame(calendar_data)
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No events scheduled. Upload a file on the Homepage or add events manually above.")
    
    st.markdown('</div>', unsafe_allow_html=True)