"""
Crisis Manager - CrewAI Package v3.3
Enhanced with 5-group A/B/C/D/E comparative testing framework.
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

# New: Experiment modules for A/B/C/D/E testing
from .experiment_runner import ExperimentRunner, ExperimentReport, ExperimentGroup
from .mas_no_kb import MASNoKBCrew
from .personas import get_persona, get_group_description, get_mas_no_kb_personas

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
    "CrisisConfig",
    # Experiment Framework
    "ExperimentRunner",
    "ExperimentReport",
    "ExperimentGroup",
    "MASNoKBCrew",
    "get_persona",
    "get_group_description",
    "get_mas_no_kb_personas"
]
