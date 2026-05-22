from crewai import Task

from demo.wanderbot.agents import booking_agent, notifier_agent, researcher_agent

research_task = Task(
    description=(
        "Search for available flights from {origin} to {destination} on {date}. "
        "Return all available options with their flight IDs, airlines, departure times, "
        "arrival times, prices, and seat availability."
    ),
    expected_output=(
        "A JSON list of available flights each containing: id, airline, departure_time, "
        "arrival_time, price_usd, and seats_available."
    ),
    agent=researcher_agent,
)

booking_task = Task(
    description=(
        "Using the flight options provided by the researcher, book the best available flight "
        "for passenger {name}. Select the flight offering the best balance of price and "
        "convenience. Use the exact flight ID from the search results."
    ),
    expected_output=(
        "A booking confirmation containing: booking_id, flight_id, passenger_name, "
        "tickets booked, and status."
    ),
    agent=booking_agent,
    context=[research_task],
)

notification_task = Task(
    description=(
        "Send a booking confirmation email to {email} with the full details from the "
        "completed booking. Include the flight information and booking reference number."
    ),
    expected_output=(
        "Confirmation that the email was sent successfully, including the recipient address "
        "and a summary of the booking details included in the message body."
    ),
    agent=notifier_agent,
    context=[booking_task],
)
