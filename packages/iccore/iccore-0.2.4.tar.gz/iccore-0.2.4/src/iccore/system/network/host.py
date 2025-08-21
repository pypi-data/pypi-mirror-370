from pydantic import BaseModel


class Host(BaseModel, frozen=True):
    """
    Class representing some network location - can
    be used to put or get files to or from that location
    """

    name: str
