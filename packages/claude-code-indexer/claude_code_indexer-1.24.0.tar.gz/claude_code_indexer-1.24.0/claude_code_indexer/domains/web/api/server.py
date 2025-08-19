"""GOD Mode Web Dashboard API Server."""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from claude_code_indexer.commands.god_mode import GodModeOrchestrator
except ImportError:
    # Fallback import for development
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from commands.god_mode import GodModeOrchestrator

try:
    from claude_code_indexer.commands.tmux_orchestrator import TmuxOrchestrator
except ImportError:
    from commands.tmux_orchestrator import TmuxOrchestrator

try:
    from claude_code_indexer.agent_registry import AgentRegistry, AgentType
    from claude_code_indexer.agent_spawner import AgentSpawner
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from agent_registry import AgentRegistry, AgentType
    from agent_spawner import AgentSpawner


# Pydantic models
class Task(BaseModel):
    id: Optional[str] = None
    agent: str
    description: str
    priority: int = 5
    status: str = "pending"
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None


class GodModeConfig(BaseModel):
    enabled: bool
    auto_accept: bool
    vibecode_mode: bool
    max_tokens_per_session: int


class AgentStatus(BaseModel):
    name: str
    active: bool
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tokens_used: int = 0
    last_activity: Optional[datetime] = None


class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    active_agents: int
    queued_tasks: int
    completed_tasks: int
    total_tokens: int


# Initialize FastAPI app
app = FastAPI(title="GOD Mode Dashboard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class DashboardState:
    def __init__(self):
        self.god_mode = GodModeOrchestrator()
        self.tmux_orchestrator = None
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.websockets: List[WebSocket] = []
        
        # Initialize agent registry and spawner
        self.agent_registry = AgentRegistry()
        self.agent_spawner = AgentSpawner(self.god_mode)
        
        # Initialize agents from registry
        self.agents: Dict[str, AgentStatus] = {}
        for agent_info in self.agent_registry.list_agents():
            self.agents[agent_info["type"]] = AgentStatus(
                name=agent_info["type"],
                active=False
            )
        
        self.system_metrics = SystemMetrics(
            cpu_usage=0.0,
            memory_usage=0.0,
            active_agents=0,
            queued_tasks=0,
            completed_tasks=0,
            total_tokens=0
        )
        self.audit_log: List[Dict] = []
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected websockets."""
        disconnected = []
        for websocket in self.websockets:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            if ws in self.websockets:
                self.websockets.remove(ws)


state = DashboardState()


# API Routes
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "GOD Mode Dashboard API"}


@app.get("/api/status")
async def get_status():
    """Get GOD mode status."""
    import yaml
    config_file = state.god_mode.config_file
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {
            "enabled": False,
            "auto_accept": True,
            "vibecode_mode": True,
            "agents": {}
        }
    
    return {
        "god_mode": {
            "enabled": config.get("enabled", False),
            "auto_accept": config.get("auto_accept", True),
            "vibecode_mode": config.get("vibecode_mode", True),
        },
        "tmux": {
            "connected": state.tmux_orchestrator is not None,
            "session_name": state.tmux_orchestrator.session_name if state.tmux_orchestrator else None
        },
        "token_usage": state.god_mode.token_usage
    }


@app.post("/api/god-mode/enable")
async def enable_god_mode():
    """Enable GOD mode."""
    await state.god_mode.enable()
    await state.broadcast({
        "type": "god_mode_status",
        "enabled": True,
        "timestamp": datetime.now().isoformat()
    })
    return {"status": "enabled"}


@app.post("/api/god-mode/disable")
async def disable_god_mode():
    """Disable GOD mode."""
    await state.god_mode.disable()
    await state.broadcast({
        "type": "god_mode_status",
        "enabled": False,
        "timestamp": datetime.now().isoformat()
    })
    return {"status": "disabled"}


@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks."""
    return {
        "queued": state.task_queue,
        "active": list(state.active_tasks.values()),
        "completed": state.completed_tasks[-50:]  # Last 50 completed tasks
    }


@app.post("/api/tasks")
async def create_task(task: Task):
    """Create a new task."""
    task.id = str(uuid4())
    task.created_at = datetime.now()
    task.status = "queued"
    
    state.task_queue.append(task)
    
    await state.broadcast({
        "type": "task_created",
        "task": task.dict(),
        "timestamp": datetime.now().isoformat()
    })
    
    # Process task in background
    asyncio.create_task(process_task(task))
    
    return task


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a task."""
    # Remove from queue
    state.task_queue = [t for t in state.task_queue if t.id != task_id]
    
    # Mark as cancelled if active
    if task_id in state.active_tasks:
        task = state.active_tasks[task_id]
        task.status = "cancelled"
        task.completed_at = datetime.now()
        state.completed_tasks.append(task)
        del state.active_tasks[task_id]
    
    await state.broadcast({
        "type": "task_cancelled",
        "task_id": task_id,
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "cancelled"}


@app.get("/api/agents")
async def get_agents():
    """Get agent statuses."""
    return list(state.agents.values())


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    import psutil
    
    # Update metrics
    state.system_metrics.cpu_usage = psutil.cpu_percent()
    state.system_metrics.memory_usage = psutil.virtual_memory().percent
    state.system_metrics.active_agents = sum(1 for a in state.agents.values() if a.active)
    state.system_metrics.queued_tasks = len(state.task_queue)
    state.system_metrics.completed_tasks = len(state.completed_tasks)
    state.system_metrics.total_tokens = state.god_mode.token_usage.get("total", 0)
    
    return state.system_metrics


@app.get("/api/audit-log")
async def get_audit_log(limit: int = 100):
    """Get audit log entries."""
    audit_file = state.god_mode.audit_log_path
    entries = []
    
    if audit_file.exists():
        with open(audit_file, 'r') as f:
            lines = f.readlines()[-limit:]
            for line in lines:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    
    return entries


@app.post("/api/tmux/connect")
async def connect_tmux(session_name: str = "god-mode"):
    """Connect to tmux session."""
    state.tmux_orchestrator = TmuxOrchestrator(session_name)
    
    if not state.tmux_orchestrator.session_exists():
        state.tmux_orchestrator.create_session()
        state.tmux_orchestrator.create_layout()
    
    await state.broadcast({
        "type": "tmux_connected",
        "session_name": session_name,
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "connected", "session_name": session_name}


@app.post("/api/tmux/disconnect")
async def disconnect_tmux():
    """Disconnect from tmux session."""
    state.tmux_orchestrator = None
    
    await state.broadcast({
        "type": "tmux_disconnected",
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "disconnected"}


@app.get("/api/agents/capabilities")
async def get_agent_capabilities():
    """Get all available agent types and their capabilities."""
    return state.agent_registry.list_agents()


@app.post("/api/agents/spawn")
async def spawn_subagent(request: Dict):
    """Spawn a new subagent for a task."""
    try:
        agent_type = request.get("agent_type", "general-purpose")
        task_description = request.get("task")
        priority = request.get("priority", 5)
        context = request.get("context", {})
        
        # Convert string to AgentType enum
        try:
            agent_enum = AgentType(agent_type)
        except ValueError:
            # Try to find by name
            result = state.agent_registry.get_agent_by_name(agent_type)
            if result:
                agent_enum = result[0]
            else:
                raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        # Spawn the agent
        task_id = state.agent_spawner.spawn_agent(
            agent_type=agent_enum,
            task_description=task_description,
            priority=priority,
            context=context,
            use_claude_session=request.get("use_claude_session", True)
        )
        
        # Broadcast event
        await state.broadcast({
            "type": "subagent_spawned",
            "task_id": task_id,
            "agent_type": agent_enum.value,
            "task": task_description,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "task_id": task_id,
            "agent_type": agent_enum.value,
            "status": "spawned"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/agents/delegate")
async def delegate_task(request: Dict):
    """Automatically delegate a task to the most appropriate agent."""
    try:
        task_description = request.get("task")
        context = request.get("context", {})
        
        if not task_description:
            raise HTTPException(status_code=400, detail="Task description is required")
        
        # Delegate to appropriate agent
        task_id = state.agent_spawner.delegate_task(task_description, context)
        
        # Get the selected agent info
        task_info = state.agent_spawner.get_task_status(task_id)
        
        await state.broadcast({
            "type": "task_delegated",
            "task_id": task_id,
            "agent_type": task_info.agent_type if task_info else "unknown",
            "task": task_description,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "task_id": task_id,
            "selected_agent": task_info.agent_type if task_info else "unknown",
            "status": "delegated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/agents/tasks")
async def get_agent_tasks():
    """Get all active subagent tasks."""
    tasks = state.agent_spawner.get_active_tasks()
    return [
        {
            "task_id": task.task_id,
            "agent_type": task.agent_type,
            "description": task.task_description,
            "priority": task.priority,
            "status": task.status,
            "created_at": task.created_at,
            "started_at": task.started_at
        }
        for task in tasks
    ]


@app.get("/api/agents/tasks/{task_id}")
async def get_agent_task_status(task_id: str):
    """Get status of a specific subagent task."""
    task = state.agent_spawner.get_task_status(task_id)
    
    if not task:
        # Check for completed result
        result = state.agent_spawner.check_task_result(task_id)
        if result:
            return result
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "agent_type": task.agent_type,
        "description": task.task_description,
        "priority": task.priority,
        "status": task.status,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "result": task.result,
        "error": task.error
    }


@app.get("/api/agents/metrics")
async def get_agent_metrics():
    """Get metrics about agent usage and performance."""
    return state.agent_spawner.get_agent_metrics()


@app.post("/api/emergency-stop")
async def emergency_stop():
    """Emergency stop - disable GOD mode and clear all tasks."""
    # Disable GOD mode
    await state.god_mode.disable()
    
    # Clear all tasks
    state.task_queue.clear()
    
    # Cancel active tasks
    for task in state.active_tasks.values():
        task.status = "cancelled"
        task.completed_at = datetime.now()
        state.completed_tasks.append(task)
    state.active_tasks.clear()
    
    # Reset agents
    for agent in state.agents.values():
        agent.active = False
        agent.current_task = None
    
    await state.broadcast({
        "type": "emergency_stop",
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "emergency_stop_executed"}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    state.websockets.append(websocket)
    
    # Send initial state
    await websocket.send_json({
        "type": "connected",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        if websocket in state.websockets:
            state.websockets.remove(websocket)


# Background task processor
async def process_task(task: Task):
    """Process a task asynchronously."""
    try:
        # Move task to active
        if task in state.task_queue:
            state.task_queue.remove(task)
        
        task.status = "running"
        task.started_at = datetime.now()
        state.active_tasks[task.id] = task
        
        # Update agent status
        if task.agent in state.agents:
            agent = state.agents[task.agent]
            agent.active = True
            agent.current_task = task.description
            agent.last_activity = datetime.now()
        
        await state.broadcast({
            "type": "task_started",
            "task": task.dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        # Execute task based on integration mode
        if state.tmux_orchestrator:
            # Use tmux integration
            task_id = state.tmux_orchestrator.execute_agent_task(
                task.agent, 
                task.description
            )
            # Simulate processing time
            await asyncio.sleep(5)
            task.result = f"Task completed via tmux: {task_id}"
        else:
            # Use GOD mode directly
            success, result = await asyncio.get_event_loop().run_in_executor(
                None,
                state.god_mode._execute_cci_directly,
                task.description
            )
            task.result = result if success else None
            task.error = result if not success else None
        
        # Mark task as completed
        task.status = "completed" if not task.error else "failed"
        task.completed_at = datetime.now()
        
        # Update agent status
        if task.agent in state.agents:
            agent = state.agents[task.agent]
            agent.active = False
            agent.current_task = None
            agent.tasks_completed += 1
            agent.tokens_used += 100  # Simulated token usage
        
        # Move to completed
        del state.active_tasks[task.id]
        state.completed_tasks.append(task)
        
        # Update metrics
        state.system_metrics.completed_tasks += 1
        state.system_metrics.total_tokens += 100
        
        await state.broadcast({
            "type": "task_completed",
            "task": task.dict(),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.completed_at = datetime.now()
        
        if task.id in state.active_tasks:
            del state.active_tasks[task.id]
        state.completed_tasks.append(task)
        
        await state.broadcast({
            "type": "task_failed",
            "task": task.dict(),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })


# Background monitor
async def monitor_system():
    """Monitor system and send periodic updates."""
    while True:
        await asyncio.sleep(5)  # Update every 5 seconds
        
        metrics = await get_metrics()
        
        await state.broadcast({
            "type": "metrics_update",
            "metrics": metrics.dict() if hasattr(metrics, 'dict') else metrics,
            "timestamp": datetime.now().isoformat()
        })


@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup."""
    asyncio.create_task(monitor_system())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='GOD Mode Dashboard API Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)