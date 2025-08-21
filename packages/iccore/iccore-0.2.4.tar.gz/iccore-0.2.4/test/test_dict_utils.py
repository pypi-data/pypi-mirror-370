from iccore import dict_utils


def test_merge_dicts():

    a = {"a": 1, "b": 2}
    b = {"c": 3, "d": 4}
    merged = dict_utils.merge_dicts(a, b)
    assert merged == {"a": 1, "b": 2, "c": 3, "d": 4}


def test_copy_without_type():

    content = {"a": 1, "b": [2, 3, 4], "c": 5}
    without_t = dict_utils.copy_without_type(content, list)
    assert without_t == {"a": 1, "c": 5}


def test_split_dict_on_type():

    content = {"a": 1, "b": [2, 3, 4], "c": 5}
    without_t, with_t = dict_utils.split_dict_on_type(content, list)
    assert with_t == {"b": [2, 3, 4]}
    assert without_t == {"a": 1, "c": 5}


def test_permute():

    content = {"a": 1, "b": [2, 3], "c": ["x", "y"]}
    expected = [
        {"a": 1, "b": 2, "c": "x"},
        {"a": 1, "b": 2, "c": "y"},
        {"a": 1, "b": 3, "c": "x"},
        {"a": 1, "b": 3, "c": "y"},
    ]
    permutations = dict_utils.permute(content)
    for permutation in expected:
        assert permutation in permutations


def test_nested_sort():

    data = {
        "layer0": {
            "field0": [2, 5, 1, 3, 4],
            "field1": [1, 2, 3, 4, 5],
            "field2": [
                ["a", "b", "c"],
                ["d", "e", "f"],
                ["h", "i", "j"],
                ["k", "l", "m"],
                ["o", "p", "q"],
            ],
        },
        "layer1": {
            "field0": [2, 5, 1, 3, 4],
            "field1": [1, 2, 3, 4, 5],
            "field2": [
                ["a", "b", "c"],
                ["d", "e", "f"],
                ["h", "i", "j"],
                ["k", "l", "m"],
                ["o", "p", "q"],
            ],
        },
    }

    dict_utils.inplace_sort_nested(data, excludes=("field1"))

    assert data["layer0"]["field0"] == (1, 2, 3, 4, 5)
    assert data["layer0"]["field1"] == [1, 2, 3, 4, 5]
    assert data["layer0"]["field2"][0] == ["h", "i", "j"]
    assert data["layer0"]["field2"][1] == ["a", "b", "c"]
