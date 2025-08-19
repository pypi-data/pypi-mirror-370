from typing import Dict


def dict_union(a: Dict, b: Dict):
    all_keys = sorted(set(a).union(b))
    return {key: (a.get(key), b.get(key)) for key in all_keys}
