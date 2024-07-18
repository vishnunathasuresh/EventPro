import streamlit as st 
from streamlit import session_state
import pickle as pkl
from os import makedirs, remove
from backend.constants import INTERNALS_PATH, CHAT_FILE
from backend.data_processing import add_to_session_state
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration



page_configuration(
    icon="📧",
    title="Chat Room",
    autorefresh=True
)
show_go_back_to_home_in_sidebar()

chat_help = """
This is a chat applet that allows for quick and efficient communication between **elevated-users** and **admins**.
"""
USER_HANDLE = session_state.user_info["handle"]
USERTYPE = session_state.user_info["user_type"]
FILE = INTERNALS_PATH + CHAT_FILE
AVATAR = session_state.user_info["avatar"]


def main()-> None:
    st.title("📧 Chat Window", help = chat_help)
    st.divider()
    

    clear_chat_history = st.button(
        label="Clear Chat History for all",
        type="primary",
        disabled=USERTYPE != "admin",
        help="Clears the messages and restarts the chat afresh."
    )

    if clear_chat_history:
        clear_chat_history_for_all()

    add_to_session_state(
        messages = []
    )
    
    # Load messages to memory from files
    load_messages_from_file()

    # Display chat messages from history on app rerun
    load_messages_to_app()
    
    # Show message-input-box and add to messages
    if prompt := st.chat_input("Your Message"):
        load_messages_from_file()

        handle = USER_HANDLE
        final_prompt = f"##### {handle}\n{prompt}"
        with st.chat_message("user", avatar=AVATAR):
            st.write(final_prompt)

        session_state.messages.append(
            {
                "role": USER_HANDLE,
                "content": final_prompt,
                "avatar": AVATAR,
            }
        )
        write_messages_to_file()

def clear_chat_history_for_all():
    try:
        remove(FILE)
    finally:
        session_state.messages = []
        st.rerun()

def write_messages_to_file():
    with open(FILE, "wb") as file:
        pkl.dump(session_state.messages, file)

def load_messages_from_file():
    try:
        with open(FILE, "rb") as file:
            session_state.messages = pkl.load(file)
    except FileNotFoundError:
        session_state.messages = []
        makedirs(INTERNALS_PATH, exist_ok=True)

def load_messages_to_app():
    for message in session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])
    
if __name__ == '__main__':
    main()