# test_string_utils.py

from iccore.string_utils import split_strip_lines


def test_basic_strip_and_split():
    content = "  line one  \nline two \n   line three  "
    expected = ["line one", "line two", "line three"]
    assert expected == split_strip_lines(content)


def test_remove_empty_lines():
    content = "  line one  \n\n   \nline two"
    expected = ["line one", "line two"]
    assert expected == split_strip_lines(content)


def test_keep_empty_lines():
    content = "  line one  \n\n   \nline two"
    expected = ["line one", "", "", "line two"]
    assert expected == split_strip_lines(content, remove_empties=False)


def test_empty_string():
    content = ""
    expected = []
    assert expected == split_strip_lines(content)


def test_empty_string_keep_empties():
    content = ""
    expected = []
    assert expected == split_strip_lines(content, remove_empties=False)
