
from unittest import TestCase
from discord_embed_model.model import to_discord_embed

from discord_embed_model.stateful import StatefulEmbed, StatefulFormatter, StatefulStorageManager


class Test_Stateful(TestCase):
    def test_1(self):
        x = StatefulFormatter(
            title="help {this}"
        )
        res = x.format(this="1")
        
        self.assertEqual(res.title, "help 1")
        self.assertGreaterEqual(len(StatefulStorageManager._storages["memory"]), 1)    

    def test_2(self):
        x = StatefulEmbed(
            title="this is a embed",
            description="this is a description",
            fields=[
                {
                    "name": "this is a field",
                    "value": "this is a field value",
                    "inline": False
                }
            ]
        )

        someobject = object()

        x.cache(someobject)

        self.assertEqual(StatefulEmbed.retrieve(x.uid), someobject)

    def test_3(self):
        x = StatefulEmbed(
            title="this is a embed",
            description="this is a description",
            fields=[
                {
                    "name": "this is a field",
                    "value": "this is a field value",
                    "inline": False
                }
            ]
        )

        x.cache()

        de = to_discord_embed(x)
        
        res = StatefulEmbed.retrieve(de, target_storage="memory", method="footer")

        assert res is not None
        assert res == x

        
