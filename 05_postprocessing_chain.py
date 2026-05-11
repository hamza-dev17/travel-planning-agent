from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


def build_postprocessing_chain():
    prompt = ChatPromptTemplate.from_template(
        """
You are a travel report editor.
Turn the agent's raw output into a clear and well-structured final report.

Required sections:
1) Trip Summary
2) Weather
3) Flight Information
4) Hotels
5) Attractions
6) Cost Breakdown
7) Travel Tips
8) Budget Review (Within budget / Over budget)

Budget limit: {total_budget} TL
Raw agent output:
{agent_output}
"""
    )
    model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
    return prompt | model


def format_final_response(agent_output: str, preprocessed_data: dict[str, Any]) -> str:
    try:
        chain = build_postprocessing_chain()
        result = chain.invoke(
            {
                "agent_output": agent_output,
                "total_budget": preprocessed_data.get("total_budget", "N/A"),
            }
        )
        return result.content
    except Exception:
        return (
            "TRAVEL RECOMMENDATION\n\n"
            f"Destination: {preprocessed_data.get('destination_city')}\n"
            f"Number of nights: {preprocessed_data.get('nights')}\n"
            f"Number of travelers: {preprocessed_data.get('people')}\n\n"
            "Agent Output:\n"
            f"{agent_output}"
        )
