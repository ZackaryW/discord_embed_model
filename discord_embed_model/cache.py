
import typing
import uuid
from discord import Embed
from uuid import uuid4

from pydantic import UUID4
from discord_embed_model.extra import EmbedData, EmbedExtra
from discord_embed_model.utils import dict_has_value


class MemoryCache:
    def __init__(self):
        self._cache = {}
        
        self.__last_item = None
        self.__last_uid = None

    def uid_method(self, embed : Embed | EmbedData | EmbedExtra) -> typing.Tuple[Embed, str]:
        if isinstance(embed, EmbedExtra):
            data = embed.embed
        elif isinstance(embed, EmbedData):
            data = embed
        else:
            data = embed.to_dict()
            data = EmbedData(**data)
        
        # validate is uuid
        if dict_has_value("footer::text", data):
            val = data["footer"]["text"]
            uidval =  UUID4(val)
            if str(uidval) == val:
                return embed, val
            
        uid= str(uuid4())
        data.footer = {"text" : uid}
        return data.toEmbed(), uid
    

    def __getitem__(self, embed : Embed):
        data =embed.to_dict()
        if not dict_has_value("footer::text", data):
            raise KeyError
        
        return self._cache[data["footer"]["text"]], data
    
    
    def __setitem__(self, embed : Embed | EmbedData | EmbedExtra, value):
        data, uid = self.uid_method(embed)
        self._cache[uid] = value

        self.__last_item = data
        self.__last_uid = uid

    @property
    def saved(self):
        return self.__last_item, self.__last_uid
    
    @property
    def savedItem(self):
        return self.__last_item
    
    @property
    def savedUID(self):
        return self.__last_uid