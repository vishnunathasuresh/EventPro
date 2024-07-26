#paths
DATABASE_DIRECTORY_PATH = "./databases/"
DATABASE_EXTENSION = ".eventpro.db"
SAVED_DATABASES_DIRECTORY_PATH = "./databases/archived/"
INTERNALS_PATH = "./.internals/"
IMAGES_DIRECTORY_PATH = "./assets/"
REPORTS_PATH = "./reports/"
RESULTS_PATH = "./results/"
CHAT_FILE = "chat.data"

#vaiables
CLASSES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "lkg", "ukg"]
CLASS_TO_NUMBER = {
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
    "vi": "6",
    "vii": "7",
    "viii": "8",
    "ix": "9",
    "x": "10",
    "xi": "11",
    "xii": "12",
    "lkg": "lkg",
    "ukg": "ukg",
}
DEFAULT_EVENTS = [
    "Pencil Drawing",
    "Elocution Malayalam",
    "Elocution English",
    "Elocution Hindi",
    "Story Telling Malayalam",
    "Story Telling Hindi",
    "Story Telling English",
    "Painting Crayons",
    "Painting Water Colour",
    "Painting Oil Colour",
    "Cartoon",
    "Abstract Reasoning",
    "Clay Modelling",
    "Show and Tell",
    "Extempore English",
    "Extempore Malayalam",
    "Extempore Hindi",
    "Digital Painting",
    "Power Point Presentation",
    "Essay Writing English",
    "Essay Writing Malayalam",
    "Essay Writing Hindi",
    "Story Writing English",
    "Story Writing Malayalam",
    "Story Writing Hindi",
    "Poetry Writing English",
    "Poetry Writing Malayalam",
    "Poetry Writing Hindi",
    "Recitation English",
    "Recitation Malayalam",
    "Recitation Hindi",
    "Recitation Sanskrit",
    "Recitation Arabic",
    "Light Music- Boys",
    "Light Music - Girls",
    "Patriotic Song",
    "Classical Music - Boys",
    "Classical Music - Girls",
    "Bharatnatyam - B&G",
    "Mohiniattom - Girls",
    "Mappilapattu Boys",
    "Mappilapattu Girls",
    "Monoact- Common",
    "Mimicry -Common",
    "Folk Dance - Boys",
    "Folk Dance- Girls",
    "Kuchipudi Girls",
    "Flute",
    "Mridangam",
    "Tabala",
    "Violin",
    "Keyboard",
    "Guitar",
    "Group Song",
    "Group Dance",
    "Western Solo",
    "Quiz",
    "Mime"
]
DEFAULT_HOUSES = [
    "Red",
    "Yellow",
    "Blue",
    "Green",
]
DEFAULT_PARAMETERS = {
    "number_of_categories": 5,
    "number_of_judges" : 3,
    "max_marks" : 10,
    "max_number_of_event_participation" : 5,
    "events":DEFAULT_EVENTS,
    "houses": DEFAULT_HOUSES,
}
DEFAULT_USERSDATA = {
    "admin": {"name": "Admin", "password": "admin@nmcs", "user_type": "admin"},
    "teacher": {
        "name": "Teacher",
        "password": "teacher@eventpro",
        "user_type": "elevated-user",
    },
    "student": {"name": "Student", "password": "student@eventpro", "user_type": "user"},
}
AVATARS = "😊🤩😄😎🐍🤔😌😑😇🥹🐱🦁🐯🐼🐨🐰🐭🦜🪽🦋🕊️🦚❄️🔥☄️🌛🌞⭐🌈⚡"
COOKIE_EXPIRY_DAYS = 1