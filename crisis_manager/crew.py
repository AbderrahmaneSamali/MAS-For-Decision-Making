"""
Crisis Manager - CrewAI Crew Orchestrator
Main crew that coordinates the multi-agent decision-making process.
"""

from crewai import Crew, Task, Process
from .agents import create_scientist_agent, create_compliance_agent, create_judge_agent


class CrisisManagerCrew:
    """
    Orchestrates the Crisis Manager multi-agent system.
    
    The crew follows a sequential process:
    1. Scientist Agent: Analyzes scenario and finds precedents
    2. Compliance Agent: Evaluates legal/ethical risks
    3. Judge Agent: Synthesizes and delivers verdict
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.scientist = create_scientist_agent()
        self.compliance = create_compliance_agent()
        self.judge = create_judge_agent()
    
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
            4. Summarize the most relevant precedent and its outcome
            
            Provide a structured analysis with:
            - Matched Precedent ID and match score
            - Historical action taken and consequence
            - Connected rules (violated/complied)
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
            3. Identify which hard laws (weight 10) would be violated
            4. Identify which soft heuristics apply and their weights
            5. Flag any conflicts between pragmatism and compliance
            
            Provide a compliance assessment with:
            - Risk scores (Financial, Ethical, Legal)
            - Applicable rules ranked by weight
            - Clear compliance recommendation
            """,
            expected_output="""A compliance assessment containing:
            - Risk scores (0-10) for Financial, Ethical, Legal
            - List of applicable rules with weights
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
            3. Resolve any conflicts using rule weights (Law_Hard weight 10 > Heuristic_Soft)
            4. Deliver a clear APPROVE or REJECT verdict
            5. Provide specific action recommendations with deadlines
            
            Your verdict MUST include:
            - Clear decision (APPROVE/REJECT the proposed action)
            - Primary legal citation supporting the decision
            - Risk summary with scores
            - Ordered action plan with priorities
            """,
            expected_output="""A final verdict document containing:
            - DECISION: Clear APPROVE or REJECT
            - CITATION: Primary precedent and rules cited
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
        return str(result)
    
    def get_agents(self) -> list:
        """Return the list of agents in this crew."""
        return [self.scientist, self.compliance, self.judge]
    
    def get_agent_roles(self) -> dict:
        """Return a dictionary of agent roles and goals."""
        return {
            "Scientist": {
                "role": self.scientist.role,
                "goal": self.scientist.goal
            },
            "Compliance": {
                "role": self.compliance.role,
                "goal": self.compliance.goal
            },
            "Judge": {
                "role": self.judge.role,
                "goal": self.judge.goal
            }
        }
