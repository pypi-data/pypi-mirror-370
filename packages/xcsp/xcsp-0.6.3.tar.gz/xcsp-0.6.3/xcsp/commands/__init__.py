import importlib

from loguru import logger

ALIAS_COMMANDS = {
    "i": "install",
    "s": "solver"
}

def manage_subcommand(arguments):
    # Executing the specified Metrics command.
    command = arguments['subcommand']
    try:
        if command in ALIAS_COMMANDS:
            command = ALIAS_COMMANDS[command]
        module = importlib.import_module("xcsp.commands." + command.replace("-", "_"))
        if hasattr(module, 'manage_command'):
            module.manage_command(arguments)
    except TypeError as e:
        logger.error(f"Command '{command}' not found.")
        logger.error(e)