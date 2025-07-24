import os
import sqlite3
from backend.constants import DATABASE_DIRECTORY_PATH, DATABASE_EXTENSION
from backend.data_processing import (
    process_grade_marks,
    process_student_data_from,
    get_class_category_dict_from,
)
from backend.file_operations import get_current_database_path, get_houses
from datetime import datetime
from components.messages import show_error_message, show_general_message
from components.navigation import go_to_home_page


class SQliteConnectCursor:
    def __init__(self, file_path=get_current_database_path()) -> None:
        self.file_path = file_path
        self.connection = sqlite3.connect(database=self.file_path)

    def __enter__(self):
        cursor = self.connection.cursor()
        return cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.commit()
        self.connection.close()


class SQliteConnectConnection:
    def __init__(self, file_path=get_current_database_path()) -> None:
        self.file_path = file_path
        self.connection = sqlite3.connect(database=self.file_path)

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.commit()
        self.connection.close()


class DatabaseEngine:
    def __init__(
        self,
        database_name,
        number_of_judges,
        max_marks_for_each_judge,
        min_marks_for_prize,
        available_events_,
        grades,
        max_number_of_events,
        edited_class_category_dataframe,
        uploaded_csv,
    ):
        self.current_year = datetime.now().year
        self.database_name = database_name
        self.number_of_judges = number_of_judges
        self.max_marks_for_each_judge = max_marks_for_each_judge
        self.min_marks_for_prize = min_marks_for_prize

        self.available_events = list(
            set([event.title() for event in available_events_["Event"]])
        )

        self.available_events = [(event,) for event in self.available_events]
        self.group_events:list[tuple] = list(
            set(
                [
                    (event,)
                    for event in available_events_["Event"]
                    if available_events_["Group Event"][available_events_["Event"] == event].any()
                ]
            )
        )

        self.grades_min_marks = process_grade_marks(grades)

        self.class_category_dict = get_class_category_dict_from(
            edited_class_category_dataframe
        )

        self.max_number_of_events = max_number_of_events
        self.uploaded_csv = uploaded_csv

        self.student_data = process_student_data_from(
            self.uploaded_csv, self.class_category_dict
        )
        self.database_file_path = (
            DATABASE_DIRECTORY_PATH
            + f"{database_name}-{self.current_year}"
            + DATABASE_EXTENSION
        )

    def create_database(self):
        try:
            if os.path.exists(self.database_file_path):
                os.remove(path=self.database_file_path)

            self.create_student_table()
            self.create_participant_table()
            self.create_event_name_table()
            self.create_parameter_table()
            self.create_class_category_table()
            self.create_grade_marks_table()
            self.create_house_table()

            show_general_message("Database Created Successfully!")
            go_to_home_page()

        except Exception as e:
            show_error_message(e)

    def create_student_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = """
            --sql
            CREATE TABLE STUDENT(
                ADMISSION_NUMBER TEXT PRIMARY KEY,
                STUDENT_NAME TEXT,
                CLASS TEXT,
                DIVISION TEXT,
                HOUSE TEXT,
                CATEGORY TEXT
            )
            ;
            """
            query2 = """
            --sql
            INSERT INTO STUDENT VALUES (?,?,?,?,?,?)
            ;
            """
            cursor.execute(query1)
            student_data = list(set(self.student_data))
            cursor.executemany(query2, student_data)

    def create_participant_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = f"""
            --sql
            CREATE TABLE PARTICIPANT(
                ADMISSION_NUMBER TEXT,
                EVENT_NAME TEXT ,
                {', '.join([f'JUDGE{NUM+1} INT' for NUM in range(self.number_of_judges)])},
                TOTAL_MARKS INT,
                GRADE INT,
                RANK TEXT,
                DISQUALIFIED BOOLEAN DEFAULT 0,
                REMARKS TEXT DEFAULT "",
                PRIMARY KEY(ADMISSION_NUMBER, EVENT_NAME)
            )
            ;
            """
            cursor.execute(query1)

    def create_event_name_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = """
            --sql
            CREATE TABLE EVENT_NAME (EVENT_NAME TEXT)
            ;
            """
            query2 = """
            --sql
            INSERT INTO EVENT_NAME VALUES (?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, self.available_events)
    
    def create_group_event_name_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = """
            --sql
            CREATE TABLE GROUP_EVENT_NAME (EVENT_NAME TEXT)
            ;
            """
            query2 = """
            --sql
            INSERT INTO GROUP_EVENT_NAME VALUES (?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, self.group_events)

    def create_parameter_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = """
            --sql
            CREATE TABLE PARAMETER (
                DATABASENAME TEXT, 
                NUMBER_OF_JUDGES INT, 
                MAX_MARKS_FOR_EACH_JUDGE INT, 
                MIN_MARKS_FOR_PRIZE INT, 
                TOTAL_MARKS,
                RESULTS_READY BOOLEAN,
                MAXIMUM_EVENTS_FOR_PARTICIPATION INT
            )
            ;
            """
            query2 = """
            --sql
            INSERT INTO PARAMETER VALUES (?, ?, ?, ?, ?, ?, ?)
            ;
            """
            cursor.execute(query1)
            cursor.execute(
                query2,
                (
                    f"{self.database_name}-{self.current_year}.eventpro.db",
                    self.number_of_judges,
                    self.max_marks_for_each_judge,
                    self.min_marks_for_prize,
                    self.max_marks_for_each_judge * self.number_of_judges,
                    False,
                    self.max_number_of_events,
                ),
            )

    def create_class_category_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = """
            --sql
            CREATE TABLE CLASS_CATEGORY (
                CLASS TEXT,
                CATEGORY TEXT
            )
            ;
            """
            query2 = """
            --sql
            INSERT INTO CLASS_CATEGORY VALUES (?, ?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, list(self.class_category_dict.items()))

    def create_grade_marks_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = """
            --sql
            CREATE TABLE GRADE_MARKS(
                GRADE TEXT,
                MIN_MARKS INT
            )
            ;
            """
            query2 = """
            --sql
            INSERT INTO GRADE_MARKS VALUES (?, ?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, list(self.grades_min_marks.items()))

    def create_house_table(self):
        with SQliteConnectCursor(self.database_file_path) as cursor:
            query1 = """
            --sql
            CREATE TABLE HOUSE(HOUSE TEXT)
            ;
            """
            query2 = """
            --sql
            INSERT INTO HOUSE VALUES (?)
            ;
            """
            cursor.execute(query1)
            cursor.executemany(query2, get_houses())
