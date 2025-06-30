# backend/auth.py
import streamlit as st
import yaml
import bcrypt
import streamlit_authenticator as stauth

def authenticate_user():

    # Load the configuration file
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    # Initialize the authenticator with config settings
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Render the login form
    with st.form(key="login_form"):
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            # Check if username exists and match password
            if username in config['credentials']['usernames']:
                stored_hashed_password = config['credentials']['usernames'][username]['password']
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                    user_info = config['credentials']['usernames'][username]
                    name = user_info['name']
                    role = user_info['role']
                    st.session_state.user_role = role
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.name = name
                    st.rerun()  # Rerun the app to reload the state
                    return authenticator, config, name, username  # Return successful login details
                else:
                    st.error("Username/password is incorrect.")
            else:
                st.error("Username does not exist.")
                
    return None, None, None, None
