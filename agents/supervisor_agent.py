import json
import re
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from agents.base_agent import BaseAgent
from core.state_manager import ProjectState

class SupervisorAgent(BaseAgent):
    """Supervisor agent that coordinates all other agents"""
    
    def __init__(self, llm):
        super().__init__("Supervisor", llm)
    
    def create_system_prompt(self) -> str:
        return """You are the Supervisor Agent, acting as a senior project manager for software development.

RESPONSIBILITIES:
1. Analyze the complete flow and break it into logical, manageable tasks
2. Assign tasks to appropriate agents (Frontend, Backend, Database, Documentation)
3. Ensure proper task sequencing and dependency management
4. Coordinate between agents for API integrations and data flow
5. Monitor progress and handle any issues that arise

DECISION MAKING:
- Break down complex requirements into specific, actionable tasks
- Consider dependencies between frontend, backend, and database components
- Ensure each task is complete and well-defined
- Prioritize tasks based on dependencies and logical flow

TASK ASSIGNMENT STRATEGY:
- Database tasks first (schema, models, connections)
- Backend tasks second (APIs, business logic, data processing)
- Frontend tasks third (UI components, API integration, user interactions)
- Documentation tasks throughout and final consolidation

Always provide clear, specific task descriptions that agents can execute independently."""

    async def analyze_and_plan(self, state: ProjectState) -> Dict[str, Any]:
        """Analyze flow and create comprehensive task plan"""
        
        print("🔍 Supervisor: Starting project analysis...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.create_system_prompt()),
            ("human", """
Analyze the following project requirements and create a comprehensive task breakdown:

FLOW: {flow}

DESIGN CONFIG: {design_config}

ROOT PATH: {root_path}

Based on this information:
1. Extract the technology stack and architecture requirements
2. Identify all major features and functionalities
3. Break down into specific tasks for each gent type
4. Consider dependencies and proper sequencing
5. Create detailed task descriptions

Return your analysis as a JSON object with:
- "tech_stack": extracted technologies and frameworks
- "architecture": overall system architecture
- "database_tasks": list of database-related tasks
- "backend_tasks": list of backend development tasks  
- "frontend_tasks": list of frontend development tasks
- "integration_points": API endpoints and data flow requirements
- "task_sequence": recommended order of execution

Each task should include:
- "id": unique identifier
- "description": detailed task description
- "agent": target agent (database/backend/frontend)
- "dependencies": list of task IDs this depends on
- "deliverables": expected outputs/files
""")
        ])
        
        print("🔍 Supervisor: Sending request to LLM...")
        
        response = await self.llm.ainvoke(
            prompt.format_messages(
                flow=state.flow,
                design_config=state.design_config,
                root_path=state.root_path
            )
        )
        
        print("🔍 Supervisor: Received LLM response, processing...")
        
        try:
            # Extract JSON from response
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                print("🔍 Supervisor: Successfully parsed JSON response")
                return result
            else:
                # Fallback parsing
                print("🔍 Supervisor: JSON parsing failed, using fallback")
                return self._parse_response_fallback(content)
        except Exception as e:
            print(f"🔍 Supervisor: Error parsing response: {e}")
            return self._create_default_plan(state)
    
    def _parse_response_fallback(self, content: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        # Simple fallback plan
        return {
            "tech_stack": ["HTML", "CSS", "JavaScript", "Python", "SQLite"],
            "database_tasks": [
                {"id": "db_1", "description": "Set up database schema", "agent": "database", "dependencies": []}
            ],
            "backend_tasks": [
                {"id": "be_1", "description": "Create API endpoints", "agent": "backend", "dependencies": ["db_1"]}
            ],
            "frontend_tasks": [
                {"id": "fe_1", "description": "Create user interface", "agent": "frontend", "dependencies": ["be_1"]}
            ]
        }
    
    def _create_default_plan(self, state: ProjectState) -> Dict[str, Any]:
        """Create a default plan when analysis fails"""
        return {
            "tech_stack": ["HTML", "CSS", "JavaScript", "Python", "SQLite"],
            "architecture": "Full-stack web application",
            "database_tasks": [
                {
                    "id": "db_setup",
                    "description": "Initialize database and create schema based on flow requirements",
                    "agent": "database",
                    "dependencies": [],
                    "deliverables": ["database schema", "connection setup", "models"]
                }
            ],
            "backend_tasks": [
                {
                    "id": "api_setup", 
                    "description": "Create backend API structure and endpoints",
                    "agent": "backend",
                    "dependencies": ["db_setup"],
                    "deliverables": ["API endpoints", "business logic", "data validation"]
                }
            ],
            "frontend_tasks": [
                {
                    "id": "ui_setup",
                    "description": "Create frontend user interface and components", 
                    "agent": "frontend",
                    "dependencies": ["api_setup"],
                    "deliverables": ["HTML pages", "CSS styling", "JavaScript functionality"]
                }
            ]
        }
    
    async def assign_next_task(self, state: ProjectState) -> Optional[Dict[str, Any]]:
        """Determine and assign the next task to appropriate agent"""
        
        if state.task_plan is None:
            # Create initial plan
            state.task_plan = await self.analyze_and_plan(state)
        
        # Find next available task based on dependencies
        all_tasks = (
            state.task_plan.get('database_tasks', []) +
            state.task_plan.get('backend_tasks', []) +
            state.task_plan.get('frontend_tasks', [])
        )
        
        for task in all_tasks:
            task_id = task['id']
            if (state.completed_tasks is not None and task_id not in state.completed_tasks and 
                state.pending_tasks is not None and task_id not in state.pending_tasks):
                # Check if dependencies are met
                dependencies = task.get('dependencies', [])
                if state.completed_tasks is not None and all(dep in state.completed_tasks for dep in dependencies):
                    if state.pending_tasks is not None:
                        state.pending_tasks.append(task_id)
                    return task
        
        return None 