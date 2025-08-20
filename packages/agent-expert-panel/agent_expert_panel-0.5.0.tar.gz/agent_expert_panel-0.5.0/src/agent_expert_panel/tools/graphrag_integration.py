"""
GraphRAG Integration for Agent Expert Panel

This module implements GraphRAG integration for persistent knowledge storage,
enabling the expert panel to maintain and query a structured knowledge base
across sessions using the official Microsoft GraphRAG Python SDK.
"""

import asyncio
import logging
import os
import tempfile
import yaml
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List


# Handle optional GraphRAG dependency
GRAPHRAG_AVAILABLE = False
try:
    # Import from the official GraphRAG SDK
    import graphrag  # noqa: F401

    GRAPHRAG_AVAILABLE = True
except ImportError:
    # GraphRAG is not available
    pass

logger = logging.getLogger(__name__)


class GraphRAGKnowledgeManager:
    """
    GraphRAG-powered knowledge management system for the Expert Panel.

    This class provides persistent storage and retrieval of knowledge using
    Microsoft's official GraphRAG system, enabling the panel to build and query
    a structured knowledge base across multiple sessions.
    """

    def __init__(
        self,
        workspace_dir: Path,
        domain: str = "general",
        persist_across_sessions: bool = True,
        llm_model: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        Initialize the GraphRAG Knowledge Manager.

        Args:
            workspace_dir: Directory for storing GraphRAG data and outputs
            domain: Domain context for the knowledge base
            persist_across_sessions: Whether to persist data across sessions
            llm_model: LLM model to use for GraphRAG processing
            embedding_model: Embedding model for vector representations
        """
        if not GRAPHRAG_AVAILABLE:
            raise ImportError(
                "GraphRAG is not available. Please install it with: pip install graphrag"
            )

        self.workspace_dir = Path(workspace_dir)
        self.domain = domain
        self.persist_across_sessions = persist_across_sessions
        self.llm_model = llm_model
        self.embedding_model = embedding_model

        # Create necessary directories
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.input_dir = self.workspace_dir / "input"
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir = self.workspace_dir / "output"

        # Initialize GraphRAG configuration
        self._create_config()
        self.indexed = False
        self.documents_added = 0
        self.is_initialized = False

        logger.info(f"GraphRAG Knowledge Manager initialized for domain: {domain}")

    async def initialize(self) -> bool:
        """
        Initialize the GraphRAG system.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if not GRAPHRAG_AVAILABLE:
                logger.warning("GraphRAG is not available")
                return False

            # Ensure workspace is set up
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            self.input_dir.mkdir(exist_ok=True)

            # Configuration is already created in __init__
            self.is_initialized = True
            logger.info("GraphRAG Knowledge Manager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize GraphRAG: {e}")
            self.is_initialized = False
            return False

    def _create_config(self) -> None:
        """Create GraphRAG configuration files."""
        # Create settings.yaml file for GraphRAG
        config_data = {
            "llm": {
                "api_key": "${OPENAI_API_KEY}",
                "type": "openai_chat",
                "model": self.llm_model,
                "model_supports_json": True,
                "max_tokens": 4000,
                "temperature": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "top_p": 1.0,
            },
            "parallelization": {
                "stagger": 0.3,
                "num_threads": 50,
            },
            "async_mode": "threaded",
            "embeddings": {
                "api_key": "${OPENAI_API_KEY}",
                "type": "openai_embedding",
                "model": self.embedding_model,
                "max_tokens": 8191,
            },
            "encoding_model": "cl100k_base",
            "skip_workflows": [],
            "input": {
                "type": "file",
                "file_type": "text",
                "base_dir": str(self.input_dir),
                "file_encoding": "utf-8",
                # Double $ escaping required for YAML variable substitution
                "file_pattern": ".*\\.txt$$",
            },
            "cache": {
                "type": "file",
                "base_dir": str(self.workspace_dir / "cache"),
            },
            "storage": {
                "type": "file",
                "base_dir": str(self.output_dir),
            },
            "reporting": {
                "type": "file",
                "base_dir": str(self.workspace_dir / "reports"),
            },
            "entity_extraction": {
                "prompt": "Given a text document, identify all entities and their entity types from the text and output in JSON format.",
                "entity_types": [
                    "person",
                    "organization",
                    "location",
                    "event",
                    "concept",
                ],
                "max_gleanings": 1,
            },
            "summarize_descriptions": {
                "prompt": "Given one or more entities, and a list of descriptions, all related to the same entity or group of entities, write a comprehensive description of the entity.",
                "max_length": 500,
            },
            "claim_extraction": {
                "prompt": "Given a text document, extract all factual claims from the text.",
                "description": "Any claims or facts that could be relevant for information retrieval.",
                "max_gleanings": 1,
            },
            "community_reports": {
                "prompt": "Given a list of entities that belong to the same community as well as their relationships, write a comprehensive description of the community.",
                "max_length": 1500,
            },
            "cluster_graph": {
                "max_cluster_size": 10,
            },
            "embed_graph": {
                "enabled": False,
            },
            "umap": {
                "enabled": False,
            },
        }

        # Write the configuration to a YAML file
        settings_file = self.workspace_dir / "settings.yaml"
        with open(settings_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

        self.settings_file = settings_file

    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the GraphRAG knowledge base.

        Args:
            documents: List of documents with 'title' and 'content' keys

        Returns:
            True if successful, False otherwise
        """
        try:
            # Write documents to input directory
            for i, doc in enumerate(documents):
                title = doc.get("title", f"document_{i}")
                content = doc.get("content", "")

                # Clean title for filename
                safe_title = "".join(
                    c for c in title if c.isalnum() or c in (" ", "-", "_")
                ).rstrip()
                filename = f"{safe_title}_{i}.txt"

                file_path = self.input_dir / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\n\n{content}")

                logger.info(f"Added document: {filename}")

            # Update the documents counter
            self.documents_added += len(documents)

            # Trigger indexing after adding documents
            await self._build_index()
            return True

        except Exception as e:
            logger.error(f"Error adding documents to GraphRAG: {e}")
            return False

    async def _build_index(self) -> bool:
        """Build the GraphRAG index from input documents."""
        try:
            logger.info("Building GraphRAG index...")

            # Validate workspace directory path for security
            workspace_abs = self.workspace_dir.resolve()
            if not workspace_abs.exists():
                logger.error(f"Workspace directory does not exist: {workspace_abs}")
                return False

            # Basic path traversal protection - ensure workspace is not root
            if workspace_abs == Path("/") or len(workspace_abs.parts) < 2:
                logger.error(f"Invalid workspace path for security: {workspace_abs}")
                return False

            # Run GraphRAG indexing using command line interface
            # This is the most reliable way to use GraphRAG currently
            import subprocess

            # Set environment variables for API keys
            env = os.environ.copy()
            if not env.get("OPENAI_API_KEY"):
                logger.warning("OPENAI_API_KEY not set - GraphRAG indexing may fail")

            # Run GraphRAG indexing command
            cmd = [
                "graphrag",
                "index",
                "--root",
                str(workspace_abs),
                "--config",
                str(self.settings_file),
            ]

            # Run in a thread pool since this is a blocking operation
            loop = asyncio.get_event_loop()
            try:
                result = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        env=env,
                        cwd=str(workspace_abs),
                        timeout=300,  # 5 minute timeout
                    ),
                )
            except subprocess.TimeoutExpired:
                logger.error("GraphRAG indexing timed out after 5 minutes")
                return False

            if result.returncode == 0:
                self.indexed = True
                logger.info("GraphRAG index built successfully")
                return True
            else:
                logger.error(f"GraphRAG indexing failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error building GraphRAG index: {e}")
            return False

    async def global_search(self, query: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Perform a global search across the entire knowledge graph.

        Args:
            query: Search query
            max_tokens: Maximum tokens for the response

        Returns:
            Dictionary with search results and metadata
        """
        if not self.indexed:
            logger.warning("GraphRAG index not built yet. Building now...")
            await self._build_index()

        try:
            logger.info(f"Performing global search: {query}")

            # Run GraphRAG global search using command line interface
            import subprocess

            env = os.environ.copy()

            # Use validated workspace path
            workspace_abs = self.workspace_dir.resolve()

            cmd = [
                "graphrag",
                "query",
                "--root",
                str(workspace_abs),
                "--method",
                "global",
                query,
            ]

            # Run in a thread pool since this is a blocking operation
            loop = asyncio.get_event_loop()
            try:
                result = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        env=env,
                        cwd=str(workspace_abs),
                        timeout=60,  # 1 minute timeout for queries
                    ),
                )
            except subprocess.TimeoutExpired:
                logger.error("GraphRAG global search timed out after 1 minute")
                return {
                    "query": query,
                    "error": "Search timed out",
                    "search_type": "global",
                }

            if result.returncode == 0:
                response = result.stdout.strip()
                return {
                    "query": query,
                    "response": response,
                    "context_data": {},
                    "completion_time": datetime.now().isoformat(),
                    "search_type": "global",
                }
            else:
                error_msg = result.stderr.strip() or "Unknown error occurred"
                logger.error(f"GraphRAG global search failed: {error_msg}")
                return {
                    "query": query,
                    "response": f"Search failed: {error_msg}",
                    "context_data": {},
                    "completion_time": datetime.now().isoformat(),
                    "search_type": "global",
                    "error": error_msg,
                }

        except Exception as e:
            logger.error(f"Error in global search: {e}")
            return {
                "query": query,
                "response": f"Search failed: {e}",
                "context_data": {},
                "completion_time": datetime.now().isoformat(),
                "search_type": "global",
                "error": str(e),
            }

    async def local_search(self, query: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Perform a local search for specific entities or relationships.

        Args:
            query: Search query
            max_tokens: Maximum tokens for the response

        Returns:
            Dictionary with search results and metadata
        """
        if not self.indexed:
            logger.warning("GraphRAG index not built yet. Building now...")
            await self._build_index()

        try:
            logger.info(f"Performing local search: {query}")

            # Run GraphRAG local search using command line interface
            import subprocess

            env = os.environ.copy()

            # Use validated workspace path
            workspace_abs = self.workspace_dir.resolve()

            cmd = [
                "graphrag",
                "query",
                "--root",
                str(workspace_abs),
                "--method",
                "local",
                query,
            ]

            # Run in a thread pool since this is a blocking operation
            loop = asyncio.get_event_loop()
            try:
                result = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        env=env,
                        cwd=str(workspace_abs),
                        timeout=60,  # 1 minute timeout for queries
                    ),
                )
            except subprocess.TimeoutExpired:
                logger.error("GraphRAG local search timed out after 1 minute")
                return {
                    "query": query,
                    "error": "Search timed out",
                    "search_type": "local",
                }

            if result.returncode == 0:
                response = result.stdout.strip()
                return {
                    "query": query,
                    "response": response,
                    "context_data": {},
                    "completion_time": datetime.now().isoformat(),
                    "search_type": "local",
                }
            else:
                error_msg = result.stderr.strip() or "Unknown error occurred"
                logger.error(f"GraphRAG local search failed: {error_msg}")
                return {
                    "query": query,
                    "response": f"Search failed: {error_msg}",
                    "context_data": {},
                    "completion_time": datetime.now().isoformat(),
                    "search_type": "local",
                    "error": error_msg,
                }

        except Exception as e:
            logger.error(f"Error in local search: {e}")
            return {
                "query": query,
                "response": f"Search failed: {e}",
                "context_data": {},
                "completion_time": datetime.now().isoformat(),
                "search_type": "local",
                "error": str(e),
            }

    async def hybrid_search(self, query: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Perform both global and local searches and combine results.

        Args:
            query: Search query
            max_tokens: Maximum tokens per search

        Returns:
            Dictionary with combined search results
        """
        # Run both searches concurrently
        global_result, local_result = await asyncio.gather(
            self.global_search(query, max_tokens // 2),
            self.local_search(query, max_tokens // 2),
            return_exceptions=True,
        )

        # Handle exceptions
        if isinstance(global_result, Exception):
            global_result = {
                "error": str(global_result),
                "response": "Global search failed",
            }
        if isinstance(local_result, Exception):
            local_result = {
                "error": str(local_result),
                "response": "Local search failed",
            }

        return {
            "query": query,
            "global_search": global_result,
            "local_search": local_result,
            "combined_response": f"Global: {global_result.get('response', '')}\n\nLocal: {local_result.get('response', '')}",
            "completion_time": datetime.now().isoformat(),
            "search_type": "hybrid",
        }

    async def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of the knowledge base status."""
        return {
            "domain": self.domain,
            "workspace_dir": str(self.workspace_dir),
            "documents_count": self.documents_added,
            "has_index": self.indexed,
            "is_initialized": self.is_initialized,
        }

    async def add_user_context(
        self, context: str, context_type: str = "general", session_id: str = None
    ) -> bool:
        """
        Add user context to the knowledge base.

        Args:
            context: User context information
            context_type: Type of context (e.g., "preferences", "goals", "constraints")
            session_id: Optional session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            title = (
                f"User Context ({context_type}) - {session_id}"
                if session_id
                else f"User Context ({context_type})"
            )
            documents = [{"title": title, "content": context}]
            return await self.add_documents(documents)
        except Exception as e:
            logger.error(f"Error adding user context: {e}")
            return False

    async def add_research_findings(
        self, findings: Dict[str, Any], session_id: str = None
    ) -> bool:
        """
        Add research findings to the knowledge base.

        Args:
            findings: Research findings data (dict containing original_query, summary, key_findings, sources)
            session_id: Optional session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle both dict and list inputs for backwards compatibility
            if isinstance(findings, list):
                # Legacy format - list of findings
                documents = []
                for i, finding in enumerate(findings):
                    title = (
                        f"Research Finding {i + 1} - {session_id}"
                        if session_id
                        else f"Research Finding {i + 1}"
                    )
                    content = finding.get("content", str(finding))
                    documents.append({"title": title, "content": content})
            else:
                # New format - structured research data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                title = (
                    f"research_{session_id}_{timestamp}.txt"
                    if session_id
                    else f"research_{timestamp}.txt"
                )

                # Format content from research findings
                content_parts = [
                    f"# Research Results: {findings.get('original_query', 'Unknown Query')}",
                    f"\n## Summary\n{findings.get('summary', 'No summary provided')}",
                ]

                # Add key findings
                key_findings = findings.get("key_findings", [])
                if key_findings:
                    content_parts.append("\n## Key Findings")
                    for i, finding in enumerate(key_findings, 1):
                        if isinstance(finding, dict):
                            content_parts.append(
                                f"{i}. {finding.get('content', str(finding))}"
                            )
                        else:
                            content_parts.append(f"{i}. {finding}")

                # Add sources
                sources = findings.get("sources", [])
                if sources:
                    content_parts.append("\n## Sources")
                    for i, source in enumerate(sources, 1):
                        content_parts.append(f"{i}. {source}")

                content = "\n".join(content_parts)

                # Create the document
                file_path = self.input_dir / title
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                logger.info(f"Added research findings document: {title}")
                self.documents_added += 1
                return True

            # For legacy list format, use the documents approach
            return await self.add_documents(documents)

        except Exception as e:
            logger.error(f"Error adding research findings: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            # Check if output directory exists and has data
            if not self.output_dir.exists():
                return {
                    "indexed": False,
                    "documents": 0,
                    "entities": 0,
                    "relationships": 0,
                }

            # Count input documents
            doc_count = (
                len(list(self.input_dir.glob("*.txt")))
                if self.input_dir.exists()
                else 0
            )

            # Try to read basic stats from GraphRAG output
            stats = {
                "indexed": self.indexed,
                "documents": doc_count,
                "domain": self.domain,
                "workspace_dir": str(self.workspace_dir),
                "last_updated": datetime.now().isoformat(),
            }

            # Try to get more detailed stats from GraphRAG output files
            try:
                # Look for entity and relationship data in parquet files
                parquet_files = list(self.output_dir.glob("**/*.parquet"))

                if parquet_files:
                    try:
                        import pandas as pd

                        # Look for entities
                        entity_files = [
                            f for f in parquet_files if "entities" in f.name.lower()
                        ]
                        if entity_files:
                            entities_df = pd.read_parquet(entity_files[0])
                            stats["entities"] = len(entities_df)

                        # Look for relationships
                        rel_files = [
                            f
                            for f in parquet_files
                            if "relationships" in f.name.lower()
                        ]
                        if rel_files:
                            relationships_df = pd.read_parquet(rel_files[0])
                            stats["relationships"] = len(relationships_df)

                    except ImportError:
                        logger.debug("pandas not available for reading parquet files")
                        stats["entities"] = "unknown"
                        stats["relationships"] = "unknown"

            except Exception as e:
                logger.debug(f"Could not read detailed stats: {e}")
                stats["entities"] = "unknown"
                stats["relationships"] = "unknown"

            return stats

        except Exception as e:
            logger.error(f"Error getting GraphRAG stats: {e}")
            return {"error": str(e), "indexed": False}


class LegacyKnowledgeAdapter:
    """
    Adapter to make GraphRAGKnowledgeManager compatible with legacy KnowledgeBase interface.
    """

    def __init__(self, graphrag_manager: GraphRAGKnowledgeManager):
        """Initialize with a GraphRAG knowledge manager."""
        self.graphrag_manager = graphrag_manager
        self.logger = logging.getLogger(__name__)

    async def query_knowledge(self, query: str, search_type: str = "hybrid") -> str:
        """
        Query the GraphRAG knowledge base.

        Args:
            query: Query string
            search_type: Type of search ("global", "local", or "hybrid")

        Returns:
            Response string from GraphRAG
        """
        try:
            if search_type == "global":
                result = await self.graphrag_manager.global_search(query)
            elif search_type == "local":
                result = await self.graphrag_manager.local_search(query)
            else:  # hybrid
                result = await self.graphrag_manager.hybrid_search(query)
                return result.get("combined_response", "No results found")

            return result.get("response", "No results found")

        except Exception as e:
            self.logger.error(f"Error querying GraphRAG knowledge: {e}")
            return f"Knowledge query failed: {e}"

    async def add_knowledge(self, content: str, source: str = "expert_panel") -> bool:
        """
        Add knowledge to the GraphRAG system.

        Args:
            content: Content to add to knowledge base
            source: Source identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            documents = [{"title": f"Knowledge from {source}", "content": content}]
            return await self.graphrag_manager.add_documents(documents)
        except Exception as e:
            self.logger.error(f"Error adding knowledge to GraphRAG: {e}")
            return False

    async def migrate_knowledge_base(
        self, knowledge_base, session_id: str = None
    ) -> bool:
        """
        Migrate a complete knowledge base to GraphRAG.

        Args:
            knowledge_base: KnowledgeBase object to migrate
            session_id: Optional session identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            success = True

            # Add user context if available
            if hasattr(knowledge_base, "summary") and knowledge_base.summary:
                context_success = await self.graphrag_manager.add_user_context(
                    knowledge_base.summary, session_id
                )
                success = success and context_success

            # Add research findings
            if hasattr(knowledge_base, "web_research") and knowledge_base.web_research:
                findings_success = await self.graphrag_manager.add_research_findings(
                    knowledge_base.web_research, session_id
                )
                success = success and findings_success

            # Add documents
            if hasattr(knowledge_base, "documents") and knowledge_base.documents:
                docs_success = await self.graphrag_manager.add_documents(
                    knowledge_base.documents
                )
                success = success and docs_success

            # Add facts as documents
            if hasattr(knowledge_base, "facts") and knowledge_base.facts:
                fact_docs = [
                    {"title": f"Fact {i + 1}", "content": fact.get("fact", str(fact))}
                    for i, fact in enumerate(knowledge_base.facts)
                ]
                facts_success = await self.graphrag_manager.add_documents(fact_docs)
                success = success and facts_success

            return success

        except Exception as e:
            self.logger.error(f"Error migrating knowledge base: {e}")
            return False


async def create_graphrag_knowledge_manager(
    domain: str,
    workspace_dir: Path | None = None,
    persist_across_sessions: bool = True,
    **kwargs,
) -> GraphRAGKnowledgeManager | None:
    """
    Create and initialize a GraphRAG Knowledge Manager.

    Args:
        domain: Domain context for the knowledge base
        workspace_dir: Directory for GraphRAG workspace
        persist_across_sessions: Whether to persist data
        **kwargs: Additional configuration options

    Returns:
        Initialized GraphRAGKnowledgeManager or None if unavailable
    """
    if not GRAPHRAG_AVAILABLE:
        logger.warning("GraphRAG is not available - cannot create knowledge manager")
        return None

    try:
        if workspace_dir is None:
            workspace_dir = Path(tempfile.mkdtemp(prefix=f"graphrag_{domain}_"))

        manager = GraphRAGKnowledgeManager(
            workspace_dir=workspace_dir,
            domain=domain,
            persist_across_sessions=persist_across_sessions,
            **kwargs,
        )

        logger.info(f"GraphRAG Knowledge Manager created for domain: {domain}")
        return manager

    except Exception as e:
        logger.error(f"Failed to create GraphRAG Knowledge Manager: {e}")
        return None


# Export the main classes and functions
__all__ = [
    "GraphRAGKnowledgeManager",
    "LegacyKnowledgeAdapter",
    "create_graphrag_knowledge_manager",
    "GRAPHRAG_AVAILABLE",
]
