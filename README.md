# Travel Planning Agent

A simple LangChain + Groq demo that turns a travel request into a structured trip plan.

## Highlights

- Extracts destination, nights, travelers, and budget from natural language
- Uses sample tools for weather, flights, hotels, attractions, and trip cost
- Supports follow-up updates in the same chat
- Runs from the terminal

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Run

```bash
python 06_main_agent.py
```

## Commands

- `help` or `yardim`
- `samples` or `ornekler`
- `example 1` or `ornek 1`
- `1` to `8`
- `reset` or `sifirla`
- `exit` or `quit` or `cikis`

## Project Files

- `01_destination_database.py` - sample travel data
- `02_travel_tools.py` - LangChain tools
- `03_travel_agent.py` - agent setup
- `04_preprocessing_chain.py` - request parsing
- `05_postprocessing_chain.py` - response formatting
- `06_main_agent.py` - interactive CLI

## Note

This repo uses sample data, so it is a demo project rather than a live booking system.
