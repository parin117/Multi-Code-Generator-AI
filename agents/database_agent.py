import json
import re
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.base_agent import BaseAgent
from core.state_manager import ProjectState

class DatabaseAgent(BaseAgent):
    """Database agent for handling database-related tasks"""
    
    def __init__(self, llm):
        super().__init__("Database", llm)
    
    def create_system_prompt(self) -> str:
        base_prompt = super().create_system_prompt()
        return f"""{base_prompt}

SPECIALIZED EXPERTISE:
- Database design and schema creation
- SQL query optimization and indexing
- Data modeling and relationships
- Database connection management
- Migration scripts and version control
- Data validation and constraints

BEST PRACTICES:
- Design normalized database schemas
- Implement proper indexing strategies
- Add comprehensive data validation
- Create efficient queries
- Handle database connections properly
- Include proper error handling and logging

OUTPUT REQUIREMENTS:
- Generate complete database setup files
- Include schema definitions and relationships
- Provide connection configuration
- Add data seeding if required
- Create database utilities and helpers"""

    async def execute_task(self, task: str, state: ProjectState) -> Dict[str, Any]:
        """Execute database-related task"""
        # Get existing project files for context
        existing_files = self._get_project_context(state.root_path)
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.create_system_prompt()),
            ("human", """
Execute the following database task:

TASK: {task}

PROJECT FLOW: {flow}

DESIGN CONFIG: {design_config}

ROOT PATH: {root_path}

EXISTING PROJECT FILES: {existing_files}

Requirements:
1. Analyze the task and project requirements thoroughly
2. Design appropriate database schema and structure
3. Create all necessary database files and configurations
4. Include proper error handling and validation
5. Generate migration scripts if needed
6. Provide clear documentation

For each file you create, provide:
- File path (relative to root)
- Complete file content
- Brief description of purpose

Return response in JSON format:
{{
    "files": [
        {{
            "path": "relative/path/to/file",
            "content": "complete file content",
            "description": "file purpose"
        }}
    ],
    "summary": "what was accomplished",
    "next_steps": ["any recommendations for other agents"]
}}
""")
        ])
        
        response = await self.llm.ainvoke(
            prompt.format_messages(
                task=task,
                flow=state.flow,
                design_config=state.design_config,
                root_path=state.root_path,
                existing_files=existing_files
            )
        )
        # --- New logic: check if files exist and are correct ---
        try:
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            result = json.loads(json_match.group()) if json_match else {"files": []}
        except Exception:
            result = {"files": []}
        files_to_fix = []
        for file_info in result.get('files', []):
            file_path = os.path.join(state.root_path, file_info['path'])
            if not os.path.exists(file_path):
                files_to_fix.append(file_info)
            else:
                content = self.file_manager.read_file(file_path)
                if content and not self.is_content_correct(content, file_info):
                    files_to_fix.append(file_info)
        if not files_to_fix:
            return {
                "files": [],
                "summary": "All files already exist and are correct. Skipping task.",
                "created_files": [],
                "next_steps": []
            }
        # --- End new logic ---
        # Otherwise, generate/fix the files as before
        for file_info in files_to_fix:
            file_path = os.path.join(state.root_path, file_info['path'])
            self.file_manager.write_file(file_path, file_info['content'])
        created_files = [f['path'] for f in files_to_fix]
        return {
            "files": files_to_fix,
            "summary": result.get('summary', 'Task completed'),
            "created_files": created_files,
            "next_steps": result.get('next_steps', [])
        }
    
    def is_content_correct(self, content: str, file_info: dict) -> bool:
        # Placeholder: always returns False (always rewrites). Replace with LLM or custom logic.
        return False
    
    def _get_project_context(self, root_path: str) -> str:
        """Get context from existing project files"""
        try:
            files = self.file_manager.list_files(root_path, ['.py', '.sql', '.js', '.html', '.css', '.json'])
            context = []
            for file_path in files[:10]:  # Limit to prevent token overflow
                content = self.file_manager.read_file(file_path)
                if content:
                    rel_path = os.path.relpath(file_path, root_path)
                    context.append(f"File: {rel_path}\n{content[:500]}...")
            return "\n\n".join(context)
        except Exception as e:
            return f"Error reading project context: {e}" 