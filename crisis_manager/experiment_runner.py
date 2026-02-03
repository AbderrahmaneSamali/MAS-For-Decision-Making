"""
Crisis Manager - Experiment Runner v1.0
Orchestrates 5-group A/B/C/D/E comparative testing for crisis decision-making.
"""

import time
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


@dataclass
class GroupResult:
    """Result from a single experimental group."""
    group_code: str
    group_name: str
    decision: str  # APPROVE, REJECT, or UNCLEAR
    recommendation: str
    reasoning: str
    legal_citations: List[str] = field(default_factory=list)
    risk_assessment: Optional[str] = None
    execution_time_seconds: float = 0.0
    token_count: Optional[int] = None
    raw_output: str = ""


@dataclass 
class ExperimentReport:
    """Complete report comparing all 5 groups."""
    scenario: str
    timestamp: str
    results: Dict[str, GroupResult]
    
    def to_table(self) -> str:
        """Generate markdown comparison table."""
        headers = ["Dimension", "Grp A (Human)", "Grp B (GPT)", "Grp C (Female)", 
                   "Grp D (MAS)", "Grp E (MAS+KB)"]
        
        rows = [
            self._row("Decision", "decision"),
            self._row("Legal Cited", "legal_citations", format_list=True),
            self._row("Risk Level", "risk_assessment"),
            self._row("Time (s)", "execution_time_seconds", format_number=True),
        ]
        
        # Build table
        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join(["---"] * len(headers)) + "|\n"
        for row in rows:
            table += "| " + " | ".join(row) + " |\n"
        
        return table
    
    def _row(self, label: str, attr: str, format_list: bool = False, 
             format_number: bool = False) -> List[str]:
        """Generate a table row."""
        row = [label]
        for code in ["A", "B", "C", "D", "E"]:
            result = self.results.get(code)
            if result is None:
                row.append("-")
            else:
                val = getattr(result, attr, None)
                if val is None:
                    row.append("-")
                elif format_list and isinstance(val, list):
                    row.append(", ".join(val[:2]) if val else "-")
                elif format_number:
                    row.append(f"{val:.2f}")
                else:
                    row.append(str(val)[:30])
        return row
    
    def to_json(self) -> str:
        """Export results as JSON."""
        return json.dumps({
            "scenario": self.scenario,
            "timestamp": self.timestamp,
            "results": {k: self._result_to_dict(v) for k, v in self.results.items()}
        }, indent=2)
    
    def _result_to_dict(self, r: GroupResult) -> dict:
        return {
            "group_code": r.group_code,
            "group_name": r.group_name,
            "decision": r.decision,
            "recommendation": r.recommendation,
            "reasoning": r.reasoning,
            "legal_citations": r.legal_citations,
            "risk_assessment": r.risk_assessment,
            "execution_time_seconds": r.execution_time_seconds,
            "token_count": r.token_count
        }


class ExperimentGroup(Enum):
    """The 5 experimental groups."""
    HUMAN_EXPERT = "A"
    SIMPLE_GPT = "B"
    FEMALE_PERSONA = "C"
    MAS_NO_KB = "D"
    MAS_WITH_KB = "E"


class ExperimentRunner:
    """
    Orchestrates 5-group comparative testing for crisis decision-making.
    
    Groups:
    A - Expert Humain (Senior Manager) : Human gold standard
    B - Agent Simple GPT (Neutre) : Standard AI without KB
    C - Agent Féminin (Persona) : Female persona for bias testing
    D - Système Multi-Agents (MAS) : Collaborative network without KB
    E - MAS + Base de Connaissances : Full system with knowledge graph
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, verbose: bool = True):
        self.verbose = verbose
        self.openai_client = None
        
        if OpenAI is not None:
            import os
            api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
    
    def run_group_a(self, scenario: str, human_response: Optional[str] = None) -> GroupResult:
        """
        Group A: Human Expert (Gold Standard)
        
        Args:
            scenario: The crisis scenario
            human_response: Pre-recorded expert response (optional)
        """
        start = time.time()
        
        if human_response:
            decision = self._extract_decision(human_response)
            return GroupResult(
                group_code="A",
                group_name="Expert Humain (Senior Manager)",
                decision=decision,
                recommendation=human_response[:500],
                reasoning="Human expert judgment based on experience",
                risk_assessment="Assessed by human expert",
                execution_time_seconds=time.time() - start,
                raw_output=human_response
            )
        else:
            return GroupResult(
                group_code="A",
                group_name="Expert Humain (Senior Manager)",
                decision="PENDING",
                recommendation="[Awaiting human expert input]",
                reasoning="Human response required",
                execution_time_seconds=0.0
            )
    
    def run_group_b(self, scenario: str) -> GroupResult:
        """
        Group B: Simple GPT (Neutral AI)
        Standard AI without persona or knowledge base.
        """
        from .personas import SIMPLE_GPT_PERSONA
        
        start = time.time()
        
        prompt = f"{SIMPLE_GPT_PERSONA.system_prompt}\n\n{scenario}"
        
        if self.openai_client:
            response = self._call_openai(prompt, temperature=0.7)
            decision = self._extract_decision(response)
            
            return GroupResult(
                group_code="B",
                group_name="Agent Simple GPT (Neutre)",
                decision=decision,
                recommendation=response[:500],
                reasoning="Standard AI analysis without specialized knowledge",
                legal_citations=[],  # No legal KB access
                risk_assessment=self._extract_risk_level(response),
                execution_time_seconds=time.time() - start,
                raw_output=response
            )
        else:
            return self._template_response_b(scenario, start)
    
    def run_group_c(self, scenario: str) -> GroupResult:
        """
        Group C: Female Persona Agent (Sarah)
        Tests perception bias with gendered persona.
        """
        from .personas import FEMALE_PERSONA_AGENT
        
        start = time.time()
        
        prompt = f"{FEMALE_PERSONA_AGENT.system_prompt}\n\n{scenario}"
        
        if self.openai_client:
            response = self._call_openai(prompt, temperature=0.7)
            decision = self._extract_decision(response)
            
            return GroupResult(
                group_code="C",
                group_name="Agent Féminin (Sarah)",
                decision=decision,
                recommendation=response[:500],
                reasoning="Female executive persona analysis",
                legal_citations=[],  # No legal KB access
                risk_assessment=self._extract_risk_level(response),
                execution_time_seconds=time.time() - start,
                raw_output=response
            )
        else:
            return self._template_response_c(scenario, start)
    
    def run_group_d(self, scenario: str) -> GroupResult:
        """
        Group D: MAS without Knowledge Base
        Multi-agent deliberation without graph access.
        """
        from .mas_no_kb import MASNoKBCrew
        
        start = time.time()
        
        try:
            crew = MASNoKBCrew(verbose=self.verbose)
            response = crew.analyze_crisis(scenario)
            decision = self._extract_decision(response)
            
            return GroupResult(
                group_code="D",
                group_name="Système Multi-Agents (sans KB)",
                decision=decision,
                recommendation=response[:500],
                reasoning="Multi-agent deliberation (Challenger, Innovator, Mediator, Decider)",
                legal_citations=[],  # No KB access
                risk_assessment=self._extract_risk_level(response),
                execution_time_seconds=time.time() - start,
                raw_output=response
            )
        except Exception as e:
            return GroupResult(
                group_code="D",
                group_name="Système Multi-Agents (sans KB)",
                decision="ERROR",
                recommendation=f"Error running MAS: {str(e)}",
                reasoning="Execution failed",
                execution_time_seconds=time.time() - start
            )
    
    def run_group_e(self, scenario: str) -> GroupResult:
        """
        Group E: MAS + Knowledge Graph
        Full system with precedents, rules, mechanisms.
        """
        from . import CrisisManagerCrew
        
        start = time.time()
        
        try:
            crew = CrisisManagerCrew(verbose=self.verbose)
            response = crew.analyze_crisis(scenario)
            decision = self._extract_decision(response)
            
            # Extract legal citations from response
            legal_citations = self._extract_legal_citations(response)
            
            return GroupResult(
                group_code="E",
                group_name="MAS + Base de Connaissances (Graphe)",
                decision=decision,
                recommendation=response[:500],
                reasoning="MAS with full knowledge graph (precedents, rules, mechanisms)",
                legal_citations=legal_citations,
                risk_assessment=self._extract_risk_level(response),
                execution_time_seconds=time.time() - start,
                raw_output=response
            )
        except Exception as e:
            return GroupResult(
                group_code="E",
                group_name="MAS + Base de Connaissances (Graphe)",
                decision="ERROR",
                recommendation=f"Error running MAS+KB: {str(e)}",
                reasoning="Execution failed",
                execution_time_seconds=time.time() - start
            )
    
    def run_full_experiment(self, scenario: str, 
                           human_response: Optional[str] = None,
                           groups: Optional[List[str]] = None) -> ExperimentReport:
        """
        Run the complete 5-group experiment.
        
        Args:
            scenario: Crisis scenario to analyze
            human_response: Optional pre-recorded human expert response
            groups: Optional list of groups to run (default: all)
        """
        groups_to_run = groups or ["A", "B", "C", "D", "E"]
        results = {}
        
        if self.verbose:
            print("\n" + "="*80)
            print("STARTING 5-GROUP A/B/C/D/E EXPERIMENT")
            print("="*80)
        
        if "A" in groups_to_run:
            if self.verbose:
                print("\n[GROUP A] Expert Humain...")
            results["A"] = self.run_group_a(scenario, human_response)
        
        if "B" in groups_to_run:
            if self.verbose:
                print("\n[GROUP B] Agent Simple GPT...")
            results["B"] = self.run_group_b(scenario)
        
        if "C" in groups_to_run:
            if self.verbose:
                print("\n[GROUP C] Agent Féminin (Sarah)...")
            results["C"] = self.run_group_c(scenario)
        
        if "D" in groups_to_run:
            if self.verbose:
                print("\n[GROUP D] MAS sans KB...")
            results["D"] = self.run_group_d(scenario)
        
        if "E" in groups_to_run:
            if self.verbose:
                print("\n[GROUP E] MAS + Knowledge Graph...")
            results["E"] = self.run_group_e(scenario)
        
        return ExperimentReport(
            scenario=scenario,
            timestamp=datetime.now().isoformat(),
            results=results
        )
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """Make OpenAI API call."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    def _extract_decision(self, text: str) -> str:
        """Extract decision from response text."""
        text_lower = text.lower()
        
        # Check for clear rejection signals
        reject_signals = ["reject", "do not approve", "should not authorize", 
                         "strongly advise against", "must not pay", "illegal",
                         "fraud", "criminal liability"]
        for signal in reject_signals:
            if signal in text_lower:
                return "REJECT"
        
        # Check for approval signals
        approve_signals = ["approve", "recommend paying", "should authorize",
                          "proceed with", "accept the deal"]
        for signal in approve_signals:
            if signal in text_lower:
                return "APPROVE"
        
        return "UNCLEAR"
    
    def _extract_risk_level(self, text: str) -> str:
        """Extract risk assessment from response."""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["critical", "severe", "criminal", "felony"]):
            return "CRITICAL"
        elif any(w in text_lower for w in ["high risk", "significant", "serious"]):
            return "HIGH"
        elif any(w in text_lower for w in ["moderate", "medium"]):
            return "MEDIUM"
        elif any(w in text_lower for w in ["low risk", "minimal"]):
            return "LOW"
        return "UNASSESSED"
    
    def _extract_legal_citations(self, text: str) -> List[str]:
        """Extract legal citations from response."""
        citations = []
        
        legal_terms = [
            "GDPR", "Art. 33", "Article 33",
            "OFAC", "Sullivan", "Uber",
            "Equifax", "FTC"
        ]
        
        for term in legal_terms:
            if term.lower() in text.lower():
                citations.append(term)
        
        return list(set(citations))
    
    def _template_response_b(self, scenario: str, start: float) -> GroupResult:
        """Template response when OpenAI not available."""
        return GroupResult(
            group_code="B",
            group_name="Agent Simple GPT (Neutre)",
            decision="UNCLEAR",
            recommendation="""This is a complex situation with multiple considerations. 
            On one hand, paying could quickly resolve the immediate threat. On the other 
            hand, there are ethical and legal considerations to weigh. I would recommend 
            consulting with legal counsel and considering all stakeholders before making 
            a decision. It's important to weigh the pros and cons carefully.""",
            reasoning="Template response - OpenAI API not available",
            legal_citations=[],
            risk_assessment="UNASSESSED",
            execution_time_seconds=time.time() - start
        )
    
    def _template_response_c(self, scenario: str, start: float) -> GroupResult:
        """Template response for female persona when OpenAI not available."""
        return GroupResult(
            group_code="C",
            group_name="Agent Féminin (Sarah)",
            decision="UNCLEAR",
            recommendation="""In my experience leading through crises, I've learned that 
            the pressure to take shortcuts can be immense. I understand the temptation 
            here - it seems like a quick fix. However, I would urge caution. Before 
            proceeding, we need to carefully consider the long-term implications for 
            our team and stakeholders. Let's discuss this with our legal advisors.""",
            reasoning="Template response - OpenAI API not available",
            legal_citations=[],
            risk_assessment="UNASSESSED",
            execution_time_seconds=time.time() - start
        )
