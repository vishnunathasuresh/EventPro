import streamlit as st
import os
from backend.ResultsGenerator import CertificateGenerator
from backend.database_reader import DatabaseFetch
from backend.documents_generator import ReportGenerator
from components.messages import show_arrow_message, show_success_message
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration
from backend.constants import CERTIFICATES_PATH


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
    create_manual_certificates()
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


def create_manual_certificates():
    with st.container(border=True):
        st.subheader("Create Manual Certificates", divider=True)
        col1, col2 = st.columns(2)
        with col1:    
            category_ = st.text_input(
                label="Category",
                value="",
                placeholder="eg: Category 1"
            )

            event = st.text_input(
                label="Event Name",
                value="",
                placeholder="eg: Painting",
            )

            prize = st.selectbox(
                label="Prize",
                options=["First", "Second", "Third", "Consolation"],
                index=0,
            )
        with col2:
            admission_number = st.text_input(
                label="Admission Number",
                value="",
                disabled=category_.strip() == "" or event.strip() == "",
                placeholder="eg: S8557"
            )
            
            date = st.date_input(
                label="Date",
                format="DD-MM-YYYY",
            )
            disabled_condition = not (
                admission_number in fetch.get_all_admission_numbers()
                and event.strip() != ""
                and category_.strip()!= ""
            )
            create_certificate = st.button(
                "Create Certificate",
                disabled=disabled_condition,
                use_container_width=True
            )
        
        if not disabled_condition:
        
            name, class_, division, _, _ = fetch.get_details_of_admission_number(admission_number)
            name = name.title()
            st.info(name)

            class_division = cert_object.class_division(class_, division)
            st.info(class_division)

            category_event = cert_object.category_event(category_, event)
            prize = cert_object.prize(prize) # type: ignore

            if create_certificate:
                os.makedirs(CERTIFICATES_PATH + "CUSTOM/", exist_ok=True)
                
                cert_object.create_certificate(
                    name=name,
                    class_division=class_division, # type: ignore
                    category_event=category_event,
                    prize=prize,
                    date = date.strftime("%d-%m-%Y"),# type: ignore
                    location=(
                        CERTIFICATES_PATH + f"CUSTOM/{category_event} - {prize} - {admission_number}.png"
                    )
                )
                show_arrow_message("Created Certificate")
        



def show_certificates():
    with st.container(border=True):
        st.subheader("🏅 Download Template", divider=True)

        st.image(cert_object.get_template_file(), caption="Certificate Template")

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
