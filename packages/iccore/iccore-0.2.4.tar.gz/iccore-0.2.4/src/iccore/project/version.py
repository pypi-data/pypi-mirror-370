"""
This module has functionality for representing and
manipulating project version numbers.
"""

from datetime import date

from pydantic import BaseModel


class Version(BaseModel, frozen=True):
    """
    Representation of a package version number.

    This resembles a semver scheme but doesn't necessarily
    follow one.

    Args:
        content (str): Version in string form x.y.zzzz
        scheme (str): The versioning scheme to use, 'semver' or 'date'

    Attributes:
        major (int): Major version number
        minor (int): Minor version number
        patch (int): Path version number
        scheme (str): Versioning scheme to use
    """

    major: int
    minor: int
    patch: int
    scheme: str = "semver"

    def as_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def increment(version: Version, field="patch", today=date.today()) -> Version:
    major = version.major
    minor = version.minor
    patch = version.patch

    if version.scheme == "semver":
        if field == "patch":
            patch += 1
        elif field == "minor":
            patch = 0
            minor += 1
        elif field == "major":
            major += 1
            minor = 0
            patch = 0
    elif version.scheme == "date":
        major = today.year - 2000
        minor = today.month
        if minor != version.minor:
            patch = 1
        else:
            patch = version.patch + 1
    return version.model_copy(update={"major": major, "minor": minor, "patch": patch})


def parse(content: str, scheme: str = "semver") -> Version:
    """
    Parse the version from the input content, assumes 'major.minor.patch' format.
    """
    major, minor, patch = content.split(".")
    return Version(major=int(major), minor=int(minor), patch=int(patch), scheme=scheme)
