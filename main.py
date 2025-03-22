import streamlit as st

def main():
    st.set_page_config(page_title="Secure Entry/Exits", layout="wide")

    
    if "entry_status" not in st.session_state:
        st.session_state.entry_status = {
            "Main Entrance Door": "secured",
            "Back Door": "unsecured",
            "Side Window": "pending"
        }

    if "previous_status" not in st.session_state:
        st.session_state.previous_status = st.session_state.entry_status.copy()

   
    background_color = "red" if "unsecured" in [st.session_state.entry_status["Main Entrance Door"], st.session_state.entry_status["Back Door"]] else "white"

    
    st.markdown(
        f"""
        <style>
            body {{
                background-color: {background_color};
            }}
            .stButton>button {{
                background-color:black;
                color:white;
                border-radius: 8px !important;
                padding: 4px 8px !important;
                border: !important;
                text-align: center !important;
                font-size: 16px !important;
                cursor: pointer !important;
                display: inline-block !important;
                width: 100px;
                margin-top: 20px;
                transition: background-color 0.3s, transform 0.3s;
            }}
            .stButton>button:hover {{
                border:1px solid black;
                background-color: white !important;
                color:black;
                transform: scale(1.05);
                
            }}
            
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" integrity="sha384-k6RqeWeci5ZR/Lv4MR0sA0FfDOMDi1H2A8FNoVhD8zD4Uj6kf0CCDXPtk3tAw3K" crossorigin="anonymous"/>

        """,
        unsafe_allow_html=True
    )

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
                if status == "pending":
                    if st.button("Secure", key="side_window_secure_button"):
                        st.toast("⏳ Side Window status is PENDING")
                else:
                    button_label = 'Secure' if status == "unsecured" else 'Unsecure'
                    if st.button(button_label, key=name):
                        new_status = "unsecured" if status == "secured" else "secured"
                        st.session_state.entry_status[name] = new_status
                        toast_icon = "✔️" if new_status == "secured" else "⚠️"
                        st.toast(f"{toast_icon} {name} is now {new_status.upper()}!")
                        st.rerun()

if __name__ == "__main__":
    main()