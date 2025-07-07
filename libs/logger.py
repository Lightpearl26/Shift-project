#-*- coding: utf-8 -*-

"""
SHIFT PROJECT libs
____________________________________________________________________________________________________
logger lib
version : 1.0
____________________________________________________________________________________________________
This Lib contains all logging system of the game
____________________________________________________________________________________________________
(c) Lafiteau Franck
"""

# import external modules
from os.path import join, getctime, exists
from os import listdir, mkdir, remove
from threading import current_thread
from time import ctime, localtime

# Create module constants
LOG_FOLDER: str = join("cache", "logs")

# Create object
class Logger:
    """
    Logger object

    This object represent the logger of the game

    attributs:
        - log_folder: str = Directory of logs
        - logs: list[dict[str, str]] = list of all logs
    """
    def __init__(self, folder: str=LOG_FOLDER) -> None:
        self.log_folder: str = folder
        self.logs: list[dict[str, str]] = []

        # We remove the Latest.log from the folder
        if exists(join(folder, "Latest.log")):
            log_date = localtime(getctime(join(folder, "Latest.log")))
            date = f"{log_date[0]}-{log_date[1]}-{log_date[2]}"
            if not exists(join(folder, date)):
                mkdir(join(folder, date))
            date_folder = join(folder, date)
            duplicates = len(listdir(date_folder))+1
            with open(join(folder, "Latest.log"), "r", encoding="utf-8") as latest:
                with open(join(date_folder, f"{duplicates}.log"), "w", encoding="utf-8") as logfile:
                    logfile.write(latest.read())
                    logfile.close()
                latest.close()
            remove(join(folder, "Latest.log"))

        # log that the logger is initialized
        self.debug("Logger initialized")

    # create logging methods
    def debug(self, message: str) -> str:
        """
        this methods logs a debug message and return the string of the corresponding log
        """
        level = "Debug"
        time = ctime()
        threadname = current_thread().name
        log = {
            "level": level,
            "time": time,
            "thread": threadname,
            "message": message
        }
        self.logs.append(log)
        strflog = f"[ {level} ][ {threadname} ][ {time} ]: {message}"
        return strflog

    def info(self, message: str) -> str:
        """
        this methods logs a info message and return the string of the corresponding log
        """
        level = "Info"
        time = ctime()
        threadname = current_thread().name
        log = {
            "level": level,
            "time": time,
            "thread": threadname,
            "message": message
        }
        self.logs.append(log)
        strflog = f"[ {level} ][ {threadname} ][ {time} ]: {message}"
        return strflog

    def warning(self, message: str) -> str:
        """
        this methods logs a debug message and return the string of the corresponding log
        """
        level = "Warning"
        time = ctime()
        threadname = current_thread().name
        log = {
            "level": level,
            "time": time,
            "thread": threadname,
            "message": message
        }
        self.logs.append(log)
        strflog = f"[ {level} ][ {threadname} ][ {time} ]: {message}"
        return strflog

    def error(self, message: str) -> str:
        """
        this methods logs a debug message and return the string of the corresponding log
        """
        level = "Error"
        time = ctime()
        threadname = current_thread().name
        log = {
            "level": level,
            "time": time,
            "thread": threadname,
            "message": message
        }
        self.logs.append(log)
        strflog = f"[ {level} ][ {threadname} ][ {time} ]: {message}"
        return strflog

    def fatal(self, threadname: str, message: str) -> str:
        """
        this methods logs a debug message and return the string of the corresponding log
        """
        level = "Fatal"
        time = ctime()
        log = {
            "level": level,
            "time": time,
            "thread": threadname,
            "message": message
        }
        self.logs.append(log)
        strflog = f"[ {level} ][ {threadname} ][ {time} ]: {message}"
        return strflog

    def get_strflog(self, log: dict[str, str]) -> str:
        """
        get the string format of a log
        """
        strflog = f"[ {log["level"]} ][ {log["thread"]} ][ {log["time"]} ]: {log["message"]}"
        return strflog

    def save(self) -> None:
        """
        Save logs to Latest.log
        """
        with open(join(self.log_folder, "Latest.log"), "w", encoding="utf-8") as file:
            for log in self.logs:
                file.write(self.get_strflog(log)+"\n")
            file.close()
