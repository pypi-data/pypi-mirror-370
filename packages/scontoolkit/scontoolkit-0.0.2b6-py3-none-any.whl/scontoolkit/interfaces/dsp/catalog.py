from abc import ABC, abstractmethod
from typing import List
from ...models.dsp.v2025_1_rc2.catalog import Dataset


class ICatalogService(ABC):

    @abstractmethod
    def create_dataset(self, dataset: Dataset) -> str:
        pass

    @abstractmethod
    def get_dataset(self, id: str) -> Dataset:
        pass

    @abstractmethod
    def list_datasets(self) -> List[Dataset]:
        pass

    # @abstractmethod
    # def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> bool:
    #     pass

    @abstractmethod
    def delete_dataset(self, dataset_id: str) -> bool:
        pass
