import datetime

from iccore import time_utils
from iccore.data.units import timestamp_from_seconds_since


def test_timestamp_for_paths():

    test_time = datetime.datetime(2000, 5, 12, 14, 45, 23)

    time_str = time_utils.get_timestamp_for_paths(test_time)

    assert time_str == "20000512T14_45_23"


def test_timestamp_since():

    reference = "2001-01-01T00:00:00Z"
    count = 1000
    result = timestamp_from_seconds_since(count, reference)
    assert result.isoformat() == "2001-01-01T00:16:40+00:00"
