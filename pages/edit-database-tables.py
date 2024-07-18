import streamlit as st
from streamlit import session_state
from time import sleep
from pandas import DataFrame, read_sql
from backend.database_reader import DatabaseFetch,SQliteConnectConnection, SQliteConnectCursor
from components.messages import show_success_message
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration


page_configuration("✏️","View & Edit Database")
show_go_back_to_home_in_sidebar()

USER_TYPE = session_state.user_info["user_type"]
fetch = DatabaseFetch()


ALL_ADMISSION_NUMBERS = fetch.get_all_admission_numbers()

def get_student_df():
    query = """
    --sql
    SELECT ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, CATEGORY
    FROM STUDENT
    ORDER BY CLASS, DIVISION, STUDENT_NAME
    ;
    """
    with SQliteConnectConnection() as conn:
        df = read_sql(
            query, conn
        )

    return df

def get_participant_df():
    query = """
    --sql
    SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE,CATEGORY, EVENT_NAME
    FROM STUDENT, PARTICIPANT
    WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
    ORDER BY CLASS, DIVISION, STUDENT_NAME
    ;
    """
    with SQliteConnectConnection() as conn:
        df = read_sql(
            query, conn
        )

    return df 


def main()->None:
    st.title("🔍 View Current Participants")
    st.divider()

    


    # student-database-view
    student_table_container = st.container(border=True)
    with student_table_container:
        st.subheader(
            body="📌 View Student Details",
            divider=True
        )

        student_dataframe = get_student_df()
        st.dataframe(
            data = student_dataframe,
            use_container_width=True,
            hide_index=True
        )
        
    # participants-database-view
    participant_table_container = st.container(border=True)
    
    with participant_table_container:
        st.subheader("🏃‍♂️ View Participants")
        participant_dataframe = get_participant_df()
        st.dataframe(
            data = participant_dataframe,
            use_container_width=True,
            hide_index=True
        )
    
    # student-database-edit
    if USER_TYPE != "user":
        show_student_editor()
        
def show_student_editor():
    student_edit_container = st.container(border=True)
    with student_edit_container:
        st.subheader(
            body="✂️ Student Edit Details",
            divider=True,
            help="It can be used to alter the **name,class, house** and **division** of a student."
        )
        selected_admission_number = st.text_input(
            label="Enter the Admission number",
            key="temp_admission_number"
        )
        houses = fetch.get_houses() + [None]
        divisions = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        class_cat = get_class_category_dict_from_database()
        classes = list(class_cat.keys())
        if selected_admission_number in fetch.get_all_admission_numbers():
            name, class_, division, house = get_name_class_division_house_from_admission_number(selected_admission_number)
            selected_name = st.text_input(
                label="Enter the student name",
                value=name
            )
            selected_class = st.selectbox(
                label="Select the class",
                options=classes,
                index=classes.index(class_)
            )
            selected_division = st.selectbox(
                label="Select the division",
                options=divisions,
                index=divisions.index(division)
            )
            selected_house = st.selectbox(
                label="Select the House for the candidate",
                options = houses,
                index=houses.index(house)
            )
            submit_details = st.button(
                "Submit to Database",
                type="primary",
            )
            if submit_details:
                update_student_details_to_database(
                    selected_admission_number,
                    selected_name,
                    selected_class,
                    selected_division,
                    selected_house,
                    class_cat[class_]
                )
        else:
            st.warning(
                'Admission number not entered' if selected_admission_number == "" or selected_admission_number is None
                else "Admission number not in database",
                icon="😑"
            )
        
def update_student_details_to_database(admission_number, name, class_, division, house,category):
    with SQliteConnectCursor() as cursor:
        query = """
        --sql
        UPDATE STUDENT
        SET STUDENT_NAME = ?,
        CLASS = ?,
        DIVISION = ?,
        HOUSE = ?,
        CATEGORY = ?
        WHERE ADMISSION_NUMBER = ?
        ;
        """
        data = (name, class_, division, house, category, admission_number)
        cursor.execute(query, data)
    show_success_message("Successfully updated!...", icon="✅")
    sleep(2)
    st.rerun()
def get_name_class_division_house_from_admission_number(admission_number):
    with SQliteConnectCursor() as cursor:
        query = """
        --sql
        SELECT STUDENT_NAME, CLASS, DIVISION, HOUSE FROM STUDENT
        WHERE ADMISSION_NUMBER = ?
        ;
        """
        cursor.execute(query, (admission_number,))
        return cursor.fetchone()
def get_class_category_dict_from_database():

    with SQliteConnectCursor() as cursor:
        query = """
        --sql
        SELECT CLASS, CATEGORY
        FROM CLASS_CATEGORY
        ;
        """
        cursor.execute(query)
        return dict(cursor.fetchall())


if __name__ == "__main__":
    main()