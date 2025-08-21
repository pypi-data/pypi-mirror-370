from logngraph.log.levels import *
from datetime import datetime
import sys

__all__ = [
    "Logger",
]


class Logger:
    def __init__(self, name: str, filename: str = None, level: int = INFO):
        """
        Logger class

        :param name: Name of the logger
        :param filename: Filename of the log file (optional)
        :param level: Logging level (can be changed using Logger.set_level)
        """
        self.name = name
        self.filename = filename
        self.file = open(filename, "w") if filename else None
        self.stdout = sys.stdout
        self.level = level

        self.print("\x1b[38;5;165m\x1b[1mStarted logger!\x1b[0m\n")

    @property
    def dtstr(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

    def set_level(self, level: int) -> bool:
        if 0 <= level <= 6:
            self.level = level
            return True
        return False

    def print(self, text: str) -> None:
        if self.file is not None:
            self.file.write(text)
        self.stdout.write(text)

    def trace(self, msg: str) -> None:
        if self.level <= TRACE:
            log = f"\x1b[38;5;123mTRACE: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def debug(self, msg: str) -> None:
        if self.level <= DEBUG:
            log = f"\x1b[38;5;11mDEBUG: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def info(self, msg: str) -> None:
        if self.level <= INFO:
            log = f"\x1b[38;5;251mINFO:  {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def warn(self, msg: str) -> None:
        if self.level <= WARNING:
            log = f"\x1b[38;5;208m\x1b[1mWARN:  {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def error(self, msg: str) -> None:
        if self.level <= ERROR:
            log = f"\x1b[38;5;196m\x1b[1mERROR: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def fatal(self, msg: str) -> None:
        if self.level <= FATAL:
            log = f"\x1b[38;5;124m\x1b[1mFATAL: {self.dtstr}: [{self.name}]: {msg}\x1b[0m\n"
            self.print(log)

    def __del__(self) -> None:
        self.print("\x1b[38;5;165m\x1b[1mShutting down logger...\x1b[0m\n")
        if self.file is not None:
            self.file.close()


if __name__ == "__main__":
    # Testing field
    logger = Logger(__name__, "test.log", TRACE)
    logger.trace("trace")
    logger.debug("debug")
    logger.info("info")
    logger.warn("warn")
    logger.error("error")
    logger.fatal("fatal")

