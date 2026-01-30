"""
Crisis Manager - Configuration v3.2
Externalized constants and configuration for the crisis management system.
"""

from typing import Dict, Any


class CrisisConfig:
    """Centralized configuration for Crisis Manager."""
    
    # Financial defaults (in USD)
    BASE_PENALTY_ESTIMATE: int = 1_000_000
    INSURANCE_LOSS_DEFAULT: int = 20_000_000
    
    # Risk multipliers
    CONCEALMENT_MULTIPLIER: float = 3.5
    
    # Risk score thresholds
    RISK_CRITICAL_THRESHOLD: float = 7.0
    RISK_HIGH_THRESHOLD: float = 5.0
    
    # Search configuration
    MAX_SEARCH_RESULTS: int = 7
    MIN_MATCH_SCORE: float = 0.1
    
    # Keyword scoring weights
    HIGH_FINANCIAL_KEYWORDS: list = [
        "million", "bankruptcy", "critical", "40%", "major", "insurance"
    ]
    HIGH_ETHICAL_KEYWORDS: list = [
        "fraud", "corruption", "deception", "lie", "steal", "bribe", "conceal", "hide"
    ]
    HIGH_LEGAL_KEYWORDS: list = [
        "criminal", "felony", "gdpr", "sanction", "lawsuit", "prison", "72h"
    ]
    
    # Concealment trigger keywords
    CONCEALMENT_KEYWORDS: list = [
        "conceal", "hide", "delay", "cover up", "wait", "disguise"
    ]
    
    # Insurance void trigger keywords
    INSURANCE_VOID_KEYWORDS: list = [
        "delay", "wait", "2 week", "72h", "insurance"
    ]
    
    # Rule weight hierarchy
    LAW_HARD_WEIGHT: int = 10
    HEURISTIC_SOFT_MAX_WEIGHT: int = 9
    HEURISTIC_SOFT_MIN_WEIGHT: int = 4
    
    @classmethod
    def get_risk_level(cls, total_risk: float) -> str:
        """Determine risk level from score."""
        if total_risk > cls.RISK_CRITICAL_THRESHOLD:
            return "CRITICAL"
        elif total_risk > cls.RISK_HIGH_THRESHOLD:
            return "HIGH"
        return "MEDIUM"
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "base_penalty_estimate": cls.BASE_PENALTY_ESTIMATE,
            "insurance_loss_default": cls.INSURANCE_LOSS_DEFAULT,
            "concealment_multiplier": cls.CONCEALMENT_MULTIPLIER,
            "risk_thresholds": {
                "critical": cls.RISK_CRITICAL_THRESHOLD,
                "high": cls.RISK_HIGH_THRESHOLD
            }
        }
