from pandas import DataFrame
import streamlit as st
from backend.database_reader import (
    DatabaseFetch,
    DatabaseFetchDataframe,
    ParameterUpdator,
)
from backend.file_operations import get_current_database_name
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration


page_configuration(
    icon="📄",
    title="Current Database Specifications",
    autorefresh=True,
    refresh_interval_seconds=10,
)
show_go_back_to_home_in_sidebar()


def main() -> None:
    st.title("Current Database Specifications")
    st.divider()

    show_database_updates()
    show_parameter_info()
    show_tables()
    if st.session_state["user_info"]["user_type"] == "admin":
        edit_section()


def show_database_updates():
    number_of_students = len(fetch.get_all_admission_numbers())
    participants_number = fetch.get_participant_number()
    st.subheader("Database Updates", divider=True)
    cola, colb = st.columns(2)
    with cola:
        with st.container(border=True):
            st.metric(
                label="Number of Students",
                value=number_of_students,
                delta=number_of_students,
            )
    with colb:
        with st.container(border=True):
            st.metric(
                label="Number of Participants",
                value=participants_number,
                delta=participants_number,
            )


def show_parameter_info():
    (
        max_marks_for_each_judge,
        number_of_judges,
        min_marks_for_prize,
        max_events,
    ) = fetch.get_database_specs()

    st.subheader(str(get_current_database_name()) + " Parameters", divider=True)
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric(
                label="Database Type",
                value="SQLite",
                delta="Version 3",
                delta_color="off",
            )

    with col2:
        with st.container(border=True):
            st.metric(
                label="Maximum Marks for a Judge",
                value=max_marks_for_each_judge,
                delta=max_marks_for_each_judge,
            )
    with col3:
        with st.container(border=True):
            st.metric(
                label="Number of Judges", value=number_of_judges, delta=number_of_judges
            )
    with col4:
        with st.container(border=True):
            st.metric(
                label="Total Marks for an Event",
                value=max_marks_for_each_judge * number_of_judges,
                delta=max_marks_for_each_judge * number_of_judges,
            )
    with col5:
        with st.container(border=True):
            st.metric(
                label="Minimum Marks For Prize",
                value=min_marks_for_prize,
                delta=min_marks_for_prize,
            )
    with col6:
        with st.container(border=True):
            st.metric(
                label="Maximum Events for Participation",
                value=max_events,
                delta=max_events,
            )


def show_tables():
    available_events = {"Event name": fetch.get_events()}
    grades = df_fetch.get_grade_marks_df()
    class_category_allocated_dataframe = df_fetch.get_class_category_df()

    col7, col8 = st.columns(2)

    with col7:
        st.subheader("Category - Class Distribution", divider=True)
        st.dataframe(
            data=class_category_allocated_dataframe,
            hide_index=True,
            use_container_width=True,
        )
    with col8:
        st.subheader("Grades - Marks Criteria", divider=True)
        st.dataframe(data=grades, hide_index=True, use_container_width=True)

    st.subheader("Available events", divider=True)
    st.dataframe(data=available_events, use_container_width=True, hide_index=True)


def edit_section():
    params = fetch.get_database_specs()
    total_marks = params[0] * params[1]
    grades = df_fetch.get_grade_marks_df()
    available_events = DataFrame({"EVENT_NAME": fetch.get_events()})

    with st.container(border=True):
        st.subheader("Edit Parameters Section", divider=True)
        events_tab, grade_tab, parameter_tab = st.tabs(
            ["Edit Events", "Edit Grades", "Edit Other Parameters"]
        )
        with events_tab:
            edit_events_df: DataFrame = st.data_editor(
                data=available_events,
                column_config={
                    "EVENT_NAME": st.column_config.TextColumn(
                        label="Event name", required=True
                    )
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
            )
            if not edit_events_df.equals(available_events):
                if st.button("Update Events"):
                    push_parameters.update_events_to_parameters(edit_events_df)
        with grade_tab:
            edited_grades_df: DataFrame = st.data_editor(
                data=grades,
                column_config={
                    "GRADE": st.column_config.TextColumn(
                        label="Grade", required=True, disabled=True
                    ),
                    "MIN_MARKS": st.column_config.NumberColumn(
                        label="Min. Marks Required",
                        required=True,
                        min_value=0,
                        max_value=total_marks,
                        step=1,
                    ),
                },
                num_rows="fixed",
                use_container_width=True,
                hide_index=True,
            )
            if not edited_grades_df.equals(grades):
                if st.button("Update Grades"):
                    push_parameters.update_grades_min_marks(edited_grades_df)
        with parameter_tab:
            max_marks_for_each_judge = st.number_input(
                label="Maximum marks that can be awarded by a single judge",
                min_value=10,
                max_value=100,
                step=1,
                value=params[0],
            )
            number_of_judges = params[1]

            total_marks = number_of_judges * max_marks_for_each_judge  # type:ignore
            st.info("Total marks :" + str(total_marks), icon="✅")

            min_marks_for_prize = st.number_input(
                label="The Minimum marks to secure a prize **(inclusive)**",
                min_value=1,
                max_value=total_marks,
                step=1,
                value=params[2],
            )

            max_no_of_events = st.number_input(
                label="Maximum number of events a participant can participate in",
                min_value=1,
                max_value=total_marks,
                step=1,
                value=params[3],
            )
            if any(
                (
                    max_no_of_events != params[3],
                    min_marks_for_prize != params[2],
                    max_marks_for_each_judge != params[0],
                )
            ):
                if st.button("Update Parameters"):
                    push_parameters.update_other_parameters(
                        max_marks_for_each_judge=max_marks_for_each_judge,
                        total_marks=total_marks,
                        min_marks_for_prize=min_marks_for_prize,
                        max_no_of_events=max_no_of_events,
                    )


fetch = DatabaseFetch()
df_fetch = DatabaseFetchDataframe()
push_parameters = ParameterUpdator()

if __name__ == "__main__":
    main()
