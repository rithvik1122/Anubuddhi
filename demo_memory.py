"""
Demo: Memory-Augmented Agentic Design System

This demonstrates how the memory system enables:
1. Learning from past experiments
2. Reusing building blocks
3. Building complex experiments from simpler ones
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import only the memory module directly
from agentic_quantum.memory.memory_system import ExperimentMemory
import json

def demo_memory_system():
    """Demonstrate the cognitive memory system."""
    
    print("=" * 70)
    print("🧠 AGENTIC MEMORY SYSTEM DEMONSTRATION")
    print("=" * 70)
    
    # Initialize memory system
    print("\n1️⃣  Initializing memory system...")
    memory = ExperimentMemory(persist_dir="./demo_memory")
    print("✓ Memory system initialized")
    
    # Simulate storing a Bell state experiment
    print("\n2️⃣  Storing a Bell state preparation experiment...")
    bell_experiment = {
        "title": "Bell State Preparation with PBS",
        "description": "Generate maximally entangled Bell states using polarizing beam splitter",
        "physics_explanation": "Uses PBS and HWP to create |Φ+⟩ state through polarization entanglement",
        "expected_outcome": "Violates Bell inequality with S > 2",
        "components": [
            {"type": "laser", "name": "Pump Laser", "x": 0, "y": 5, "parameters": {"wavelength": "405nm", "power": "50mW"}},
            {"type": "polarizing_beam_splitter", "name": "PBS1", "x": 3, "y": 5, "angle": 45},
            {"type": "half_wave_plate", "name": "HWP1", "x": 2, "y": 5, "angle": 22.5},
            {"type": "detector", "name": "D1", "x": 5, "y": 7},
            {"type": "detector", "name": "D2", "x": 5, "y": 3}
        ]
    }
    
    exp_id_1 = memory.store_experiment(
        bell_experiment,
        user_query="Design a Bell state generator using polarization",
        conversation_context=None
    )
    print(f"✓ Stored experiment: {exp_id_1}")
    
    # Store a HOM interferometer
    print("\n3️⃣  Storing a HOM interferometer experiment...")
    hom_experiment = {
        "title": "Hong-Ou-Mandel Interferometer",
        "description": "Two-photon interference measurement",
        "physics_explanation": "Demonstrates quantum indistinguishability through interference dip",
        "expected_outcome": "Zero coincidence counts at perfect temporal overlap",
        "components": [
            {"type": "laser", "name": "Source1", "x": 0, "y": 7, "parameters": {"wavelength": "810nm"}},
            {"type": "laser", "name": "Source2", "x": 0, "y": 3, "parameters": {"wavelength": "810nm"}},
            {"type": "beam_splitter", "name": "BS1", "x": 5, "y": 5, "parameters": {"ratio": "50/50"}},
            {"type": "detector", "name": "D1", "x": 8, "y": 7},
            {"type": "detector", "name": "D2", "x": 8, "y": 3}
        ]
    }
    
    exp_id_2 = memory.store_experiment(
        hom_experiment,
        user_query="Create a Hong-Ou-Mandel interference setup",
        conversation_context=None
    )
    print(f"✓ Stored experiment: {exp_id_2}")
    
    # Store a double-slit experiment
    print("\n4️⃣  Storing a double-slit experiment...")
    ds_experiment = {
        "title": "Double-Slit Interference",
        "description": "Classic wave-particle duality demonstration",
        "physics_explanation": "Single photons create interference pattern",
        "expected_outcome": "Sinusoidal intensity pattern on screen",
        "components": [
            {"type": "laser", "name": "HeNe Laser", "x": 0, "y": 5, "parameters": {"wavelength": "632.8nm"}},
            {"type": "lens", "name": "Collimating Lens", "x": 2, "y": 5},
            {"type": "double_slit", "name": "Slits", "x": 5, "y": 5, "parameters": {"spacing": "0.5mm"}},
            {"type": "screen", "name": "Detection Screen", "x": 10, "y": 5}
        ]
    }
    
    exp_id_3 = memory.store_experiment(
        ds_experiment,
        user_query="Design a double slit experiment with HeNe laser",
        conversation_context=None
    )
    print(f"✓ Stored experiment: {exp_id_3}")
    
    # Show statistics
    print("\n5️⃣  Memory statistics:")
    stats = memory.get_statistics()
    print(f"   📁 Episodic memories (experiments): {stats['episodic_count']}")
    print(f"   🧩 Procedural memories (patterns): {stats['patterns_count']}")
    print(f"   📚 Semantic knowledge: {stats['semantic_count']}")
    
    # Demonstrate semantic search
    print("\n6️⃣  Semantic search: 'entanglement experiment'")
    similar = memory.retrieve_similar_experiments("entanglement experiment", n_results=2)
    for exp in similar:
        print(f"   → {exp['title']}")
        print(f"      Query: {exp['user_query']}")
        if exp['similarity_score']:
            print(f"      Similarity: {exp['similarity_score']:.3f}")
    
    # Retrieve building blocks
    print("\n7️⃣  Available building blocks:")
    patterns = memory.retrieve_building_blocks(n_results=10)
    for pattern in patterns:
        print(f"   🧩 {pattern['pattern_type'].replace('_', ' ').title()}")
        print(f"      {pattern['description']}")
        print(f"      Components: {', '.join(pattern['component_types'])}")
        print()
    
    # Demonstrate memory-augmented prompt
    print("\n8️⃣  Memory-augmented prompt generation:")
    print("\n   User asks: 'Design a quantum teleportation experiment'")
    print("\n   --- Augmented Prompt with Memory ---")
    augmented = memory.augment_prompt_with_memory(
        "Design a quantum teleportation experiment",
        use_similar=True,
        use_patterns=True
    )
    print(augmented)
    
    print("\n" + "=" * 70)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Capabilities Demonstrated:")
    print("  ✓ Episodic memory: Stores complete experiments")
    print("  ✓ Pattern extraction: Automatically detects building blocks")
    print("  ✓ Semantic search: Finds relevant past work")
    print("  ✓ Memory augmentation: Enhances prompts with experience")
    print("\n💡 The AI can now:")
    print("   • Remember past successful designs")
    print("   • Reuse proven building blocks")
    print("   • Compose complex experiments from simpler ones")
    print("   • Learn and improve over time!")
    print()

if __name__ == "__main__":
    demo_memory_system()
