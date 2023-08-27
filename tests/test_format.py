
from unittest import TestCase

from discord import Embed as DiscordEmbed

from discord_embed_model.formatter import Formatter

class T_Format(TestCase):
    def test_1(self):
        x = Formatter(
            title="title {this}",
            description="description {this}",
            url="url {that}",
            color=0x123456,
            thumbnail={
                "url": "thumbnail_url {this}"
            },
            footer={
                "text": "footer_text {this}",
                "icon_url": "footer_icon_url {that}"
            },
            fields=[
                {
                    "name": "field_name {this}",
                    "value": "field_value {that}",
                    "inline": False
                }
            ]
        )

        res: DiscordEmbed =x.format(this="1", that="2")
        self.assertIsInstance(res, DiscordEmbed)
        self.assertEqual(res.title, "title 1")
        self.assertEqual(res.description, "description 1")
        self.assertEqual(res.url, "url 2")
        self.assertEqual(res.color.value, 0x123456)
        self.assertEqual(res.thumbnail.url, "thumbnail_url 1")
        self.assertEqual(res.footer.text, "footer_text 1")
        self.assertEqual(res.footer.icon_url, "footer_icon_url 2")

        self.assertEqual(res.fields[0].name, "field_name 1")
        self.assertEqual(res.fields[0].value, "field_value 2")

        

    def test_2(self):
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

        res: DiscordEmbed = template.format(user=User("1"))
        assert res.title == "1 has joined the server!"
        assert res.description == "Welcome to the server, <@1>!"

    def test_3(self):
        template = Formatter(
            title = "{user.name} has joined the server!",
            description = "Welcome to the server, {user.mention}!",
            color = 0x00ff00,
        )

        class User:
            def __init__(self, name):
                self.name = name

            @property
            def mention(self):
                return f"<@{self.name}>"

        res: DiscordEmbed = template.format(user=User("1"))
        assert res.title == "1 has joined the server!"
        assert res.description == "Welcome to the server, <@1>!"
    
    def test_4(self):
        template = Formatter(title="{template} word")
        template.advance_prep_lambda("template", func=lambda _, x : x["other_var"])

        res: DiscordEmbed = template.format(other_var="2")

        assert res.title == "2 word"

class T_parse(TestCase):
    def test_1(self):
        x = Formatter(
            title="title {this}",
            description="description {this}",
            url="url {that}",
            color=0x123456,
            thumbnail={
                "url": "thumbnail_url {this}"
            },
            footer={
                "text": "footer_text {this}",
                "icon_url": "footer_icon_url {that}"
            },
            fields=[
                {
                    "name": "field_name {this}",
                    "value": "field_value {that}",
                    "inline": False
                }
            ]
        )

        res: DiscordEmbed =x.format(this="1", that="2")

        extracted, _ = x.parseEmbed(res)

        self.assertTrue("this" in extracted)
        self.assertTrue("that" in extracted)

        self.assertEqual(extracted["this"], '1')
        self.assertEqual(extracted["that"], '2')
