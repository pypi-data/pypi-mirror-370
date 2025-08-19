from natsort import natsorted


def sorted_dict(dic: dict, for_key_not_value: bool = False, reverse: bool = False):
    if for_key_not_value:
        dic_sorted = {k: v for k, v in natsorted(dic.items(), key=lambda item: item[0], reverse=reverse)}
    else:
        dic_sorted = {k: v for k, v in natsorted(dic.items(), key=lambda item: item[1], reverse=reverse)}
    return dic_sorted
