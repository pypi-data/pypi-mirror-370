"""
Module for handling filtering of objects based on a tag
"""

from typing import NamedTuple


class Taggable:
    """
    Mixin for an entity with a tag
    """

    def has_tag(self, tag: str) -> bool:
        """
        True if the instance has the supplied tag
        """
        raise NotImplementedError()


class TagFilter(NamedTuple):
    """
    The filter to apply
    """

    includes: set[str]
    excludes: set[str]

    def __call__(self, taggable: Taggable) -> bool:
        """
        Return whether something with a tag is included in the includes list
        and not excluded from the exclides list.

        An empty includes list implies include all, unless excluded.
        """

        exclude = any(taggable.has_tag(t) for t in self.excludes)
        if self.includes:
            include = any(taggable.has_tag(t) for t in self.includes)
            return include and not exclude
        return not exclude
