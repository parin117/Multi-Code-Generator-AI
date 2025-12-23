import json
import re
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.base_agent import BaseAgent
from core.state_manager import ProjectState

class DocumentationAgent(BaseAgent):
    """Documentation agent for creating project documentation"""
    
    def __init__(self, llm):
        super().__init__("Documentation", llm)
    
    def create_system_prompt(self) -> str:
        base_prompt = super().create_system_prompt()
        return f"""{base_prompt}

SPECIALIZED EXPERTISE:
- Technical documentation and README creation
- Installation and setup guides
- API documentation
- User guides and tutorials
- Code documentation and comments
- Deployment instructions

BEST PRACTICES:
- Write clear, step-by-step instructions
- Include all necessary prerequisites
- Provide troubleshooting sections
- Add examples and code snippets
- Structure documentation logically
- Make instructions beginner-friendly
- Include deployment and production setup

OUTPUT REQUIREMENTS:
- Generate comprehensive README.md
- Include installation instructions
- Add development setup guide
- Provide API documentation
- Create user guides
- Add troubleshooting section
- Include deployment instructions"""

    async def execute_task(self, task: str, state: ProjectState) -> Dict[str, Any]:
        """Execute documentation task"""
        existing_files = self._get_project_context(state.root_path)
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.create_system_prompt()),
            ("human", """
Create comprehensive documentation for the project:

TASK: {task}

PROJECT FLOW: {flow}

DESIGN CONFIG: {design_config}

ROOT PATH: {root_path}

EXISTING PROJECT FILES: {existing_files}

Create documentation that includes:
1. Complete README.md with project overview
2. Step-by-step installation instructions
3. Development environment setup
4. How to run the application locally
5. API documentation (if applicable)
6. User guide and features overview
7. Troubleshooting common issues
8. Deployment instructions

The documentation should be detailed enough that any developer can:
- Understand what the project does
- Set it up locally without issues
- Start development immediately
- Deploy to production

Return response in JSON format:
{{
    "files": [
        {{
            "path": "relative/path/to/file",
            "content": "complete file content", 
            "description": "file purpose"
        }}
    ],
    "summary": "documentation created",
    "next_steps": ["any additional documentation needed"]
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
            files = self.file_manager.list_files(root_path)
            context = []
            
            # Get file structure
            structure = []
            for file_path in files:
                rel_path = os.path.relpath(file_path, root_path)
                structure.append(rel_path)
            
            context.append(f"Project Structure:\n" + "\n".join(structure[:30]))
            
            # Get sample content from key files
            for file_path in files[:8]:
                content = self.file_manager.read_file(file_path)
                if content:
                    rel_path = os.path.relpath(file_path, root_path)
                    context.append(f"File: {rel_path}\n{content[:400]}...")
                    
            return "\n\n".join(context)
        except Exception as e:
            return f"Error reading project context: {e}" 