"""
Tools for the Travel Agent to search for flights, hotels, and weather.
"""


def get_5_day_weather(city: str) -> dict:
    """Get a 5-day weather forecast."""
    return {
        "city": city,
        "forecast": ["Sunny", "Cloudy", "Rain", "Sunny", "Windy"],
    }


def search_flights(to_city: str) -> dict:
    """Search for flights."""
    return {"to": to_city, "price": "$450", "status": "Available"}


def search_hotels(city: str) -> dict:
    """Find hotels."""
    return {"city": city, "hotel": "Grand ADK Hotel", "price": "$180"}
