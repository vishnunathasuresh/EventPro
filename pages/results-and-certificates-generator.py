import streamlit as st
from backend.ResultsGenerator import CertificateGenerator
from backend.database_reader import DatabaseFetch
from backend.documents_generator import ReportGenerator
from components.messages import show_success_message
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration


page_configuration("🎖️", "Results & Certificates")
show_go_back_to_home_in_sidebar()

TEMPLATE_HELP = """

"""
GENERATE_CERTIFICATES_HELP = """

"""


def main():
    st.title("🎖️ Results & Certificates")
    st.divider()

    show_certificates()
    show_results()
    show_generate_reports()


def show_results():
    with st.container(border=True):
        st.subheader("🏅 Show Results", divider=True)
        category_selected = st.selectbox(
            label="Category",
            index=0,
            options=fetch.get_categories(),
        )
        event_selected = st.selectbox(
            label="Event",
            options=fetch.get_events_from_category(category_selected),
            index=0,
        )
        if event_selected is not None and category_selected is not None:
            st.dataframe(
                data=cert_object.fetch_ranked_df(category_selected, event_selected),
                hide_index=True
            )
            if st.button("Create Files in the Server"):
                cert_object.generate(category_selected, event_selected)
        


def show_generate_reports():
    with st.container(border=True):
        st.subheader("🏅 Generate Reports", divider=True)
        if st.button("Recreate Reports"):
            with st.spinner("Recreating Reports"):
                rep_obj.generate_reports()
                show_success_message("Recreated Reports")
        



def show_certificates():
    with st.container(border=True):
        st.subheader("🏅 Download Template", divider=True)

        st.download_button(
            label="Download Certificate Template",
            data=cert_object.get_template_file(),
            file_name="template-certificate.png",
            type="primary",
            help=TEMPLATE_HELP,
        )


fetch = DatabaseFetch()
cert_object =CertificateGenerator()
rep_obj = ReportGenerator(category_based_report_needed = True, judgement_sheets_needed=True)
if __name__ == "__main__":
    main()
