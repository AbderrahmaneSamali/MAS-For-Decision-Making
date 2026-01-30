# Crisis Manager - Multi-Agent Decision System

A CrewAI-powered multi-agent system for managerial crisis decision-making.

## Features

- **Knowledge Graph**: JSON-LD database with cases, precedents, rules, and heuristics
- **3 Specialized Agents**:
  - **Scientist**: Pattern matching and precedent research
  - **Compliance Officer**: Legal/ethical risk assessment
  - **Judge**: Final verdict with conflict resolution
- **Graph Traversal Tools**: Search, lookup, risk calculation, edge traversal

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set your OpenAI API key:
```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Linux/Mac
export OPENAI_API_KEY=your-key-here
```

## Usage

```bash
python main.py
```

Then choose from the menu:
1. Analyze a custom crisis scenario
2. Run the sample ransomware/bug bounty scenario
3. View agent roles
4. Exit

## Project Structure

```
Decisio Making/
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── crisis_manager/
    ├── __init__.py              # Package exports
    ├── agents.py                # CrewAI agent definitions
    ├── crew.py                  # Crew orchestrator
    ├── tools.py                 # Custom tools
    └── knowledge_base.json      # Knowledge graph data
```

## Knowledge Base

The system includes:
- **8 Business Cases**: Nepotism, conflicts of interest, corruption, etc.
- **3 Real Precedents**: Uber 2016, Norsk Hydro 2019, Colonial Pipeline 2021
- **6 Rules/Heuristics**: GDPR, OFAC, ethical hardline, pragmatism, etc.

## License

MIT
