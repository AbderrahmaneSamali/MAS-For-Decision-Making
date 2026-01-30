"""
Crisis Manager - CrewAI Crew Orchestrator v3.2
Enhanced with memory integration for decision history tracking.
"""

from crewai import Crew, Task, Process
from .agents import create_scientist_agent, create_compliance_agent, create_judge_agent
from .memory_service import get_memory_service


class CrisisManagerCrew:
    """
    Orchestrates the Crisis Manager multi-agent system.
    
    The crew follows a sequential process:
    1. Scientist Agent: Analyzes scenario and finds precedents using graph traversal
    2. Compliance Agent: Evaluates legal/ethical risks with mechanism analysis
    3. Judge Agent: Synthesizes causal chains and delivers verdict
    
    v3.2 Enhancements:
    - Memory service integration for decision history
    - Optimized tool assignments per agent role
    - O(1) graph lookups via KnowledgeService singleton
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.scientist = create_scientist_agent()
        self.compliance = create_compliance_agent()
        self.judge = create_judge_agent()
        self.memory = get_memory_service()
    
    def analyze_crisis(self, scenario: str) -> str:
        """
        Analyze a crisis scenario using the multi-agent system.
        
        Args:
            scenario: Description of the managerial crisis/dilemma
            
        Returns:
            Final verdict and recommendations from the Judge agent
        """
        # Task 1: Scientist analyzes and finds precedents
        research_task = Task(
            description=f"""Analyze the following crisis scenario and search the knowledge graph 
            for relevant precedents and similar cases.
            
            SCENARIO:
            {scenario}
            
            Your task:
            1. Extract key entities and keywords from the scenario
            2. Use the graph_search tool to find matching precedents
            3. Use the edge_traversal tool to find which rules those precedents violated or complied with
            4. Use path_finder to discover indirect relationships between entities
            5. Use reachability_analysis to understand the full impact scope
            6. Summarize the most relevant precedent and its outcome
            
            Provide a structured analysis with:
            - Matched Precedent ID and match score
            - Historical action taken and consequence
            - Connected rules (violated/complied)
            - Reachable impact nodes
            """,
            expected_output="""A structured analysis containing:
            - Primary matched precedent with ID and relevance score
            - Historical action and consequence
            - List of connected rules with relationships
            - Key insights for the compliance review""",
            agent=self.scientist
        )
        
        # Task 2: Compliance Officer evaluates risks
        compliance_task = Task(
            description=f"""Based on the research findings, evaluate the legal and ethical risks 
            of the proposed action in this scenario:
            
            SCENARIO:
            {scenario}
            
            Your task:
            1. Use the rule_lookup tool to get all applicable rules with their weights
            2. Use the risk_calculator tool to score Financial, Ethical, and Legal risks
            3. Use mechanism_lookup to identify second-order effects (insurance void, concealment multiplier)
            4. Use edge_traversal to trace which regulations connect to which mechanisms
            5. Identify which hard laws (weight 10) would be violated
            6. Identify which soft heuristics apply and their weights
            7. Flag any conflicts between pragmatism and compliance
            
            Provide a compliance assessment with:
            - Risk scores (Financial, Ethical, Legal)
            - Applicable rules ranked by weight
            - Triggered mechanisms and their effects
            - Clear compliance recommendation
            """,
            expected_output="""A compliance assessment containing:
            - Risk scores (0-10) for Financial, Ethical, Legal
            - List of applicable rules with weights
            - List of triggered mechanisms with multipliers
            - Identified rule conflicts
            - Preliminary compliance recommendation""",
            agent=self.compliance,
            context=[research_task]
        )
        
        # Task 3: Judge delivers final verdict
        judgment_task = Task(
            description=f"""As the final arbiter, synthesize the research and compliance analyses 
            to deliver a clear verdict on this crisis scenario:
            
            SCENARIO:
            {scenario}
            
            Your task:
            1. Review the precedent analysis from the Scientist
            2. Review the risk assessment from the Compliance Officer
            3. Use causal_chain_trace to trace Action -> Mechanism -> Consequence
            4. Use risk_calculator to validate the final exposure calculation
            5. Resolve any conflicts using rule weights (Law_Hard weight 10 > Heuristic_Soft)
            6. Deliver a clear APPROVE or REJECT verdict
            7. Provide specific action recommendations with deadlines
            
            Your verdict MUST include:
            - Clear decision (APPROVE/REJECT the proposed action)
            - Primary legal citation supporting the decision
            - Total exposure calculation: (Base Penalty × Multiplier) + Insurance Loss
            - Ordered action plan with priorities
            """,
            expected_output="""A final verdict document containing:
            - DECISION: Clear APPROVE or REJECT
            - CITATION: Primary precedent and rules cited
            - EXPOSURE: Total financial exposure calculation
            - RISK SUMMARY: Scores and total risk level
            - ACTION PLAN: Numbered steps with priorities and deadlines
            - CONFIDENCE: Score based on precedent match""",
            agent=self.judge,
            context=[research_task, compliance_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.scientist, self.compliance, self.judge],
            tasks=[research_task, compliance_task, judgment_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        result_str = str(result)
        
        # Record decision in memory
        self._record_decision(scenario, result_str)
        
        return result_str
    
    def _record_decision(self, scenario: str, result: str):
        """Record the decision in memory for future reference."""
        # Extract verdict from result
        verdict = "UNKNOWN"
        if "REJECT" in result.upper():
            verdict = "REJECT"
        elif "APPROVE" in result.upper():
            verdict = "APPROVE"
        
        # Extract precedent (simple heuristic)
        precedent_used = None
        if "UBER" in result.upper():
            precedent_used = "PRECEDENT_UBER_2016"
        elif "HYDRO" in result.upper():
            precedent_used = "PRECEDENT_HYDRO_2019"
        elif "COLONIAL" in result.upper():
            precedent_used = "PRECEDENT_COLONIAL_2021"
        elif "EQUIFAX" in result.upper():
            precedent_used = "PRECEDENT_EQUIFAX_2017"
        
        self.memory.record_decision(
            scenario=scenario,
            verdict=verdict,
            precedent_used=precedent_used
        )
    
    def get_similar_past_decisions(self, scenario: str, limit: int = 5):
        """Find similar past decisions for the given scenario."""
        return self.memory.get_similar_decisions(scenario, limit)
    
    def get_agents(self) -> list:
        """Return the list of agents in this crew."""
        return [self.scientist, self.compliance, self.judge]
    
    def get_agent_roles(self) -> dict:
        """Return a dictionary of agent roles and goals."""
        return {
            "Scientist": {
                "role": self.scientist.role,
                "goal": self.scientist.goal,
                "tools": [t.name for t in self.scientist.tools]
            },
            "Compliance": {
                "role": self.compliance.role,
                "goal": self.compliance.goal,
                "tools": [t.name for t in self.compliance.tools]
            },
            "Judge": {
                "role": self.judge.role,
                "goal": self.judge.goal,
                "tools": [t.name for t in self.judge.tools]
            }
        }
    
    def get_decision_stats(self) -> dict:
        """Get statistics about past decisions."""
        return {
            "verdict_distribution": self.memory.get_verdict_distribution(),
            "precedent_usage": self.memory.get_precedent_stats(),
            "recent_decisions": self.memory.get_recent_decisions(5)
        }
