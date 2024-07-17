# Simple logger for Dockerised applications.
import datetime


class Log:
    def __init__(self, source="Unknown - please code usage correctly"):
        self.source = source
        self.info("Log initialised.")

    def _getTimestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(self, error_type: str, message: str):
        print(f"{self._getTimestamp()} | {self.source} | {error_type} | {message}")

    def error(self, message: str):
        self._log("ERROR", message)

    def warning(self, message: str):
        self._log("WARNING", message)

    def info(self, message: str):
        self._log("INFO", message)
