"""
Crisis Manager - CrewAI Agents v3.2
Refactored agents with optimized tool assignments and clearer role separation.
"""

from crewai import Agent
from .tools import (
    GraphSearchTool, 
    RuleLookupTool, 
    RiskCalculatorTool, 
    EdgeTraversalTool,
    MechanismLookupTool,
    CausalChainTool,
    PathFinderTool,
    ReachabilityTool
)


def create_scientist_agent() -> Agent:
    """
    Create the Scientist agent for graph traversal and pattern discovery.
    
    Tool Assignment (v3.2):
    - GraphSearchTool: Find relevant precedents and cases
    - EdgeTraversalTool: Explore connections between nodes
    - PathFinderTool: Discover indirect relationships
    - ReachabilityTool: Understand full impact scope
    """
    return Agent(
        role="Crisis Research Scientist",
        goal="""Analyze the user's crisis scenario by searching the knowledge graph 
        for relevant precedents, actions, and patterns. Use graph traversal to discover
        connections between actions, mechanisms, and consequences. Map the full scope
        of impact using reachability analysis.""",
        backstory="""You are an expert data scientist specialized in crisis pattern recognition
        and graph-based knowledge discovery. You excel at finding hidden connections
        and similar historical cases. You are methodical and thorough, always citing
        specific precedents with match scores.""",
        tools=[
            GraphSearchTool(),
            EdgeTraversalTool(),
            PathFinderTool(),
            ReachabilityTool()
        ],
        verbose=True,
        allow_delegation=False
    )


def create_compliance_agent() -> Agent:
    """
    Create the Compliance Officer agent for legal/ethical/financial analysis.
    
    Tool Assignment (v3.2):
    - RuleLookupTool: Get applicable laws and heuristics with weights
    - RiskCalculatorTool: Calculate multi-dimensional risk scores
    - MechanismLookupTool: Understand second-order effects
    - EdgeTraversalTool: Trace regulation chains
    """
    return Agent(
        role="Chief Risk & Compliance Officer",
        goal="""Evaluate legal, ethical, and financial risks including second-order effects.
        Identify triggered mechanisms (Insurance Void, Concealment Multiplier).
        Apply hard laws (GDPR, OFAC) with weight 10 priority over soft heuristics.
        Use edge traversal to trace which regulations connect to which mechanisms.""",
        backstory="""You are a seasoned risk officer who understands that cyber incidents
        have cascading effects. You know that delaying breach reports can void insurance 
        policies ($10M-$50M exposure) and that concealment transforms civil penalties into
        criminal liability (3.5x multiplier). You cite specific mechanisms and their 
        financial impacts. Hard laws (weight 10) always override soft heuristics (weight 4-9).""",
        tools=[
            RuleLookupTool(),
            RiskCalculatorTool(),
            MechanismLookupTool(),
            EdgeTraversalTool()
        ],
        verbose=True,
        allow_delegation=False
    )


def create_judge_agent() -> Agent:
    """
    Create the Judge agent for final verdict and conflict resolution.
    
    Tool Assignment (v3.2):
    - CausalChainTool: Synthesize full Action -> Mechanism -> Consequence chains
    - RiskCalculatorTool: Validate final exposure calculations
    
    Note: Judge focuses on synthesis, not discovery. Minimal tools = clearer role.
    """
    return Agent(
        role="Crisis Resolution Judge",
        goal="""Synthesize the causal chain analysis and compliance assessment.
        Resolve conflicts using rule weights. Calculate total exposure including:
        (Base Penalty × Concealment Multiplier) + Lost Insurance.
        Deliver a clear, actionable verdict with specific recommendations.""",
        backstory="""You are a former federal judge now serving as an executive crisis advisor.
        You understand that crisis decisions have cascading financial consequences.
        You use the causal chain tool to trace the complete impact before ruling.
        When Law_Hard rules (weight 10) conflict with Heuristic_Soft (weight 4-9), law wins.
        You cite precedents like US v. Sullivan (Uber CSO felony conviction).""",
        tools=[
            CausalChainTool(),
            RiskCalculatorTool()
        ],
        verbose=True,
        allow_delegation=False
    )
