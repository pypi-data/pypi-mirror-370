from typing import Union, List, Literal, Any, Callable, Optional
import json
import hashlib


def recursive_update_dict(
    d1: dict, d2: dict, op: Callable[[Any, Any], Any], recurse: bool = True
) -> dict:
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        if d1 is None:
            return d2
        elif d2 is None:
            return d1
        else:
            return op(d1, d2)
    for k2, v2 in d2.items():
        if isinstance(v2, dict):
            v1 = d1.get(k2, {})
            if isinstance(v1, dict):
                if recurse:
                    if isinstance(recurse, int) and not isinstance(recurse, bool):
                        recurse -= 1
                    d1[k2] = recursive_update_dict(v1, v2, op, recurse)
                else:
                    d1[k2] = op(v1, v2)
            else:
                if k2 in d1:
                    d1[k2] = op(v1, v2)
                else:
                    d1[k2] = v2
        else:
            if k2 in d1:
                d1[k2] = op(d1[k2], v2)
            else:
                d1[k2] = v2
    return d1


def _generic_contains(c, key):
    if isinstance(c, dict):
        return key in c
    elif isinstance(c, (tuple, list)):
        return -len(c) <= key and key <= len(c) - 1
    else:
        return False


def travel_dict(
    d: dict,
    keylist: Optional[List[str]] = None,
    mode: Literal["r", "w"] = "r",
    strict: bool = False,
    default: Any = None,
) -> Union[Any, callable]:
    def __set(pointer, key, value):
        pointer[key] = value

    pointer = d
    if not keylist:
        keylist = []
    match mode:
        case "w":
            for key in keylist[:-1]:
                if not _generic_contains(pointer, key):
                    if strict:
                        raise KeyError(key)
                    pointer[key] = dict()
                pointer = pointer[key]
            return lambda v: __set(pointer, keylist[-1], v)
        case "r":
            for key in keylist:
                if not hasattr(pointer, "__contains__") or not _generic_contains(
                    pointer, key
                ):
                    if strict:
                        raise KeyError(key)
                    return default
                else:
                    pointer = pointer[key]
            return pointer


def jsondict_hash(d: dict):
    def _make_hash(o):
        if isinstance(o, list):
            return hash([_make_hash(e) for e in o])
        elif isinstance(o, dict):
            new_o = {k: _make_hash(v) for k, v in sorted(o.items())}
            return hash(tuple(frozenset(new_o.items())))
        else:
            return hash(o)

    dict_str = json.dumps(d, sort_keys=True, default=_make_hash)
    return hashlib.md5(dict_str.encode()).hexdigest()
