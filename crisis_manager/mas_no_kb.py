"""
Crisis Manager - MAS without Knowledge Base v1.0
Multi-agent system for Group D testing - operates WITHOUT knowledge graph access.
"""

from crewai import Agent, Crew, Task, Process
from .personas import (
    MAS_CHALLENGER_NO_KB,
    MAS_INNOVATOR_NO_KB, 
    MAS_MEDIATOR_NO_KB,
    MAS_DECIDER_NO_KB
)


def create_challenger_agent() -> Agent:
    """Create the Challenger agent - questions assumptions."""
    persona = MAS_CHALLENGER_NO_KB
    return Agent(
        role=persona.role,
        goal="""Challenge assumptions, identify hidden risks, and surface potential 
        failure modes in the proposed crisis response. Play devil's advocate.""",
        backstory=persona.system_prompt,
        verbose=True,
        allow_delegation=False
    )


def create_innovator_agent() -> Agent:
    """Create the Innovator agent - generates creative solutions."""
    persona = MAS_INNOVATOR_NO_KB
    return Agent(
        role=persona.role,
        goal="""Generate creative alternative solutions to the crisis. Think beyond 
        conventional approaches and propose novel risk mitigation strategies.""",
        backstory=persona.system_prompt,
        verbose=True,
        allow_delegation=False
    )


def create_mediator_agent() -> Agent:
    """Create the Mediator agent - synthesizes viewpoints."""
    persona = MAS_MEDIATOR_NO_KB
    return Agent(
        role=persona.role,
        goal="""Synthesize different perspectives from the team. Find common ground, 
        integrate conflicting viewpoints, and build consensus toward a decision.""",
        backstory=persona.system_prompt,
        verbose=True,
        allow_delegation=False
    )


def create_decider_agent() -> Agent:
    """Create the Decider agent - makes final decision."""
    persona = MAS_DECIDER_NO_KB
    return Agent(
        role=persona.role,
        goal="""Make the final decision after considering all perspectives. 
        Clearly articulate the rationale and define concrete next steps.""",
        backstory=persona.system_prompt,
        verbose=True,
        allow_delegation=False
    )


class MASNoKBCrew:
    """
    Multi-Agent System without Knowledge Base access.
    
    Used for Group D testing - demonstrates MAS collaboration
    WITHOUT the structured knowledge graph containing:
    - Legal precedents
    - Regulatory rules
    - Risk mechanisms
    - Case dilemmas
    
    This allows comparison with Group E (full MAS+KB) to measure
    the value added by the knowledge graph.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.challenger = create_challenger_agent()
        self.innovator = create_innovator_agent()
        self.mediator = create_mediator_agent()
        self.decider = create_decider_agent()
    
    def analyze_crisis(self, scenario: str) -> str:
        """
        Analyze a crisis scenario using the 4-agent deliberation process.
        
        Process:
        1. Challenger identifies risks and questions
        2. Innovator proposes creative alternatives
        3. Mediator synthesizes perspectives
        4. Decider makes final recommendation
        """
        
        # Task 1: Challenge assumptions
        challenge_task = Task(
            description=f"""Analyze the following crisis scenario and identify:
            1. Hidden risks that might be overlooked
            2. Assumptions that should be questioned
            3. Potential failure modes of proposed solutions
            4. Questions that must be answered before deciding
            
            SCENARIO:
            {scenario}
            
            Provide your critical analysis as the Challenger.""",
            expected_output="""A critical analysis including:
            - Key risks identified
            - Questioned assumptions
            - Potential failure modes
            - Critical questions to address""",
            agent=self.challenger
        )
        
        # Task 2: Generate alternatives
        innovate_task = Task(
            description=f"""Based on the Challenger's analysis, generate creative 
            alternative solutions to this crisis:
            
            SCENARIO:
            {scenario}
            
            Think beyond conventional approaches. Consider:
            1. Novel risk mitigation strategies
            2. Creative stakeholder engagement
            3. Alternative framing of the problem
            4. Unconventional but ethical solutions""",
            expected_output="""Creative alternatives including:
            - At least 3 alternative approaches
            - Pros and cons of each
            - Implementation considerations""",
            agent=self.innovator,
            context=[challenge_task]
        )
        
        # Task 3: Synthesize perspectives
        mediate_task = Task(
            description=f"""Synthesize the Challenger's risks and the Innovator's 
            alternatives into a coherent analysis:
            
            SCENARIO:
            {scenario}
            
            Your synthesis should:
            1. Acknowledge valid concerns from the Challenger
            2. Evaluate feasibility of Innovator's alternatives
            3. Find common ground between perspectives
            4. Prepare a balanced brief for the Decider""",
            expected_output="""A balanced synthesis including:
            - Key points of agreement
            - Remaining tensions to resolve
            - Recommended path forward with rationale""",
            agent=self.mediator,
            context=[challenge_task, innovate_task]
        )
        
        # Task 4: Final decision
        decide_task = Task(
            description=f"""As the Decider, review the team's analysis and make 
            the final recommendation:
            
            SCENARIO:
            {scenario}
            
            Your decision must:
            1. Clearly state APPROVE or REJECT with rationale
            2. Acknowledge key risks and how they're addressed
            3. Define concrete next steps
            4. Assign accountability for implementation""",
            expected_output="""FINAL DECISION including:
            - Clear verdict: APPROVE or REJECT
            - Rationale based on team analysis
            - Risk mitigation measures
            - Immediate next steps with owners""",
            agent=self.decider,
            context=[challenge_task, innovate_task, mediate_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.challenger, self.innovator, self.mediator, self.decider],
            tasks=[challenge_task, innovate_task, mediate_task, decide_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        return str(result)
    
    def get_agent_roles(self) -> dict:
        """Return agent role descriptions."""
        return {
            "challenger": {
                "name": "Alex",
                "role": "Challenger",
                "function": "Questions assumptions and surfaces risks"
            },
            "innovator": {
                "name": "Maya", 
                "role": "Innovator",
                "function": "Generates creative alternative solutions"
            },
            "mediator": {
                "name": "Jordan",
                "role": "Mediator", 
                "function": "Synthesizes viewpoints and builds consensus"
            },
            "decider": {
                "name": "Morgan",
                "role": "Decider",
                "function": "Makes final decision with accountability"
            }
        }
