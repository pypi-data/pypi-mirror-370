import typer  # type: ignore
from rich.console import Console  # type: ignore

app = typer.Typer()
console = Console()


@app.command()  # type: ignore
def main() -> None:
    """Console script for nicolas_cache."""
    console.print(
        "Replace this message by putting your code into nicolas_cache.cli.main"
    )
    console.print("See Typer documentation at https://typer.tiangolo.com/")


if __name__ == "__main__":
    app()
