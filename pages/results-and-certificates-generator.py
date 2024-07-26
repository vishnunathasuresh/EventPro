import streamlit as st
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


def show_generate_reports():
    with st.container(border=True):
        st.subheader("🏅 Generate Reports", divider=True)


def show_certificates():
    with st.container(border=True):
        st.subheader("🏅 Certificates", divider=True)

        st.download_button(
            label="Download Certificate Template",
            data="../assets/icon-border.png",
            file_name="template-certificate.png",
            type="primary",
            help=TEMPLATE_HELP,
        )

        generate_certicates = st.button(
            label="Generate Certificates",
            type="primary",
            help=GENERATE_CERTIFICATES_HELP,
        )
        if generate_certicates:
            generate_certicates_files()


def generate_certicates_files():
    pass


if __name__ == "__main__":
    main()
