"""Claude Code Subagent Spawner System."""
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from .agent_registry import AgentRegistry, AgentType, AgentCapability


@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    task_id: str
    agent_type: str
    task_description: str
    priority: int = 5
    status: str = "pending"
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.context is None:
            self.context = {}


class AgentSpawner:
    """Spawns and manages Claude Code subagents."""
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.registry = AgentRegistry()
        self.active_agents: Dict[str, AgentTask] = {}
        self.task_results: Dict[str, Any] = {}
        self.proxy_dir = Path(".claude_subagents")
        self.proxy_dir.mkdir(exist_ok=True)
        
    def spawn_agent(
        self, 
        agent_type: AgentType, 
        task_description: str,
        priority: int = 5,
        context: Optional[Dict] = None,
        use_claude_session: bool = True
    ) -> str:
        """Spawn a subagent for a specific task.
        
        Args:
            agent_type: Type of agent to spawn
            task_description: Description of the task
            priority: Task priority (1-10)
            context: Additional context for the task
            use_claude_session: Whether to use current Claude session
            
        Returns:
            Task ID for tracking
        """
        # Generate unique task ID
        task_id = f"{agent_type.value}_{int(time.time() * 1000)}"
        
        # Get agent capability
        capability = self.registry.get_agent(agent_type)
        if not capability:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create agent task
        task = AgentTask(
            task_id=task_id,
            agent_type=agent_type.value,
            task_description=task_description,
            priority=priority,
            context=context or {}
        )
        
        # Store active task
        self.active_agents[task_id] = task
        
        if use_claude_session:
            # Create proxy request for current Claude session
            self._create_claude_proxy_task(task_id, agent_type, task, capability)
        else:
            # Execute directly via subprocess (future implementation)
            self._execute_direct_spawn(task_id, agent_type, task, capability)
        
        return task_id
    
    def _create_claude_proxy_task(
        self, 
        task_id: str, 
        agent_type: AgentType,
        task: AgentTask,
        capability: AgentCapability
    ) -> None:
        """Create a proxy task file for current Claude session to execute."""
        
        # Build the agent instructions
        instructions = self._build_agent_instructions(
            task_id, agent_type, task, capability
        )
        
        # Create proxy request
        proxy_data = {
            "task_id": task_id,
            "agent_type": agent_type.value,
            "agent_name": capability.name,
            "task": asdict(task),
            "capability": {
                "name": capability.name,
                "description": capability.description,
                "tools": capability.tools,
                "model": capability.model,
                "prompt_template": capability.prompt_template
            },
            "instructions": instructions,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save proxy request
        proxy_file = self.proxy_dir / f"request_{task_id}.json"
        with open(proxy_file, 'w') as f:
            json.dump(proxy_data, f, indent=2)
        
        # Update task status
        task.status = "queued"
        task.started_at = datetime.now().isoformat()
        
        print(f"📝 Subagent task created: {proxy_file}")
        
    def _build_agent_instructions(
        self,
        task_id: str,
        agent_type: AgentType,
        task: AgentTask,
        capability: AgentCapability
    ) -> str:
        """Build detailed instructions for the subagent."""
        
        tools_str = "all available tools" if capability.tools == ["*"] else f"{', '.join(capability.tools)}"
        
        instructions = f"""
=== CLAUDE CODE SUBAGENT TASK ===

You are now acting as a specialized {capability.name} subagent.

ROLE: {capability.description}

AGENT CONFIGURATION:
- Model: {capability.model}
- Available Tools: {tools_str}
- Specialized Domains: {', '.join(capability.specialized_domains)}

CONTEXT:
{capability.prompt_template}

TASK DETAILS:
- Task ID: {task_id}
- Priority: {task.priority}/10
- Description: {task.task_description}

"""
        
        if task.context:
            instructions += f"""ADDITIONAL CONTEXT:
{json.dumps(task.context, indent=2)}

"""
        
        instructions += f"""EXECUTION REQUIREMENTS:
1. Focus on your specialized domain and expertise
2. Use only the tools available to your agent type
3. Follow the project's coding conventions and best practices
4. Provide clear, actionable results
5. Save your results to: {self.proxy_dir}/result_{task_id}.json

RESULT FORMAT:
{{
    "task_id": "{task_id}",
    "status": "completed|failed",
    "result": "detailed result here",
    "artifacts": ["list of created/modified files"],
    "metrics": {{"lines_added": 0, "files_modified": 0}},
    "error": null
}}

Please execute this task now.
"""
        
        return instructions
    
    def _execute_direct_spawn(
        self,
        task_id: str,
        agent_type: AgentType,
        task: AgentTask,
        capability: AgentCapability
    ) -> None:
        """Execute agent task directly via subprocess (future implementation)."""
        # This would spawn a separate Python process or use the Task tool
        # For now, we'll use the proxy method
        self._create_claude_proxy_task(task_id, agent_type, task, capability)
    
    def check_task_result(self, task_id: str) -> Optional[Dict]:
        """Check if a task has completed and return its result."""
        result_file = self.proxy_dir / f"result_{task_id}.json"
        
        if result_file.exists():
            with open(result_file, 'r') as f:
                result = json.load(f)
            
            # Update task status
            if task_id in self.active_agents:
                task = self.active_agents[task_id]
                task.status = result.get("status", "completed")
                task.completed_at = datetime.now().isoformat()
                task.result = result.get("result")
                task.error = result.get("error")
                
                # Move to completed
                self.task_results[task_id] = result
                
            # Clean up files
            result_file.unlink()
            request_file = self.proxy_dir / f"request_{task_id}.json"
            if request_file.exists():
                request_file.unlink()
            
            return result
        
        return None
    
    def get_active_tasks(self) -> List[AgentTask]:
        """Get all active agent tasks."""
        return list(self.active_agents.values())
    
    def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get status of a specific task."""
        return self.active_agents.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel an active task."""
        if task_id in self.active_agents:
            task = self.active_agents[task_id]
            task.status = "cancelled"
            task.completed_at = datetime.now().isoformat()
            
            # Clean up proxy files
            for filename in [f"request_{task_id}.json", f"result_{task_id}.json"]:
                file_path = self.proxy_dir / filename
                if file_path.exists():
                    file_path.unlink()
            
            return True
        return False
    
    def delegate_task(self, task_description: str, context: Optional[Dict] = None) -> str:
        """Automatically select the best agent and delegate the task."""
        # Use registry to select the best agent
        agent_type = self.registry.select_agent_for_task(task_description)
        
        # Spawn the selected agent
        task_id = self.spawn_agent(
            agent_type=agent_type,
            task_description=task_description,
            context=context
        )
        
        print(f"🤖 Task delegated to {agent_type.value}: {task_id}")
        return task_id
    
    def batch_spawn(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Spawn multiple agents for batch processing."""
        task_ids = []
        
        for task_data in tasks:
            agent_type = AgentType(task_data.get("agent_type", "general-purpose"))
            task_id = self.spawn_agent(
                agent_type=agent_type,
                task_description=task_data["description"],
                priority=task_data.get("priority", 5),
                context=task_data.get("context", {})
            )
            task_ids.append(task_id)
            
        return task_ids
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get metrics about agent usage and performance."""
        metrics = {
            "total_tasks": len(self.active_agents) + len(self.task_results),
            "active_tasks": len(self.active_agents),
            "completed_tasks": len(self.task_results),
            "agents_usage": {},
            "success_rate": 0.0
        }
        
        # Count usage by agent type
        for task in list(self.active_agents.values()) + list(self.task_results.values()):
            if isinstance(task, AgentTask):
                agent_type = task.agent_type
            else:
                agent_type = task.get("agent_type", "unknown")
            
            metrics["agents_usage"][agent_type] = metrics["agents_usage"].get(agent_type, 0) + 1
        
        # Calculate success rate
        if self.task_results:
            successful = sum(1 for r in self.task_results.values() 
                           if isinstance(r, dict) and r.get("status") == "completed")
            metrics["success_rate"] = (successful / len(self.task_results)) * 100
        
        return metrics