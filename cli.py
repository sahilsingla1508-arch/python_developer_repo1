import typer
from pipeline import run_pipeline
from storage import get_connection, get_events, get_variable_history, get_trace_statistics

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

    typer.echo(f"Tracing {script}...")

    variables = run_pipeline(script)

    typer.echo("Tracing completed.")
    typer.echo(f"Static Variables: {variables}")


@app.command()
def replay(db: str = "chronicle.db"):
    """
    Replay all recorded trace events.
    """

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

    with get_connection(db) as conn:
        stats = get_trace_statistics(conn)

    typer.echo("\nTrace Statistics\n")

    typer.echo(f"Total Events : {stats['events']}")
    typer.echo(f"Variables    : {stats['variables']}")
    typer.echo(f"Steps        : {stats['steps']}")


if __name__ == "__main__":
    app()