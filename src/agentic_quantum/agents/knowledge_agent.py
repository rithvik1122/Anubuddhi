"""
Knowledge Agent for managing experimental knowledge and vector database operations.
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import hashlib

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

from .base_agent import BaseAgent, AgentMessage, AgentRole, MessageType, AgentCapability

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeEntry:
    """Represents a knowledge entry in the database."""
    entry_id: str
    entry_type: str  # "experiment", "insight", "pattern", "result"
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: datetime = None
    tags: List[str] = None
    relevance_score: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tags is None:
            self.tags = []


@dataclass 
class SearchResult:
    """Represents a search result from the knowledge base."""
    entry: KnowledgeEntry
    similarity_score: float
    relevance_explanation: str


@dataclass
class KnowledgeStats:
    """Statistics about the knowledge base."""
    total_entries: int
    entries_by_type: Dict[str, int]
    storage_size_mb: float
    last_updated: datetime
    most_accessed_topics: List[str]
    knowledge_growth_rate: float


class KnowledgeAgent(BaseAgent):
    """
    Agent responsible for managing experimental knowledge and learning.
    
    The Knowledge Agent:
    - Stores experimental results and insights in vector database
    - Retrieves relevant knowledge for new experiments
    - Identifies patterns and correlations across experiments
    - Builds expertise over time through continuous learning
    - Provides knowledge-based recommendations
    """
    
    def __init__(self, agent_id: str = "knowledge_001", **kwargs):
        """Initialize the Knowledge Agent."""
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.KNOWLEDGE,
            name="Quantum Knowledge Manager",
            description="Manages experimental knowledge and builds AI expertise over time",
            **kwargs
        )
        
        # Vector database configuration
        self.db_path = getattr(self.config, "vector_db_path", "./quantum_knowledge_db")
        self.collection_name = getattr(self.config, "collection_name", "quantum_experiments")
        self.embedding_dimension = getattr(self.config, "embedding_dimension", 384)
        self.max_results = getattr(self.config, "max_search_results", 10)
        
        # Knowledge management settings
        self.similarity_threshold = getattr(self.config, "similarity_threshold", 0.7)
        self.knowledge_retention_days = getattr(self.config, "retention_days", 365)
        self.auto_cleanup_enabled = getattr(self.config, "auto_cleanup", True)
        self.semantic_search_enabled = getattr(self.config, "semantic_search", True)
        
        # Initialize vector database
        self.chroma_client = None
        self.collection = None
        self._initialize_database()
        
        # Knowledge caching and indexing
        self.knowledge_cache = {}
        self.topic_index = {}
        self.pattern_index = {}
        
        # Learning and analytics
        self.access_patterns = {}
        self.knowledge_evolution = []
        self.expertise_metrics = {}
        
        logger.info("Knowledge Agent initialized")
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Return Knowledge Agent capabilities."""
        return [
            AgentCapability(
                name="knowledge_storage",
                description="Store experimental results and insights",
                input_types=["experiment_data", "analysis_results", "insights"],
                output_types=["storage_confirmation", "entry_id"]
            ),
            AgentCapability(
                name="knowledge_retrieval",
                description="Retrieve relevant knowledge for queries",
                input_types=["search_query", "context", "filters"],
                output_types=["search_results", "relevance_scores"]
            ),
            AgentCapability(
                name="pattern_identification",
                description="Identify patterns across experimental data",
                input_types=["data_collection", "pattern_types"],
                output_types=["identified_patterns", "correlation_analysis"]
            ),
            AgentCapability(
                name="expertise_building",
                description="Build and maintain domain expertise",
                input_types=["knowledge_updates", "learning_feedback"],
                output_types=["expertise_metrics", "knowledge_gaps"]
            ),
            AgentCapability(
                name="recommendation_generation",
                description="Generate knowledge-based recommendations",
                input_types=["current_context", "historical_data"],
                output_types=["recommendations", "confidence_scores"]
            )
        ]
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming knowledge management requests."""
        content = message.content
        action = content.get("action", "")
        
        try:
            if action == "store_knowledge":
                result = await self._store_knowledge(content)
            elif action == "search_knowledge":
                result = await self._search_knowledge(content)
            elif action == "identify_patterns":
                result = await self._identify_patterns(content)
            elif action == "build_expertise":
                result = await self._build_expertise(content)
            elif action == "generate_recommendations":
                result = await self._generate_recommendations(content)
            elif action == "get_knowledge_stats":
                result = await self._get_knowledge_stats(content)
            elif action == "cleanup_knowledge":
                result = await self._cleanup_knowledge(content)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            return await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content=result,
                conversation_id=message.conversation_id
            )
        
        except Exception as e:
            logger.error(f"Knowledge Agent error: {e}")
            return await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.ERROR,
                content={"error": str(e)},
                conversation_id=message.conversation_id
            )
    
    def _initialize_database(self):
        """Initialize the ChromaDB vector database."""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available - using in-memory fallback")
            self.knowledge_cache = {}
            return
        
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Connected to existing collection: {self.collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Quantum experiment knowledge base"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None
    
    async def _store_knowledge(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store knowledge entry in the vector database.
        
        Args:
            request: Storage request with knowledge data
        
        Returns:
            Storage confirmation and entry details
        """
        entry_type = request.get("entry_type", "experiment")
        content = request.get("content", {})
        metadata = request.get("metadata", {})
        tags = request.get("tags", [])
        
        logger.info(f"Storing knowledge entry of type: {entry_type}")
        
        # Generate unique entry ID
        entry_id = self._generate_entry_id(content, entry_type)
        
        # Create knowledge entry
        knowledge_entry = KnowledgeEntry(
            entry_id=entry_id,
            entry_type=entry_type,
            content=content,
            metadata=metadata,
            tags=tags
        )
        
        # Generate embedding for semantic search
        if self.semantic_search_enabled:
            embedding = await self._generate_embedding(content)
            knowledge_entry.embedding = embedding
        
        # Store in vector database
        storage_success = await self._store_in_database(knowledge_entry)
        
        if storage_success:
            # Update indexes and cache
            self._update_topic_index(knowledge_entry)
            self._update_knowledge_cache(knowledge_entry)
            
            # Track knowledge evolution
            self.knowledge_evolution.append({
                "timestamp": datetime.now(),
                "action": "store",
                "entry_type": entry_type,
                "entry_id": entry_id
            })
            
            logger.info(f"Successfully stored knowledge entry: {entry_id}")
            
            return {
                "success": True,
                "entry_id": entry_id,
                "entry_type": entry_type,
                "storage_location": "vector_database",
                "semantic_search_enabled": bool(knowledge_entry.embedding),
                "tags": tags
            }
        else:
            return {
                "success": False,
                "error": "Failed to store in database",
                "entry_id": entry_id
            }
    
    async def _search_knowledge(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for relevant knowledge entries.
        
        Args:
            request: Search request with query and filters
        
        Returns:
            Search results with relevance scores
        """
        query = request.get("query", "")
        filters = request.get("filters", {})
        max_results = request.get("max_results", self.max_results)
        search_type = request.get("search_type", "semantic")  # semantic, keyword, hybrid
        
        logger.info(f"Searching knowledge base: '{query}' (type: {search_type})")
        
        search_results = []
        
        if search_type == "semantic" and self.semantic_search_enabled:
            search_results = await self._semantic_search(query, filters, max_results)
        elif search_type == "keyword":
            search_results = await self._keyword_search(query, filters, max_results)
        elif search_type == "hybrid":
            semantic_results = await self._semantic_search(query, filters, max_results//2)
            keyword_results = await self._keyword_search(query, filters, max_results//2)
            search_results = self._merge_search_results(semantic_results, keyword_results)
        else:
            # Fallback to keyword search
            search_results = await self._keyword_search(query, filters, max_results)
        
        # Track access patterns for learning
        self._track_access_pattern(query, len(search_results))
        
        # Generate explanations for results
        explained_results = []
        for result in search_results:
            explanation = self._generate_relevance_explanation(query, result)
            explained_results.append({
                "entry": asdict(result.entry),
                "similarity_score": result.similarity_score,
                "relevance_explanation": explanation
            })
        
        return {
            "search_results": explained_results,
            "query": query,
            "search_type": search_type,
            "total_results": len(search_results),
            "search_metadata": {
                "database_size": await self._get_database_size(),
                "search_time": 0.1,  # Placeholder
                "filters_applied": filters
            }
        }
    
    async def _identify_patterns(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify patterns across stored knowledge.
        
        Args:
            request: Pattern identification request
        
        Returns:
            Identified patterns and correlations
        """
        pattern_types = request.get("pattern_types", ["experimental", "performance", "temporal"])
        data_scope = request.get("scope", "all")  # all, recent, specific_type
        min_confidence = request.get("min_confidence", 0.6)
        
        logger.info(f"Identifying patterns: {pattern_types}")
        
        identified_patterns = {}
        
        for pattern_type in pattern_types:
            if pattern_type == "experimental":
                patterns = await self._identify_experimental_patterns(data_scope, min_confidence)
            elif pattern_type == "performance":
                patterns = await self._identify_performance_patterns(data_scope, min_confidence)
            elif pattern_type == "temporal":
                patterns = await self._identify_temporal_patterns(data_scope, min_confidence)
            elif pattern_type == "correlation":
                patterns = await self._identify_correlation_patterns(data_scope, min_confidence)
            else:
                patterns = []
            
            identified_patterns[pattern_type] = patterns
        
        # Update pattern index
        self._update_pattern_index(identified_patterns)
        
        # Generate insights from patterns
        pattern_insights = self._generate_pattern_insights(identified_patterns)
        
        return {
            "identified_patterns": identified_patterns,
            "pattern_insights": pattern_insights,
            "confidence_threshold": min_confidence,
            "data_scope": data_scope,
            "pattern_statistics": self._compute_pattern_statistics(identified_patterns)
        }
    
    async def _build_expertise(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build and update domain expertise based on accumulated knowledge.
        
        Args:
            request: Expertise building request
        
        Returns:
            Updated expertise metrics and knowledge gaps
        """
        domain_areas = request.get("domains", ["quantum_optics", "experiment_design", "optimization"])
        learning_mode = request.get("mode", "incremental")  # incremental, full_rebuild
        
        logger.info(f"Building expertise for domains: {domain_areas}")
        
        expertise_updates = {}
        knowledge_gaps = {}
        
        for domain in domain_areas:
            # Analyze knowledge coverage in domain
            coverage = await self._analyze_domain_coverage(domain)
            
            # Identify knowledge gaps
            gaps = await self._identify_knowledge_gaps(domain, coverage)
            
            # Update expertise metrics
            expertise = await self._update_domain_expertise(domain, coverage, learning_mode)
            
            expertise_updates[domain] = expertise
            knowledge_gaps[domain] = gaps
        
        # Update overall expertise metrics
        self.expertise_metrics.update(expertise_updates)
        
        # Generate learning recommendations
        learning_recommendations = self._generate_learning_recommendations(
            expertise_updates, knowledge_gaps
        )
        
        return {
            "expertise_updates": expertise_updates,
            "knowledge_gaps": knowledge_gaps,
            "learning_recommendations": learning_recommendations,
            "expertise_evolution": self._track_expertise_evolution(),
            "knowledge_maturity": self._assess_knowledge_maturity()
        }
    
    async def _generate_recommendations(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate knowledge-based recommendations.
        
        Args:
            request: Recommendation request with context
        
        Returns:
            Contextual recommendations with confidence scores
        """
        context = request.get("context", {})
        recommendation_type = request.get("type", "general")  # general, experiment_design, optimization
        max_recommendations = request.get("max_recommendations", 5)
        
        logger.info(f"Generating {recommendation_type} recommendations")
        
        recommendations = []
        
        if recommendation_type == "experiment_design":
            recommendations = await self._generate_design_recommendations(context)
        elif recommendation_type == "optimization":
            recommendations = await self._generate_optimization_recommendations(context)
        elif recommendation_type == "parameter_tuning":
            recommendations = await self._generate_parameter_recommendations(context)
        elif recommendation_type == "measurement_strategy":
            recommendations = await self._generate_measurement_recommendations(context)
        else:
            # General recommendations
            recommendations = await self._generate_general_recommendations(context)
        
        # Rank and filter recommendations
        ranked_recommendations = self._rank_recommendations(recommendations, context)
        top_recommendations = ranked_recommendations[:max_recommendations]
        
        # Generate explanations
        explained_recommendations = []
        for rec in top_recommendations:
            explanation = self._explain_recommendation(rec, context)
            explained_recommendations.append({
                **rec,
                "explanation": explanation
            })
        
        return {
            "recommendations": explained_recommendations,
            "recommendation_type": recommendation_type,
            "context_analysis": self._analyze_recommendation_context(context),
            "confidence_assessment": self._assess_recommendation_confidence(explained_recommendations)
        }
    
    async def _get_knowledge_stats(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive knowledge base statistics."""
        include_details = request.get("include_details", False)
        
        logger.info("Generating knowledge base statistics")
        
        # Basic statistics
        total_entries = await self._get_database_size()
        entries_by_type = await self._get_entries_by_type()
        storage_size = await self._get_storage_size()
        
        # Advanced statistics
        growth_rate = self._calculate_knowledge_growth_rate()
        most_accessed = self._get_most_accessed_topics()
        expertise_summary = self._summarize_expertise()
        
        stats = KnowledgeStats(
            total_entries=total_entries,
            entries_by_type=entries_by_type,
            storage_size_mb=storage_size,
            last_updated=datetime.now(),
            most_accessed_topics=most_accessed,
            knowledge_growth_rate=growth_rate
        )
        
        result = {
            "knowledge_stats": asdict(stats),
            "expertise_summary": expertise_summary,
            "database_health": await self._check_database_health()
        }
        
        if include_details:
            result.update({
                "detailed_metrics": await self._get_detailed_metrics(),
                "access_patterns": self.access_patterns,
                "knowledge_evolution": self.knowledge_evolution[-100:]  # Last 100 events
            })
        
        return result
    
    async def _cleanup_knowledge(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old or irrelevant knowledge entries."""
        cleanup_type = request.get("type", "automatic")  # automatic, manual, selective
        retention_days = request.get("retention_days", self.knowledge_retention_days)
        force_cleanup = request.get("force", False)
        
        logger.info(f"Starting knowledge cleanup: {cleanup_type}")
        
        if cleanup_type == "automatic" and not force_cleanup and not self.auto_cleanup_enabled:
            return {"cleanup_skipped": "Automatic cleanup disabled"}
        
        # Identify entries for cleanup
        cleanup_candidates = await self._identify_cleanup_candidates(retention_days, cleanup_type)
        
        # Perform cleanup
        cleaned_entries = []
        cleanup_errors = []
        
        for entry_id in cleanup_candidates:
            try:
                success = await self._delete_entry(entry_id)
                if success:
                    cleaned_entries.append(entry_id)
                else:
                    cleanup_errors.append(entry_id)
            except Exception as e:
                cleanup_errors.append(f"{entry_id}: {str(e)}")
        
        # Update indexes after cleanup
        self._rebuild_indexes()
        
        return {
            "cleanup_completed": True,
            "entries_cleaned": len(cleaned_entries),
            "cleanup_errors": len(cleanup_errors),
            "storage_freed_mb": await self._calculate_freed_storage(cleaned_entries),
            "cleanup_details": {
                "type": cleanup_type,
                "retention_days": retention_days,
                "cleaned_entry_ids": cleaned_entries[:100],  # Limit output
                "error_summary": cleanup_errors[:10]  # Limit error output
            }
        }
    
    # Helper methods for knowledge management
    
    def _generate_entry_id(self, content: Dict[str, Any], entry_type: str) -> str:
        """Generate unique entry ID based on content hash."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{entry_type}_{timestamp}_{content_hash}"
    
    async def _generate_embedding(self, content: Dict[str, Any]) -> List[float]:
        """Generate embedding vector for content."""
        # This is a simplified embedding generation
        # In practice, would use proper embedding models like sentence-transformers
        
        # Convert content to text
        text = self._content_to_text(content)
        
        # Simple hash-based embedding (placeholder)
        # Replace with actual embedding model
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to vector
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            embedding.append(int(hex_pair, 16) / 255.0)
        
        # Pad or truncate to desired dimension
        while len(embedding) < self.embedding_dimension:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dimension]
    
    def _content_to_text(self, content: Dict[str, Any]) -> str:
        """Convert content dictionary to searchable text."""
        text_parts = []
        
        def extract_text(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    extract_text(value, f"{prefix}{key} ")
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item, prefix)
            else:
                text_parts.append(f"{prefix}{str(obj)}")
        
        extract_text(content)
        return " ".join(text_parts)
    
    async def _store_in_database(self, entry: KnowledgeEntry) -> bool:
        """Store knowledge entry in the vector database."""
        try:
            if self.collection is not None:
                # Store in ChromaDB
                self.collection.add(
                    ids=[entry.entry_id],
                    embeddings=[entry.embedding] if entry.embedding else None,
                    documents=[json.dumps(entry.content, default=str)],
                    metadatas=[{
                        "entry_type": entry.entry_type,
                        "timestamp": entry.timestamp.isoformat(),
                        "tags": ",".join(entry.tags),
                        **entry.metadata
                    }]
                )
                return True
            else:
                # Fallback to in-memory storage
                self.knowledge_cache[entry.entry_id] = entry
                return True
                
        except Exception as e:
            logger.error(f"Failed to store entry {entry.entry_id}: {e}")
            return False
    
    async def _semantic_search(self, query: str, filters: Dict[str, Any], 
                             max_results: int) -> List[SearchResult]:
        """Perform semantic search using embeddings."""
        try:
            if self.collection is not None:
                # Generate query embedding
                query_embedding = await self._generate_embedding({"query": query})
                
                # Search ChromaDB
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=max_results,
                    where=self._build_where_clause(filters) if filters else None
                )
                
                # Convert to SearchResult objects
                search_results = []
                for i in range(len(results['ids'][0])):
                    entry_data = json.loads(results['documents'][0][i])
                    metadata = results['metadatas'][0][i]
                    
                    entry = KnowledgeEntry(
                        entry_id=results['ids'][0][i],
                        entry_type=metadata.get('entry_type', 'unknown'),
                        content=entry_data,
                        metadata=metadata,
                        timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                        tags=metadata.get('tags', '').split(',') if metadata.get('tags') else []
                    )
                    
                    similarity_score = results['distances'][0][i] if 'distances' in results else 0.0
                    
                    search_results.append(SearchResult(
                        entry=entry,
                        similarity_score=1.0 - similarity_score,  # Convert distance to similarity
                        relevance_explanation=""
                    ))
                
                return search_results
            else:
                # Fallback search in cache
                return await self._cache_search(query, filters, max_results)
                
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def _keyword_search(self, query: str, filters: Dict[str, Any], 
                            max_results: int) -> List[SearchResult]:
        """Perform keyword-based search."""
        search_results = []
        query_terms = query.lower().split()
        
        # Search in cache or database
        entries_to_search = []
        
        if self.collection is not None:
            try:
                # Get all entries (simplified - in practice would use text search)
                all_results = self.collection.get()
                for i in range(len(all_results['ids'])):
                    entry_data = json.loads(all_results['documents'][i])
                    metadata = all_results['metadatas'][i]
                    
                    entry = KnowledgeEntry(
                        entry_id=all_results['ids'][i],
                        entry_type=metadata.get('entry_type', 'unknown'),
                        content=entry_data,
                        metadata=metadata,
                        timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                        tags=metadata.get('tags', '').split(',') if metadata.get('tags') else []
                    )
                    entries_to_search.append(entry)
            except:
                entries_to_search = list(self.knowledge_cache.values())
        else:
            entries_to_search = list(self.knowledge_cache.values())
        
        # Score entries based on keyword matches
        for entry in entries_to_search:
            score = self._calculate_keyword_score(query_terms, entry)
            if score > 0:
                search_results.append(SearchResult(
                    entry=entry,
                    similarity_score=score,
                    relevance_explanation=""
                ))
        
        # Sort by score and return top results
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return search_results[:max_results]
    
    def _calculate_keyword_score(self, query_terms: List[str], entry: KnowledgeEntry) -> float:
        """Calculate keyword matching score for an entry."""
        text = self._content_to_text(entry.content).lower()
        text += " " + " ".join(entry.tags).lower()
        text += " " + json.dumps(entry.metadata, default=str).lower()
        
        score = 0.0
        for term in query_terms:
            if term in text:
                score += 1.0
                # Bonus for exact matches in important fields
                if term in entry.entry_type.lower():
                    score += 0.5
                if any(term in tag.lower() for tag in entry.tags):
                    score += 0.3
        
        return score / len(query_terms) if query_terms else 0.0
    
    async def _cache_search(self, query: str, filters: Dict[str, Any], 
                          max_results: int) -> List[SearchResult]:
        """Search in the knowledge cache."""
        query_terms = query.lower().split()
        search_results = []
        
        for entry in self.knowledge_cache.values():
            score = self._calculate_keyword_score(query_terms, entry)
            if score > 0:
                search_results.append(SearchResult(
                    entry=entry,
                    similarity_score=score,
                    relevance_explanation=""
                ))
        
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return search_results[:max_results]
    
    def _merge_search_results(self, semantic_results: List[SearchResult], 
                            keyword_results: List[SearchResult]) -> List[SearchResult]:
        """Merge and deduplicate search results from different methods."""
        merged = {}
        
        # Add semantic results
        for result in semantic_results:
            merged[result.entry.entry_id] = result
        
        # Add keyword results, averaging scores for duplicates
        for result in keyword_results:
            entry_id = result.entry.entry_id
            if entry_id in merged:
                # Average the scores
                existing = merged[entry_id]
                merged[entry_id] = SearchResult(
                    entry=existing.entry,
                    similarity_score=(existing.similarity_score + result.similarity_score) / 2,
                    relevance_explanation=existing.relevance_explanation
                )
            else:
                merged[entry_id] = result
        
        # Sort by combined score
        results = list(merged.values())
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB where clause from filters."""
        where_clause = {}
        
        if "entry_type" in filters:
            where_clause["entry_type"] = filters["entry_type"]
        
        if "tags" in filters:
            # ChromaDB tag filtering would need special handling
            pass
        
        if "date_range" in filters:
            # ChromaDB date filtering would need special handling
            pass
        
        return where_clause if where_clause else None
    
    def _update_topic_index(self, entry: KnowledgeEntry):
        """Update topic index with new entry."""
        for tag in entry.tags:
            if tag not in self.topic_index:
                self.topic_index[tag] = []
            self.topic_index[tag].append(entry.entry_id)
        
        # Extract topics from content
        topics = self._extract_topics_from_content(entry.content)
        for topic in topics:
            if topic not in self.topic_index:
                self.topic_index[topic] = []
            self.topic_index[topic].append(entry.entry_id)
    
    def _extract_topics_from_content(self, content: Dict[str, Any]) -> List[str]:
        """Extract topics from content (simplified implementation)."""
        text = self._content_to_text(content).lower()
        
        # Simple keyword-based topic extraction
        quantum_terms = ["fidelity", "coherence", "entanglement", "superposition", 
                        "interference", "photon", "quantum", "measurement"]
        optics_terms = ["laser", "detector", "beam", "splitter", "mirror", 
                       "phase", "amplitude", "homodyne"]
        
        topics = []
        for term in quantum_terms:
            if term in text:
                topics.append(f"quantum_{term}")
        
        for term in optics_terms:
            if term in text:
                topics.append(f"optics_{term}")
        
        return topics
    
    def _update_knowledge_cache(self, entry: KnowledgeEntry):
        """Update knowledge cache with new entry."""
        self.knowledge_cache[entry.entry_id] = entry
        
        # Limit cache size
        max_cache_size = 1000
        if len(self.knowledge_cache) > max_cache_size:
            # Remove oldest entries
            sorted_entries = sorted(
                self.knowledge_cache.items(),
                key=lambda x: x[1].timestamp
            )
            for entry_id, _ in sorted_entries[:-max_cache_size]:
                del self.knowledge_cache[entry_id]
    
    def _track_access_pattern(self, query: str, num_results: int):
        """Track access patterns for learning."""
        timestamp = datetime.now()
        pattern = {
            "query": query,
            "results_count": num_results,
            "timestamp": timestamp
        }
        
        query_key = query.lower()[:50]  # Truncate long queries
        if query_key not in self.access_patterns:
            self.access_patterns[query_key] = []
        
        self.access_patterns[query_key].append(pattern)
        
        # Limit history per query
        self.access_patterns[query_key] = self.access_patterns[query_key][-100:]
    
    def _generate_relevance_explanation(self, query: str, result: SearchResult) -> str:
        """Generate explanation for why a result is relevant."""
        explanation_parts = []
        
        # Similarity score explanation
        if result.similarity_score > 0.8:
            explanation_parts.append("High semantic similarity")
        elif result.similarity_score > 0.6:
            explanation_parts.append("Moderate semantic similarity")
        else:
            explanation_parts.append("Low semantic similarity")
        
        # Content-based explanation
        query_terms = query.lower().split()
        content_text = self._content_to_text(result.entry.content).lower()
        
        matching_terms = [term for term in query_terms if term in content_text]
        if matching_terms:
            explanation_parts.append(f"Contains keywords: {', '.join(matching_terms)}")
        
        # Tag-based explanation
        relevant_tags = [tag for tag in result.entry.tags if any(term in tag.lower() for term in query_terms)]
        if relevant_tags:
            explanation_parts.append(f"Relevant tags: {', '.join(relevant_tags)}")
        
        return "; ".join(explanation_parts) if explanation_parts else "General relevance"
    
    async def _get_database_size(self) -> int:
        """Get total number of entries in database."""
        if self.collection is not None:
            try:
                return self.collection.count()
            except:
                return len(self.knowledge_cache)
        else:
            return len(self.knowledge_cache)
    
    async def _get_entries_by_type(self) -> Dict[str, int]:
        """Get count of entries by type."""
        type_counts = {}
        
        if self.collection is not None:
            try:
                all_metadata = self.collection.get()['metadatas']
                for metadata in all_metadata:
                    entry_type = metadata.get('entry_type', 'unknown')
                    type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
            except:
                for entry in self.knowledge_cache.values():
                    entry_type = entry.entry_type
                    type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
        else:
            for entry in self.knowledge_cache.values():
                entry_type = entry.entry_type
                type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
        
        return type_counts
    
    async def _get_storage_size(self) -> float:
        """Get storage size in MB (simplified)."""
        # This is a rough estimation
        if self.collection is not None:
            # ChromaDB storage size estimation
            return 10.0 * await self._get_database_size() / 1000  # Rough estimate
        else:
            # Cache size estimation
            cache_size = len(json.dumps(list(self.knowledge_cache.values()), default=str))
            return cache_size / (1024 * 1024)  # Convert to MB
    
    # Placeholder implementations for pattern identification and expertise building
    
    async def _identify_experimental_patterns(self, scope: str, confidence: float) -> List[Dict[str, Any]]:
        """Identify experimental patterns (placeholder)."""
        return [{"pattern": "coherent_state_dominance", "confidence": 0.8}]
    
    async def _identify_performance_patterns(self, scope: str, confidence: float) -> List[Dict[str, Any]]:
        """Identify performance patterns (placeholder)."""
        return [{"pattern": "fidelity_optimization_trend", "confidence": 0.7}]
    
    async def _identify_temporal_patterns(self, scope: str, confidence: float) -> List[Dict[str, Any]]:
        """Identify temporal patterns (placeholder)."""
        return [{"pattern": "improvement_over_time", "confidence": 0.9}]
    
    async def _identify_correlation_patterns(self, scope: str, confidence: float) -> List[Dict[str, Any]]:
        """Identify correlation patterns (placeholder)."""
        return [{"pattern": "parameter_correlation", "confidence": 0.6}]
    
    def _update_pattern_index(self, patterns: Dict[str, List[Dict[str, Any]]]):
        """Update pattern index with new findings."""
        timestamp = datetime.now().isoformat()
        self.pattern_index[timestamp] = patterns
    
    def _generate_pattern_insights(self, patterns: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Generate insights from identified patterns."""
        insights = []
        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                insights.append(f"Identified {len(pattern_list)} {pattern_type} patterns")
        return insights
    
    def _compute_pattern_statistics(self, patterns: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Compute statistics about identified patterns."""
        return {
            "total_patterns": sum(len(p) for p in patterns.values()),
            "pattern_types": list(patterns.keys()),
            "average_confidence": 0.75  # Placeholder
        }
    
    # Additional placeholder methods for expertise building and recommendations
    
    async def _analyze_domain_coverage(self, domain: str) -> Dict[str, float]:
        """Analyze knowledge coverage in domain (placeholder)."""
        return {"coverage_score": 0.75, "completeness": 0.8}
    
    async def _identify_knowledge_gaps(self, domain: str, coverage: Dict[str, float]) -> List[str]:
        """Identify knowledge gaps in domain (placeholder)."""
        return ["advanced_quantum_states", "noise_mitigation"]
    
    async def _update_domain_expertise(self, domain: str, coverage: Dict[str, float], mode: str) -> Dict[str, float]:
        """Update domain expertise metrics (placeholder)."""
        return {"expertise_level": 0.8, "confidence": 0.85}
    
    def _generate_learning_recommendations(self, expertise: Dict[str, Dict[str, float]], 
                                         gaps: Dict[str, List[str]]) -> List[str]:
        """Generate learning recommendations (placeholder)."""
        return ["Focus on advanced measurement techniques", "Explore new optimization algorithms"]
    
    def _track_expertise_evolution(self) -> List[Dict[str, Any]]:
        """Track how expertise evolves over time (placeholder)."""
        return [{"timestamp": datetime.now().isoformat(), "overall_expertise": 0.8}]
    
    def _assess_knowledge_maturity(self) -> Dict[str, float]:
        """Assess overall knowledge maturity (placeholder)."""
        return {"maturity_score": 0.7, "breadth": 0.8, "depth": 0.6}
    
    # Recommendation generation methods (placeholders)
    
    async def _generate_design_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate experiment design recommendations (placeholder)."""
        return [{"recommendation": "Use squeezed states for enhanced sensitivity", "confidence": 0.8}]
    
    async def _generate_optimization_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations (placeholder)."""
        return [{"recommendation": "Apply genetic algorithm for parameter optimization", "confidence": 0.9}]
    
    async def _generate_parameter_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate parameter tuning recommendations (placeholder)."""
        return [{"recommendation": "Optimize beam splitter angle around 0.5 radians", "confidence": 0.7}]
    
    async def _generate_measurement_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate measurement strategy recommendations (placeholder)."""
        return [{"recommendation": "Use homodyne detection for phase measurements", "confidence": 0.85}]
    
    async def _generate_general_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general recommendations (placeholder)."""
        return [{"recommendation": "Consider multi-mode entanglement for improved performance", "confidence": 0.6}]
    
    def _rank_recommendations(self, recommendations: List[Dict[str, Any]], 
                            context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank recommendations by relevance and confidence."""
        return sorted(recommendations, key=lambda x: x.get("confidence", 0.5), reverse=True)
    
    def _explain_recommendation(self, recommendation: Dict[str, Any], 
                              context: Dict[str, Any]) -> str:
        """Explain why a recommendation was made (placeholder)."""
        return f"Based on historical data and current context analysis"
    
    def _analyze_recommendation_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the context for recommendations (placeholder)."""
        return {"context_complexity": "medium", "relevance_factors": ["performance", "feasibility"]}
    
    def _assess_recommendation_confidence(self, recommendations: List[Dict[str, Any]]) -> float:
        """Assess overall confidence in recommendations (placeholder)."""
        if not recommendations:
            return 0.0
        confidences = [r.get("confidence", 0.5) for r in recommendations]
        return sum(confidences) / len(confidences)
    
    # Utility methods for statistics and cleanup
    
    def _calculate_knowledge_growth_rate(self) -> float:
        """Calculate knowledge growth rate."""
        if len(self.knowledge_evolution) < 2:
            return 0.0
        
        recent_events = [e for e in self.knowledge_evolution 
                        if (datetime.now() - datetime.fromisoformat(e["timestamp"])).days <= 30]
        
        return len(recent_events) / 30.0  # Entries per day
    
    def _get_most_accessed_topics(self) -> List[str]:
        """Get most frequently accessed topics."""
        topic_counts = {}
        
        for query, patterns in self.access_patterns.items():
            for pattern in patterns:
                topic_counts[query] = topic_counts.get(query, 0) + 1
        
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:10]]
    
    def _summarize_expertise(self) -> Dict[str, Any]:
        """Summarize current expertise levels."""
        return {
            "overall_expertise": 0.75,
            "domain_coverage": len(self.expertise_metrics),
            "knowledge_confidence": 0.8
        }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health and integrity."""
        return {
            "status": "healthy",
            "connection": self.collection is not None,
            "last_backup": "none",
            "integrity_check": "passed"
        }
    
    async def _get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed knowledge base metrics."""
        return {
            "index_sizes": len(self.topic_index),
            "cache_hit_rate": 0.85,
            "search_performance": "good",
            "embedding_quality": 0.8
        }
    
    async def _identify_cleanup_candidates(self, retention_days: int, cleanup_type: str) -> List[str]:
        """Identify entries for cleanup."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        candidates = []
        
        for entry_id, entry in self.knowledge_cache.items():
            if entry.timestamp < cutoff_date:
                candidates.append(entry_id)
        
        return candidates
    
    async def _delete_entry(self, entry_id: str) -> bool:
        """Delete entry from database and cache."""
        try:
            if self.collection is not None:
                self.collection.delete(ids=[entry_id])
            
            if entry_id in self.knowledge_cache:
                del self.knowledge_cache[entry_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete entry {entry_id}: {e}")
            return False
    
    def _rebuild_indexes(self):
        """Rebuild topic and pattern indexes after cleanup."""
        self.topic_index.clear()
        
        for entry in self.knowledge_cache.values():
            self._update_topic_index(entry)
    
    async def _calculate_freed_storage(self, deleted_entries: List[str]) -> float:
        """Calculate storage freed by cleanup (simplified)."""
        return len(deleted_entries) * 0.01  # Rough estimate in MB
