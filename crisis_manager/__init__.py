"""
Crisis Manager - CrewAI Package v3.2
Enhanced with shared services and memory layer.
"""

from .crew import CrisisManagerCrew
from .agents import create_scientist_agent, create_compliance_agent, create_judge_agent
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
from .knowledge_service import KnowledgeService, get_knowledge_service
from .memory_service import MemoryService, get_memory_service
from .config import CrisisConfig

__all__ = [
    # Crew
    "CrisisManagerCrew",
    # Agents
    "create_scientist_agent",
    "create_compliance_agent", 
    "create_judge_agent",
    # Tools
    "GraphSearchTool",
    "RuleLookupTool",
    "RiskCalculatorTool",
    "EdgeTraversalTool",
    "MechanismLookupTool",
    "CausalChainTool",
    "PathFinderTool",
    "ReachabilityTool",
    # Services
    "KnowledgeService",
    "get_knowledge_service",
    "MemoryService",
    "get_memory_service",
    # Config
    "CrisisConfig"
]
