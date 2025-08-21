import os
os.environ["sconnector.meta.db_url"] = "localhost:27017"
os.environ["sconnector.meta.db_name"] = "SingularSpace"
os.environ["sconnector.meta.db_user"] = "singular-connector"
os.environ["sconnector.meta.db_pwd"] = "mySecretCombination"

import unittest, json
from src.scontoolkit.services.meta_db_service import mongo_storage
import asyncio


class TestCatalog(unittest.TestCase):

    def test_get_offers(self):
        offers = asyncio.run(mongo_storage.list_offers())
        print(offers)

