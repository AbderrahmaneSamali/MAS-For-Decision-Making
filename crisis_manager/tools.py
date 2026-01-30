"""
Crisis Manager - CrewAI Tools v3.2
Refactored tools using shared KnowledgeService and externalized configuration.
"""

import json
from typing import Any
from crewai.tools import BaseTool
from pydantic import Field

from .knowledge_service import get_knowledge_service, KnowledgeService
from .config import CrisisConfig


class GraphSearchTool(BaseTool):
    """Tool for searching the knowledge graph by tags/keywords."""
    
    name: str = "graph_search"
    description: str = """Search the knowledge graph for cases, precedents, actions, and mechanisms
    matching the given keywords. Returns matched nodes with relevance scores.
    Use this to find relevant precedents and mechanisms for a given scenario."""
    
    def _run(self, query: str) -> str:
        """Search for nodes matching the query keywords."""
        ks = get_knowledge_service()
        keywords = [k.strip() for k in query.split(",")]
        
        results = ks.search_by_keywords(keywords)
        
        # Format results
        formatted = []
        for node in results[:CrisisConfig.MAX_SEARCH_RESULTS]:
            formatted.append({
                "id": node.get("id"),
                "type": node.get("type", node.get("_collection", "")),
                "match_score": node.get("match_score", 0),
                "title": node.get("title", node.get("description", "")),
                "sentiment": node.get("sentiment"),
                "action": node.get("action"),
                "consequence": node.get("consequence"),
                "legal_citation": node.get("legal_citation")
            })
        
        if not formatted:
            return "No matching nodes found."
        
        return json.dumps(formatted, indent=2, ensure_ascii=False)


class RuleLookupTool(BaseTool):
    """Tool for retrieving rules and heuristics with their weights."""
    
    name: str = "rule_lookup"
    description: str = """Retrieve rules and heuristics from the knowledge base.
    Returns rules with their weights for conflict resolution.
    Use weight values to determine which rules take precedence.
    Law_Hard (weight 10) always overrides Heuristic_Soft (weight 4-9)."""
    
    def _run(self, rule_type: str = "all") -> str:
        """Get rules by type: 'hard', 'soft', or 'all'."""
        ks = get_knowledge_service()
        rules = ks.get_rules_by_type(rule_type)
        return json.dumps(rules, indent=2, ensure_ascii=False)


class RiskCalculatorTool(BaseTool):
    """Tool for calculating risk scores with mechanism multipliers."""
    
    name: str = "risk_calculator"
    description: str = """Calculate Financial, Ethical, and Legal risk scores (0-10) 
    for a given scenario. Includes mechanism multipliers for second-order effects.
    Input should describe the scenario and any triggered mechanisms.
    Formula: Total Risk = (Base Fine * Concealment Multiplier) + Lost Insurance."""
    
    def _run(self, scenario_json: str) -> str:
        """Calculate risk scores with mechanism effects."""
        ks = get_knowledge_service()
        
        try:
            scenario = json.loads(scenario_json)
        except json.JSONDecodeError:
            scenario = {"description": scenario_json}
        
        desc = str(scenario).lower()
        
        # Base scores using config keywords
        financial_score = min(10, 3 + sum(2 for k in CrisisConfig.HIGH_FINANCIAL_KEYWORDS if k in desc))
        ethical_score = min(10, 3 + sum(2 for k in CrisisConfig.HIGH_ETHICAL_KEYWORDS if k in desc))
        legal_score = min(10, 3 + sum(2 for k in CrisisConfig.HIGH_LEGAL_KEYWORDS if k in desc))
        
        # Check for mechanism triggers
        mechanisms_triggered = []
        multiplier = 1.0
        insurance_loss = 0
        
        # Check concealment
        if any(k in desc for k in CrisisConfig.CONCEALMENT_KEYWORDS):
            mechanisms_triggered.append("CONCEPT_CONCEALMENT_MULTIPLIER")
            multiplier = CrisisConfig.CONCEALMENT_MULTIPLIER
            legal_score = min(10, legal_score * 1.5)
        
        # Check insurance void
        if any(k in desc for k in CrisisConfig.INSURANCE_VOID_KEYWORDS):
            mechanisms_triggered.append("CONCEPT_INSURANCE_VOID")
            insurance_loss = CrisisConfig.INSURANCE_LOSS_DEFAULT
            financial_score = min(10, financial_score + 3)
        
        # Calculate totals
        base_penalty = CrisisConfig.BASE_PENALTY_ESTIMATE
        total_penalty = (base_penalty * multiplier) + insurance_loss
        total_risk = (financial_score + ethical_score + legal_score) / 3
        
        result = {
            "financial_score": financial_score,
            "ethical_score": ethical_score,
            "legal_score": legal_score,
            "total_risk": round(total_risk, 1),
            "risk_level": CrisisConfig.get_risk_level(total_risk),
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
    
    def _run(self, node_id: str) -> str:
        """Find all edges connected to the given node using O(1) indexed lookup."""
        ks = get_knowledge_service()
        connected = []
        
        # O(1) outgoing edges lookup
        for edge in ks.get_outgoing_edges(node_id):
            target_node = ks.get_node(edge["target"])
            connected.append({
                "direction": "outgoing",
                "relationship": edge["relationship"],
                "target": edge["target"],
                "target_type": target_node.get("type") if target_node else None
            })
        
        # O(1) incoming edges lookup
        for edge in ks.get_incoming_edges(node_id):
            source_node = ks.get_node(edge["source"])
            connected.append({
                "direction": "incoming",
                "relationship": edge["relationship"],
                "source": edge["source"],
                "source_type": source_node.get("type") if source_node else None
            })
        
        if not connected:
            return f"No edges found for node: {node_id}"
        
        return json.dumps(connected, indent=2)


class MechanismLookupTool(BaseTool):
    """Tool for looking up Risk and Financial mechanisms."""
    
    name: str = "mechanism_lookup"
    description: str = """Look up Risk_Mechanism and Financial_Mechanism nodes from the knowledge base.
    These mechanisms transform actions into consequences with multiplier effects.
    Use this to understand second-order effects like insurance voidance or penalty multipliers."""
    
    def _run(self, mechanism_type: str = "all") -> str:
        """Get mechanisms by type: 'risk', 'financial', or 'all'."""
        ks = get_knowledge_service()
        mechanisms = ks.get_mechanisms_by_type(mechanism_type)
        
        if not mechanisms:
            return "No mechanisms found."
        
        return json.dumps(mechanisms, indent=2, ensure_ascii=False)


class CausalChainTool(BaseTool):
    """Tool for tracing complete causal chains: Action -> Mechanism -> Consequence."""
    
    name: str = "causal_chain_trace"
    description: str = """Trace the full causal chain for a given action.
    Returns: Action -> Triggered Mechanisms -> Violated Rules -> Expected Consequences.
    Use this to understand the complete impact of a proposed decision.
    Input: action keywords like 'delay', 'conceal', 'disclose'."""
    
    def _run(self, action_keywords: str) -> str:
        """Trace causal chain from action to consequence using graph traversal."""
        ks = get_knowledge_service()
        keywords = [k.strip().lower() for k in action_keywords.split(",")]
        
        # Find matching action
        matched_action = None
        for action in ks.actions:
            action_kw = [k.lower() for k in action.get("keywords", [])]
            tags = [t.lower() for t in action.get("tags", [])]
            if any(k in " ".join(action_kw + tags) for k in keywords):
                matched_action = action
                break
        
        if not matched_action:
            return f"No action found matching: {action_keywords}"
        
        # Use indexed edge lookup to find connections
        triggered_mechanisms = []
        violated_rules = []
        
        for edge in ks.get_outgoing_edges(matched_action["id"]):
            target_id = edge["target"]
            target_node = ks.get_node(target_id)
            
            if target_node:
                node_type = target_node.get("type", "")
                
                if "Mechanism" in node_type:
                    triggered_mechanisms.append({
                        "mechanism_id": target_id,
                        "relationship": edge["relationship"],
                        "type": node_type,
                        "definition": target_node.get("definition", ""),
                        "effect": target_node.get("effect", ""),
                        "multiplier": target_node.get("multiplier_value"),
                        "financial_impact": target_node.get("financial_impact"),
                        "typical_exposure": target_node.get("typical_exposure")
                    })
                elif target_node.get("type") in ("Law_Hard", "Heuristic_Soft"):
                    violated_rules.append({
                        "rule_id": target_id,
                        "relationship": edge["relationship"],
                        "type": target_node["type"],
                        "weight": target_node.get("weight"),
                        "content": target_node.get("content", ""),
                        "penalty": target_node.get("penalty", "")
                    })
        
        # Find matching precedents using keyword search
        matching_precedents = []
        precedent_results = ks.search_by_keywords(keywords, ["precedents"])
        for prec in precedent_results[:3]:
            matching_precedents.append({
                "precedent_id": prec["id"],
                "type": prec.get("type", ""),
                "action": prec.get("action", ""),
                "consequence": prec.get("consequence", ""),
                "legal_citation": prec.get("legal_citation", ""),
                "match_score": prec.get("match_score", 0)
            })
        
        # Calculate total exposure
        total_multiplier = 1.0
        insurance_exposure = 0
        for mech in triggered_mechanisms:
            if mech.get("multiplier"):
                total_multiplier *= mech["multiplier"]
            if "insurance" in mech.get("definition", "").lower():
                insurance_exposure = CrisisConfig.INSURANCE_LOSS_DEFAULT
        
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


class PathFinderTool(BaseTool):
    """NEW: Tool for finding paths between nodes in the knowledge graph."""
    
    name: str = "path_finder"
    description: str = """Find all paths between two nodes in the knowledge graph.
    Use this to discover indirect relationships and causal chains.
    Input: 'start_node_id, end_node_id' (comma-separated).
    Returns paths with the nodes traversed."""
    
    def _run(self, nodes: str) -> str:
        """Find paths between two nodes using BFS."""
        ks = get_knowledge_service()
        
        parts = [n.strip() for n in nodes.split(",")]
        if len(parts) != 2:
            return "Error: Provide exactly two node IDs separated by comma."
        
        start_id, end_id = parts
        
        # Validate nodes exist
        if not ks.get_node(start_id):
            return f"Error: Start node '{start_id}' not found."
        if not ks.get_node(end_id):
            return f"Error: End node '{end_id}' not found."
        
        # Find all paths
        paths = ks.find_all_paths(start_id, end_id, max_depth=4)
        
        if not paths:
            return f"No path found between '{start_id}' and '{end_id}'."
        
        # Format paths with node details
        formatted_paths = []
        for path in paths:
            path_details = []
            for node_id in path:
                node = ks.get_node(node_id)
                path_details.append({
                    "id": node_id,
                    "type": node.get("type") if node else "Unknown"
                })
            formatted_paths.append(path_details)
        
        return json.dumps({
            "start": start_id,
            "end": end_id,
            "paths_found": len(paths),
            "paths": formatted_paths
        }, indent=2)


class ReachabilityTool(BaseTool):
    """NEW: Tool for finding all nodes reachable from a given node."""
    
    name: str = "reachability_analysis"
    description: str = """Find all nodes reachable from a given starting node.
    Returns nodes with their distance (hop count) from the start.
    Use this to understand the full impact scope of an action or decision."""
    
    def _run(self, start_node: str) -> str:
        """Get all reachable nodes with distances."""
        ks = get_knowledge_service()
        
        if not ks.get_node(start_node):
            return f"Error: Node '{start_node}' not found."
        
        reachable = ks.get_reachable_nodes(start_node, max_depth=4)
        
        # Group by distance
        by_distance = {}
        for node_id, distance in reachable.items():
            if distance not in by_distance:
                by_distance[distance] = []
            node = ks.get_node(node_id)
            by_distance[distance].append({
                "id": node_id,
                "type": node.get("type") if node else "Unknown"
            })
        
        return json.dumps({
            "start_node": start_node,
            "total_reachable": len(reachable),
            "nodes_by_distance": by_distance
        }, indent=2)
