import streamlit as st
from streamlit import session_state


def get_authenticated_pages_database_present():
    USERTYPE = session_state["user_info"]["user_type"]
    ADMIN = "admin"
    USER = "user"

    with st.sidebar:
        st.image("./assets/long-icon.png", use_column_width=True)

        menu_container = st.container(border=False)

        with menu_container:
            actions_container = st.container()
            database_container = st.container()
            connect_container = st.container()
            with actions_container:
                st.subheader("Actions", divider=True)

                st.page_link(
                    label="Participant Entry",
                    page="./pages/participant-entry.py",
                    icon="✒️",
                    help="Create and manage participants.",
                    use_container_width=True,
                )

                st.page_link(
                    label="Reports",
                    page="./pages/report-generator.py",
                    icon="📃",
                    disabled=USERTYPE != ADMIN,
                    help="Generate detailed reports of participants.",
                    use_container_width=True,
                )

                st.page_link(
                    label="Judgement",
                    page="./pages/judge-events.py",
                    icon="🎯",
                    disabled=USERTYPE != ADMIN,
                    help="Judge events that have occured.",
                    use_container_width=True,
                )

                st.page_link(
                    label="Group Judgement",
                    page="./pages/group-judge-events.py",
                    icon="🎯",
                    disabled=USERTYPE != ADMIN,
                    help="Judge events that have occured.",
                    use_container_width=True,
                )

                st.page_link(
                    label="Results and Certificates",
                    page="./pages/results-and-certificates-generator.py",
                    icon="🎖️",
                    disabled=USERTYPE != ADMIN,
                    help="Generate final result and issue certificates.",
                    use_container_width=True,
                )

                st.page_link(
                    label="Manage Users",
                    page="./pages/manage-users.py",
                    icon="🛡️",
                    disabled=USERTYPE != ADMIN,
                    help="Manage users having access to the application.",
                    use_container_width=True,
                )

            with database_container:
                st.subheader("Database", divider=True)

                st.page_link(
                    label="Current Database",
                    page="./pages/current-database-specifications.py",
                    icon="🚀",
                    disabled=USERTYPE == USER,
                    help="Shows the current database specifications.",
                    use_container_width=True,
                )

                st.page_link(
                    label="View & Edit Tables",
                    page="./pages/edit-database-tables.py",
                    icon="📝",
                    disabled=USERTYPE == USER,
                    help="View the participants entered in the database & edit student details",
                    use_container_width=True,
                )

                st.page_link(
                    label="View Previous Databases",
                    page="./pages/view-previous-databases.py",
                    icon="👈",
                    disabled=USERTYPE == USER,
                    help="View results and namelist from previous databases.",
                    use_container_width=True,
                )

            with connect_container:
                st.subheader("Connect", divider=True)

                st.page_link(
                    label="Chat Room",
                    page="./pages/chat-room.py",
                    icon="📧",
                    disabled=USERTYPE == USER,
                    help="Connect with other users via group chat.",
                    use_container_width=True,
                )
                st.page_link(
                    label="About Me",
                    page="./pages/about-me.py",
                    icon="😊",
                    help="Connect with the creator of the application.",
                    use_container_width=True,
                )


def get_authenticated_no_database_pages():
    USERTYPE = st.session_state["user_info"]["user_type"]

    with st.sidebar:
        st.image("./assets/long-icon.png", use_column_width=True)
        menu_container = st.container(border=True)
        with menu_container:
            st.subheader("Navigation Menu", divider=True)
            st.page_link(
                page="./main.py", label="Home", icon="🏡", use_container_width=True
            )
            st.page_link(
                page="./pages/new-database.py",
                label="New Database",
                icon="🚀",
                use_container_width=True,
                disabled=USERTYPE != "admin",
            )
            st.page_link(
                label="View Previous",
                page="./pages/view-previous-databases.py",
                icon="⏮️",
                use_container_width=True,
                disabled=USERTYPE == "user",
            )
            st.page_link(
                page="./pages/manage-users.py",
                label="Manage Users",
                icon="🧔‍♂️",
                use_container_width=True,
                disabled=USERTYPE != "admin",
            )
            st.page_link(
                page="./pages/about-me.py",
                label="About Me",
                icon="🧑‍💻",
                use_container_width=True,
            )


def get_unauthenticated_pages():
    with st.sidebar:
        st.image("./assets/long-icon.png", use_column_width=True)
        with st.container(border=True):
            st.title("Navigation Menu")
            st.page_link(
                page="./main.py", label="Home", icon="🏡", use_container_width=True
            )


def show_go_back_to_home_in_sidebar():
    with st.sidebar:
        st.image("./assets/long-icon.png", use_column_width=True)
        with st.container(border=True):
            st.subheader("Navigation Menu", divider=True)
            st.page_link(
                label="Go to Home",
                page="main.py",
                icon="🏠",
                help="View the main page of the application.",
                use_container_width=True,
            )


def go_to_home_page():
    st.switch_page("main.py")
