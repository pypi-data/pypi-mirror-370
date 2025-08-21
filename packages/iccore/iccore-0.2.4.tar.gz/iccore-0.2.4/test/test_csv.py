from pydantic import BaseModel
import csv
import os
import shutil

from iccore.serialization import csv_utils
from iccore.test_utils import get_test_output_dir


class SimpleModel(BaseModel):

    field0: int = 0
    field1: str = "test"
    field2: float = 0.345


def test_csv_write_read():

    output_path = get_test_output_dir() / "test.csv"
    os.makedirs(output_path.parent, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        print(csv_utils.get_fieldnames(SimpleModel))
        writer = csv.DictWriter(f, fieldnames=csv_utils.get_fieldnames(SimpleModel))

        writer.writeheader()
        for idx in range(3):
            writer.writerow(SimpleModel().model_dump())

    with open(output_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        models = [SimpleModel(**row) for row in reader]

    assert len(models) == 3
    assert models[0].field0 == 0
    assert models[0].field1 == "test"
    assert models[1].field2 == 0.345

    shutil.rmtree(output_path.parent)


def test_csv_string_ops():

    assert csv_utils.get_header_str(SimpleModel, ", ") == "field0, field1, field2"

    assert csv_utils.get_line(SimpleModel(), ", ") == "0, test, 0.345"
