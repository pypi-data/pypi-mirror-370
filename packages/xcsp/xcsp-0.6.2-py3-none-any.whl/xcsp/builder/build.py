"""Build system for XCSP Launcher.

This module defines strategies to build solver sources either automatically
(based on detected build files) or manually (based on explicit configuration).
It also provides utility functions to execute builds while logging their output.
"""
import os
import shutil
import stat
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import psutil
from loguru import logger

import xcsp.utils.paths as paths
from xcsp.utils.dict import get_with_fallback
from xcsp.utils.placeholder import replace_placeholder, replace_solver_dir_in_list, replace_solver_dir_in_str
from xcsp.utils.system import normalized_system_name

# Mapping of detected build configuration files to standard build commands
MAP_FILE_BUILD_COMMANDS = {
    "build.gradle": ["./gradlew build -x test", "gradle build -x test"],
    "pom.xml": ["mvn package", "mvn install"],
    "CMakeLists.txt": ["cmake . && make", "cmake .. && make"],
    "Makefile": ["make"],
    "Cargo.toml": ["cargo build"],
    "setup.py": ["python setup.py install", "python setup.py build"],
    "pyproject.toml": ["python -m build"]
}

def try_build_from_file(detected_file: Path, log_path: Path) -> bool:
    """Attempt to build a project based on the detected build configuration file.

    Args:
        detected_file (Path): The main build configuration file (e.g., CMakeLists.txt, build.gradle).
        log_path (Path): Path to the build log file.

    Returns:
        bool: True if the build succeeded, False otherwise.
    """
    build_commands = MAP_FILE_BUILD_COMMANDS.get(detected_file.name)
    if not build_commands:
        logger.error(f"No known build commands associated with '{detected_file.name}'.")
        return False

    log_path.parent.mkdir(parents=True, exist_ok=True)

    success = False
    for command in build_commands:
        logger.info(f"Trying build command: {command}")

        with open(log_path, "a") as log_file:
            log_file.write(f"\n--- Trying build command: {command} ---\n")
            log_file.flush()

            try:
                process = psutil.Popen(
                    command,
                    shell=True,
                    cwd=detected_file.parent,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                returncode = process.wait()
                if returncode == 0:
                    logger.success(f"Build succeeded with command: {command}")
                    success = True
                    return True
                else:
                    logger.warning(f"Build failed with command: {command} (exit code {returncode})")

            except Exception as e:
                logger.exception(f"Exception occurred during build: {e}")

    if not success:
        logger.error("All attempted build commands failed.")
    return success

class BuildStrategy(ABC):
    """Abstract base class representing a build strategy for a solver."""

    def __init__(self, path_solver: Path, config_strategy, config=None):
        self._path_solver = path_solver
        self._config_strategy = config_strategy
        self._config = config

    def build(self) -> bool:
        """Execute the build process inside the solver directory."""
        with paths.ChangeDirectory(self._path_solver):
            return self._internal_build()

    @abstractmethod
    def _internal_build(self) -> bool:
        """Internal method for performing the build, must be implemented by subclasses."""
        pass

class AutoBuildStrategy(BuildStrategy):
    """Build strategy using automatic detection based on known build files."""

    def _internal_build(self) -> bool:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(paths.get_cache_dir()) / f"solver_build_{timestamp}.log"
        return try_build_from_file(self._config_strategy.builder_file(), log_path)

class ManualBuildStrategy(BuildStrategy):
    """Build strategy using manual build instructions provided in the configuration."""

    def __init__(self, path_solver: Path, config_strategy, config):
        super().__init__(path_solver, config_strategy, config)

    def _internal_build(self) -> bool:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path(paths.get_cache_dir()) / f"solver_build_{timestamp}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Log of building in {log_path}")

        build_config = self._config.get("build", {})
        build_steps = get_with_fallback(build_config,"default_steps","build_steps",{}) #build_steps for retro compatibility
        skip_for_system = False
        if "build_steps" in build_steps:
            logger.warning("Using 'build_steps' in configuration is deprecated, use 'default_steps' instead.")
        if "per_os" in build_steps:
            build_steps = build_config.get("per_os",{}).get(normalized_system_name(),{}).get("steps",None)
            skip_for_system = build_config.get("per_os",{}).get(normalized_system_name(),{}).get("skip",None)

        build_command = build_config.get("build_command")
        # 🧹 Normalisation
        if build_steps is None and build_command:
            if isinstance(build_command, str):
                build_command = [build_command]
            build_steps = [{"cmd": c} for c in build_command]

        if not build_steps and not skip_for_system:
            logger.warning("No manual build command specified in configuration.")
            return False
        elif skip_for_system:
            logger.info(f"Skipping manual build for {normalized_system_name()} as per configuration.")
            return True

        success = False

        with open(log_path, "a") as log_file:
            log_file.write("\n--- Trying manual build ---\n")
            logger.info("Trying manual build")

            for index, step in enumerate(build_steps):
                cmd_raw = step.get("cmd")
                if not cmd_raw:
                    logger.warning(f"Step {index + 1} is missing 'cmd'. Skipping.")
                    continue

                cwd_raw = step.get("cwd", str(self._path_solver))

                cmd = replace_solver_dir_in_list(replace_placeholder(cmd_raw), str(self._path_solver))
                try:
                    if not shutil.which(cmd[0]) and not os.access(cmd[0], os.X_OK):
                        path = Path(cmd[0])
                        current_mode = path.stat().st_mode
                        path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                except Exception as e:
                    logger.exception(f"Exception occurred during manual build (chmod on {cmd[0]}): {e}")
                    logger.error("Current working directory: {}".format(os.getcwd()))
                    return False

                cwd_str = replace_solver_dir_in_str(cwd_raw,str(self._path_solver))

                logger.info(f"Step {index + 1}/{len(build_steps)}: {' '.join(cmd)}")
                log_file.write(f"Step {index + 1}/{len(build_steps)}: {' '.join(cmd)} (cwd: {cwd_str})\n")
                log_file.flush()

                try:
                    result = subprocess.run(
                        cmd,
                        cwd=cwd_str,
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                    if result.returncode == 0:
                        logger.success(f"Step {index + 1} succeeded.")
                        success = True
                    else:
                        logger.warning(f"Step {index + 1} failed with exit code {result.returncode}.")
                        success = False
                        break
                except Exception as e:
                    logger.exception(f"Exception occurred during step {index + 1}: {e}")
                    success = False
                    break

            if not success:
                logger.error("Manual build failed after all steps.")

        return success
