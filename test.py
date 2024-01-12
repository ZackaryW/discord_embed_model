from time import sleep
from discord_embed_model.cache import MemoryCache
from discord_embed_model.model import EmbedModel

m = EmbedModel()
m.template.title = "This is a template title {a1}"
m.template.add_field(name="This is a field", value="This is a value {a2}")

embed = m.format(a1=1, a2=2)

cache = MemoryCache()
cache[embed] = "somenote i want to memorize"
embed = cache.savedItem

sleep(1)

trd = cache[embed]

assert trd[0] == "somenote i want to memorize"
pass