from pathlib import Path
import pytest
import yaml

from iccore.serialization import read_yaml


def test_read_yaml():
    test_dir = Path(__file__).parent / "data"
    test_yaml = test_dir / "test_yaml.yml"

    content = read_yaml(test_yaml)
    print(content)
    assert content["test"] == "yaml"


def test_read_bad_yaml():
    test_dir = Path(__file__).parent / "data"
    test_yaml = test_dir / "bad_yaml.yml"

    with pytest.raises(yaml.YAMLError):
        read_yaml(test_yaml)
