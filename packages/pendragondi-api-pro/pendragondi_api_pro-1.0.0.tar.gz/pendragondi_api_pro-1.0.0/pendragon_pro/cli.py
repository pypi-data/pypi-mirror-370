import typer
from pathlib import Path
from .core import get_event_log
from .export import export_json, export_csv, export_html

app = typer.Typer(help="Pendragon Pro – Export duplicate detection event logs")

@app.command()
def export(
    output: str = typer.Option("report.html", "-o", "--output", help="Output file path"),
    format: str = typer.Option("html", "-f", "--format", help="Report format: html, json, csv"),
):
    """Export duplicate events to a report."""
    events = get_event_log().snapshot()

    if format.lower() == "json":
        export_json(events, output)
    elif format.lower() == "csv":
        export_csv(events, output)
    else:
        export_html(events, output)

    typer.echo(f"Report saved to {Path(output).resolve()}")

if __name__ == "__main__":
    app()
