import os
import datetime
import atexit

class Logger:
    ANSI_RESET = "\033[0m"
    ANSI_GREEN = "\033[32m"
    ANSI_YELLOW = "\033[33m"
    ANSI_BLUE = "\033[34m"
    ANSI_RED = "\033[31m"
    def __init__(self, log_file=None):
        self.log_file = log_file
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            self.file = open(log_file, 'a', buffering=1)  # line-buffered
            atexit.register(self.file.close)
        else: self.file = None
    def _timestamp(self):  return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def _log(self, tag, message, color=None):
        ts = self._timestamp()
        formatted = f"[{ts}] [{tag}] {message}"
        if self.file: self.file.write(formatted + '\n')
        else:
            if color: formatted = f"{color}{tag}{self.ANSI_RESET} {message}"
            print(formatted)

    def info(self, message:str, user:str|None=None):
        if user: message = user+" - "+message
        self._log("INFO", message, self.ANSI_BLUE)

    def warn(self, message: str, user: str | None = None):
        if user: message = user + " - " + message
        self._log("WARN", message, self.ANSI_YELLOW)

    def ok(self, message: str, user: str | None = None):
        if user: message = user + " - " + message
        self._log("OK", message, self.ANSI_GREEN)

    def error(self, message: str, user: str | None = None):
        if user: message = user + " - " + message
        self._log("ERROR", message, self.ANSI_RED)