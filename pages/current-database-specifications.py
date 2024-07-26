import streamlit as st
from backend.database_reader import DatabaseFetch, DatabaseFetchDataframe
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


fetch = DatabaseFetch()
df_fetch = DatabaseFetchDataframe()

if __name__ == "__main__":
    main()
