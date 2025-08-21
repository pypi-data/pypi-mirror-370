import inspect
from pathlib import Path
import os


def get_test_data_dir() -> Path:

    calling_frame = inspect.stack()[1]
    calling_file = Path(calling_frame.filename)

    parent = calling_file.parent
    while parent:
        if parent.name == "test":
            return parent / "data"
        parent = parent.parent

    return calling_file.parent / "data"


def get_test_output_dir() -> Path:

    calling_frame = inspect.stack()[1]
    calling_func = calling_frame.function
    return Path(os.getcwd()) / f"test_output/{calling_func}"
