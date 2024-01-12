import typing
from typing import Any
from discord.embeds import Embed
import discord.types.embed as et
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

_typeAdapter : TypeAdapter = TypeAdapter(et.Embed)

class EmbedData(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )
    title: str = None
    type: et.EmbedType = "rich"
    description: str = None
    url: str = None
    timestamp: str = None
    color: int = 0
    footer: et.EmbedFooter = None
    image: et.EmbedImage = None
    thumbnail: et.EmbedThumbnail = None
    video: et.EmbedVideo = None
    provider: et.EmbedProvider = None
    author: et.EmbedAuthor = None
    fields: typing.List[et.EmbedField] = None
    
    _on_change_callback : typing.Callable
    
    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "_on_change_callback", None)

    def __setitem__(self, key, value):
        if "::" not in key:
            return setattr(self, key, value)

        splitted = key.split("::")
        target = self
        for k in splitted[:-1]:
            if isinstance(target, list):
                target = target[int(k)]
            elif isinstance(target, dict):
                target = target[k]
            else:
                target = getattr(target, k)

        # check if value changed
        if isinstance(target, list) and len(target) > int(splitted[-1]) and target[int(splitted[-1])] == value:
            return
        elif isinstance(target, dict) and target[splitted[-1]] == value:
            return
        elif getattr(target, splitted[-1], None) == value:
            return

        setattr(target, splitted[-1], value)
        if self._on_change_callback is not None:
            self._on_change_callback(self, key, value)
        
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if self._on_change_callback is not None:
            self._on_change_callback(self, name, value)

    def validateData(self):
        _typeAdapter.validate_python(self.model_dump(exclude_defaults=True))

    def add_field(self, name: str, value: str, inline: bool = True):
        if self.fields is None:
            self.fields = []

        self.fields.append(et.EmbedField(name=name, value=value, inline=inline))
        curr_index = len(self.fields) - 1
        self._on_change_callback(self, f"fields::{curr_index}::name", value)
        self._on_change_callback(self, f"fields::{curr_index}::value", value)

    def toEmbed(self):
        return Embed.from_dict(
            self.model_dump()
        )
    
    
class EmbedExtra(BaseModel):
    embed : EmbedData
    callbacks : typing.List[typing.Callable] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self.embed, "_ref", self._callback)

    @classmethod
    def fromEmbedData(cls, embed: EmbedData):
        return cls(embed=embed)
    
    @classmethod
    def fromEmbed(cls, embed: Embed):
        return cls(embed=embed.to_dict())
    
    def toEmbed(self):
        return Embed.from_dict(
            self.embed.model_dump(exclude_defaults=True, include={"type"})
        )
    
    def _callback(self, *args):
        for callback in self.callbacks:
            callback(self, *args)

