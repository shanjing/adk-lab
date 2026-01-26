"""
Tools for the Travel Agent to search for flights, hotels, and weather.
"""
from pydantic import BaseModel, Field

# Schemas
class WeatherInput(BaseModel):
    city: str = Field(..., description="The city to get the weather for.")

class FlightSearchInput(BaseModel):
    to_city: str = Field(..., description="The city to fly to.")   

class HotelSearchInput(BaseModel):
    city: str = Field(..., description="The city to find a hotel in.")


# Tools
def get_5_day_weather(args: WeatherInput) -> dict:
    """Get a 5-day weather forecast."""
    return {
        "city": args.city,
        "forecast": ["Sunny", "Cloudy", "Rain", "Sunny", "Windy"],
    }

def search_flights(args: FlightSearchInput) -> dict:
    """Search for flights."""
    return {"to": args.to_city, "price": "$450", "status": "Available"}


def search_hotels(args: HotelSearchInput) -> dict:
    """Find hotels."""
    return {"city": args.city, "hotel": "Grand ADK Hotel", "price": "$180"}
