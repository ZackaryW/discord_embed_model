
import datetime
from functools import cached_property
import typing
from pydantic import BaseModel, ConfigDict, Field as _Field, field_validator
from discord import Embed as DiscordEmbed

from discord_embed_model.utils import extract_fstring_keys, hex_to_rgb

class _Base(BaseModel):
    model_config = ConfigDict(
        ignored_types=(cached_property,),
    )

    @cached_property
    def _format_fields(self):
        fkeys_all = set()
        contain_fstring = {}

        for name, _ in self.model_fields.items():
            # check if type hint is str
            var = getattr(self, name)
            if isinstance(var, list) and all(isinstance(x, _Base) for x in var):
                contain_fstring[name] = []
                for x in var:
                    x : _Base
                    fkeys, cmap = x._format_fields
                    fkeys_all.update(fkeys)
                    contain_fstring[name].append(cmap)

                continue

            if isinstance(var, _Base):
                fkeys, cmap = var._format_fields
                fkeys_all.update(fkeys)
                contain_fstring[name] = cmap

                continue

            if not isinstance(var, str):
                continue

            if len((fkeys:=extract_fstring_keys(var))) ==0:
                continue

            fkeys_all.update(fkeys)
            contain_fstring[name] = len(fkeys) > 0

        return fkeys_all, contain_fstring

class Author(_Base):
    name: str
    url: str
    icon_url: str = None

class Footer(_Base):
    text: str
    icon_url: str = None

class Image(_Base):
    url: str

class Thumbnail(_Base):
    url: str

class Video(_Base):
    url: str
    height: int
    width: int

class Provider(_Base):
    name: str
    url: str

class Colour(_Base):
    r : int
    g : int
    b : int
    value : int

class Field(_Base):
    name: str = None
    value: str = None
    inline: bool = False

class Embed(_Base):
    title: str = None
    description: str = None
    url: str = None
    color: Colour | int = None

    timestamp: datetime.datetime | str | int = None
    footer: Footer = None
    image: Image = None
    thumbnail: Thumbnail = None
    video: Video = None
    provider: Provider = None
    author : Author = None

    fields: typing.List[Field] = _Field(default_factory=list)

    @field_validator("color", mode="before")
    @classmethod
    def _pre_validate_color(cls, v):
        if isinstance(v, Colour):
            return v
        
        if isinstance(v, int):
            r,g,b = hex_to_rgb(v)
            return Colour(**{"r":r,"g":g,"b":b,"value":v})

        raise ValueError("color must be either Colour or int")

    def _embed_dict(self):
        ret = {
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'color': self.color.value if self.color else None,
            'timestamp': self.timestamp,
        }
        return {k: v for k, v in ret.items() if v is not None}



def to_pydantic_embed(embed : DiscordEmbed):
    embed_dict = embed.to_dict()
    if "color" in embed_dict:

        t= embed._colour
        embed_dict['color'] = Colour(**{"r":t.r,"g":t.g,"b":t.b,"value":t.value})
    return Embed(**embed_dict)


def to_discord_embed(input : Embed):
    embed : DiscordEmbed = DiscordEmbed.from_dict(input._embed_dict())
    if input.author:
        embed.set_author(**input.author.model_dump())
    if input.footer:
        embed.set_footer(**input.footer.model_dump())
    if input.image:
        embed.set_image(**input.image.model_dump())
    if input.thumbnail:
        embed.set_thumbnail(**input.thumbnail.model_dump())
    if input.fields:
        for field in input.fields:
            embed.add_field(**field.model_dump())
    return embed

