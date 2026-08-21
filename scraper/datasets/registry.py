from typing import Callable

PARSERS: dict[str, Callable[[dict], list[dict]]] = {}


def register(type_name: str):
    def wrapper(func: Callable[[dict], list[dict]]):
        PARSERS[type_name] = func
        return func

    return wrapper
