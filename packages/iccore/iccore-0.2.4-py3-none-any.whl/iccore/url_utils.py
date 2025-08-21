from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Url:
    scheme: str
    netloc: str
    path: str = ""
    params: str = ""
    query: str = ""
    fragment: str = ""


def parse_url(url_str: str) -> Url:
    """
    Split the url into its components
    """
    parsed = urlparse(url_str)
    return Url(
        scheme=parsed.scheme,
        netloc=parsed.netloc,
        path=parsed.path,
        params=parsed.params,
        query=parsed.query,
        fragment=parsed.fragment,
    )
