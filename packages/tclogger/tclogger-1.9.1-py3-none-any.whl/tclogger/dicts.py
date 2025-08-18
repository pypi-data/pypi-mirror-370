from typing import Union
from functools import partial

from .types import KeysType
from .matches import MatchKeyFuncType, match_key


class CaseInsensitiveDict(dict):
    """Inspired by: https://stackoverflow.com/a/32888599"""

    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(self.__class__._k(key))

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(self.__class__._k(key))

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(self.__class__._k(key))

    def has_key(self, key):
        return super(CaseInsensitiveDict, self).has_key(self.__class__._k(key))

    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(
            self.__class__._k(key), *args, **kwargs
        )

    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(
            self.__class__._k(key), *args, **kwargs
        )

    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(
            self.__class__._k(key), *args, **kwargs
        )

    def update(self, E={}, **F):
        super(CaseInsensitiveDict, self).update(self.__class__(E))
        super(CaseInsensitiveDict, self).update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)


def dict_get(d: dict, keys: KeysType, default=None, sep: str = "."):
    if isinstance(keys, str) and sep:
        keys = keys.split(sep)
    for key in keys:
        if (isinstance(d, dict) and key in d) or (isinstance(d, list) and key < len(d)):
            d = d[key]
        else:
            return default
    return d


def dict_set(d: dict, keys: KeysType, value, sep: str = "."):
    if isinstance(keys, str) and sep:
        keys = keys.split(sep)
    for key in keys[:-1]:
        if isinstance(d, dict):
            d = d.setdefault(key, {})
        elif isinstance(d, list):
            if key >= len(d):
                d.extend([{} for _ in range(key - len(d) + 1)])
            d = d[key]

    if isinstance(d, dict):
        d[keys[-1]] = value
    elif isinstance(d, list):
        if keys[-1] >= len(d):
            d.extend([None for _ in range(keys[-1] - len(d) + 1)])
        d[keys[-1]] = value


def dict_get_all(
    d: Union[dict, list],
    key: KeysType,
    value,
    ignore_case: bool = False,
    use_regex: bool = False,
    sep: str = ".",
    index_list: bool = False,
): ...


def inner_dict_set_all(
    d: Union[dict, list],
    key: KeysType,
    value,
    index_list: bool,
    keys_path: list,
    match_func: MatchKeyFuncType = match_key,
):
    """recursive helper function for `dict_set_all()`"""
    if isinstance(d, dict):
        for k, v in d.items():
            new_keys_path = keys_path + [k]
            if match_func(new_keys_path, key):
                d[k] = value
            if isinstance(v, (dict, list)):
                inner_dict_set_all(
                    v,
                    key,
                    value,
                    index_list=index_list,
                    keys_path=new_keys_path,
                    match_func=match_func,
                )

    elif isinstance(d, list):
        for idx, item in enumerate(d):
            if index_list:
                new_keys_path = keys_path + [idx]
            else:
                new_keys_path = keys_path

            if match_func(new_keys_path, key):
                d[idx] = value

            if isinstance(item, (dict, list)):
                inner_dict_set_all(
                    item,
                    key,
                    value,
                    index_list=index_list,
                    keys_path=new_keys_path,
                    match_func=match_func,
                )


def dict_set_all(
    d: Union[dict, list],
    key: KeysType,
    value,
    index_list: bool = False,
    ignore_case: bool = False,
    use_regex: bool = False,
    sep: str = ".",
):
    """
    Recursively replace values of all items with field `key` in a dict/list.
    Args:
    - d: input dict or list
    - key: key (pattern) to match and set
    - value: value to set for all matching keys
    - ignore_case: ignore case of key when matching
    - use_regex: use regex to match key
    - sep: separator to use for chaining keys
    - index_list: if True, include list indices in the keys path when matching
    """
    match_func = partial(
        match_key,
        ignore_case=ignore_case,
        use_regex=use_regex,
        sep=sep,
    )
    inner_dict_set_all(
        d,
        key,
        value,
        index_list=index_list,
        keys_path=[],
        match_func=match_func,
    )
