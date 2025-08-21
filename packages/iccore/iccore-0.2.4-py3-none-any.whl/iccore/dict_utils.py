"""
This module has some basic utilities for working with dictionaries.
"""

from itertools import product


def copy_without_type(source: dict, omit_type: type = list) -> dict:
    """
    Make and return a copy of the input source dict
    but don't include any items with given value type.
    """
    ret = {}
    for key, value in source.items():
        if not isinstance(value, omit_type):
            ret[key] = value
    return ret


def merge_dicts(x: dict, y: dict) -> dict:
    """
    Shallow merge dicts x and y. This function is just to give
    the operation a more explicit/obvious name
    """
    return {**x, **y}


def split_dict_on_type(source: dict, split_type: type = list):
    """
    Given a dict, return two dicts. One with item values of split_type
    type and one without.
    """

    without_type = copy_without_type(source, split_type)
    with_type = source
    for key in without_type:
        del with_type[key]
    return without_type, with_type


def get_key_or_default_int(content: dict, key: str, default: int) -> int:
    """
    Given a dicttionary return the request key or else the provided default int.
    """

    if key in content:
        return int(content[key])
    return default


def permute(source: dict) -> list[dict]:
    """
    Given a dict containing list/tuple values, return a list of all
    permutations as dictionaries.
        source = {"a": 1,
                  "b": [2, 3],
                  "c": ["x", "y"]} ->
            [{'a': 1, 'b': 2, 'c': 'x'},
            {'a': 1, 'b': 2, 'c': 'y'},
            {'a': 1, 'b': 3, 'c': 'x'},
            {'a': 1, 'b': 3, 'c': 'y'}]
    """
    products = product(
        *[v if isinstance(v, (list, tuple)) else [v] for v in source.values()]
    )
    return [dict(zip(source.keys(), values)) for values in products]


def inplace_sort_nested(data: dict, excludes: tuple[str] | None = None):
    """
    Sort the first child entry in a dict and propagate the sort order to
    the others
    """

    for outer_key, outer_values in data.items():
        sortable = []
        for key, value in outer_values.items():
            if not excludes or (key not in excludes):
                sortable.append(value)
        sorted_vals = list(zip(*sorted(zip(*sortable))))
        count = 0
        for key, value in outer_values.items():
            if not excludes or (key not in excludes):
                data[outer_key][key] = sorted_vals[count]
                count += 1
