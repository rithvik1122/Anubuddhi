"""
Example workflow demonstrating the complete Agentic Quantum system.

This example shows how the different agents work together to design, analyze,
and optimize quantum experiments using an LLM-based multi-agent approach.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_quantum.core.config import Config
from agentic_quantum.core.system import AgenticQuantumSystem
from agentic_quantum.agents.designer_agent import DesignerAgent
from agentic_quantum.agents.analyzer_agent import AnalyzerAgent
from agentic_quantum.agents.optimizer_agent import OptimizerAgent
from agentic_quantum.agents.knowledge_agent import KnowledgeAgent
from agentic_quantum.agents.coordinator_agent import CoordinatorAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuantumExperimentWorkflowDemo:
    """
    Demonstration of the complete quantum experiment design workflow.
    
    This class shows how to:
    1. Initialize the multi-agent system
    2. Create and execute workflows for quantum experiment design
    3. Monitor progress and handle results
    4. Build knowledge over time through multiple experiments
    """
    
    def __init__(self):
        """Initialize the demo system."""
        # Initialize main system (it will load config automatically)
        self.system = AgenticQuantumSystem()
        self.config = self.system.config
        
        # Get agents from the system
        self.designer = self.system.designer_agent
        self.analyzer = self.system.analyzer_agent
        self.optimizer = self.system.optimizer_agent
        self.knowledge = self.system.knowledge_agent
        self.coordinator = self.system.coordinator_agent
        
        logger.info("Quantum Experiment Workflow Demo initialized")
    
    async def setup_system(self):
        """Set up the complete agent system."""
        logger.info("Setting up multi-agent system...")
        
        # Register all agents with the coordinator
        await self.coordinator.register_agent(self.designer)
        await self.coordinator.register_agent(self.analyzer)
        await self.coordinator.register_agent(self.optimizer)
        await self.coordinator.register_agent(self.knowledge)
        
        # Start the coordinator's workflow executor
        await self.coordinator.start_workflow_executor()
        
        logger.info("Multi-agent system setup complete")
    
    async def run_basic_experiment_design(self):
        """
        Run a basic quantum experiment design workflow.
        
        This demonstrates the core functionality of designing a new quantum
        experiment from scratch using the Designer Agent.
        """
        logger.info("🧪 Running Basic Experiment Design Workflow")
        
        # Define experiment goals
        experiment_goal = "Design a high-fidelity quantum teleportation experiment"
        objectives = [
            "Maximize teleportation fidelity",
            "Minimize resource requirements",
            "Ensure experimental feasibility"
        ]
        constraints = {
            "max_photons": 4,
            "available_detectors": ["homodyne", "photon_counting"],
            "budget_limit": 100000
        }
        
        # Create workflow
        workflow_request = {
            "action": "create_workflow",
            "experiment_goal": experiment_goal,
            "objectives": objectives,
            "constraints": constraints,
            "strategy": "sequential"
        }
        
        # Send workflow creation request to coordinator
        from agentic_quantum.agents.base_agent import AgentMessage, MessageType
        
        message = AgentMessage(
            message_id="demo_workflow_001",
            sender_id="demo_system",
            receiver_id=self.coordinator.agent_id,
            message_type=MessageType.REQUEST,
            content=workflow_request
        )
        
        # Process workflow creation
        response = await self.coordinator.process_message(message)
        
        if response and response.content.get("workflow_id"):
            workflow_id = response.content["workflow_id"]
            logger.info(f"✅ Workflow created: {workflow_id}")
            
            # Execute the workflow
            execution_request = {
                "action": "execute_workflow",
                "workflow_id": workflow_id,
                "strategy": "adaptive"
            }
            
            exec_message = AgentMessage(
                message_id="demo_exec_001",
                sender_id="demo_system",
                receiver_id=self.coordinator.agent_id,
                message_type=MessageType.REQUEST,
                content=execution_request
            )
            
            exec_response = await self.coordinator.process_message(exec_message)
            logger.info(f"📊 Workflow execution started: {exec_response.content}")
            
            # Monitor workflow progress
            await self._monitor_workflow_progress(workflow_id)
            
        else:
            logger.error("❌ Failed to create workflow")
    
    async def run_optimization_workflow(self):
        """
        Run an optimization workflow to improve existing experiments.
        
        This demonstrates how the system can learn from previous experiments
        and iteratively improve performance.
        """
        logger.info("🔧 Running Optimization Workflow")
        
        # First, store some initial experimental data
        await self._populate_knowledge_base()
        
        # Define optimization goals
        optimization_goal = "Optimize quantum state preparation for maximum purity"
        objectives = [
            "Maximize state purity",
            "Minimize preparation time",
            "Reduce noise sensitivity"
        ]
        constraints = {
            "max_optimization_iterations": 50,
            "convergence_threshold": 0.01,
            "time_limit_minutes": 30
        }
        
        # Create optimization workflow
        workflow_request = {
            "action": "create_workflow",
            "experiment_goal": optimization_goal,
            "objectives": objectives,
            "constraints": constraints,
            "strategy": "parallel"
        }
        
        from agentic_quantum.agents.base_agent import AgentMessage, MessageType
        
        message = AgentMessage(
            message_id="demo_optimization_001",
            sender_id="demo_system",
            receiver_id=self.coordinator.agent_id,
            message_type=MessageType.REQUEST,
            content=workflow_request
        )
        
        response = await self.coordinator.process_message(message)
        
        if response and response.content.get("workflow_id"):
            workflow_id = response.content["workflow_id"]
            logger.info(f"✅ Optimization workflow created: {workflow_id}")
            
            # Execute optimization
            execution_request = {
                "action": "execute_workflow",
                "workflow_id": workflow_id,
                "strategy": "priority_based"
            }
            
            exec_message = AgentMessage(
                message_id="demo_opt_exec_001",
                sender_id="demo_system",
                receiver_id=self.coordinator.agent_id,
                message_type=MessageType.REQUEST,
                content=execution_request
            )
            
            await self.coordinator.process_message(exec_message)
            await self._monitor_workflow_progress(workflow_id)
    
    async def run_comprehensive_analysis(self):
        """
        Run a comprehensive analysis workflow.
        
        This demonstrates advanced analysis capabilities including pattern
        detection and insight generation across multiple experiments.
        """
        logger.info("📈 Running Comprehensive Analysis Workflow")
        
        # Analysis goals
        analysis_goal = "Comprehensive analysis of quantum experiment performance patterns"
        objectives = [
            "Identify performance patterns",
            "Detect optimization opportunities",
            "Generate actionable insights"
        ]
        
        workflow_request = {
            "action": "create_workflow",
            "experiment_goal": analysis_goal,
            "objectives": objectives,
            "constraints": {"analysis_depth": "comprehensive"},
            "strategy": "adaptive"
        }
        
        from agentic_quantum.agents.base_agent import AgentMessage, MessageType
        
        message = AgentMessage(
            message_id="demo_analysis_001",
            sender_id="demo_system",
            receiver_id=self.coordinator.agent_id,
            message_type=MessageType.REQUEST,
            content=workflow_request
        )
        
        response = await self.coordinator.process_message(message)
        
        if response and response.content.get("workflow_id"):
            workflow_id = response.content["workflow_id"]
            logger.info(f"✅ Analysis workflow created: {workflow_id}")
            
            # Execute analysis
            execution_request = {
                "action": "execute_workflow",
                "workflow_id": workflow_id
            }
            
            exec_message = AgentMessage(
                message_id="demo_analysis_exec_001",
                sender_id="demo_system",
                receiver_id=self.coordinator.agent_id,
                message_type=MessageType.REQUEST,
                content=execution_request
            )
            
            await self.coordinator.process_message(exec_message)
            await self._monitor_workflow_progress(workflow_id)
    
    async def demonstrate_knowledge_evolution(self):
        """
        Demonstrate how the system builds knowledge over time.
        
        This shows the learning capabilities of the system through
        multiple experiment cycles.
        """
        logger.info("🧠 Demonstrating Knowledge Evolution")
        
        # Run multiple experiment cycles to build knowledge
        experiment_types = [
            "quantum_teleportation",
            "bell_state_measurement", 
            "quantum_key_distribution",
            "quantum_error_correction"
        ]
        
        for i, exp_type in enumerate(experiment_types):
            logger.info(f"🔬 Running experiment cycle {i+1}: {exp_type}")
            
            # Create workflow for this experiment type
            workflow_request = {
                "action": "create_workflow",
                "experiment_goal": f"Design and optimize {exp_type} experiment",
                "objectives": ["maximize_fidelity", "minimize_resources"],
                "constraints": {"complexity_limit": "medium"},
                "strategy": "comprehensive"
            }
            
            from agentic_quantum.agents.base_agent import AgentMessage, MessageType
            
            message = AgentMessage(
                message_id=f"demo_knowledge_{i:03d}",
                sender_id="demo_system",
                receiver_id=self.coordinator.agent_id,
                message_type=MessageType.REQUEST,
                content=workflow_request
            )
            
            response = await self.coordinator.process_message(message)
            
            if response and response.content.get("workflow_id"):
                workflow_id = response.content["workflow_id"]
                
                # Execute workflow
                execution_request = {
                    "action": "execute_workflow",
                    "workflow_id": workflow_id
                }
                
                exec_message = AgentMessage(
                    message_id=f"demo_knowledge_exec_{i:03d}",
                    sender_id="demo_system",
                    receiver_id=self.coordinator.agent_id,
                    message_type=MessageType.REQUEST,
                    content=execution_request
                )
                
                await self.coordinator.process_message(exec_message)
                
                # Brief monitoring (shortened for demo)
                await asyncio.sleep(2)  # Simulate workflow execution
                
                logger.info(f"✅ Completed experiment cycle {i+1}")
        
        # Analyze knowledge evolution
        await self._analyze_knowledge_evolution()
    
    async def _populate_knowledge_base(self):
        """Populate the knowledge base with initial experimental data."""
        logger.info("📚 Populating knowledge base with initial data")
        
        sample_experiments = [
            {
                "experiment_type": "coherent_state_preparation",
                "parameters": {"amplitude": 1.5, "phase": 0.0},
                "results": {"fidelity": 0.95, "purity": 0.98},
                "metadata": {"duration": 120, "resources": "laser,detector"}
            },
            {
                "experiment_type": "squeezed_state_generation",
                "parameters": {"squeezing_parameter": 0.8, "angle": 1.57},
                "results": {"fidelity": 0.87, "variance_reduction": 0.6},
                "metadata": {"duration": 180, "resources": "OPO,homodyne"}
            },
            {
                "experiment_type": "bell_state_preparation",
                "parameters": {"entanglement_angle": 0.785},
                "results": {"fidelity": 0.92, "concurrence": 0.89},
                "metadata": {"duration": 200, "resources": "SPDC,PBS,detectors"}
            }
        ]
        
        from agentic_quantum.agents.base_agent import AgentMessage, MessageType
        
        for i, exp_data in enumerate(sample_experiments):
            store_request = {
                "action": "store_knowledge",
                "entry_type": "experiment",
                "content": exp_data,
                "tags": [exp_data["experiment_type"], "baseline", "reference"],
                "metadata": {"source": "initial_population", "quality": "verified"}
            }
            
            message = AgentMessage(
                message_id=f"populate_{i:03d}",
                sender_id="demo_system",
                receiver_id=self.knowledge.agent_id,
                message_type=MessageType.REQUEST,
                content=store_request
            )
            
            await self.knowledge.process_message(message)
        
        logger.info("✅ Knowledge base populated with sample data")
    
    async def _monitor_workflow_progress(self, workflow_id: str):
        """Monitor workflow progress and display updates."""
        logger.info(f"👁️ Monitoring workflow progress: {workflow_id}")
        
        from agentic_quantum.agents.base_agent import AgentMessage, MessageType
        
        # Monitor for a limited time in demo
        for _ in range(5):
            monitor_request = {
                "action": "monitor_workflow",
                "workflow_id": workflow_id
            }
            
            message = AgentMessage(
                message_id=f"monitor_{workflow_id}",
                sender_id="demo_system",
                receiver_id=self.coordinator.agent_id,
                message_type=MessageType.REQUEST,
                content=monitor_request
            )
            
            response = await self.coordinator.process_message(message)
            
            if response:
                progress = response.content
                logger.info(f"📊 Progress: {progress.get('progress_percentage', 0):.1f}% "
                          f"({progress.get('completed_tasks', 0)}/{progress.get('total_tasks', 0)} tasks)")
                
                if progress.get('status') == 'completed':
                    logger.info("✅ Workflow completed successfully!")
                    break
                elif progress.get('status') == 'failed':
                    logger.error("❌ Workflow failed!")
                    break
            
            await asyncio.sleep(1)  # Check every second
    
    async def _analyze_knowledge_evolution(self):
        """Analyze how knowledge has evolved over time."""
        logger.info("🔍 Analyzing knowledge evolution")
        
        from agentic_quantum.agents.base_agent import AgentMessage, MessageType
        
        # Get knowledge statistics
        stats_request = {
            "action": "get_knowledge_stats",
            "include_details": True
        }
        
        message = AgentMessage(
            message_id="analyze_evolution",
            sender_id="demo_system",
            receiver_id=self.knowledge.agent_id,
            message_type=MessageType.REQUEST,
            content=stats_request
        )
        
        response = await self.knowledge.process_message(message)
        
        if response:
            stats = response.content
            logger.info(f"📈 Knowledge Base Stats:")
            logger.info(f"   Total entries: {stats.get('knowledge_stats', {}).get('total_entries', 0)}")
            logger.info(f"   Growth rate: {stats.get('knowledge_stats', {}).get('knowledge_growth_rate', 0):.2f} entries/day")
            logger.info(f"   Most accessed topics: {stats.get('knowledge_stats', {}).get('most_accessed_topics', [])[:3]}")
        
        # Identify patterns
        pattern_request = {
            "action": "identify_patterns",
            "pattern_types": ["experimental", "performance", "temporal"],
            "min_confidence": 0.6
        }
        
        pattern_message = AgentMessage(
            message_id="identify_patterns",
            sender_id="demo_system",
            receiver_id=self.knowledge.agent_id,
            message_type=MessageType.REQUEST,
            content=pattern_request
        )
        
        pattern_response = await self.knowledge.process_message(pattern_message)
        
        if pattern_response:
            patterns = pattern_response.content
            logger.info(f"🔗 Identified Patterns:")
            for pattern_type, pattern_list in patterns.get('identified_patterns', {}).items():
                logger.info(f"   {pattern_type}: {len(pattern_list)} patterns found")
    
    async def get_system_status(self):
        """Get comprehensive system status and performance metrics."""
        logger.info("📊 Getting system status")
        
        from agentic_quantum.agents.base_agent import AgentMessage, MessageType
        
        status_request = {
            "action": "get_system_status"
        }
        
        message = AgentMessage(
            message_id="system_status",
            sender_id="demo_system",
            receiver_id=self.coordinator.agent_id,
            message_type=MessageType.REQUEST,
            content=status_request
        )
        
        response = await self.coordinator.process_message(message)
        
        if response:
            status = response.content
            logger.info("🖥️ System Status:")
            logger.info(f"   Active workflows: {status.get('active_workflows', 0)}")
            logger.info(f"   Registered agents: {status.get('registered_agents', 0)}")
            logger.info(f"   System health: {status.get('system_health', 'unknown')}")
            
            agent_perf = status.get('agent_performance', {})
            for agent_id, metrics in agent_perf.items():
                logger.info(f"   {agent_id}: {metrics.get('success_rate', 0):.2f} success rate, "
                          f"{metrics.get('performance_score', 0):.2f} performance score")
    
    async def cleanup_system(self):
        """Clean up system resources."""
        logger.info("🧹 Cleaning up system resources")
        
        # Stop workflow executor
        await self.coordinator.stop_workflow_executor()
        
        logger.info("✅ System cleanup complete")


async def main():
    """
    Main demonstration function.
    
    This runs a complete demonstration of the Agentic Quantum system,
    showcasing all major capabilities and agent interactions.
    """
    print("🚀 Starting Agentic Quantum System Demonstration")
    print("=" * 60)
    
    # Initialize demo
    demo = QuantumExperimentWorkflowDemo()
    
    try:
        # Setup system
        await demo.setup_system()
        
        print("\n📋 Demo Agenda:")
        print("1. Basic Experiment Design")
        print("2. Optimization Workflow")
        print("3. Comprehensive Analysis")
        print("4. Knowledge Evolution")
        print("5. System Status Review")
        print()
        
        # Run demonstrations
        await demo.run_basic_experiment_design()
        print("\n" + "-" * 40 + "\n")
        
        await demo.run_optimization_workflow()
        print("\n" + "-" * 40 + "\n")
        
        await demo.run_comprehensive_analysis()
        print("\n" + "-" * 40 + "\n")
        
        await demo.demonstrate_knowledge_evolution()
        print("\n" + "-" * 40 + "\n")
        
        await demo.get_system_status()
        
        print("\n🎉 Demonstration completed successfully!")
        print("The Agentic Quantum system has demonstrated:")
        print("✅ Multi-agent collaboration")
        print("✅ Intelligent workflow orchestration")  
        print("✅ Knowledge accumulation and learning")
        print("✅ Experiment design and optimization")
        print("✅ Comprehensive analysis and insights")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        print(f"\n❌ Demo failed: {e}")
        
    finally:
        # Cleanup
        await demo.cleanup_system()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
