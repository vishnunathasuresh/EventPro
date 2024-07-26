from pandas import DataFrame
from backend.constants import *
import os
import yaml


def get_usersdata():
    def create_directory_with_error_if_present():
        os.makedirs(INTERNALS_PATH, exist_ok=False)

    def load_default_userdata_and_write_to_file():
        USERDATA = DEFAULT_USERSDATA
        with open(INTERNALS_PATH + "users.yaml", "w") as file:
            yaml.dump(DEFAULT_USERSDATA, file)
        return USERDATA

    def get_users_data() -> dict:
        with open(INTERNALS_PATH + "users.yaml") as file:
            USERDATA: dict = yaml.safe_load(file)
        return USERDATA

    try:
        create_directory_with_error_if_present()
        USERDATA = load_default_userdata_and_write_to_file()
    except OSError:
        USERDATA = get_users_data()
        if USERDATA == {}:
            USERDATA = load_default_userdata_and_write_to_file()
    finally:
        return USERDATA


def get_parameters() -> dict:
    def create_file_and_load_default_parameters():
        with open(INTERNALS_PATH + "default_parameters.yaml", "w") as file:
            yaml.dump(DEFAULT_PARAMETERS, file)
        return DEFAULT_PARAMETERS

    def load_parameters_if_file_present():
        with open(INTERNALS_PATH + "default_parameters.yaml", "r") as file:
            PARAMETERS = yaml.safe_load(file)
        return PARAMETERS

    try:
        PARAMETERS = load_parameters_if_file_present()
    except OSError:
        PARAMETERS = create_file_and_load_default_parameters()
    finally:
        return PARAMETERS


def get_current_database_name_and_path():
    """get current_database, path"""
    try:
        current_database = [
            file
            for file in os.listdir(DATABASE_DIRECTORY_PATH)
            if file.endswith(DATABASE_EXTENSION)
        ]
        if current_database == []:
            return None, None
        else:
            return current_database[0], DATABASE_DIRECTORY_PATH + current_database[0]
    except FileNotFoundError:
        os.makedirs(SAVED_DATABASES_DIRECTORY_PATH)
        return None, None


def get_saved_databases() -> list[str]:
    try:
        saved_databases = [
            file
            for file in os.listdir(SAVED_DATABASES_DIRECTORY_PATH)
            if file.endswith(DATABASE_EXTENSION)
        ]
    except FileNotFoundError:
        os.makedirs(SAVED_DATABASES_DIRECTORY_PATH)
        saved_databases = []
    finally:
        return saved_databases


def get_current_database_name():
    try:
        current_database = [
            file
            for file in os.listdir(DATABASE_DIRECTORY_PATH)
            if file.endswith(DATABASE_EXTENSION)
        ]
        if current_database == []:
            return None
        else:
            return current_database[0]
    except FileNotFoundError:
        os.makedirs(SAVED_DATABASES_DIRECTORY_PATH)
        return None


def get_current_database_path():
    return DATABASE_DIRECTORY_PATH + str(get_current_database_name())


def delete_database_permanent():
    database_path = get_current_database_path()
    os.remove(database_path)


def archive_database():
    from shutil import move

    database_path = DATABASE_DIRECTORY_PATH + str(get_current_database_name())
    new_path = SAVED_DATABASES_DIRECTORY_PATH
    move(database_path, new_path)


def push_edits_to_users_yaml(df):
    from yaml import dump

    dictionary = df.to_dict()
    final_dict = {}
    for index in dictionary["username"]:
        final_dict[dictionary["username"][index]] = {
            "name": dictionary["name"][index],
            "password": dictionary["password"][index],
            "user_type": dictionary["user_type"][index],
        }

    with open(INTERNALS_PATH + "users.yaml", "w") as file:
        dump(final_dict, file)


def get_user_data_as_dataframe():
    data = get_usersdata()
    new_data = []
    nd = {}
    for username in data:
        new_data.append(
            dict(
                username=username,
                name=data[username]["name"],
                password=data[username]["password"],
                user_type=data[username]["user_type"],
            )
        )
    nd = {
        "username": [username for username in data],
        "name": [data[username]["name"] for username in data],
        "password": [data[username]["password"] for username in data],
        "user_type": [data[username]["user_type"] for username in data],
    }
    return DataFrame(nd)


def get_houses():
    from yaml import safe_load

    with open(INTERNALS_PATH + "default_parameters.yaml") as file:
        houses = safe_load(file)["houses"]
        houses = [(house,) for house in houses]
    return houses
