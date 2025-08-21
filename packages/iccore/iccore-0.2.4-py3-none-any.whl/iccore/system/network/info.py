from pydantic import BaseModel


class NetworkInfo(BaseModel, frozen=True):

    hostname: str = ""
    ip_address: str = ""
