"""Logging utilities for the XCSP Launcher.

This module centralizes logging patterns for consistent message reporting across the application.
"""
import sys

from loguru import logger

def unknown_command(args):
    """Handle unknown or invalid subcommands.

    Args:
        args (Namespace): The parsed arguments where the subcommand was not recognized.
    """
    logger.error(f"Unknown subcommand: {args.get('subcommand', 'N/A')}. Please check the available commands.")


def init_log(level):
    logger.remove()
    logger.add(sys.stderr, level=level)