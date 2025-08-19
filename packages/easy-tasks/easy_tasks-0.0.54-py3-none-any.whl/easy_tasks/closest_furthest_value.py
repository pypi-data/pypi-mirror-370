from typing import Any

def furthest_value_in_list(List: list, number: int | float) -> int | float:
    return max(List, key=lambda x: abs(x - number))


def closest_value_in_list(List: list, number: int | float) -> int | float:
    return min(List, key=lambda x: abs(x - number))


def furthest_value_in_dict(Dict: dict, number: int | float) -> int | float:
    return max(Dict, key=lambda x: abs(Dict[x] - number))


def closest_value_in_dict(Dict: dict, number: int | float) -> int | float:
    return min(Dict, key=lambda x: abs(Dict[x] - number))

def get_first_from_list(l: list) -> Any | None:
    return next(iter(l or []), None)
