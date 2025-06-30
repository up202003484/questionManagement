# app.py
import streamlit as st
from backend.auth import authenticate_user
from frontend.ui_question import capture_question_ui
from frontend.ui_kanban import display_kanban_board
from frontend.ui_discussion import discussion_board
# from frontend.ui_audio import display_audio_ui
import pathlib
import os


def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")



def main():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        # Show the login form if not authenticated
        authenticator, config, name, username = authenticate_user()
        st.markdown("""
            **🔐 Authentication options available:**  

            | Username        | Password     | Role  Capabilities|
            |-----------------|--------------|-----------|
            | question_owner  | qo123        | Captures and edits questions' priority                                                            |
            | decision_maker  | dm123        |  Captures questions and decides the status changes for each question from inception to resolution |
            | product_owner   | po123        | Captures and reviews questions, adjusts priority, and links business objectives                   |
            | dev_user        | dev123       | Captures questions and discusses them from a technological standpoint                             |
        """)
        if authenticator and username:
            loged_in()
        else:
            st.warning("Please log in to continue.")
    else:
        # If already authenticated, show the backlog
        loged_in()

def loged_in():
    
    username_top_page = st.session_state['name'].title()
    icon_path = "https://upload.wikimedia.org/wikipedia/commons/2/2c/Default_pfp.svg"

    html_content = f"""
    <div style="text-align:center;">
        <img src="{icon_path}" style="width: 80px; height: 80px; border-radius: 50%;"/>
        <h3 style="color:black;">Hello, {username_top_page}</h3>
        <hr style="border:1px solid #c0c0c0;"/>
    </div>
    """

    st.sidebar.markdown(html_content, unsafe_allow_html=True)


    

    # Initialize session state for navigation
    if "page" not in st.session_state:
        st.session_state.page = "Kanban"

    # Sidebar menu (HTML-based clickable items)
    with st.sidebar:
        st.markdown("""
        <style>
          
            div.stButton > button {
                all: unset;
                display: inline-block;
                padding: 4px 8px; /* optional, controls spacing around text */
                color: black;
                background-color: transparent;
                cursor: pointer;
                font-size: 16px;
                border-radius: 688px;
            }

            div.stButton > button:hover {
                color: white;
                background-color: #c0c0c0;
            }

            div.stButton > button:focus:not(:active) {
                color: white;
                background-color: #c0c0c0;
            }
        </style>
        """, unsafe_allow_html=True)

        with st.container():

            menu = {
                "Kanban": "📋 Question Board",
                "Capture Question": "✍️ Capture Question",
                "Discussion": "💬 Discussion",
                # "Audio": "🎤 Audio"
            }

            for key, label in menu.items():
                if st.button(label, key=key):
                    st.session_state.page = key

        # --- Page Routing ---
    if st.session_state.page == "Capture Question":
        capture_question_ui()
    elif st.session_state.page == "Discussion":
        discussion_board()
    elif st.session_state.page == "Kanban":
        display_kanban_board()
    # elif st.session_state.page == "Audio":
    #     display_audio_ui()  # Assuming you have a function for audio UI


    html_content = f"""
            <hr style="border:1px solid #c0c0c0;"/>
        """
    st.sidebar.markdown(html_content, unsafe_allow_html=True)
    

    if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.name = None
            st.rerun()  

    # Add footer at the bottom of the sidebar
    # st.sidebar.markdown(
    #     """
    #     <div style=" text-align: center;">
    #         <p style="color:gray; font-size: 12px;">Copyright © 2025 - Diogo Lemos</p>
    #     </div>
    #     """,
    #     unsafe_allow_html=True
    # )

    

    



if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Architecture Questions")
    st.session_state["theme"] = "light"
    css_path=pathlib.Path("assets/styles.css")
    load_css(css_path)
    main()
