
from functools import cached_property
import typing
from pydantic import BaseModel, ConfigDict, model_validator
from discord_embed_model.model import Embed, DiscordEmbed, to_pydantic_embed
import inspect
import parse

from discord_embed_model.utils import traverse_value

class Formatter(Embed):
    """
    template embed class
    """

    model_config = ConfigDict(
        ignored_types=(cached_property,),
        frozen=True,
    )

    @model_validator(mode="after")
    def _validate_model(self):
        fkeys_all, _ = self._format_fields
        if len(fkeys_all) == 0:
            raise ValueError("No fstring keys found.")
        
        return self

    
    def _format_sub_block(self, item : BaseModel, mapping : dict,**kwargs):
        ret = {}
        for k, v in mapping.items():
            if not v:
                ret = getattr(item, k)
            else:
                ret[k] = getattr(item, k).format(**kwargs)
        return ret

    @property
    def _fstring_maps(self):
        return self._format_fields[1]


    def format(self, **kwargs)-> DiscordEmbed:
        """
        Format the embed with the given kwargs, supports various types of formatting.

        method 1: using 'advance_prep' to format and validate input
        ```python
        template = Formatter(title="{template}")
        template.advance_prep("template", func=lambda x : x.upper())

        res: DiscordEmbed = template.format(template="word")
        ```

        this example makes sure the input is a str and uppercases it.

        |-----------------------------------------------------------------------|

        method 2: using `advance_prep` to pre process
        ```py
        template = Formatter(title="{template} {template_repeat}")
        template.advance_prep_lambda("template_repeat", func=lambda _, x : x["template"])

        res: DiscordEmbed = template.format(other_var="word")

        assert res.title == "word word"
        ```
        this example shows how to use `advance_prep` to repeat a variable.

        |-----------------------------------------------------------------------|

        method 3: using variable path
        ```py
        template = Formatter(title="{input.count} word")
        class Input:
            count : int

        res: DiscordEmbed = template.format(input=Input(count=2))

        assert res.title == "2 word"

        """

        kwargs = self._advance_prep(**kwargs)

        fmap_keys_ni_base = [
            x for x,y in self._fstring_maps.items() if isinstance(y, dict)
        ]
        output_base = self._embed_dict()
        for k, v in output_base.items():
            if not self._fstring_maps.get(k, False):
                continue
            else:
                v : str
                output_base[k] = v.format(**kwargs) 
                
        output_embed = DiscordEmbed.from_dict(output_base)

        for k in fmap_keys_ni_base:
            ret : dict = self._format_sub_block(
                getattr(self, k), self._fstring_maps[k], **kwargs
            )

            # ! this is to solve a case where color k is passed in empty
            if len(ret) == 0:
                continue

            match k:
                case "author":
                    output_embed.set_author(**ret)
                case "thumbnail":
                    output_embed.set_thumbnail(**ret)
                case "image":
                    output_embed.set_image(**ret)
                case "footer":
                    output_embed.set_footer(**ret)
                case _:
                    raise ValueError(f"Unknown key {k}")
                
        if self.fields is not None:
            for i, field in enumerate(self.fields):
                if self._fstring_maps["fields"][i]["name"]:
                    name = field.name.format(**kwargs)
                else:
                    name = field.name
                if self._fstring_maps["fields"][i]["value"]:
                    value = field.value.format(**kwargs)
                else:
                    value = field.value


                output_embed.add_field(
                    inline=field.inline,
                    name=name,
                    value=value
                )

        return output_embed

    #ANCHOR - advance prep
    def __init__(self, **data):
        super().__init__(**data)
        self._advance_preps : typing.Dict[str, typing.List[typing.Callable]] = {}

    def advance_prep(self, *args):
        """
        decorator version to register a function to be called before formatting.
        """

        def decorator(func):
            for arg in args:
                if arg not in self._advance_preps:
                    self._advance_preps[arg] = []
                if func in self._advance_preps[arg]:
                    return func
                self._advance_preps[arg].append(func)
            return func
        return decorator
    
    def advance_prep_lambda(self, *args, func):
        """
        non decorator version to register a function to be called before formatting.
        """

        for arg in args:
            if arg not in self._advance_preps:
                self._advance_preps[arg] = []
            if func in self._advance_preps[arg]:
                return func
            self._advance_preps[arg].append(func)

    def _advance_prep(self, **kwargs):
        """
        internal handler to prepare kwargs for formatting, check format() for more info.
        """

        new_kwargs = kwargs.copy()

        pending_fields = []

        # getattr recursively
        for key in self._format_fields[0]:
            if "." not in key:
                pending_fields.append(key)
                continue

            splitted = key.split(".")
            
            if splitted[0] not in kwargs:
                raise ValueError(f"Key {key} not found in kwargs.")
            baseval = kwargs[splitted[0]]

            for split in splitted[1:]:
                if isinstance(baseval, dict):
                    baseval = baseval[split]
                else:
                    baseval = getattr(baseval, split)
                
            new_kwargs[key] = baseval        

        for key, funcs in self._advance_preps.items():
            if key not in kwargs and key not in self._format_fields[0]:
                continue

            for func in funcs:
                if key in kwargs:
                    v = kwargs[key]
                else:
                    v = None

                # check how many args the function takes
                sig = inspect.signature(func)
                if len(sig.parameters) == 0:
                    vv =func()
                elif len(sig.parameters) == 1:
                    vv = func(v)
                else:
                    vv = func(v, kwargs)
                
                if vv is not None:
                    v = vv

            new_kwargs[key] = v

        return new_kwargs
                

    # ANCHOR parser
    def parseEmbed(self, embed : typing.Union[DiscordEmbed, Embed]):
        """
        parse a discord embed and extract the values
        """

        if isinstance(embed, DiscordEmbed):
            embed = to_pydantic_embed(embed)

        unconsumed_keys = set(self._format_fields[0])
        result_dict = {}

        for raw_str, addr in self._iter_fstring_fields():
            raw_field = traverse_value(embed, addr)

            single_bracketed = raw_str.startswith("{") \
                and raw_str.endswith("}")\
                and raw_str.count("{") == raw_str.count("}") == 1

            # check if all fields in this key are consumed
            field_vars = self._get_fstring_field(addr)

            # if all field vars are consumed
            if all(x in result_dict for x in field_vars):
                continue

            if single_bracketed:
                result_dict[raw_str[1:-1]] =  raw_field
                unconsumed_keys.remove(raw_str[1:-1])
                continue

            

            parsed = parse.parse(raw_str, raw_field)

            if parsed is None:
                continue
                
            result_dict.update(parsed.named)
            unconsumed_keys.difference_update(parsed.named.keys())
            
        return result_dict, unconsumed_keys
