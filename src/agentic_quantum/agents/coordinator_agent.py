"""
Coordinator Agent for orchestrating multi-agent quantum experiment design workflows.
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from .base_agent import BaseAgent, AgentMessage, AgentRole, MessageType, AgentCapability
from .designer_agent import DesignerAgent
from .analyzer_agent import AnalyzerAgent  
from .optimizer_agent import OptimizerAgent
from .knowledge_agent import KnowledgeAgent

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class WorkflowTask:
    """Represents a task in the workflow."""
    task_id: str
    task_type: str  # "design", "analyze", "optimize", "knowledge"
    target_agent: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class WorkflowPlan:
    """Represents a complete workflow execution plan."""
    workflow_id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    progress_percentage: float = 0.0
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        self.total_tasks = len(self.tasks)


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for individual agents."""
    agent_id: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    last_active: Optional[datetime] = None
    performance_score: float = 0.0


class CoordinatorAgent(BaseAgent):
    """
    Central coordinator agent for orchestrating multi-agent workflows.
    
    The Coordinator Agent:
    - Plans and executes complex multi-agent workflows
    - Manages task dependencies and scheduling
    - Monitors agent performance and system health
    - Handles error recovery and fault tolerance
    - Optimizes workflow execution strategies
    - Provides system-wide orchestration and control
    """
    
    def __init__(self, agent_id: str = "coordinator_001", **kwargs):
        """Initialize the Coordinator Agent."""
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.COORDINATOR,
            name="Quantum Workflow Coordinator",
            description="Orchestrates multi-agent quantum experiment design workflows",
            **kwargs
        )
        
        # Workflow management
        self.active_workflows: Dict[str, WorkflowPlan] = {}
        self.workflow_history: List[WorkflowPlan] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Agent management
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.agent_performance: Dict[str, AgentPerformanceMetrics] = {}
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}
        
        # Execution control
        self.max_concurrent_tasks = getattr(self.config, "max_concurrent_tasks", 5)
        self.task_timeout = getattr(self.config, "task_timeout_seconds", 300)
        self.retry_delays = [1, 2, 5, 10]  # Exponential backoff
        self.workflow_executor = None
        
        # Performance monitoring
        self.system_metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_workflow_duration": 0.0,
            "system_uptime": datetime.now(),
            "cpu_usage": 0.0,
            "memory_usage": 0.0
        }
        
        # Strategy and optimization
        self.execution_strategies = {
            "sequential": self._execute_sequential,
            "parallel": self._execute_parallel,
            "adaptive": self._execute_adaptive,
            "priority_based": self._execute_priority_based
        }
        
        self.default_strategy = getattr(self.config, "default_execution_strategy", "adaptive")
        
        logger.info("Coordinator Agent initialized")
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Return Coordinator Agent capabilities."""
        return [
            AgentCapability(
                name="workflow_planning",
                description="Plan and create multi-agent workflows",
                input_types=["experiment_goals", "constraints", "preferences"],
                output_types=["workflow_plan", "task_schedule"]
            ),
            AgentCapability(
                name="workflow_execution",
                description="Execute and monitor workflow progress",
                input_types=["workflow_plan", "execution_strategy"],
                output_types=["execution_status", "progress_updates"]
            ),
            AgentCapability(
                name="agent_coordination",
                description="Coordinate communication between agents",
                input_types=["agent_messages", "coordination_requests"],
                output_types=["coordinated_actions", "agent_assignments"]
            ),
            AgentCapability(
                name="performance_monitoring",
                description="Monitor system and agent performance",
                input_types=["performance_data", "metrics_request"],
                output_types=["performance_metrics", "optimization_suggestions"]
            ),
            AgentCapability(
                name="error_recovery",
                description="Handle errors and implement recovery strategies",
                input_types=["error_reports", "failure_conditions"],
                output_types=["recovery_actions", "corrective_measures"]
            )
        ]
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process coordination requests and workflow commands."""
        content = message.content
        action = content.get("action", "")
        
        try:
            if action == "create_workflow":
                result = await self._create_workflow(content)
            elif action == "execute_workflow":
                result = await self._execute_workflow(content)
            elif action == "monitor_workflow":
                result = await self._monitor_workflow(content)
            elif action == "pause_workflow":
                result = await self._pause_workflow(content)
            elif action == "resume_workflow":
                result = await self._resume_workflow(content)
            elif action == "cancel_workflow":
                result = await self._cancel_workflow(content)
            elif action == "register_agent":
                result = await self._register_agent(content)
            elif action == "get_system_status":
                result = await self._get_system_status(content)
            elif action == "optimize_performance":
                result = await self._optimize_performance(content)
            elif action == "handle_error":
                result = await self._handle_error(content)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            return await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content=result,
                conversation_id=message.conversation_id
            )
        
        except Exception as e:
            logger.error(f"Coordinator Agent error: {e}")
            return await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.ERROR,
                content={"error": str(e)},
                conversation_id=message.conversation_id
            )
    
    async def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator."""
        self.registered_agents[agent.agent_id] = agent
        self.agent_capabilities[agent.agent_id] = agent.get_capabilities()
        self.agent_performance[agent.agent_id] = AgentPerformanceMetrics(
            agent_id=agent.agent_id
        )
        
        logger.info(f"Registered agent: {agent.agent_id} ({agent.role.value})")
    
    async def start_workflow_executor(self):
        """Start the workflow execution engine."""
        if self.workflow_executor is None:
            self.workflow_executor = asyncio.create_task(self._workflow_execution_loop())
            logger.info("Workflow executor started")
    
    async def stop_workflow_executor(self):
        """Stop the workflow execution engine."""
        if self.workflow_executor:
            self.workflow_executor.cancel()
            try:
                await self.workflow_executor
            except asyncio.CancelledError:
                pass
            self.workflow_executor = None
            logger.info("Workflow executor stopped")
    
    async def _create_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workflow plan.
        
        Args:
            request: Workflow creation request
        
        Returns:
            Created workflow plan details
        """
        experiment_goal = request.get("experiment_goal", "")
        objectives = request.get("objectives", [])
        constraints = request.get("constraints", {})
        strategy = request.get("strategy", self.default_strategy)
        
        logger.info(f"Creating workflow for goal: {experiment_goal}")
        
        # Generate workflow ID
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_workflows)}"
        
        # Plan workflow tasks based on experiment goal
        tasks = await self._plan_workflow_tasks(experiment_goal, objectives, constraints)
        
        # Create workflow plan
        workflow = WorkflowPlan(
            workflow_id=workflow_id,
            name=f"Quantum Experiment: {experiment_goal}",
            description=f"Multi-agent workflow for {experiment_goal}",
            tasks=tasks,
            estimated_duration=self._estimate_workflow_duration(tasks)
        )
        
        # Store workflow
        self.active_workflows[workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow_id} with {len(tasks)} tasks")
        
        return {
            "workflow_id": workflow_id,
            "workflow_plan": asdict(workflow),
            "execution_strategy": strategy,
            "estimated_duration_minutes": workflow.estimated_duration.total_seconds() / 60 if workflow.estimated_duration else None,
            "task_summary": self._summarize_tasks(tasks)
        }
    
    async def _plan_workflow_tasks(self, goal: str, objectives: List[str], 
                                 constraints: Dict[str, Any]) -> List[WorkflowTask]:
        """Plan the sequence of tasks needed for the workflow."""
        tasks = []
        task_counter = 0
        
        # Analyze goal to determine workflow type
        workflow_type = self._classify_workflow_type(goal, objectives)
        
        if workflow_type == "experiment_design":
            tasks.extend(self._plan_design_workflow(goal, objectives, constraints, task_counter))
        elif workflow_type == "optimization":
            tasks.extend(self._plan_optimization_workflow(goal, objectives, constraints, task_counter))
        elif workflow_type == "analysis":
            tasks.extend(self._plan_analysis_workflow(goal, objectives, constraints, task_counter))
        elif workflow_type == "comprehensive":
            tasks.extend(self._plan_comprehensive_workflow(goal, objectives, constraints, task_counter))
        else:
            # Default comprehensive workflow
            tasks.extend(self._plan_comprehensive_workflow(goal, objectives, constraints, task_counter))
        
        return tasks
    
    def _classify_workflow_type(self, goal: str, objectives: List[str]) -> str:
        """Classify the type of workflow based on goal and objectives."""
        goal_lower = goal.lower()
        objectives_str = " ".join(objectives).lower()
        
        if "design" in goal_lower or "create" in goal_lower:
            return "experiment_design"
        elif "optimize" in goal_lower or "improve" in goal_lower:
            return "optimization"
        elif "analyze" in goal_lower or "evaluate" in goal_lower:
            return "analysis"
        else:
            return "comprehensive"
    
    def _plan_design_workflow(self, goal: str, objectives: List[str], 
                            constraints: Dict[str, Any], start_counter: int) -> List[WorkflowTask]:
        """Plan an experiment design workflow."""
        tasks = []
        
        # Task 1: Design initial experiment
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 1:03d}",
            task_type="design",
            target_agent="designer_001",
            action="design_experiment",
            parameters={
                "goal": goal,
                "objectives": objectives,
                "constraints": constraints,
                "design_type": "initial"
            },
            priority=TaskPriority.HIGH
        ))
        
        # Task 2: Analyze design
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 2:03d}",
            task_type="analyze",
            target_agent="analyzer_001",
            action="analyze_experiment",
            parameters={
                "analysis_type": "design_evaluation",
                "metrics": ["fidelity", "feasibility", "complexity"]
            },
            dependencies=[f"task_{start_counter + 1:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        # Task 3: Store design knowledge
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 3:03d}",
            task_type="knowledge",
            target_agent="knowledge_001",
            action="store_knowledge",
            parameters={
                "entry_type": "experiment_design",
                "tags": ["design", "initial"]
            },
            dependencies=[f"task_{start_counter + 1:03d}", f"task_{start_counter + 2:03d}"],
            priority=TaskPriority.MEDIUM
        ))
        
        return tasks
    
    def _plan_optimization_workflow(self, goal: str, objectives: List[str], 
                                  constraints: Dict[str, Any], start_counter: int) -> List[WorkflowTask]:
        """Plan an optimization workflow."""
        tasks = []
        
        # Task 1: Retrieve existing experiments
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 1:03d}",
            task_type="knowledge",
            target_agent="knowledge_001",
            action="search_knowledge",
            parameters={
                "query": goal,
                "search_type": "semantic",
                "max_results": 10
            },
            priority=TaskPriority.MEDIUM
        ))
        
        # Task 2: Optimize experiment
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 2:03d}",
            task_type="optimize",
            target_agent="optimizer_001",
            action="optimize_experiment",
            parameters={
                "optimization_type": "genetic_algorithm",
                "objectives": objectives,
                "constraints": constraints
            },
            dependencies=[f"task_{start_counter + 1:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        # Task 3: Analyze optimization results
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 3:03d}",
            task_type="analyze",
            target_agent="analyzer_001",
            action="analyze_optimization",
            parameters={
                "analysis_type": "optimization_evaluation",
                "metrics": ["improvement", "convergence", "stability"]
            },
            dependencies=[f"task_{start_counter + 2:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        return tasks
    
    def _plan_analysis_workflow(self, goal: str, objectives: List[str], 
                              constraints: Dict[str, Any], start_counter: int) -> List[WorkflowTask]:
        """Plan an analysis workflow."""
        tasks = []
        
        # Task 1: Retrieve experimental data
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 1:03d}",
            task_type="knowledge",
            target_agent="knowledge_001",
            action="search_knowledge",
            parameters={
                "query": goal,
                "search_type": "hybrid",
                "filters": {"entry_type": "experiment"}
            },
            priority=TaskPriority.MEDIUM
        ))
        
        # Task 2: Perform comprehensive analysis
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 2:03d}",
            task_type="analyze",
            target_agent="analyzer_001",
            action="comprehensive_analysis",
            parameters={
                "analysis_scope": "detailed",
                "objectives": objectives,
                "include_patterns": True
            },
            dependencies=[f"task_{start_counter + 1:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        # Task 3: Generate insights
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 3:03d}",
            task_type="analyze",
            target_agent="analyzer_001",
            action="generate_insights",
            parameters={
                "insight_types": ["performance", "optimization", "patterns"]
            },
            dependencies=[f"task_{start_counter + 2:03d}"],
            priority=TaskPriority.MEDIUM
        ))
        
        return tasks
    
    def _plan_comprehensive_workflow(self, goal: str, objectives: List[str], 
                                   constraints: Dict[str, Any], start_counter: int) -> List[WorkflowTask]:
        """Plan a comprehensive workflow covering all aspects."""
        tasks = []
        
        # Phase 1: Knowledge gathering
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 1:03d}",
            task_type="knowledge",
            target_agent="knowledge_001",
            action="search_knowledge",
            parameters={
                "query": goal,
                "search_type": "comprehensive",
                "include_patterns": True
            },
            priority=TaskPriority.MEDIUM
        ))
        
        # Phase 2: Initial design
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 2:03d}",
            task_type="design",
            target_agent="designer_001",
            action="design_experiment",
            parameters={
                "goal": goal,
                "objectives": objectives,
                "constraints": constraints,
                "design_mode": "knowledge_informed"
            },
            dependencies=[f"task_{start_counter + 1:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        # Phase 3: Initial analysis
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 3:03d}",
            task_type="analyze",
            target_agent="analyzer_001",
            action="analyze_experiment",
            parameters={
                "analysis_type": "comprehensive",
                "baseline_evaluation": True
            },
            dependencies=[f"task_{start_counter + 2:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        # Phase 4: Optimization
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 4:03d}",
            task_type="optimize",
            target_agent="optimizer_001",
            action="optimize_experiment",
            parameters={
                "optimization_strategy": "multi_objective",
                "objectives": objectives,
                "constraints": constraints
            },
            dependencies=[f"task_{start_counter + 3:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        # Phase 5: Final analysis
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 5:03d}",
            task_type="analyze",
            target_agent="analyzer_001",
            action="analyze_optimization",
            parameters={
                "analysis_type": "final_evaluation",
                "compare_with_baseline": True,
                "generate_report": True
            },
            dependencies=[f"task_{start_counter + 4:03d}"],
            priority=TaskPriority.HIGH
        ))
        
        # Phase 6: Knowledge storage
        tasks.append(WorkflowTask(
            task_id=f"task_{start_counter + 6:03d}",
            task_type="knowledge",
            target_agent="knowledge_001",
            action="store_knowledge",
            parameters={
                "entry_type": "complete_workflow",
                "include_all_results": True,
                "tags": ["comprehensive", "optimized"]
            },
            dependencies=[f"task_{start_counter + 5:03d}"],
            priority=TaskPriority.MEDIUM
        ))
        
        return tasks
    
    async def _execute_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a planned workflow."""
        workflow_id = request.get("workflow_id", "")
        execution_strategy = request.get("strategy", self.default_strategy)
        
        if workflow_id not in self.active_workflows:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow = self.active_workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.PENDING:
            return {"error": f"Workflow {workflow_id} is not in pending status"}
        
        logger.info(f"Starting execution of workflow {workflow_id} with strategy: {execution_strategy}")
        
        # Update workflow status
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        # Queue workflow for execution
        await self.task_queue.put({
            "workflow_id": workflow_id,
            "strategy": execution_strategy
        })
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "execution_strategy": execution_strategy,
            "estimated_completion": workflow.estimated_duration,
            "task_count": len(workflow.tasks)
        }
    
    async def _workflow_execution_loop(self):
        """Main workflow execution loop."""
        logger.info("Starting workflow execution loop")
        
        while True:
            try:
                # Get next workflow to execute
                workflow_request = await self.task_queue.get()
                workflow_id = workflow_request["workflow_id"]
                strategy = workflow_request["strategy"]
                
                if workflow_id in self.active_workflows:
                    workflow = self.active_workflows[workflow_id]
                    
                    # Execute workflow using specified strategy
                    execution_strategy = self.execution_strategies.get(
                        strategy, self._execute_adaptive
                    )
                    
                    try:
                        await execution_strategy(workflow)
                        workflow.status = WorkflowStatus.COMPLETED
                        workflow.completed_at = datetime.now()
                        workflow.actual_duration = workflow.completed_at - workflow.started_at
                        
                        # Move to history
                        self.workflow_history.append(workflow)
                        del self.active_workflows[workflow_id]
                        
                        logger.info(f"Workflow {workflow_id} completed successfully")
                        
                    except Exception as e:
                        logger.error(f"Workflow {workflow_id} failed: {e}")
                        workflow.status = WorkflowStatus.FAILED
                        await self._handle_workflow_failure(workflow, str(e))
                
                self.task_queue.task_done()
                
            except asyncio.CancelledError:
                logger.info("Workflow execution loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in workflow execution loop: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying
    
    async def _execute_sequential(self, workflow: WorkflowPlan):
        """Execute tasks sequentially."""
        logger.info(f"Executing workflow {workflow.workflow_id} sequentially")
        
        # Sort tasks by dependencies
        sorted_tasks = self._topological_sort(workflow.tasks)
        
        for task in sorted_tasks:
            if workflow.status != WorkflowStatus.RUNNING:
                break
            
            await self._execute_task(task)
            workflow.completed_tasks += 1
            workflow.progress_percentage = (workflow.completed_tasks / workflow.total_tasks) * 100
    
    async def _execute_parallel(self, workflow: WorkflowPlan):
        """Execute tasks in parallel where possible."""
        logger.info(f"Executing workflow {workflow.workflow_id} in parallel")
        
        # Group tasks by dependency level
        dependency_levels = self._group_by_dependency_level(workflow.tasks)
        
        for level, tasks in dependency_levels.items():
            if workflow.status != WorkflowStatus.RUNNING:
                break
            
            # Execute tasks at this level in parallel
            semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
            
            async def execute_with_semaphore(task):
                async with semaphore:
                    await self._execute_task(task)
                    workflow.completed_tasks += 1
                    workflow.progress_percentage = (workflow.completed_tasks / workflow.total_tasks) * 100
            
            await asyncio.gather(*[execute_with_semaphore(task) for task in tasks])
    
    async def _execute_adaptive(self, workflow: WorkflowPlan):
        """Execute tasks using adaptive strategy based on system state."""
        logger.info(f"Executing workflow {workflow.workflow_id} adaptively")
        
        # Analyze system load and task characteristics
        system_load = self._assess_system_load()
        task_complexity = self._assess_task_complexity(workflow.tasks)
        
        if system_load < 0.3 and task_complexity < 0.5:
            # Low load, simple tasks - use parallel execution
            await self._execute_parallel(workflow)
        elif system_load > 0.7 or task_complexity > 0.8:
            # High load or complex tasks - use sequential execution
            await self._execute_sequential(workflow)
        else:
            # Medium conditions - use priority-based execution
            await self._execute_priority_based(workflow)
    
    async def _execute_priority_based(self, workflow: WorkflowPlan):
        """Execute tasks based on priority and dependencies."""
        logger.info(f"Executing workflow {workflow.workflow_id} by priority")
        
        remaining_tasks = workflow.tasks.copy()
        
        while remaining_tasks and workflow.status == WorkflowStatus.RUNNING:
            # Find executable tasks (dependencies satisfied)
            executable_tasks = []
            completed_task_ids = {task.task_id for task in workflow.tasks 
                                if task.status == WorkflowStatus.COMPLETED}
            
            for task in remaining_tasks:
                if all(dep in completed_task_ids for dep in task.dependencies):
                    executable_tasks.append(task)
            
            if not executable_tasks:
                logger.warning("No executable tasks found - possible dependency cycle")
                break
            
            # Sort by priority and execute highest priority tasks
            executable_tasks.sort(key=lambda t: t.priority.value, reverse=True)
            
            # Execute top priority tasks in parallel (up to max concurrent)
            batch_size = min(len(executable_tasks), self.max_concurrent_tasks)
            batch_tasks = executable_tasks[:batch_size]
            
            await asyncio.gather(*[self._execute_task(task) for task in batch_tasks])
            
            # Remove completed tasks
            for task in batch_tasks:
                if task in remaining_tasks:
                    remaining_tasks.remove(task)
                workflow.completed_tasks += 1
            
            workflow.progress_percentage = (workflow.completed_tasks / workflow.total_tasks) * 100
    
    async def _execute_task(self, task: WorkflowTask):
        """Execute a single task."""
        logger.info(f"Executing task {task.task_id}: {task.action}")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # Find target agent
            target_agent = self.registered_agents.get(task.target_agent)
            if not target_agent:
                raise ValueError(f"Agent {task.target_agent} not found")
            
            # Send task message to agent
            message = AgentMessage(
                message_id=f"task_{task.task_id}",
                sender_id=self.agent_id,
                receiver_id=task.target_agent,
                message_type=MessageType.REQUEST,
                content={
                    "action": task.action,
                    **task.parameters
                },
                conversation_id=f"workflow_{task.task_id}"
            )
            
            # Execute with timeout
            response = await asyncio.wait_for(
                target_agent.process_message(message),
                timeout=self.task_timeout
            )
            
            if response and response.message_type != MessageType.ERROR:
                task.result = response.content
                task.status = WorkflowStatus.COMPLETED
                task.completed_at = datetime.now()
                
                # Update agent performance metrics
                self._update_agent_performance(task.target_agent, success=True, 
                                             response_time=(task.completed_at - task.started_at).total_seconds())
                
                logger.info(f"Task {task.task_id} completed successfully")
            else:
                error_msg = response.content.get("error", "Unknown error") if response else "No response"
                raise RuntimeError(error_msg)
        
        except asyncio.TimeoutError:
            task.status = WorkflowStatus.FAILED
            task.error = "Task timeout"
            self._update_agent_performance(task.target_agent, success=False, response_time=self.task_timeout)
            logger.error(f"Task {task.task_id} timed out")
            
            # Retry if possible
            if task.retry_count < task.max_retries:
                await self._retry_task(task)
        
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self._update_agent_performance(task.target_agent, success=False, 
                                         response_time=(task.completed_at - task.started_at).total_seconds())
            logger.error(f"Task {task.task_id} failed: {e}")
            
            # Retry if possible
            if task.retry_count < task.max_retries:
                await self._retry_task(task)
    
    async def _retry_task(self, task: WorkflowTask):
        """Retry a failed task with exponential backoff."""
        task.retry_count += 1
        delay = self.retry_delays[min(task.retry_count - 1, len(self.retry_delays) - 1)]
        
        logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count}/{task.max_retries}) after {delay}s")
        
        await asyncio.sleep(delay)
        
        # Reset task status for retry
        task.status = WorkflowStatus.PENDING
        task.error = None
        
        # Re-execute the task
        await self._execute_task(task)
    
    def _topological_sort(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Sort tasks topologically based on dependencies."""
        # Build dependency graph
        task_map = {task.task_id: task for task in tasks}
        in_degree = {task.task_id: 0 for task in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.task_id] += 1
        
        # Kahn's algorithm
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        sorted_tasks = []
        
        while queue:
            current_id = queue.pop(0)
            current_task = task_map[current_id]
            sorted_tasks.append(current_task)
            
            # Update dependencies
            for task in tasks:
                if current_id in task.dependencies:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)
        
        return sorted_tasks
    
    def _group_by_dependency_level(self, tasks: List[WorkflowTask]) -> Dict[int, List[WorkflowTask]]:
        """Group tasks by their dependency level."""
        levels = {}
        task_levels = {}
        
        def calculate_level(task_id, task_map, memo):
            if task_id in memo:
                return memo[task_id]
            
            task = task_map[task_id]
            if not task.dependencies:
                level = 0
            else:
                level = max(calculate_level(dep, task_map, memo) for dep in task.dependencies if dep in task_map) + 1
            
            memo[task_id] = level
            return level
        
        task_map = {task.task_id: task for task in tasks}
        
        for task in tasks:
            level = calculate_level(task.task_id, task_map, task_levels)
            if level not in levels:
                levels[level] = []
            levels[level].append(task)
        
        return levels
    
    def _assess_system_load(self) -> float:
        """Assess current system load (simplified)."""
        # This would typically check CPU, memory, active tasks, etc.
        active_tasks = len(self.running_tasks)
        max_capacity = self.max_concurrent_tasks * 2  # Rough estimate
        return min(active_tasks / max_capacity, 1.0)
    
    def _assess_task_complexity(self, tasks: List[WorkflowTask]) -> float:
        """Assess overall complexity of task set."""
        complexity_scores = {
            "design_experiment": 0.8,
            "optimize_experiment": 0.9,
            "analyze_experiment": 0.6,
            "store_knowledge": 0.3,
            "search_knowledge": 0.4
        }
        
        if not tasks:
            return 0.0
        
        total_complexity = sum(complexity_scores.get(task.action, 0.5) for task in tasks)
        return total_complexity / len(tasks)
    
    def _update_agent_performance(self, agent_id: str, success: bool, response_time: float):
        """Update performance metrics for an agent."""
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = AgentPerformanceMetrics(agent_id=agent_id)
        
        metrics = self.agent_performance[agent_id]
        metrics.total_tasks += 1
        metrics.last_active = datetime.now()
        
        if success:
            metrics.completed_tasks += 1
        else:
            metrics.failed_tasks += 1
        
        metrics.success_rate = metrics.completed_tasks / metrics.total_tasks
        
        # Update average response time
        metrics.average_response_time = (
            (metrics.average_response_time * (metrics.total_tasks - 1) + response_time) / 
            metrics.total_tasks
        )
        
        # Calculate performance score
        metrics.performance_score = (
            metrics.success_rate * 0.6 + 
            (1.0 - min(metrics.average_response_time / 60.0, 1.0)) * 0.4
        )
    
    async def _handle_workflow_failure(self, workflow: WorkflowPlan, error: str):
        """Handle workflow failure and implement recovery strategies."""
        logger.error(f"Handling failure for workflow {workflow.workflow_id}: {error}")
        
        workflow.completed_at = datetime.now()
        workflow.actual_duration = workflow.completed_at - workflow.started_at
        
        # Analyze failure
        failed_tasks = [task for task in workflow.tasks if task.status == WorkflowStatus.FAILED]
        failure_analysis = {
            "workflow_id": workflow.workflow_id,
            "error": error,
            "failed_tasks": len(failed_tasks),
            "completion_percentage": workflow.progress_percentage,
            "duration_before_failure": workflow.actual_duration.total_seconds()
        }
        
        # Store failure information for learning
        await self._store_failure_knowledge(failure_analysis)
        
        # Move to history
        self.workflow_history.append(workflow)
        if workflow.workflow_id in self.active_workflows:
            del self.active_workflows[workflow.workflow_id]
    
    async def _store_failure_knowledge(self, failure_analysis: Dict[str, Any]):
        """Store failure information for future learning."""
        if "knowledge_001" in self.registered_agents:
            knowledge_agent = self.registered_agents["knowledge_001"]
            
            message = AgentMessage(
                message_id=f"failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sender_id=self.agent_id,
                receiver_id="knowledge_001",
                message_type=MessageType.REQUEST,
                content={
                    "action": "store_knowledge",
                    "entry_type": "workflow_failure",
                    "content": failure_analysis,
                    "tags": ["failure", "learning", "workflow"]
                }
            )
            
            try:
                await knowledge_agent.process_message(message)
            except Exception as e:
                logger.error(f"Failed to store failure knowledge: {e}")
    
    # Monitoring and management methods
    
    async def _monitor_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor workflow progress and status."""
        workflow_id = request.get("workflow_id", "")
        
        if workflow_id not in self.active_workflows:
            return {"error": f"Workflow {workflow_id} not found in active workflows"}
        
        workflow = self.active_workflows[workflow_id]
        
        # Calculate detailed progress
        task_statuses = {}
        for status in WorkflowStatus:
            task_statuses[status.value] = len([t for t in workflow.tasks if t.status == status])
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "progress_percentage": workflow.progress_percentage,
            "completed_tasks": workflow.completed_tasks,
            "total_tasks": workflow.total_tasks,
            "task_statuses": task_statuses,
            "estimated_completion": self._estimate_completion_time(workflow),
            "current_phase": self._identify_current_phase(workflow)
        }
    
    async def _pause_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Pause workflow execution."""
        workflow_id = request.get("workflow_id", "")
        
        if workflow_id not in self.active_workflows:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.PAUSED
        
        logger.info(f"Paused workflow {workflow_id}")
        
        return {
            "workflow_id": workflow_id,
            "status": "paused",
            "progress_at_pause": workflow.progress_percentage
        }
    
    async def _resume_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Resume paused workflow execution."""
        workflow_id = request.get("workflow_id", "")
        
        if workflow_id not in self.active_workflows:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow = self.active_workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.PAUSED:
            return {"error": f"Workflow {workflow_id} is not paused"}
        
        workflow.status = WorkflowStatus.RUNNING
        
        # Re-queue for execution
        await self.task_queue.put({
            "workflow_id": workflow_id,
            "strategy": "adaptive"  # Use adaptive strategy for resumed workflows
        })
        
        logger.info(f"Resumed workflow {workflow_id}")
        
        return {
            "workflow_id": workflow_id,
            "status": "resumed",
            "remaining_tasks": workflow.total_tasks - workflow.completed_tasks
        }
    
    async def _cancel_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel workflow execution."""
        workflow_id = request.get("workflow_id", "")
        
        if workflow_id not in self.active_workflows:
            return {"error": f"Workflow {workflow_id} not found"}
        
        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.now()
        
        # Move to history
        self.workflow_history.append(workflow)
        del self.active_workflows[workflow_id]
        
        logger.info(f"Cancelled workflow {workflow_id}")
        
        return {
            "workflow_id": workflow_id,
            "status": "cancelled",
            "completion_percentage": workflow.progress_percentage
        }
    
    async def _register_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent with the coordinator."""
        agent_info = request.get("agent_info", {})
        agent_id = agent_info.get("agent_id", "")
        
        if not agent_id:
            return {"error": "Agent ID required"}
        
        # This is a simplified registration - in practice would need actual agent object
        self.agent_capabilities[agent_id] = agent_info.get("capabilities", [])
        self.agent_performance[agent_id] = AgentPerformanceMetrics(agent_id=agent_id)
        
        return {
            "agent_id": agent_id,
            "status": "registered",
            "capabilities_count": len(self.agent_capabilities[agent_id])
        }
    
    async def _get_system_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "system_metrics": self.system_metrics,
            "active_workflows": len(self.active_workflows),
            "registered_agents": len(self.registered_agents),
            "agent_performance": {
                agent_id: {
                    "success_rate": metrics.success_rate,
                    "performance_score": metrics.performance_score,
                    "total_tasks": metrics.total_tasks
                }
                for agent_id, metrics in self.agent_performance.items()
            },
            "system_health": self._assess_system_health(),
            "resource_utilization": {
                "task_queue_size": self.task_queue.qsize(),
                "running_tasks": len(self.running_tasks),
                "max_concurrent": self.max_concurrent_tasks
            }
        }
    
    async def _optimize_performance(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system performance based on current metrics."""
        optimization_areas = request.get("areas", ["task_scheduling", "resource_allocation", "agent_load_balancing"])
        
        optimizations_applied = []
        
        if "task_scheduling" in optimization_areas:
            # Optimize task scheduling strategy
            optimal_strategy = self._determine_optimal_strategy()
            if optimal_strategy != self.default_strategy:
                self.default_strategy = optimal_strategy
                optimizations_applied.append(f"Changed default strategy to {optimal_strategy}")
        
        if "resource_allocation" in optimization_areas:
            # Optimize resource allocation
            optimal_concurrent = self._calculate_optimal_concurrency()
            if optimal_concurrent != self.max_concurrent_tasks:
                self.max_concurrent_tasks = optimal_concurrent
                optimizations_applied.append(f"Adjusted max concurrent tasks to {optimal_concurrent}")
        
        if "agent_load_balancing" in optimization_areas:
            # Implement agent load balancing
            load_balancing_changes = self._optimize_agent_load_balancing()
            optimizations_applied.extend(load_balancing_changes)
        
        return {
            "optimizations_applied": optimizations_applied,
            "new_configuration": {
                "default_strategy": self.default_strategy,
                "max_concurrent_tasks": self.max_concurrent_tasks
            },
            "expected_improvement": self._estimate_performance_improvement(optimizations_applied)
        }
    
    async def _handle_error(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system errors and implement recovery strategies."""
        error_type = request.get("error_type", "")
        error_details = request.get("error_details", {})
        
        recovery_actions = []
        
        if error_type == "agent_failure":
            # Handle agent failure
            agent_id = error_details.get("agent_id", "")
            recovery_actions.extend(self._handle_agent_failure(agent_id))
        
        elif error_type == "workflow_stall":
            # Handle workflow stall
            workflow_id = error_details.get("workflow_id", "")
            recovery_actions.extend(await self._handle_workflow_stall(workflow_id))
        
        elif error_type == "system_overload":
            # Handle system overload
            recovery_actions.extend(self._handle_system_overload())
        
        return {
            "error_type": error_type,
            "recovery_actions": recovery_actions,
            "system_stability": self._assess_system_stability()
        }
    
    # Utility methods
    
    def _estimate_workflow_duration(self, tasks: List[WorkflowTask]) -> timedelta:
        """Estimate workflow duration based on tasks."""
        # Simplified estimation based on task types
        task_durations = {
            "design": timedelta(minutes=10),
            "analyze": timedelta(minutes=5),
            "optimize": timedelta(minutes=15),
            "knowledge": timedelta(minutes=2)
        }
        
        total_duration = timedelta(0)
        for task in tasks:
            task_type = task.task_type
            base_duration = task_durations.get(task_type, timedelta(minutes=5))
            
            # Adjust for priority and complexity
            if task.priority == TaskPriority.HIGH:
                base_duration *= 1.2
            elif task.priority == TaskPriority.CRITICAL:
                base_duration *= 1.5
            
            total_duration += base_duration
        
        return total_duration
    
    def _summarize_tasks(self, tasks: List[WorkflowTask]) -> Dict[str, Any]:
        """Create a summary of tasks in the workflow."""
        task_types = {}
        priority_counts = {}
        
        for task in tasks:
            task_types[task.task_type] = task_types.get(task.task_type, 0) + 1
            priority_counts[task.priority.name] = priority_counts.get(task.priority.name, 0) + 1
        
        return {
            "total_tasks": len(tasks),
            "task_types": task_types,
            "priority_distribution": priority_counts,
            "estimated_total_duration": str(self._estimate_workflow_duration(tasks))
        }
    
    def _estimate_completion_time(self, workflow: WorkflowPlan) -> Optional[str]:
        """Estimate when workflow will complete."""
        if workflow.status != WorkflowStatus.RUNNING or workflow.progress_percentage == 0:
            return None
        
        elapsed = datetime.now() - workflow.started_at
        total_estimated = elapsed / (workflow.progress_percentage / 100.0)
        remaining = total_estimated - elapsed
        
        completion_time = datetime.now() + remaining
        return completion_time.isoformat()
    
    def _identify_current_phase(self, workflow: WorkflowPlan) -> str:
        """Identify the current phase of workflow execution."""
        running_tasks = [task for task in workflow.tasks if task.status == WorkflowStatus.RUNNING]
        
        if not running_tasks:
            if workflow.completed_tasks == 0:
                return "initialization"
            elif workflow.completed_tasks == workflow.total_tasks:
                return "completed"
            else:
                return "between_phases"
        
        # Identify phase by task types currently running
        task_types = {task.task_type for task in running_tasks}
        
        if "design" in task_types:
            return "design_phase"
        elif "analyze" in task_types:
            return "analysis_phase"
        elif "optimize" in task_types:
            return "optimization_phase"
        elif "knowledge" in task_types:
            return "knowledge_phase"
        else:
            return "execution_phase"
    
    def _assess_system_health(self) -> str:
        """Assess overall system health."""
        # Check various health indicators
        health_score = 0.0
        
        # Agent performance
        if self.agent_performance:
            avg_performance = sum(m.performance_score for m in self.agent_performance.values()) / len(self.agent_performance)
            health_score += avg_performance * 0.4
        else:
            health_score += 0.2  # Partial score if no agents
        
        # Workflow success rate
        if self.workflow_history:
            successful_workflows = sum(1 for w in self.workflow_history if w.status == WorkflowStatus.COMPLETED)
            success_rate = successful_workflows / len(self.workflow_history)
            health_score += success_rate * 0.3
        else:
            health_score += 0.15  # Partial score if no history
        
        # System resource utilization
        system_load = self._assess_system_load()
        resource_score = 1.0 - min(system_load, 1.0)  # Lower load = better health
        health_score += resource_score * 0.3
        
        if health_score >= 0.8:
            return "excellent"
        elif health_score >= 0.6:
            return "good"
        elif health_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _determine_optimal_strategy(self) -> str:
        """Determine optimal execution strategy based on historical performance."""
        # Analyze historical performance of different strategies
        # This is simplified - would analyze actual performance data
        return "adaptive"
    
    def _calculate_optimal_concurrency(self) -> int:
        """Calculate optimal number of concurrent tasks."""
        # Base on system performance and agent capabilities
        current_load = self._assess_system_load()
        
        if current_load < 0.3:
            return min(self.max_concurrent_tasks + 2, 10)
        elif current_load > 0.7:
            return max(self.max_concurrent_tasks - 1, 2)
        else:
            return self.max_concurrent_tasks
    
    def _optimize_agent_load_balancing(self) -> List[str]:
        """Optimize load balancing across agents."""
        changes = []
        
        # Analyze agent performance and redistribute load if needed
        if len(self.agent_performance) > 1:
            performance_scores = [(agent_id, metrics.performance_score) 
                                for agent_id, metrics in self.agent_performance.items()]
            performance_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Identify underperforming agents
            avg_performance = sum(score for _, score in performance_scores) / len(performance_scores)
            underperforming = [agent_id for agent_id, score in performance_scores if score < avg_performance * 0.8]
            
            if underperforming:
                changes.append(f"Identified {len(underperforming)} underperforming agents for attention")
        
        return changes
    
    def _estimate_performance_improvement(self, optimizations: List[str]) -> float:
        """Estimate expected performance improvement from optimizations."""
        # Simplified estimation based on types of optimizations
        base_improvement = len(optimizations) * 0.05  # 5% per optimization
        return min(base_improvement, 0.3)  # Cap at 30% improvement
    
    def _handle_agent_failure(self, agent_id: str) -> List[str]:
        """Handle agent failure and implement recovery."""
        recovery_actions = []
        
        if agent_id in self.agent_performance:
            # Mark agent as problematic
            self.agent_performance[agent_id].performance_score *= 0.5
            recovery_actions.append(f"Reduced performance score for agent {agent_id}")
            
            # Could implement agent restart, task redistribution, etc.
            recovery_actions.append(f"Initiated recovery procedures for agent {agent_id}")
        
        return recovery_actions
    
    async def _handle_workflow_stall(self, workflow_id: str) -> List[str]:
        """Handle workflow stall situation."""
        recovery_actions = []
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            
            # Identify stalled tasks
            stalled_tasks = [task for task in workflow.tasks 
                           if task.status == WorkflowStatus.RUNNING and 
                           task.started_at and 
                           (datetime.now() - task.started_at).total_seconds() > self.task_timeout]
            
            if stalled_tasks:
                # Reset stalled tasks
                for task in stalled_tasks:
                    task.status = WorkflowStatus.PENDING
                    task.started_at = None
                    recovery_actions.append(f"Reset stalled task {task.task_id}")
                
                # Re-queue workflow
                await self.task_queue.put({
                    "workflow_id": workflow_id,
                    "strategy": "sequential"  # Use more conservative strategy
                })
                recovery_actions.append(f"Re-queued workflow {workflow_id} with sequential strategy")
        
        return recovery_actions
    
    def _handle_system_overload(self) -> List[str]:
        """Handle system overload situation."""
        recovery_actions = []
        
        # Reduce concurrent task limit
        if self.max_concurrent_tasks > 2:
            self.max_concurrent_tasks = max(2, self.max_concurrent_tasks // 2)
            recovery_actions.append(f"Reduced max concurrent tasks to {self.max_concurrent_tasks}")
        
        # Switch to conservative execution strategy
        if self.default_strategy != "sequential":
            self.default_strategy = "sequential"
            recovery_actions.append("Switched to sequential execution strategy")
        
        return recovery_actions
    
    def _assess_system_stability(self) -> str:
        """Assess current system stability."""
        # Check for recent failures, performance trends, etc.
        recent_failures = sum(1 for w in self.workflow_history[-10:] 
                            if w.status == WorkflowStatus.FAILED)
        
        if recent_failures == 0:
            return "stable"
        elif recent_failures <= 2:
            return "mostly_stable"
        elif recent_failures <= 5:
            return "unstable"
        else:
            return "critical"
