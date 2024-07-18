import streamlit as st
from streamlit import session_state,column_config
from backend.constants import INTERNALS_PATH
from backend.data_processing import is_any_dataframe_cell_empty
from backend.file_operations import get_user_data_as_dataframe, push_edits_to_users_yaml
from components.navigation import show_go_back_to_home_in_sidebar, go_to_home_page
from components.page_configuration_component import page_configuration


page_configuration('🧔‍♂️', "Manage Users")
show_go_back_to_home_in_sidebar()

USERNAME = session_state.user_info["username"]
USERTYPE = session_state.user_info["user_type"]
USERTYPES = ["admin", "elevated-user", "user"]

def main()-> None:
    st.title("🧑‍💻 User Management System")
    st.divider()


    if USERTYPE == "admin":
        user_data_dataframe = get_user_data_as_dataframe()
        user_data_edit_table_column_data = {
            "username": column_config.TextColumn(
                label="Username",
                required=True,
            ),
            "name":column_config.TextColumn(
                label="Name",
                required=True,
            ),
            "password":column_config.TextColumn(
                label="Password",
                required=True 
            ),
            "user_type":column_config.SelectboxColumn(
                label="User Type",
                required=True,
                options=USERTYPES
            )
        }
        with st.container():
            updated_user_data_dataframe = st.data_editor(
                data=user_data_dataframe,
                column_config=user_data_edit_table_column_data,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
            )

            submit_edits = st.button(
                label="Submit Changes to the Database",
                type="primary",
                disabled=False
            )
            if submit_edits:
                push_edits_to_users_yaml(updated_user_data_dataframe)
                go_to_home_page()


if __name__ == '__main__':
    main()