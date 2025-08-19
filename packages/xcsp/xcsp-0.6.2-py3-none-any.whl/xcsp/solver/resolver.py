"""Solver configuration resolver for XCSP Launcher.

This module provides utilities to locate a solver configuration file (.xsc.yaml)
either from the local cloned repository or from the system-installed configurations.
It supports fallback mechanisms and ensures the correct configuration is used during installation.
"""

from pathlib import Path
from loguru import logger

import xcsp.utils.paths as paths

# Default list of acceptable configuration file extensions
DEFAULT_EXT = [".xsc.yaml", ".xsc", ".solver.yaml", ".solver",".xsc.yml", ".solver.yml"]

def find_local_config(clone_path: Path, solver_name: str) -> Path | None:
    """Search for a configuration file in the cloned solver repository.

    Args:
        clone_path (Path): Path to the cloned repository.
        solver_name (str): Name of the solver to match configuration files.

    Returns:
        Path | None: Path to the configuration file if found, otherwise None.
    """
    logger.info(f"Searching for a local configuration file in {clone_path}...")
    for ext in DEFAULT_EXT:
        logger.debug(f"We try to found a configuration with the extension {ext}")
        for file in clone_path.glob(f"**/{solver_name}{ext}"):
            logger.success(f"Local configuration file found: {file}")
            return file
    logger.info("No local configuration file found.")
    return None

def find_system_config(solver_name: str) -> Path | None:
    """Search for a configuration file in the system-wide installed configurations.

    Args:
        solver_name (str): Name of the solver to match configuration files.

    Returns:
        Path | None: Path to the system configuration file if found, otherwise None.
    """
    system_path = paths.get_system_config_dir() / f"{solver_name.lower()}.xsc.yaml"
    logger.info(f"Searching for a system configuration file in {paths.get_system_config_dir()}...")
    if system_path.exists():
        logger.success(f"System configuration file found: {system_path}")
        return system_path
    logger.info("No system configuration file found.")
    return None

def find_user_config(solver_name: str) -> Path | None:
    """Search for a configuration file in the user installed configurations.

    Args:
        solver_name (str): Name of the solver to match configuration files.

    Returns:
        Path | None: Path to the system configuration file if found, otherwise None.
    """
    logger.info(f"Searching for a user configuration file in {paths.get_solver_config_dir()}...")

    for ext in DEFAULT_EXT:
        logger.debug(f"We try to found a configuration with the extension {ext}")
        user_path = paths.get_solver_config_dir() / f"{solver_name.lower()}{ext}"
        if user_path.exists():
            logger.success(f"User configuration file found: {user_path}")
            return user_path
    logger.info("No user configuration file found.")
    return None

def resolve_config(clone_path: Path, solver_name: str) -> Path | None:
    """Resolve the best available configuration file for a solver.

    The method tries, in order:
    1. To find a local configuration file in the cloned repository.
    2. To find a system-wide installed configuration file.
    3. To find a user installed configuration file.

    Args:
        clone_path (Path): Path to the cloned repository.
        solver_name (str): Name of the solver.

    Returns:
        Path | None: Path to the configuration file if found, otherwise None.
    """
    logger.info(f"Resolving configuration for solver '{solver_name}'...")
    config = find_local_config(clone_path, solver_name)
    if config:
        return config

    config = find_system_config(solver_name)
    if config:
        return config

    config = find_user_config(solver_name)
    if config:
        return config


    logger.warning(
        f"No configuration file found for solver '{solver_name}'. "
        f"It is highly recommended to provide a solver configuration (.xsc.yaml) file in the git repository or in {paths.get_system_config_dir()}."
    )
    return None
