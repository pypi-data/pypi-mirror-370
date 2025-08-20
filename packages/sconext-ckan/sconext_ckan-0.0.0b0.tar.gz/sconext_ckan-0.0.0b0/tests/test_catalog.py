import os

os.environ["sconext.ckan.url"] = "https://datamanager-inherit.euinno.eu"
os.environ["sconext.ckan.admin_key"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJxdWRJYkFYWVRxc3BDMHVpMVpYSGszMmJQZUxicVlwY1NOMFNUOUR0QWZKWWZRaFphODRLM21ZWkRsYnhxcGZUUjBRbVlrT0VycGlvd3hTNCIsImlhdCI6MTc1MzE3MTg5N30.w50spOtyvj2FfpPjWNkgU_sFmryOWw-quYDLhKgwiGw"

os.environ["sconnector.meta.db_url"] = "localhost:27017"
os.environ["sconnector.meta.db_name"] = "SingularSpace"
os.environ["sconnector.meta.db_user"] = "singular-connector"
os.environ["sconnector.meta.db_pwd"] = "mySecretCombination"


import unittest, json
from src.sconext_ckan_catalog.ckan_catalog import CKANCatalogService
import asyncio



class TestCatalog(unittest.TestCase):
    catalog = CKANCatalogService()

    def test_retrieve_assets(self):
        assets = self.catalog.__retrieve_assets__()
        print(assets)

    def test_list_datasets(self):
        from scontoolkit.services.meta_db_service import mongo_storage
        ctlg = asyncio.run(self.catalog.list_datasets(mongo_storage))
        print(ctlg)

    def test_get_catalog(self):
        from scontoolkit.services.meta_db_service import mongo_storage
        ctlg = asyncio.run(self.catalog.get_catalog(mongo_storage))
        print(ctlg)
