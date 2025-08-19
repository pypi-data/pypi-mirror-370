"""Solver installation manager for XCSP Launcher.

This module handles the full process of installing a solver from a repository:
cloning the repository, detecting or resolving configuration files, verifying
build requirements, building the solver, and placing binaries at the correct locations.
"""

import enum
import os
import platform
import shutil
import tempfile
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path

import requests
import yaml
from git import Repo
from loguru import logger
from timeit import default_timer as timer

from xcsp.builder.build import AutoBuildStrategy, ManualBuildStrategy
from xcsp.builder.check import check_available_builder_for_language, MAP_FILE_LANGUAGE, MAP_LANGUAGE_FILES, MAP_BUILDER
from xcsp.utils.archive import ALL_ARCHIVE_EXTENSIONS, extract_archive
from xcsp.utils.args import at_least_one, at_most_one
from xcsp.utils.dict import get_with_fallback
from xcsp.utils.http import resolve_url, download
from xcsp.utils.placeholder import replace_placeholder, replace_core_placeholder, replace_solver_dir_in_str, \
    replace_bin_dir_in_str
from xcsp.solver.cache import CACHE, Cache
from xcsp.solver.resolver import resolve_config, DEFAULT_EXT
import xcsp.utils.paths as paths
from xcsp.utils.log import unknown_command
from xcsp.utils.softwarevers import sort_versions
from xcsp.utils.system import is_system_compatible, normalized_system_name
from xcsp.utils.versiondir.core import VersionDirectory


class RepoSource(enum.Enum):
    """Enumeration of supported repository hosting services."""
    GITHUB = "github.com"
    GITLAB = "gitlab.com"


class ConfigStrategy(ABC):
    """Abstract base class representing a strategy for handling solver configurations."""

    def __init__(self, solver_path: Path, repo):
        self._language = None
        self._builder_file = None
        self._solver_path = solver_path
        self._repo = repo

    def check(self):
        """Check if a valid builder is available for the detected language."""
        return check_available_builder_for_language(self.language())

    def language(self):
        """Return the programming language of the solver."""
        return self._language

    def builder_file(self) -> Path:
        """Return the main build configuration file."""
        return self._builder_file

    @abstractmethod
    def versions(self):
        """Yield information about available versions of the solver."""
        pass

    @abstractmethod
    def detect_language(self):
        """Detect the programming language of the solver based on available files."""
        pass


class NoConfigFileStrategy(ConfigStrategy):
    """Strategy used when no solver configuration file is provided."""

    def versions(self):
        """Yield a single version 'latest' based on the current commit hash."""
        yield {"version": "latest", "git_tag": self._repo.head.object.hexsha, "alias": []}

    def detect_language(self):
        """Attempt to detect the language by scanning known build files."""
        list_files = set(os.listdir(self._solver_path))
        for file in MAP_FILE_LANGUAGE.keys():
            if file in list_files:
                self._language = MAP_FILE_LANGUAGE[file]
                self._builder_file = Path(self._solver_path, file)
                logger.success(f"Detected language using builder file '{file}': {self.language()}")
                return
        raise ValueError("Unable to detect the project language automatically.")


class ConfigFileStrategy(ConfigStrategy):
    """Strategy used when a solver configuration file is available."""

    def __init__(self, solver_path: Path, config):
        super().__init__(solver_path, None)
        self._config = config

    def language(self):
        """Return the programming language from the configuration."""
        return self._config["language"]

    def detect_language(self):
        """Detect the language based on configuration and project structure."""
        logger.success(f"Language provided by configuration file: {self.language()}")
        l = self.language()
        files = MAP_LANGUAGE_FILES[l]
        logger.debug(f"Looking for one of: {', '.join(files)}")

        list_files = set(os.listdir(self._solver_path))
        for f in files:
            if f in list_files:
                self._builder_file = Path(self._solver_path, f)
                return

    def versions(self):
        """Yield all versions specified in the configuration."""
        for v in self._config["versions"]:
            yield v


def build_cmd(config, bin_executable, bin_dir):
    result_cmd = []
    if config["command"].get("prefix"):
        result_cmd.extend(replace_placeholder(config["command"]["prefix"]))

    template = config["command"]["template"]
    options = config["command"].get("always_include_options")
    result_cmd.extend(replace_core_placeholder(template, bin_executable, bin_dir, options))
    return result_cmd


class Installer:
    """Main class responsible for installing a solver from a repository."""

    def __init__(self, url: str, solver_name: str, id_s: str, config=None):
        self._url = url
        self._solver = solver_name
        self._id = id_s
        self._path_solver = None
        self._start_time = timer()
        self._repo = None
        self._config = config
        self._config_strategy = None
        self._mode_build_strategy = None

    def _init(self):
        """Initialize the solver installation directory."""
        self._path_solver = Path(paths.get_solver_install_dir()) / self._id

        if not self._id in CACHE:
            CACHE[self._id] = {
                "path_solver": str(self._path_solver.absolute()),
                "name_solver": self._solver,
                "id_solver": self._id,
                "versions": defaultdict(dict),
            }

    def _resolve_config(self):
        """Resolve and load the solver configuration if available."""

        if self._config is not None:
            self._init_strategies_with_config()
            return

        config_file = resolve_config(self._path_solver, self._solver)

        if config_file is None:
            self._config_strategy = NoConfigFileStrategy(self._path_solver, self._repo)
            self._mode_build_strategy = AutoBuildStrategy(self._path_solver, self._config_strategy)
            return

        with open(config_file, "r") as f:
            self._config = yaml.safe_load(f)
            self._init_strategies_with_config()

    def _init_strategies_with_config(self):
        self._config_strategy = ConfigFileStrategy(self._path_solver, self._config)
        if self._config.get("mode", "manual") == "auto":
            self._mode_build_strategy = AutoBuildStrategy(self._path_solver, self._config_strategy)
        else:
            self._mode_build_strategy = ManualBuildStrategy(self._path_solver, self._config_strategy, self._config)

    def _check(self):
        """Check if the required build tools are available."""
        if not self._config_strategy.check():
            language = self._config_strategy.language()
            logger.error(
                f"None of the builders are available for language '{language}': {', '.join(MAP_BUILDER.get(language))}")
            raise ValueError(
                f"No available builders for the detected language '{language}'.")

    def _manage_dependency(self):
        start_dep_time = timer()
        if not self._config:
            return

        dependencies = self._config.get("build", {}).get("dependencies", [])
        if not dependencies:
            logger.info("No dependencies to manage.")
            return

        logger.info("Managing solver dependencies...")
        for dep in dependencies:
            git_url = dep.get("git")
            url = dep.get("url")
            if git_url:
                self._manage_git_dependency(dep, git_url)
            elif url and any(url.endswith(ext) for ext in ALL_ARCHIVE_EXTENSIONS):
                self._manage_archive_dependency(dep, url)
            elif url:
                self._manage_file_dependency(dep, url)
            else:
                logger.warning(f"Dependency {dep} does not have a valid URL or git repository specified.")
                continue

    def _manage_git_dependency(self, dep, git_url):
        name = git_url.split("/")[-1].replace(".git", "")
        default_dir = self._path_solver.parent.parent / "deps" / name
        target_dir = replace_solver_dir_in_str(dep.get("dir"), str(self._repo.get_source_path)) if dep.get(
            "dir") else default_dir
        target_dir = Path(target_dir)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if target_dir.exists():
            logger.info(f"Updating existing dependency in: {target_dir}")
            start_time = timer()
            try:
                repo = Repo(target_dir)
                repo.remotes.origin.pull()
                logger.success(f"Pulled updates for {name} in {timer() - start_time:.2f}s.")
            except Exception as e:
                logger.error(f"Failed to update dependency at {target_dir}: {e}")
        else:
            logger.info(f"Cloning dependency '{name}' into: {target_dir}")
            start_time = timer()
            try:
                Repo.clone_from(git_url, target_dir)
                logger.success(f"Cloned {name} in {timer() - start_time:.2f}s.")
            except Exception as e:
                logger.error(f"Failed to clone dependency from {git_url} to {target_dir}: {e}")

    def _manage_archive_dependency(self, dep, url):
        name = url.split("/")[-1].split(".")[0]
        default_dir = self._repo.get_source_path().parent / "deps" / name
        target_dir = replace_solver_dir_in_str(dep.get("dir"), str(self._repo.get_source_path())) if dep.get(
            "dir") else default_dir
        target_dir = Path(target_dir)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        if target_dir.exists():
            logger.info("Dependency already exists, nothing to do.")
            return
        logger.info(f"Downloading and extracting dependency from {url} to {target_dir}")
        start_time = timer()
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                download(url, tmp_dir)
                logger.info(f"Downloaded finished in {timer() - start_time:.2f} seconds.")
                archive_path = Path(tmp_dir) / url.split("/")[-1]
                extract_archive(archive_path, target_dir)
                logger.success(f"Extracted dependency to {target_dir} in {timer() - start_time:.2f} seconds.")
        except requests.RequestException as e:
            logger.error(f"Failed to download dependency from {url}: {e}")
            logger.exception(e)
        except Exception as e:
            logger.error(f"Failed to extract dependency from {url} to {target_dir}: {e}")
            logger.exception(e)

    def _manage_file_dependency(self, dep, url):
        start_time = timer()
        name = url.split("/")[-1].split(".")[0]
        default_dest = self._repo.get_source_path().parent / "deps" / name
        target_dir = replace_solver_dir_in_str(dep.get("dir"), str(self._repo.get_source_path())) if dep.get(
                "dir") else default_dest
        target_dir = Path(target_dir)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            download(url, target_dir)
            logger.success(f"Downloaded dependency from {url} to {target_dir} in {timer() - start_time:.2f} seconds.")
        except requests.RequestException as e:
            logger.error(f"Failed to download dependency from {url}: {e}")
            logger.exception(e)
        except Exception as e:
            logger.error(f"Failed to manage file dependency from {url} to {target_dir}: {e}")
            logger.exception(e)

    def install(self):
        """Main method to install the solver."""
        self._init()
        self._resolve_config()

        self._raise_for_check_system()
        self._repo = VersionDirectory(self._path_solver, self._config)
        self._config_strategy.detect_language()

        self._manage_dependency()
        self._check()

        have_latest = False
        # original_ref = self._repo.active_branch.name if not self._repo.head.is_detached else self._repo.head.object.hexsha
        with paths.ChangeDirectory(self._path_solver):
            for v in self._config_strategy.versions():
                version_timer = timer()
                logger.info(f"Version '{v['version']}' start ...")
                try:
                    logger.info(f"Move to version '{v['version']}'")
                    self._repo.change_version(get_with_fallback(v, "git_tag", "version"))
                    need_compile = v.get("executable") is not None and not (
                            Path(self._repo.get_source_path()) / v.get('executable')).exists() and not self._config.get(
                        "build", {}).get("per_os", {}).get(normalized_system_name(), {}).get('skip', False)
                    build_start = timer()
                    if not self._mode_build_strategy.build() and need_compile:
                        logger.error(f"Build failed for version '{v['version']}'. Installation aborted.")
                        break
                    logger.info(f"Building completed in {timer() - build_start:.2f} seconds.")
                    bin_dir = paths.get_bin_dir_of_solver(self._id,
                                                          f"{v['version']}-{get_with_fallback(v, 'git_tag', 'version')}")
                    os.makedirs(bin_dir, exist_ok=True)

                    if v.get("executable") is None:
                        logger.warning(
                            f"Version '{v['version']}' was built, but no executable was specified. "
                            f"Please manually copy your binaries into {bin_dir}.")
                        continue
                    executable_path = Path(v['executable'])
                    result_path = shutil.copy(Path(self._repo.get_source_path()) / v["executable"],
                                              bin_dir / executable_path.name)
                    logger.success(f"Executable for version '{v['version']}' successfully copied to {result_path}.")
                    if self._config is not None and self._config.get("command") is not None:
                        CACHE[self._id]["versions"][v['version']] = {
                            "options": self._config["command"].get("options", dict()),
                            "cmd": build_cmd(self._config, bin_dir / executable_path.name, bin_dir),
                            "alias": v.get("alias", list())
                        }
                        have_latest = have_latest or "latest" in v.get("alias", []) or v.get("version") == "latest" or v.get("git_tag") == "latest"
                    logger.debug(executable_path.name)

                    logger.info("Moving files to the binary directory...")
                    for file in v.get("files", []):
                        from_path = replace_solver_dir_in_str(file.get("from"), str(self._repo.get_source_path()))
                        to_path = replace_bin_dir_in_str(file.get("to"), str(bin_dir.absolute()))
                        logger.info(f"Copying file from '{from_path}' to '{to_path}'")
                        try:
                            shutil.copy(from_path, to_path)
                            logger.success(f"{from_path}....OK")
                        except Exception as e:
                            logger.error(f"Failed to move file from '{from_path}' to '{to_path}': {e}")
                            logger.exception(e)
                except OSError as e:
                    logger.error(
                        f"An error occurred when building the version '{v['version']}' of solver {self._solver}")
                    logger.exception(e)
                except Exception as e:
                    logger.error("An unexpected error occurred during the installation process.")
                    logger.exception(e)
                    logger.error(f"Failed to build version '{v['version']}' of solver {self._solver}.")
                finally:
                    logger.info(f"Restoring original repository (if needed)...")
                    self._repo.restore()
                    logger.info(f"Version '{v['version']}' end ... {timer() - version_timer:.2f} seconds.")
            list_versions = sort_versions(list(CACHE[self._id]["versions"].keys()))
            if not have_latest and len(list_versions)>0:
                latest = list_versions[-1]
                logger.debug(list_versions)
                logger.info(f"No version with alias 'latest' found, setting '{latest}' as latest version.")
                CACHE[self._id]["versions"][latest]["alias"].append("latest")
        logger.info("Generating cache of solver...")
        Cache.save_cache(CACHE)
        logger.info(f"Installation (of all versions) completed in {timer() - self._start_time:.2f} seconds.")

    def _raise_for_check_system(self):
        """Raise an error if the system check is not compatible."""
        if self._config is None or "system" not in self._config:
            return
        systems = self._config.get("system", "all")
        if isinstance(systems, str):
            systems = [systems]
        if not is_system_compatible(systems):
            system_list = ",".join(systems) if isinstance(systems, list) else systems
            raise ValueError(
                f"Current system {platform.system().lower()} is not compatible with the system from {system_list}.")


def fill_parser(parser):
    """Add the 'install' subcommand to the parser."""
    parser_install = parser.add_parser("install", aliases=["i"],
                                       help="Subcommand to install a solver from a repository.")
    parser_install.add_argument("--id", help="Unique ID for the solver.", type=str, required=False, default=None)
    parser_install.add_argument("--name", help="Human-readable name of the solver.", type=str, required=False,
                                default=None)
    parser_install.add_argument("-c", "--config", help="A path to a config file.", type=str, required=False,
                                default=None)
    parser_install.add_argument("--url", help="Direct URL to the repository (alternative to --repo).", required=False,
                                default=None)
    parser_install.add_argument("--repo", help="Repository in the form 'namespace/repo' (alternative to --url).",
                                required=False, default=None)
    parser_install.add_argument("--source", help="Hosting service for the repository.", choices=[e for e in RepoSource],
                                default=RepoSource.GITHUB, type=RepoSource)


def install(args):
    """Execute the installation process based on parsed arguments."""
    logger.debug(args)
    manage_conflictual_args(args)

    name = args['name']
    id_s = args['id']
    url = args['url']
    config = None

    config_path = args['config']  # get the config path from args
    if config_path is None and url is not None and any(
            [url.endwith(ext) for ext in DEFAULT_EXT]):  # check if url is a config file
        # if the url is a config file, download it
        config_path = paths.get_solver_config_dir() / url.split("/")[-1]
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(config_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Configuration file downloaded successfully from {url}.")
        except requests.RequestException as e:
            logger.error(f"Failed to download configuration file from {url}: {e}")
            return

    # If a config file is provided, load it
    if config_path is not None and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            name = config['name']
            id_s = config['id']
            url = config.get('git', None) or config.get('path', None)
    # Now if url is always None and config is also None, we try to resolve the url from repo and source
    if url is None and config is None:
        url = resolve_url(args['repo'], args['source'])

    # Now we have either a valid URL or loaded config
    installer = Installer(url, name, id_s, config=config)
    installer.install()


def manage_conflictual_args(args):
    """Ensure that only one of the URL, repo, or config arguments is provided."""
    keys = ['url', 'repo', 'config']
    if not at_least_one(args, keys):
        raise ValueError(",".join(keys) + " cannot be None simultaneously.")
    if not at_most_one(args, keys):
        raise ValueError("Can't be more one of these option specified : " + ",".join(keys) + ". ")


MAP_COMMAND = {
    "install": install,
}


def manage_command(args):
    """Dispatch and manage subcommands for the XCSP launcher binary.

    Args:
        args (dict): Parsed command-line arguments.
    """
    subcommand = args['subcommand']
    MAP_COMMAND.get(subcommand, unknown_command)(args)
