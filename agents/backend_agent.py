import json
import re
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.base_agent import BaseAgent
from core.state_manager import ProjectState

class BackendAgent(BaseAgent):
    """Backend agent for handling server-side development"""
    
    def __init__(self, llm):
        super().__init__("Backend", llm)
    
    def create_system_prompt(self) -> str:
        base_prompt = super().create_system_prompt()
        return f"""{base_prompt}

SPECIALIZED EXPERTISE:
- API development and RESTful services
- Server-side business logic implementation
- Database integration and ORM usage
- Authentication and authorization
- Data validation and processing
- Error handling and logging
- Performance optimization

BEST PRACTICES:
- Follow RESTful API design principles
- Implement proper request/response validation
- Add comprehensive error handling
- Use appropriate HTTP status codes
- Implement security best practices
- Create modular, maintainable code structure
- Add logging and monitoring capabilities

OUTPUT REQUIREMENTS:
- Generate complete backend application structure
- Include API endpoints and routing
- Implement business logic and data processing
- Add authentication and middleware
- Create configuration and environment setup
- Provide API documentation"""

    async def execute_task(self, task: str, state: ProjectState) -> Dict[str, Any]:
        """Execute backend development task"""
        existing_files = self._get_project_context(state.root_path)
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.create_system_prompt()),
            ("human", """
Execute the following backend development task:

TASK: {task}

PROJECT FLOW: {flow}

DESIGN CONFIG: {design_config}

ROOT PATH: {root_path}

EXISTING PROJECT FILES: {existing_files}

Requirements:
1. Analyze task requirements and project flow
2. Create robust backend architecture
3. Implement all necessary API endpoints
4. Add proper error handling and validation
5. Integrate with database layer
6. Follow security best practices
7. Create comprehensive documentation

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
    "api_endpoints": [
        {{
            "method": "GET/POST/PUT/DELETE",
            "path": "/api/endpoint",
            "description": "endpoint purpose"
        }}
    ],
    "summary": "what was accomplished",
    "next_steps": ["recommendations for frontend integration"]
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
            files = self.file_manager.list_files(root_path, ['.py', '.js', '.json', '.sql'])
            context = []
            for file_path in files[:15]:  # Limit to prevent token overflow
                content = self.file_manager.read_file(file_path)
                if content:
                    rel_path = os.path.relpath(file_path, root_path)
                    context.append(f"File: {rel_path}\n{content[:600]}...")
            return "\n\n".join(context)
        except Exception as e:
            return f"Error reading project context: {e}" 