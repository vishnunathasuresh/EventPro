import sqlite3
from backend.file_operations import get_current_database_path 


class SQliteConnectCursor:
    def __init__(self, file_path= get_current_database_path()) -> None:
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