from typing import Iterable


def unpack_iterable(iterabl: list | tuple):
    """go from a nested iterable to one list containing every previously nested item; will not iterate on strings"""
    singles = []
    for l in iterabl:
        if type(l) != str and isinstance(l, Iterable):
            ls = unpack_iterable(l)
            singles.extend(ls)
        else:
            singles.append(l)
    return singles


def unpack_list(List: list | tuple):
    """go from a nested iterable to one list containing every previously nested item; will not iterate on strings\nis the same as unpack_iterable"""
    return unpack_iterable(List)
