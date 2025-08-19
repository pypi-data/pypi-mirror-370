import os.path
from abc import ABC, abstractmethod

from git import Repo
from loguru import logger
from timeit import default_timer as timer

from xcsp.utils.archive import extract_archive
from xcsp.utils.http import download
from xcsp.utils.system import normalized_system_name
import requests

def _download(v, version_path):
    url = v.get("urls", dict()).get(normalized_system_name())
    if url is None:
        logger.error(
            f"The version {v.get('version')} has no URL for the current system {normalized_system_name()}.")
        return None
    logger.info(f"Downloading version {v.get('version')} from {url} to {version_path}/tmp")
    archive_name = url.split("/")[-1]
    try:
        path = version_path / "tmp" / archive_name
        download(url, path)
        logger.info(f"Version {v.get('version')} downloaded successfully.")
        return path
    except requests.RequestException as e:
        logger.error(f"Failed to download version {v.get('version')} from {url}: {e}")
        return None



class Backend(ABC):
    def __init__(self, repo_path, meta: dict):
        self._repo_path = repo_path
        self._repo = None
        self._meta = meta
        self._current_version = None
        self._original_version = None
        self._cwd = None

    @abstractmethod
    def init(self):
        """
        Initializes the repository. This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def change_version(self, version: str):
        """
        Changes the current version of the repository to the specified version.

        Args:
            version (str): The version to switch to.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def restore(self):
        """
        Restores the original version of the repository.
        """
        self.change_version(self._original_version)
    @abstractmethod
    def get_source_path(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def get_current_version(self):
        return self._current_version

    def get_cwd(self):
        return self._cwd


class GitVersionBackend(Backend):
    def init(self):
        start_time = timer()
        logger.info(f"Cloning the solver from {self._meta.get('git')} into {self._repo_path}")
        self._repo = self._repo = Repo(self._repo_path) if os.path.exists(self._repo_path) else Repo.clone_from(
            self._meta.get("git"), self._repo_path, recursive=True)
        # o = self._repo.remotes.origin
        # o.pull()
        logger.info(f"Repository cloned in {timer() - start_time:.2f} seconds.")
        self._original_version = self._repo.active_branch.name if not self._repo.head.is_detached else self._repo.head.object.hexsha
        self._current_version = self._original_version
        self._cwd = self._repo_path

    def change_version(self, version: str):
        self._repo.git.checkout(version)
        self._current_version = version

    def get_source_path(self):
        return self.get_cwd()




class ArchiveVersionBackend(Backend):
    def init(self):
        global_timer = timer()
        for index, v in enumerate(self._meta.get("versions", [])):
            logger.info(f"Starting to initialize (download and extract) version: {v.get('version')}")
            version_path = self._repo_path / v.get("version")
            version_path.mkdir(parents=True, exist_ok=True)

            if index == 0:
                self._current_version = v.get("version")
                self._original_version = v.get("version")
                self._cwd = version_path


            tmp_path = version_path / "tmp"
            tmp_path.mkdir(parents=True, exist_ok=True)

            source_path = version_path / "source"
            source_path.mkdir(parents=True, exist_ok=True)

            download_timer = timer()
            archive_name = _download(v, version_path)
            logger.success(f"Download completed in {timer() - download_timer:.2f} seconds for version {v.get('version')}.")
            if archive_name is None:
                logger.error(f"Failed to download version {v.get('version')}. Skipping.")
                continue
            try:
                extract_timer = timer()
                extract_archive(archive_name, source_path)
                logger.success(f"Archive {archive_name} extracted successfully for version {v.get('version')} in {timer() - extract_timer:.2f} seconds.")
            except Exception as e:
                logger.error(f"Failed to extract archive {archive_name} for version {v.get('version')}: {e}")
                logger.exception(e)
                continue
            logger.success(f"Version {v.get('version')} initialized successfully in {timer() - global_timer:.2f} seconds.")
        logger.info("All versions processed in {:.2f} seconds.".format(timer() - global_timer))
    def change_version(self, version: str):
        version_path = self._repo_path / version
        if not version_path.is_dir() or not version_path.exists():
            logger.error(f"Version {version} does not exist.")
            return
        self._cwd  = version_path

    def get_source_path(self):
        return self.get_cwd() / "source"


class LocalUserVersionBackend(Backend):
    def init(self):
        self._original_version = "current"
        self._current_version = "current"
        self._cwd = self._repo_path

    def change_version(self, version: str):
        logger.info("No version change needed for local user repository.")

    def get_source_path(self):
        return self.get_cwd()

