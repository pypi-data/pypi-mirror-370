from scontoolkit.interfaces.dsp.catalog import ICatalogService
from scontoolkit.models.dsp.v2025_1_rc2.catalog import Dataset, RootCatalog
from scontoolkit.services.meta_db_service import MongoStorage, mongo_storage

from ckanapi import RemoteCKAN
import os

# A Dataset MUST have at least one hasPolicy attribute that contain an Offer defining the Policy associated with the Dataset.
# A Dataset MUST hold at least one Distribution object in the distribution attribute.
# Each DataService object MUST HAVE at least one DataService which specifies where the distribution is obtained. Specifically, a DataService specifies the endpoint for initiating a Contract Negotiation and Transfer Process.
# A DataService.endpointURL property contains the URL of the service the Contract Negotiation endpoints extend. The endpoint's DSP version MUST be consistent with the version the Catalog object was served through.
# An Offer contains the following attributes:
#
# An Offer MUST have an @id that is a unique identifier.
# An Offer MUST be unique to a Dataset since the target of the Offer is derived from its enclosing context.
# Offers MUST NOT contain any target attributes. The value of the target attribute MUST be the Dataset ID. (Note: If the Offer is used in an enclosing Catalog or Dataset, there must not be any target attribute set.)
# 5.3.3 ERROR - Catalog Error



class CKANCatalogService(ICatalogService):
    def __init__(self):
        self._datasets = {}
        self.__ckan_url__ = os.getenv("sconext.ckan.url")
        self.__admin_key__ = os.getenv("sconext.ckan.admin_key")

        self.ckan = RemoteCKAN(self.__ckan_url__ , apikey=self.__admin_key__)

    def __retrieve_assets__(self):
        orgs = self.ckan.action.organization_list()
        datasets = []
        for org in orgs:
            current = self.ckan.action.organization_show(id=org, include_datasets=True)
            datasets.extend(current['packages'])
        return datasets

    async def get_catalog(self, db: MongoStorage):
        # resp: RootCatalog
        dsets = await self.list_datasets(db)

        resp = RootCatalog(
            id='tha_doume',
            context=["https://w3id.org/dspace/2025/1/context.jsonld"],
            type="Catalog",
            participantId="tha-doume",
            dataset=dsets
        )
        return resp

    def create_dataset(self, dataset: Dataset) -> str:
        self._datasets[dataset.id] = dataset
        return dataset.id

    async def get_dataset(self, dataset_id: str, db: MongoStorage) -> Dataset:

        dataset = self.ckan.action.package_show(id=dataset_id)
        exposed = await db.get_offers_for_datasets([dataset_id])
        offers = [await db.get_offer(offer_id) for offer_id in exposed[dataset_id]]
        resp = Dataset(
            id=dataset_id if 'urn' in dataset_id else f"urn:uuid:{dataset_id.split(':')[-1]}",
            type="Dataset",
            distribution=[],
            hasPolicy=[],
        )
        resp.hasPolicy.extend(offers)
        return resp

    async def list_datasets(self, db: MongoStorage) -> list[Dataset]:
        ckan_dsets = self.__retrieve_assets__()
        exposed = await db.get_offers_for_datasets([item['id'] for item in ckan_dsets])
        dsets = []
        for dataset_id, offer_ids in exposed.items():
            offers = [await db.get_offer(item) for item in offer_ids]
            current = Dataset(
                id=dataset_id if 'urn' in dataset_id else f"urn:uuid:{dataset_id.split(':')[-1]}",
                type="Dataset",
                distribution=[],
                hasPolicy=[],
            )
            current.hasPolicy.extend(offers)
            dsets.append(current)
        return dsets

    def delete_dataset(self, dataset_id: str) -> bool:
        return self._datasets.pop(dataset_id, None) is not None
