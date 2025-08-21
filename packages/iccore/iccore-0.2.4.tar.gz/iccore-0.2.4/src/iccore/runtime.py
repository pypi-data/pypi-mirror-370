"""
This module is used to maintain a global application state
"""

import logging

logger = logging.getLogger(__name__)


class ctx:
    """
    This class is used to set a global state in
    the application specifying whether it should
    modify real system resources (filesystem, network, shell)
    or not.

    There are three dry run levels:

    * 0: Off - resources can be modified
    * 1: Read only - resources can be read but not changed
    * 2: Full - resources can not be accessed at all

    A buffer of commands not run is also maintained - this can be useful
    for unit testing.
    """

    _DRY_RUN: int = 0
    _CMD_BUFFER: list[str] = []

    @staticmethod
    def set_is_dry_run(value: int = 2):
        ctx._DRY_RUN = value

    @staticmethod
    def set_is_read_only():
        ctx._DRY_RUN = 1

    @staticmethod
    def is_dry_run():
        return ctx._DRY_RUN > 0

    @staticmethod
    def can_read():
        return ctx._DRY_RUN <= 1

    @staticmethod
    def can_modify():
        return ctx._DRY_RUN == 0

    @staticmethod
    def add_cmd(cmd: str):
        ctx._CMD_BUFFER.append(cmd)
        logger.info(cmd)

    @staticmethod
    def clear_buffer():
        ctx._CMD_BUFFER.clear()

    @staticmethod
    def get_buffer():
        return ctx._CMD_BUFFER
