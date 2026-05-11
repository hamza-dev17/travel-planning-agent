from __future__ import annotations

from pathlib import Path
import importlib.util
from typing import Any

from langchain_core.tools import tool


_BASE_DIR = Path(__file__).resolve().parent
_DB_PATH = _BASE_DIR / "01_destination_database.py"
_spec = importlib.util.spec_from_file_location("destination_database", _DB_PATH)
_db = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_db)

DESTINATIONS = _db.DESTINATIONS
FLIGHTS = _db.FLIGHTS
HOTELS = _db.HOTELS


@tool
def get_weather_forecast(city: str, date: str = "N/A") -> str:
    """Return sample weather information for a city and date."""
    info = DESTINATIONS.get(city)
    if not info:
        return f"No weather data found for {city}."
    weather = info["weather"]
    return f"{city} ({date}): {weather['temp']}C, {weather['condition']}, Humidity: {weather['humidity']}%"


@tool
def check_flight_prices(from_city: str, to_city: str) -> str:
    """Return sample flight information between two cities."""
    flight = FLIGHTS.get((from_city, to_city))
    if not flight:
        return f"No flight found for the route {from_city} -> {to_city}."
    return f"{from_city} -> {to_city}: {flight['price']} TL ({flight['duration']}, {flight['airline']})"


@tool
def search_hotels(city: str, budget_per_night: float, check_in: str = "N/A", check_out: str = "N/A") -> str:
    """Filter hotels by nightly budget."""
    city_hotels = HOTELS.get(city, [])
    filtered = [h for h in city_hotels if h["price"] <= budget_per_night]
    if not filtered:
        return f"No hotel found in {city} for {check_in} - {check_out} under {budget_per_night} TL per night."

    lines = [f"{city} hotels ({check_in} - {check_out}):"]
    for hotel in filtered:
        amenities = ", ".join(hotel["amenities"])
        lines.append(f"- {hotel['name']}: {hotel['price']} TL/night, {hotel['rating']} stars, Amenities: {amenities}")
    return "\n".join(lines)


@tool
def get_attractions_and_activities(city: str) -> str:
    """Return popular attractions for a city."""
    info = DESTINATIONS.get(city)
    if not info:
        return f"No attractions found for {city}."
    attractions = ", ".join(info["attractions"])
    return f"Recommended places in {city}: {attractions}"


@tool
def calculate_trip_cost(
    flight_price_per_person: float,
    hotel_price_per_night: float,
    nights: int,
    daily_budget_per_person: float,
    people: int = 1,
) -> str:
    """Calculate the total trip cost by category."""
    flight_total = flight_price_per_person * people
    hotel_total = hotel_price_per_night * nights
    food_activities_total = daily_budget_per_person * nights * people
    total = flight_total + hotel_total + food_activities_total

    return (
        f"Flight: {flight_total:.0f} TL\n"
        f"Hotel ({nights} nights x {hotel_price_per_night:.0f} TL): {hotel_total:.0f} TL\n"
        f"Food and activities ({nights} days x {daily_budget_per_person:.0f} TL x {people} travelers): {food_activities_total:.0f} TL\n"
        f"Total: {total:.0f} TL"
    )


@tool
def get_travel_tips_recommendations(destination_city: str, trip_type: str = "general") -> str:
    """Return practical travel tips for a destination."""
    info = DESTINATIONS.get(destination_city)
    if not info:
        return f"No travel tips found for {destination_city}."

    best_time = "April-June and September-November"
    tips = info["tips"]
    supported_types = ", ".join(info["trip_types"])

    return (
        f"{destination_city} ({trip_type} trip)\n"
        f"Best time: {best_time}\n"
        f"Tips: {tips}\n"
        f"Suitable trip types: {supported_types}"
    )


def all_travel_tools() -> list[Any]:
    return [
        get_weather_forecast,
        check_flight_prices,
        search_hotels,
        get_attractions_and_activities,
        calculate_trip_cost,
        get_travel_tips_recommendations,
    ]
