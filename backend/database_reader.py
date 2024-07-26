from pandas import read_sql
from backend.file_operations import get_current_database_path
from backend.sqlite_connections import SQliteConnectCursor, SQliteConnectConnection


class DatabaseFetch:
    def __init__(self) -> None:
        self.path = get_current_database_path()

    def get_events_from_category(self, category):
        with SQliteConnectCursor() as cursor:
            cursor.execute(
                """
            --sql
            SELECT DISTINCT EVENT_NAME 
            FROM PARTICIPANT,STUDENT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
            AND STUDENT.CATEGORY = ?
            ;
            """,
                (category,),
            )

            eves = cursor.fetchall()
        return [E[0] for E in eves]

    def get_parameters(self):
        """
        NUMBER_OF_JUDGES, MAX_MARKS_FOR_EACH_JUDGE, MIN_MARKS_FOR_PRIZE, MAXIMUM_EVENTS_FOR_PARTICIPATION, RESULTS_READY
        """
        with SQliteConnectCursor(file_path=self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT NUMBER_OF_JUDGES, MAX_MARKS_FOR_EACH_JUDGE, MIN_MARKS_FOR_PRIZE, MAXIMUM_EVENTS_FOR_PARTICIPATION, RESULTS_READY
            FROM PARAMETER
            ;
            """
            )
            data = cursor.fetchone()
        return data

    def get_events(self):
        with SQliteConnectCursor(self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT EVENT_NAME FROM EVENT_NAME
            ;
            """
            )
            eves = cursor.fetchall()
        return [E[0] for E in eves]

    def get_categories(self):
        with SQliteConnectCursor(self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT DISTINCT CATEGORY FROM CLASS_CATEGORY
            ;
            """
            )
            cats = cursor.fetchall()
        return [cat[0] for cat in cats]

    def get_classes(self):
        with SQliteConnectCursor(self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT DISTINCT CLASS FROM CLASS_CATEGORY
            ;
            """
            )
            cats = cursor.fetchall()
        return [cat[0] for cat in cats]

    def get_houses(self):
        with SQliteConnectCursor(self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT HOUSE FROM HOUSE
            ;
            """
            )
            houses = cursor.fetchall()
        return [house[0] for house in houses]

    def get_details_of_admission_number(self, admission_number):
        """
        STUDENT_NAME, CLASS, DIVISION, HOUSE,  events
        """
        with SQliteConnectCursor(self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT STUDENT_NAME, CLASS, DIVISION, HOUSE
            FROM STUDENT
            WHERE ADMISSION_NUMBER = ?
            ;
            """,
                (admission_number,),
            )

            name, class_, division, house = cursor.fetchone()
        EVENTS = self.get_events_from_database(admission_number)
        return name, class_, division, house, EVENTS

    def get_events_from_database(self, admission_number):
        with SQliteConnectCursor(self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT EVENT_NAME
            FROM PARTICIPANT
            WHERE ADMISSION_NUMBER = ?
            ;
            """,
                (admission_number,),
            )

            DATA = cursor.fetchall()
            DATA = [d[0] for d in DATA]
        return DATA

    def get_all_admission_numbers(self):
        with SQliteConnectCursor(self.path) as cursor:
            cursor.execute(
                """
            --sql
            SELECT DISTINCT ADMISSION_NUMBER
            FROM STUDENT
            ;
            """
            )
            cats = cursor.fetchall()

            DATA = [cat[0] for cat in cats]
        return DATA

    def get_database_specs(self):
        """
        returns
        MAX_MARKS_FOR_EACH_JUDGE, NUMBER_OF_JUDGES,
        MIN_MARKS_FOR_PRIZE, MAXIMUM_EVENTS_FOR_PARTICIPATION
        """
        with SQliteConnectCursor() as cursor:
            query = """
            --sql
            SELECT MAX_MARKS_FOR_EACH_JUDGE,
            NUMBER_OF_JUDGES,
            MIN_MARKS_FOR_PRIZE,
            MAXIMUM_EVENTS_FOR_PARTICIPATION
            FROM PARAMETER
            ;
            """

            cursor.execute(query)
            tup1 = cursor.fetchone()
        return tup1

    def get_participant_number(self):
        with SQliteConnectCursor() as cursor:
            cursor.execute(
                """
            --sql
            SELECT COUNT(DISTINCT ADMISSION_NUMBER) FROM PARTICIPANT
            ;
            """
            )
            a = cursor.fetchone()[0]
        return a

    def get_distinct_events_in_participant_table(self):
        with SQliteConnectCursor() as cursor:
            cursor.execute(
                """
            --sql
            SELECT DISTINCT EVENT_NAME FROM PARTICIPANT
            ;
            """
            )
            return [house[0] for house in cursor.fetchall()]


class DatabaseFetchDataframe:
    def __init__(self) -> None:
        self.database_path = get_current_database_path()

    def get_participant_df(self):
        query = """
        --sql
        SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE,CATEGORY, EVENT_NAME
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        ORDER BY CLASS, DIVISION, STUDENT_NAME
        ;
        """
        with SQliteConnectConnection() as conn:
            df = read_sql(query, conn)

        return df

    def get_student_df(self):
        query = """
        --sql
        SELECT ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, CATEGORY
        FROM STUDENT
        ORDER BY CLASS, DIVISION, STUDENT_NAME
        ;
        """
        with SQliteConnectConnection() as conn:
            df = read_sql(query, conn)

        return df

    def get_class_category_df(self):
        with SQliteConnectConnection() as conn:
            df = read_sql(
                "SELECT * FROM CLASS_CATEGORY ",
                con=conn,
            )
        return df

    def get_grade_marks_df(self):
        with SQliteConnectConnection() as conn:
            df = read_sql(
                "SELECT * FROM GRADE_MARKS ",
                con=conn,
            )
        return df

    def get_participants_from_event_category_df(self, category, event):
        from pandas import read_sql

        with SQliteConnectConnection() as conn:
            query = """
            --sql
            SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE
            FROM STUDENT, PARTICIPANT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
            AND CATEGORY = ?
            AND EVENT_NAME = ?
            ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
            ;
            """
            data = read_sql(query, conn, params=(category, event))
            return data
