from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq


_BASE_DIR = Path(__file__).resolve().parent
_TOOLS_PATH = _BASE_DIR / "02_travel_tools.py"
_spec = importlib.util.spec_from_file_location("travel_tools", _TOOLS_PATH)
_tools_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_tools_module)


def build_travel_agent():
    load_dotenv()
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    tools = _tools_module.all_travel_tools()
    system_prompt = (
        "You are a travel planning assistant. "
        "Use tools for weather, flights, hotels, attractions, cost, and travel tips. "
        "If a route or hotel cannot be found, suggest alternatives."
    )
    return create_agent(model=llm, tools=tools, system_prompt=system_prompt)


def _extract_tool_trace(messages: list[Any]) -> tuple[list[str], list[str]]:
    used_tools: list[str] = []
    tool_outputs: list[str] = []

    for msg in messages:
        tool_calls = getattr(msg, "tool_calls", None) or []
        for call in tool_calls:
            name = call.get("name")
            if name and name not in used_tools:
                used_tools.append(name)

        if getattr(msg, "type", "") == "tool":
            name = getattr(msg, "name", "arac")
            content = getattr(msg, "content", "")
            preview = str(content).strip().replace("\n", " | ")
            if len(preview) > 180:
                preview = preview[:180] + "..."
            tool_outputs.append(f"- {name}: {preview}")

    return used_tools, tool_outputs


def run_agent(preprocessed_data: dict[str, Any]) -> str:
    agent_executor = build_travel_agent()
    total_budget = preprocessed_data.get("total_budget")
    total_budget_text = f"{total_budget} TL" if isinstance(total_budget, (int, float)) else str(total_budget)

    user_goal = (
        "Create a travel plan using the following parameters:\n"
        f"- Origin: {preprocessed_data.get('origin_city')}\n"
        f"- Destination: {preprocessed_data.get('destination_city')}\n"
        f"- Number of nights: {preprocessed_data.get('nights')}\n"
        f"- Number of travelers: {preprocessed_data.get('people')}\n"
        f"- Total budget: {total_budget_text}\n"
        f"- Hotel budget per night: {preprocessed_data.get('hotel_budget_per_night')} TL\n"
        f"- Daily budget per person: {preprocessed_data.get('daily_budget_per_person')} TL\n"
        f"- Travel date: {preprocessed_data.get('travel_date')}\n"
        f"- Check-in / Check-out: {preprocessed_data.get('check_in')} - {preprocessed_data.get('check_out')}\n"
        f"- Trip type: {preprocessed_data.get('trip_type')}\n"
        "\nUse the tools to gather weather, flights, hotels, attractions, cost, and recommendations. "
        "If some data is missing, suggest alternatives and still provide a clear final plan."
    )

    result = agent_executor.invoke({"messages": [{"role": "user", "content": user_goal}]})
    messages = result.get("messages", [])
    if not messages:
        return "Cikti uretilemedi."

    final_answer = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
    used_tools, tool_outputs = _extract_tool_trace(messages)

    tools_section = "Used Tools: " + (", ".join(used_tools) if used_tools else "Not determined")
    outputs_section = "Tool Outputs:\n" + ("\n".join(tool_outputs) if tool_outputs else "- No tool output captured")
    return f"{tools_section}\n\n{outputs_section}\n\nAgent Result:\n{final_answer}"
