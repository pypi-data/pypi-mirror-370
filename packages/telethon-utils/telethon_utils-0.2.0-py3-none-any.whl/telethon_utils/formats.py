from typing import TypeVar

T = TypeVar("T")


def reformat_to_pait_list(items: list[T]) -> list[list[T]]:
    _tmp: list[T] = []

    final: list[list[T]] = []
    for i, item in enumerate(items):
        _tmp.append(item)
        if len(_tmp) == 2 or i + 1 == len(items):
            final.append(_tmp.copy())
            _tmp = []

    return final
