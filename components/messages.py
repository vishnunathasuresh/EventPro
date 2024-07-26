import streamlit as st


def show_error_message(*args, icon="❌"):
    st.toast(*args, icon=icon)


def show_success_message(*args, icon="✅"):
    st.toast(*args, icon=icon)


def show_arrow_message(*args, icon="➡️"):
    st.toast(*args, icon=icon)


def show_general_message(*args, icon="✨"):
    st.toast(*args, icon=icon)
