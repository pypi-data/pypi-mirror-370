from dataclasses import dataclass, field
from typing import Any, Optional, List

import os
from urllib.parse import urlparse
import pygit2

from snakemake_interface_storage_plugins.settings import StorageProviderSettingsBase
from snakemake_interface_storage_plugins.storage_provider import (  # noqa
    StorageProviderBase,
    StorageQueryValidationResult,
    ExampleQuery,
    QueryType,
    Operation,
)
from snakemake_interface_storage_plugins.storage_object import (
    StorageObjectRead,
    StorageObjectWrite,
    retry_decorator,
)
from snakemake_interface_storage_plugins.io import IOCacheStorageInterface, Mtime

# Raise errors that will not be handled within this plugin but thrown upwards to
# Snakemake and the user as WorkflowError.
from snakemake_interface_common.exceptions import WorkflowError  # noqa


class RemoteSSHCallbacks(pygit2.RemoteCallbacks):
    def __init__(
        self, username="git", public_key=None, private_key=None, passphrase=""
    ):
        super().__init__()
        self.username = username
        self.public_key = public_key
        self.private_key = private_key
        self.passphrase = passphrase

    def credentials(self, url, username_from_url, allowed_types):
        if allowed_types & pygit2.enums.CredentialType.USERNAME:
            return pygit2.Username(self.username)
        if allowed_types & pygit2.enums.CredentialType.SSH_KEY:
            return pygit2.Keypair(
                self.username, self.public_key, self.private_key, self.passphrase
            )
        raise ValueError(
            "Unsupported credential type or the remote repository is not accessible."
        )


def error_handler(logger: Any, msg: str, ignore: bool, e: Exception):
    """Handle errors whether to ignore or raise an exception."""
    if ignore:
        logger.warning(f"{msg}: {e}.")
    else:
        raise WorkflowError(f"{msg}: {e}") from e


# Optional:
# Define settings for your storage plugin (e.g. host url, credentials).
# They will occur in the Snakemake CLI as --storage-<storage-plugin-name>-<param-name>
# Make sure that all defined fields are 'Optional' and specify a default value
# of None or anything else that makes sense in your case.
# Note that we allow storage plugin settings to be tagged by the user. That means,
# that each of them can be specified multiple times (an implicit nargs=+), and
# the user can add a tag in front of each value (e.g. tagname1:value1 tagname2:value2).
# This way, a storage plugin can be used multiple times within a workflow with different
# settings.
@dataclass
class StorageProviderSettings(StorageProviderSettingsBase):
    enable_rate_limits: Optional[bool] = field(
        default=True,
        metadata={
            "help": "Use rate limiting for platforms that require it (e.g. GitHub).",
            "env_var": False,
            "required": False,
        },
    )
    max_requests_per_second: Optional[float] = field(
        default=1,
        metadata={
            "help": "Maximum number of requests per second for this storage provider. "
            "0.01 is recommended for GitHub if many repositories are "
            "cloned to avoid exceeding the rate limit.",
            "env_var": False,
            "required": False,
        },
    )
    local_path_delimiter: Optional[str] = field(
        default="+",
        metadata={
            "help": "Delimiter to replace '/' with in the local path of "
            "the cloned repositories.",
            "env_var": False,
            "required": False,
        },
    )
    fetch_to_update: Optional[bool] = field(
        default=True,
        metadata={
            "help": "Fetch changes from the remote if the repository already "
            "exists in local.",
            "env_var": False,
            "required": False,
        },
    )
    ssh_username: Optional[str] = field(
        default="git",
        metadata={
            "help": "Username for SSH authentication.",
            "env_var": False,
            "required": False,
        },
    )
    ssh_pubkey_path: Optional[str] = field(
        default="/dev/null",
        metadata={
            "help": "Path to the SSH public key for authentication.",
            "env_var": False,
            "required": False,
        },
    )
    ssh_privkey_path: Optional[str] = field(
        default="/dev/null",
        metadata={
            "help": "Path to the SSH private key for authentication.",
            "env_var": False,
            "required": False,
        },
    )
    ssh_passphrase: Optional[str] = field(
        default="",
        metadata={
            "help": "Passphrase for the SSH private key.",
            "env_var": False,
            "required": False,
        },
    )
    custom_heads: Optional[dict] = field(
        default=None,
        metadata={
            "help": "Do checkout to a custom branche(or tag) and commit after cloning."
            '{"<GIT_URL>": {"tag": "<TAG>", "branch": '
            '"<BRANCH>", "commit": "<COMMIT_ID>"}}',
            "env_var": False,
            "required": False,
        },
    )
    keep_local: Optional[bool] = field(
        default=True,
        metadata={
            "help": "Keep the cloned repositories after the workflow is finished.",
            "env_var": False,
            "required": False,
        },
    )
    ignore_errors: Optional[bool] = field(
        default=False,
        metadata={
            "help": "Ignore errors when cloning or pulling repositories. "
            "This is useful to keep continuing cloning or pulling "
            "repositories even if some of them fail.",
            "env_var": False,
            "required": False,
        },
    )
    retrieve: Optional[bool] = field(
        default=False,
        metadata={
            "help": "This value should always be Flase, as this storage provider "
            "does not support retrieving objects. ",
            "env_var": False,
            "required": False,
        },
    )
    _is_test: Optional[bool] = field(
        default=False,
        metadata={
            "help": "This is only used for unit tests.",
            "env_var": False,
            "required": False,
        },
    )


# Required:
# Implementation of your storage provider
# This class can be empty as the one below.
# You can however use it to store global information or maintain e.g. a connection
# pool.
# Inside of the provider, you can use self.logger (a normal Python logger of type
# logging.Logger) to log any additional informations or
# warnings.
class StorageProvider(StorageProviderBase):
    # For compatibility with future changes, you should not overwrite the __init__
    # method. Instead, use __post_init__ to set additional attributes and initialize
    # futher stuff.

    def __post_init__(self):
        # This is optional and can be removed if not needed.
        # Alternatively, you can e.g. prepare a connection to your storage backend here.
        # and set additional attributes.
        self.done_queries = set()
        self.limit_mode = True

    @classmethod
    def example_queries(cls) -> List[ExampleQuery]:
        """Return an example queries with description for this storage provider (at
        least one)."""
        return [
            ExampleQuery(
                query="https://example.com/repo.git",
                type=QueryType.INPUT,
                description="The remote git repository is accessed via HTTPS.",
            ),
            ExampleQuery(
                query="ssh://example.com/repo.git",
                type=QueryType.INPUT,
                description="The remote git repository is accessed via SSH.",
            ),
        ]

    def rate_limiter_key(self, query: str, operation: Operation) -> Any:
        """Return a key for identifying a rate limiter given a query and an operation.

        This is used to identify a rate limiter for the query.
        E.g. for a storage provider like http that would be the host name.
        For s3 it might be just the endpoint URL.
        """
        return urlparse(query).netloc

    def default_max_requests_per_second(self) -> float:
        """Return the default maximum number of requests per second for this storage
        provider."""
        return self.settings.max_requests_per_second

    def use_rate_limiter(self) -> bool:
        """Return False if no rate limiting is needed for this provider."""
        if not self.settings.enable_rate_limits:
            return False
        return self.limit_mode

    @classmethod
    def is_valid_query(cls, query: str) -> StorageQueryValidationResult:
        """Return whether the given query is valid for this storage provider."""
        # Ensure that also queries containing wildcards (e.g. {sample}) are accepted
        # and considered valid. The wildcards will be resolved before the storage
        # object is actually used.
        url_parsed = urlparse(query)

        if url_parsed.scheme not in ["ssh", "https"]:
            return StorageQueryValidationResult(
                query=query,
                valid=False,
                reason="Only 'ssh', 'https', and 'file' schemes are supported."
                f"(got '{url_parsed.scheme})'",
            )

        return StorageQueryValidationResult(valid=True, query=query)

    # If required, overwrite the method postprocess_query from StorageProviderBase
    # in order to e.g. normalize the query or add information from the settings to it.
    # Otherwise, remove this method as it will be inherited from the base class.
    def postprocess_query(self, query: str) -> str:
        return query

    # This can be used to change how the rendered query is displayed in the logs to
    # prevent accidentally printing sensitive information e.g. tokens in a URL.
    def safe_print(self, query: str) -> str:
        """Process the query to remove potentially sensitive information when printing."""
        return query


# Required:
# Implementation of storage object. If certain methods cannot be supported by your
# storage (e.g. because it is read-only see
# snakemake-storage-http for comparison), remove the corresponding base classes
# from the list of inherited items.
# Inside of the object, you can use self.provider to access the provider (e.g. for )
# self.provider.logger, see above, or self.provider.settings).
class StorageObject(StorageObjectRead, StorageObjectWrite):
    async def inventory(self, cache: IOCacheStorageInterface):
        """From this file, try to find as much existence and modification date
        information as possible. Only retrieve that information that comes for free
        given the current object.
        """
        # This is optional and can be left as is

        # If this is implemented in a storage object, results have to be stored in
        # the given IOCache object, using self.cache_key() as key.
        # Optionally, this can take a custom local suffix, needed e.g. when you want
        # to cache more items than the current query: self.cache_key(local_suffix=...)
        self._clone_or_pull()

        if os.path.exists(self.local_path()):
            cache_key = self.cache_key(str(self.local_path()))
            cache.exists_in_storage[cache_key] = True
            stat_info = os.stat(self.local_path())
            cache.mtime[cache_key] = Mtime(storage=stat_info.st_mtime)
            cache.size[cache_key] = stat_info.st_size

    def get_inventory_parent(self) -> Optional[str]:
        """Return the parent directory of this object."""
        # this is optional and can be left as is
        return None

    def local_suffix(self) -> str:
        """Return a unique suffix for the local path, determined from self.query."""
        return self._get_directory_to_clone()

    def cleanup(self):
        """Perform local cleanup of any remainders of the storage object."""
        # self.local_path() should not be removed, as this is taken care of by
        # Snakemake.

    # Fallible methods should implement some retry logic.
    # The easiest way to do this (but not the only one) is to use the retry_decorator
    # provided by snakemake-interface-storage-plugins.
    @retry_decorator
    def exists(self) -> bool:
        # return True if the object exists
        if (
            hasattr(self.provider.settings, "_is_test")
            and self.provider.settings._is_test
        ):
            self._clone_or_pull()
        return os.path.exists(self.local_path())

    @retry_decorator
    def mtime(self) -> float:
        # return the modification time
        # When this method is called, all repositories should already have been cloned
        # and pulled. So, rate limiter is not needed anymore.
        self.provider.limit_mode = False
        return 0

    @retry_decorator
    def size(self) -> int:
        # return the size in bytes
        # same as mtime()
        self.provider.limit_mode = False
        return 0

    @retry_decorator
    def local_footprint(self) -> int:
        # Local footprint is the size of the object on the local disk.
        # For directories, this should return the recursive sum of the
        # directory file sizes.
        # If the storage provider supports ondemand eligibility (see retrieve_object()
        # below), this should return 0 if the object is not downloaded but e.g.
        # mounted upon retrieval.
        # If this method is not overwritten here, it defaults to self.size().
        ...

    @retry_decorator
    def retrieve_object(self):
        # Ensure that the object is accessible locally under self.local_path()
        # Optionally, this can make use of the attribute self.is_ondemand_eligible,
        # which indicates that the object could be retrieved on demand,
        # e.g. by only symlinking or mounting it from whatever network storage this
        # plugin provides. For example, objects with self.is_ondemand_eligible == True
        # could mount the object via fuse instead of downloading it.
        # The job can then transparently access only the parts that matter to it
        # without having to wait for the full download.
        # On demand eligibility is calculated via Snakemake's access pattern annotation.
        # If no access pattern is annotated by the workflow developers,
        # self.is_ondemand_eligible is by default set to False.
        ...

    # The following to methods are only required if the class inherits from
    # StorageObjectReadWrite.

    @retry_decorator
    def store_object(self):
        # Ensure that the object is stored at the location specified by
        # self.local_path().
        ...

    def remove(self):
        # Remove the object from the storage. This method is still needed as
        # Snakemake calls this when keep_local is set to False.
        ...

    def _get_directory_to_clone(self) -> str:
        """Return the directory where the repository is cloned."""
        parsed_query = urlparse(self.query)
        url_path = parsed_query.path.lstrip("/").removesuffix(".git")
        url_path = url_path.replace("/", self.provider.settings.local_path_delimiter)
        if not url_path:
            raise WorkflowError(f"The URL path is missing: {self.query}.")

        return f"{parsed_query.netloc}+{url_path}"

    def _clone_or_pull(self):
        if self.query in self.provider.done_queries:
            self.provider.limit_mode = False
            return

        if os.path.exists(self.local_path()):
            if self.provider.settings.fetch_to_update:
                try:
                    self._pull_repository()
                except pygit2.GitError as e:
                    error_handler(
                        self.provider.logger,
                        "Failed to pull repository",
                        self.provider.settings.ignore_errors,
                        e,
                    )
            else:
                self.provider.limit_mode = False
        else:
            try:
                self._clone_repository()
            except pygit2.GitError as e:
                error_handler(
                    self.provider.logger,
                    "Failed to clone repository",
                    self.provider.settings.ignore_errors,
                    e,
                )

        self.provider.done_queries.add(self.query)

    def _clone_repository(self):
        try:
            self.provider.logger.info(f"Cloning {self.query} to {self.local_path()}")
            repo = pygit2.clone_repository(
                self.query,
                self.local_path(),
                callbacks=RemoteSSHCallbacks(
                    username=self.provider.settings.ssh_username,
                    public_key=self.provider.settings.ssh_pubkey_path,
                    private_key=self.provider.settings.ssh_privkey_path,
                    passphrase=self.provider.settings.ssh_passphrase,
                ),
            )
            self._check_no_default_branch(repo)
        except pygit2.GitError as e:
            error_handler(
                self.provider.logger,
                "Failed to clone repository",
                self.provider.settings.ignore_errors,
                e,
            )
        except Exception as e:
            error_handler(
                self.provider.logger,
                "An unexpected error occurred while cloning",
                self.provider.settings.ignore_errors,
                e,
            )

    def _pull_repository(self):
        repo = None
        try:
            self.provider.logger.info(
                f"Pulling repository {self.query} in {self.local_path()}"
            )
            repo = pygit2.Repository(self.local_path())
            remote = repo.remotes["origin"]
            remote.fetch(
                callbacks=RemoteSSHCallbacks(
                    username=self.provider.settings.ssh_username,
                    public_key=self.provider.settings.ssh_pubkey_path,
                    private_key=self.provider.settings.ssh_privkey_path,
                    passphrase=self.provider.settings.ssh_passphrase,
                )
            )
        except pygit2.GitError as e:
            error_handler(
                self.provider.logger,
                "Failed to pull repository",
                self.provider.settings.ignore_errors,
                e,
            )
        except Exception as e:
            error_handler(
                self.provider.logger,
                "An unexpected error occurred while pulling",
                self.provider.settings.ignore_errors,
                e,
            )

        if repo and hasattr(self.provider.settings, "custom_heads"):
            self._checkout_custom_head(repo)

    def _checkout_custom_head(self, repo):
        if not self.provider.settings.custom_heads:
            return

        if self.query in self.provider.settings.custom_heads:
            custom_head = self.provider.settings.custom_heads[self.query]
            try:
                tag = custom_head.get("tag", None)
                branch = custom_head.get("branch", None)
                commit_id = custom_head.get("commit", None)
                commit = None
                self.provider.logger.info(
                    f"Checking out custom head for {self.query}: "
                    f"tag={tag}, branch={branch}, commit_id={commit_id}"
                )
                if tag:
                    commit = repo.revparse_single(f"refs/tags/{tag}")
                    repo.set_head(commit.id)
                elif commit_id:
                    commit = repo.revparse_single(commit_id)
                    repo.set_head(commit.id)
                elif branch:
                    commit = repo.revparse_single(f"refs/heads/{branch}")
                    repo.set_head(f"refs/heads/{branch}")
                else:
                    commit = repo.head.peel()

                repo.checkout_tree(commit, strategy=pygit2.GIT_CHECKOUT_FORCE)
            except pygit2.GitError as e:
                error_handler(
                    self.provider.logger,
                    "Failed to checkout custom head",
                    self.provider.settings.ignore_errors,
                    e,
                )
            except Exception as e:
                error_handler(
                    self.provider.logger,
                    "An unexpected error occurred while checking out custom head",
                    self.provider.settings.ignore_errors,
                    e,
                )

    def _check_no_default_branch(self, repo: pygit2.Repository):
        """Check if the repository has no default branch."""
        if not repo.head_is_unborn:
            return

        self.provider.logger.warning(
            f"The repository {self.query} has no default branch."
        )
        first_remote_branch = None
        for ref in repo.references:
            if ref.startswith("refs/remotes/origin/"):
                first_remote_branch = ref
                break

        if first_remote_branch is None:
            error_handler(
                self.provider.logger,
                "No remote branches found in the repository",
                self.provider.settings.ignore_errors,
                Exception("No refs/remotes/origin/* found."),
            )

        self.provider.logger.info(
            f"Checking out the first remote branch: {first_remote_branch}"
        )

        try:
            repo.set_head(first_remote_branch)
            commit = repo.revparse_single(first_remote_branch)
            repo.checkout_tree(commit, strategy=pygit2.GIT_CHECKOUT_FORCE)
        except pygit2.GitError as e:
            error_handler(
                self.provider.logger,
                "Failed to checkout the first remote branch",
                self.provider.settings.ignore_errors,
                e,
            )

        return
