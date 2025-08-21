"""
This module has milestone related project elements
"""

from datetime import datetime

from pydantic import BaseModel

from .person import Person


class Issue(BaseModel, frozen=True):
    """
    An issue is a user story or defect to work on
    """

    title: str = ""
    description: str = ""
    start_date: datetime | None = None
    due_date: datetime | None = None
    assignee: Person | None = None


class Milestone(BaseModel, frozen=True):
    """
    A milestone is a collection of work items with start and
    planned end dates
    """

    title: str = ""
    description: str = ""
    start_date: datetime | None = None
    due_date: datetime | None = None
    issues: list[Issue] = []
