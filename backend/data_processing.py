from backend import *
from backend.constants import *
from streamlit import session_state 
from random import choice
import pandas as pd


def get_class_and_division(word: str):
    class_div = word.strip(" ").lower().split("-")
    class_ = CLASS_TO_NUMBER[class_div[0]]
    division = class_div[1]
    return [class_, division]

def add_to_session_state(assign = False,**key_values):
    """add key to session_state if it is not aldready present.
    
    """
    for key, value in key_values.items():
        if key not in session_state or assign:
            session_state[key] = value

    

def is_any_dataframe_cell_empty(dataframe:pd.DataFrame):
    return dataframe.isnull().values.any()



