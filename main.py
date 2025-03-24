import streamlit as st

CREDENTIALS = {
    "admin": {"password": "password123", "role": "admin"},
    "user": {"password": "userpass", "role": "user"}
}

def login():
    """Login Page"""
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
                background: linear-gradient(135deg, #007BFF, #004d99);
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease-in-out;
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
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="title">Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in CREDENTIALS and CREDENTIALS[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["role"] = CREDENTIALS[username]["role"]
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Invalid username or password!")

def dashboard():
    """Secure Entry/Exits Dashboard"""
    st.set_page_config(page_title="Secure Entry/Exits", layout="wide")

    if "entry_status" not in st.session_state:
        st.session_state.entry_status = {
            "Main Entrance Door": "secured",
            "Back Door": "unsecured",
            "Side Window": "pending"
        }

    if "previous_status" not in st.session_state:
        st.session_state.previous_status = st.session_state.entry_status.copy()

    background_color = "red" if "unsecured" in st.session_state.entry_status.values() else "white"

    st.markdown(
        f"""
        <style>
            body {{ background-color: {background_color}; }}
            .title {{
                text-align: center;
                font-size: 30px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .stButton>button {{
                background-color: black;
                color: white;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 16px;
                cursor: pointer;
                width: 100px;
                margin-top: 10px;
                transition: background-color 0.3s, transform 0.3s;
            }}
            .stButton>button:hover {{
                border: 1px solid black;
                background-color: white;
                color: black;
                transform: scale(1.05);
            }}
            .account-info-btn {{
                position: fixed;
                top: 10px;
                left: 10px;
                font-size: 16px;
                padding: 8px 15px;
                background: black;
                color: white;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: 0.3s;
            }}
            .account-info-btn:hover {{
                background: white;
                color: black;
                border: 1px solid black;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Account Info Button in the top-left corner
    if st.button("Account Info", key="account_info", help="Click to view account details"):
        st.session_state["show_sidebar"] = not st.session_state.get("show_sidebar", False)

    if st.session_state.get("show_sidebar", False):
        with st.sidebar:
            st.markdown("## 👤 User Details")
            st.write(f"🔐 **User:** {st.session_state.get('username', 'N/A')}")
            st.write(f"👤 **Role:** {st.session_state.get('role', 'N/A')}")
            if st.button("Logout"):
                st.session_state["authenticated"] = False
                st.session_state["username"] = None
                st.session_state["role"] = None
                st.session_state["show_sidebar"] = False
                st.rerun()

    st.markdown('<div class="title">Secure Entry/Exits Dashboard</div>', unsafe_allow_html=True)

    col_alerts, col_controls = st.columns([1, 4])

    with col_alerts:
        st.subheader("Security Alerts")
        alert_messages = []
        for name, status in st.session_state.entry_status.items():
            if status == "unsecured":
                alert_messages.append(f"⚠️ {name} is UNSECURED!")
            elif status == "pending":
                alert_messages.append(f"⏳ {name} is PENDING!")

        if alert_messages:
            for message in alert_messages:
                st.warning(message)
        else:
            st.success("✔️ All entries are SECURED!")

    changed_statuses = [(name, status) for name, status in st.session_state.entry_status.items() if st.session_state.previous_status[name] != status]

    if changed_statuses:
        for name, status in changed_statuses:
            icon = "✔️" if status == "secured" else "⚠️" if status == "unsecured" else "⏳"
            msg = f"{icon} {name} is now {'SECURED' if status == 'secured' else 'UNSECURED' if status == 'unsecured' else 'PENDING'}"
            st.toast(msg)

        st.session_state.previous_status = st.session_state.entry_status.copy()

    with col_controls:
        st.write("---")
        for name, status in st.session_state.entry_status.items():
            col_entry, col_button = st.columns([3, 1])
            with col_entry:
                st.subheader(name)
                st.text(f"Type: {'Door' if 'Door' in name else 'Window'}")
                color = "orange" if status == "pending" else ("green" if status == "secured" else "red")
                
                st.markdown(
                    f'<span style="background-color:{color}; padding:5px 10px; border-radius:20px; color:white;">{status}</span>',
                    unsafe_allow_html=True,
                )

            with col_button:
                
                if name == "Main Entrance Door" and st.session_state["role"] != "admin":
                    st.text("🔒 Restricted")
                else:
                    if status == "pending":
                        if st.button("Secure", key=f"{name}_secure_button"):
                            st.toast(f"⏳ {name} status is PENDING")
                    else:
                        button_label = 'Secure' if status == "unsecured" else 'Unsecure'
                        if st.button(button_label, key=name):
                            new_status = "unsecured" if status == "secured" else "secured"
                            st.session_state.entry_status[name] = new_status
                            toast_icon = "✔️" if new_status == "secured" else "⚠️"
                            st.toast(f"{toast_icon} {name} is now {new_status.upper()}!")
                            st.rerun()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "show_sidebar" not in st.session_state:
    st.session_state["show_sidebar"] = False

if not st.session_state["authenticated"]:
    login()
else:
    dashboard()
