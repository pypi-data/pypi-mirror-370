"""
Module handling the 'solver' subcommand for the XCSP launcher CLI.

This module defines and manages options for running a solver on a given instance,
controlling output behavior, passing solver-specific options, and listing available solvers.
"""
import json
import os
from pathlib import Path

from loguru import logger
from xcsp.solver.solver import Solver
from xcsp.utils.log import unknown_command
from rich.console import Console
from rich.table import Table

from xcsp.utils.archive import decompress_lzma_file


def list_solvers(args):
    table: Table = Table(title="Solver List")

    table.add_column("Name", justify="center")
    table.add_column("ID", justify="center")
    table.add_column("Version", justify="center")
    table.add_column("Command Line", justify="left", )
    table.add_column("Alias", justify="left", )

    available = Solver.available_solvers()
    if len(available) == 0:
        logger.info("No solver available.")
        if args["json_output"]:
            print(json.dumps([], ))
        return
    if not args["json_output"]:
        for k, s in available.items():
            table.add_row(s.name, s.id, s.version, s.cmd, ','.join(s.alias))
        console = Console(width=200)
        console.print(table)
    else:
        print(
            json.dumps([{"id": k, "version": available[k].version, "cmd": available[k].cmd} for k in available.keys()]))


def solve(args):

    path_instance = Path(args.get("instance"))
    decompress, path_result = decompress_or_return_path(args, path_instance)
    try:
        s = Solver.create_from_cli(args)
        s.solve(path_result, args.get('keep_solver_output'), args['check'], args["delay"])
    except Exception as e:
        logger.error(f"An error occurred while solving the instance: {e}")
        logger.exception(e)
    finally:
        # Clean up temporary files if decompression was performed
        if decompress:
            path_result.unlink(missing_ok=True)


def decompress_or_return_path(args, path_instance):
    decompress = False
    path_result = path_instance
    if path_instance.suffix == ".lzma":
        path_result = Path(args.get("tmp_dir")) / path_instance.stem
        decompress_lzma_file(path_instance, path_result)
        decompress = True
    return decompress, path_result


def solver_cmd(args):
    """Execute the 'solver' subcommand."""
    if args["solvers"]:
        list_solvers(args)
        return
    if args.get("all_solutions") and args.get("num_solutions") != -1:
        raise ValueError(
            "Incompatible options: you cannot specify both --all-solutions and --num-solutions simultaneously.\n"
            "Use --all-solutions to find all possible solutions without limit, "
            "or --num-solutions to restrict the number of solutions."
        )
    solve(args)


def fill_parser(parser):
    """Register the 'solver' subcommand and its arguments to the parser.

    Args:
        parser: An argparse subparser object to which the 'solver' command is added.
    """
    parser_solver = parser.add_parser(
        "solver",
        aliases=["s"],
        help="Run a solver on an instance or list available solvers."
    )

    # --- Solver selection ---
    parser_solver.add_argument(
        "--name",
        type=str,
        required=False,
        help="Human-readable name of the solver."
    )
    parser_solver.add_argument(
        "-sv","--solver-version",
        type=str,
        required=False,
        default="latest",
        help="Version of the solver to run (default: latest)."
    )

    # --- Instance execution ---
    parser_solver.add_argument(
        "--instance",
        type=str,
        required=False,
        help="Path to the instance file to solve."
    )

    # --- Resolution behavior options ---
    parser_solver.add_argument(
        "-a", "--all-solutions",
        action="store_true",
        help="Report all solutions (for satisfaction problems) or intermediate improving solutions (for optimization problems)."
    )
    parser_solver.add_argument(
        "-n", "--num-solutions",
        type=int,
        help="Stop after reporting a given number of solutions.",
        default=-1
    )
    parser_solver.add_argument(
        "-i", "--intermediate",
        action="store_true",
        help="Print intermediate solutions during search."
    )
    parser_solver.add_argument(
        "-p", "--parallel",
        type=int,
        help="Run the solver using the specified number of parallel threads.",
        default=1
    )
    parser_solver.add_argument(
        "-r", "--random-seed",
        type=int,
        help="Random seed for stochastic parts of the solver.",
        default=123456789
    )
    parser_solver.add_argument(
        "--timeout",
        type=int,
        help="Maximum solving time in seconds (timeout).",
        default=1800
    )

    parser_solver.add_argument(
        "-d","--delay",
        type=int,
        help="At timeout minus delay, the solver receive a SIGTERM signal. After delay seconds, it receives a SIGKILL signal.",
        default=5
    )

    # --- Output behavior ---
    parser_solver.add_argument(
        "-k","--keep-solver-output",
        default=False,
        action="store_true",
        help="If set, keeps and displays the solver's stdout/stderr in the CLI output, "
             "prefixing lines with the value from --prefix. Otherwise, suppresses solver output."
    )

    parser_solver.add_argument(
        "-j","--json-output",
        default=False,
        action="store_true",
        help="If set, we collect the output of the solvers and we produce a json."
    )
    parser_solver.add_argument(
        "-out","--stdout",
        type=str,
        default="stdout",
        help="Target for solver standard output (default: stdout). Use a file path or 'stdout'."
    )
    parser_solver.add_argument(
        "-err","--stderr",
        type=str,
        default="stderr",
        help="Target for solver standard error (default: stderr). Use a file path or 'stderr'."
    )
    parser_solver.add_argument(
        "-pre","--prefix",
        type=str,
        default="c",
        help="Prefix to add before each line of solver output when --keep-solver-output is set."
    )

    parser_solver.add_argument(
        "-tmp","--tmp-dir",
        type=str,
        default=os.getcwd(),
        help=(
            "Temporary working directory used to store intermediate files "
            "(e.g., compiled instances, solver outputs). "
            "Defaults to the current working directory."
        ),
    )

    parser_solver.add_argument(
        "-ck","--check",
        default=False,
        action="store_true",
        help=(
            "Check the last solution using XCSP solution checker."
        ),
    )

    # --- Listing solvers ---
    parser_solver.add_argument(
        "--solvers",
        action="store_true",
        help="If set, list all installed solvers instead of running one."
    )

    # --- Solver additional options ---
    parser_solver.add_argument(
        'solver_options',
        nargs='*',
        help="Additional options to pass directly to the solver (after '--')."
    )


MAP_COMMAND = {
    "solver": solver_cmd,
}


def manage_command(args):
    """Dispatch and manage subcommands for the XCSP launcher binary.

    Args:
        args (dict): Parsed command-line arguments.
    """
    subcommand = args['subcommand']
    MAP_COMMAND.get(subcommand, unknown_command)(args)
