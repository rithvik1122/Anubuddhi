#!/usr/bin/env python3
"""
Simple test script to verify the Agentic Quantum        # Create a vacuum state (Fock state with n=0)
        vacuum_state = FockState(photon_numbers=[0, 0], max_dim=10)
        logger.info(f"✅ Created vacuum state with {vacuum_state.num_modes} modes")stem is working.
This test runs without requiring actual API keys.
"""

import asyncio
import logging
from pathlib import Path
import sys
import os

# Add the src directory to the path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_basic_imports():
    """Test that all modules can be imported correctly."""
    logger.info("🧪 Testing basic imports...")
    
    try:
        from agentic_quantum.core.config import Config as AgenticQuantumConfig
        from agentic_quantum.core.system import AgenticQuantumSystem
        from agentic_quantum.agents.base_agent import BaseAgent, AgentMessage, MessageType
        from agentic_quantum.agents.designer_agent import DesignerAgent
        from agentic_quantum.agents.analyzer_agent import AnalyzerAgent
        from agentic_quantum.agents.optimizer_agent import OptimizerAgent
        from agentic_quantum.agents.knowledge_agent import KnowledgeAgent
        from agentic_quantum.agents.coordinator_agent import CoordinatorAgent
        from agentic_quantum.quantum.states import QuantumState
        from agentic_quantum.quantum.operations import QuantumOperation
        from agentic_quantum.quantum.measurements import Measurement
        
        logger.info("✅ All imports successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

async def test_configuration():
    """Test configuration loading."""
    logger.info("🔧 Testing configuration...")
    
    try:
        from agentic_quantum.core.config import Config as AgenticQuantumConfig
        config = AgenticQuantumConfig()
        
        logger.info(f"✅ Configuration loaded:")
        logger.info(f"   - Log level: {config.log_level}")
        logger.info(f"   - Debug mode: {config.debug}")
        logger.info(f"   - Max workers: {config.max_workers}")
        logger.info(f"   - Vector DB path: {config.vector_db_path}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

async def test_quantum_operations():
    """Test basic quantum operations."""
    logger.info("⚛️  Testing quantum operations...")
    
    try:
        from agentic_quantum.quantum.states import FockState
        from agentic_quantum.quantum.operations import BeamSplitter, PhaseShift
        from agentic_quantum.quantum.measurements import PhotonNumberMeasurement
        
        # Create a vacuum state (Fock state with n=0)
        vacuum_state = FockState(photon_numbers=[0, 0], max_dim=10)
        logger.info(f"✅ Created vacuum state with {vacuum_state.num_modes} modes")
        
        # Create operations
        beam_splitter = BeamSplitter(mode1=0, mode2=1, transmittance=0.5)
        phase_shift = PhaseShift(phase=0.2, mode=0)
        
        logger.info("✅ Created quantum operations")
        
        # Create measurement
        measurement = PhotonNumberMeasurement(mode=0)
        logger.info("✅ Created photon number measurement")
        
        return True
    except Exception as e:
        logger.error(f"❌ Quantum operations test failed: {e}")
        return False

async def test_agent_creation():
    """Test agent creation without LLM calls."""
    logger.info("🤖 Testing agent creation...")
    
    try:
        from agentic_quantum.agents.designer_agent import DesignerAgent
        from agentic_quantum.agents.analyzer_agent import AnalyzerAgent
        from agentic_quantum.agents.optimizer_agent import OptimizerAgent
        from agentic_quantum.agents.knowledge_agent import KnowledgeAgent
        from agentic_quantum.agents.coordinator_agent import CoordinatorAgent
        
        # Create agents with test configuration
        config = {"llm_provider": "mock"}  # Use mock provider to avoid API calls
        
        designer = DesignerAgent(config=config)
        analyzer = AnalyzerAgent(config=config)
        optimizer = OptimizerAgent(config=config)
        knowledge = KnowledgeAgent(config=config)
        coordinator = CoordinatorAgent(config=config)
        
        logger.info("✅ All agents created successfully:")
        logger.info(f"   - Designer Agent: {designer.name}")
        logger.info(f"   - Analyzer Agent: {analyzer.name}")
        logger.info(f"   - Optimizer Agent: {optimizer.name}")
        logger.info(f"   - Knowledge Agent: {knowledge.name}")
        logger.info(f"   - Coordinator Agent: {coordinator.name}")
        
        # Test agent capabilities
        logger.info("🔍 Testing agent capabilities...")
        for agent in [designer, analyzer, optimizer, knowledge, coordinator]:
            capabilities = agent.get_capabilities()
            logger.info(f"   - {agent.name}: {len(capabilities)} capabilities")
        
        return True
    except Exception as e:
        logger.error(f"❌ Agent creation test failed: {e}")
        return False

async def test_system_initialization():
    """Test system initialization."""
    logger.info("🚀 Testing system initialization...")
    
    try:
        from agentic_quantum.core.system import AgenticQuantumSystem
        from agentic_quantum.core.config import Config as AgenticQuantumConfig
        
        # Create configuration for testing
        config = AgenticQuantumConfig()
        config.llm_provider = "mock"  # Use mock provider
        
        # Initialize system
        system = AgenticQuantumSystem(config_override=config.__dict__)
        
        logger.info("✅ System initialized successfully")
        logger.info(f"   - Configuration: {type(config).__name__}")
        logger.info(f"   - System ready: {hasattr(system, 'config')}")
        
        return True
    except Exception as e:
        logger.error(f"❌ System initialization test failed: {e}")
        return False

async def test_knowledge_storage():
    """Test knowledge storage without LLM calls."""
    logger.info("💾 Testing knowledge storage...")
    
    try:
        from agentic_quantum.agents.knowledge_agent import KnowledgeAgent, KnowledgeEntry
        from datetime import datetime
        
        # Create knowledge agent
        knowledge_agent = KnowledgeAgent(config={"llm_provider": "mock"})
        
        # Create test knowledge entry
        test_entry = KnowledgeEntry(
            entry_id="test_001",
            entry_type="experiment",
            content={
                "experiment_type": "quantum_state_preparation",
                "target_state": "coherent",
                "fidelity": 0.95,
                "notes": "Test experiment for system validation"
            },
            metadata={
                "created_by": "test_system",
                "experiment_date": datetime.now().isoformat()
            },
            tags=["test", "coherent_state", "high_fidelity"]
        )
        
        # Store in cache (since we might not have ChromaDB running)
        knowledge_agent.knowledge_cache[test_entry.entry_id] = test_entry
        
        logger.info("✅ Knowledge storage test successful:")
        logger.info(f"   - Entry ID: {test_entry.entry_id}")
        logger.info(f"   - Entry type: {test_entry.entry_type}")
        logger.info(f"   - Tags: {test_entry.tags}")
        logger.info(f"   - Cache size: {len(knowledge_agent.knowledge_cache)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Knowledge storage test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and report results."""
    logger.info("🧪 Starting Agentic Quantum System Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration", test_configuration),
        ("Quantum Operations", test_quantum_operations),
        ("Agent Creation", test_agent_creation),
        ("System Initialization", test_system_initialization),
        ("Knowledge Storage", test_knowledge_storage),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running: {test_name}")
        logger.info("-" * 40)
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n🏆 Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The Agentic Quantum system is ready!")
        logger.info("\n🚀 Next steps:")
        logger.info("1. Add your API keys to .env file")
        logger.info("2. Run: python examples/complete_workflow_demo.py")
        logger.info("3. Start designing quantum experiments!")
    else:
        logger.info("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

async def main():
    """Main test function."""
    success = await run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
