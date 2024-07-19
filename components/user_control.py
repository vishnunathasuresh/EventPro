import streamlit as st
from backend.constants import *
from streamlit_authenticator import Authenticate
from backend.file_operations import get_usersdata
from random import choice




class Authenticator:
    def __init__(self) -> None:
        self.usersdata = get_usersdata()
        self.auth = Authenticate(
            {"usernames": self.usersdata},
            "eventpro-auth",
            "eventpro-auth",
            COOKIE_EXPIRY_DAYS,
        )

    def login(self):
        """
        returns username, is_authenticated, usertype
        """
        _, authenticated,username = self.auth.login()
        if authenticated:
            usertype = self.usersdata[username]["user_type"]
            userinfo = self.generate_all_details_for_current_user(username)
        else:
            usertype = None
            userinfo = {}
            
        return username, authenticated, usertype, userinfo

    
    
    def logout(self):
        with st.sidebar:
            self.auth.logout(button_name="Sign Out")

    def generate_all_details_for_current_user(self, username):
        """
        generates user_info from username, userdata(whole usersdata)
        """
        user_info = {
            "username": username,
            "name": self.usersdata[username]["name"],
            "user_type":self.usersdata[username]["user_type"],
            "handle": "@" + username,
            "avatar": "🛡️" if self.usersdata[username]["user_type"] == "admin" else choice(AVATARS),
        }
        return user_info
