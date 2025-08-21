from typing import Type

from pydantic import BaseModel


def get_fieldnames(class_t: Type) -> list[str]:
    return list(class_t.model_fields)


def get_header_str(class_t: Type, delimiter: str = ",") -> str:
    return delimiter.join(get_fieldnames(class_t))


def get_line(model: BaseModel, delimiter: str = ",") -> str:
    return delimiter.join([str(v) for v in model.model_dump().values()])
