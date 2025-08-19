import pickle
import os


def pickle_pack(data, path, append=False):
    if os.path.isfile(path) and append == True:
        org_data = pickle_unpack(path)
        org_type = type(org_data)
        if org_type in (tuple, list):
            if org_type == tuple:
                data = (*org_data, data)
            elif org_type == list:
                data = [*org_data, data]
        else:
            data = (org_data, data)
    with open(path, "wb") as f:
        pickle.dump(data, f)


def pickle_pack(data, path):
    with open(path, "wb") as f:
        pickle.dump(data, f)


def pickle_unpack(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data
