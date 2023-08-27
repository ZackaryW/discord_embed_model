
from unittest import TestCase

from discord import Embed as DiscordEmbed

from discord_embed_model.model import to_pydantic_embed, Embed, to_discord_embed

class Test_Embed_init(TestCase):
    def test_1(self):
        x = DiscordEmbed(
            title='title',
            description='description',
            url='url',
            color=0x123456,
        )
        x.set_author(name='author_name', url='author_url', icon_url='author_icon_url')
        x.set_footer(text='footer_text', icon_url='footer_icon_url')
        x.set_image(url='image_url')
        x.set_thumbnail(url='thumbnail_url')
        x.add_field(name='field_name', value='field_value', inline=False)
        y = to_pydantic_embed(x)
        self.assertIsInstance(y, Embed)
        self.assertEqual(y.title, x.title)
        self.assertEqual(y.description, x.description)
        self.assertEqual(y.url, x.url)
        self.assertEqual(y.color.value, x.color.value)
        self.assertEqual(y.author.name, x.author.name)
        self.assertEqual(y.author.url, x.author.url)
        self.assertEqual(y.author.icon_url, x.author.icon_url)
        self.assertEqual(y.footer.text, x.footer.text)
        self.assertEqual(y.footer.icon_url, x.footer.icon_url)
        self.assertEqual(y.thumbnail.url, x.thumbnail.url)
        self.assertEqual(y.image.url, x.image.url)
        self.assertEqual(y.fields[0].name, x.fields[0].name)
        self.assertEqual(y.fields[0].value, x.fields[0].value)

        # convert back
        z = to_discord_embed(y)
        self.assertIsInstance(z, DiscordEmbed)
        self.assertEqual(z.title, x.title)
        self.assertEqual(z.description, x.description)
        self.assertEqual(z.url, x.url)
        self.assertEqual(z.color.value, x.color.value)
        self.assertEqual(z.author.name, x.author.name)
        self.assertEqual(z.author.url, x.author.url)
        self.assertEqual(z.author.icon_url, x.author.icon_url)
        self.assertEqual(z.footer.text, x.footer.text)
        self.assertEqual(z.footer.icon_url, x.footer.icon_url)
        self.assertEqual(z.thumbnail.url, x.thumbnail.url)
        self.assertEqual(z.image.url, x.image.url)
        self.assertEqual(z.fields[0].name, x.fields[0].name)
        self.assertEqual(z.fields[0].value, x.fields[0].value)
        