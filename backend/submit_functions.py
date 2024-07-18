from time import sleep
from pandas import DataFrame
import streamlit as st
from backend.database_reader import *
from backend.sqlite_connections import *
from components.messages import show_success_message


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

def push_judgement_to_participant_table(df:DataFrame, JUDGELABELS):
    data = df.to_dict(orient="records")
    with SQliteConnectCursor() as cursor:
        query = """
        --sql
        UPDATE PARTICIPANT
        SET TOTAL_MARKS = ?,
        GRADE = ?,
        RANK = ?,
        DISQUALIFIED = ?,
        REMARKS = ?

        WHERE ADMISSION_NUMBER = ?
        ;
        """
        
        for rec in data:

            cursor.execute(query, (rec["TOTAL_MARKS"], rec["GRADE"], rec["RANK"],rec["DISQUALIFIED"], rec["REMARKS"], rec["ADMISSION_NUMBER"]))
            for judge in JUDGELABELS:
                Q2 = F"""
                --sql
                UPDATE PARTICIPANT SET {judge} = ? WHERE ADMISSION_NUMBER = ?
                ;
                """
                cursor.execute(Q2, (rec[judge], rec["ADMISSION_NUMBER"]))
        st.toast("The data has been updated at the server", icon="✅")

def update_student_details_to_student_table(admission_number, name, class_, division, house,category):
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