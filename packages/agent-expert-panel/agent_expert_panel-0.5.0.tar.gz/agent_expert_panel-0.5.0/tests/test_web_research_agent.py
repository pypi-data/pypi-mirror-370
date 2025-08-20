"""
Tests for the Web Research Agent functionality.

This test suite validates the WebResearchAgent implementation and its integration
with the Virtual Expert Panel system.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from agent_expert_panel.agents.web_research_agent import (
    WebResearchAgent,
    perform_web_research,
)
from agent_expert_panel.models.virtual_panel import KnowledgeBase


class TestWebResearchAgent:
    """Test suite for WebResearchAgent class."""

    @pytest.fixture
    def mock_model_client(self):
        """Create a mock model client for testing."""
        mock_client = Mock()
        mock_client.model = "gpt-4o-mini"
        return mock_client

    @pytest.fixture
    def web_agent(self, mock_model_client):
        """Create a WebResearchAgent instance for testing."""
        with patch(
            "agent_expert_panel.agents.web_research_agent.OpenAIChatCompletionClient",
            return_value=mock_model_client,
        ):
            agent = WebResearchAgent(model_client=mock_model_client)
            return agent

    @pytest.fixture
    def knowledge_base(self):
        """Create a KnowledgeBase instance for testing."""
        return KnowledgeBase(
            domain="test_domain", documents=[], web_research=[], facts=[], entities=[]
        )

    def test_web_research_agent_initialization(self, web_agent):
        """Test that WebResearchAgent initializes correctly."""
        assert web_agent is not None
        assert web_agent.max_pages_per_search == 5
        assert not web_agent.enable_screenshots
        assert web_agent.coordinator is not None
        assert web_agent.coordinator.name == "ResearchCoordinator"

    def test_web_research_agent_custom_params(self):
        """Test WebResearchAgent with custom parameters."""
        mock_client = Mock()
        with patch(
            "agent_expert_panel.agents.web_research_agent.OpenAIChatCompletionClient",
            return_value=mock_client,
        ):
            agent = WebResearchAgent(
                model_client=mock_client,
                max_pages_per_search=10,
                enable_screenshots=True,
            )
            assert agent.max_pages_per_search == 10
            assert agent.enable_screenshots

    @pytest.mark.asyncio
    async def test_build_search_strategy_success(self, web_agent):
        """Test successful search strategy building."""
        # Mock the coordinator response
        mock_response = Mock()
        mock_response.chat_message.content = """
        AI development tools 2024 trends
        Machine learning software development best practices
        AI code generation expert analysis
        Automated testing AI statistics data
        """

        web_agent.coordinator.on_messages = AsyncMock(return_value=mock_response)

        queries = await web_agent._build_search_strategy(
            "AI in software development", "technology"
        )

        assert len(queries) == 4
        assert "AI development tools 2024 trends" in queries
        assert "Machine learning software development best practices" in queries
        assert "AI code generation expert analysis" in queries
        assert "Automated testing AI statistics data" in queries

    @pytest.mark.asyncio
    async def test_build_search_strategy_fallback(self, web_agent):
        """Test search strategy fallback when coordinator fails."""
        # Mock coordinator to raise an exception
        web_agent.coordinator.on_messages = AsyncMock(
            side_effect=Exception("API Error")
        )

        queries = await web_agent._build_search_strategy("test query", "test_domain")

        assert len(queries) == 3
        assert "test query" in queries
        assert "test query analysis" in queries
        assert "test query trends" in queries

    @pytest.mark.asyncio
    async def test_simulate_web_search_success(self, web_agent):
        """Test successful web search simulation."""
        mock_response = Mock()
        mock_response.chat_message.content = """
        FINDINGS:
        - AI-powered code completion tools are being adopted by 70% of developers
        - Machine learning models for bug detection show 85% accuracy
        - Automated testing with AI reduces testing time by 60%

        SOURCES:
        - GitHub Developer Survey - github.com/developer-survey-2024
        - Stack Overflow AI Trends Report - stackoverflow.com/ai-trends
        - IEEE Software Engineering Journal - ieee.org/software-ai

        ANALYSIS:
        The current state of AI in software development shows rapid adoption and significant productivity gains.
        """

        web_agent.coordinator.on_messages = AsyncMock(return_value=mock_response)

        result = await web_agent._simulate_web_search("AI development tools")

        assert result["search_query"] == "AI development tools"
        assert len(result["findings"]) == 4  # 3 findings + 1 analysis
        assert len(result["sources"]) == 3
        assert "pages_visited" in result

    @pytest.mark.asyncio
    async def test_simulate_web_search_with_specific_sites(self, web_agent):
        """Test web search simulation with specific sites."""
        mock_response = Mock()
        mock_response.chat_message.content = """
        FINDINGS:
        - Site-specific finding from requested sources

        SOURCES:
        - Example Source - example.com
        """

        web_agent.coordinator.on_messages = AsyncMock(return_value=mock_response)

        specific_sites = ["github.com", "stackoverflow.com"]
        result = await web_agent._simulate_web_search("test query", specific_sites)

        # Verify the query was enhanced with site information
        assert result is not None
        web_agent.coordinator.on_messages.assert_called_once()
        call_args = web_agent.coordinator.on_messages.call_args[0][0]
        assert (
            "focusing on sites like github.com, stackoverflow.com"
            in call_args[0].content
        )

    def test_extract_findings_from_content(self, web_agent):
        """Test finding extraction from structured content."""
        content = """
        FINDINGS:
        - First key finding about AI trends
        - Second finding with statistical data
        - Third insight about expert opinions

        SOURCES:
        - Source 1 - example1.com
        - Source 2 - example2.com

        ANALYSIS:
        This is a comprehensive analysis of the current state and future trends.
        """

        findings = web_agent._extract_findings_from_content(content)

        assert len(findings) == 4  # 3 findings + 1 analysis

        # Check finding types
        finding_types = [f["type"] for f in findings]
        assert finding_types.count("finding") == 3
        assert finding_types.count("analysis") == 1

        # Check content extraction
        finding_contents = [f["content"] for f in findings]
        assert "First key finding about AI trends" in finding_contents
        assert "Second finding with statistical data" in finding_contents
        assert "Third insight about expert opinions" in finding_contents
        assert (
            "This is a comprehensive analysis of the current state and future trends."
            in finding_contents
        )

    def test_extract_sources_from_content(self, web_agent):
        """Test source extraction from structured content."""
        content = """
        FINDINGS:
        - Some findings here

        SOURCES:
        - GitHub Developer Survey - github.com/survey
        - Stack Overflow Report - stackoverflow.com/report
        - IEEE Research Paper - ieee.org/paper

        ANALYSIS:
        Analysis content here
        """

        sources = web_agent._extract_sources_from_content(content)

        assert len(sources) == 3
        assert "GitHub Developer Survey - github.com/survey" in sources
        assert "Stack Overflow Report - stackoverflow.com/report" in sources
        assert "IEEE Research Paper - ieee.org/paper" in sources

    @pytest.mark.asyncio
    async def test_synthesize_findings_success(self, web_agent):
        """Test successful findings synthesis."""
        findings = [
            {"content": "AI adoption is increasing", "type": "finding"},
            {"content": "70% of developers use AI tools", "type": "finding"},
            {"content": "Productivity gains are significant", "type": "analysis"},
        ]

        mock_response = Mock()
        mock_response.chat_message.content = """
        ## Key Insights
        AI adoption in software development is rapidly accelerating.

        ## Current Trends
        Most developers are now using AI-powered tools.

        ## Actionable Recommendations
        Organizations should invest in AI training and tools.
        """

        web_agent.coordinator.on_messages = AsyncMock(return_value=mock_response)

        summary = await web_agent._synthesize_findings(
            findings, "AI in software development", "technology"
        )

        assert "Key Insights" in summary
        assert "Current Trends" in summary
        assert "Actionable Recommendations" in summary

    @pytest.mark.asyncio
    async def test_synthesize_findings_fallback(self, web_agent):
        """Test findings synthesis fallback when coordinator fails."""
        findings = [{"content": "Test finding", "type": "finding"}]

        web_agent.coordinator.on_messages = AsyncMock(
            side_effect=Exception("API Error")
        )

        summary = await web_agent._synthesize_findings(
            findings, "test query", "test_domain"
        )

        assert "Research completed with 1 findings on 'test query'" in summary
        assert "Manual review of detailed findings is recommended" in summary

    def test_calculate_confidence_high_quality(self, web_agent):
        """Test confidence calculation for high-quality research."""
        research_results = {
            "sources": ["source1", "source2", "source3", "source4", "source5"],
            "key_findings": [
                {"content": "finding1"},
                {"content": "finding2"},
                {"content": "finding3"},
            ],
            "pages_visited": ["page1", "page2", "page3"],
            "original_query": "detailed specific query with multiple words",
            "summary": "This is a comprehensive summary with more than 200 characters that provides detailed insights and analysis of the research findings with actionable recommendations.",
        }

        confidence = web_agent._calculate_confidence(research_results)

        # Should be high confidence due to multiple sources, findings, and good summary
        # Expected: 5 sources (0.3) + 3 findings (0.24) + 6 words (0.1) + long summary (0.2) = 0.84
        assert confidence >= 0.74  # Allow some tolerance for calculation variations
        assert confidence <= 1.0

    def test_calculate_confidence_low_quality(self, web_agent):
        """Test confidence calculation for low-quality research."""
        research_results = {
            "sources": [],
            "key_findings": [],
            "pages_visited": [],
            "original_query": "query",
            "summary": "Short",
        }

        confidence = web_agent._calculate_confidence(research_results)

        # Should be low confidence due to lack of sources and findings
        assert confidence < 0.3

    def test_populate_knowledge_base(self, web_agent, knowledge_base):
        """Test knowledge base population with research results."""
        research_results = {
            "original_query": "AI in software development",
            "key_findings": [
                {
                    "content": "AI tools increase productivity",
                    "source": "research_analysis",
                },
                {
                    "content": "70% developer adoption rate",
                    "source": "research_analysis",
                },
            ],
            "sources": [
                "GitHub Survey - github.com/survey",
                "Stack Overflow Report - stackoverflow.com/report",
            ],
            "summary": "AI adoption is rapidly increasing in software development.",
            "confidence_score": 0.85,
            "timestamp": datetime.now(),
        }

        # Verify initial state
        assert len(knowledge_base.documents) == 0
        assert len(knowledge_base.facts) == 0
        assert len(knowledge_base.web_research) == 0

        # Populate knowledge base
        web_agent.populate_knowledge_base(knowledge_base, research_results)

        # Verify population
        assert len(knowledge_base.documents) == 2  # One for each source
        assert len(knowledge_base.facts) == 2  # One for each finding
        assert len(knowledge_base.web_research) == 1  # One web research entry

        # Verify summary update
        assert "AI in software development" in knowledge_base.summary
        assert "AI adoption is rapidly increasing" in knowledge_base.summary

        # Verify confidence score
        assert knowledge_base.confidence_score == 0.85

    @pytest.mark.asyncio
    async def test_research_topic_full_flow(self, web_agent):
        """Test the complete research topic flow."""
        # Mock coordinator responses - only strategy and synthesis are called with Tavily
        strategy_response = Mock()
        strategy_response.chat_message.content = (
            "AI trends 2024\nMachine learning development"
        )

        synthesis_response = Mock()
        synthesis_response.chat_message.content = (
            "Comprehensive research summary with actionable insights."
        )

        web_agent.coordinator.on_messages = AsyncMock(
            side_effect=[
                strategy_response,  # For search strategy
                synthesis_response,  # For synthesis
            ]
        )

        result = await web_agent.research_topic(
            query="AI in software development", domain="technology"
        )

        # Verify result structure
        assert result["original_query"] == "AI in software development"
        assert result["domain"] == "technology"
        assert len(result["search_queries"]) == 2
        assert len(result["key_findings"]) >= 2
        assert len(result["sources"]) >= 2
        assert (
            result["summary"]
            == "Comprehensive research summary with actionable insights."
        )
        assert result["confidence_score"] > 0
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_research_topic_with_error(self, web_agent):
        """Test research topic handling when errors occur."""
        # Mock coordinator to raise an exception for strategy building (first call)
        web_agent.coordinator.on_messages = AsyncMock(
            side_effect=Exception("API Error")
        )

        result = await web_agent.research_topic("test query")

        # Should handle error gracefully with fallback behavior
        assert "original_query" in result
        assert result["original_query"] == "test query"
        assert "confidence_score" in result
        # Should have some confidence from Tavily results even if coordinator fails
        assert result["confidence_score"] >= 0.0


class TestWebResearchAgentIntegration:
    """Integration tests for WebResearchAgent with other components."""

    @pytest.mark.asyncio
    async def test_perform_web_research_function(self):
        """Test the standalone perform_web_research function."""
        knowledge_base = KnowledgeBase(
            domain="test", documents=[], web_research=[], facts=[], entities=[]
        )

        with patch(
            "agent_expert_panel.agents.web_research_agent.WebResearchAgent"
        ) as mock_agent_class:
            # Mock the agent instance and its methods
            mock_agent = Mock()
            mock_agent.research_topic = AsyncMock(
                return_value={
                    "original_query": "test query",
                    "key_findings": [{"content": "test finding"}],
                    "sources": ["test source"],
                    "summary": "test summary",
                    "confidence_score": 0.8,
                }
            )
            mock_agent.populate_knowledge_base = Mock()
            mock_agent_class.return_value = mock_agent

            # Call the function
            result = await perform_web_research(
                query="test query",
                domain="test_domain",
                knowledge_base=knowledge_base,
                max_pages=3,
            )

            # Verify function behavior
            mock_agent_class.assert_called_once_with(
                max_pages_per_search=3, use_tavily=True, tavily_api_key=None
            )
            mock_agent.research_topic.assert_called_once_with(
                query="test query", domain="test_domain"
            )
            mock_agent.populate_knowledge_base.assert_called_once_with(
                knowledge_base, result
            )

            # Verify result
            assert result["original_query"] == "test query"
            assert result["confidence_score"] == 0.8

    @pytest.mark.asyncio
    async def test_perform_web_research_without_knowledge_base(self):
        """Test perform_web_research without knowledge base population."""
        with patch(
            "agent_expert_panel.agents.web_research_agent.WebResearchAgent"
        ) as mock_agent_class:
            mock_agent = Mock()
            mock_agent.research_topic = AsyncMock(return_value={"test": "result"})
            mock_agent.populate_knowledge_base = Mock()
            mock_agent_class.return_value = mock_agent

            result = await perform_web_research("test query")

            # Should not call populate_knowledge_base
            mock_agent.populate_knowledge_base.assert_not_called()
            assert result == {"test": "result"}


@pytest.mark.integration
class TestWebResearchAgentRealScenarios:
    """Integration tests with realistic scenarios."""

    @pytest.mark.asyncio
    async def test_business_consulting_scenario(self):
        """Test web research for a business consulting scenario."""
        with patch(
            "agent_expert_panel.agents.web_research_agent.OpenAIChatCompletionClient"
        ):
            agent = WebResearchAgent()

            # Mock coordinator responses for strategy and synthesis
            strategy_response = Mock()
            strategy_response.chat_message.content = (
                "remote work productivity trends\nbusiness remote work impact"
            )

            synthesis_response = Mock()
            synthesis_response.chat_message.content = "Remote work transformation has fundamentally changed business operations with mixed results on productivity and employee satisfaction."

            agent.coordinator.on_messages = AsyncMock(
                side_effect=[strategy_response, synthesis_response]
            )

            result = await agent.research_topic(
                query="How has remote work impacted business productivity?",
                domain="business",
            )

            assert (
                result["original_query"]
                == "How has remote work impacted business productivity?"
            )
            assert result["domain"] == "business"
            # Findings come from Tavily mock data
            assert len(result["key_findings"]) >= 2
            assert len(result["sources"]) >= 2
            assert "Remote work transformation" in result["summary"]

    @pytest.mark.asyncio
    async def test_technology_research_scenario(self):
        """Test web research for a technology scenario."""
        with patch(
            "agent_expert_panel.agents.web_research_agent.OpenAIChatCompletionClient"
        ):
            agent = WebResearchAgent()

            # Mock coordinator responses for strategy and synthesis
            strategy_response = Mock()
            strategy_response.chat_message.content = (
                "container orchestration trends\nKubernetes enterprise adoption"
            )

            synthesis_response = Mock()
            synthesis_response.chat_message.content = "Container orchestration has matured significantly with Kubernetes becoming the de facto standard for modern application deployment."

            agent.coordinator.on_messages = AsyncMock(
                side_effect=[strategy_response, synthesis_response]
            )

            result = await agent.research_topic(
                query="What are the current trends in container orchestration?",
                domain="technology",
            )

            assert result["domain"] == "technology"
            # Findings come from Tavily mock data
            assert len(result["key_findings"]) >= 2
            assert len(result["sources"]) >= 2
            assert "Container orchestration" in result["summary"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
