import streamlit as st

def main():
    st.set_page_config(page_title="Demo", layout="wide")

    # Initialize session state for entry statuses
    if "entry_status" not in st.session_state:
        st.session_state.entry_status = {
            "Main Entrance": "secured",
            "Back Door": "unsecured",
            "Side Window": "pending"  # Start with pending for Side Window
        }

    if "previous_status" not in st.session_state:
        st.session_state.previous_status = st.session_state.entry_status.copy()

    # Custom CSS for buttons
    st.markdown(
        """
        <style>
            .stButton>button {
                background-color: black !important;
                color: white !important;
                border-radius: 8px !important;
                padding: 4px 8px !important; /* Reduced padding for smaller buttons */
                border: none !important;
                text-align: center !important;
                font-size: 16px !important;
                cursor: pointer !important;
                display: inline-block !important;
                width: 100px; /* Set button width */
                margin-top: 20px; /* Adjust margin to push the button down */
            }
            .stButton>button:hover {
                background-color: #333 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Layout columns: Left for alerts, Right for controls
    col_alerts, col_controls = st.columns([1, 4])

    with col_alerts:
        st.subheader("🚨 Security Alerts")
        
        # Check for any unsecured entries
        alert_messages = []
        for name, status in st.session_state.entry_status.items():
            if status == "unsecured":
                alert_messages.append(f"⚠️ {name} is UNSECURED!")
        
        # Always show alert for Side Window
        if st.session_state.entry_status["Side Window"] == "pending":
            alert_messages.append("⚠️ Side Window is PENDING!")

        if alert_messages:
            for message in alert_messages:
                st.warning(message)
        else:
            st.success("✅ All entries are SECURED!")

    # Pop-up notification when status changes
    changed_statuses = []

    for name, status in st.session_state.entry_status.items():
        if st.session_state.previous_status[name] != status:
            changed_statuses.append((name, status))

    if changed_statuses:
        for name, status in changed_statuses:
            msg = f"{name} is now {'SECURED ✅' if status == 'secured' else 'UNSECURED ⚠️' if status == 'unsecured' else 'PENDING ⏳'}"
            st.toast(msg, icon="✅" if status == 'secured' else "⚠️")

        # Update previous status after showing notification
        st.session_state.previous_status = st.session_state.entry_status.copy()

    with col_controls:
        st.write("---")
        # Create a container for entries
        entry_columns = st.columns(2)

        for i, (name, status) in enumerate(st.session_state.entry_status.items()):
            with entry_columns[i % 2]:  # Alternate between the two columns
                # Display entry details
                st.subheader(name)
                st.text(f"Type: {'Door' if 'Door' in name else 'Window'}")

                # Status indicator with custom styles
                color = "orange" if name == "Side Window" and status == "pending" else ("green" if status == "secured" else "red")
                
                st.markdown(
                    f'<span style="background-color:{color}; padding:5px 10px; border-radius:20px; color:white;">{status}</span>',
                    unsafe_allow_html=True,
                )

                # Adjust the layout for buttons
                button_column = st.empty()  # Create an empty column for button
                button_label = "Unsecure" if status == "secured" else "Secure"
                with button_column:
                    if st.button(button_label, key=name):
                        if name == "Side Window":
                            new_status = "pending" if status == "pending" else "pending"
                            st.session_state.entry_status[name] = new_status
                        else:
                            new_status = (
                                "unsecured" if status == "secured" else "secured"
                            )
                            st.session_state.entry_status[name] = new_status
                            st.toast(f"{name} is now {new_status.upper()}!", icon="✅" if new_status == "secured" else "⚠️")

                        # Refresh the app to reflect changes (optional)
                        st.rerun()

if __name__ == "__main__":
    main()