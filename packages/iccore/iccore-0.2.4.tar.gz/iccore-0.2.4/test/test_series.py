import numpy as np

from iccore.data.measurement import Measurement
from iccore.data import Series, Array
from iccore.data.series import append_array, insert_series


def xtest_append_array():

    a = Array(quantity=Quantity(name="a"), data=np.array([1, 2, 3, 4]))

    b = Array(quantity=Quantity(name="a"), data=np.array([5, 6, 7, 8]))

    combined = append_array(a, b)
    assert list(combined.data) == [1, 2, 3, 4, 5, 6, 7, 8]

    c = Array(quantity=Quantity(name="c"), data=np.array([[1, 2, 3], [4, 5, 6]]))

    d = Array(quantity=Quantity(name="d"), data=np.array([[7, 8, 9], [10, 11, 12]]))

    combined_2d = append_array(c, d)
    expected = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]

    for idx, item in enumerate(combined_2d.data):
        assert list(item) == expected[idx]


def xtest_insert_array():

    a = Array(quantity=Quantity(name="a"), data=np.array([1, 2, 5, 6]))

    b = Array(quantity=Quantity(name="a"), data=np.array([3, 4]))

    combined = insert_array(a, b, 2)
    assert list(combined.data) == [1, 2, 3, 4, 5, 6]

    c = Array(
        quantity=Quantity(name="c"), data=np.array([[1, 2, 3], [4, 5, 6], [13, 14, 15]])
    )

    d = Array(quantity=Quantity(name="d"), data=np.array([[7, 8, 9], [10, 11, 12]]))

    combined_2d = insert_array(c, d, 2)
    expected = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]

    for idx, item in enumerate(combined_2d.data):
        assert list(item) == expected[idx]


def xtest_insert_series():

    series = Series(
        x=Array(quantity=Quantity(name="x"), data=np.array([1, 2, 3, 6, 7])),
        y=Array(quantity=Quantity(name="y"), data=np.array(["a", "b", "c"])),
        values=[
            Array(
                quantity=Quantity(name="v"),
                data=np.array(
                    [[1, 2, 3], [4, 5, 6], [7, 8, 9], [16, 17, 18], [19, 20, 21]]
                ),
            )
        ],
    )

    new = Series(
        x=Array(quantity=Quantity(name="x"), data=np.array([4, 5])),
        y=Array(quantity=Quantity(name="y"), data=np.array(["a", "b", "c"])),
        values=[
            Array(
                quantity=Quantity(name="v"), data=np.array([[10, 11, 12], [13, 14, 15]])
            )
        ],
    )

    merged = insert_series(series, new)

    assert list(merged.x.data) == [1, 2, 3, 4, 5, 6, 7]
