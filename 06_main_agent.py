from __future__ import annotations

import importlib.util
import re
import threading
import time
from pathlib import Path
from typing import Any


_BASE_DIR = Path(__file__).resolve().parent


def _load_module(filename: str, module_name: str):
    path = _BASE_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


pre = _load_module("04_preprocessing_chain.py", "preprocessing_chain")
agent = _load_module("03_travel_agent.py", "travel_agent")
post = _load_module("05_postprocessing_chain.py", "postprocessing_chain")
MODEL_NAME = "llama-3.3-70b-versatile (ChatGroq)"

SAMPLE_QUESTIONS = [
    "I want a 5-day vacation in Antalya in July. We are 2 people and the total budget is 75000 TL. Include weather, hotels, and places to visit.",
    "I want a cultural trip in Istanbul. 3 days, 1 person, budget 30000 TL. Create a day-by-day plan.",
    "Create an adventure-focused 4-day plan for Cappadocia. Budget 50000 TL for 2 people.",
    "I am planning a weekend getaway to Izmir. 2 nights, 1 person, hotel budget 4000 TL per night.",
    "Create an economical plan from Istanbul to Antalya including flights and hotel. 3 nights, 2 people, total budget 45000 TL.",
    "I am thinking about a trip from Ankara to Cappadocia. 2 days, 2 people, with a focus on cultural places.",
    "Recommend the best option for a beach holiday. It can be Antalya or Izmir, 4 nights, 2 people, budget 60000 TL.",
    "Create a luxury plan for Istanbul. 2 nights, 2 people, hotel budget 8000 TL per night.",
]


def _is_travel_related(text: str) -> bool:
    lower = text.lower()
    travel_keywords = [
        "travel",
        "trip",
        "vacation",
        "tour",
        "flight",
        "hotel",
        "itinerary",
        "budget",
        "destination",
        "weather",
        "vacation",
        "seyahat",
        "tatil",
        "gezi",
        "ucus",
        "otel",
        "rota",
        "destinasyon",
        "hava durumu",
        "butce",
        "bilet",
        "rezervasyon",
        "antalya",
        "istanbul",
        "izmir",
        "ankara",
        "cappadocia",
        "kapadokya",
    ]
    if any(keyword in lower for keyword in travel_keywords):
        return True
    return bool(re.search(r"\b(\d+)\s*(gun|gün|gece)\b", lower))


def _is_follow_up_update(text: str) -> bool:
    lower = text.lower()
    follow_up_keywords = [
        "update",
        "change",
        "modify",
        "adjust",
        "guncelle",
        "güncelle",
        "degistir",
        "değiştir",
        "this",
        "that",
        "this plan",
        "also",
        "additionally",
        "butceyi",
        "bütçeyi",
        "otel butcesi",
        "gunluk butce",
        "günlük bütçe",
        "kisi sayisi",
        "gece sayisi",
    ]
    return any(k in lower for k in follow_up_keywords)


def _build_contextual_request(previous: dict[str, Any], update_text: str) -> str:
    return (
        f"Previous travel request: {previous.get('raw_request', '')}\n"
        f"Update: {update_text}\n"
        "This is a follow-up message. Keep the previous plan and apply only the new information."
    )


def _print_header() -> None:
    print("\n" + "=" * 72)
    print("                 TRAVEL PLANNING AGENT - DEMO CHAT")
    print("=" * 72)
    print("Commands: 'help', 'samples', 'example 1', '1..8', 'reset', 'exit'")


def _print_samples() -> None:
    print("\nSample questions:")
    for i, question in enumerate(SAMPLE_QUESTIONS, start=1):
        print(f"{i}. {question}")


def _stream_print(text: str, delay: float = 0.008) -> None:
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def _show_thinking(stop_event: threading.Event) -> None:
    frames = ["|", "/", "-", "\\"]
    idx = 0
    while not stop_event.is_set():
        frame = frames[idx % len(frames)]
        print(f"\rAgent thinking {frame}", end="", flush=True)
        idx += 1
        time.sleep(0.12)
    print("\r" + " " * 30 + "\r", end="", flush=True)


def _extract_tools_from_agent_output(raw_agent_output: str) -> str:
    match = re.search(r"Kullanilan Araclar:\s*(.+)", raw_agent_output)
    if match:
        return match.group(1).strip()
    return "Belirlenemedi"


def _build_ai_footer(clean_data: dict[str, Any], raw_agent_output: str) -> str:
    tools_used = _extract_tools_from_agent_output(raw_agent_output)
    destination = clean_data.get("destination_city", "Not specified")
    nights = clean_data.get("nights", "N/A")
    people = clean_data.get("people", "N/A")
    total_budget = clean_data.get("total_budget", "Not specified")
    budget_text = f"{total_budget} TL" if isinstance(total_budget, (int, float)) else str(total_budget)

    return (
        "\n\nAI Summary:\n"
        f"This response was created for {destination} with {nights} nights and {people} travelers. "
        f"Budget: {budget_text}.\n"
        f"Model: {MODEL_NAME}\n"
        f"Used Tools: {tools_used}"
    )


def run_travel_planner(user_input: str, previous_context: dict[str, Any] | None = None) -> tuple[str, dict[str, Any]]:
    if previous_context and _is_follow_up_update(user_input):
        contextual_input = _build_contextual_request(previous_context, user_input)
        clean_data = pre.preprocess_user_input(contextual_input)
    else:
        clean_data = pre.preprocess_user_input(user_input)

    raw_agent_output = agent.run_agent(clean_data)
    final_output = post.format_final_response(raw_agent_output, clean_data)
    final_output = final_output + _build_ai_footer(clean_data, raw_agent_output)
    return final_output, clean_data


if __name__ == "__main__":
    _print_header()
    _print_samples()
    session_context: dict[str, Any] | None = None

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            print("Please enter a travel request.")
            continue
        lower = user_input.lower()

        if lower in {"exit", "quit", "cikis"}:
            print("See you next time.")
            break

        if lower in {"reset", "sifirla"}:
            session_context = None
            print("Conversation memory cleared. You can start a new plan now.")
            continue

        if lower in {"help", "yardim"}:
            print("Write a travel request. Example: 'Create a 3-night plan for Antalya with a budget of 30000 TL'.")
            continue

        if lower in {"samples", "ornekler"}:
            _print_samples()
            continue

        if lower.startswith("example "):
            try:
                idx = int(lower.split()[1]) - 1
                user_input = SAMPLE_QUESTIONS[idx]
                print(f"Selected sample: {user_input}")
            except (ValueError, IndexError):
                print("Enter a valid sample number, for example: 'example 2' or 'ornek 2'")
                continue
        elif lower.startswith("ornek "):
            try:
                idx = int(lower.split()[1]) - 1
                user_input = SAMPLE_QUESTIONS[idx]
                print(f"Selected sample: {user_input}")
            except (ValueError, IndexError):
                print("Enter a valid sample number, for example: 'example 2' or 'ornek 2'")
                continue
        elif lower.isdigit():
            try:
                idx = int(lower) - 1
                user_input = SAMPLE_QUESTIONS[idx]
                print(f"Selected sample: {user_input}")
            except (ValueError, IndexError):
                print(f"Valid range: 1 - {len(SAMPLE_QUESTIONS)}")
                continue

        if not _is_travel_related(user_input) and not (session_context and _is_follow_up_update(user_input)):
            print(
                "This assistant is designed only for travel planning. "
                "Please enter a question that includes a flight, hotel, trip length, budget, or destination."
            )
            continue

        print("\n" + "-" * 72)
        print("Agent:")
        print("-" * 72)

        stop_event = threading.Event()
        spinner = threading.Thread(target=_show_thinking, args=(stop_event,), daemon=True)
        spinner.start()
        try:
            response_text, session_context = run_travel_planner(user_input, session_context)
        finally:
            stop_event.set()
            spinner.join()

        _stream_print(response_text)
        print("-" * 72)
