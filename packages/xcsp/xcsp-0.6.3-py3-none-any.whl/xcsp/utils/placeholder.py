import shlex
import shutil
import re

PLACEHOLDERS = {
    "{{java}}": shutil.which("java"),
    "{{python}}": shutil.which("python"),
    "{{cmake}}": shutil.which("cmake"),
    "{{bash}}": shutil.which("bash"),
}



def normalize_placeholders(text: str) -> str:
    """
    Convert all placeholders of the form {{ KEY }} to {{ key }} (lowercased key),
    preserving spacing inside the double braces.

    Args:
        text (str): Input string with placeholders.

    Returns:
        str: Modified string with placeholders lowercased.
    """
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
    return pattern.sub(lambda m: "{{"+ m.group(1).lower() +"}}", text)


def replace_placeholder(cmd):
    """ Replace placeholders in a command string with their corresponding values.
    Args:
        cmd (str): The command string containing placeholders.
    Returns:
        list: A list of command arguments with placeholders replaced.
    """
    cmd = normalize_placeholders(cmd)
    for k, v in PLACEHOLDERS.items():
        cmd = cmd.replace(k, str(v))
    return shlex.split(cmd)


def replace_solver_dir_in_list(cmd, dir):
    """ Replace the placeholder {{solver_dir}} in each command string in the list with the specified directory.
    Args:
        cmd (list): A list of command strings containing the placeholder.
        dir (str): The directory to replace the placeholder with.
    Returns:
        list: A list of command strings with the placeholder replaced by the directory.
    """
    for index, c in enumerate(cmd):
        cmd[index] = replace_solver_dir_in_str(c, dir)
    return cmd


def replace_solver_dir_in_str(cmd, dir):
    """ Replace the placeholder {{solver_dir}} in the command with the specified directory."""
    return replace_dir(cmd, dir, "solver_dir")

def replace_bin_dir_in_str (cmd, dir):
    """ Replace the placeholder {{bin_dir}} in the command with the specified directory."""
    return replace_dir(cmd, dir, "bin_dir")

def replace_dir(cmd, dir, key):
    """
    Replace the placeholder {{key}} in the command with the specified directory.

    Args:
        cmd (str): The command string containing the placeholder.
        dir (str): The directory to replace the placeholder with.
        key (str): The placeholder key to replace (e.g., "solver_dir", "bin_dir").

    Returns:
        str: The command string with the placeholder replaced by the directory.
    """
    return normalize_placeholders(cmd).replace("{{"+key+"}}", dir)

def replace_core_placeholder(cmd, executable, bin_dir, options):
    cmds = cmd.split()
    result = []
    for item in cmds:
        r = normalize_placeholders(item)
        if "{{executable}}" in r:
            r = r.replace("{{executable}}", str(executable))
            result.append(r)
            continue
        if "{{bin_dir}}" in r:
            r = r.replace("{{bin_dir}}", str(bin_dir))
            result.append(r)
            continue
        if "{{options}}" in r:
            for opt in shlex.split(options):
                result.append(opt.strip())
            continue
        result.append(r)
    return result
