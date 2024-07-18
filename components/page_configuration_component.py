import streamlit as st
from streamlit_autorefresh import st_autorefresh


def page_configuration(icon, title, autorefresh = False):
	st.set_page_config(
		page_icon=icon,
		page_title=title,
		layout="wide",
	)
	st.logo(
		image='./assets/icon-square-rounded-border.png',
		icon_image='./assets/icon-square-rounded-border.png'
	)
	if autorefresh:
		cnt = st_autorefresh(interval=3000,)