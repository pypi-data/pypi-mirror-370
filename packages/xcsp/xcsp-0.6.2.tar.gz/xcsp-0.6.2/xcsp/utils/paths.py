"""Path utilities for XCSP Launcher.

This module centralizes all filesystem paths used by the launcher:
logs, solver installations, solver configurations, binaries, and user preferences.
"""

import os
import sys
from pathlib import Path
from typing import Iterable

from platformdirs import user_cache_dir, user_config_dir, user_data_dir
from rich.console import Console
from rich.table import Table

from xcsp import __title__

def get_cache_dir() -> Path:
    """Return the directory where cache files are stored."""
    return Path(user_cache_dir(__title__, __title__))

def get_solver_install_dir() -> Path:
    """Return the directory where solver sources are downloaded and compiled."""
    return Path(user_data_dir(__title__, __title__)) / "solvers"

def get_solver_config_dir() -> Path:
    """Return the directory where user-specific solver configuration files (.xsc.yaml) are stored."""
    return Path(user_config_dir(__title__, __title__)) / "solvers"

def get_bin_dir_of_solver(solver: str, version: str) -> Path:
    """Return the directory where compiled solver binaries are stored.

    Args:
        solver (str): Solver name.
        version (str): Solver version.

    Returns:
        Path: Path to the directory containing binaries for the given solver and version.
    """
    return get_solver_bin_dir() / solver / version


def get_solver_bin_dir():
    return Path(user_data_dir(__title__, __title__)) / "bin"


def get_user_preferences_dir() -> Path:
    """Return the directory for storing user preferences (e.g., config.yaml, settings)."""
    return Path(user_config_dir(__title__, __title__))

def get_system_config_dir() -> list[Path]:
    """Return the system-wide directory for installed solver configurations.

    This depends on the operating system:
    - Windows: C:/Program Files/<AppName>/configs
    - macOS: /usr/local/share/<AppName>/configs
    - Linux: /usr/share/<AppName>/configs

    Returns:
        Path: System configuration directory path.
    """
    if sys.platform == "win32":
        return [Path(f"C:/Program Files/{__title__}/configs")] # TODO: Possibly allow custom installation paths?
    elif sys.platform == "darwin":
        return [Path(f"/usr/local/share/{__title__}/configs"),Path(f'/opt/homebrew/{__title__}/configs')]
    else:
        return [Path(f"/usr/share/{__title__}/configs")]


def get_system_tools_dir() -> Iterable[Path]:
    """Return the system-wide directory for external tools.

    This depends on the operating system:
    - Windows: C:/Program Files/<AppName>/tools
    - macOS: /usr/local/share/<AppName>/tools
    - Linux: /usr/share/<AppName>/tools

    Returns:
        Path: System configuration directory path.
    """
    if sys.platform == "win32":
        return [Path(f"C:/Program Files/{__title__}/tools")]  # TODO: Possibly allow custom installation paths?
    elif sys.platform == "darwin":
        return [Path(f"/usr/local/share/{__title__}/tools"),Path(f'/opt/homebrew/{__title__}/tools'),Path(f'/opt/homebrew/share/{__title__}/tools')]
    else:
        return [Path(f"/usr/share/{__title__}/tools")]

def print_path_summary():
    """Print a summary of important XCSP Launcher paths using Rich."""
    console = Console(width=200)
    table = Table(title=f"[bold cyan]{__title__} – Path Summary", show_lines=True)

    table.add_column("Purpose", justify="center")
    table.add_column("Path", justify="center")

    table.add_row("🧱 Solver install dir (sources and deps)", str(get_solver_install_dir()))
    table.add_row("🧱 Solver binary dir (binaries for each version) ", str(get_solver_bin_dir()))
    table.add_row("📦 System config dir", ", ".join(map(str, get_system_config_dir())))
    table.add_row("🧪 Solver config dir", str(get_solver_config_dir()))
    table.add_row("⚙️ User preferences", str(get_user_preferences_dir()))
    table.add_row("🧠 Cache directory (logs)", str(get_cache_dir()))

    console.print(table)

class ChangeDirectory:
    """Context manager to temporarily change the current working directory."""

    def __init__(self, new_path: Path):
        """Initialize the context manager with the target directory."""
        self.new_path = new_path
        self.saved_path = os.getcwd()

    def __enter__(self):
        """Change the working directory when entering the context."""
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        """Restore the original working directory when exiting the context."""
        os.chdir(self.saved_path)

# Ensure important directories exist at startup
for path in [get_cache_dir(), get_solver_install_dir(), get_solver_config_dir(), get_user_preferences_dir()]:
    path.mkdir(parents=True, exist_ok=True)
