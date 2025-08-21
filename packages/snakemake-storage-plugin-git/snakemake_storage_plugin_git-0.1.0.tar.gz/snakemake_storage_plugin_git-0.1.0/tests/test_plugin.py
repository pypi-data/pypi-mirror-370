import os
from typing import Optional, Type
from snakemake_interface_storage_plugins.tests import TestStorageBase
from snakemake_interface_storage_plugins.storage_provider import StorageProviderBase
from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase
from snakemake_storage_plugin_git import StorageProvider, StorageProviderSettings


class TestStorage(TestStorageBase):
    __test__ = True
    retrieve_only = True
    store_only = False
    delete = False
    touch = False
    files_only = True

    def get_query(self, tmp_path) -> str:
        # Return a query. If retrieve_only is True, this should be a query that
        # is present in the storage, as it will not be created.
        return "https://github.com/SE-UP/snakemake-storage-plugin-git"

    def get_query_not_existing(self, tmp_path) -> str:
        # Return a query that is not present in the storage.
        return "https://github.com/SE-UP/snakemake-storage-plugin-svn"

    def get_storage_provider_cls(self) -> Type[StorageProviderBase]:
        # Return the StorageProvider class of this plugin
        return StorageProvider

    def get_storage_provider_settings(self) -> Optional[StorageProviderSettingsBase]:
        # instantiate StorageProviderSettings of this plugin as appropriate
        return StorageProviderSettings(
            enable_rate_limits=True,
            max_requests_per_second=0.1,
            fetch_to_update=True,
            ssh_username="git",
            ssh_pubkey_path=os.path.expanduser("~/.ssh/id_rsa.pub"),
            ssh_privkey_path=os.path.expanduser("~/.ssh/id_rsa"),
            ignore_errors=True,
            keep_local=True,
            retrieve=False,
            _is_test=True,
        )
