"""
__main__.py — Unified CLI entry point for PyChronicle.

Usage
-----
Run the pipeline (AST + trace + SQLite):

    python -m pychronicle run <script.py> [db_path]

Run the pipeline then display the full timeline view:

    python -m pychronicle view <script.py> [db_path]

Both sub-commands share the same positional arguments:
    script  Path to the Python script to analyse and trace.
    db      Optional path to the SQLite database (default: chronicle.db).

Examples
--------
    python -m pychronicle run examples/sample_script.py
    python -m pychronicle run examples/sample_script.py my_trace.db
    python -m pychronicle view examples/sample_script.py
    python -m pychronicle view examples/sample_script.py my_trace.db

Exit codes
----------
    0  — success (pipeline ran without errors)
    1  — usage error or missing script argument
    2  — pipeline reported failure (script error, file not found, etc.)
"""

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="pychronicle",
        description=(
            "PyChronicle - AST-powered time-travel debugger for Python.\n"
            "Traces a Python script, captures every variable change as a\n"
            "timestamped SQLite event, and replays the execution timeline."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    # --- run sub-command ---
    run_parser = subparsers.add_parser(
        "run",
        help="Run the pipeline: AST analysis -> trace -> SQLite storage.",
        description=(
            "Execute the full PyChronicle pipeline on <script.py>.\n"
            "Writes every variable-change event to <db_path>."
        ),
    )
    run_parser.add_argument("script", help="Path to the Python script to trace.")
    run_parser.add_argument(
        "db",
        nargs="?",
        default="chronicle.db",
        help="SQLite database path (default: chronicle.db).",
    )

    # --- view sub-command ---
    view_parser = subparsers.add_parser(
        "view",
        help="Run the pipeline then display the full timeline view.",
        description=(
            "Execute the full PyChronicle pipeline on <script.py>, then\n"
            "replay every event in the terminal showing the code viewer\n"
            "and variable panel at each step."
        ),
    )
    view_parser.add_argument("script", help="Path to the Python script to trace.")
    view_parser.add_argument(
        "db",
        nargs="?",
        default="chronicle.db",
        help="SQLite database path (default: chronicle.db).",
    )

    return parser


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute the 'run' sub-command.  Returns an exit code."""
    import json
    from pipeline.runner import run_pipeline

    result = run_pipeline(args.script, args.db)

    print("=" * 50)
    print("PyChronicle Pipeline Result")
    print("=" * 50)
    print(f"Success     : {result['success']}")
    print(f"Script      : {result['script_path']}")
    print(f"DB          : {result['db_path']}")
    print(f"AST vars    : {json.dumps(result['ast_variables'])}")
    print(f"Event count : {result['event_count']}")
    if result["error"]:
        print(f"Error       : {result['error']}")
    print("=" * 50)

    return 0 if result["success"] else 2


def _cmd_view(args: argparse.Namespace) -> int:
    """Execute the 'view' sub-command.  Returns an exit code."""
    from ui.app import run_viewer

    result = run_viewer(args.script, args.db)
    return 0 if result["success"] else 2


def main(argv: list | None = None) -> int:
    """
    Parse *argv* (defaults to sys.argv[1:]) and dispatch to the appropriate
    sub-command handler.

    Returns the integer exit code (0 = success, 1 = usage error, 2 = failure).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _cmd_run(args)
    if args.command == "view":
        return _cmd_view(args)

    # Unreachable if subparsers.required=True, but defensive fallback:
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
