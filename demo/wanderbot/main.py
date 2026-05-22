import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import agentlens
import typer
from crewai import Crew, Process
from rich.console import Console
from rich.panel import Panel

from demo.wanderbot.agents import booking_agent, notifier_agent, researcher_agent
from demo.wanderbot.tasks import booking_task, notification_task, research_task

agentlens.instrument(service_name="wanderbot")

app = typer.Typer(help="WanderBot — AI travel booking assistant")
console = Console()


@app.command()
def book(
    origin: str = typer.Option(..., help="Departure airport code (e.g. HYD)"),
    destination: str = typer.Option(..., help="Destination airport code (e.g. NRT)"),
    date: str = typer.Option(..., help="Travel date in YYYY-MM-DD format"),
    name: str = typer.Option(..., help="Passenger full name"),
    email: str = typer.Option(..., help="Passenger email address"),
) -> None:
    console.print(Panel(
        f"Booking flight from [bold]{origin}[/bold] to [bold]{destination}[/bold] on [bold]{date}[/bold]\n"
        f"Passenger: {name} | Email: {email}",
        title="WanderBot Travel Booking",
        border_style="blue",
    ))

    crew = Crew(
        agents=[researcher_agent, booking_agent, notifier_agent],
        tasks=[research_task, booking_task, notification_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={
        "origin": origin,
        "destination": destination,
        "date": date,
        "name": name,
        "email": email,
    })

    console.print(Panel(
        str(result),
        title="Booking Complete",
        border_style="green",
    ))


@app.command()
def info() -> None:
    """Show current WanderBot configuration."""
    console.print(f"LLM: {os.environ.get('WANDERBOT_LLM', 'groq/llama-3.3-70b-versatile')}")
    console.print(f"HEC: {os.environ.get('SPLUNK_HEC_URL', 'not set')}")
    console.print(f"Index: {os.environ.get('SPLUNK_INDEX', 'agentlens')}")


if __name__ == "__main__":
    app()
