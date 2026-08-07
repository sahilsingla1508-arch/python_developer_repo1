import typer
from pipeline import run_pipeline
from storage import get_connection, get_events

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


if __name__ == "__main__":
    app()