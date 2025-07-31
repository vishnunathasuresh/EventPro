from io import BytesIO
from math import inf
import os 
import shutil
from turtle import width
from altair import Config
from pandas import read_sql
from backend.constants import CERTIFICATES_PATH, CLASS_TO_NUMBER, RESULTS_PATH
from backend.data_processing import get_judge_labels
from backend.sqlite_connections import SQliteConnectConnection, SQliteConnectCursor
from datetime import datetime
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
from components.messages import show_arrow_message
import logging
from backend.config import CONFIG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


info = CONFIG


class ResultsGenerator:
    def __init__(self) -> None:
        self.categories = self.__get_distinct_category_from_participants()
        self.category_events = self.__get_category_event_dictionary()
        self.judge_labels = self.__get_judge_labels_from_db()
        self.certificateMaker = CertificateGenerator()

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

    def generate(self, gen_all_certificates=False):
        self.__create_results_directory()

        with SQliteConnectConnection() as conn:
            for category in self.category_events:
                os.makedirs(RESULTS_PATH + category, exist_ok=True)

                for event in self.category_events[category]:
                    if gen_all_certificates:
                        self.certificateMaker.generate(category, event)

                    self.__create_event_report(conn, event, category)
                    os.makedirs(
                        RESULTS_PATH + category + "/Judgement Sheets/", exist_ok=True
                    )
                    self.__create_judgement_sheets(conn, event, category)


class CertificateGenerator:
    def __init__(self) -> None:
        self.name_coordinates = tuple(info.get("name", {}).get("coordinates", (436, 555)))
        self.class_division_coordinates = tuple(info.get("class-division", {}).get("coordinates", (1250, 555)))
        self.category_event_coordinates = tuple(info.get("category-event", {}).get("coordinates", (130, 710)))
        self.date_coordinates = tuple(info.get("date", {}).get("coordinates", (1200, 900)))
        self.prize_coordinates = tuple(info.get("prize", {}).get("coordinates", (475, 630)))
        self.color = info.get("font-color", "black")

    def get_template_file(self):
        """
        Generates an image that is white with name, class-division, category-event, prize and date in a fixed place.

        """
        certificate = self.create_certificate(
            name="Leonardo Da Vinci",
            class_division="XII-D",
            category_event="Category5 - Painting",
            prize="First Prize",
            date=self.date()
        )
        with BytesIO() as buf:
            certificate.save(buf, format="PNG")
            img_bytes = buf.getvalue()
        return img_bytes
        
    @staticmethod
    def class_division(class_, division):
        for key in CLASS_TO_NUMBER:
            if CLASS_TO_NUMBER[key] == class_:
                return f"{key.upper()} - {division}"

    @staticmethod
    def category_event(category:str, event_name:str):
        return f"{category.title()} - {event_name.title()}"

    @staticmethod
    def prize(prize:str):
        return prize.title() + " Prize"

    @staticmethod
    def date():
        now=datetime.now() 
        formatted_date = now.strftime("%d-%m-%Y")
        return formatted_date
    
    @staticmethod
    def time():
        now = datetime.now()
        formatted_time = now.strftime("%H:%M")
        return formatted_time

    def fetch_ranked_df(self, category, event_name):
        with SQliteConnectConnection() as conn:
            query = """
            --sql
            SELECT STUDENT_NAME, CLASS, DIVISION, CATEGORY, EVENT_NAME, RANK
            FROM STUDENT, PARTICIPANT
            WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
            AND CATEGORY = ?
            AND EVENT_NAME = ?
            AND RANK IS NOT NULL
            ;
                """
            df = read_sql(query, conn, params=(category, event_name))
        
        return df

    def fetch_ranked_participants(self, category, event_name):
        final_data = []
        with SQliteConnectCursor() as cursor:
            cursor.execute(
                """
                --sql
                SELECT STUDENT_NAME, CLASS, DIVISION, CATEGORY, EVENT_NAME, RANK
                FROM STUDENT, PARTICIPANT
                WHERE STUDENT.ADMISSION_NUMBER = PARTICIPANT.ADMISSION_NUMBER
                AND CATEGORY = ?
                AND EVENT_NAME = ?
                AND RANK IS NOT NULL
                ;
                """,
                (category, event_name)
            )
            fetched_data = cursor.fetchall()
            for rec in fetched_data:
                final_data.append(
                    {
                        "name": rec[0],
                        "class-division": self.class_division(rec[1], rec[2]),
                        "category-event": self.category_event(rec[3], rec[4]),
                        "prize": self.prize(rec[5]),
                        "date": self.date(),
                        "time": self.time()
                    }
                )

        return final_data

    def generate(self, category:str, event_name:str):
        """
        Generates the certificates for respective events
        """
        records = self.fetch_ranked_participants( category, event_name)
        certificates_event_path = CERTIFICATES_PATH + category.title() + "/"+ event_name.title()
        shutil.rmtree(certificates_event_path, ignore_errors=True)
        os.makedirs(certificates_event_path, exist_ok=True)
        for rec in records:
            name = rec["name"]
            class_division = rec["class-division"]
            category_event = rec["category-event"]
            prize = rec["prize"]
            date = rec["date"]
            loc = certificates_event_path + f"/{category_event} - {prize} - {name}.png"
            self.create_certificate(name, class_division, category_event, prize, date, loc)
        else:
            show_arrow_message(f"Created Certificates")
    

    
    def draw_text(self, image:PIL.Image.Image, name:str, class_division:str, category_event:str, prize:str, date:str):
        """
        Draws the text on the image
        """
        draw = PIL.ImageDraw.Draw(image)
        name_font_size = info.get("name", {}).get("height", 30)
        class_division_font_size = info.get("class-division", {}).get("height", 30)
        category_event_font_size = info.get("category-event", {}).get("height", 30)
        prize_font_size = info.get("prize", {}).get("height", 30)
        date_font_size = info.get("date", {}).get("height", 30)

        name_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=name_font_size
        ) 
        class_division_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=class_division_font_size
        )
        category_event_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=category_event_font_size
        )
        prize_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=prize_font_size
        )
        date_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=date_font_size
        )
        color = info.get("font-color", "black")
        # name-of-the-student
        draw.text(
            xy=self.name_coordinates, text=name.title(), font=name_font, fill=color, stroke_width=0
        )

        # class-division-of-the-student
        draw.text(
            xy=self.class_division_coordinates,
            text=class_division.upper(),
            font=class_division_font,
            fill=color,
            stroke_width=0,
        )

        # prize-of-the-student
        draw.text(
            xy=self.prize_coordinates, text=prize.title(), font=prize_font, fill=color, stroke_width=0
        )

        # category-event-of-the-student
        draw.text(
            xy=self.category_event_coordinates, text=category_event.title(), font=category_event_font, fill=color, stroke_width=0
        )

        # date-of-the-event
        draw.text(xy=self.date_coordinates, text=date, font=date_font, fill=color, stroke_width=0)

    def get_template_certificate(self):
        """
        Generates an image that is white with name, class-division, category-event, prize and date in a fixed place.
        """
        image = PIL.Image.open(info.get("sample-certificate", "./assets/certificate.png"))
        self.draw_text(
            image,
            name="Leonardo Da Vinci",
            class_division="XII-D",
            category_event="Category5 - Painting",
            prize="First Prize",
            date=self.date()
        )
        return image

    def create_certificate(self, name:str, class_division:str, category_event:str, prize:str, date:str, location:str|None = None):
        
        if not os.path.exists("./.internals/whitesheet.png"):
            image = PIL.Image.open(info.get("sample-certificate", "./assets/certificate.png"))
            width, height = image.size
            # Create a white image if it doesn't exist
            white_image = PIL.Image.new("RGB", (width, height), "white")
            white_image.save("./.internals/whitesheet.png")
        image = PIL.Image.open("./.internals/whitesheet.png")
        draw = PIL.ImageDraw.Draw(image)
        fontmedium = PIL.ImageFont.truetype(font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"), size=info.get("font", {}).get("medium", 36))
        fontsmall = PIL.ImageFont.truetype(font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"), size=info.get("font", {}).get("small", 32))
        fontbig = PIL.ImageFont.truetype(font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"), size=info.get("font", {}).get("big", 37))
        name_font_size = info.get("name", {}).get("height", 30)
        class_division_font_size = info.get("class-division", {}).get("height", 30)
        category_event_font_size = info.get("category-event", {}).get("height", 30)
        prize_font_size = info.get("prize", {}).get("height", 30)
        date_font_size = info.get("date", {}).get("height", 30)

        name_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=name_font_size
        )
        class_division_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=class_division_font_size
        )
        category_event_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=category_event_font_size
        )
        prize_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=prize_font_size
        )
        date_font = PIL.ImageFont.truetype(
            font=info.get("font", {}).get("ttf", "./assets/kalam.ttf"),
            size=date_font_size
        )


        color = info.get("font-color", "black")

        # name-of-the-student
        draw.text(
            xy=self.name_coordinates, text=name.title(), font=name_font, fill=color, stroke_width=0
        )

        # class-division-of-the-student
        draw.text(
            xy=self.class_division_coordinates,
            text=class_division.upper(),
            font=class_division_font,
            fill=color,
            stroke_width=0,
        )

        # prize-of-the-student
        draw.text(
            xy=self.prize_coordinates, text=prize.title(), font=prize_font, fill=color, stroke_width=0
        )

        # category-event-of-the-student
        draw.text(
            xy=self.category_event_coordinates, text=category_event.title(), font=category_event_font, fill=color, stroke_width=0
        )

        # date-of-the-event
        draw.text(xy=self.date_coordinates, text=date, font=date_font, fill=color, stroke_width=0)

        # save-image
        if location:
            image.save(location)
        
        return image

        
