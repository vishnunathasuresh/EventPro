import streamlit as st

from backend.database_reader import *
from backend.sqlite_connections import *


def submit_student_details_to_participant_table(
    admission_number,
    house_selected,
    events_selected,
    event_column,
):
    if house_selected == 'No House':
        house_selected = None
    
    if events_selected != []:pass
    def submit():
        with SQliteConnectCursor(get_current_database_path()) as cursor:
            query = """
            --sql
            DELETE FROM PARTICIPANT WHERE ADMISSION_NUMBER = ?
            ;
            """
            cursor.execute(query, (admission_number,))
        
        with SQliteConnectCursor(get_current_database_path()) as cursor:
            query = """
            --sql
            UPDATE STUDENT 
            SET HOUSE = ?
            WHERE ADMISSION_NUMBER = ?
            ;
            """
            cursor.execute(query, (house_selected, admission_number))
            st.toast("House : "+ str(house_selected), icon="✨")
            
            for event in events_selected:

                query = """
                --sql
                INSERT INTO PARTICIPANT (ADMISSION_NUMBER, EVENT_NAME)
                VALUES (?, ?)
                ;
                """
                cursor.execute(query, (admission_number, event))
                st.toast(
                    "Participant has been registered for " + event,
                    icon="➡️",
                )


    with event_column:
        with st.spinner("Updating Database..."):
            submit()

        
        st.toast(
            "The student details has been submitted to the database successfully",
            icon="✅",
        )