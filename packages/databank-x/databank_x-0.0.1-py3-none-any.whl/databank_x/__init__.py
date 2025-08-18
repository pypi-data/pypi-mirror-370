from cryptography.fernet import Fernet
import json
import os
import logging
import pandas as pd

global log
log = False
data = {}

class basic:
    def basic_List():
        global data
        data = {
            "test1":[1 , "hi"],
            "test2":["his",86]
        }
        if log:
            logging.info("Initialized basic data structure.")
    def show_List():
        global data
        if log:
            logging.info("Displaying data structure.")
        return data

    def add_data(datas , directory):
        global data
        data[directory].append(datas)
        if log:
            logging.info(f"Added data '{datas}' to directory '{directory}'.")

    def add_directory(name):
        global data
        data[name] = []
        if log:
            logging.info(f"Added new directory '{name}'.")

    def remove_directory(name):
        global data
        del data[name]
        if log:
            logging.info(f"Removed directory '{name}'.")
    def remove_data(directory, datass):
        global data
        data[directory].pop(datass)

    def index_searche(directory, indexes):
        global data
        if log:
            logging.info(f"Searching for index '{indexes}' in directory '{directory}'.")
        try:
            return data[directory][indexes]
        except (KeyError, IndexError):
            return "error"

    def string_data(datas, directory):
        global data
        stri = list(datas)
        data[directory].append(stri)
        if log:
            logging.info(f"Added string data '{stri}' to directory '{directory}'.")

class saves:

    def save_json(file):
        global data
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        if log:
            logging.info(f"Data saved to JSON file '{file}'.")

    def see_json(file):
        if log:
            logging.info(f"Loading data from JSON file '{file}'.")
        with open(file, "r", encoding="utf-8") as f:
            data_loaded = json.load(f)
            return data_loaded
        
    def overwrite_data_json(file):
        global data
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if log:
            logging.info(f"Data overwritten from JSON file '{file}'.")

class security:
    def encrypt(files):
        global data
        key = Fernet.generate_key()
        fernet = Fernet(key)

        with open(files, "r") as file:
            data2 = json.loads(file.read())

            json_str = json.dumps(data2)
            encrypted = fernet.encrypt(json_str.encode())

        with open("keys.txt", "w") as ff:
            ff.write(key.decode())
        file5 = str(files)
        with open(file5, "w", encoding="utf-8") as f_write:
            f_write.write(encrypted.decode())
        if log:
            logging.info(f"File '{files}' encrypted and key saved to 'keys.txt'.")

    def decrypt(filess,keys):

        with open(keys, "r") as ff:
            keysi = ff.read()

        with open(filess, "r", encoding="utf-8") as f_write:
            token = f_write.read()

        fernet = Fernet(keysi)
        decrypted = fernet.decrypt(token)

        with open(filess, "w", encoding="utf-8") as f_write:
            f_write.write(decrypted.decode())
        if log:
            logging.info(f"File '{filess}' decrypted using key from '{keys}'.")

class LogManager:

    @staticmethod
    def setup(file):
        global log
        logging.basicConfig(
            filename=file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        log = True
        logging.info(f"Logging initialized with file '{file}'.")

    @staticmethod
    def see_log(file):
        if os.path.exists(file):
            with open(file, "r") as f:
                return f.read()
        else:
            return "Log file does not exist."

    @staticmethod
    def log_message(message):
        if log:
            logging.info(message)
        else:
            print("Logging is not enabled.")

class convert:
    def convert_to_excel(excel_file):
        global data
        df = pd.DataFrame.from_dict(data, orient='index').transpose()
        df.to_excel(excel_file, index=False)
        if log:
            logging.info(f"Data converted to Excel file '{excel_file}'.")

    def convert_to_csv(csv_file):
        global data
        df = pd.DataFrame.from_dict(data, orient='index').transpose()
        df.to_csv(csv_file, index=False)
        if log:
            logging.info(f"Data converted to CSV file '{csv_file}'.")
class search:
    def search_data(value):
        global data
        for key, werte in data.items():
            if value in werte:  
                return key, werte
        return None
class backup:
    def backup_data():
        global data
        backup_file = "backup.json"
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        if log:
            logging.info(f"Data backed up to '{backup_file}'.")
