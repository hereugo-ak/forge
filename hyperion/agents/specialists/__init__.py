"""Specialist agents — 12 domain experts with proprietary analytical skills."""

from hyperion.agents.specialists.competitive_intel import CompetitiveIntel, COMPETITIVE_INTEL_SPEC
from hyperion.agents.specialists.consumer_insights import ConsumerInsightsAnalyst, CONSUMER_INSIGHTS_SPEC
from hyperion.agents.specialists.financial_analyst import FinancialAnalyst, FINANCIAL_ANALYST_SPEC
from hyperion.agents.specialists.innovation_analyst import InnovationAnalyst, INNOVATION_ANALYST_SPEC
from hyperion.agents.specialists.ma_analyst import MAAnalyst, MA_ANALYST_SPEC
from hyperion.agents.specialists.market_analyst import MarketAnalyst, MARKET_ANALYST_SPEC
from hyperion.agents.specialists.operations_analyst import OperationsAnalyst, OPERATIONS_ANALYST_SPEC
from hyperion.agents.specialists.regulatory_analyst import RegulatoryAnalyst, REGULATORY_ANALYST_SPEC
from hyperion.agents.specialists.risk_analyst import RiskAnalyst, RISK_ANALYST_SPEC
from hyperion.agents.specialists.strategy_analyst import StrategyAnalyst, STRATEGY_ANALYST_SPEC
from hyperion.agents.specialists.sustainability_analyst import SustainabilityAnalyst, SUSTAINABILITY_ANALYST_SPEC
from hyperion.agents.specialists.technology_analyst import TechnologyAnalyst, TECHNOLOGY_ANALYST_SPEC

__all__ = [
    "MarketAnalyst",
    "MARKET_ANALYST_SPEC",
    "CompetitiveIntel",
    "COMPETITIVE_INTEL_SPEC",
    "FinancialAnalyst",
    "FINANCIAL_ANALYST_SPEC",
    "RiskAnalyst",
    "RISK_ANALYST_SPEC",
    "TechnologyAnalyst",
    "TECHNOLOGY_ANALYST_SPEC",
    "OperationsAnalyst",
    "OPERATIONS_ANALYST_SPEC",
    "RegulatoryAnalyst",
    "REGULATORY_ANALYST_SPEC",
    "SustainabilityAnalyst",
    "SUSTAINABILITY_ANALYST_SPEC",
    "ConsumerInsightsAnalyst",
    "CONSUMER_INSIGHTS_SPEC",
    "MAAnalyst",
    "MA_ANALYST_SPEC",
    "InnovationAnalyst",
    "INNOVATION_ANALYST_SPEC",
    "StrategyAnalyst",
    "STRATEGY_ANALYST_SPEC",
]
