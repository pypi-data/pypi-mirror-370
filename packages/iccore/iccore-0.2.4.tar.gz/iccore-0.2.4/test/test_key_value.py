from iccore.serialization import key_value


def test_key_value():

    blocks_str = """
    key0 : val0
    key1 : val1
    key2 : val2

    key3 : val3
    key4 : val4
    key5 : val5
    """

    blocks = key_value.get_key_value_blocks(blocks_str)
    assert len(blocks) == 2
    assert blocks[1]["key3"] == "val3"
