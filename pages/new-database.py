import streamlit as st
from streamlit import column_config
from pandas import DataFrame
from io import StringIO
from csv import reader as csv_reader
import os
from backend.constants import DATABASE_DIRECTORY_PATH, DATABASE_EXTENSION, INTERNALS_PATH
from backend.data_processing import get_class_and_division, is_any_dataframe_cell_empty
from backend.file_operations import get_parameters
from backend.sqlite_connections import SQliteConnectCursor
from components.messages import show_error_message, show_general_message
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration

page_configuration(
    "🚀", "New Database"
)
show_go_back_to_home_in_sidebar()


def main() -> None:
    st.title("New Database")
    st.divider()

    create_database_container = st.container(border=True)
    with create_database_container:
        database_name = st.text_input(
            label="What should be the database name?",
            placeholder="eg. Memories",
        )

        max_marks_for_each_judge = st.number_input(
            "The maximum marks a Judge can Award",
            min_value=5,
            step=1,
            value=10,
            max_value=1000,
        )

        number_of_judges = st.number_input(
            "Enter the number of judges for each event",
            value=3,
            step=1,
            max_value=10,
            min_value=1,
        )

        total_marks = number_of_judges * max_marks_for_each_judge

        grades_table_column_info = {
            "grade": column_config.Column(disabled=True, label="Grade"),
            "min_marks": column_config.NumberColumn(
                label="Maximum Marks",
                required=True,
                step=1,
                max_value=0.4 * total_marks,
                min_value=0,
            ),
        }
        default_grades = get_default_grades(total_marks)
        st.subheader("Edit Grades", divider=True)
        grades = st.data_editor(
            data=default_grades,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config=grades_table_column_info,
        )

        min_marks_for_prize = st.number_input(
            "Minimum marks for Price attainment",
            min_value=0,
            max_value=total_marks,
            value=int(0.75 * total_marks),
            step=1,
        )

        

        events_table_column_info = {
            "event": column_config.TextColumn(
                label="Event", required=True, validate="^[a-zA-Z]+$"
            )
        }
        st.subheader("Edit Events", divider=True)
        max_number_of_events=st.number_input(
            "Enter the number of events a student can participate in",
            value=5,
            step=1,
            max_value=len(EVENTS),
            min_value=1,
        )
        available_events = st.data_editor(
            data={"Event": EVENTS},
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            column_config=events_table_column_info,
        )

        
        categories_and_classes_container = st.container(border=True)
        with categories_and_classes_container:
            st.subheader("Categories and Classes Allotment", divider=True)

            class_category_dict = {
                "class": CLASSES,
                "category": [None for _ in range(len(CLASSES))],
            }
            number_of_categories = st.number_input(
                label="Number of Categories",
                min_value=2,
                max_value=10,
                value=4,
                step=1,
            )
            categories = [
                f"category {number}" for number in range(1, int(number_of_categories) + 1)
            ]

            categories_and_classes_table_container = st.container()
            with categories_and_classes_table_container:
                edited_class_category_column_info = {
                    "class": column_config.TextColumn(label="Class", disabled=True),
                    "category": column_config.SelectboxColumn(
                        label="Category", required=True, options=categories
                    ),
                }
                edited_class_category_dataframe = st.data_editor(
                    data=DataFrame(class_category_dict),
                    use_container_width=True,
                    num_rows="fixed",
                    column_config=edited_class_category_column_info,
                    hide_index=True
                )


                uploaded_csv = st.file_uploader(
                    label="Upload Student Data",
                    type="csv",
                    accept_multiple_files=False,
                    help=CSV_HELP,
                )
                
                

                    
    all_parameters_are_set = (
        database_name != ""
        and max_marks_for_each_judge
        and number_of_judges
        and max_number_of_events
        and min_marks_for_prize
        and not is_any_dataframe_cell_empty(DataFrame(available_events))
        and not is_any_dataframe_cell_empty(DataFrame(grades))
        and not is_any_dataframe_cell_empty(edited_class_category_dataframe)
        and uploaded_csv is not None
    )

    submit_and_create_database = st.button(
        "Submit and Create Database",
        type="primary",
        disabled=not all_parameters_are_set,
    )
    if submit_and_create_database:
        create_new_database(
            database_name=database_name,
            max_marks_for_each_judge=max_marks_for_each_judge,
            number_of_judges=number_of_judges,
            min_marks_for_prize=min_marks_for_prize,
            available_events_=available_events,
            grades=grades,
            max_number_of_events = max_number_of_events,
            edited_class_category_dataframe=edited_class_category_dataframe,
            uploaded_csv=uploaded_csv
        )

def get_class_category_dict_from(dataframe: DataFrame):
    dictionary = dataframe.to_dict()
    final_dict = {}
    classes = dictionary["class"]
    categories = dictionary["category"]
    for index in classes.keys():
        final_dict[classes[index]] = categories[index]
    return final_dict

def dataframe_to_category_to_class_list_dict(dataframe, categories):
    data = dataframe.to_dict(
        orient="tight",
    )["data"]
    class_category_allocated_dictionary = {category: [] for category in categories}
    for record in data:
        class_, category = record
        class_category_allocated_dictionary[category].append(class_)
    return class_category_allocated_dictionary





def create_new_database(
    database_name,
    number_of_judges,
    max_marks_for_each_judge,
    min_marks_for_prize,
    available_events_,
    grades,
    max_number_of_events,
    edited_class_category_dataframe,
    uploaded_csv
):
    from datetime import datetime
    current_year = datetime.now().year
    try:
        
        available_events:list[str] = list(set([event.title() for event in available_events_["Event"]]))
        available_events = [(event,) for event in available_events] # type: ignore
        grades_min_marks =process_grade_marks(grades)
        class_category_dict = get_class_category_dict_from(edited_class_category_dataframe)
        student_data = process_student_data_from(uploaded_csv, class_category_dict)
        database_file_path = DATABASE_DIRECTORY_PATH+f"{database_name}-{current_year}"+ DATABASE_EXTENSION

        if os.path.exists(database_file_path):
            os.remove(path=database_file_path)

        with SQliteConnectCursor(database_file_path) as cursor:
            # events
            query1 = """
            --sql
            CREATE TABLE EVENT_NAME (EVENT_NAME TEXT)
            ;
            """
            query2 ="""
            --sql
            INSERT INTO EVENT_NAME VALUES (?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, available_events)
            
            # PARAMETERS
            query1 = """
            --sql
            CREATE TABLE PARAMETER (
                DATABASENAME TEXT, 
                NUMBER_OF_JUDGES INT, 
                MAX_MARKS_FOR_EACH_JUDGE INT, 
                MIN_MARKS_FOR_PRIZE INT, 
                TOTAL_MARKS,
                RESULTS_READY BOOLEAN,
                MAXIMUM_EVENTS_FOR_PARTICIPATION INT
            )
            ;
            """
            query2 = """
            --sql
            INSERT INTO PARAMETER VALUES (?, ?, ?, ?, ?, ?, ?)
            ;
            """
            cursor.execute(query1)
            cursor.execute(
                query2, 
                (
                    f"{database_name}-{current_year}.eventpro.db",
                    number_of_judges, 
                    max_marks_for_each_judge,
                    min_marks_for_prize,
                    max_marks_for_each_judge * number_of_judges,
                    False,
                    max_number_of_events
                ))
            
            #class-category
            query1 = """
            --sql
            CREATE TABLE CLASS_CATEGORY (
                CLASS TEXT,
                CATEGORY TEXT
            )
            ;
            """
            query2 = """
            --sql
            INSERT INTO CLASS_CATEGORY VALUES (?, ?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, list(class_category_dict.items()))

            #grade_marks
            query1 = """
            --sql
            CREATE TABLE GRADE_MARKS(
                GRADE TEXT,
                MIN_MARKS INT
            )
            ;
            """
            query2 ="""
            --sql
            INSERT INTO GRADE_MARKS VALUES (?, ?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, list(grades_min_marks.items()))

            # STUDENT
            query1 = """
            --sql
            CREATE TABLE STUDENT(
                ADMISSION_NUMBER TEXT PRIMARY KEY,
                STUDENT_NAME TEXT,
                CLASS TEXT,
                DIVISION TEXT,
                HOUSE TEXT,
                CATEGORY TEXT
            )
            ;
            """
            query2 = """
            --sql
            INSERT INTO STUDENT VALUES (?,?,?,?,?,?)
            ;
            """
            cursor.execute(query1)
            student_data = list(set(student_data))
            cursor.executemany(query2, student_data)
            

            #houses
            query1 = """
            --sql
            CREATE TABLE HOUSE(HOUSE TEXT)
            ;
            """
            query2 = """
            --sql
            INSERT INTO HOUSE VALUES (?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, get_houses())

            #participant
            query1 = f"""
            --sql
            CREATE TABLE PARTICIPANT(
                ADMISSION_NUMBER TEXT,
                EVENT_NAME TEXT ,
                {', '.join([f'JUDGE{NUM+1} INT' for NUM in range(number_of_judges)])},
                TOTAL_MARKS INT,
                GRADE INT,
                RANK TEXT,
                DISQUALIFIED BOOLEAN DEFAULT 0,
                REMARKS TEXT DEFAULT "",
                PRIMARY KEY(ADMISSION_NUMBER, EVENT_NAME)
            )
            ;
            """
            cursor.execute(query1)
            

            show_general_message("Database created successfully")
            st.switch_page("main.py")







    except Exception as e:
        show_error_message(e)

def get_houses():
    from yaml import safe_load

    with open(INTERNALS_PATH+"default_parameters.yaml") as file:
        houses = safe_load(file)["houses"]
        houses = [(house,) for house in houses]
    return houses


def get_default_grades(TOTAL_MARKS):
    if TOTAL_MARKS:
        return [
            {
                "grade": "A",
                "min_marks": int(0.85 * TOTAL_MARKS),
            },
            {
                "grade": "B",
                "min_marks": int(0.75 * TOTAL_MARKS),
            },
            {
                "grade": "C",
                "min_marks": int(0.65 * TOTAL_MARKS),
            },
            {
                "grade": "D",
                "min_marks": int(0.55 * TOTAL_MARKS),
            },
            {
                "grade": "E",
                "min_marks": int(0.45 * TOTAL_MARKS),
            },
            {
                "grade": "F",
                "min_marks": int(0.35 * TOTAL_MARKS),
            },
        ]

def process_grade_marks(dataframe):
    final_dict = {}
    for dictionary in dataframe:
        final_dict[dictionary["grade"].upper()] = dictionary["min_marks"]
    return final_dict

def process_student_data_from(csv_data, class_category_dict):
    try:
        student_data = []
        file = StringIO(csv_data.getvalue().decode("utf-8"))
        admn_nos = tuple()
        for row in csv_reader(file):
            admn_no = row[0]
            name = row[1]
            class_, division = get_class_and_division(row[2])
            category = class_category_dict[class_]
            if admn_no not in admn_nos:
                student_data.append((admn_no, name.title(), class_, division.upper(), None, category))
                admn_nos = admn_nos = (admn_no,)
        return student_data
    except:
        raise SyntaxError("The csv file does not meet the syntax required.")


EVENTS = get_parameters()["events"]
CLASSES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "lkg", "ukg"]
CSV_HELP = """
- Upload student data as a csv file.
- The csv file should be less than 200MB.
- The csv should contain student data from all classes.
- The csv file should be devoid of headers and should contain data in the order :
**ADMISSION_NUMBER , NAME , CLASS-DIVISION(eg.XII-D)
- example entry : **S8559, Vishnunath A Suresh, XII-D**
- Special note : 
    - The class-division should be exactly formatted as the above.
The CLASS and DIVISION should be seperated by "-".
    - The House can only be entered during participant registration.
    - The Headers should be ensured to be removed to remove unnecessary errors during other operations.
"""

if __name__ == "__main__":
    main()
