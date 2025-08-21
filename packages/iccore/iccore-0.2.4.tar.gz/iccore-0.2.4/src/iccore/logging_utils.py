import logging


def setup_default_logger(log_filename: str | None = None):
    fmt = "%(asctime)s%(msecs)03d | %(filename)s:%(lineno)s:%(funcName)s | %(message)s"
    logging.basicConfig(
        filename=log_filename,
        filemode="w",
        format=fmt,
        datefmt="%Y%m%dT%H:%M:%S:",
        level=logging.INFO,
    )


class LogLine:
    """
    Helper class to represent a log line
    """

    def __init__(self, timestamp: float, thread_id: int, message: str):
        self.timestamp = timestamp
        self.message = message
        self.thread_id = thread_id

    def __str__(self):
        return f"{self.timestamp} | {self.thread_id} | {self.message}"
