from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Tuple

from vectice.api.json.code_version import CodeVersion, DatabricksVersion, GitVersion
from vectice.utils.common_utils import hide_logs

if TYPE_CHECKING:
    from git.repo import Repo


_logger = logging.getLogger(__name__)


def capture_code_version() -> CodeVersion | None:
    """Capture code version.

    Implementation that captures the code version to be sent to the BE as part of registering assets for the lineage

    Returns:
        CodeVersion or None
    """
    repository, databricks_code_source = _look_for_repos()
    code_version: CodeVersion | None = None
    if repository:
        git_version: GitVersion | None = _extract_git_version(repository)
        code_version = CodeVersion(git_version=git_version) if git_version else code_version
    elif databricks_code_source is not None:
        databricks_version = _extract_databricks_code_version(databricks_code_source)
        code_version = CodeVersion(databricks_version=databricks_version) if databricks_version else code_version

    return code_version


def is_databricks():
    return "DATABRICKS_RUNTIME_VERSION" in os.environ


def _look_for_repos() -> Tuple[Repo | None, Dict[str, Any] | None]:
    databricks_code_source: Dict[str, Any] | None = None
    repository = _look_for_git_repository()

    if is_databricks():
        databricks_code_source = _look_for_databricks_code_source_info()

    return repository, databricks_code_source


def _look_for_databricks_code_source_info() -> Dict[str, Any] | None:
    databricks_code_source: Dict[str, Any] | None = None
    try:
        from IPython.core.getipython import get_ipython

        ipython_content = get_ipython().get_parent()  # type: ignore
        databricks_code_source = {
            "date": ipython_content["header"]["date"],
            "browserHostName": ipython_content["metadata"]["commandMetadata"]["tags"]["browserHostName"],
            "notebook_path": ipython_content["metadata"]["commandMetadata"]["extraContext"]["notebook_path"],
            "notebook_id": ipython_content["metadata"]["commandMetadata"]["extraContext"]["notebook_id"],
        }
    except Exception as error:
        _logger.debug(f"Code capture databrick failed: {error.__class__.__name__}: {error}. ")
        _logger.info("Extracting the code source version from Databricks failed.")

    return databricks_code_source


def _look_for_git_repository(repo_path: str = ".") -> Repo | None:
    def _log_error(error: str):
        _logger.debug(
            f"Code capture git failed: {error.__class__.__name__}: {error}. "
            "Make sure the current directory is a valid Git repository (non-bare, non worktree) "
            "and its permissions allow the current user to access it."
        )

    try:
        from git import GitError
    except ImportError as error:
        _log_error(str(error))
        return None

    try:
        repo_path = os.path.abspath(repo_path)
    except OSError:
        _logger.debug(f"Code capture failed: the directory '{repo_path}' cannot be accessed by the system")
        return None
    try:
        from git.repo import Repo

        return Repo(repo_path, search_parent_directories=True)
    except GitError as error:
        _log_error(str(error) or repo_path)
        return None


def _extract_databricks_code_version(databricks_code_source: Dict[str, Any]) -> DatabricksVersion:
    url = f"https://{databricks_code_source['browserHostName']}/#notebook/{databricks_code_source['notebook_id']}"
    relative_path = databricks_code_source["notebook_path"]
    date = databricks_code_source["date"]
    databricks_version = DatabricksVersion(url_notebook=url, relative_path=relative_path, timestamp=date)
    return databricks_version


def inform_if_git_repo():
    with hide_logs("vectice"):
        repo = _look_for_git_repository()
    if repo:
        _logger.debug("A git repository was found but code capture is disabled.")


def _extract_git_version(repository: Repo) -> GitVersion | None:
    prefix = "Extracting the Git version failed"
    try:
        url = repository.remotes.origin.url
    except Exception as error:
        _logger.warning(f"{prefix}: we couldn't get the remote URL (no origin?): {error!r}")
        return None
    url = url.rsplit(".git", 1)[0]
    repository_name = url.split("/")[-1]
    try:
        branch_name = repository.active_branch.name
    except Exception as error:
        _logger.warning(f"{prefix}: we couldn't get the branch name (detached mode?): {error!r}")
        return None
    try:
        commit_hash = repository.head.object.hexsha
    except Exception as error:
        _logger.warning(f"{prefix}: we couldn't get the commit hash (no commits?): {error!r})")
        return None
    is_dirty = repository.is_dirty()
    uri = _extract_aws_code_commit(url, repository_name, commit_hash) if "amazonaws" in url else url
    return GitVersion(repository_name, branch_name, commit_hash, is_dirty, uri)


def _extract_aws_code_commit(url: str, repository_name: str, commit_hash: str) -> str:
    region = url.split(".")[1]
    return f"https://{region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repository_name}/commit/{commit_hash}?region={region}"
