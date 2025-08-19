from pathlib import Path

from xcsp.utils.versiondir.backend import GitVersionBackend, LocalUserVersionBackend, ArchiveVersionBackend


class VersionDirectory:
    def __init__(self, root_path: Path, meta_info: dict):
        self._root_path = root_path
        self._meta_info = meta_info
        local_path = meta_info.get("path", None)
        is_local_git = (local_path / ".git").exists() if local_path else False
        self._impl = None
        if local_path or is_local_git:
            self._impl = LocalUserVersionBackend(self._root_path, self._meta_info)
        elif meta_info.get("git",None) is not None:
            self._impl = GitVersionBackend(self._root_path, self._meta_info)
        else:
            self._impl = ArchiveVersionBackend(self._root_path, self._meta_info)
        self._impl.init()
    def change_version(self, version: str) -> None:
        """
        Changes the current version to the specified version.
        """
        self._impl.change_version(version)

    def get_root_path(self) -> Path:
        """
        Returns the root path of the version directory.
        """
        return self._root_path

    def get_current_version_path(self) -> Path:
        """
        Returns the path of the current version.
        """
        return self._impl.get_cwd()
    def restore(self):
        """
        Restores the original version of the repository.
        """
        self._impl.change_version(self._impl.get_current_version())

    def get_source_path(self):
        """
        Returns the source path of the current version.
        """
        return self._impl.get_source_path()