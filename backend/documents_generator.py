from pandas import read_sql
import os, shutil
from backend.constants import REPORTS_PATH
from backend.data_processing import get_judge_labels
from backend.excel_writer import ExcelDataframeWriter
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

    def create_reports_directory(self):
        shutil.rmtree(REPORTS_PATH, ignore_errors=True)
        os.makedirs(REPORTS_PATH)

    def generate_reports(self):
        self.create_reports_directory()

        with SQliteConnectConnection() as conn:
            for category in self.category_events:
                os.makedirs(REPORTS_PATH + category.title(), exist_ok=True)
                self.create_event_participant_count_report(conn, category)

                if self.category_based_report_needed:
                    self.create_category_reports(conn, category)

                if self.judgement_sheets_needed:
                    self.create_judgement_sheets(conn, category)

                self.create_event_reports(conn, category)
    
    def create_event_participant_count_report(self, conn, category):
        query = """
        --sql
        SELECT EVENT_NAME, COUNT(PARTICIPANT.ADMISSION_NUMBER) AS "Participant Count"
        FROM PARTICIPANT, STUDENT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        GROUP BY EVENT_NAME
        ORDER BY EVENT_NAME ASC;
        """
        event_participant_count_path = REPORTS_PATH + category.title() + "/Event Participant Count.xlsx"
        os.makedirs(os.path.dirname(event_participant_count_path), exist_ok=True)
        df = read_sql(query, conn)
        
        with ExcelDataframeWriter(event_participant_count_path) as xl_obj:
            xl_obj.generate_doc(
                df,
                category.title(),
                "Event Participant Count - " + category.title(),
            )

    def create_category_reports(self, conn, category):
        q1 = """
        --sql
        SELECT PARTICIPANT.ADMISSION_NUMBER AS "Admn. No", 
        STUDENT_NAME as "Name", 
        CLASS as "Class", 
        DIVISION as "Division", 
        HOUSE as "House", 
        GROUP_CONCAT(EVENT_NAME, '  |  ') AS "Events"
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        GROUP BY PARTICIPANT.ADMISSION_NUMBER
        HAVING CATEGORY = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        q2 = """
        --sql
        SELECT PARTICIPANT.ADMISSION_NUMBER AS "Admn. No", 
        STUDENT_NAME as "Name", 
        CLASS as "Class", 
        DIVISION as "Division", 
        HOUSE as "House", 
        EVENT_NAME as "Event Name"
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND CATEGORY = ?
        ORDER BY EVENT_NAME ASC, CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        q3 = """
        --sql
        SELECT EVENT_NAME AS "Event Name",
        COUNT(STUDENT.ADMISSION_NUMBER) AS "Participant Count"
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        GROUP BY CATEGORY, EVENT_NAME
        HAVING CATEGORY = ?
        ORDER BY EVENT_NAME ASC, CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        category_report_path = (
            REPORTS_PATH
            + category.title()
            + f"/{category.title()} - Category Report.xlsx"
        )

        df1 = read_sql(q1, conn, params=(category,))
        df2 = read_sql(q2, conn, params=(category,))
        df3 = read_sql(q3, conn, params=(category,))

        with ExcelDataframeWriter(category_report_path) as xl_obj:
            xl_obj.generate_doc(
                df1, f"{category.title()} - Students", category.title() + " - Students"
            )
            xl_obj.generate_doc(
                df2, f"{category.title()} - All Events", category.title() + " - Events"
            )
            xl_obj.generate_doc(
                df3,
                f"{category.title()} - Statistics",
                category.title() + " - Statistics",
            )

    def create_event_reports(self, conn, category: str):
        events = self.__get_distinct_events_from_category(category)
        query = """
        --sql
        SELECT 
        STUDENT.ADMISSION_NUMBER AS "Admn. No", 
        STUDENT_NAME AS "Name", 
        CLASS AS "Class", 
        DIVISION AS "Division", 
        HOUSE AS "House"
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND EVENT_NAME = ?
        AND STUDENT.CATEGORY = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """

        event_path = (
            REPORTS_PATH + category.title() + f"/{category.title()} - Event Report.xlsx"
        )

        with ExcelDataframeWriter(event_path) as xl_obj:
            for event in sorted(events):
                df = read_sql(query, conn, params=(event, category))
                xl_obj.generate_doc(
                    dataframe=df,
                    sheet_title=event.strip().title(),
                    report_title=str(category + " - " + event).title(),
                )

    def create_judgement_sheets(self, conn, category: str):
        os.makedirs(REPORTS_PATH + category.title() + "/Judgement Sheets/")
        query = f"""
        --sql
        SELECT STUDENT.ADMISSION_NUMBER as "Admn. No.", 
        STUDENT_NAME as "Name",
        CLASS as "Class", 
        DIVISION as "Division", 
        HOUSE as "House", 
        {self.judge_labels.title()}, 
        TOTAL_MARKS AS "Total Marks",
        GRADE as "Grade" ,
        RANK as "Rank",
        DISQUALIFIED as "Disqualified",
        REMARKS as "Remarks"
        FROM STUDENT, PARTICIPANT
        WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
        AND EVENT_NAME = ?
        AND CATEGORY = ?
        ORDER BY CLASS ASC, DIVISION ASC, STUDENT_NAME ASC
        ;
        """
        judgement_sheet_path = (
            REPORTS_PATH
            + category.title()
            + "/Judgement Sheets/"
            + f"{category.title()} - Judgement Sheet.xlsx"
        )

        with ExcelDataframeWriter(judgement_sheet_path) as xl_obj:
            for event in sorted(self.__get_distinct_events_from_category(category)):
                data = read_sql(query, conn, params=(event, category))
                xl_obj.generate_doc(
                    dataframe=data,
                    sheet_title=event.title(),
                    report_title=f"{category.title()} - {event.title()}",
                )
