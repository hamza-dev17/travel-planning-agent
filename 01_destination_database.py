from __future__ import annotations

DESTINATIONS = {
    "Istanbul": {
        "weather": {"temp": 22, "condition": "Sunny", "humidity": 60},
        "attractions": ["Blue Mosque", "Topkapi Palace", "Grand Bazaar", "Bosphorus Cruise"],
        "tips": "Best in Oct-Nov, wear comfortable shoes, bargain in bazaars",
        "trip_types": ["cultural", "city-break"],
    },
    "Antalya": {
        "weather": {"temp": 28, "condition": "Sunny", "humidity": 55},
        "attractions": ["Duden Waterfalls", "Kaleici Old Town", "Konyaalti Beach", "Side Ruins"],
        "tips": "Perfect for beach lovers, bring sunscreen and light clothes",
        "trip_types": ["beach", "relax"],
    },
    "Cappadocia": {
        "weather": {"temp": 20, "condition": "Cloudy", "humidity": 45},
        "attractions": ["Hot Air Balloon Ride", "Goreme Open Air Museum", "Underground Cities"],
        "tips": "Book balloon rides early and bring a light jacket for mornings",
        "trip_types": ["adventure", "cultural"],
    },
    "Izmir": {
        "weather": {"temp": 26, "condition": "Sunny", "humidity": 58},
        "attractions": ["Kordon", "Ephesus Day Trip", "Agora Open Air Museum"],
        "tips": "Great in spring and early autumn; use public ferry lines",
        "trip_types": ["city-break", "cultural"],
    },
}

FLIGHTS = {
    ("Istanbul", "Antalya"): {"price": 450, "duration": "2h", "airline": "Turkish Airlines"},
    ("Antalya", "Istanbul"): {"price": 430, "duration": "2h", "airline": "Pegasus"},
    ("Istanbul", "Cappadocia"): {"price": 350, "duration": "1h 20m", "airline": "AnadoluJet"},
    ("Ankara", "Cappadocia"): {"price": 300, "duration": "1h", "airline": "Pegasus"},
    ("Istanbul", "Izmir"): {"price": 280, "duration": "1h 10m", "airline": "SunExpress"},
}

HOTELS = {
    "Istanbul": [
        {"name": "Golden Horn Hotel", "price": 160, "rating": 4.7, "amenities": ["WiFi", "Breakfast", "Restaurant"]},
        {"name": "City Budget Inn", "price": 90, "rating": 4.1, "amenities": ["WiFi", "Breakfast"]},
    ],
    "Antalya": [
        {"name": "Blue Coast Resort", "price": 140, "rating": 4.6, "amenities": ["WiFi", "Pool", "All Inclusive"]},
        {"name": "Mediterranean Stay", "price": 110, "rating": 4.3, "amenities": ["WiFi", "Breakfast", "Beach Access"]},
    ],
    "Cappadocia": [
        {"name": "Stone Cave Suites", "price": 130, "rating": 4.8, "amenities": ["WiFi", "Breakfast", "Terrace"]},
        {"name": "Balloon View Hotel", "price": 95, "rating": 4.2, "amenities": ["WiFi", "Breakfast"]},
    ],
    "Izmir": [
        {"name": "Kordon Prime", "price": 120, "rating": 4.5, "amenities": ["WiFi", "Breakfast", "Gym"]},
        {"name": "Agora Rooms", "price": 85, "rating": 4.0, "amenities": ["WiFi", "Breakfast"]},
    ],
}
