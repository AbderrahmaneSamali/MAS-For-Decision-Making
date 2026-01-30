# Crisis Manager MAS - Technical Documentation

> **Version**: 3.2  
> **Last Updated**: 2026-01-30  
> **Framework**: CrewAI + Knowledge Graph

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Knowledge Graph](#knowledge-graph)
5. [Tools Reference](#tools-reference)
6. [Agents](#agents)
7. [API Reference](#api-reference)
8. [Configuration](#configuration)
9. [Memory System](#memory-system)
10. [Usage Examples](#usage-examples)

---

## Overview

Crisis Manager is a **Multi-Agent System (MAS)** for managerial crisis decision-making. It uses a knowledge graph of precedents, rules, and mechanisms to analyze crisis scenarios and deliver actionable verdicts.

### Key Capabilities

- **Precedent Matching**: Find similar historical cases (Uber 2016, Equifax 2017, etc.)
- **Risk Assessment**: Calculate Financial, Ethical, and Legal risk scores
- **Causal Chain Tracing**: Map Action → Mechanism → Consequence flows
- **Conflict Resolution**: Apply rule weights to resolve competing priorities
- **Decision Memory**: Learn from past decisions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CRISIS MANAGER v3.2                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  SCIENTIST  │───▶│ COMPLIANCE  │───▶│    JUDGE    │             │
│  │   Agent     │    │   Agent     │    │   Agent     │             │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘             │
│         │                  │                  │                     │
│         ▼                  ▼                  ▼                     │
│  ┌─────────────────────────────────────────────────────┐           │
│  │              KNOWLEDGE SERVICE (Singleton)          │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │           │
│  │  │ Source Index│  │Target Index │  │ Node Index  │ │           │
│  │  │   O(1)     │  │    O(1)     │  │    O(1)     │ │           │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │           │
│  └─────────────────────────────────────────────────────┘           │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────┐           │
│  │                 knowledge_base.json                  │           │
│  │  Cases │ Precedents │ Rules │ Mechanisms │ Edges    │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐                      │
│  │  MEMORY SERVICE  │    │     CONFIG       │                      │
│  │ decision_history │    │ Externalized     │                      │
│  └──────────────────┘    └──────────────────┘                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Components

### File Structure

```
crisis_manager/
├── __init__.py           # Package exports
├── config.py             # Externalized constants
├── knowledge_service.py  # Singleton graph service
├── memory_service.py     # Decision history
├── agents.py             # Agent definitions
├── tools.py              # 8 custom tools
├── crew.py               # Crew orchestrator
└── knowledge_base.json   # Knowledge graph data
```

### Dependency Flow

```
config.py                    ← No dependencies
knowledge_service.py         ← config.py
memory_service.py            ← No dependencies
tools.py                     ← knowledge_service.py, config.py
agents.py                    ← tools.py
crew.py                      ← agents.py, memory_service.py
```

---

## Knowledge Graph

### Node Types

| Type | Count | Description |
|------|-------|-------------|
| `Case_Dilemma` | 8 | Business ethics scenarios |
| `Case_Failure` / `Case_Success` | 4 | Historical precedents |
| `Law_Hard` | 2 | Mandatory regulations (weight=10) |
| `Heuristic_Soft` | 4 | Best practices (weight=4-9) |
| `Risk_Mechanism` | 4 | Risk amplifiers |
| `Financial_Mechanism` | 1 | Financial effects |
| `Action` | 3 | Decision options |

### Edge Relationships

| Relationship | Meaning |
|--------------|---------|
| `VIOLATED` | Action/precedent broke a rule |
| `COMPLIED` | Action/precedent followed a rule |
| `ACTIVATED` | Triggered a mechanism |
| `TRIGGERS` | Direct causation |
| `RISKED` | Potential violation |
| `INCREASES` | Amplifies another node |
| `CONFLICTS_WITH` | Rule/heuristic tension |

### Example Subgraph

```
ACTION_CONCEAL_AS_BOUNTY
    │
    ├──ACTIVATES──▶ CONCEPT_CONCEALMENT_MULTIPLIER (×3.5)
    │
    ├──ACTIVATES──▶ CONCEPT_EXECUTIVE_LIABILITY
    │
    └──VIOLATES───▶ RULE_ETHICAL_HARDLINE (weight=9)
```

---

## Tools Reference

### 1. GraphSearchTool
**Name**: `graph_search`  
**Input**: Comma-separated keywords  
**Output**: Matching nodes with scores

```python
# Example
graph_search("ransomware, concealment, breach")
# Returns: PRECEDENT_UBER_2016 (score: 0.8), ACTION_CONCEAL_AS_BOUNTY (score: 0.6)
```

### 2. RuleLookupTool
**Name**: `rule_lookup`  
**Input**: `"hard"`, `"soft"`, or `"all"`  
**Output**: Rules sorted by weight

### 3. RiskCalculatorTool
**Name**: `risk_calculator`  
**Input**: Scenario description (string or JSON)  
**Output**: Risk scores + mechanisms triggered

```json
{
  "financial_score": 8,
  "ethical_score": 9,
  "legal_score": 10,
  "total_risk": 9.0,
  "risk_level": "CRITICAL",
  "mechanisms_triggered": ["CONCEPT_CONCEALMENT_MULTIPLIER"],
  "total_exposure_estimate": "$23,500,000"
}
```

### 4. EdgeTraversalTool
**Name**: `edge_traversal`  
**Input**: Node ID  
**Output**: Connected nodes with relationships

### 5. MechanismLookupTool
**Name**: `mechanism_lookup`  
**Input**: `"risk"`, `"financial"`, or `"all"`  
**Output**: Mechanisms with effects

### 6. CausalChainTool
**Name**: `causal_chain_trace`  
**Input**: Action keywords  
**Output**: Full causal chain with exposure calculation

### 7. PathFinderTool
**Name**: `path_finder`  
**Input**: `"START_NODE, END_NODE"`  
**Output**: All paths between nodes (max depth 4)

### 8. ReachabilityTool
**Name**: `reachability_analysis`  
**Input**: Start node ID  
**Output**: All reachable nodes with distances

---

## Agents

### Scientist Agent

**Role**: Crisis Research Scientist  
**Tools**: GraphSearch, EdgeTraversal, PathFinder, Reachability  
**Focus**: Pattern discovery and precedent matching

### Compliance Agent

**Role**: Chief Risk & Compliance Officer  
**Tools**: RuleLookup, RiskCalculator, MechanismLookup, EdgeTraversal  
**Focus**: Legal/ethical risk assessment

### Judge Agent

**Role**: Crisis Resolution Judge  
**Tools**: CausalChain, RiskCalculator  
**Focus**: Synthesis and final verdict

---

## API Reference

### CrisisManagerCrew

```python
from crisis_manager import CrisisManagerCrew

crew = CrisisManagerCrew(verbose=True)

# Analyze a crisis
result = crew.analyze_crisis("Your scenario here...")

# Get agent info
roles = crew.get_agent_roles()

# Get similar past decisions
similar = crew.get_similar_past_decisions("scenario text", limit=5)

# Get decision statistics
stats = crew.get_decision_stats()
```

### KnowledgeService

```python
from crisis_manager import get_knowledge_service

ks = get_knowledge_service()

# O(1) node lookup
node = ks.get_node("PRECEDENT_UBER_2016")

# O(1) edge lookups
outgoing = ks.get_outgoing_edges("ACTION_DELAY_REPORTING")
incoming = ks.get_incoming_edges("RULE_GDPR_33")

# Path finding
path = ks.find_path("ACTION_DELAY_REPORTING", "CONCEPT_INSURANCE_VOID")
all_paths = ks.find_all_paths(start, end, max_depth=4)

# Reachability
reachable = ks.get_reachable_nodes("ACTION_CONCEAL_AS_BOUNTY", max_depth=3)
```

### MemoryService

```python
from crisis_manager import get_memory_service

memory = get_memory_service()

# Record a decision
decision_id = memory.record_decision(
    scenario="...",
    verdict="REJECT",
    precedent_used="PRECEDENT_UBER_2016",
    risk_scores={"financial": 8, "ethical": 9, "legal": 10}
)

# Add feedback
memory.add_feedback(decision_id, outcome="correct", notes="Good call")

# Retrieve history
recent = memory.get_recent_decisions(10)
accuracy = memory.get_feedback_accuracy()
```

---

## Configuration

All constants are in `config.py`:

```python
from crisis_manager import CrisisConfig

# Financial defaults
CrisisConfig.BASE_PENALTY_ESTIMATE    # $1,000,000
CrisisConfig.INSURANCE_LOSS_DEFAULT   # $20,000,000

# Multipliers
CrisisConfig.CONCEALMENT_MULTIPLIER   # 3.5

# Risk thresholds
CrisisConfig.RISK_CRITICAL_THRESHOLD  # 7.0
CrisisConfig.RISK_HIGH_THRESHOLD      # 5.0

# Keywords for detection
CrisisConfig.HIGH_FINANCIAL_KEYWORDS
CrisisConfig.HIGH_ETHICAL_KEYWORDS
CrisisConfig.HIGH_LEGAL_KEYWORDS
```

---

## Memory System

Decisions are persisted to `decision_history.json`:

```json
{
  "decisions": [
    {
      "id": "DEC_20260130_213045",
      "timestamp": "2026-01-30T21:30:45",
      "scenario_hash": "abc123def456",
      "scenario_preview": "CEO of mid-sized Fintech...",
      "verdict": "REJECT",
      "precedent_used": "PRECEDENT_UBER_2016",
      "risk_scores": {"financial": 8, "ethical": 9, "legal": 10},
      "confidence": 0.95
    }
  ],
  "precedent_usage": {
    "PRECEDENT_UBER_2016": 5,
    "PRECEDENT_HYDRO_2019": 2
  },
  "feedback": [
    {"decision_id": "DEC_...", "outcome": "correct", "notes": ""}
  ]
}
```

---

## Usage Examples

### Basic Analysis

```python
from crisis_manager import CrisisManagerCrew

crew = CrisisManagerCrew()
result = crew.analyze_crisis("""
    We discovered a data breach affecting 50,000 users.
    Hackers want $50K in Bitcoin. CISO suggests paying and
    calling it a 'Bug Bounty' to avoid disclosure.
""")
print(result)
```

### Custom Graph Query

```python
from crisis_manager import get_knowledge_service

ks = get_knowledge_service()

# Find all nodes connected to concealment
edges = ks.get_outgoing_edges("ACTION_CONCEAL_AS_BOUNTY")
for edge in edges:
    print(f"{edge['relationship']} → {edge['target']}")
```

### Check Reachable Impact

```python
ks = get_knowledge_service()
impact = ks.get_reachable_nodes("ACTION_DELAY_REPORTING", max_depth=2)

for node_id, distance in impact.items():
    print(f"Distance {distance}: {node_id}")
```

---

## License

MIT License - See [README.md](./README.md)
