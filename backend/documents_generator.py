from pandas import read_sql
import os, shutil
from backend.constants import REPORTS_PATH, RESULTS_PATH
from backend.data_processing import get_judge_labels
from backend.sqlite_connections import SQliteConnectConnection, SQliteConnectCursor


class ReportGenerator:
    def __init__(
        self, category_based_report_needed: bool, judgement_sheets_needed: bool
    ) -> None:
        self.categories = self.__get_distinct_category_from_participants()
        self.category_events = self.__get_category_event_dictionary()
        self.judge_labels = self.__get_judge_labels_from_db()

        self.category_based_report_needed = category_based_report_needed
        self.judgement_sheets_needed = judgement_sheets_needed

    def __get_distinct_category_from_participants(self) -> list[str]:
        with SQliteConnectCursor() as cursor:
            query = """
            --sql
            SELECT DISTINCT CATEGORY
            FROM STUDENT, PARTICIPANT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER 
            ;
            """
            cursor.execute(query)
            categories = [cat[0] for cat in cursor.fetchall()]
        return categories

    def __get_distinct_events_from_category(self, category) -> list[str]:
        with SQliteConnectCursor() as cursor:
            query = """
            --sql
            SELECT DISTINCT EVENT_NAME
            FROM STUDENT, PARTICIPANT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
            AND STUDENT.CATEGORY = ?
            ;
            """
            cursor.execute(query, (category,))
            events = [event[0] for event in cursor.fetchall()]
        return events

    def __get_category_event_dictionary(self) -> dict[str, list[str]]:
        category_events = {
            category: self.__get_distinct_events_from_category(category)
            for category in self.categories
        }
        return category_events

    def __get_judge_labels_from_db(self):
        with SQliteConnectCursor() as cursor:
            query = """
            --sql
            SELECT NUMBER_OF_JUDGES 
            FROM PARAMETER
            ;
            """
            cursor.execute(query)
            judge_no = cursor.fetchone()[0]
            judge_labels = get_judge_labels(judge_no)
        return judge_labels

    def __create_category_reports(self, conn, category: str):
        query = """
        --sql
        SELECT PARTICIPANT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, GROUP_CONCAT(EVENT_NAME, ', ') AS EVENTS
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        GROUP BY PARTICIPANT.ADMISSION_NUMBER
        HAVING CATEGORY = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        category_report_path = (
            REPORTS_PATH + category + f"/{category.title()} - Category Report.xlsx"
        )
        data = read_sql(query, conn, params=(category,))
        data.to_excel(
            excel_writer=category_report_path,
            header=["Admission number", "Name", "Class", "Division", "House", "Events"],
            index=False,
        )

    def __create_event_report(self, conn, event: str, category: str):
        query = f"""
        --sql
        SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, TOTAL_MARKS, RANK
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND EVENT_NAME = ?
        AND STUDENT.CATEGORY = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        data = read_sql(query, conn, params=(event, category))
        event_report_path = (
            REPORTS_PATH
            + category
            + f"/{category.title()} - {event.title()} - Report.xlsx"
        )

        data.to_excel(
            excel_writer=event_report_path,
            sheet_name=event,
            header=[
                "Admission number",
                "Name",
                "Class",
                "Division",
                "House",
                "Total",
                "Rank",
            ],
            index=False,
        )

    def __create_judgement_sheets(self, conn, event: str, category: str):
        query = f"""
        --sql
        SELECT '' AS CHESTNUMBER, STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, {self.judge_labels}, TOTAL_MARKS AS TOTAL, RANK
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND EVENT_NAME = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        judgement_sheet_path = (
            REPORTS_PATH
            + category
            + "/Judgement Sheets/"
            + f"{category.title()} - {event.title()} - Judgement Sheet.xlsx"
        )
        data = read_sql(query, conn, params=(event,))
        data.to_excel(
            excel_writer=judgement_sheet_path,
            sheet_name=event,
            header=[
                "Chest Number",
                "Admission number",
                "Name",
                "Class",
                "Division",
                "House",
            ]
            + self.judge_labels.split(", ")
            + ["Total", "Rank"],
            index=False,
        )

    def __create_reports_directory(self):
        shutil.rmtree(REPORTS_PATH, ignore_errors=True)
        os.makedirs(REPORTS_PATH)

    def generate(self):
        self.__create_reports_directory()

        with SQliteConnectConnection() as conn:
            for category in self.category_events:
                os.makedirs(REPORTS_PATH + category, exist_ok=True)

                if self.category_based_report_needed:
                    self.__create_category_reports(conn, category)

                for event in self.category_events[category]:
                    self.__create_event_report(conn, event, category)

                    if self.judgement_sheets_needed:
                        os.makedirs(
                            REPORTS_PATH + category + "/Judgement Sheets/",
                            exist_ok=True,
                        )
                        self.__create_judgement_sheets(conn, event, category)


class ResultGenerator:
    def __init__(self) -> None:
        self.categories = self.__get_distinct_category_from_participants()
        self.category_events = self.__get_category_event_dictionary()
        self.judge_labels = self.__get_judge_labels_from_db()

    def __get_distinct_category_from_participants(self) -> list[str]:
        with SQliteConnectCursor() as cursor:
            query = """
            --sql
            SELECT DISTINCT CATEGORY
            FROM STUDENT, PARTICIPANT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER 
            AND PARTICIPANT.GRADE IS NOT NONE
            ;
            """
            cursor.execute(query)
            categories = [cat[0] for cat in cursor.fetchall()]
        return categories

    def __get_distinct_events_from_category(self, category) -> list[str]:
        with SQliteConnectCursor() as cursor:
            query = """
            --sql
            SELECT DISTINCT EVENT_NAME
            FROM STUDENT, PARTICIPANT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
            AND STUDENT.CATEGORY = ?
            AND PARTICIPANT.GRADE IS NOT NONE

            ;
            """
            cursor.execute(query, (category,))
            events = [event[0] for event in cursor.fetchall()]
        return events

    def __get_category_event_dictionary(self) -> dict[str, list[str]]:
        category_events = {
            category: self.__get_distinct_events_from_category(category)
            for category in self.categories
        }
        return category_events

    def __get_judge_labels_from_db(self):
        with SQliteConnectCursor() as cursor:
            query = """
            --sql
            SELECT NUMBER_OF_JUDGES 
            FROM PARAMETER
            ;
            """
            cursor.execute(query)
            judge_no = cursor.fetchone()[0]
            judge_labels = get_judge_labels(judge_no)
        return judge_labels

    def __create_event_report(self, conn, event: str, category: str):
        query = f"""
        --sql
        SELECT STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, TOTAL_MARKS, RANK
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND EVENT_NAME = ?
        AND STUDENT.CATEGORY = ?
        ORDER BY RANK DESC, CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        data = read_sql(query, conn, params=(event, category))
        event_report_path = (
            RESULTS_PATH
            + category
            + f"/{category.title()} - {event.title()} - Result.xlsx"
        )

        data.to_excel(
            excel_writer=event_report_path,
            sheet_name=event,
            header=[
                "Admission number",
                "Name",
                "Class",
                "Division",
                "House",
                "Total",
                "Rank",
            ],
            index=False,
        )

    def __create_judgement_sheets(self, conn, event: str, category: str):
        query = f"""
        --sql
        SELECT '' AS CHESTNUMBER, STUDENT.ADMISSION_NUMBER, STUDENT_NAME, CLASS, DIVISION, HOUSE, {self.judge_labels}, TOTAL_MARKS AS TOTAL, RANK
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND EVENT_NAME = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        judgement_sheet_path = (
            RESULTS_PATH
            + category
            + "/Judgement Sheets/"
            + f"{category.title()} - {event.title()} - Judgement Sheet.xlsx"
        )
        data = read_sql(query, conn, params=(event,))
        data.to_excel(
            excel_writer=judgement_sheet_path,
            sheet_name=event,
            header=[
                "Chest Number",
                "Admission number",
                "Name",
                "Class",
                "Division",
                "House",
            ]
            + self.judge_labels.split(", ")
            + ["Total", "Rank"],
            index=False,
        )

    def __create_results_directory(self):
        shutil.rmtree(RESULTS_PATH)
        os.makedirs(RESULTS_PATH)

    def generate(self):
        self.__create_results_directory()

        with SQliteConnectConnection() as conn:
            for category in self.category_events:
                os.makedirs(RESULTS_PATH + category, exist_ok=True)

                for event in self.category_events[category]:
                    self.__create_event_report(conn, event, category)
                    os.makedirs(
                        RESULTS_PATH + category + "/Judgement Sheets/", exist_ok=True
                    )
                    self.__create_judgement_sheets(conn, event, category)
