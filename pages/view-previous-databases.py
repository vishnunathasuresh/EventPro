import streamlit as st
import os
from pandas import read_sql
from backend.file_operations import get_current_database_path
from backend.sqlite_connections import SQliteConnectConnection, SQliteConnectCursor
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration
from backend.constants import SAVED_DATABASES_DIRECTORY_PATH, DATABASE_EXTENSION


DATABASE_PATH = get_current_database_path()

page_configuration("👈", "View Previous Databases")
show_go_back_to_home_in_sidebar()


ALL_ARCHIVED_FILE_NAMES: list[str] = [
    file
    for file in os.listdir(SAVED_DATABASES_DIRECTORY_PATH)
    if file.endswith(DATABASE_EXTENSION)
]
NAMES_PATHS_DICTIONARY = {
    file.removesuffix(DATABASE_EXTENSION): SAVED_DATABASES_DIRECTORY_PATH + file
    for file in ALL_ARCHIVED_FILE_NAMES
}


def main() -> None:
    st.title("🔍 View Databases")
    st.divider()

    disabled_condition = NAMES_PATHS_DICTIONARY == {}
    if disabled_condition:
        st.info("There is no previous database records available.", icon="😑")
    selected_database = st.selectbox(
        label="Select the database to show the tables",
        options=list(NAMES_PATHS_DICTIONARY.keys()),
        placeholder="Database name",
        index=0,
        disabled=disabled_condition,
    )

    if selected_database is not None:
        student_dataframe = get_dataframes_from(
            databasepath=NAMES_PATHS_DICTIONARY[selected_database]
        )

        student_table_container = st.container(border=True)
        participant_table_container = st.container(border=True)

        with student_table_container:
            st.subheader(body="Student Table", divider=True)
            st.dataframe(
                data=student_dataframe, use_container_width=True, hide_index=True
            )

        with participant_table_container:
            st.subheader(body="Participant Table", divider=True)
            cat = st.selectbox(
                label="Select Category",
                index=0,
                options=get_categories_from(NAMES_PATHS_DICTIONARY[selected_database]),
                disabled=disabled_condition,
            )

            event = st.selectbox(
                label="Select Event",
                index=0,
                options=get_events_from(NAMES_PATHS_DICTIONARY[selected_database]),
                disabled=disabled_condition,
            )
            participant_dataframe = get_participant_df(
                cat, event, NAMES_PATHS_DICTIONARY[selected_database]
            )
            st.dataframe(
                data=participant_dataframe, use_container_width=True, hide_index=True
            )


def get_dataframes_from(databasepath: str):
    with SQliteConnectConnection(databasepath) as conn:
        student_dataframe = read_sql("SELECT * FROM STUDENT", conn)

    return student_dataframe


def get_categories_from(path):
    with SQliteConnectCursor(path) as cursor:
        cursor.execute(
            """
        --sql
        SELECT DISTINCT CATEGORY FROM CLASS_CATEGORY
        ;
        """
        )
        return [a[0] for a in cursor.fetchall()]


def get_events_from(path):
    with SQliteConnectCursor(path) as cursor:
        cursor.execute(
            """
        --sql
        SELECT DISTINCT EVENT_NAME FROM EVENT_NAME
        ;
        """
        )
        return [a[0] for a in cursor.fetchall()]


def get_participant_df(category, event, selected_database_path):
    query = """
    --sql
    SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, TOTAL_MARKS, GRADE, RANK, DISQUALIFIED, REMARKS
    FROM PARTICIPANT, STUDENT
    WHERE PARTICIPANT.ADMISSION_NUMBER = STUDENT.ADMISSION_NUMBER
    AND CATEGORY = ?
    AND EVENT_NAME = ?
    ORDER BY TOTAL_MARKS DESC
    ;
    """
    with SQliteConnectConnection(selected_database_path) as conn:
        dataframe = read_sql(query, conn, params=(category, event))
    return dataframe


if __name__ == "__main__":
    main()
