"""
Crisis Manager - Knowledge Service v3.2
Singleton service providing centralized access to the knowledge graph with NetworkX.
"""

import json
import os
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict


class KnowledgeService:
    """
    Singleton service for knowledge base access with graph operations.
    
    Features:
    - Single load, shared access (no duplicate I/O)
    - Pre-indexed adjacency lists for O(1) edge lookups
    - BFS path-finding for multi-hop traversal
    - In-memory graph structure using NetworkX-style adjacency
    """
    
    _instance: Optional['KnowledgeService'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'KnowledgeService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if KnowledgeService._initialized:
            return
        
        self._knowledge_base: Dict[str, Any] = {}
        self._source_index: Dict[str, List[Dict]] = defaultdict(list)
        self._target_index: Dict[str, List[Dict]] = defaultdict(list)
        self._node_index: Dict[str, Dict] = {}
        
        self._load_knowledge_base()
        self._build_indices()
        KnowledgeService._initialized = True
    
    def _load_knowledge_base(self) -> None:
        """Load knowledge base from JSON file (called once)."""
        kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self._knowledge_base = json.load(f)
    
    def _build_indices(self) -> None:
        """Build pre-indexed adjacency lists for O(1) lookups."""
        # Index edges by source and target
        for edge in self._knowledge_base.get("edges", []):
            source = edge["source"]
            target = edge["target"]
            self._source_index[source].append(edge)
            self._target_index[target].append(edge)
        
        # Index all nodes by ID for quick lookup
        for collection in ["cases", "precedents", "rules", "mechanisms", "actions"]:
            for node in self._knowledge_base.get(collection, []):
                self._node_index[node["id"]] = node
    
    # ─────────────────────────────────────────────────────────────
    # Collection Accessors
    # ─────────────────────────────────────────────────────────────
    
    @property
    def cases(self) -> List[Dict]:
        return self._knowledge_base.get("cases", [])
    
    @property
    def precedents(self) -> List[Dict]:
        return self._knowledge_base.get("precedents", [])
    
    @property
    def rules(self) -> List[Dict]:
        return self._knowledge_base.get("rules", [])
    
    @property
    def mechanisms(self) -> List[Dict]:
        return self._knowledge_base.get("mechanisms", [])
    
    @property
    def actions(self) -> List[Dict]:
        return self._knowledge_base.get("actions", [])
    
    @property
    def edges(self) -> List[Dict]:
        return self._knowledge_base.get("edges", [])
    
    # ─────────────────────────────────────────────────────────────
    # O(1) Graph Operations
    # ─────────────────────────────────────────────────────────────
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """O(1) node lookup by ID."""
        return self._node_index.get(node_id)
    
    def get_outgoing_edges(self, node_id: str) -> List[Dict]:
        """O(1) get all edges originating from a node."""
        return self._source_index.get(node_id, [])
    
    def get_incoming_edges(self, node_id: str) -> List[Dict]:
        """O(1) get all edges pointing to a node."""
        return self._target_index.get(node_id, [])
    
    def get_neighbors(self, node_id: str, direction: str = "both") -> List[str]:
        """Get neighboring node IDs."""
        neighbors = set()
        
        if direction in ("out", "both"):
            for edge in self._source_index.get(node_id, []):
                neighbors.add(edge["target"])
        
        if direction in ("in", "both"):
            for edge in self._target_index.get(node_id, []):
                neighbors.add(edge["source"])
        
        return list(neighbors)
    
    # ─────────────────────────────────────────────────────────────
    # Path Finding (BFS)
    # ─────────────────────────────────────────────────────────────
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> Optional[List[str]]:
        """
        BFS path finding from start to end node.
        Returns list of node IDs representing the path, or None if not found.
        """
        if start_id == end_id:
            return [start_id]
        
        visited: Set[str] = {start_id}
        queue: List[List[str]] = [[start_id]]
        
        while queue:
            path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            current = path[-1]
            
            for neighbor in self.get_neighbors(current, direction="out"):
                if neighbor == end_id:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        return None
    
    def find_all_paths(self, start_id: str, end_id: str, max_depth: int = 4) -> List[List[str]]:
        """Find all paths between two nodes up to max_depth."""
        all_paths = []
        
        def dfs(current: str, target: str, path: List[str], visited: Set[str]):
            if len(path) > max_depth:
                return
            
            if current == target:
                all_paths.append(path[:])
                return
            
            for neighbor in self.get_neighbors(current, direction="out"):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, target, path, visited)
                    path.pop()
                    visited.remove(neighbor)
        
        dfs(start_id, end_id, [start_id], {start_id})
        return all_paths
    
    # ─────────────────────────────────────────────────────────────
    # Transitive Closure
    # ─────────────────────────────────────────────────────────────
    
    def get_reachable_nodes(self, start_id: str, max_depth: int = 5) -> Dict[str, int]:
        """
        Get all nodes reachable from start_id with their distances.
        Returns dict of {node_id: distance}.
        """
        reachable = {start_id: 0}
        queue = [(start_id, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            for neighbor in self.get_neighbors(current, direction="out"):
                if neighbor not in reachable:
                    reachable[neighbor] = depth + 1
                    queue.append((neighbor, depth + 1))
        
        return reachable
    
    # ─────────────────────────────────────────────────────────────
    # Filtered Queries
    # ─────────────────────────────────────────────────────────────
    
    def get_rules_by_type(self, rule_type: str = "all") -> List[Dict]:
        """Get rules filtered by type: 'hard', 'soft', or 'all'."""
        rules = self.rules
        
        if rule_type.lower() == "hard":
            rules = [r for r in rules if r["type"] == "Law_Hard"]
        elif rule_type.lower() == "soft":
            rules = [r for r in rules if r["type"] == "Heuristic_Soft"]
        
        return sorted(rules, key=lambda x: x.get("weight", 0), reverse=True)
    
    def get_mechanisms_by_type(self, mech_type: str = "all") -> List[Dict]:
        """Get mechanisms filtered by type: 'risk', 'financial', or 'all'."""
        mechanisms = self.mechanisms
        
        if mech_type.lower() == "risk":
            mechanisms = [m for m in mechanisms if m["type"] == "Risk_Mechanism"]
        elif mech_type.lower() == "financial":
            mechanisms = [m for m in mechanisms if m["type"] == "Financial_Mechanism"]
        
        return mechanisms
    
    # ─────────────────────────────────────────────────────────────
    # Search
    # ─────────────────────────────────────────────────────────────
    
    def search_by_keywords(self, keywords: List[str], collections: List[str] = None) -> List[Dict]:
        """
        Search nodes by keyword matching across specified collections.
        Returns nodes with match scores.
        """
        if collections is None:
            collections = ["cases", "precedents", "actions", "mechanisms"]
        
        results = []
        keywords_lower = [k.lower() for k in keywords]
        
        for collection in collections:
            for node in self._knowledge_base.get(collection, []):
                tags = [t.lower() for t in node.get("tags", [])]
                node_keywords = [k.lower() for k in node.get("keywords", [])]
                searchable = tags + node_keywords
                
                matches = sum(1 for k in keywords_lower if any(k in s for s in searchable))
                
                if matches > 0:
                    result = dict(node)
                    result["match_score"] = matches / len(keywords)
                    result["_collection"] = collection
                    results.append(result)
        
        return sorted(results, key=lambda x: x["match_score"], reverse=True)


# Global singleton accessor
def get_knowledge_service() -> KnowledgeService:
    """Get the singleton KnowledgeService instance."""
    return KnowledgeService()
