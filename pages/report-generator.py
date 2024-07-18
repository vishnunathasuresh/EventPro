import streamlit as st
from streamlit import column_config, session_state
from backend.file_operations import get_current_database_path
from components.navigation import show_go_back_to_home_in_sidebar

from components.page_configuration_component import page_configuration
from backend.database_reader import DatabaseFetch, SQliteConnectCursor,SQliteConnectConnection


page_configuration("📝", "Report Generation")
show_go_back_to_home_in_sidebar()

def get_participating_events():

    with SQliteConnectCursor() as cursor:
        cursor.execute("""
        --sql
        SELECT DISTINCT EVENT_NAME FROM PARTICIPANT
        ;
        """)
        return [house[0] for house in cursor.fetchall()]

fetch = DatabaseFetch()
CURRENT_DATABASE_PATH = get_current_database_path()
EVENTS = get_participating_events()
CATEGORIES = fetch.get_categories()


def get_labels(judge_no):
    return ', '.join(
        [f'JUDGE{num}' for num in range(1, judge_no+ 1)]
    )

def main()-> None:
    st.title("Report Generation")
    st.divider()
    

    view_table_container = st.container(border=True)
    options_container = st.container(border=True)

    with view_table_container:
        category = st.selectbox(
            label="Choose the Category",
            options=CATEGORIES
        )
        event = st.selectbox(
            label="Select the Event",
            options=EVENTS,
        )
        if category!= "" and event != "":
            data = get_dataframe_from_database(CURRENT_DATABASE_PATH,category, event)
            st.dataframe(
                data=data,
                hide_index=True,
                use_container_width=True
            )
    disabled_condition = False
    with options_container:
        category_based_report_is_required = st.toggle(
            label="Category based report",
            disabled=disabled_condition            
        )
        
        judgement_sheet_is_required = st.toggle(
            label="Judgement sheet required",
            disabled= disabled_condition
        )

        st.image("./assets/report-structure.png",width= 500)

        
        submit_and_create_reports = st.button(
            label="Create Reports",
            type='primary'
        )
        if submit_and_create_reports:
            with st.spinner("Reports are being generated... Do not press any key... Please Wait"):
                disabled_condition = True
                create_reports(
                    category_based_report_is_required,
                    judgement_sheet_is_required
                )
            st.toast("Reports generated successfully", icon="✅")
            disabled_condition = False
def get_dataframe_from_database(database, category, event):
    from pandas import read_sql
    with SQliteConnectConnection() as conn:
        query = """
        --sql
        SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND CATEGORY = ?
        AND EVENT_NAME = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        data = read_sql(
            query, conn,
            params=(category, event)
        )
        return data

def create_reports(
    category_based_report_is_required, 
    judgement_sheet_is_required
):
    from pandas import read_sql, ExcelWriter
    import os, shutil
    categories = []
    events = []
    with SQliteConnectCursor() as cursor:
        query = """
        --sql
         SELECT DISTINCT CATEGORY
         FROM STUDENT, PARTICIPANT
         WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER 
        ;
        """
        cursor.execute(query)
        categories = [cat[0] for cat in cursor.fetchall()]
        cat_eve = {}
        for category in categories:
            query = """
            --sql
            SELECT DISTINCT EVENT_NAME
            FROM STUDENT, PARTICIPANT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
            AND STUDENT.CATEGORY = ?
            ;
            """ 
            cursor.execute(query,(category,))
            events = [event[0] for event in cursor.fetchall()]
            cat_eve[category] = events
        query = """
        --sql
        SELECT NUMBER_OF_JUDGES 
        FROM PARAMETER
        ;
        """ 
        cursor.execute(query)
        judge_no = cursor.fetchone()[0]
        judge_labels = get_labels(judge_no)
        shutil.rmtree("./reports",ignore_errors= True)
        os.makedirs("./reports", exist_ok= True)
    for category in cat_eve.keys():
        os.makedirs(f"./reports/{ category }",exist_ok= True)
        with SQliteConnectConnection() as conn:
            if category_based_report_is_required:
                query = """
                --sql
                SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, GROUP_CONCAT(EVENT_NAME, ', ') AS EVENTS
                FROM STUDENT, PARTICIPANT
                WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
                AND CATEGORY = ? 
                ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
                ;
                """
                data = read_sql(query, conn, params=(category,))
                data.to_excel(
                    f"./reports/{category}/{category} - report.xlsx",
                    header=["Admission number", "Name", "Class", "Division", "House", "Events"],
                    index= False
                )
            
            for event in cat_eve[category]:
                if judgement_sheet_is_required:
                    os.makedirs(f"./reports/{category}/judgement sheets/", exist_ok= True)
                    query = f"""
                    --sql
                    SELECT '' AS CHESTNUMBER, STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, {judge_labels}, '' AS TOTAL, '' AS RANK_IF_ANY
                    FROM STUDENT, PARTICIPANT
                    WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
                    AND EVENT_NAME = ?
                    ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
                    ;
                    """
                    data = read_sql(query, conn, params=(event,))
                    data.to_excel(
                        f"./reports/{category}/judgement sheets/{category} - {event} - judgement sheet - report.xlsx",
                        header=["Chest Number","Admission number", "Name", "Class", "Division", "House"] + judge_labels.split(", ") + ["Total", "Rank"],
                        index=False
                    )

                query = f"""
                --sql
                SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, TOTAL_MARKS, RANK
                FROM STUDENT, PARTICIPANT
                WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
                AND EVENT_NAME = ?
                ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
                ;
                """
                data = read_sql(query, conn, params=(event,))
                
                data.to_excel(
                    f"./reports/{category}/{category} - {event} - report.xlsx",
                    header=["Admission number", "Name", "Class", "Division", "House"] + ["Total", "Rank"],
                    index=False
                )

    


if __name__ == '__main__':
    main()