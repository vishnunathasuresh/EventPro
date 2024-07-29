from altair import Axis
import streamlit as st
from streamlit import session_state
from pandas import DataFrame, read_sql
from backend.database_reader import DatabaseFetch
from backend.file_operations import get_current_database_path
from backend.sqlite_connections import SQliteConnectConnection, SQliteConnectCursor
from backend.submit_functions import push_judgement_to_participant_table
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration


page_configuration("🎯", "Judge Events")
show_go_back_to_home_in_sidebar()


def main() -> None:
    st.title("Judgement")
    st.divider()

    column_info = get_column_info()

    event_selection_container = st.container(border=True)
    table_container = st.container(border=True)
    final_sheet_view_container = st.container(border=True)

    with event_selection_container:
        category_selected = st.selectbox(
            label="Select the Category",
            options=CATEGORIES,
            index=0,
            key="judgement_category",
        )
        EVENTS = fetch.get_events_from_category(category_selected)
        event_selected = st.selectbox(
            label="Select the Event", options=EVENTS, index=0, key="judgement_event"
        )
    st.session_state.orginal_df = fetch_data(category_selected, event_selected)
    if event_selected is not None:
        with table_container:
            st.subheader(
                f"✏️ Marks Updation Sheet for :blue[{str(category_selected).title()} - {event_selected}]",
                divider=True,
            )

            edited_df = st.data_editor(
                data=st.session_state.orginal_df,
                num_rows="fixed",
                key="edited_df",
                use_container_width=True,
                hide_index=True,
                disabled=DISABLED_COLUMNS_JUDGEMENT_TABLE,
                column_config=column_info,
                height=TABLE_MAX_HEIGHT,
            )

        with final_sheet_view_container:
            st.subheader(
                f"📝 Final Judgement Sheet for :orange[{str(category_selected).title()} - {event_selected}]",
                divider=True,
            )
            st.toggle("Consolation prize Allowed", key="consolation_allowed")
            st.number_input(
                "The minimum marks for awarding a prize (INCLUSIVE)",
                min_value=1,
                max_value=NUMBER_OF_JUDGES * MAX_MARKS_FOR_ONE_JUDGE,
                step=1,
                value=MIN_MARKS_FOR_PRIZE,
                key="min_marks_for_prize",
            )

            processed_dataframe = process_dataframe(edited_df)
            st.dataframe(
                processed_dataframe,
                hide_index=True,
                use_container_width=True,
                height=TABLE_MAX_HEIGHT,
            )

            disabled_submit_judgement_condition = (
                edited_df[edited_df["DISQUALIFIED"] == False].isnull().values.any()
            )

            submit_judgement = st.button(
                "Submit Changes",
                disabled=disabled_submit_judgement_condition,  # type: ignore
                type="primary",  # type:ignore
            )

            if submit_judgement:
                push_judgement_to_participant_table(processed_dataframe, JUDGELABELS)


def get_column_info():
    admno_name_class_division_column_info = {
        "ADMISSION_NUMBER": "Admission Number",
        "STUDENT_NAME": "Name",
        "CLASS": "Class",
        "DIVISION": "Division",
    }
    judges_column_info = {
        f"JUDGE{number}": st.column_config.NumberColumn(
            f"Judge {number}",
            required=True,
            max_value=MAX_MARKS_FOR_ONE_JUDGE,
            min_value=0,
        )
        for number in range(1, NUMBER_OF_JUDGES + 1)
    }
    total_grade_disqualifiedstatus_remarks_column_info = {
        "TOTAL_MARKS": st.column_config.NumberColumn(
            "Total",
            disabled=True,
            min_value=0,
        ),
        "GRADE": "Grade",
        "DISQUALIFIED": st.column_config.CheckboxColumn("Disqualified"),
        "REMARKS": "Remarks if Any",
    }

    admno_name_class_division_column_info.update(judges_column_info)  # type: ignore
    admno_name_class_division_column_info.update(
        total_grade_disqualifiedstatus_remarks_column_info
    )
    final_column_info = admno_name_class_division_column_info.copy()
    return final_column_info


def get_grades_minmarks():
    with SQliteConnectCursor() as cursor:
        query = """
        --sql
        SELECT GRADE, MIN_MARKS FROM GRADE_MARKS ORDER BY MIN_MARKS ASC
        ;
        """
        cursor.execute(query)
        data = dict(cursor.fetchall())
    return data


def process_dataframe(dataframe: DataFrame):
    dataframe = dataframe.copy()
    columns_to_add = JUDGELABELS
    df = dataframe

    # calculate total marks of all students
    df["TOTAL_MARKS"] = df[columns_to_add].sum(axis=1)

    # grade all students based on their total-marks
    df["GRADE"] = df["TOTAL_MARKS"].apply(assign_grade)

    # rank un-disqualified students on the basis of their total-marks
    df["RANK"] = df[df["DISQUALIFIED"] == False]["TOTAL_MARKS"].rank(
        method="dense", ascending=False
    )
    df["RANK"] = df["RANK"].fillna(-1)

    # beautify and turn the decimal rank denoted by .rank() method to an appropriate string
    df["RANK"] = df[["RANK", "DISQUALIFIED"]].apply(assign_rank, axis=1)  # type: ignore

    df["RANK"] = df[["RANK", "TOTAL_MARKS"]].apply(
        evaluate_consolation, axis=1  # type: ignore
    )

    # sort students on the basis of total-marks in descending order
    df.sort_values(by="TOTAL_MARKS", ascending=False, inplace=False)
    return df


def assign_grade(marks):
    bigger_numbers = [n for n in GRADE_MINMARKS.values() if n > marks]
    if bigger_numbers == []:
        max_num = max(GRADE_MINMARKS.values())
    else:
        max_num = min(bigger_numbers)

    for key, min_marks in GRADE_MINMARKS.items():
        if min_marks == max_num:
            grade = key
            break

    return grade


def evaluate_consolation(x):
    if (x["RANK"] is not None) and (
        x["TOTAL_MARKS"] < session_state.min_marks_for_prize
        and session_state.consolation_allowed
    ):
        return "CONSOLATION"  # consolation RANK IF RANK IS 1,2,3 BUT LESS THAN MIN_MARKS_FOR_PRIZE
    elif x["TOTAL_MARKS"] < session_state.min_marks_for_prize:
        return None
    else:
        return x["RANK"]  # NONE OR FIRST, SECOND OR THIRD


def assign_rank(x):
    if x["DISQUALIFIED"] == False:
        if x["RANK"] == 1.0:
            return "FIRST"
        elif x["RANK"] == 2.0:
            return "SECOND"
        elif x["RANK"] == 3.0:
            return "THIRD"
        else:
            return None
    else:
        return None


def fetch_data(category, event):
    with SQliteConnectConnection() as conn:
        query = f"""
        --sql
        SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, {", ".join(JUDGELABELS)}, DISQUALIFIED, REMARKS
        FROM STUDENT, PARTICIPANT 
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND CATEGORY = '{category}' 
        AND EVENT_NAME = '{event}'
        ;
        """
        data = read_sql(query, conn)
    return data


@st.cache_data
def get_class_category_from(database_path):
    with SQliteConnectCursor() as cursor:
        query = """
        --sql
        SELECT CLASS, CATEGORY FROM CLASS_CATEGORY
        ;
        """
        cursor.execute(query)
        data = dict(cursor.fetchall())
    return data


def get_params_from_database():
    with SQliteConnectCursor() as cursor:
        query = """
        --sql
        SELECT  NUMBER_OF_JUDGES, MAX_MARKS_FOR_EACH_JUDGE ,MIN_MARKS_FOR_PRIZE
        FROM PARAMETER
        ;
        """
        cursor.execute(query)
        TUP = cursor.fetchone()

    return TUP


fetch = DatabaseFetch()
CURRENT_DATABASE_PATH = get_current_database_path()
CLASS_CATEGORY = get_class_category_from(database_path=CURRENT_DATABASE_PATH)
CATEGORIES = list(set(CLASS_CATEGORY.values()))
CATEGORIES.sort()
(
    NUMBER_OF_JUDGES,
    MAX_MARKS_FOR_ONE_JUDGE,
    MIN_MARKS_FOR_PRIZE,
) = get_params_from_database()
JUDGELABELS = [f"JUDGE{number}" for number in range(1, NUMBER_OF_JUDGES + 1)]

TABLE_MAX_HEIGHT = None
DISABLED_COLUMNS_JUDGEMENT_TABLE = ["ADMISSION_NUMBER", "STUDENT_NAME", "CLASS"]
GRADE_MINMARKS = get_grades_minmarks()


if __name__ == "__main__":
    main()
