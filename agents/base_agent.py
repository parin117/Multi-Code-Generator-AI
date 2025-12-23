from typing import Dict, Any
from core.file_manager import FileManager
from core.state_manager import ProjectState

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, llm):
        self.name = name
        self.llm = llm
        self.file_manager = FileManager()
    
    def create_system_prompt(self) -> str:
        """Create system prompt for the agent"""
        return f"""You are a {self.name} agent in a multi-agent software development system.
        
CORE PRINCIPLES:
1. Write production-quality, well-structured code
2. Follow best practices and coding standards
3. Include comprehensive error handling
4. Add detailed comments and documentation
5. Ensure code is modular and maintainable
6. Validate your work before completion

CAPABILITIES:
- Read existing files in the project directory
- Write new files and modify existing ones
- Create directory structures
- Analyze project requirements and dependencies

Always provide detailed, high-quality implementations that demonstrate professional software development standards."""

    async def execute_task(self, task: str, state: ProjectState) -> Dict[str, Any]:
        """Execute assigned task - to be implemented by subclasses"""
        raise NotImplementedError 