"""
Crisis Manager - CrewAI Tools v3.1
Custom tools for graph traversal, risk calculation, and causal mechanism tracing.
"""

import json
import os
from typing import Any
from crewai.tools import BaseTool
from pydantic import Field


class GraphSearchTool(BaseTool):
    """Tool for searching the knowledge graph by tags/keywords."""
    
    name: str = "graph_search"
    description: str = """Search the knowledge graph for cases, precedents, actions, and mechanisms
    matching the given keywords. Returns matched nodes with relevance scores.
    Use this to find relevant precedents and mechanisms for a given scenario."""
    
    knowledge_base: dict = Field(default_factory=dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
    
    def _run(self, query: str) -> str:
        """Search for nodes matching the query keywords."""
        keywords = [k.strip().lower() for k in query.split(",")]
        results = []
        
        # Search cases
        for case in self.knowledge_base.get("cases", []):
            tags = [t.lower() for t in case.get("tags", [])]
            matches = sum(1 for k in keywords if any(k in t for t in tags))
            if matches > 0:
                results.append({
                    "id": case["id"],
                    "type": case["type"],
                    "title": case.get("title", ""),
                    "match_score": matches / len(keywords),
                    "sentiment": case.get("sentiment", 0),
                    "dilemma": case.get("dilemma", ""),
                    "key_fact": case.get("key_fact", "")
                })
        
        # Search precedents
        for prec in self.knowledge_base.get("precedents", []):
            tags = [t.lower() for t in prec.get("tags", [])]
            matches = sum(1 for k in keywords if any(k in t for t in tags))
            if matches > 0:
                results.append({
                    "id": prec["id"],
                    "type": prec["type"],
                    "action": prec.get("action", ""),
                    "consequence": prec.get("consequence", ""),
                    "match_score": matches / len(keywords),
                    "sentiment": prec.get("sentiment", 0),
                    "legal_citation": prec.get("legal_citation", "")
                })
        
        # Search actions (v3.1)
        for action in self.knowledge_base.get("actions", []):
            tags = [t.lower() for t in action.get("tags", [])]
            keywords_list = [k.lower() for k in action.get("keywords", [])]
            matches = sum(1 for k in keywords if any(k in t for t in tags + keywords_list))
            if matches > 0:
                results.append({
                    "id": action["id"],
                    "type": "Action",
                    "description": action.get("description", ""),
                    "match_score": matches / len(keywords)
                })
        
        # Search mechanisms (v3.1)
        for mech in self.knowledge_base.get("mechanisms", []):
            tags = [t.lower() for t in mech.get("tags", [])]
            matches = sum(1 for k in keywords if any(k in t for t in tags))
            if matches > 0:
                results.append({
                    "id": mech["id"],
                    "type": mech["type"],
                    "definition": mech.get("definition", ""),
                    "effect": mech.get("effect", ""),
                    "match_score": matches / len(keywords)
                })
        
        # Sort by match score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        if not results:
            return "No matching nodes found."
        
        return json.dumps(results[:7], indent=2, ensure_ascii=False)


class RuleLookupTool(BaseTool):
    """Tool for retrieving rules and heuristics with their weights."""
    
    name: str = "rule_lookup"
    description: str = """Retrieve rules and heuristics from the knowledge base.
    Returns rules with their weights for conflict resolution.
    Use weight values to determine which rules take precedence."""
    
    knowledge_base: dict = Field(default_factory=dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
    
    def _run(self, rule_type: str = "all") -> str:
        """Get rules by type: 'hard', 'soft', or 'all'."""
        rules = self.knowledge_base.get("rules", [])
        
        if rule_type.lower() == "hard":
            rules = [r for r in rules if r["type"] == "Law_Hard"]
        elif rule_type.lower() == "soft":
            rules = [r for r in rules if r["type"] == "Heuristic_Soft"]
        
        # Sort by weight
        rules.sort(key=lambda x: x.get("weight", 0), reverse=True)
        
        return json.dumps(rules, indent=2, ensure_ascii=False)


class RiskCalculatorTool(BaseTool):
    """Tool for calculating risk scores with mechanism multipliers (v3.1)."""
    
    name: str = "risk_calculator"
    description: str = """Calculate Financial, Ethical, and Legal risk scores (0-10) 
    for a given scenario. Now includes mechanism multipliers for second-order effects.
    Input should describe the scenario and any triggered mechanisms.
    Formula: Total Risk = (Base Fine * Concealment Multiplier) + Lost Insurance."""
    
    knowledge_base: dict = Field(default_factory=dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
    
    def _run(self, scenario_json: str) -> str:
        """Calculate risk scores with mechanism effects."""
        try:
            scenario = json.loads(scenario_json)
        except json.JSONDecodeError:
            scenario = {"description": scenario_json}
        
        desc = str(scenario).lower()
        
        # Base scores
        high_financial = ["million", "bankruptcy", "critical", "40%", "major", "insurance"]
        high_ethical = ["fraud", "corruption", "deception", "lie", "steal", "bribe", "conceal", "hide"]
        high_legal = ["criminal", "felony", "gdpr", "sanction", "lawsuit", "prison", "72h"]
        
        financial_score = min(10, 3 + sum(2 for k in high_financial if k in desc))
        ethical_score = min(10, 3 + sum(2 for k in high_ethical if k in desc))
        legal_score = min(10, 3 + sum(2 for k in high_legal if k in desc))
        
        # Check for mechanism triggers
        mechanisms_triggered = []
        multiplier = 1.0
        insurance_loss = 0
        
        # Check concealment
        if any(k in desc for k in ["conceal", "hide", "delay", "cover up", "wait"]):
            mechanisms_triggered.append("CONCEPT_CONCEALMENT_MULTIPLIER")
            multiplier = 3.5
            legal_score = min(10, legal_score * 1.5)
        
        # Check insurance void (72h delay)
        if any(k in desc for k in ["delay", "wait", "2 week", "72h", "insurance"]):
            mechanisms_triggered.append("CONCEPT_INSURANCE_VOID")
            insurance_loss = 20000000  # $20M example
            financial_score = min(10, financial_score + 3)
        
        # Calculate totals
        base_penalty_estimate = 1000000  # $1M base
        total_penalty = (base_penalty_estimate * multiplier) + insurance_loss
        total_risk = (financial_score + ethical_score + legal_score) / 3
        
        result = {
            "financial_score": financial_score,
            "ethical_score": ethical_score,
            "legal_score": legal_score,
            "total_risk": round(total_risk, 1),
            "risk_level": "CRITICAL" if total_risk > 7 else "HIGH" if total_risk > 5 else "MEDIUM",
            "mechanisms_triggered": mechanisms_triggered,
            "penalty_multiplier": multiplier,
            "insurance_loss_estimate": f"${insurance_loss:,}" if insurance_loss else "$0",
            "total_exposure_estimate": f"${total_penalty:,.0f}"
        }
        
        return json.dumps(result, indent=2)


class EdgeTraversalTool(BaseTool):
    """Tool for traversing graph edges to find related nodes."""
    
    name: str = "edge_traversal"
    description: str = """Traverse the knowledge graph edges from a given node.
    Returns all connected nodes with relationships (VIOLATED, COMPLIED, TRIGGERS, ACTIVATES, etc).
    Use this to understand causal chains: Action -> Mechanism -> Consequence."""
    
    knowledge_base: dict = Field(default_factory=dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
    
    def _run(self, node_id: str) -> str:
        """Find all edges connected to the given node."""
        edges = self.knowledge_base.get("edges", [])
        connected = []
        
        for edge in edges:
            if edge["source"] == node_id:
                connected.append({
                    "direction": "outgoing",
                    "relationship": edge["relationship"],
                    "target": edge["target"]
                })
            elif edge["target"] == node_id:
                connected.append({
                    "direction": "incoming",
                    "relationship": edge["relationship"],
                    "source": edge["source"]
                })
        
        if not connected:
            return f"No edges found for node: {node_id}"
        
        return json.dumps(connected, indent=2)


class MechanismLookupTool(BaseTool):
    """Tool for looking up Risk and Financial mechanisms (v3.1)."""
    
    name: str = "mechanism_lookup"
    description: str = """Look up Risk_Mechanism and Financial_Mechanism nodes from the knowledge base.
    These mechanisms transform actions into consequences with multiplier effects.
    Use this to understand second-order effects like insurance voidance or penalty multipliers."""
    
    knowledge_base: dict = Field(default_factory=dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
    
    def _run(self, mechanism_type: str = "all") -> str:
        """Get mechanisms by type: 'risk', 'financial', or 'all'."""
        mechanisms = self.knowledge_base.get("mechanisms", [])
        
        if mechanism_type.lower() == "risk":
            mechanisms = [m for m in mechanisms if m["type"] == "Risk_Mechanism"]
        elif mechanism_type.lower() == "financial":
            mechanisms = [m for m in mechanisms if m["type"] == "Financial_Mechanism"]
        
        if not mechanisms:
            return "No mechanisms found."
        
        return json.dumps(mechanisms, indent=2, ensure_ascii=False)


class CausalChainTool(BaseTool):
    """Tool for tracing complete causal chains: Action -> Mechanism -> Consequence (v3.1)."""
    
    name: str = "causal_chain_trace"
    description: str = """Trace the full causal chain for a given action.
    Returns: Action -> Triggered Mechanisms -> Violated Rules -> Expected Consequences.
    Use this to understand the complete impact of a proposed decision.
    Input: action keywords like 'delay', 'conceal', 'disclose'."""
    
    knowledge_base: dict = Field(default_factory=dict)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
    
    def _run(self, action_keywords: str) -> str:
        """Trace causal chain from action to consequence."""
        keywords = [k.strip().lower() for k in action_keywords.split(",")]
        
        # Find matching action
        matched_action = None
        for action in self.knowledge_base.get("actions", []):
            action_keywords_list = [k.lower() for k in action.get("keywords", [])]
            tags = [t.lower() for t in action.get("tags", [])]
            if any(k in " ".join(action_keywords_list + tags) for k in keywords):
                matched_action = action
                break
        
        if not matched_action:
            return f"No action found matching: {action_keywords}"
        
        # Find edges from this action
        edges = self.knowledge_base.get("edges", [])
        triggered_mechanisms = []
        violated_rules = []
        
        for edge in edges:
            if edge["source"] == matched_action["id"]:
                target_id = edge["target"]
                relationship = edge["relationship"]
                
                # Find the target node
                for mech in self.knowledge_base.get("mechanisms", []):
                    if mech["id"] == target_id:
                        triggered_mechanisms.append({
                            "mechanism_id": mech["id"],
                            "relationship": relationship,
                            "type": mech["type"],
                            "definition": mech.get("definition", ""),
                            "effect": mech.get("effect", ""),
                            "multiplier": mech.get("multiplier_value"),
                            "financial_impact": mech.get("financial_impact"),
                            "typical_exposure": mech.get("typical_exposure")
                        })
                
                for rule in self.knowledge_base.get("rules", []):
                    if rule["id"] == target_id:
                        violated_rules.append({
                            "rule_id": rule["id"],
                            "relationship": relationship,
                            "type": rule["type"],
                            "weight": rule["weight"],
                            "content": rule["content"],
                            "penalty": rule.get("penalty", "")
                        })
        
        # Find precedents that match this pattern
        matching_precedents = []
        for prec in self.knowledge_base.get("precedents", []):
            prec_tags = [t.lower() for t in prec.get("tags", [])]
            if any(k in " ".join(prec_tags) for k in keywords):
                matching_precedents.append({
                    "precedent_id": prec["id"],
                    "type": prec["type"],
                    "action": prec.get("action", ""),
                    "consequence": prec.get("consequence", ""),
                    "legal_citation": prec.get("legal_citation", "")
                })
        
        # Calculate total exposure
        total_multiplier = 1.0
        insurance_exposure = 0
        for mech in triggered_mechanisms:
            if mech.get("multiplier"):
                total_multiplier *= mech["multiplier"]
            if "insurance" in mech.get("definition", "").lower():
                insurance_exposure = 20000000  # $20M default
        
        result = {
            "action": {
                "id": matched_action["id"],
                "description": matched_action.get("description", "")
            },
            "causal_chain": {
                "triggered_mechanisms": triggered_mechanisms,
                "violated_rules": violated_rules,
                "matching_precedents": matching_precedents
            },
            "exposure_calculation": {
                "penalty_multiplier": total_multiplier,
                "insurance_exposure": f"${insurance_exposure:,}" if insurance_exposure else "$0",
                "total_risk_formula": f"(Base_Penalty × {total_multiplier}) + ${insurance_exposure:,}"
            }
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)

