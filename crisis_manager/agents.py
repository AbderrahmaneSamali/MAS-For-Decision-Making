"""
Crisis Manager - CrewAI Agents v3.1
Three specialized agents with causal mechanism tracing capabilities.
"""

from crewai import Agent
from .tools import (
    GraphSearchTool, 
    RuleLookupTool, 
    RiskCalculatorTool, 
    EdgeTraversalTool,
    MechanismLookupTool,
    CausalChainTool
)


def create_scientist_agent() -> Agent:
    """Create the Scientist agent for graph traversal and causal chain tracing."""
    return Agent(
        role="Crisis Research Scientist",
        goal="""Analyze the user's crisis scenario by searching the knowledge graph 
        for relevant precedents, actions, and mechanisms. Trace the full causal chain:
        Action -> Mechanism -> Consequence. Extract key entities and find matching patterns.""",
        backstory="""You are an expert data scientist specialized in crisis pattern recognition
        and causal inference. You understand that actions trigger mechanisms which produce
        consequences. You trace the full causal chain using the knowledge graph.
        You are methodical and thorough, always citing specific precedents and mechanisms.""",
        tools=[GraphSearchTool(), EdgeTraversalTool(), CausalChainTool()],
        verbose=True,
        allow_delegation=False
    )


def create_compliance_agent() -> Agent:
    """Create the Compliance Officer agent for legal/ethical/financial analysis."""
    return Agent(
        role="Chief Risk & Compliance Officer",
        goal="""Evaluate legal, ethical, and financial risks including second-order effects.
        Identify triggered mechanisms (Insurance Void, Concealment Multiplier).
        Apply hard laws (GDPR, OFAC) with weight 10 priority over soft heuristics.""",
        backstory="""You are a seasoned risk officer who understands that cyber incidents
        have cascading effects. You know that delaying breach reports can void insurance 
        policies ($10M-$50M exposure) and that concealment transforms civil penalties into
        criminal liability (3.5x multiplier). You cite specific mechanisms and their 
        financial impacts. Hard laws (weight 10) always override soft heuristics (weight 4-9).""",
        tools=[RuleLookupTool(), RiskCalculatorTool(), MechanismLookupTool()],
        verbose=True,
        allow_delegation=False
    )


def create_judge_agent() -> Agent:
    """Create the Judge agent for final verdict and conflict resolution."""
    return Agent(
        role="Crisis Resolution Judge",
        goal="""Synthesize the causal chain analysis and compliance assessment.
        Resolve conflicts using rule weights. Calculate total exposure including:
        (Base Penalty × Concealment Multiplier) + Lost Insurance.
        Deliver a clear, actionable verdict with specific recommendations.""",
        backstory="""You are a former federal judge now serving as an executive crisis advisor.
        You understand that crisis decisions have cascading financial consequences.
        You use the causal chain to calculate total exposure before ruling.
        When Law_Hard rules (weight 10) conflict with Heuristic_Soft (weight 4-9), law wins.
        You cite precedents like US v. Sullivan (Uber CSO felony conviction).""",
        tools=[RuleLookupTool(), RiskCalculatorTool(), EdgeTraversalTool(), CausalChainTool(), MechanismLookupTool()],
        verbose=True,
        allow_delegation=False
    )
