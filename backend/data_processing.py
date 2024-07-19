from io import StringIO
from csv import reader as csv_reader
from backend.constants import *
from streamlit import session_state 
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

def process_grade_marks(dataframe):
    final_dict = {}
    for dictionary in dataframe:
        final_dict[dictionary["grade"].upper()] = dictionary["min_marks"]
    return final_dict

def process_student_data_from(csv_data, class_category_dict):
    try:
        student_data = []
        file = StringIO(csv_data.getvalue().decode("utf-8"))
        admn_nos = tuple()
        for row in csv_reader(file):
            admn_no = row[0]
            name = row[1]
            class_, division = get_class_and_division(row[2])
            category = class_category_dict[class_]
            if admn_no not in admn_nos:
                student_data.append((admn_no, name.title(), class_, division.upper(), None, category))
                admn_nos = admn_nos = (admn_no,)
        return student_data
    except:
        raise SyntaxError("The csv file does not meet the syntax required.")

def get_judge_labels(judge_no):
    return ', '.join(
        [f'JUDGE{num}' for num in range(1, judge_no+ 1)]
    )

def get_default_grades(TOTAL_MARKS):
    if TOTAL_MARKS:
        return [
            {
                "grade": "A",
                "min_marks": int(0.85 * TOTAL_MARKS),
            },
            {
                "grade": "B",
                "min_marks": int(0.75 * TOTAL_MARKS),
            },
            {
                "grade": "C",
                "min_marks": int(0.65 * TOTAL_MARKS),
            },
            {
                "grade": "D",
                "min_marks": int(0.55 * TOTAL_MARKS),
            },
            {
                "grade": "E",
                "min_marks": int(0.45 * TOTAL_MARKS),
            },
            {
                "grade": "F",
                "min_marks": int(0.35 * TOTAL_MARKS),
            },
        ]

def get_class_category_dict_from(dataframe: pd.DataFrame):
    dictionary = dataframe.to_dict()
    final_dict = {}
    classes = dictionary["class"]
    categories = dictionary["category"]
    for index in classes.keys():
        final_dict[classes[index]] = categories[index]
    return final_dict
