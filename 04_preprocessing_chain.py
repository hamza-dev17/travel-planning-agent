from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


def _extract_amount(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    raw = match.group(1).replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _extract_total_budget(text: str) -> float | None:
    # Capture the total budget while excluding daily and hotel budgets.
    pattern = (
        r"(toplam\s+butce|toplam\s+bütçe|butce\s+limitim|bütçe\s+limitim|"
        r"butce\s+limiti|bütçe\s+limiti|limitim|butcem|bütçem|butce|bütçe)"
        r"\s*(?:[:=]|\s+)?(?:₺|tl|lira|\$)?\s*(\d+(?:[.,]\d+)?)"
    )
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        start = max(0, match.start() - 12)
        context = text[start : match.start()]
        if "gunluk" in context or "günlük" in context or "otel" in context:
            continue
        raw = match.group(2).replace(".", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            continue
    return None


def _normalize_budget_fields(data: dict[str, Any], user_input: str) -> dict[str, Any]:
    lower = user_input.lower()

    explicit_total = _extract_total_budget(lower)
    explicit_hotel = _extract_amount(r"(?:otel\s+butcesi|otel\s+bütçesi|nightly|per\s+night|gecelik)\s*(?:[:=]|\s+)?(?:₺|tl|lira|\$)?\s*(\d+(?:[.,]\d+)?)", lower)
    explicit_daily = _extract_amount(r"(?:gunluk|günlük|daily)\s*(?:butce|bütçe)?\s*(?:[:=]|\s+)?(?:₺|tl|lira|\$)?\s*(\d+(?:[.,]\d+)?)", lower)

    if explicit_hotel is not None:
        data["hotel_budget_per_night"] = explicit_hotel
    elif data.get("hotel_budget_per_night") in (None, "", "N/A"):
        data["hotel_budget_per_night"] = 4000

    if explicit_daily is not None:
        data["daily_budget_per_person"] = explicit_daily
    elif data.get("daily_budget_per_person") in (None, "", "N/A"):
        data["daily_budget_per_person"] = 1500

    if explicit_total is not None:
        data["total_budget"] = explicit_total
    elif data.get("total_budget") in (None, "", "N/A"):
        data["total_budget"] = "Belirtilmedi"

    return data


def _fallback_extract(user_input: str) -> dict[str, Any]:
    lower = user_input.lower()
    city_match = re.findall(r"\b(istanbul|antalya|cappadocia|izmir|ankara)\b", lower)
    destination = city_match[-1].title() if city_match else "Istanbul"

    days_match = re.search(r"(\d+)\s*(day|days|gun|gün|gece|night|nights)", lower)
    nights = int(days_match.group(1)) if days_match else 3

    people_match = re.search(r"(\d+)\s*(people|person|kisi|kişi)", lower)
    people = int(people_match.group(1)) if people_match else 1

    data = {
        "origin_city": "Istanbul",
        "destination_city": destination,
        "nights": nights,
        "total_budget": "Belirtilmedi",
        "people": people,
        "trip_type": "general",
        "hotel_budget_per_night": 4000,
        "daily_budget_per_person": 1500,
        "travel_date": "N/A",
        "check_in": "N/A",
        "check_out": "N/A",
        "raw_request": user_input,
    }
    return _normalize_budget_fields(data, user_input)


def build_preprocessing_chain():
    prompt = ChatPromptTemplate.from_template(
        """
Extract travel-planning parameters from the user request.
Return valid JSON with ONLY these keys:
origin_city, destination_city, nights, total_budget, people, trip_type,
hotel_budget_per_night, daily_budget_per_person, travel_date, check_in, check_out, raw_request.

Rules:
- Make reasonable assumptions when values are missing.
- Keep destination_city in Title Case.
- Use numbers for budget and other numeric fields.

User request:
{user_input}
"""
    )

    model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    return prompt | model


def preprocess_user_input(user_input: str) -> dict[str, Any]:
    try:
        chain = build_preprocessing_chain()
        response = chain.invoke({"user_input": user_input})
        text = response.content.strip()
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start != -1 and json_end != -1:
            parsed = json.loads(text[json_start : json_end + 1])
            return _normalize_budget_fields(parsed, user_input)
    except Exception:
        pass

    return _fallback_extract(user_input)
