import platform
from loguru import logger
import psutil
def is_system_compatible(system_config) -> bool:
    """
    Check if the current system is compatible with the given system config.

    Args:
        system_config (str or list[str]): The 'system' field from YAML.

    Returns:
        bool: True if the current system matches the config, False otherwise.
    """
    if not system_config:
        return False  # defensive default

    current_system = normalized_system_name()

    # Normalize config
    if isinstance(system_config, str):
        system_config = [system_config]

    normalized_config = {s.strip().lower() for s in system_config}

    return "all" in normalized_config or current_system in normalized_config


def normalized_system_name():
    # Normalize current platform
    current_system = platform.system().lower()  # e.g., "linux", "darwin", "windows"
    if current_system == "darwin":
        current_system = "macos"
    return current_system


def kill_process(process, timeout, solver):
    try:
        if process.is_running():
            logger.warning(f"Solver exceeded time limit of {timeout}s. Killing process.")
            process.kill()
            logger.info(f"Process killed successfully after exceeding time limit.")
            solver.set_is_timeout(True)
        else:
            logger.info("Process already terminated before timeout.")
    except psutil.NoSuchProcess:
        logger.error("No such process found when attempting to kill it.")
    except psutil.AccessDenied:
        logger.error("Permission denied while trying to kill the process.")
    except Exception as e:
        logger.exception(f"An error occurred while trying to kill the process: {e}")

def term_process(process, timeout, solver):
    try:
        if process.is_running():
            logger.warning(f"Send a SIGTERM to process after {timeout}s.")
            process.terminate()
            logger.info(f"SIGTERM send successfully.")
            solver.set_is_timeout(True)
        else:
            logger.info("Process already terminated before timeout.")
    except psutil.NoSuchProcess:
        logger.error("No such process found when attempting to terminate it.")
    except psutil.AccessDenied:
        logger.error("Permission denied while trying to terminate the process.")
    except Exception as e:
        logger.exception(f"An error occurred while trying to terminate the process: {e}")