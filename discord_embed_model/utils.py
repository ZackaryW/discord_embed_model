import string

def extract_vars(fstring:str):
    if "{" not in fstring:
        return []

    # string.formatter
    f= string.Formatter().parse(fstring)
    return [x[1] for x in f if x[1] is not None]

def dict_has_value(key : str, data :dict):
    splitted = key.split("::")
    target = data
    for k in splitted:
        if isinstance(target, list) and len(target) > int(k):
            target = target[int(k)]
        elif isinstance(target, dict) and k in target:
            target = target[k]
        elif hasattr(target, k):
            target = getattr(target, k)
        else:
            return False
        
    return True    

        