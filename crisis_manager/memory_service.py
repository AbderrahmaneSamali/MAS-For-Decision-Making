"""
Crisis Manager - Memory Service v3.2
Persistent storage for decision history and learning.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any


class MemoryService:
    """
    Service for persisting decision history and enabling learning from past decisions.
    
    Features:
    - Store decision outcomes with scenario fingerprints
    - Retrieve similar past decisions
    - Track precedent usage frequency
    - Enable feedback loop for future improvements
    """
    
    _instance: Optional['MemoryService'] = None
    _initialized: bool = False
    
    MEMORY_FILE = "decision_history.json"
    
    def __new__(cls) -> 'MemoryService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if MemoryService._initialized:
            return
        
        self._memory_path = os.path.join(os.path.dirname(__file__), self.MEMORY_FILE)
        self._history: Dict[str, Any] = self._load_history()
        MemoryService._initialized = True
    
    def _load_history(self) -> Dict[str, Any]:
        """Load existing decision history or create new."""
        if os.path.exists(self._memory_path):
            try:
                with open(self._memory_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "decisions": [],
            "precedent_usage": {},
            "feedback": []
        }
    
    def _save_history(self) -> None:
        """Persist decision history to file."""
        with open(self._memory_path, "w", encoding="utf-8") as f:
            json.dump(self._history, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _hash_scenario(scenario: str) -> str:
        """Create a fingerprint hash for a scenario."""
        normalized = " ".join(scenario.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    # ─────────────────────────────────────────────────────────────
    # Decision Recording
    # ─────────────────────────────────────────────────────────────
    
    def record_decision(
        self,
        scenario: str,
        verdict: str,
        precedent_used: Optional[str] = None,
        risk_scores: Optional[Dict[str, float]] = None,
        rules_cited: Optional[List[str]] = None,
        confidence: Optional[float] = None
    ) -> str:
        """
        Record a decision for future reference.
        Returns the decision ID.
        """
        decision_id = f"DEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        decision = {
            "id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "scenario_hash": self._hash_scenario(scenario),
            "scenario_preview": scenario[:200] + "..." if len(scenario) > 200 else scenario,
            "verdict": verdict,
            "precedent_used": precedent_used,
            "risk_scores": risk_scores or {},
            "rules_cited": rules_cited or [],
            "confidence": confidence
        }
        
        self._history["decisions"].append(decision)
        
        # Track precedent usage
        if precedent_used:
            usage = self._history["precedent_usage"]
            usage[precedent_used] = usage.get(precedent_used, 0) + 1
        
        self._save_history()
        return decision_id
    
    def add_feedback(self, decision_id: str, outcome: str, notes: str = "") -> None:
        """
        Add feedback on a past decision for learning.
        
        Args:
            decision_id: ID of the decision
            outcome: "correct", "incorrect", or "partially_correct"
            notes: Additional context
        """
        feedback = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "outcome": outcome,
            "notes": notes
        }
        
        self._history["feedback"].append(feedback)
        self._save_history()
    
    # ─────────────────────────────────────────────────────────────
    # Retrieval
    # ─────────────────────────────────────────────────────────────
    
    def get_similar_decisions(self, scenario: str, limit: int = 5) -> List[Dict]:
        """
        Find past decisions with similar scenarios.
        Uses keyword overlap for similarity (simple approach).
        """
        scenario_words = set(scenario.lower().split())
        results = []
        
        for decision in self._history["decisions"]:
            preview_words = set(decision.get("scenario_preview", "").lower().split())
            overlap = len(scenario_words & preview_words)
            
            if overlap > 3:  # Minimum overlap threshold
                decision_copy = dict(decision)
                decision_copy["similarity_score"] = overlap / len(scenario_words)
                results.append(decision_copy)
        
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]
    
    def get_precedent_stats(self) -> Dict[str, int]:
        """Get usage statistics for precedents."""
        return dict(self._history["precedent_usage"])
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get most recent decisions."""
        return self._history["decisions"][-limit:][::-1]
    
    def get_decision_by_id(self, decision_id: str) -> Optional[Dict]:
        """Get a specific decision by ID."""
        for decision in self._history["decisions"]:
            if decision["id"] == decision_id:
                return decision
        return None
    
    # ─────────────────────────────────────────────────────────────
    # Analytics
    # ─────────────────────────────────────────────────────────────
    
    def get_verdict_distribution(self) -> Dict[str, int]:
        """Get distribution of verdicts (APPROVE/REJECT)."""
        distribution = {}
        for decision in self._history["decisions"]:
            verdict = decision.get("verdict", "UNKNOWN")
            distribution[verdict] = distribution.get(verdict, 0) + 1
        return distribution
    
    def get_feedback_accuracy(self) -> float:
        """Calculate accuracy based on feedback."""
        if not self._history["feedback"]:
            return 0.0
        
        correct = sum(1 for f in self._history["feedback"] if f["outcome"] == "correct")
        return correct / len(self._history["feedback"])


# Global singleton accessor
def get_memory_service() -> MemoryService:
    """Get the singleton MemoryService instance."""
    return MemoryService()
