# discord_embed_model

this is an extension of the discord.py library that provides many useful features for creating and modifying embeds

## Installation

```bash
pip install discord-embed-model
```

## Usage

1. transforming discord embed into a pydantic instance

```py
from discord import Embed as DiscordEmbed
from discord_embed_model import Embed, to_pydantic_embed

discordEmbed : DiscordEmbed
embed : Embed = to_pydantic_embed(discordEmbed)
```

2. formatting embeds using templates

```py
from discord_embed_model import Formatter

template = Formatter(
    title="hello {user.mention}
)

user : discord.User
embed = template.format(user=user) # embed.title == "hello @user"
```

3. embed that is retrievable

```py
from discord import Interaction
from discord_embed_model import StatefulEmbed

embed = StatefulEmbed(
    title="i can get this back",
)

embed.cache()

# sent out to discord

interaction : Interaction

# get embed
rembed = interaction.message.embeds[0]

retrieved = StatefulEmbed.retrieve(rembed, target_storage=rembed.TARGET_STORAGE, method=rembed.TARGET_CONTEXT)
assert retrieved is embed

```
