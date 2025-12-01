"""
Agentic Memory System for Quantum Experiment Design
Implements episodic, semantic, and procedural memory.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sentence-transformers, fall back to simple embedder if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using fallback embedder")


class BGEEmbedder:
    """
    Professional semantic embedder using BGE-base-en-v1.5.
    - 110M parameters
    - 84.7% retrieval accuracy
    - 768-dimensional embeddings
    - Understands scientific and technical language
    """
    def __init__(self):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers is required for BGEEmbedder")
        
        # Load BGE-base-en-v1.5 model (will download on first use, ~440MB)
        logger.info("Loading BGE-base-en-v1.5 embedding model...")
        self.model = SentenceTransformer('BAAI/bge-base-en-v1.5')
        logger.info("✓ BGE embedder loaded successfully")
    
    def name(self) -> str:
        """Return embedder name for ChromaDB."""
        return "bge-base-en-v1.5"
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """
        Embed texts using BGE model.
        Automatically handles batching and GPU if available.
        """
        # BGE models benefit from instruction prefix for queries
        # For storage, we use the text as-is
        embeddings = self.model.encode(
            input,
            normalize_embeddings=True,  # Important for cosine similarity
            show_progress_bar=False
        )
        return embeddings.tolist()


class ExperimentMemory:
    """
    Cognitive memory system for quantum experiment design.
    
    Three memory types:
    1. Episodic: Specific past designs and conversations
    2. Semantic: General knowledge about components and physics
    3. Procedural: Design patterns and building blocks
    """
    
    def __init__(self, persist_dir: str = "./memory"):
        """
        Initialize the memory system with BGE professional embeddings.
        
        Args:
            persist_dir: Directory to store memory database
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True, parents=True)
        
        # Create BGE embedder (will download model on first use, ~440MB one-time)
        logger.info("Initializing BGE-base-en-v1.5 embedder for semantic search...")
        self.embedder = BGEEmbedder()
        
        # Initialize ChromaDB client with new API
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Create collections for different memory types with custom embedder
        self.episodic_memory = self.client.get_or_create_collection(
            name="episodic_experiments",
            metadata={
                "description": "Past experimental designs with full context",
                "type": "episodic"
            },
            embedding_function=self.embedder
        )
        
        self.semantic_memory = self.client.get_or_create_collection(
            name="semantic_knowledge",
            metadata={
                "description": "Component knowledge and physics principles",
                "type": "semantic"
            },
            embedding_function=self.embedder
        )
        
        self.procedural_memory = self.client.get_or_create_collection(
            name="procedural_patterns",
            metadata={
                "description": "Design patterns and reusable building blocks",
                "type": "procedural"
            },
            embedding_function=self.embedder
        )
        
        logger.info("✓ Memory system initialized with BGE-base-en-v1.5 (professional semantic embeddings)")

    def get_embedding_info(self) -> Dict[str, Any]:
        """
        Get information about the current embedding model for UI display.
        
        Returns:
            Dictionary with model info
        """
        return {
            "model": "BGE-base-en-v1.5",
            "type": "BAAI General Embedding",
            "parameters": "110M",
            "dimensions": 768,
            "accuracy": "84.7%",
            "description": "Professional semantic embeddings for scientific text"
        }
    
    def store_experiment(self, 
                        experiment_data: Dict[str, Any],
                        user_query: str,
                        conversation_context: Optional[List[Dict]] = None) -> str:
        """
        Store a complete experiment in episodic memory.
        
        Args:
            experiment_data: Full experiment design with components, beam paths, etc.
            user_query: Original user request
            conversation_context: Full conversation history
            
        Returns:
            Unique experiment ID
        """
        timestamp = datetime.now().isoformat()
        exp_id = f"exp_{datetime.now().timestamp()}"
        
        # Extract key information for embedding
        title = experiment_data.get('title', 'Untitled Experiment')
        description = experiment_data.get('description', '')
        physics = experiment_data.get('physics_explanation', '')
        outcome = experiment_data.get('expected_outcome', '')
        
        # Create document for semantic search - ONLY user query for similarity matching
        # We store full experiment data in metadata, but search only on user query
        document = user_query
        
        # Extract components for indexing
        components = experiment_data.get('components', [])
        component_types = [c.get('type', 'unknown') for c in components]
        component_names = [c.get('name', '') for c in components]
        
        # Store in episodic memory
        metadata = {
            "experiment_id": exp_id,
            "timestamp": timestamp,
            "user_query": user_query,
            "title": title,
            "description": description,
            "num_components": len(components),
            "component_types": json.dumps(list(set(component_types))),
            "component_names": json.dumps(component_names),
            "has_conversation": conversation_context is not None,
            "full_data": json.dumps(experiment_data)
        }
        
        self.episodic_memory.add(
            documents=[document],
            metadatas=[metadata],
            ids=[exp_id]
        )
        
        logger.info(f"Stored experiment {exp_id}: {title}")
        
        # Extract and store building blocks
        self._extract_building_blocks(experiment_data, exp_id)
        
        return exp_id
    
    def _extract_building_blocks(self, experiment_data: Dict, source_exp_id: str):
        """
        Extract reusable patterns/modules from an experiment.
        
        Examples:
        - Bell state preparation module (PBS + HWP)
        - HOM interferometer setup
        - Beam expansion telescope
        - Detection setup
        """
        components = experiment_data.get('components', [])
        
        # Pattern detection: Look for common functional modules
        patterns = self._detect_patterns(components)
        
        for pattern in patterns:
            pattern_id = f"pattern_{datetime.now().timestamp()}_{pattern['type']}"
            
            document = f"""
            Pattern Type: {pattern['type']}
            Description: {pattern['description']}
            Components: {', '.join(pattern['component_types'])}
            Use Case: {pattern['use_case']}
            """
            
            metadata = {
                "pattern_id": pattern_id,
                "pattern_type": pattern['type'],
                "source_experiment": source_exp_id,
                "component_types": json.dumps(pattern['component_types']),
                "description": pattern['description'],
                "components_json": json.dumps(pattern['components']),
                "timestamp": datetime.now().isoformat()
            }
            
            self.procedural_memory.add(
                documents=[document],
                metadatas=[metadata],
                ids=[pattern_id]
            )
            
            logger.info(f"Extracted pattern: {pattern['type']}")
    
    def _detect_patterns(self, components: List[Dict]) -> List[Dict]:
        """
        Detect common experimental patterns in component list.
        
        Returns:
            List of detected patterns with their components
        """
        patterns = []
        component_types = [c.get('type', '') for c in components]
        
        # Pattern 1: Bell State Preparation (PBS + HWP + Source)
        if 'polarizing_beam_splitter' in component_types and 'half_wave_plate' in component_types:
            bell_components = [c for c in components if c.get('type') in 
                             ['polarizing_beam_splitter', 'half_wave_plate', 'source', 'laser']]
            if bell_components:
                patterns.append({
                    'type': 'bell_state_preparation',
                    'description': 'Bell state preparation using PBS and HWP',
                    'component_types': ['polarizing_beam_splitter', 'half_wave_plate', 'source'],
                    'use_case': 'Quantum entanglement generation',
                    'components': bell_components
                })
        
        # Pattern 2: HOM Interferometer (BS + 2 detectors)
        if 'beam_splitter' in component_types and component_types.count('detector') >= 2:
            hom_components = [c for c in components if c.get('type') in 
                            ['beam_splitter', 'detector', 'source']]
            if len(hom_components) >= 3:
                patterns.append({
                    'type': 'hom_interferometer',
                    'description': 'Hong-Ou-Mandel interferometer setup',
                    'component_types': ['beam_splitter', 'detector', 'detector'],
                    'use_case': 'Two-photon interference measurement',
                    'components': hom_components
                })
        
        # Pattern 3: Beam Expansion (2 lenses)
        lenses = [c for c in components if 'lens' in c.get('type', '').lower()]
        if len(lenses) >= 2:
            patterns.append({
                'type': 'beam_expansion',
                'description': 'Beam expansion telescope',
                'component_types': ['lens', 'lens'],
                'use_case': 'Beam size control and collimation',
                'components': lenses[:2]
            })
        
        # Pattern 4: Double Slit Setup
        if 'double_slit' in component_types and 'screen' in component_types:
            ds_components = [c for c in components if c.get('type') in 
                           ['double_slit', 'screen', 'source', 'laser', 'lens']]
            patterns.append({
                'type': 'double_slit_interference',
                'description': 'Double-slit interference experiment',
                'component_types': ['source', 'double_slit', 'screen'],
                'use_case': 'Wave-particle duality demonstration',
                'components': ds_components
            })
        
        return patterns
    
    def get_all_experiments(self) -> List[Dict]:
        """
        Get ALL stored experiments without any similarity filtering.
        Returns complete list for LLM evaluation.
        
        Returns:
            List of all experiments with full metadata
        """
        try:
            # Get all documents from episodic memory
            results = self.episodic_memory.get()
            
            experiments = []
            if results['ids']:
                for idx, exp_id in enumerate(results['ids']):
                    metadata = results['metadatas'][idx] if results.get('metadatas') else {}
                    
                    # Handle list or dict metadata
                    if isinstance(metadata, list):
                        metadata = metadata[0] if metadata else {}
                    
                    experiments.append({
                        'experiment_id': exp_id,
                        'title': metadata.get('title', 'N/A') if isinstance(metadata, dict) else 'N/A',
                        'description': metadata.get('description', 'N/A') if isinstance(metadata, dict) else 'N/A',
                        'user_query': metadata.get('user_query', 'N/A') if isinstance(metadata, dict) else 'N/A',
                        'timestamp': metadata.get('timestamp', 'N/A') if isinstance(metadata, dict) else 'N/A',
                        'human_approved': metadata.get('human_approved', False) if isinstance(metadata, dict) else False,
                        'full_data': json.loads(metadata.get('full_data', '{}')) if isinstance(metadata, dict) else {},
                        'document': results['documents'][idx] if results.get('documents') else ''
                    })
            
            logger.info(f"Retrieved {len(experiments)} total experiments from memory")
            return experiments
        except Exception as e:
            logger.error(f"Error retrieving all experiments: {e}")
            return []
    
    def retrieve_similar_experiments(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Find similar past experiments using semantic search.
        
        Args:
            query: Natural language query or experiment description
            n_results: Number of results to return
            
        Returns:
            List of similar experiments with metadata
        """
        results = self.episodic_memory.query(
            query_texts=[query],
            n_results=n_results
        )
        
        experiments = []
        if results['ids']:
            for idx, exp_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][idx]
                # Metadata might be a list or dict depending on ChromaDB version
                if isinstance(metadata, list):
                    metadata = metadata[0] if metadata else {}
                
                experiments.append({
                    'experiment_id': exp_id,
                    'title': metadata.get('title', 'N/A') if isinstance(metadata, dict) else 'N/A',
                    'description': metadata.get('description', 'N/A') if isinstance(metadata, dict) else 'N/A',
                    'user_query': metadata.get('user_query', 'N/A') if isinstance(metadata, dict) else 'N/A',
                    'timestamp': metadata.get('timestamp', 'N/A') if isinstance(metadata, dict) else 'N/A',
                    'similarity_score': 1.0 - results['distances'][0][idx] if results.get('distances') else None,
                    'full_data': json.loads(metadata.get('full_data', '{}')) if isinstance(metadata, dict) else {},
                    'document': results['documents'][0][idx]
                })
        
        logger.info(f"Retrieved {len(experiments)} similar experiments for: {query}")
        return experiments
    
    def retrieve_building_blocks(self, pattern_type: Optional[str] = None, 
                                 query: Optional[str] = None,
                                 n_results: int = 5) -> List[Dict]:
        """
        Retrieve reusable design patterns/building blocks.
        
        Args:
            pattern_type: Specific pattern type to retrieve
            query: Natural language query for semantic search
            n_results: Number of results
            
        Returns:
            List of building blocks with full component details
        """
        if pattern_type:
            # Filter by pattern type
            results = self.procedural_memory.get(
                where={"pattern_type": pattern_type}
            )
        elif query:
            # Semantic search
            results = self.procedural_memory.query(
                query_texts=[query],
                n_results=n_results
            )
        else:
            # Get recent patterns
            results = self.procedural_memory.get(
                limit=n_results
            )
        
        patterns = []
        if results.get('ids'):
            ids = results['ids'] if isinstance(results['ids'], list) else results['ids'][0]
            metadatas = results['metadatas'] if isinstance(results['metadatas'], list) else results['metadatas'][0]
            
            for idx, pattern_id in enumerate(ids):
                metadata = metadatas[idx]
                # Handle metadata being a list
                if isinstance(metadata, list):
                    metadata = metadata[0] if metadata else {}
                
                patterns.append({
                    'pattern_id': pattern_id,
                    'pattern_type': metadata.get('pattern_type', 'unknown') if isinstance(metadata, dict) else 'unknown',
                    'description': metadata.get('description', '') if isinstance(metadata, dict) else '',
                    'component_types': json.loads(metadata.get('component_types', '[]')) if isinstance(metadata, dict) else [],
                    'components': json.loads(metadata.get('components_json', '[]')) if isinstance(metadata, dict) else [],
                    'source_experiment': metadata.get('source_experiment', 'N/A') if isinstance(metadata, dict) else 'N/A'
                })
        
        logger.info(f"Retrieved {len(patterns)} building blocks")
        return patterns
    
    def get_conversation_context(self, n_recent: int = 5) -> List[Dict]:
        """
        Retrieve recent conversation context for continuity.
        
        Args:
            n_recent: Number of recent experiments to include
            
        Returns:
            List of recent experiments with conversation data
        """
        # Get most recent experiments
        all_experiments = self.episodic_memory.get(
            limit=n_recent,
            include=['metadatas', 'documents']
        )
        
        context = []
        if all_experiments.get('ids'):
            for idx, exp_id in enumerate(all_experiments['ids']):
                metadata = all_experiments['metadatas'][idx]
                context.append({
                    'experiment_id': exp_id,
                    'title': metadata.get('title', 'N/A'),
                    'user_query': metadata.get('user_query', 'N/A'),
                    'timestamp': metadata.get('timestamp', 'N/A')
                })
        
        return context
    
    def augment_prompt_with_memory(self, user_query: str, 
                                   use_similar: bool = True,
                                   use_patterns: bool = True) -> str:
        """
        Augment user query with relevant memory context.
        
        This is the key to making the AI "experienced" - it sees relevant
        past work and can build upon it.
        
        Args:
            user_query: Current user request
            use_similar: Include similar past experiments
            use_patterns: Include relevant building blocks
            
        Returns:
            Augmented prompt with memory context
        """
        augmented_sections = []
        
        if use_similar:
            similar = self.retrieve_similar_experiments(user_query, n_results=3)
            if similar:
                augmented_sections.append("## Relevant Past Experience:\n")
                for exp in similar[:2]:  # Top 2 most relevant
                    augmented_sections.append(f"""
### Past Design: {exp['title']}
- Original request: {exp['user_query']}
- Description: {exp['description']}
- Components used: {len(exp['full_data'].get('components', []))} components
""")
        
        if use_patterns:
            # Try to find relevant patterns
            patterns = self.retrieve_building_blocks(query=user_query, n_results=3)
            if patterns:
                augmented_sections.append("\n## Available Building Blocks:\n")
                for pattern in patterns:
                    augmented_sections.append(f"""
### {pattern['pattern_type'].replace('_', ' ').title()}
- Description: {pattern['description']}
- Components: {', '.join(pattern['component_types'])}
- You can reuse this pattern by adapting these components:
{json.dumps(pattern['components'], indent=2)}
""")
        
        if augmented_sections:
            context = "\n".join(augmented_sections)
            return f"""{context}

---

## Current User Request:
{user_query}

**Instructions**: Use your experience from past designs and available building blocks to create an optimized design. If a building block is relevant, adapt and reuse it rather than starting from scratch.
"""
        
        return user_query
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            'episodic_count': self.episodic_memory.count(),
            'patterns_count': self.procedural_memory.count(),
            'semantic_count': self.semantic_memory.count()
        }
