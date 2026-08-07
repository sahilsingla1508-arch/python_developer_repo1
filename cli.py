import typer
from pipeline import run_pipeline

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


if __name__ == "__main__":
    app()