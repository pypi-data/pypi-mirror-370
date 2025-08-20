# from abc import ABC, abstractmethod
# from typing import List
# from ...models.dsp.v2025_1_rc2.catalog import Dataset
# import os
# from fastapi import APIRouter
#
#
# @ids_router.post("/request")#, response_model=Union[Catalog, CatalogError])
# def catalog(request: CatalogRequestMessage):# -> Union[Catalog, CatalogError]:
#     print(request)
#     for catalogService in ExtensionRegistry.get_by_interface(ICatalogService):
#         print(catalogService.list_datasets())
#
#     # if request.filter
#     # return get_catalog()
#
# class IRouter(ABC):
#
#     def get_router(cls):
#         prefix = os.getenv('ROUTER_PREFIX', '/custom')
#         return
#
#
#     @abstractmethod
#     def create_dataset(self, dataset: Dataset) -> str:
#         pass
