"""
Experiment Evaluation Module v1.0
Evaluates and scores crisis decision experiment results.

Metrics:
1. Decision Quality - Did the group reach a clear verdict?
2. Legal Grounding - Were relevant laws/precedents cited?
3. Risk Assessment - Was risk properly identified and quantified?
4. Reasoning Depth - Quality of justification
5. Response Time - Efficiency of analysis
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class EvaluationCriteria:
    """Define expected outcomes for a scenario."""
    scenario_id: str
    expected_decision: str  # APPROVE, REJECT, or UNCLEAR
    required_legal_citations: List[str] = field(default_factory=list)
    required_risk_flags: List[str] = field(default_factory=list)
    min_acceptable_risk_level: str = "MEDIUM"  # MEDIUM, HIGH, CRITICAL
    key_concepts: List[str] = field(default_factory=list)


@dataclass
class GroupScore:
    """Score for a single experimental group."""
    group_code: str
    group_name: str
    
    # Individual scores (0-10)
    decision_score: float = 0.0
    legal_score: float = 0.0
    risk_score: float = 0.0
    reasoning_score: float = 0.0
    efficiency_score: float = 0.0
    
    # Overall
    total_score: float = 0.0
    grade: str = "F"
    
    # Details
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    def calculate_total(self, weights: Dict[str, float] = None):
        """Calculate weighted total score."""
        if weights is None:
            weights = {
                "decision": 0.25,
                "legal": 0.25,
                "risk": 0.20,
                "reasoning": 0.20,
                "efficiency": 0.10
            }
        
        self.total_score = (
            self.decision_score * weights["decision"] +
            self.legal_score * weights["legal"] +
            self.risk_score * weights["risk"] +
            self.reasoning_score * weights["reasoning"] +
            self.efficiency_score * weights["efficiency"]
        )
        
        # Assign grade
        if self.total_score >= 9:
            self.grade = "A+"
        elif self.total_score >= 8:
            self.grade = "A"
        elif self.total_score >= 7:
            self.grade = "B"
        elif self.total_score >= 6:
            self.grade = "C"
        elif self.total_score >= 5:
            self.grade = "D"
        else:
            self.grade = "F"


class ExperimentEvaluator:
    """Evaluates experiment results against criteria."""
    
    # Default evaluation criteria for common scenarios
    DEFAULT_CRITERIA = {
        "conflict_of_interest": EvaluationCriteria(
            scenario_id="conflict_of_interest",
            expected_decision="REJECT",  # Should reject keeping undisclosed conflict
            required_legal_citations=["GDPR", "ethics", "conflict"],
            required_risk_flags=["concealment", "conflict", "integrity"],
            min_acceptable_risk_level="HIGH",
            key_concepts=["disclosure", "transparency", "fiduciary duty", "corruption"]
        ),
        "ransomware_bounty": EvaluationCriteria(
            scenario_id="ransomware_bounty",
            expected_decision="REJECT",
            required_legal_citations=["GDPR", "Sullivan", "Uber", "OFAC"],
            required_risk_flags=["fraud", "concealment", "criminal"],
            min_acceptable_risk_level="CRITICAL",
            key_concepts=["72h", "mandatory reporting", "insurance void", "felony"]
        ),
        "nepotism": EvaluationCriteria(
            scenario_id="nepotism",
            expected_decision="REJECT",  # Should reject pure nepotism, but nuanced
            required_legal_citations=[],
            required_risk_flags=["favoritism", "team morale", "discrimination"],
            min_acceptable_risk_level="MEDIUM",
            key_concepts=["meritocracy", "team dynamics", "retention"]
        )
    }
    
    def __init__(self, criteria: Optional[EvaluationCriteria] = None):
        self.criteria = criteria
    
    def load_results(self, filepath: str) -> Dict[str, Any]:
        """Load experiment results from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def detect_scenario_type(self, scenario_text: str) -> str:
        """Auto-detect scenario type from text."""
        scenario_lower = scenario_text.lower()
        
        if any(kw in scenario_lower for kw in ["ransomware", "bug bounty", "hacker", "breach"]):
            return "ransomware_bounty"
        elif any(kw in scenario_lower for kw in ["conflit d'intérêt", "conflict of interest", "fournisseur", "supplier"]):
            return "conflict_of_interest"
        elif any(kw in scenario_lower for kw in ["fils", "son", "nepotism", "famille", "family"]):
            return "nepotism"
        else:
            return "unknown"
    
    def evaluate_group(self, result: Dict[str, Any], criteria: EvaluationCriteria) -> GroupScore:
        """Evaluate a single group's result."""
        score = GroupScore(
            group_code=result.get("group_code", "?"),
            group_name=result.get("group_name", "Unknown")
        )
        
        # 1. Decision Score (0-10)
        decision = result.get("decision", "UNCLEAR")
        if decision == criteria.expected_decision:
            score.decision_score = 10.0
            score.strengths.append(f"Correct decision: {decision}")
        elif decision == "UNCLEAR":
            score.decision_score = 3.0
            score.weaknesses.append("Failed to reach clear decision")
        else:
            score.decision_score = 2.0
            score.weaknesses.append(f"Wrong decision: {decision} (expected {criteria.expected_decision})")
        
        # 2. Legal Score (0-10)
        citations = result.get("legal_citations", [])
        recommendation = result.get("recommendation", "").lower()
        
        legal_matches = 0
        for required in criteria.required_legal_citations:
            if any(required.lower() in c.lower() for c in citations) or required.lower() in recommendation:
                legal_matches += 1
        
        if criteria.required_legal_citations:
            score.legal_score = min(10.0, (legal_matches / len(criteria.required_legal_citations)) * 10)
        else:
            # No specific citations required - check for any legal reasoning
            if citations:
                score.legal_score = 7.0
                score.strengths.append(f"Cited: {', '.join(citations)}")
            elif any(kw in recommendation for kw in ["law", "legal", "regulation", "policy", "loi", "juridique"]):
                score.legal_score = 5.0
            else:
                score.legal_score = 2.0
                score.weaknesses.append("No legal grounding")
        
        if citations:
            score.strengths.append(f"Legal citations: {', '.join(citations)}")
        
        # 3. Risk Assessment Score (0-10)
        risk_level = result.get("risk_assessment", "UNASSESSED")
        risk_hierarchy = {"UNASSESSED": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        min_level = risk_hierarchy.get(criteria.min_acceptable_risk_level, 2)
        actual_level = risk_hierarchy.get(risk_level, 0)
        
        if actual_level >= min_level:
            score.risk_score = min(10.0, 6.0 + (actual_level * 1.0))
            score.strengths.append(f"Appropriate risk level: {risk_level}")
        elif actual_level > 0:
            score.risk_score = actual_level * 2.0
            score.weaknesses.append(f"Underestimated risk: {risk_level}")
        else:
            score.risk_score = 0.0
            score.weaknesses.append("Failed to assess risk")
        
        # 4. Reasoning Score (0-10)
        reasoning_text = result.get("recommendation", "") + " " + result.get("reasoning", "")
        
        # Check for key concepts
        concept_matches = sum(1 for c in criteria.key_concepts if c.lower() in reasoning_text.lower())
        base_reasoning = min(6.0, len(reasoning_text) / 100)  # Length bonus (max 6)
        concept_bonus = min(4.0, concept_matches * 1.0)  # Concept bonus (max 4)
        score.reasoning_score = base_reasoning + concept_bonus
        
        if concept_matches > 0:
            score.strengths.append(f"Addressed {concept_matches} key concepts")
        
        # 5. Efficiency Score (0-10)
        exec_time = result.get("execution_time_seconds", 999)
        if exec_time < 10:
            score.efficiency_score = 10.0
        elif exec_time < 30:
            score.efficiency_score = 8.0
        elif exec_time < 60:
            score.efficiency_score = 6.0
        elif exec_time < 120:
            score.efficiency_score = 4.0
        else:
            score.efficiency_score = 2.0
        
        # Calculate total
        score.calculate_total()
        
        return score
    
    def evaluate_experiment(self, filepath: str, criteria: Optional[EvaluationCriteria] = None) -> Dict[str, GroupScore]:
        """Evaluate full experiment results."""
        data = self.load_results(filepath)
        
        # Auto-detect criteria if not provided
        if criteria is None:
            scenario_type = self.detect_scenario_type(data.get("scenario", ""))
            criteria = self.DEFAULT_CRITERIA.get(scenario_type, EvaluationCriteria(
                scenario_id="generic",
                expected_decision="REJECT",
                min_acceptable_risk_level="MEDIUM"
            ))
            print(f"[Auto-detected scenario type: {scenario_type}]")
        
        scores = {}
        for group_code, result in data.get("results", {}).items():
            scores[group_code] = self.evaluate_group(result, criteria)
        
        return scores
    
    def generate_report(self, scores: Dict[str, GroupScore]) -> str:
        """Generate evaluation report."""
        lines = []
        lines.append("=" * 70)
        lines.append("EXPERIMENT EVALUATION REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary table
        lines.append("SCORES BY GROUP:")
        lines.append("-" * 70)
        lines.append(f"{'Group':<30} {'Decision':>8} {'Legal':>7} {'Risk':>6} {'Reason':>7} {'Speed':>6} {'TOTAL':>7} {'Grade':>6}")
        lines.append("-" * 70)
        
        for code in sorted(scores.keys()):
            s = scores[code]
            lines.append(
                f"{s.group_name:<30} {s.decision_score:>8.1f} {s.legal_score:>7.1f} "
                f"{s.risk_score:>6.1f} {s.reasoning_score:>7.1f} {s.efficiency_score:>6.1f} "
                f"{s.total_score:>7.1f} {s.grade:>6}"
            )
        
        lines.append("-" * 70)
        lines.append("")
        
        # Winner
        winner = max(scores.values(), key=lambda x: x.total_score)
        lines.append(f"WINNER: {winner.group_name} (Grade: {winner.grade}, Score: {winner.total_score:.1f}/10)")
        lines.append("")
        
        # Detailed breakdown
        lines.append("=" * 70)
        lines.append("DETAILED ANALYSIS BY GROUP")
        lines.append("=" * 70)
        
        for code in sorted(scores.keys()):
            s = scores[code]
            lines.append(f"\n[{code}] {s.group_name}")
            lines.append(f"    Total Score: {s.total_score:.1f}/10 (Grade: {s.grade})")
            lines.append(f"    Components: Decision={s.decision_score:.0f}, Legal={s.legal_score:.0f}, Risk={s.risk_score:.0f}, Reasoning={s.reasoning_score:.0f}, Speed={s.efficiency_score:.0f}")
            if s.strengths:
                lines.append(f"    [+] Strengths: {'; '.join(s.strengths)}")
            if s.weaknesses:
                lines.append(f"    [-] Weaknesses: {'; '.join(s.weaknesses)}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


def main():
    """CLI for evaluating experiment results."""
    import sys
    
    print("\n" + "="*60)
    print("  EXPERIMENT RESULTS EVALUATOR")
    print("="*60 + "\n")
    
    # Find JSON files
    json_files = [f for f in os.listdir(".") if f.startswith("experiment_results") and f.endswith(".json")]
    
    if not json_files:
        print("No experiment result files found in current directory.")
        return
    
    print("Available result files:")
    for i, f in enumerate(json_files, 1):
        print(f"  {i}. {f}")
    
    choice = input(f"\nSelect file (1-{len(json_files)}): ").strip()
    try:
        idx = int(choice) - 1
        filepath = json_files[idx]
    except:
        filepath = json_files[-1]  # Default to most recent
    
    print(f"\nEvaluating: {filepath}")
    
    # Run evaluation
    evaluator = ExperimentEvaluator()
    scores = evaluator.evaluate_experiment(filepath)
    report = evaluator.generate_report(scores)
    
    print("\n" + report)
    
    # Save report
    report_file = filepath.replace(".json", "_evaluation.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
