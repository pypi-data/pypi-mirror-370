"""
Class representing a person, eg a user on a platform
"""

from pydantic import BaseModel


class Person(BaseModel, frozen=True):
    """
    A person class - used for referencing project
    contributors.
    """

    name: str = ""
    email: str = ""
    orcid: str = ""
    username: str
