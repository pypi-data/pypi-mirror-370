from typing import List


def at_least_one(args, keys:List[str]) -> bool:
    """
    Check if at least one of the specified keys is present in the args dictionary.

    :param args: Dictionary of arguments.
    :param keys: List of keys to check in the args dictionary.
    :return: True if at least one key is present, False otherwise.
    """
    return any(key in args and args.get(key) is not None for key in keys)

def at_most_one(args, keys:List[str]) -> bool:
    """
    Check if at most one of the specified keys is present in the args dictionary.

    :param args: Dictionary of arguments.
    :param keys: List of keys to check in the args dictionary.
    :return: True if at most one key is present, False otherwise.
    """
    count = sum(1 for key in keys if key in args and args.get(key) is not None)
    return count <= 1