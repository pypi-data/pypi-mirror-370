"""
Web Research Agent for Virtual Expert Panel

This module implements a specialized web research agent using web scraping and search
to perform internet research and populate the knowledge base.
"""

import logging
from typing import Any, Optional, Dict, List
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..models.virtual_panel import KnowledgeBase
from ..models.config import AgentConfig
from ..tools.tavily_search import TavilyWebSearchTool
from ..memory import Mem0Manager

# Research effectiveness scoring constants
KEY_FINDINGS_WEIGHT = 0.1
KEY_FINDINGS_MAX_BONUS = 0.3
SOURCES_WEIGHT = 0.05
SOURCES_MAX_BONUS = 0.2
BASE_EFFECTIVENESS_BONUS = 0.2
CONFIDENCE_WEIGHT = 0.3
BASE_EFFECTIVENESS_SCORE = 0.5


class WebResearchAgent:
    """
    Specialized agent for web research using basic web scraping and search.

    This agent can search the internet, extract information from web pages,
    and populate the knowledge base with research findings.
    """

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient | None = None,
        max_pages_per_search: int = 5,
        enable_screenshots: bool = False,
        use_tavily: bool = True,
        tavily_api_key: str | None = None,
        mem0_manager: Mem0Manager | None = None,
    ):
        """
        Initialize the Web Research Agent.

        Args:
            model_client: OpenAI model client for the agent
            max_pages_per_search: Maximum number of pages to visit per search
            enable_screenshots: Whether to take screenshots of pages (not implemented)
            use_tavily: Whether to use Tavily for real web searches (default: True)
            tavily_api_key: Tavily API key (optional, will use TAVILY_API_KEY env var)
            mem0_manager: Mem0 memory manager for learning from research patterns
        """
        self.logger = logging.getLogger(__name__)
        self.max_pages_per_search = max_pages_per_search
        self.enable_screenshots = enable_screenshots
        self.use_tavily = use_tavily

        # Store Mem0 manager for learning from research patterns
        self.mem0_manager = mem0_manager

        # Initialize Tavily search tool if enabled
        self.tavily_tool = None
        if use_tavily:
            try:
                self.tavily_tool = TavilyWebSearchTool(api_key=tavily_api_key)
                self.logger.info("Tavily search tool initialized successfully")
            except ValueError as e:
                self.logger.error(f"Invalid Tavily API key: {e}")
                raise ValueError(
                    f"Tavily API key validation failed: {e}. "
                    "Please ensure TAVILY_API_KEY is set correctly."
                )
            except ImportError as e:
                self.logger.error(f"Missing dependencies for Tavily tool: {e}")
                raise ImportError(
                    f"Required dependencies for Tavily search are not installed: {e}. "
                    "Please install with 'pip install langchain-tavily'."
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize Tavily tool: {e}")
                raise ValueError(
                    f"Tavily search tool initialization failed: {e}. "
                    "Please ensure TAVILY_API_KEY is set or set use_tavily=False to disable real web search."
                )

        # Create model client if not provided
        if model_client is None:
            model_client = OpenAIChatCompletionClient(
                model="gpt-4o-mini",
                api_key=None,  # Will use environment variable
            )

        # Research coordination agent
        self.coordinator = AssistantAgent(
            name="ResearchCoordinator",
            model_client=model_client,
            system_message="""
            You are a Research Coordinator that performs internet research and analysis.

            Your role is to:
            1. Plan effective web research strategies
            2. Analyze web search results and content
            3. Extract key information from web sources
            4. Synthesize findings into comprehensive summaries

            When given a research task:
            1. Generate effective search queries
            2. Analyze search results for relevance and credibility
            3. Extract facts, data, and insights from content
            4. Provide comprehensive summaries with source citations

            Always cite your sources and indicate the confidence level of information found.
            Focus on recent, authoritative, and relevant information.
            """,
        )

        self.logger.info("WebResearchAgent initialized successfully")

    @classmethod
    def from_config(
        cls,
        config: AgentConfig,
        use_tavily: bool = True,
        tavily_api_key: str | None = None,
        mem0_manager: Mem0Manager | None = None,
        max_pages_per_search: int = 5,
    ) -> "WebResearchAgent":
        """
        Create a WebResearchAgent from configuration.

        Args:
            config: Agent configuration from YAML file
            use_tavily: Whether to use Tavily for real web searches
            tavily_api_key: Optional Tavily API key
            mem0_manager: Optional Mem0 memory manager
            max_pages_per_search: Maximum pages to search per query

        Returns:
            Configured WebResearchAgent instance
        """
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from autogen_core.models import ModelInfo

        # Create model client from config
        model_client = OpenAIChatCompletionClient(
            model=config.model_name,
            base_url=config.openai_base_url,
            api_key=config.openai_api_key,
            model_info=ModelInfo(**config.model_info.model_dump()),
        )

        # Create WebResearchAgent with the model client
        return cls(
            model_client=model_client,
            max_pages_per_search=max_pages_per_search,
            use_tavily=use_tavily,
            tavily_api_key=tavily_api_key,
            mem0_manager=mem0_manager,
        )

    async def _get_memory_guided_strategies(
        self, query: str, domain: str | None
    ) -> list[str]:
        """
        Get search strategies based on memory of past successful research.

        Args:
            query: Research query
            domain: Domain context

        Returns:
            List of recommended search strategies
        """
        if not self.mem0_manager or not domain:
            return []

        try:
            strategies = await self.mem0_manager.query_research_strategies(
                domain=domain, query_type=query, limit=3
            )

            # Extract strategy recommendations from memory
            recommendations = []
            for strategy in strategies:
                content = strategy.get("content", "")
                if "strategy" in content.lower():
                    # Extract strategy from content
                    # Simple extraction - could be enhanced with NLP
                    parts = content.split("strategy")[-1].split(".")[0]
                    if parts.strip():
                        recommendations.append(parts.strip().rstrip(":"))

            if recommendations:
                self.logger.info(
                    f"Retrieved {len(recommendations)} memory-guided strategies"
                )

            return recommendations

        except Exception as e:
            self.logger.warning(f"Failed to get memory-guided strategies: {e}")
            return []

    async def _store_research_effectiveness(
        self, query: str, domain: str | None, strategy: str, results: dict[str, Any]
    ) -> None:
        """
        Store the effectiveness of a research strategy for future learning.

        Args:
            query: Original research query
            domain: Domain context
            strategy: Strategy used
            results: Research results to evaluate effectiveness
        """
        if not self.mem0_manager or not domain:
            return

        try:
            # Calculate effectiveness based on results quality
            effectiveness = self._calculate_research_effectiveness(results)

            await self.mem0_manager.add_research_strategy(
                query=query,
                strategy=strategy,
                effectiveness_score=effectiveness,
                domain=domain,
                research_results={
                    "key_findings_count": len(results.get("key_findings", [])),
                    "sources_count": len(results.get("sources", [])),
                    "confidence": results.get("confidence", 0.0),
                },
            )

            self.logger.info(
                f"Stored research strategy effectiveness: {effectiveness:.2f}"
            )

        except Exception as e:
            self.logger.warning(f"Failed to store research effectiveness: {e}")

    def _calculate_research_effectiveness(self, results: dict[str, Any]) -> float:
        """Calculate effectiveness score for research results."""
        effectiveness = 0.0

        # Base score
        effectiveness += BASE_EFFECTIVENESS_BONUS

        # Quality indicators
        key_findings = results.get("key_findings", [])
        if key_findings:
            effectiveness += min(
                len(key_findings) * KEY_FINDINGS_WEIGHT, KEY_FINDINGS_MAX_BONUS
            )

        sources = results.get("sources", [])
        if sources:
            effectiveness += min(len(sources) * SOURCES_WEIGHT, SOURCES_MAX_BONUS)

        confidence = results.get("confidence", 0.0)
        effectiveness += confidence * CONFIDENCE_WEIGHT

        return min(effectiveness, 1.0)

    async def research_topic(
        self,
        query: str,
        domain: str | None = None,
        specific_sites: list[str] | None = None,
        time_filter: str = "any",
    ) -> dict[str, Any]:
        """
        Perform comprehensive web research on a given topic.

        Args:
            query: Research query or topic
            domain: Optional domain context for focused research
            specific_sites: Optional list of specific sites to search
            time_filter: Time filter for search results

        Returns:
            Dictionary containing research results and metadata
        """
        self.logger.info(f"Starting web research for query: {query}")

        # Get memory-guided strategies for enhanced research
        memory_strategies = await self._get_memory_guided_strategies(query, domain)

        # Build search strategy (enhanced with memory insights)
        search_queries = await self._build_search_strategy(
            query, domain, memory_strategies
        )

        research_results = {
            "original_query": query,
            "domain": domain,
            "search_queries": search_queries,
            "pages_visited": [],
            "key_findings": [],
            "sources": [],
            "summary": "",
            "confidence_score": 0.0,
            "timestamp": datetime.now(),
        }

        try:
            # Perform web research using Tavily
            for search_query in search_queries[:3]:  # Limit to 3 search queries
                self.logger.info(f"Researching: {search_query}")

                if self.use_tavily and self.tavily_tool:
                    # Use real Tavily web search
                    search_results = await self._perform_tavily_search(
                        search_query, specific_sites, domain
                    )
                else:
                    # No fallback - raise error if Tavily is not available
                    raise ValueError(
                        "Web search is not available. Please set TAVILY_API_KEY environment variable "
                        "and ensure use_tavily=True, or use WebResearchAgent with use_tavily=False "
                        "for simulation mode."
                    )

                if search_results:
                    research_results["pages_visited"].extend(
                        search_results.get("pages_visited", [])
                    )
                    research_results["key_findings"].extend(
                        search_results.get("findings", [])
                    )
                    research_results["sources"].extend(
                        search_results.get("sources", [])
                    )

            # Synthesize and summarize findings
            research_results["summary"] = await self._synthesize_findings(
                research_results["key_findings"], query, domain
            )

            # Calculate confidence score based on research quality
            research_results["confidence_score"] = self._calculate_confidence(
                research_results
            )

            self.logger.info(
                f"Web research completed. Generated {len(research_results['key_findings'])} key findings"
            )

        except Exception as e:
            self.logger.error(f"Error during web research: {e}")
            research_results["error"] = str(e)
            research_results["summary"] = f"Research failed due to error: {e}"

        # Store research effectiveness for future learning
        if not research_results.get("error"):
            strategy_description = f"Used search queries: {', '.join(search_queries)}"
            await self._store_research_effectiveness(
                query, domain, strategy_description, research_results
            )

        return research_results

    async def _build_search_strategy(
        self,
        query: str,
        domain: str | None = None,
        memory_strategies: list[str] | None = None,
    ) -> list[str]:
        """Build a list of effective search queries for the research topic."""

        strategy_prompt = f"""
        Create 3-5 effective web search queries for researching: "{query}"
        {f"Domain context: {domain}" if domain else ""}

        {
            f'''
        MEMORY-GUIDED STRATEGIES (from past successful research):
        {chr(10).join(f"- {strategy}" for strategy in memory_strategies)}
        '''
            if memory_strategies
            else ""
        }

        Consider:
        - Different angles and perspectives on the topic
        - Specific facts, statistics, or data points needed
        - Recent developments or current trends
        - Expert opinions or authoritative sources
        - Best practices and case studies
        {
            "- Apply successful strategies from memory insights above"
            if memory_strategies
            else ""
        }

        Return only the search queries, one per line, without numbering or bullets.
        """

        try:
            # Use the coordinator to plan search strategy
            message = TextMessage(content=strategy_prompt, source="user")
            response = await self.coordinator.on_messages(
                [message], CancellationToken()
            )

            # Extract search queries from response
            queries = []
            if hasattr(response, "chat_message") and hasattr(
                response.chat_message, "content"
            ):
                content = response.chat_message.content
                # Split by lines and clean up
                queries = [
                    line.strip()
                    for line in content.split("\n")
                    if line.strip()
                    and not line.strip().startswith(
                        ("#", "-", "*", "1", "2", "3", "4", "5")
                    )
                ]

            # Fallback to basic query variations if extraction fails
            if not queries:
                queries = [
                    query,
                    f"{query} latest trends 2024",
                    f"{query} expert analysis",
                    f"{query} statistics data",
                    f"{query} best practices",
                ]

            return queries[:5]  # Limit to 5 queries

        except Exception as e:
            self.logger.warning(f"Failed to build search strategy: {e}")
            # Fallback to basic queries
            return [query, f"{query} analysis", f"{query} trends"]

    async def _perform_tavily_search(
        self,
        search_query: str,
        specific_sites: list[str] | None = None,
        domain: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Perform real web search using Tavily's API.

        Args:
            search_query: The search query to execute
            specific_sites: Optional list of specific sites to focus on
            domain: Optional domain context for the search

        Returns:
            Dictionary containing search results in the expected format
        """
        try:
            self.logger.info(f"Performing Tavily search for: {search_query}")

            # Determine search parameters based on domain
            search_depth = "advanced" if domain else "basic"
            topic = "general"

            # Map domain to Tavily topic if applicable
            if domain:
                domain_lower = domain.lower()
                if "finance" in domain_lower or "business" in domain_lower:
                    topic = "finance"
                elif "news" in domain_lower or "current" in domain_lower:
                    topic = "news"

            # Use Tavily tool to perform the search
            tavily_results = self.tavily_tool.search(
                query=search_query,
                max_results=self.max_pages_per_search,
                search_depth=search_depth,
                topic=topic,
                include_answer=True,
                include_raw_content=True,
                include_images=False,
                include_domains=specific_sites,
                exclude_domains=None,
            )

            if not tavily_results.get("success", False):
                error_msg = tavily_results.get("error", "Unknown error")
                self.logger.error(f"Tavily search failed: {error_msg}")
                raise RuntimeError(f"Tavily search failed: {error_msg}")

            # Convert Tavily results to the expected format
            findings = []
            sources = []
            pages_visited = []

            # Process Tavily search results
            for result in tavily_results.get("results", []):
                # Create finding entry
                finding = {
                    "content": result.get("content", ""),
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "score": result.get("score", 0.0),
                    "type": "web_result",
                    "confidence": "high" if result.get("score", 0) > 0.8 else "medium",
                }
                findings.append(finding)

                # Create source entry
                source = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "domain": result.get("url", "").split("/")[2]
                    if result.get("url")
                    else "",
                    "content_preview": result.get("content", "")[:200] + "..."
                    if result.get("content")
                    else "",
                }
                sources.append(source)
                pages_visited.append(result.get("url", ""))

            # Add Tavily's AI answer as a special finding if available
            if tavily_results.get("answer"):
                answer_finding = {
                    "content": tavily_results["answer"],
                    "title": "AI-Generated Summary",
                    "url": "tavily://ai-summary",
                    "score": 1.0,
                    "type": "ai_summary",
                    "confidence": "high",
                }
                findings.insert(0, answer_finding)  # Put AI summary first

            search_results = {
                "search_query": search_query,
                "findings": findings,
                "sources": sources,
                "pages_visited": pages_visited,
                "raw_response": f"Tavily search completed with {len(findings)} findings",
                "tavily_data": tavily_results,  # Store original Tavily data for reference
            }

            self.logger.info(
                f"Tavily search completed: {len(findings)} findings from {len(sources)} sources"
            )
            return search_results

        except Exception as e:
            self.logger.error(f"Tavily search failed for query '{search_query}': {e}")
            raise RuntimeError(f"Tavily search failed for query '{search_query}': {e}")

    async def _simulate_web_search(
        self, search_query: str, specific_sites: Optional[List[str]] = None
    ) -> dict[str, Any]:
        """
        Simulate web search results using the research agent's knowledge.

        This method is used as a fallback when Tavily is not available or configured.
        It generates simulated search results based on the agent's training data.

        In a production implementation, this would use real web APIs like:
        - Google Custom Search API
        - Bing Search API
        - DuckDuckGo API
        - Web scraping with requests/beautifulsoup
        """

        # Modify query for specific sites if provided
        enhanced_query = search_query
        if specific_sites:
            site_info = f" focusing on sites like {', '.join(specific_sites)}"
            enhanced_query = f"{search_query}{site_info}"

        research_prompt = f"""
        Based on your knowledge, provide research findings for the query: "{enhanced_query}"

        Provide information structured as follows:

        FINDINGS:
        - [Provide 3-5 key findings, facts, or insights]
        - [Include specific data points, statistics, or trends when possible]
        - [Focus on recent developments and expert opinions]

        SOURCES:
        - [List 3-5 authoritative sources that would contain this information]
        - [Include mix of: academic sites, news sources, industry reports, official documentation]
        - [Format as: Source Name - example.com/article-title]

        ANALYSIS:
        [Provide a brief analysis of the current state and trends in this area]

        Focus on accuracy, relevance, and actionable insights.
        Indicate confidence levels where appropriate.
        """

        try:
            # Send research request to coordinator
            message = TextMessage(content=research_prompt, source="user")
            response = await self.coordinator.on_messages(
                [message], CancellationToken()
            )

            # Parse response and extract structured data
            if hasattr(response, "chat_message") and hasattr(
                response.chat_message, "content"
            ):
                content = response.chat_message.content

                # Extract findings and sources from the response
                findings = self._extract_findings_from_content(content)
                sources = self._extract_sources_from_content(content)

                return {
                    "search_query": search_query,
                    "raw_response": content,
                    "findings": findings,
                    "sources": sources,
                    "pages_visited": sources,  # Simulated
                }

        except Exception as e:
            self.logger.error(
                f"Simulated web search failed for query '{search_query}': {e}"
            )
            return {}

        return {}

    def _extract_findings_from_content(self, content: str) -> list[dict[str, Any]]:
        """Extract structured findings from research content."""
        findings = []

        # Parse the structured response
        lines = content.split("\n")
        in_findings_section = False
        in_analysis_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Section markers
            if line.upper().startswith("FINDINGS"):
                in_findings_section = True
                in_analysis_section = False
                continue
            elif line.upper().startswith("SOURCES"):
                in_findings_section = False
                in_analysis_section = False
                continue
            elif line.upper().startswith("ANALYSIS"):
                in_findings_section = False
                in_analysis_section = True
                continue

            # Extract findings
            if in_findings_section and line.startswith("-"):
                finding_text = line[1:].strip()
                if finding_text:
                    findings.append(
                        {
                            "type": "finding",
                            "content": finding_text,
                            "timestamp": datetime.now(),
                            "source": "research_analysis",
                        }
                    )

            # Extract analysis as a finding
            elif in_analysis_section and len(line) > 20:
                findings.append(
                    {
                        "type": "analysis",
                        "content": line,
                        "timestamp": datetime.now(),
                        "source": "research_analysis",
                    }
                )

        return findings

    def _extract_sources_from_content(self, content: str) -> list[str]:
        """Extract source references from content."""
        sources = []

        lines = content.split("\n")
        in_sources_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.upper().startswith("SOURCES"):
                in_sources_section = True
                continue
            elif line.upper().startswith("ANALYSIS"):
                in_sources_section = False
                continue

            if in_sources_section and line.startswith("-"):
                source_text = line[1:].strip()
                if source_text:
                    sources.append(source_text)

        return sources

    async def _synthesize_findings(
        self,
        findings: list[dict[str, Any]],
        original_query: str,
        domain: str | None = None,
    ) -> str:
        """Synthesize research findings into a coherent summary."""
        if not findings:
            return "No significant findings from web research."

        findings_text = "\n".join([f"- {f['content']}" for f in findings])

        synthesis_prompt = f"""
        Based on the following research findings for the query "{original_query}" {f"in the {domain} domain" if domain else ""}:

        {findings_text}

        Provide a comprehensive research summary that includes:

        1. **Key Insights**: Main findings and important discoveries
        2. **Current Trends**: Latest developments and emerging patterns
        3. **Data & Evidence**: Supporting statistics and factual information
        4. **Expert Perspectives**: Authoritative opinions and recommendations
        5. **Actionable Recommendations**: Practical next steps or considerations

        Structure the summary to be informative, well-organized, and actionable.
        Highlight the most important and recent information.
        """

        try:
            message = TextMessage(content=synthesis_prompt, source="user")
            response = await self.coordinator.on_messages(
                [message], CancellationToken()
            )

            if hasattr(response, "chat_message") and hasattr(
                response.chat_message, "content"
            ):
                return response.chat_message.content
        except Exception as e:
            self.logger.error(f"Failed to synthesize findings: {e}")

        # Fallback to basic summary
        return f"Research completed with {len(findings)} findings on '{original_query}'. Key areas covered include current trends, expert analysis, and practical recommendations. Manual review of detailed findings is recommended for comprehensive understanding."

    def _calculate_confidence(self, research_results: dict[str, Any]) -> float:
        """Calculate confidence score based on research quality."""
        score = 0.0

        # Factor 1: Number of sources (max 0.3)
        num_sources = len(research_results.get("sources", []))
        score += min(num_sources * 0.06, 0.3)

        # Factor 2: Number of findings (max 0.4)
        num_findings = len(research_results.get("key_findings", []))
        score += min(num_findings * 0.08, 0.4)

        # Factor 3: Query specificity (max 0.1)
        query_words = len(research_results.get("original_query", "").split())
        if query_words >= 3:
            score += 0.1
        elif query_words >= 2:
            score += 0.05

        # Factor 4: Summary quality (basic check, max 0.2)
        summary_length = len(research_results.get("summary", ""))
        if summary_length > 200:
            score += 0.2
        elif summary_length > 100:
            score += 0.1
        elif summary_length > 50:
            score += 0.05

        return min(score, 1.0)

    def populate_knowledge_base(
        self, knowledge_base: KnowledgeBase, research_results: dict[str, Any]
    ) -> None:
        """
        Populate the knowledge base with research findings.

        Args:
            knowledge_base: The knowledge base to populate
            research_results: Results from web research
        """
        self.logger.info("Populating knowledge base with web research results")

        # Add web research results
        knowledge_base.add_web_result(
            query=research_results["original_query"],
            results=research_results.get("key_findings", []),
        )

        # Extract and add facts
        for finding in research_results.get("key_findings", []):
            if isinstance(finding, dict) and "content" in finding:
                knowledge_base.extract_fact(
                    fact=finding["content"],
                    source=finding.get("source", "web_research"),
                    confidence=research_results.get("confidence_score", 0.5),
                )

        # Add sources as documents
        for i, source in enumerate(research_results.get("sources", [])):
            knowledge_base.add_document(
                title=f"Research Source {i + 1}",
                content=f"Source: {source}\n\nSummary: {research_results.get('summary', '')}",
                source=source,
                metadata={
                    "research_query": research_results["original_query"],
                    "confidence": research_results.get("confidence_score", 0.5),
                    "timestamp": research_results.get("timestamp"),
                    "type": "web_research",
                },
            )

        # Update knowledge base summary
        if research_results.get("summary"):
            if knowledge_base.summary:
                knowledge_base.summary += f"\n\n## Web Research: {research_results['original_query']}\n{research_results['summary']}"
            else:
                knowledge_base.summary = f"## Web Research: {research_results['original_query']}\n{research_results['summary']}"

        # Update confidence score (weighted average)
        existing_confidence = knowledge_base.confidence_score
        new_confidence = research_results.get("confidence_score", 0.5)

        # Weight new research higher if knowledge base is empty
        if existing_confidence == 0.0:
            knowledge_base.confidence_score = new_confidence
        else:
            knowledge_base.confidence_score = (
                existing_confidence * 0.6 + new_confidence * 0.4
            )

        self.logger.info(
            f"Knowledge base updated with {len(research_results.get('key_findings', []))} findings"
        )


async def perform_web_research(
    query: str,
    domain: Optional[str] = None,
    knowledge_base: KnowledgeBase | None = None,
    max_pages: int = 5,
    use_tavily: bool = True,
    tavily_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to perform web research and optionally populate knowledge base.

    Args:
        query: Research query
        domain: Optional domain context
        knowledge_base: Optional knowledge base to populate
        max_pages: Maximum pages to visit
        use_tavily: Whether to use Tavily for real web searches (default: True)
        tavily_api_key: Optional Tavily API key

    Returns:
        Research results dictionary
    """
    # Create web research agent with Tavily support
    web_agent = WebResearchAgent(
        max_pages_per_search=max_pages,
        use_tavily=use_tavily,
        tavily_api_key=tavily_api_key,
    )

    # Perform research
    research_results = await web_agent.research_topic(query=query, domain=domain)

    # Populate knowledge base if provided
    if knowledge_base:
        web_agent.populate_knowledge_base(knowledge_base, research_results)

    return research_results
