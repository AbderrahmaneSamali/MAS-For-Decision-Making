# Crisis Manager - Multi-Agent Decision System v3.2

A CrewAI-powered multi-agent system for managerial crisis decision-making with graph-based knowledge traversal.

## v3.2 Enhancements

- **Shared KnowledgeService**: Singleton with O(1) indexed lookups (no duplicate I/O)
- **Graph Engine**: NetworkX-style adjacency lists, BFS/DFS path-finding
- **Memory Layer**: Persistent decision history for learning
- **Externalized Config**: All constants in `config.py`
- **Enhanced Knowledge Base**: Temporal metadata, confidence scores, English translations

## Features

- **Knowledge Graph**: JSON-LD database with cases, precedents, rules, mechanisms, and actions
- **3 Specialized Agents** with optimized tool assignments:
  - **Scientist**: Graph search, edge traversal, path finding, reachability
  - **Compliance Officer**: Rule lookup, risk calculation, mechanisms, edge traversal
  - **Judge**: Causal chain synthesis, risk validation
- **8 Graph Traversal Tools**: Search, lookup, risk calc, edges, mechanisms, causal chain, paths, reachability
- **Decision Memory**: Track verdicts and precedent usage over time

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
├── main.py                          # CLI entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── crisis_manager/
    ├── __init__.py                  # Package exports
    ├── agents.py                    # CrewAI agent definitions (v3.2)
    ├── crew.py                      # Crew orchestrator with memory
    ├── tools.py                     # 8 custom tools (refactored)
    ├── config.py                    # Externalized configuration
    ├── knowledge_service.py         # Singleton graph service
    ├── memory_service.py            # Decision history persistence
    ├── knowledge_base.json          # Enhanced knowledge graph
    └── decision_history.json        # Auto-generated memory file
```

## Knowledge Base (v3.2)

- **8 Business Cases**: Nepotism, conflicts of interest, corruption (English)
- **4 Real Precedents**: Uber 2016, Norsk Hydro 2019, Colonial Pipeline 2021, Equifax 2017
- **6 Rules/Heuristics**: GDPR, OFAC, ethical hardline, pragmatism, etc.
- **5 Mechanisms**: Concealment multiplier, trust paradox, insurance void, etc.
- **3 Actions**: Delay reporting, immediate disclosure, conceal as bounty
- **32 Edges**: Full connectivity between nodes

## Architecture Improvements

| Before (v3.1) | After (v3.2) |
|---------------|--------------|
| 6 duplicate file loads | 1 singleton load |
| O(n) edge lookup | O(1) indexed lookup |
| Hardcoded constants | Externalized config |
| No memory | Decision history |
| No path finding | BFS/DFS traversal |
| Mixed languages | English only |

## License

MIT
