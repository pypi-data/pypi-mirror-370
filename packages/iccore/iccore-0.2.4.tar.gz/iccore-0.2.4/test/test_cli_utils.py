from iccore.cli_utils import serialize_args, deserialize_args


def test_cli_utils():

    cli_args = {"arg1": "val1", "arg2": "val2", "arg3": None}
    serialized = serialize_args(cli_args)
    assert serialized == " --arg1 val1 --arg2 val2 --arg3 "


def test_regular_args():
    cli = "program --user Alice --age 30 --admin"
    assert deserialize_args(cli) == {"user": "Alice", "age": "30", "admin": None}


def test_empty_arguments():
    cli_args = ""
    expected_output = {}
    assert deserialize_args(cli_args) == expected_output


def test_only_flags():
    cli = "program --verbose --debug"
    assert deserialize_args(cli) == {"verbose": None, "debug": None}
