import sys
from pathlib import Path

import typer
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentlens.config import get_config
from agentlens.exporter import SplunkHECSpanExporter

app = typer.Typer()
console = Console()


class _CapturingExporter(SplunkHECSpanExporter):
    def __init__(self) -> None:
        super().__init__()
        self.result: SpanExportResult = SpanExportResult.FAILURE

    def export(self, spans):
        self.result = super().export(spans)
        return self.result


@app.command()
def verify() -> None:
    config = get_config()

    exporter = _CapturingExporter()
    provider = TracerProvider(
        resource=Resource.create({"service.name": "agentlens-verify"})
    )
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("agentlens.verify")

    with tracer.start_as_current_span("verify.hec_connectivity") as span:
        span.set_attribute("verify.source", "verify_hec.py")
        span.set_attribute("verify.purpose", "phase1_smoke_test")

    success = exporter.result == SpanExportResult.SUCCESS

    token_set = bool(config.splunk_hec_token)
    token_display = config.splunk_hec_token[:8] + "..." if token_set else "NOT SET"

    search_url = (
        "http://localhost:8000/en-US/app/search/search"
        "?q=index%3Dagentlens+source%3Dagentlens&earliest=-5m&latest=now"
    )

    table = Table(
        title="AgentLens HEC Verification",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Detail")
    table.add_column("Status", justify="center", no_wrap=True)

    ok = "[green]PASS[/green]"
    fail = "[red]FAIL[/red]"

    table.add_row("Config loaded", config.splunk_hec_url, ok)
    table.add_row("HEC token", token_display, ok if token_set else fail)
    table.add_row("Index", config.splunk_index, ok)
    table.add_row("Sourcetype", config.splunk_sourcetype, ok)
    table.add_row("Span created", "verify.hec_connectivity", ok)
    table.add_row("HEC export", "SUCCESS" if success else "FAILURE", ok if success else fail)

    console.print()
    console.print(table)
    console.print()

    if success:
        console.print("[green]Verification passed. Event sent to Splunk.[/green]")
        console.print(f"Search now: {search_url}")
    else:
        console.print("[red]Verification failed. Check .env and HEC settings.[/red]")
        console.print("  1. Confirm Splunk is running at http://localhost:8000")
        console.print("  2. Verify SPLUNK_HEC_TOKEN in .env matches Settings > Data Inputs > HTTP Event Collector")
        console.print("  3. Set DEBUG=true in .env to see raw export attempts")

    raise typer.Exit(code=0 if success else 1)


if __name__ == "__main__":
    app()
