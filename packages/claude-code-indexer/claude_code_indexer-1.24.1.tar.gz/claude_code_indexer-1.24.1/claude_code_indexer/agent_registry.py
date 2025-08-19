"""Claude Code Subagent Registry System."""
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


class AgentType(Enum):
    """Available Claude Code subagent types."""
    GENERAL_PURPOSE = "general-purpose"
    TEST_WRITER = "test-writer"
    DATABASE_ARCHITECT = "database-architect"
    COCOS_3D_DEVELOPER = "cocos-3d-game-developer"
    # Legacy agent types for compatibility
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    

@dataclass
class AgentCapability:
    """Defines capabilities and configuration for a subagent."""
    name: str
    description: str
    tools: List[str]
    prompt_template: str
    model: str = "claude-3-sonnet"
    max_tokens: int = 4000
    specialized_domains: List[str] = field(default_factory=list)
    

class AgentRegistry:
    """Registry of available Claude Code subagents and their capabilities."""
    
    def __init__(self):
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self) -> Dict[AgentType, AgentCapability]:
        """Initialize all available agents with their capabilities."""
        return {
            AgentType.GENERAL_PURPOSE: AgentCapability(
                name="General Purpose Agent",
                description="Handles complex research, code search, and multi-step tasks",
                tools=["*"],  # Access to all tools
                prompt_template="""You are a general-purpose agent capable of handling complex, multi-step tasks.
                Focus on thorough research, accurate code search, and comprehensive analysis.
                When searching for keywords or files, be persistent and thorough.""",
                model="claude-3-sonnet",
                specialized_domains=["research", "analysis", "documentation"]
            ),
            
            AgentType.TEST_WRITER: AgentCapability(
                name="Test Writer Agent",
                description="Specializes in writing unit tests, integration tests, and e2e tests",
                tools=["Read", "Edit", "Write", "Grep", "Bash"],
                prompt_template="""You are a specialized test-writing agent.
                Your expertise includes:
                - Writing comprehensive unit tests with high coverage
                - Creating integration tests for API endpoints
                - Developing end-to-end tests for user workflows
                - Setting up test fixtures and mocks
                - Following testing best practices (AAA pattern, etc.)
                Always ensure tests are maintainable, readable, and follow the project's testing conventions.""",
                model="claude-3-sonnet",
                specialized_domains=["testing", "quality-assurance", "test-automation"]
            ),
            
            AgentType.DATABASE_ARCHITECT: AgentCapability(
                name="Database Architect Agent", 
                description="Designs database schemas, optimizes queries, and manages migrations",
                tools=["Read", "Edit", "Write", "Bash"],
                prompt_template="""You are a database architecture specialist.
                Your expertise includes:
                - Designing normalized, scalable database schemas
                - Optimizing SQL queries for performance
                - Creating and managing database migrations
                - Implementing proper indexes and constraints
                - Following database best practices (ACID, normalization, etc.)
                Think from first principles about data modeling and ensure designs are maintainable.""",
                model="claude-3-opus",
                specialized_domains=["database", "sql", "data-modeling", "migrations"]
            ),
            
            AgentType.COCOS_3D_DEVELOPER: AgentCapability(
                name="Cocos 3D Game Developer",
                description="Develops 3D games using Cocos Creator engine",
                tools=["Read", "Edit", "Write", "Grep"],
                prompt_template="""You are a Cocos Creator 3D game development specialist.
                Your expertise includes:
                - Scene design and 3D asset management
                - TypeScript/JavaScript game logic implementation
                - Physics and collision system setup
                - Performance optimization for mobile/web
                - Lighting, materials, and shader configuration
                Focus on creating performant, engaging 3D experiences using Cocos Creator best practices.""",
                model="claude-3-sonnet",
                specialized_domains=["game-dev", "3d-graphics", "cocos-creator", "typescript"]
            ),
            
            # Legacy agents for backward compatibility
            AgentType.ARCHITECT: AgentCapability(
                name="System Architect",
                description="Plans and designs system architecture",
                tools=["Read", "Grep", "Glob"],
                prompt_template="""You are a system architect focused on high-level design and planning.
                Analyze requirements, design solutions, and create implementation plans.""",
                model="claude-3-opus",
                specialized_domains=["architecture", "system-design", "planning"]
            ),
            
            AgentType.DEVELOPER: AgentCapability(
                name="Software Developer",
                description="Implements code and features",
                tools=["Read", "Edit", "Write", "Bash"],
                prompt_template="""You are a software developer focused on implementation.
                Write clean, maintainable code following best practices and project conventions.""",
                model="claude-3-sonnet",
                specialized_domains=["coding", "implementation", "refactoring"]
            )
        }
    
    def get_agent(self, agent_type: AgentType) -> Optional[AgentCapability]:
        """Get agent capability by type."""
        return self.agents.get(agent_type)
    
    def get_agent_by_name(self, name: str) -> Optional[tuple[AgentType, AgentCapability]]:
        """Find agent by name (case-insensitive)."""
        name_lower = name.lower().replace("-", "_").replace(" ", "_")
        
        for agent_type, capability in self.agents.items():
            if agent_type.value.replace("-", "_") == name_lower:
                return (agent_type, capability)
        
        return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents with their details."""
        agents_list = []
        for agent_type, capability in self.agents.items():
            agents_list.append({
                "type": agent_type.value,
                "name": capability.name,
                "description": capability.description,
                "model": capability.model,
                "tools_count": len(capability.tools) if capability.tools[0] != "*" else "all",
                "specialized_domains": capability.specialized_domains
            })
        return agents_list
    
    def select_agent_for_task(self, task_description: str) -> AgentType:
        """Select the most appropriate agent for a given task."""
        task_lower = task_description.lower()
        
        # Check for test-related keywords
        if any(keyword in task_lower for keyword in [
            'test', 'testing', 'unit test', 'integration test', 'e2e', 
            'coverage', 'mock', 'fixture', 'assertion'
        ]):
            return AgentType.TEST_WRITER
        
        # Check for database-related keywords
        if any(keyword in task_lower for keyword in [
            'database', 'schema', 'sql', 'query', 'migration', 
            'table', 'index', 'constraint', 'normalize'
        ]):
            return AgentType.DATABASE_ARCHITECT
        
        # Check for Cocos/game development keywords
        if any(keyword in task_lower for keyword in [
            'cocos', 'game', '3d', 'scene', 'physics', 
            'animation', 'shader', 'material', 'mesh'
        ]):
            return AgentType.COCOS_3D_DEVELOPER
        
        # Check for architecture/design keywords
        if any(keyword in task_lower for keyword in [
            'design', 'architecture', 'plan', 'structure', 
            'diagram', 'pattern', 'system design'
        ]):
            return AgentType.ARCHITECT
        
        # Check for implementation keywords
        if any(keyword in task_lower for keyword in [
            'implement', 'code', 'develop', 'create', 
            'build', 'feature', 'function', 'api'
        ]):
            return AgentType.DEVELOPER
        
        # Default to general-purpose for complex or unclear tasks
        return AgentType.GENERAL_PURPOSE
    
    def validate_tools_for_agent(self, agent_type: AgentType, requested_tools: List[str]) -> List[str]:
        """Validate and filter tools based on agent capabilities."""
        capability = self.get_agent(agent_type)
        if not capability:
            return []
        
        # If agent has access to all tools
        if capability.tools == ["*"]:
            return requested_tools
        
        # Filter to only allowed tools
        return [tool for tool in requested_tools if tool in capability.tools]