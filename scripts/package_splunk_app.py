import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tarfile

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Package the AgentLens Splunk app into a .spl file")
console = Console()

_ROOT = Path(__file__).resolve().parent.parent
_APP_DIR = _ROOT / "splunk_app" / "agentlens_app"
_OUTPUT = _ROOT / "agentlens_app.spl"

_REQUIRED_FILES = [
    _APP_DIR / "default" / "app.conf",
    _APP_DIR / "default" / "savedsearches.conf",
    _APP_DIR / "default" / "props.conf",
    _APP_DIR / "default" / "transforms.conf",
    _APP_DIR / "default" / "data" / "ui" / "views" / "agentlens_dashboard.xml",
    _APP_DIR / "default" / "data" / "ui" / "nav" / "default.xml",
    _APP_DIR / "metadata" / "default.meta",
]


@app.command()
def package() -> None:
    table = Table(title="AgentLens App Packaging", show_header=True)
    table.add_column("File", style="cyan")
    table.add_column("Status", style="white")

    missing = []
    for f in _REQUIRED_FILES:
        rel = f.relative_to(_ROOT)
        if f.exists():
            table.add_row(str(rel), "[green]OK[/green]")
        else:
            table.add_row(str(rel), "[red]MISSING[/red]")
            missing.append(f)

    console.print(table)

    if missing:
        console.print(f"[red]Cannot package: {len(missing)} required file(s) missing.[/red]")
        raise typer.Exit(code=1)

    with tarfile.open(_OUTPUT, "w:gz") as tar:
        tar.add(_APP_DIR, arcname="agentlens_app")

    size_kb = _OUTPUT.stat().st_size // 1024
    console.print(f"[green]Packaged successfully:[/green] {_OUTPUT}  ({size_kb} KB)")


@app.command()
def info() -> None:
    console.print(f"App source: {_APP_DIR}")
    console.print(f"Output:     {_OUTPUT}")


if __name__ == "__main__":
    app()
