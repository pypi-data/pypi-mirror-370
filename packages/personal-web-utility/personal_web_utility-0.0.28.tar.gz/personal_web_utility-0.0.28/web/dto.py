from pydantic import BaseModel
from typing import Any


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str):
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


class CommonDto(BaseModel):
    class Config:
        alias_generator = to_lower_camel_case
        populate_by_name = True


class PaginationDto(CommonDto):
    page: int
    total: int
    items: list[Any]


class UnitDto(CommonDto):
    value: float
    label: str = "EUR"


class MoneyDto(UnitDto):
    label: str = "EUR"
