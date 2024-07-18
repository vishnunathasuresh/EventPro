import streamlit as st
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration

page_configuration(
    icon="😎",
    title="About the Developer"
)

show_go_back_to_home_in_sidebar()


def main()-> None:
    st.title(" 💻 About Me")
    st.divider()

    st.write(WORDS)


WORDS = """
- Version 3.6 of EventPro
- Built and completed in 2024-25.
- Last Update : July 2024
- Built with Python.
- Contact Information of the Developer:
    - Email ID: vishnunath.suresh06@gmail.com
""" 

if __name__ == '__main__':
    main()