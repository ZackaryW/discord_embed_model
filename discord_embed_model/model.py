
from functools import cached_property
from discord import Embed
from discord_embed_model.extra import EmbedData, EmbedExtra
from discord_embed_model.utils import extract_vars

class EmbedModel:
    def __init__(self) -> None:
        self.__template_map = {}

        self.__template : EmbedData = EmbedData()
        object.__setattr__(self.__template, "_on_change_callback", self.__template_change_callback)

    @cached_property
    def _allvars(self):
        allvars = []
        for (v, _) in self.__template_map.values():
            allvars.extend(v)
        return set(allvars)

    @property
    def template(self):
        return self.__template
    
    def __template_change_callback(self, embeddata : EmbedData, name: str, value):
        if not isinstance(value, str):
            return

        vars = extract_vars(value)
        self.__template_map[name] = vars, value
        self.__dict__.pop("_allvars", None)
        

    def format(
        self, **kwargs
    ):
        embed ={}
        for key, (fvars, fraw) in self.__template_map.items():
            if len(fvars) == 0:
                fgen = fraw
            else:
                fgen = fraw.format(**kwargs)

            self.__set_t_val(key, fgen, embed)
        
        return Embed.from_dict(embed)

    def __set_t_val(self, key, value, target):
        if "::" in key:

            splitted = key.split("::")
            for i, k in enumerate(splitted[:-1]):
                nexti = i + 1
                nextk : str= splitted[nexti] if nexti < len(splitted) else None
                assignNext = None
                if nextk is not None:
                    assignNext = list if nextk.isnumeric() else dict

                if isinstance(target, list) and len(target) > int(k):
                    target = target[int(k)]
                elif isinstance(target, dict) and k in target:
                    target = target[k]
                elif isinstance(target, list):
                    while len(target) <= int(k):
                        target.append(assignNext())
                    target = target[int(k)]
                elif isinstance(target, dict):
                    while k not in target:
                        target[k] = assignNext()
                    target = target[k]
                else:
                    target = getattr(target, k)
            
            key = splitted[-1]

        if isinstance(target, list):
            target[int(key)] = value
        elif isinstance(target, dict):
            target[key] = value
        else:
            setattr(target, key, value)


    def extract(
        self, embed : Embed | EmbedData | EmbedExtra
    ):
        # TODO
        pass