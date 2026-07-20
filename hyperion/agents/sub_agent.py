"""
HYPERION Sub-Agent Runner — junior agent execution for context isolation.

This is NOT a generic sub-agent class. It is the mechanism that makes
HYPERION fundamentally different from a single-LLM system (§4.7).

A specialist hits a context window limit and needs deeper research.
Instead of truncating or compressing (which loses detail), the specialist
delegates: it sends a focused sub-question to a junior sub-agent, the
sub-agent does focused research in its own context window, and returns
structured findings (data, sources, confidence, gaps). The parent
synthesizes. The parent's context window is used for synthesis, not
for raw research.

This is how real consulting teams work — a partner doesn't read 200
pages of raw research. They read a senior associate's 5-page summary.
HYPERION's specialists are partners; sub-agents are associates.

Rules (§4.7):
- Max 3 sub-agents per specialist per engagement (enforced in BaseAgent)
- Sub-agents use MICRO or FAST tier only (don't burn STRONG/DEEP quota)
- Sub-agent findings are structured (KeyFinding), not free text
- Parent specialist receives structured findings and synthesizes them
- Sub-agents have 5-minute timeout — if a sub-agent doesn't return in
  5 min, the parent proceeds with available findings and flags the gap
- Sub-agents have access to a subset of parent's tools (specified at
  spawn time)
- Sub-agents cannot spawn their own sub-agents (no recursive spawning)
- Sub-agent findings include: data, sources, confidence score, and gaps
  (what the sub-agent couldn't find)

Sub-agent lifecycle (§4.7):
    Specialist identifies sub-question
      → Creates SubAgent spec (question, tier, tools, findings_model)
      → SubAgent dispatched to LLMRouter with appropriate tier
      → SubAgent executes: searches → extracts → analyzes → produces findings
      → SubAgent returns structured findings to parent
      → Parent synthesizes sub-agent findings into its own analysis
      → Parent reports to Engagement Director
"""

from __future__ import annotations

import time
from typing import Any

from hyperion.agents.bus import AgentBus, get_bus
from hyperion.config import ModelTier
from hyperion.router.budget import TaskUrgency
from hyperion.router.providers.base import RouterResponse
from hyperion.router.router import LLMRouter, get_router
from hyperion.schemas.agents import SubAgentSpec
from hyperion.schemas.models import KeyFinding


class SubAgentRunner:
    """Executes a single sub-agent research task and returns structured findings.

    This is NOT a full agent — it has no bus subscription, no state
    management, no sub-agent spawning capability. It is a focused
    research executor that:

    1. Takes a SubAgentSpec (question, tier, tools, findings_model)
    2. Constructs a system prompt appropriate for a junior researcher
    3. Uses the specified tools to gather data
    4. Calls the LLM at the specified tier (MICRO or FAST)
    5. Parses the response into structured KeyFinding objects
    6. Returns the findings to the parent specialist

    The parent specialist is responsible for:
    - Synthesizing sub-agent findings into its own analysis
    - Reporting to the Engagement Director via AgentBus
    - Flagging gaps (what the sub-agent couldn't find)

    The SubAgentRunner is responsible for:
    - Executing the research within its own context window
    - Producing structured findings (not free text)
    - Including confidence scores and gap identification
    - Respecting the 5-minute timeout (enforced by the parent via
      asyncio.wait_for in BaseAgent._spawn_sub_agent)
    """

    def __init__(
        self,
        spec: SubAgentSpec,
        bus: AgentBus | None = None,
        router: LLMRouter | None = None,
    ) -> None:
        self.spec = spec
        self.bus = bus or get_bus()
        self.router = router or get_router()

        # Validate tier constraint (§4.7)
        if spec.model_tier not in (ModelTier.MICRO, ModelTier.FAST):
            raise ValueError(
                f"Sub-agent tier must be MICRO or FAST, got {spec.model_tier.value}. "
                f"Sub-agents don't burn STRONG/DEEP quota (§4.7)."
            )

        # Tool instances — only the subset specified in the spec
        self._tools: dict[str, Any] = {}

    @property
    def question(self) -> str:
        return self.spec.question

    @property
    def parent_agent(self) -> str:
        return self.spec.parent_agent.value

    @property
    def tier(self) -> ModelTier:
        return self.spec.model_tier

    @property
    def tools(self) -> list[str]:
        return [t.value for t in self.spec.tools]

    def _get_tool(self, tool_name: str) -> Any:
        """Get a tool instance by name.

        Sub-agents only have access to the subset of parent's tools
        specified at spawn time (§4.7). This is enforced by the spec.
        """
        tool_enum = None
        for t in self.spec.tools:
            if t.value == tool_name:
                tool_enum = t
                break

        if tool_enum is None:
            raise ValueError(
                f"Sub-agent does not have access to tool '{tool_name}'. "
                f"Available tools: {self.tools}"
            )

        if tool_name not in self._tools:
            self._tools[tool_name] = self._instantiate_tool(tool_enum)

        return self._tools[tool_name]

    def _instantiate_tool(self, tool: Any) -> Any:
        """Instantiate a tool by enum value.

        Deferred imports to avoid circular dependencies.
        """
        from hyperion.config import get_settings
        from hyperion.schemas.agents import ToolName

        settings = get_settings()

        if tool == ToolName.SEARXNG:
            from hyperion.tools.searxng import SearxNGClient
            return SearxNGClient(settings=settings)
        elif tool == ToolName.JINA:
            from hyperion.tools.jina import JinaClient
            return JinaClient(settings=settings)
        elif tool == ToolName.OBSCURA:
            from hyperion.tools.obscura import ObscuraClient
            return ObscuraClient(settings=settings)
        elif tool == ToolName.CRAWL4AI:
            from hyperion.tools.crawl4ai import Crawl4AIClient
            return Crawl4AIClient(settings=settings)
        elif tool == ToolName.WAYBACK:
            from hyperion.tools.wayback import WaybackClient
            return WaybackClient(settings=settings)
        elif tool == ToolName.ALPHA_VANTAGE:
            from hyperion.tools.alpha_vantage import AlphaVantageClient
            return AlphaVantageClient(settings=settings)
        elif tool == ToolName.FRED:
            from hyperion.tools.fred import FredClient
            return FredClient(settings=settings)
        elif tool == ToolName.SECOND_BRAIN:
            from hyperion.tools.second_brain import SecondBrainClient
            return SecondBrainClient(settings=settings)
        else:
            raise ValueError(f"Sub-agents cannot use tool: {tool}")

    def _build_system_prompt(self) -> str:
        """Build the system prompt for a junior researcher.

        This is NOT a generic prompt. It is a focused research directive
        that instructs the sub-agent to:
        - Answer the specific sub-question with data, not opinion
        - Cite sources for every claim
        - Report confidence level
        - Identify gaps (what it couldn't find)
        - Return structured JSON output
        """
        tool_names = ", ".join(self.tools)
        return (
            "You are a junior research associate at HYPERION Consulting, a "
            "premium AI consulting firm. You have been assigned a focused "
            "research sub-question by a senior specialist.\n\n"
            "Your directive:\n"
            "1. Answer the specific sub-question with DATA, not opinion.\n"
            "2. Cite a source for every factual claim. No source = no claim.\n"
            "3. Report your confidence level: HIGH, MEDIUM, or LOW.\n"
            "4. Identify GAPS — what you couldn't find, what data is missing.\n"
            "5. Be concise and specific. No hedging, no waffling, no generic "
            "statements.\n"
            "6. Use the tools available to you: {tools}.\n"
            "7. Follow the tool selection strategy: SearxNG first (free, "
            "unlimited), Jina for extraction, Obscura for JS-rendered pages.\n"
            "8. Return your findings as structured JSON matching the "
            "KeyFinding schema.\n\n"
            "You are NOT a generalist. You are a focused researcher answering "
            "one specific question. Do not expand scope. Do not speculate "
            "beyond the data. If you can't find data, say so explicitly.\n\n"
            "Your output must be a JSON object with a 'findings' key containing "
            "an array of finding objects. Each finding must have:\n"
            "  - id: a unique identifier (e.g., 'finding_001')\n"
            "  - agent: '{parent}'\n"
            "  - finding_type: the type (e.g., 'market_data', 'competitor_info')\n"
            "  - title: short title for display\n"
            "  - content: the specific finding with data and evidence\n"
            "  - sources: array of source objects with id, title, url, credibility "
            "(one of: peer_reviewed, government, industry_report, news, blog, social_media)\n"
            "  - confidence: 'high', 'medium', or 'low'\n"
            "  - gaps: array of strings describing what you couldn't find"
        ).format(tools=tool_names, parent=self.parent_agent)

    def _build_user_prompt(self) -> str:
        """Build the user prompt with the sub-question and parent context."""
        context_str = ""
        if self.spec.context:
            context_parts = []
            for key, value in self.spec.context.items():
                context_parts.append(f"  {key}: {value}")
            context_str = "\n\nParent context (use this as starting point):\n" + "\n".join(context_parts)

        return (
            "Research question: {question}\n\n"
            "Parent agent: {parent}\n"
            "Research tier: {tier}\n"
            "Available tools: {tools}\n"
            "{context}\n\n"
            "Conduct focused research on this sub-question. Use the available "
            "tools to find data. Return your findings as a JSON array of "
            "KeyFinding objects."
        ).format(
            question=self.spec.question,
            parent=self.parent_agent,
            tier=self.tier.value,
            tools=", ".join(self.tools),
            context=context_str,
        )

    async def _gather_raw_data(self) -> str:
        """Gather raw data using the available tools.

        This is the research phase of the sub-agent lifecycle:
        searches → extracts → collects raw data for analysis.

        The tool selection strategy follows §5.2:
        - Search: SearxNG first, Jina if poor results, Obscura for JS pages
        - Extract: Jina Reader first, Obscura for JS, Crawl4AI fallback
        - Historical: Wayback Machine
        - Financial: Alpha Vantage
        - Macro: FRED
        """
        raw_data: list[str] = []

        # Search phase — SearxNG is always first (free, unlimited)
        if self._has_tool("searxng"):
            try:
                searxng = self._get_tool("searxng")
                results = await searxng.search(self.spec.question)
                if results:
                    raw_data.append(f"Search results:\n{results}")
            except Exception:
                pass  # Sub-agents proceed with available data

        # Extraction phase — Jina for content extraction
        if self._has_tool("jina") and raw_data:
            try:
                jina = self._get_tool("jina")
                # Extract top URLs from search results
                # The actual extraction depends on the Jina client interface
                extracted = await jina.search_and_extract(self.spec.question)
                if extracted:
                    raw_data.append(f"Extracted content:\n{extracted}")
            except Exception:
                pass

        # JS-rendered pages — Obscura
        if self._has_tool("obscura"):
            try:
                obscura = self._get_tool("obscura")
                scraped = await obscura.fetch(self.spec.question)
                if scraped:
                    raw_data.append(f"Scraped content:\n{scraped}")
            except Exception:
                pass

        # Historical data — Wayback
        if self._has_tool("wayback"):
            try:
                wayback = self._get_tool("wayback")
                snapshots = await wayback.search(self.spec.question)
                if snapshots:
                    raw_data.append(f"Historical snapshots:\n{snapshots}")
            except Exception:
                pass

        # Financial data — Alpha Vantage
        if self._has_tool("alpha_vantage"):
            try:
                av = self._get_tool("alpha_vantage")
                financials = await av.search(self.spec.question)
                if financials:
                    raw_data.append(f"Financial data:\n{financials}")
            except Exception:
                pass

        # Macro data — FRED
        if self._has_tool("fred"):
            try:
                fred = self._get_tool("fred")
                macro = await fred.search(self.spec.question)
                if macro:
                    raw_data.append(f"Macro data:\n{macro}")
            except Exception:
                pass

        # Second Brain — prior research
        if self._has_tool("second_brain"):
            try:
                brain = self._get_tool("second_brain")
                prior = await brain.search(self.spec.question)
                if prior:
                    raw_data.append(f"Prior research from vault:\n{prior}")
            except Exception:
                pass

        return "\n\n---\n\n".join(raw_data) if raw_data else "No raw data available from tools."

    def _has_tool(self, tool_name: str) -> bool:
        """Check if this sub-agent has access to a specific tool."""
        return any(t.value == tool_name for t in self.spec.tools)

    async def _analyze_and_produce_findings(self, raw_data: str) -> list[KeyFinding]:
        """Analyze raw data and produce structured KeyFinding objects.

        This is the analysis phase of the sub-agent lifecycle. The LLM
        at the specified tier processes the raw data and produces
        structured findings.

        The temperature is low (0.2) for structured output — we want
        deterministic, factual results, not creative writing.
        """
        import json

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt() + f"\n\nRaw data from tools:\n{raw_data}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response: RouterResponse = await self.router.complete(
            tier=self.spec.model_tier,
            messages=messages,
            agent_name=f"subagent_{self.parent_agent}",
            urgency=TaskUrgency.LOW,  # Sub-agents are LOW urgency (§3.5)
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        if not response.success or not response.content:
            return []

        try:
            data = json.loads(response.content)

            # The LLM should return a JSON array of findings or an object
            # with a "findings" key
            if isinstance(data, list):
                findings_data = data
            elif isinstance(data, dict) and "findings" in data:
                findings_data = data["findings"]
            elif isinstance(data, dict):
                findings_data = [data]
            else:
                return []

            findings: list[KeyFinding] = []
            for item in findings_data:
                try:
                    finding = KeyFinding.model_validate(item)
                    findings.append(finding)
                except (ValueError, TypeError):
                    continue

            return findings

        except (json.JSONDecodeError, ValueError):
            return []

    async def run(self) -> list[KeyFinding]:
        """Execute the sub-agent research task.

        This is the full sub-agent lifecycle:
        1. Gather raw data using available tools
        2. Analyze the data and produce structured findings
        3. Return findings to the parent specialist

        The parent specialist synthesizes these findings into its own
        analysis. The parent's context window is used for synthesis,
        not for raw research. This is the context isolation strategy
        (§4.7).

        The 5-minute timeout is enforced by the parent via
        asyncio.wait_for in BaseAgent._spawn_sub_agent.
        """
        start = time.time()

        # Phase 1: Gather raw data
        raw_data = await self._gather_raw_data()

        # Phase 2: Analyze and produce structured findings
        findings = await self._analyze_and_produce_findings(raw_data)

        elapsed = time.time() - start

        # If no findings were produced, return a gap finding
        if not findings:
            from hyperion.schemas.models import ConfidenceLevel
            findings = [
                KeyFinding(
                    id=f"gap_{self.parent_agent}_{int(time.time())}",
                    agent=self.parent_agent,
                    finding_type="research_gap",
                    title=f"Research gap: {self.spec.question[:100]}",
                    content=(
                        f"Sub-agent was unable to find data for this sub-question. "
                        f"This is a research gap that should be flagged to the parent. "
                        f"Tools used: {', '.join(self.tools)}. "
                        f"Time elapsed: {elapsed:.1f}s."
                    ),
                    sources=[],
                    confidence=ConfidenceLevel.LOW,
                    gaps=[self.spec.question],
                )
            ]

        return findings
