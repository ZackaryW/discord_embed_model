
from string import Formatter

def is_fstring(string : str):
    if not isinstance(string, str):
        return False
    try:
        Formatter().parse(string)
        return True
    except ValueError:
        return False

def extract_fstring_keys(string : str):
    if not isinstance(string, str):
        return []
    try:
        return [x[1] for x in Formatter().parse(string) if x[1] is not None]
    except ValueError:
        return []

def hex_to_rgb(hex : int):
    return (hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF

def traverse_value(base, keys : list):
    for key in keys:
        if isinstance(base, list):
            base = base[int(key)]
        elif isinstance(base, dict):
            base = base[key]
        else:
            base = getattr(base, key)
    return base

