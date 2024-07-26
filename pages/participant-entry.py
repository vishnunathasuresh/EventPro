import streamlit as st
from streamlit import session_state
from backend.constants import *
from backend.database_reader import DatabaseFetch
from backend.data_processing import add_to_session_state
from backend.submit_functions import submit_student_details_to_participant_table
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration

page_configuration(icon="🗓️", title="Participant Entry")
show_go_back_to_home_in_sidebar()


def main() -> None:
    st.title("✒️ Participant Entry")
    st.divider()

    entry_column, event_column = st.columns([5, 7], gap="large")

    with entry_column:
        admission_number_container = st.container(border=True)
        student_info_container = st.container(border=True)
        with admission_number_container:
            admission_number_entered = st.text_input(
                label="Enter the admission number",
                key="admission_number",
                placeholder="eg: S8557",
                on_change=update_student_details,
                value=session_state.admission_number,
            )

        with student_info_container:
            show_student_details()

    with event_column:
        show_event_and_house_selection_content(admission_number_entered, event_column)


def update_student_details():
    if session_state.admission_number in ADMISSION_NOS:
        name, class_, division, house, events = fetch.get_details_of_admission_number(
            session_state.admission_number
        )
        session_state.NAME = name
        session_state.class_number = class_
        session_state.house = house
        session_state.division = division
        session_state.events_aldready_selected = events
        if house in HOUSES:
            session_state.house_index = HOUSES.index(house)
        else:
            session_state.house_index = HOUSES.index("No House")
        st.toast("Student Data has been fetched", icon="✅")
    else:
        session_state.NAME = ""
        session_state.class_number = ""
        session_state.house = ""
        session_state.division = ""
        session_state.events_aldready_selected = None
        session_state.house_index = len(HOUSES) - 1
        st.toast(
            "The admission number entered is not present in the database.", icon="❌"
        )


def show_student_details():
    st.subheader("Student info", divider=True)
    st.write("Admission number entered : ", session_state.admission_number)
    st.write("Name : ", session_state.NAME)
    st.write("Class : ", session_state.class_number)
    st.write("Division : ", session_state.division)


def show_event_and_house_selection_content(admission_number_entered, event_column):
    event_container = st.container(border=True)
    with event_container:
        st.subheader("Participation Form", divider="grey")

        house_selected = st.selectbox(
            label="Select the house of the candidate",
            index=session_state.house_index,
            options=HOUSES,
            disabled=admission_number_entered not in ADMISSION_NOS,
        )

        events_selected = st.multiselect(
            label="Select the events",
            max_selections=MAX_SELECTION_FOR_EVENTS,
            options=EVENTS,
            default=session_state.events_aldready_selected,
            disabled=admission_number_entered not in ADMISSION_NOS,
        )

        submit_participant = st.button(
            label="Submit and confirm participation",
            type="primary",
            disabled=admission_number_entered not in ADMISSION_NOS,
            use_container_width=True,
        )

    if submit_participant:
        submit_student_details_to_participant_table(
            admission_number=session_state.admission_number,
            house_selected=house_selected,
            events_selected=events_selected,
            event_column=event_column,
        )


fetch = DatabaseFetch()
HOUSES = fetch.get_houses() + ["No House"]
MAX_SELECTION_FOR_EVENTS = fetch.get_parameters()[-2]
EVENTS = fetch.get_events()

add_to_session_state(
    admission_nos=fetch.get_all_admission_numbers(),
    NAME="",
    class_number="",
    house="",
    division="",
    events_aldready_selected=None,
    house_index=len(HOUSES) - 1,
    admission_number="",
)
ADMISSION_NOS = session_state.admission_nos

if __name__ == "__main__":
    main()
