import streamlit as st
from streamlit import column_config
from pandas import DataFrame
from backend.constants import CLASSES
from backend.data_processing import get_default_grades, is_any_dataframe_cell_empty
from backend.file_operations import get_parameters
from backend.sqlite_connections import DatabaseEngine
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration

page_configuration(
    "🚀", "New Database"
)
show_go_back_to_home_in_sidebar()


def main() -> None:
    st.title("🚀 New Database")
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
        
        #-------------------------------------------------
        st.subheader("Edit Grades", divider=True)
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

        #--------------------------------------------------
        st.subheader("Edit Events", divider=True)
        events_table_column_info = {
            "event": column_config.TextColumn(
                label="Event", required=True, validate="^[a-zA-Z]+$"
            )
        }
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

        #--------------------------------------------------
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
        engine = DatabaseEngine(
            database_name=database_name,
            number_of_judges=number_of_judges,
            max_marks_for_each_judge=max_marks_for_each_judge,
            min_marks_for_prize=min_marks_for_prize,
            available_events_=available_events,
            grades=grades,
            max_number_of_events = max_number_of_events,
            edited_class_category_dataframe=edited_class_category_dataframe,
            uploaded_csv=uploaded_csv
        )
        engine.create_database()

EVENTS = get_parameters()["events"]
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
