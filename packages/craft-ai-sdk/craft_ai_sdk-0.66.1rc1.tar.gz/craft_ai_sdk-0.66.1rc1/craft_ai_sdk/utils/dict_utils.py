from typing import Union


def remove_none_values(obj: dict):
    return {key: value for key, value in obj.items() if value is not None}


def remove_keys_from_dict(dictionnary: dict, paths_to_remove: Union[set, None] = None):
    if dictionnary is None:
        return None

    paths_to_remove = paths_to_remove or set()
    returned_dictionnary = dictionnary.copy()

    for path in paths_to_remove:
        key, _, subpath = path.partition(".")
        if subpath == "":
            returned_dictionnary.pop(key, None)
        elif isinstance(returned_dictionnary.get(key), dict):
            returned_dictionnary[key] = remove_keys_from_dict(
                returned_dictionnary[key], {subpath}
            )

    return returned_dictionnary
