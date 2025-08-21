from datetime import date

from iccore.project import version, Version


def test_version():

    ver_str = "1.2.345"
    v = version.parse(ver_str)

    v = version.increment(v, field="patch")
    assert v.as_string() == "1.2.346"

    v = version.increment(v, field="minor")
    assert v.as_string() == "1.3.0"

    v = version.increment(v, field="patch")
    v = version.increment(v, field="major")
    assert v.as_string() == "2.0.0"


def test_version_basic():

    v = version.parse("0.0.1")
    v = version.increment(v, field="patch")
    assert v.as_string() == "0.0.2"


def test_version_date():

    ver_str = "25.4.2"

    v = version.parse(ver_str, "date")

    v = version.increment(v, today=date(2025, 4, 1))
    assert v.as_string() == "25.4.3"

    v = version.increment(v, today=date(2026, 2, 1))
    assert v.as_string() == "26.2.1"
