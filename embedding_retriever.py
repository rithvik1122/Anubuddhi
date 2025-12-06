"""
Embedding-based Retrieval for Toolbox Components and Custom Elements

Uses BGE embeddings to efficiently retrieve only relevant items from:
- Toolbox composites (learned experiments)
- Custom components
- Simulation methods

This dramatically reduces token usage compared to passing everything.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


class EmbeddingRetriever:
    """Semantic search retriever for toolbox items using BGE embeddings."""
    
    def __init__(self, db_path: str = "./chroma_toolbox"):
        """
        Initialize retriever with ChromaDB.
        
        Args:
            db_path: Path to ChromaDB storage directory
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB client with BGE embeddings
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create collections for different types
        self.composites_collection = self.client.get_or_create_collection(
            name="toolbox_composites",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.custom_components_collection = self.client.get_or_create_collection(
            name="custom_components",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.simulations_collection = self.client.get_or_create_collection(
            name="simulation_methods",
            metadata={"hnsw:space": "cosine"}
        )
    
    def index_toolbox_composites(self, composites: Dict[str, Any]):
        """
        Index all toolbox composites for semantic search.
        
        Args:
            composites: Dict of composite experiments from toolbox
        """
        if not composites:
            return
        
        # Handle nested structure
        if 'composites' in composites:
            composites = composites['composites']
        
        documents = []
        metadatas = []
        ids = []
        
        for comp_id, comp_data in composites.items():
            # Skip metadata fields (start with underscore)
            if comp_id.startswith('_'):
                continue
            
            # Skip if not a dict
            if not isinstance(comp_data, dict):
                continue
            
            # Create searchable text from composite (use 'name' not 'title')
            text = f"{comp_data.get('name', '')} {comp_data.get('description', '')} {comp_data.get('physics_explanation', '')}"
            
            # Extract full_design if available
            full_design = comp_data.get('full_design', {})
            timestamp = full_design.get('approved_timestamp', '') if full_design else ''
            
            documents.append(text)
            metadatas.append({
                'name': comp_data.get('name', ''),
                'description': comp_data.get('description', ''),
                'physics': comp_data.get('physics_explanation', ''),
                'component_count': len(comp_data.get('experiment', {}).get('steps', [])),
                'timestamp': timestamp  # For preferring newer versions
            })
            ids.append(comp_id)
        
        # Add to collection (will update if exists)
        if documents:
            self.composites_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def index_custom_components(self, custom_components: Dict):
        """
        Index custom components.
        
        Args:
            custom_components: Dict of custom components or nested with 'components' key
        """
        if not custom_components:
            return
        
        # Handle nested structure
        if 'components' in custom_components:
            custom_components = custom_components['components']
        
        documents = []
        metadatas = []
        ids = []
        
        for comp_id, comp_data in custom_components.items():
            # Skip metadata fields
            if comp_id.startswith('_'):
                continue
            
            # Skip if not a dict
            if not isinstance(comp_data, dict):
                continue
            
            # Create searchable text
            text = f"{comp_data.get('name', '')} {comp_data.get('description', '')} {comp_data.get('type', '')}"
            
            documents.append(text)
            metadatas.append({
                'name': comp_data.get('name', ''),
                'type': comp_data.get('type', ''),
                'description': comp_data.get('description', '')
            })
            ids.append(comp_id)
        
        if documents:
            self.custom_components_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def index_simulation_methods(self, simulations: Dict[str, Any]):
        """
        Index successful simulation methods.
        
        Args:
            simulations: Dict of successful simulations from toolbox
        """
        if not simulations:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for sim_id, sim_data in simulations.items():
            # Create searchable text
            text = f"{sim_data.get('title', '')} {sim_data.get('approach', '')} {sim_data.get('key_insight', '')}"
            
            documents.append(text)
            metadatas.append({
                'title': sim_data.get('title', ''),
                'approach': sim_data.get('approach', ''),
                'rating': sim_data.get('rating', 0)
            })
            ids.append(sim_id)
        
        if documents:
            self.simulations_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def retrieve_similar_composites(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve most similar composite experiments.
        When multiple versions exist (same title, different timestamps),
        prefer newer versions.
        
        Args:
            query: User's experiment request
            top_k: Number of similar composites to return
            
        Returns:
            List of composite IDs, sorted by relevance (and recency for ties)
        """
        # Check if collection is empty
        collection_count = self.composites_collection.count()
        if collection_count == 0:
            return []
        
        results = self.composites_collection.query(
            query_texts=[query],
            n_results=min(top_k * 2, collection_count)  # Get extra to filter duplicates
        )
        
        if not results['ids'] or not results['ids'][0]:
            return []
        
        ids = results['ids'][0]
        distances = results['distances'][0] if results.get('distances') else [0] * len(ids)
        metadatas = results['metadatas'][0] if results.get('metadatas') else [{}] * len(ids)
        
        # Group by name (title) to handle multiple versions
        name_groups = {}
        for i, comp_id in enumerate(ids):
            name = metadatas[i].get('name', '')
            distance = distances[i]
            timestamp = metadatas[i].get('timestamp', '')
            
            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append({
                'id': comp_id,
                'distance': distance,
                'timestamp': timestamp
            })
        
        # For each name group, keep only the most recent version
        deduplicated = []
        for name, versions in name_groups.items():
            # Sort by timestamp (newest first)
            versions.sort(key=lambda x: x['timestamp'], reverse=True)
            best = versions[0]  # Most recent
            deduplicated.append(best)
        
        # Sort by distance (lower is better)
        deduplicated.sort(key=lambda x: x['distance'])
        
        # Return top_k IDs
        return [item['id'] for item in deduplicated[:top_k]]
    
    def retrieve_similar_custom_components(self, query: str, top_k: int = 5) -> List[str]:
        """
        Retrieve most relevant custom components.
        
        Args:
            query: User's experiment request
            top_k: Number of components to return
            
        Returns:
            List of component IDs
        """
        if self.custom_components_collection.count() == 0:
            return []
        
        results = self.custom_components_collection.query(
            query_texts=[query],
            n_results=min(top_k, self.custom_components_collection.count())
        )
        
        if results['ids'] and results['ids'][0]:
            return results['ids'][0]
        return []
    
    def retrieve_similar_simulations(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve most relevant simulation methods.
        
        Args:
            query: Experiment description
            top_k: Number of simulations to return
            
        Returns:
            List of simulation IDs
        """
        if self.simulations_collection.count() == 0:
            return []
        
        results = self.simulations_collection.query(
            query_texts=[query],
            n_results=min(top_k, self.simulations_collection.count())
        )
        
        if results['ids'] and results['ids'][0]:
            return results['ids'][0]
        return []
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get count of items in each collection."""
        return {
            'composites': self.composites_collection.count(),
            'custom_components': self.custom_components_collection.count(),
            'simulations': self.simulations_collection.count()
        }


def rebuild_index_from_toolbox(retriever: EmbeddingRetriever = None,
                                 toolbox_path: str = "./toolbox/learned_composites.json",
                                 custom_path: str = "./toolbox/custom_components.json",
                                 simulation_path: str = "./toolbox/simulation_toolbox.json"):
    """
    Rebuild the embedding index from existing toolbox files.
    
    Args:
        retriever: EmbeddingRetriever instance (creates new one if None)
        toolbox_path: Path to composite experiments JSON
        custom_path: Path to custom components JSON
        simulation_path: Path to simulation toolbox JSON
    """
    if retriever is None:
        retriever = EmbeddingRetriever()
    
    # Load and index composites
    if Path(toolbox_path).exists():
        with open(toolbox_path, 'r') as f:
            composites = json.load(f)
            retriever.index_toolbox_composites(composites)
            print(f"✅ Indexed {len(composites)} composite experiments")
    
    # Load and index custom components
    if Path(custom_path).exists():
        with open(custom_path, 'r') as f:
            custom = json.load(f)
            retriever.index_custom_components(custom)
            print(f"✅ Indexed {len(custom)} custom components")
    
    # Load and index simulations
    if Path(simulation_path).exists():
        with open(simulation_path, 'r') as f:
            sims = json.load(f).get('successful_simulations', {})
            retriever.index_simulation_methods(sims)
            print(f"✅ Indexed {len(sims)} simulation methods")
    
    stats = retriever.get_collection_stats()
    print(f"\n📊 Final index stats: {stats}")
    
    return stats


if __name__ == "__main__":
    # Rebuild index from existing toolbox
    print("🔄 Rebuilding embedding index from toolbox...")
    retriever = rebuild_index_from_toolbox()
    
    # Test retrieval
    print("\n🔍 Testing retrieval...")
    query = "Design a Mach-Zehnder interferometer"
    
    similar_composites = retriever.retrieve_similar_composites(query, top_k=3)
    print(f"\nSimilar composites for '{query}':")
    for comp_id in similar_composites:
        print(f"  - {comp_id}")
    
    similar_components = retriever.retrieve_similar_custom_components(query, top_k=5)
    print(f"\nRelevant custom components:")
    for comp_id in similar_components:
        print(f"  - {comp_id}")
