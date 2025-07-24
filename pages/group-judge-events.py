"""
a judgement page for group events where judges can view and judge group events.
It allows judges to view the group events, assign marks to each group, and submit their judgement.
a group event is an event where multiple participants can participate as a group.
each grp has same house. 
that is how the group is formed.
so when a group event is judged, the marks are assigned to houses.
each member gets the same marks as the group and same grade and rank.
this is just an easier way to mark events where multiple participants can participate as a group.
"""
import streamlit as st
from streamlit import session_state
from pandas import DataFrame, read_sql
from backend.database_reader import DatabaseFetch
from backend.file_operations import get_current_database_path
from backend.sqlite_connections import SQliteConnectConnection, SQliteConnectCursor
from backend.submit_functions import push_judgement_to_participant_table
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration

page_configuration("🎯", "Judge Group Events")
show_go_back_to_home_in_sidebar()

def get_group_events_from_category(category):
    """
    fetches the group events from the database based on the category selected.
    """
    with SQliteConnectCursor() as cursor:
        query = f"""
        --sql
        SELECT DISTINCT EVENT_NAME 
            FROM PARTICIPANT,STUDENT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
            AND STUDENT.CATEGORY = ?
            ;
        """
        cursor.execute(query, (category,))
        data = [row[0] for row in cursor.fetchall()]
    return data

def submit_group_judgement(processed_dataframe: DataFrame, judge_labels: list, event_name: str):
    """
    Submit group judgement by updating individual participant records.
    Each participant in a house gets the same marks as their house.
    """
    try:
        # Get individual student data from session state
        individual_data = st.session_state.get('original_individual_data')
        if individual_data is None:
            st.error("Error: Individual participant data not found. Please refresh and try again.")
            return
        
        # Merge house judgement data with individual participant data
        final_data = individual_data.merge(
            processed_dataframe[["HOUSE"] + judge_labels + ["TOTAL_MARKS", "GRADE", "RANK", "DISQUALIFIED", "REMARKS"]], 
            on="HOUSE", 
            how="left"
        )
        
        # Submit to participant table using the existing function
        push_judgement_to_participant_table(final_data, judge_labels, event_name)
        
    except Exception as e:
        st.error(f"Error submitting group judgement: {str(e)}")


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
        EVENTS = get_group_events_from_category(category_selected)
        event_selected = st.selectbox(
            label="Select the Event", options=EVENTS, index=0, key="judgement_event"
        )
        if event_selected is not None:
            st.subheader("Current Data", divider=True)
            st.dataframe(
                display_table(category_selected, event_selected),
                hide_index=True,
                use_container_width=True,
                height=TABLE_MAX_HEIGHT,
            )
    
    
    st.session_state.original_df = fetch_data(category_selected, event_selected)
    if event_selected is not None:
        
        with table_container:
            st.subheader(
                f"✏️ Marks Updation Sheet for :blue[{str(category_selected).title()} - {event_selected}]",
                divider=True,
            )
            
            """
            create a data editor with house name, 
            """

            edited_df = st.data_editor(
                data=st.session_state.original_df,
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

            processed_dataframe = process_dataframe(edited_df, st.session_state.get('original_individual_data', st.session_state.original_df))
            st.dataframe(
                processed_dataframe,
                hide_index=True,
                use_container_width=True,
                height=TABLE_MAX_HEIGHT,
            )

            submit_judgement = st.button(
                "Submit Changes",
                type="primary",  # type:ignore
            )

            if submit_judgement:
                submit_group_judgement(processed_dataframe, JUDGELABELS, event_selected)

def display_table(category_selected, event_selected):
    with SQliteConnectCursor() as cursor:
        query = f"""
        --sql
        SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, TOTAL_MARKS, GRADE, RANK, DISQUALIFIED, REMARKS
        FROM STUDENT, PARTICIPANT 
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND CATEGORY = '{category_selected}'
        AND EVENT_NAME = '{event_selected}'
        ;
        """
        data = read_sql(query, cursor.connection)
    return data


def get_column_info():
    """
    returns the column information for the data editor.
    house, judges{1-NUMBER_OF_JUDGES}, total, grade, disqualified, remarks
    where house is the house name, judges are the marks given by each judge,
    total is the total marks given by all judges, grade is the grade assigned based on total marks,
    disqualified is a checkbox to mark if the group is disqualified, and remarks is a text input for any remarks.
    The column information is used to create the data editor for the judgement page.
    
    """
    admno_name_class_division_column_info = {
        "HOUSE" : st.column_config.TextColumn(
            "House",
            required=True,
        ),
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


def process_dataframe(dataframe: DataFrame, original_df: DataFrame):
    """
    processes the dataframe to calculate total marks, grade, and rank for each group.
    it adds the marks given by each judge, calculates the total marks,
    assigns a grade based on the total marks, and ranks the groups based on their total marks
    assigns mark to all the individuals in the group.
    It also handles disqualification and consolation prizes.
    add name, id, cl from orginal_df to dataframe on the basis of house column
    """
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

    # add admn_no, name, class and division column and assign marks as per the individuals house
    # Merge with individual data to show all participants with their house's marks
    if hasattr(st.session_state, 'original_individual_data') and st.session_state.original_individual_data is not None:
        individual_data = st.session_state.original_individual_data
        df = individual_data.merge(
            df[["HOUSE"] + JUDGELABELS + ["TOTAL_MARKS", "GRADE", "RANK", "DISQUALIFIED", "REMARKS"]], 
            on="HOUSE", 
            how="left"
        )
    else:
        # Fallback: merge with original_df if available
        df = df.merge(original_df[["ADMISSION_NUMBER", "STUDENT_NAME", "CLASS", "DIVISION", "HOUSE"]], on="HOUSE", how="left")


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
    """
    Fetch group data for group events, aggregated by house.
    For group events, we need house-level data, not individual student data.
    """
    with SQliteConnectConnection() as conn:
        # First get the original individual data for later merging
        original_query = f"""
        --sql
        SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE
        FROM STUDENT, PARTICIPANT 
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND CATEGORY = '{category}' 
        AND EVENT_NAME = '{event}'
        ;
        """
        original_data = read_sql(original_query, conn)
        
        # Store original data in session state for later use
        st.session_state.original_individual_data = original_data
        
        # Get unique houses with their judging data
        house_query = f"""
        --sql
        SELECT DISTINCT HOUSE, {", ".join([f"0 as {judge}" for judge in JUDGELABELS])}, 
               0 as DISQUALIFIED, '' as REMARKS
        FROM STUDENT, PARTICIPANT 
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND CATEGORY = '{category}' 
        AND EVENT_NAME = '{event}'
        ;
        """
        house_data = read_sql(house_query, conn)
    return house_data


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
DISABLED_COLUMNS_JUDGEMENT_TABLE = ["HOUSE"]  # Only house column should be disabled for group events
GRADE_MINMARKS = get_grades_minmarks()


if __name__ == "__main__":
    main()


