from abc import ABC, abstractmethod
from typing import List, Dict
from ...models.dsp.v2025_1_rc2.low_level import Offer

class IMetaDatabase(ABC):

    @abstractmethod
    async def create_offer(self, offer: Offer) -> str:
        pass

    @abstractmethod
    async def get_offer(self, id: str) -> Offer:
        pass

    # @abstractmethod
    # async def list_offers(self) -> List[Offer]:
    #     pass
    #
    # @abstractmethod
    # async def update_offer(self, offer: Offer) -> bool:
    #     pass
    #
    # @abstractmethod
    # async def delete_offer(self, offer_id: str) -> bool:
    #     pass