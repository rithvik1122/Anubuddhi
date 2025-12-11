#!/usr/bin/env python3
"""
Build Embedding Index for Toolbox Items

This script indexes all toolbox items (composites, custom components, simulations)
into ChromaDB for efficient semantic retrieval. Run this script:

1. After initial setup
2. Whenever the toolbox is significantly updated
3. If you notice retrieval returning irrelevant results

Usage:
    python build_embedding_index.py
"""

import json
from pathlib import Path
from embedding_retriever import EmbeddingRetriever, rebuild_index_from_toolbox

def main():
    print("="*80)
    print("🔨 Building Embedding Index for Toolbox Items")
    print("="*80)
    print()
    
    # Check if toolbox files exist
    toolbox_dir = Path("./toolbox")
    if not toolbox_dir.exists():
        print(f"❌ Toolbox directory not found: {toolbox_dir}")
        print("   Please ensure toolbox directory exists with JSON files.")
        return 1
    
    # Initialize retriever
    print("📦 Initializing embedding retriever...")
    retriever = EmbeddingRetriever()
    print("✅ Retriever initialized\n")
    
    # Build index from toolbox files
    print("🔍 Scanning toolbox directory for JSON files...")
    print(f"   Directory: {toolbox_dir.absolute()}\n")
    
    try:
        stats = rebuild_index_from_toolbox(retriever)
        
        print("\n" + "="*80)
        print("✅ INDEX BUILD COMPLETE")
        print("="*80)
        print(f"\n📊 Final Statistics:")
        print(f"   • Composites indexed: {stats.get('composites', 0)}")
        print(f"   • Custom components indexed: {stats.get('custom_components', 0)}")
        print(f"   • Simulation methods indexed: {stats.get('simulations', 0)}")
        print(f"\n💾 Index stored in: ./chroma_toolbox/")
        print()
        
        # Test retrieval
        if stats.get('composites', 0) > 0:
            print("🧪 Testing retrieval with sample query...")
            test_query = "quantum interferometer with photon sources"
            results = retriever.retrieve_similar_composites(test_query, top_k=3)
            print(f"   Query: '{test_query}'")
            print(f"   Results: {len(results)} items found")
            if results:
                print(f"   Top result: {results[0]}")
            print()
        
        print("✅ Embedding index is ready for use!")
        print("   The system will now use semantic search for toolbox items.")
        print()
        
        return 0
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ INDEX BUILD FAILED")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
