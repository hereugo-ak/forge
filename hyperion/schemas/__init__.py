"""
HYPERION Schemas — the data contract between agents.

Free text is the enemy of quality at scale. Every agent produces structured
output (Pydantic models with typed fields), not free text. This means the
Synthesis Lead can programmatically reconcile findings, the Quality Gate can
programmatically score them, and the Presentation Designer can programmatically
lay them out. (ARCHITECTURE.md §0.1)

This package contains:
- agents.py: AgentSpec, AgentState, SubAgentSpec — agent identity and runtime state
- workflow.py: WorkflowDAG, TaskNode, SubTask — the dynamic engagement DAG
- models.py: FinalReport, KeyFinding, Risk, AnalysisSection — the findings contract
- research.py: ResearchTree, ResearchNode, ResearchBrief — research decomposition
"""

from hyperion.schemas.agents import (
    AgentName,
    AgentRole,
    AgentRuntimeState,
    AgentSpec,
    AgentState,
    SkillSpec,
    SubAgentSpec,
    ToolName,
)

__all__ = [
    "AgentName",
    "AgentRole",
    "AgentRuntimeState",
    "AgentSpec",
    "AgentState",
    "SkillSpec",
    "SubAgentSpec",
    "ToolName",
]
