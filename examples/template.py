from discord_embed_model import Formatter

template = Formatter(
    title = "{user} has joined the server!",
    description = "Welcome to the server, {mention_user}!",
    color = 0x00ff00,
)

class User:
    def __init__(self, name):
        self.name = name

    @property
    def mention(self):
        return f"<@{self.name}>"

template.advance_prep_lambda("user", func=lambda x : x.name)
template.advance_prep_lambda("mention_user", func =lambda _, x : x["user"].mention)

res = template.format(user=User("1"))
assert res.title == "1 has joined the server!"
assert res.description == "Welcome to the server, <@1>!"