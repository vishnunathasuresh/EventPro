import streamlit as st
from components.navigation import show_go_back_to_home_in_sidebar
from components.page_configuration_component import page_configuration

page_configuration(icon="😊", title="About the Developer")

show_go_back_to_home_in_sidebar()


def main() -> None:
    st.title(" 💻 About the Developer")
    st.divider()

    st.image("./assets/icon-square-rounded-border.png", width=150)

    st.write(WORDS)


WORDS = """
- ***Version 1.0.0 of EventPro***
- ***Built and completed in 2024-25.***
- ***Last Update : July 2024***
- ***Name :- Vishnunath A Suresh***
- ***Github Username : Vishnunath-A-Suresh***
"""

if __name__ == "__main__":
    main()
