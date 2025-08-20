from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict
from ..interfaces.dsp.metadb import IMetaDatabase
from ..models.dsp.v2025_1_rc2.low_level import Offer, Optional, Dataset
import os
import uuid
from collections import defaultdict


def generate_uuid_urn(prefix: str = "urn:uuid:") -> str:
    return f"{prefix}{uuid.uuid4()}"

class MongoStorage(IMetaDatabase):
    def __init__(self):
        url = os.getenv('sconnector.meta.db_url')
        print(url)
        db_name = os.getenv('sconnector.meta.db_name')
        user = os.getenv('sconnector.meta.db_user')
        pwd = os.getenv('sconnector.meta.db_pwd')
        motor_url = f"mongodb://{user}:{pwd}@{url}/{db_name}?authSource={db_name}"
        self.client = AsyncIOMotorClient(motor_url)
        self.db = self.client[db_name]
        self.offers = self.db["offers"]
        self.exposed = self.db["exposed"]

    async def create_offer(self, offer: Offer) -> Offer:
        offer_dict = offer.model_dump(by_alias=True)
        if offer.id == "" or not offer.id:
            offer_dict["@id"] = generate_uuid_urn()
        offer_dict["_id"] = offer_dict["@id"].split(':')[-1]

        await self.offers.insert_one(offer_dict)
        return offer

    async def get_offer(self, offer_id: str) -> Optional[Offer]:
        doc = await self.offers.find_one({"_id": offer_id})
        return Offer(**doc) if doc else None

    # async def list_offers(self) -> List[Offer]:
    #     cursor = self.offers.find()
    #     docs = await cursor.to_list(length=1000)
    #     return [Offer(**doc) for doc in docs]
    #
    # async def update_offer(self, offer: Offer) -> bool:
    #     offer_dict = offer.model_dump(by_alias=True)
    #     offer_dict["_id"] = offer_dict["@id"]
    #     result = await self.offers.replace_one({"_id": offer_dict["_id"]}, offer_dict)
    #     return result.modified_count == 1

    # async def delete_offer(self, offer_id: str) -> bool:
    #     result = await self.offers.delete_one({"_id": offer_id})
    #     return result.deleted_count == 1

    async def expose_dataset(self, dataset_id: str, offer_id: str) -> dict:
        body = {
            "_id": generate_uuid_urn(prefix=""),
            "offer_id": offer_id,
            "dataset_id": dataset_id
        }
        _ = await self.exposed.insert_one(body)
        return body

    async def get_offers_for_datasets(self, dataset_ids: List[str]) -> Dict[str, List[str]]:
        cursor = self.exposed.find({"dataset_id": {"$in": dataset_ids}})
        results = await cursor.to_list(length=None)

        mapping = defaultdict(list)
        for item in results:
            dataset_id = item.get("dataset_id")
            offer_id = item.get("offer_id")
            if dataset_id and offer_id:
                mapping[dataset_id].append(offer_id)
        return dict(mapping)

# Singleton instance
mongo_storage: MongoStorage = MongoStorage()