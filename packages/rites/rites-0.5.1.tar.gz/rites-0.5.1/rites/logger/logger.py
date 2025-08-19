from ..rituals.printer import Printer

from datetime import datetime
from enum import Enum
from colored import Fore, Style

import atexit
import sys
import traceback
import os
import zipfile


class Logger:
    """ Logger Class

        Automatic log file creation and formatting

        Args:
            log_path (str): The path to the log file directory
            log_filename_format (str): The format of the log file name - default (log-%Y-%m-%d-%Hh-%Mm-%Ss)
            log_inline_format (str): The format for the time stamp on the log lines - default ([%Y-%m-%d %H:%M:%S])
            handles_zipping (bool): Only edit this variable if there are multiple loggers in the same folder
    """
    def __init__(self, log_path, max_logs=5, log_name="Unnamed Logger", log_level=2, log_console_format="%Y-%m-%d %H:%M:%S", handles_zipping=True, handles_exit_message=False):
        self.printer = Printer()
        self.log_path = log_path
        self.max_logs = max_logs
        self.name = log_name
        self.log_inline_format = log_console_format

        # Attributes
        self.handles_zipping = handles_zipping
        self.handles_exit_message = handles_exit_message
        self.should_log_to_file = True;
        self.should_print_to_console = True;

        atexit.register(self._exit_handler)

    def _get_inline_formatted_timestamp(self):
        now = datetime.now()
        return now.strftime(self.log_inline_format)

    def _writeToLogFile(self, txt):
        try:
            with open(f"{self.log_path}/latest.log", "a+") as log_file:
                log_file.write(txt)
                log_file.close()
        except FileNotFoundError:
            open(f"{self.log_path}/latest.log", "w").write(txt)

    def _exit_handler(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()

        if self.handles_exit_message is not True:
            if exc_type is None:
                self.success("Program exited successfully.")
            else:
                self.error("Program exited with an error.")
                self.error("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

        if self.handles_zipping is True:
            # Remove the oldest log if it exceeds max_logs
            oldest_log = f"{self.log_path}/log_{self.max_logs}.rar"
            if os.path.exists(oldest_log):
                os.remove(oldest_log)

            # Shift log files
            for i in range(self.max_logs - 1, -1, -1):
                current_log = f"{self.log_path}/log_{i}.rar"
                next_log = f"{self.log_path}/log_{i + 1}.rar"
                if os.path.exists(current_log):
                    os.rename(current_log, next_log)

            # Compress latest.log into log_0.rar
            latest_log = f"{self.log_path}/latest.log"
            if os.path.exists(latest_log):
                with zipfile.ZipFile(f"{self.log_path}/log_0.rar", 'w', zipfile.ZIP_DEFLATED) as log_archive:
                    log_archive.write(latest_log, arcname="latest.log")
                os.remove(latest_log)

    def printable_timestamp(self) -> str:
        """ Returns a colored console printable timestamp

            Returns:
                str: The formatted timestamp
        """
        return f"{Fore.white}[{Style.reset}{self.printer.get_color("gray")}{self._get_inline_formatted_timestamp()}{Style.reset}{Fore.white}]{Style.reset}"

    def formatted_name(self) -> str:
        """ Returns a printable colored name

        Returns:
            str: The formatted name
        """
        return f"{self.printer.get_color("gray")}{self.name}{Style.reset}"

    def add_custom(self, key: str, word: str, r: int, g: int, b: int):
        self.printer.add_style(key, word, r, g, b)

    def custom(self, style_key: str, *txt):
        """ Logs a custom styled message

        Args:
            style_key (str): The style_name saved in the logger's printer object
            txt (str): The message to log
        """
        # If there's only one argument, use it directly
        if len(txt) == 1:
            string = str(txt[0])
        else:
            # For multiple arguments, join them with spaces
            string = " ".join(str(item) for item in txt)

        msg =  f"{self.printable_timestamp()} [{self.formatted_name()}] {self.printer.get_style(style_key).get_str()} {string}"
        
        if self.should_print_to_console:
            print(msg)
        if self.should_log_to_file:
            self._writeToLogFile(msg)

    def warning(self, *txt):
        """ Logs a warning message

            Args:
                txt (str): The message to log
        """
        self.custom("warning", *txt)

    def error(self, *txt):
        """ Logs an error message

            Args:
                txt (str): The message to log
        """
        self.custom("error", *txt)

    def debug(self, *txt):
        """ Logs a debug message

            Args:
                txt (str): The message to log
        """
        self.custom("debug", *txt)

    def success(self, *txt):
        """ Logs a success message

            Args:
                txt (str): The message to log
        """
        self.custom("success", *txt)

    def info(self, *txt):
        """ Logs a success message

            Args:
                txt (str): The message to log
        """
        self.custom("info", *txt)

    def should_print(self, should_print: bool) -> "Logger":
        """ Sets whether the logger should print to console"""
        self.should_print_to_console = should_print
        return self

    def should_log(self, should_log: bool) -> "Logger":
        """ Sets whether the logger should log to file"""
        self.should_log_to_file = should_log
        return self
    
    def dont_show_exit_message(self) -> "Logger":
        """ Disables the exit message that is printed when the program exits"""
        self.handles_exit_message = False
        return self
    
    def disable(self) -> "Logger":
        """ Disables the logger from logging to file and printing to console"""
        self.should_print_to_console = False
        self.should_log_to_file = False
        return self
    
    def enable(self) -> "Logger":
        """ Enables the logger to log to file and print to console"""
        self.should_print_to_console = True
        self.should_log_to_file = True
        return self

def get_logger(log_path, max_logs=5, log_name="Unnamed Logger", log_level=2, log_console_format="%Y-%m-%d %H:%M:%S", handles_zipping=True):
    """Returns a Logger instance"""
    return Logger(log_path, max_logs, log_name, log_level, log_console_format, handles_zipping)


def get_sec_logger(log_path, log_name="Unnamed Secondary Logger", log_level=2, log_console_format="%Y-%m-%d %H:%M:%S"):
    """Returns a Logger instance without zipping enabled"""
    return Logger(log_path, log_name=log_name, log_level=log_level, log_console_format=log_console_format, handles_zipping=False, handles_exit_message=True)


def get_tertiary_logger(log_name="Unnamed Tertiary Logger", log_level=2, log_console_format="%Y-%m-%d %H:%M:%S"):
    """Returns a Logger instance without logging to file"""
    return Logger("", log_name=log_name, log_level=log_level, log_console_format=log_console_format, handles_zipping=False, handles_exit_message=True)