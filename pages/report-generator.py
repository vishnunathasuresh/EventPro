import streamlit as st
from backend.documents_generator import ReportGenerator
from backend.file_operations import get_current_database_path
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration
from backend.database_reader import DatabaseFetch, DatabaseFetchDataframe


page_configuration("📝", "Report Generation")
show_go_back_to_home_in_sidebar()


def main() -> None:
    st.title("Report Generation")
    st.divider()

    view_table_container = st.container(border=True)
    options_container = st.container(border=True)

    with view_table_container:
        show_table_with_particular_event_and_category()

    with options_container:
        show_report_generation_content()


def show_table_with_particular_event_and_category():
    category = st.selectbox(label="Choose the Category", options=CATEGORIES)
    event = st.selectbox(
        label="Select the Event",
        options=EVENTS,
    )
    if category != "" and event != "":
        data = df_fetch.get_participants_from_event_category_df(category, event)
        st.dataframe(data=data, hide_index=True, use_container_width=True)


def show_report_generation_content():
    disabled_condition = False
    category_based_report_needed = st.toggle(
        label="Category based report", disabled=disabled_condition
    )

    judgement_sheet_needed = st.toggle(
        label="Judgement sheet required", disabled=disabled_condition
    )

    st.image("./assets/report-structure.png", width=500)

    submit_and_create_reports = st.button(label="Create Reports", type="primary")
    if submit_and_create_reports:
        with st.spinner(
            "Reports are being generated... Do not press any key... Please Wait"
        ):
            disabled_condition = True
            report_generator = ReportGenerator(
                category_based_report_needed, judgement_sheet_needed
            )
            report_generator.generate()
        st.toast("Reports generated successfully", icon="✅")
        disabled_condition = False


fetch = DatabaseFetch()
df_fetch = DatabaseFetchDataframe()
CURRENT_DATABASE_PATH = get_current_database_path()
EVENTS = fetch.get_distinct_events_in_participant_table()
CATEGORIES = fetch.get_categories()


if __name__ == "__main__":
    main()
