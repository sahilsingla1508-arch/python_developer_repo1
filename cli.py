import os
import typer
from pipeline import run_pipeline
from storage import get_connection, get_events, get_variable_history, get_trace_statistics
from exporter import export_json

app = typer.Typer(
    help="PyChronicle - AST Powered Time Travel Debugger"
)

run_app = typer.Typer()
app.add_typer(run_app, name="run")


@run_app.callback(invoke_without_command=True)
def run(script: str):
    """
    Run a Python script with tracing enabled.
    """

    if not os.path.exists(script):
        typer.echo(f"Error: script '{script}' not found.")
        raise typer.Exit(code=1)

    typer.echo(f"Tracing {script}...")

    try:
        variables = run_pipeline(script)
    except Exception as e:
        typer.echo(f"Error while tracing script: {e}")
        raise typer.Exit(code=1)

    typer.echo("Tracing completed.")
    typer.echo(f"Static Variables: {variables}")


@app.command()
def replay(db: str = "chronicle.db"):
    """
    Replay all recorded trace events.
    """

    if not os.path.exists(db):
        typer.echo(f"Error: database '{db}' not found. Run a trace first.")
        raise typer.Exit(code=1)

    typer.echo(f"Reading trace from {db}...\n")

    with get_connection(db) as conn:
        events = get_events(conn)

    if not events:
        typer.echo("No trace events found.")
        return

    for event in events:
        _, timestamp, step, line, variable, value = event

        typer.echo(
            f"Step {step} | Line {line} | {variable} = {value}"
        )


@app.command()
def watch(variable: str, db: str = "chronicle.db"):
    """
    Show the history of a single variable.
    """

    if not os.path.exists(db):
        typer.echo(f"Error: database '{db}' not found. Run a trace first.")
        raise typer.Exit(code=1)

    with get_connection(db) as conn:
        history = get_variable_history(conn, variable)

    if not history:
        typer.echo(f"No history found for '{variable}'.")
        raise typer.Exit()

    typer.echo(f"\nHistory for variable: {variable}\n")

    for event in history:
        _, timestamp, step, line, variable_name, value = event

        typer.echo(
            f"Step {step} | Line {line} | {variable_name} = {value}"
        )


@app.command()
def stats(db: str = "chronicle.db"):
    """
    Display trace statistics.
    """

    if not os.path.exists(db):
        typer.echo(f"Error: database '{db}' not found. Run a trace first.")
        raise typer.Exit(code=1)

    with get_connection(db) as conn:
        stats = get_trace_statistics(conn)

    typer.echo("\nTrace Statistics\n")

    typer.echo(f"Total Events : {stats['events']}")
    typer.echo(f"Variables    : {stats['variables']}")
    typer.echo(f"Steps        : {stats['steps']}")


@app.command()
def export(
    output: str = "trace.json",
    db: str = "chronicle.db",
):
    """
    Export trace to JSON.
    """

    if not os.path.exists(db):
        typer.echo(f"Error: database '{db}' not found. Run a trace first.")
        raise typer.Exit(code=1)

    try:
        export_json(db, output)
    except Exception as e:
        typer.echo(f"Error while exporting: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"Trace exported to {output}")


if __name__ == "__main__":
    app()