import typing
from typing import Any
import uuid

from pydantic import Field
from discord_embed_model.formatter import Formatter
from discord_embed_model.model import Embed, DiscordEmbed, Footer
from pydantic._internal._model_construction import ModelMetaclass

def _footer_create(uid : str, embed : Embed|DiscordEmbed) :
    if isinstance(embed, Embed):
        embed.footer = Footer(text=str(uid))
    else:
        embed.set_footer(text=str(uid), icon_url=None)

    return embed

def _footer_retrieve(embed : Embed|DiscordEmbed):
    if not embed.footer:
        return None
    return embed.footer.text

def _field_top_create(uid : str, embed : Embed|DiscordEmbed):
    if isinstance(embed, Embed):
        embed.fields.insert(0, {"value": str(uid), "name": "id", "inline": False})
    else:
        embed.insert_field_at(0, name="id", value=str(uid), inline=False)

    return embed

def _field_top_retrieve(embed : Embed|DiscordEmbed):
    if not embed.fields:
        return None
    return embed.fields[0].value

def _field_bottom_create(uid : str, embed : Embed|DiscordEmbed):
    if isinstance(embed, Embed):

        embed.fields.append({"value": str(uid), "name": "id", "inline": False})
    else:
        embed.add_field(name="id", value=str(uid), inline=False)

    return embed

def _field_bottom_retrieve(embed : Embed|DiscordEmbed):
    if not embed.fields:
        return None
    return embed.fields[-1].value


class StatefulStorageManager(ModelMetaclass):
    _create_contexts = {}
    _retrieve_contexts = {}

    _storages = {}

    def register_storage(self, storage_str : str, storage : typing.Union[typing.Any, dict]):
        if storage_str in self._storages:
            raise ValueError(f"Storage {storage_str} already exists.")
        self._storages[storage_str] = storage

    def register_context(self, context_loc : str, create : typing.Callable, retrieve : typing.Callable):
        if context_loc in self._create_contexts:
            raise ValueError(f"Context {context_loc} already exists.")
        
        self._create_contexts[context_loc] = create
        self._retrieve_contexts[context_loc] = retrieve

    def retrieve(self, uid: str, storage_str : str = "memory"):
        return self._storages[storage_str][uid]
    
    def retrieve_method(self, storage_str : str = "memory"):
        def _retrieve(uid : str):
            return self.retrieve(uid, storage_str)
        return _retrieve

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if "footer" not in self._create_contexts:
            self.register_context("footer", _footer_create, _footer_retrieve)
            self.register_context("fields_top", _field_top_create, _field_top_retrieve)
            self.register_context("fields_bottom", _field_bottom_create, _field_bottom_retrieve)
            self.register_storage("memory", {})
        
        return super().__call__(*args, **kwds)

class Stateful(Embed, metaclass=StatefulStorageManager):
    TARGET_CONTEXT : typing.ClassVar[typing.Union[
        typing.Literal["footer", "fields_top", "fields_bottom"], str
    ]] = "footer"
    TARGET_STORAGE : typing.ClassVar[str] = "memory"
    
    def _create_identifier(self, uid : str = None, embed : Embed|DiscordEmbed=None, target_obj : typing.Any=None):
        if uid is None:
            uid = str(uuid.uuid1())
        if embed is None:
            embed = self
        embed = self.__class__._create_contexts[self.TARGET_CONTEXT](uid, embed)
        if target_obj is None:
            target_obj = self
        self.__class__._storages[self.TARGET_STORAGE][uid] = target_obj
        return embed

class StatefulFormatter(Stateful, Formatter):
    def format(self, **kwargs):
        embed = super().format(**kwargs)
        return self._create_identifier(embed=embed, target_obj=kwargs)
    
    def formatViaObj(self, obj):
        if obj.hasattr("to_dict"):
            aobj = obj.to_dict()
        elif obj.hasattr("unpack"):
            aobj = obj.unpack()
        elif isinstance(obj, dict):
            aobj = obj
        elif obj.hasattr("dict"):
            aobj = obj.dict()
        else:
            aobj = obj.__dict__

        embed = super().format(**aobj)
        return self._create_identifier(embed=embed, target_obj=obj)

class StatefulEmbed(Stateful):
    uid : str = Field(default_factory=lambda: str(uuid.uuid1()))

    def cache(self, target_obj : typing.Any=None):
        return self._create_identifier(uid=self.uid, target_obj=target_obj)
    
    @classmethod
    def retrieve(cls, obj : typing.Union[str, DiscordEmbed], target_storage : str = None, method : str = None):
        if target_storage is None:
            target_storage = cls.TARGET_STORAGE

        if isinstance(obj, str):
            uid = obj
            return cls._storages[target_storage][uid]
        
        if method is not None and method not in cls._retrieve_contexts:
            raise ValueError(f"method {method} is not a valid method.")
            
        if method:
            jobs = [cls._retrieve_contexts[method]]
        else:
            jobs = list(cls._retrieve_contexts.values())

        for job in jobs:
            try:
                res = job(obj)
            except: # noqa
                continue

            # string is valid uuid1
            if res is None:
                continue
            if not (isinstance(res, str) or len(res) == 36):
                continue

            return cls._storages[target_storage][res]
                
                
        raise ValueError("obj is not a valid stateful embed.")
            
