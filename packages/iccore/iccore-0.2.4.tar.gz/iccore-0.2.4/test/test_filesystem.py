import os
import shutil

from iccore.filesystem import copy, replace_in_file, file_contains_string
from iccore.test_utils import get_test_output_dir, get_test_data_dir


def test_filesystem():

    data_dir = get_test_data_dir()
    output_dir = get_test_output_dir()
    os.makedirs(output_dir)

    target_file = output_dir / "file_replacement.md"
    copy(data_dir / "file_replacement.md", target_file)

    source_term = "visibility: 'public'"
    replace_term = "tags: ['public']"

    replace_in_file(target_file, source_term, replace_term)

    assert file_contains_string(target_file, replace_term)

    shutil.rmtree(output_dir)
