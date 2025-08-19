"""
Bootstrap module for XCSP Launcher.

This module is responsible for checking whether the user has installed any solvers
and optionally running the bootstrap process to install default solvers.
"""

import sys
from loguru import logger

import xcsp.utils.paths as paths




def check_bootstrap():
    """
    Check if the local solver installation directory is empty.

    This function is typically called at program startup to ensure the user has a working
    set of solvers. If none are found, it prompts the user to run the bootstrap process,
    which installs default solvers.

    """
    solver_dir = paths.get_solver_install_dir()

    if not solver_dir.exists() or not any(solver_dir.iterdir()):
        logger.info("🚀 First-time setup detected: no solvers found.")
        sys.stderr.flush()
        answer = input("Would you like to install default solvers now? [Y/n] ").strip().lower()

        if answer in ("", "y", "yes"):
            logger.info("Running bootstrap to install default solvers...")
            return True
        return False
