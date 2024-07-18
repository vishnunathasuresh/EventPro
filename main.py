from socket import gethostbyname, gethostname
import streamlit as st 
from streamlit import session_state
from backend import *
from components import *
from backend.constants import *

page_configuration(
    icon="🏡",
    title="Home"
)

def main():
    st.title("🏡 EventPro Home")
    st.divider()

    auth = Authenticator()

    username, authenticated, usertype, userinfo = auth.login()

    if authenticated:
        initialize_userinfo(userinfo, username)
        current_database = get_current_database_name()
        saved_databases = get_saved_databases()
        if current_database:
            get_authenticated_pages_database_present()
            initailize_database_functions(usertype)


        else:
            get_authenticated_no_database_pages()
            if usertype != "admin":
                show_error_message("Contact Admin... The current database is yet to be created")
        auth.logout()
        display_general_details_and_userinfo(current_database, saved_databases, userinfo)
  
    else:
        get_unauthenticated_pages()
        show_general_message("Authentication required", icon = "🛡️")
       
def initailize_database_functions(user_type):
    if user_type == "admin":
        with st.sidebar:
            st.divider()
            
            delete_database = st.button(
                label="Delete Database Permanently",
                help="This action is permanent and it cannot be reversed",
                type="primary",
                use_container_width= True,
            )

            save_database = st.button(
                label="Archive Database",
                help="Archiving a database would save the database state. The database will be deactivated for further writing purposes.",
                type="primary",
                use_container_width= True,
            )
        if delete_database:
            delete_database_permanent()
            st.rerun()
        if save_database:
            archive_database()
            st.rerun()
        
def initialize_userinfo(userinfo, username):
    if "user_info" not in session_state:
        session_state["user_info"] = userinfo
        show_success_message("Authentication successful")
        show_general_message(f"Welcome **{username}** to Eventpro", icon="🚀")
    else:
        if session_state.user_info != userinfo:
            session_state.user_info = userinfo
        
def display_general_details_and_userinfo(current_database, saved_databases, user_info):
    info_container = st.container(border= True)
    with info_container:
            st.subheader(
                "✨ Important Info",
                divider=True
            )
            databasename = current_database.split(".")[0] if current_database is not None else ""
            st.write("🚀 Current Database : ", databasename)
            st.write("🚀 Saved Databases : ", " ; ".join(saved_databases))
            f"🚀 The IP address : **{gethostbyname(gethostname())}:8501**"
    user_container = st.container(border=True)
    with user_container:
        st.subheader(
            "😉 User Info",
            divider=True
        )
        f"**➡️ Username : {user_info['username'] }**"
        f"**➡️ Name : {user_info['name'] }**"
        f"**➡️ Role : {user_info['user_type'] }**"
        f"**➡️ Handle : {user_info['handle'] }**"
        f"**➡️ Avatar : {user_info['avatar'] }**" 



if __name__ == "__main__":
    main()