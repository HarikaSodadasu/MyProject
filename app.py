import streamlit as st
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User
from auth import authenticate_user, create_user

# Create tables
Base.metadata.create_all(bind=engine)

def login():
    st.markdown("""
        <style>
            .title { text-align: center; font-size: 30px; font-weight: bold; margin-bottom: 20px; }
            .stButton>button {
                background: linear-gradient(135deg, #007BFF, #004d99);
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                border: none;
                width: 120px;
                display: block;
                margin: auto;
                margin-top: 15px;
            }
            .stButton>button:hover {
                background: linear-gradient(135deg, #0056b3, #003366);
                transform: scale(1.07);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title">Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        with SessionLocal() as db:
            user = authenticate_user(db, username, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["username"] = user.username
                st.session_state["role"] = user.role
                st.rerun()
            else:
                st.error("Invalid username or password!")

    # Register New User Section
    with st.expander("Register New User"):
        new_user = st.text_input("New Username")
        new_pw = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["user", "admin"])
        if st.button("Register"):
            with SessionLocal() as db:
                if db.query(User).filter(User.username == new_user).first():
                    st.warning("Username already exists!")
                else:
                    create_user(db, new_user, new_pw, role)
                    st.success("User registered successfully!")

def dashboard():
    st.set_page_config(page_title="Secure Entry/Exits", layout="wide")

    if "entry_status" not in st.session_state:
        st.session_state.entry_status = {
            "Main Entrance Door": "secured",
            "Back Door": "unsecured",
            "Side Window": "pending"
        }

    if "previous_status" not in st.session_state:
        st.session_state.previous_status = st.session_state.entry_status.copy()

    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                font-size: 30px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .stButton>button {
                background-color: black;
                color: white;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 16px;
                cursor: pointer;
                width: 180px;
                text-align: center;
                display: inline-block;
                transition: background-color 0.3s, transform 0.3s;
                font-weight: bold;
            }
            .stButton>button:hover {
                background-color: white;
                color: black;
                border: 1px solid black;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("Account Info", key="account_info", help="Click to view account details"):
        st.session_state["show_sidebar"] = not st.session_state.get("show_sidebar", False)

    if st.session_state.get("show_sidebar", False):
        with st.sidebar:
            st.markdown("## 👤 User Details")
            st.write(f"🔐 **User:** {st.session_state.get('username', 'N/A')}")
            st.write(f"👤 **Role:** {st.session_state.get('role', 'N/A')}")
            if st.button("Logout"):
                for key in ["authenticated", "username", "role", "show_sidebar"]:
                    st.session_state[key] = None
                st.rerun()

    st.markdown('<div class="title">Secure Entry/Exits Dashboard</div>', unsafe_allow_html=True)

    col_alerts, col_controls = st.columns([1, 4])

    with col_alerts:
        st.subheader("Security Alerts")
        alerts = []
        for name, status in st.session_state.entry_status.items():
            if status == "unsecured":
                alerts.append(f"⚠️ {name} is UNSECURED!")
            elif status == "pending":
                alerts.append(f"⏳ {name} is PENDING!")
        for alert in alerts:
            st.warning(alert)
        if not alerts:
            st.success("✔️ All entries are SECURED!")

    changed_statuses = [(name, status) for name, status in st.session_state.entry_status.items()
                        if st.session_state.previous_status[name] != status]
    if changed_statuses:
        for name, status in changed_statuses:
            icon = "✔️" if status == "secured" else "⚠️" if status == "unsecured" else "⏳"
            msg = f"{icon} {name} is now {status.upper()}"
            st.toast(msg)
        st.session_state.previous_status = st.session_state.entry_status.copy()

    with col_controls:
        st.write("---")
        for name, status in st.session_state.entry_status.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(name)
                st.text(f"Type: {'Door' if 'Door' in name else 'Window'}")
                color = "orange" if status == "pending" else ("green" if status == "secured" else "red")
                st.markdown(f'<span style="background-color:{color}; padding:5px 10px; border-radius:20px; color:white;">{status}</span>', unsafe_allow_html=True)

            with col2:  
                if name == "Side Window":
                    if st.button("🔒 Secure", key=f"{name}_secure_button"):
                        st.toast(f"⏳ {name} status is PENDING")
                elif name == "Main Entrance Door" and st.session_state["role"] != "admin":
                    st.text("🔒 Restricted")
                else:
                    icon = "🔒" if status == "secured" else "🔓"
                    label = f"{icon} {'Unsecure' if status == 'secured' else 'Secure'}"
                    if st.button(label, key=name):
                        st.session_state.entry_status[name] = "unsecured" if status == "secured" else "secured"
                        st.rerun()

# Initialize session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    login()
else:
    dashboard()
