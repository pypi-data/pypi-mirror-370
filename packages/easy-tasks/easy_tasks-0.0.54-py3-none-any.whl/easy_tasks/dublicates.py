from typing import Iterable


def find_dublicates(List: Iterable):
    """Get a list of Dubs-objects. Dubs-objects have the attributes value, number_of_dublicates and indices.

    Will not find '1' as a dublicate of 1 since they are not the same...

    Args:
        List (Iterable): what you want to check

    Returns:
        list[Dubs]: Dubs-objects have the attributes value, number_of_dublicates and indices.
    """

    class Dubs:
        def __init__(self, value, number_of_dublicates, indices) -> None:
            self.value = value
            self.number_of_dublicates = number_of_dublicates
            self.indices = indices

    dublicates = []
    schon_drinnen = []
    for Element in List:
        number = List.count(Element)
        if number > 1:
            indices = [i for i, x in enumerate(List) if x == Element]
            if not any([x == Element for x in schon_drinnen]):
                obj = Dubs(Element, number, indices)
                dublicates.append(obj)
                schon_drinnen.append(Element)
    return dublicates


# def remove_dublicates(List: list):
#     """Remove dulicates in a list. Not in place!

#     Args:
#         List (list): what you want to check

#     Returns:
#         list: list without dublicates.
#     """

#     class Dubs:
#         def __init__(self, value, number_of_dublicates, indices) -> None:
#             self.value = value
#             self.number_of_dublicates = number_of_dublicates
#             self.indices = indices

#     List_ = List + []
#     dublicates = []
#     schon_drinnen = []
#     for Element in List_:
#         number = List_.count(Element)
#         if number > 1:
#             indices = [i for i, x in enumerate(List_) if x == Element]
#             if not any([x == Element for x in schon_drinnen]):
#                 obj = Dubs(Element, number, indices)
#                 dublicates.append(obj)
#                 schon_drinnen.append(Element)
#     all_indices_nested = [i.indices[1:] for i in dublicates]
#     all_indices = []
#     for e in all_indices_nested:
#         all_indices.extend(e)
#     all_indices.sort(reverse=True)
#     for i in all_indices:
#         List_.pop(i)
#     return List_

def remove_dublicates(List: list):
    seen = set()
    return [x for x in List if not (x in seen or seen.add(x))]
