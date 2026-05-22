import os

from crewai import Agent, LLM
from dotenv import load_dotenv

from demo.wanderbot.tools import book_flight, search_flights, send_confirmation_email

load_dotenv()

_llm = LLM(
    provider="openai",
    model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY", ""),
)

researcher_agent = Agent(
    role="Travel Researcher",
    goal="Find available flights that match the user's origin, destination, and travel date",
    backstory=(
        "You are an expert travel researcher with access to a live flight database. "
        "You find the best flight options and present them clearly."
    ),
    tools=[search_flights],
    llm=_llm,
    cache=False,
    verbose=True,
)

booking_agent = Agent(
    role="Booking Specialist",
    goal="Book the selected flight for the passenger and return a confirmed booking reference",
    backstory=(
        "You are a meticulous booking specialist who secures flight reservations accurately. "
        "You always confirm booking details before finalizing."
    ),
    tools=[book_flight],
    llm=_llm,
    cache=False,
    verbose=True,
)

notifier_agent = Agent(
    role="Customer Communications",
    goal="Send a booking confirmation email to the passenger with all trip details",
    backstory=(
        "You are a customer communications expert who ensures passengers receive "
        "clear and complete confirmation of their bookings."
    ),
    tools=[send_confirmation_email],
    llm=_llm,
    cache=False,
    verbose=True,
)
