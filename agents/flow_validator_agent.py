import json
import re
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from agents.base_agent import BaseAgent
from core.state_manager import ProjectState

class FlowValidatorAgent(BaseAgent):
    """Flow validator agent to ensure complete implementation"""
    
    def __init__(self, llm):
        super().__init__("FlowValidator", llm)
    
    def create_system_prompt(self) -> str:
        base_prompt = super().create_system_prompt()
        return f"""{base_prompt}

SPECIALIZED EXPERTISE:
- Requirements analysis and validation
- Code review and completeness checking
- Flow compliance verification
- Integration testing recommendations
- Quality assurance and best practices
- Gap analysis and recommendations

VALIDATION CRITERIA:
- All flow requirements implemented
- Proper integration between components
- Code quality and best practices followed
- Complete functionality coverage
- Proper error handling implemented
- Documentation completeness
- Security considerations addressed

OUTPUT REQUIREMENTS:
- Comprehensive validation report
- List of missing or incomplete features
- Code quality assessment
- Integration verification
- Recommendations for improvements
- Clear pass/fail determination"""

    async def validate_implementation(self, state: ProjectState) -> Dict[str, Any]:
        """Validate the complete implementation against flow requirements"""
        
        existing_files = self._get_complete_project_context(state.root_path)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.create_system_prompt()),
            ("human", """
Validate the complete project implementation against the original requirements:

ORIGINAL FLOW: {flow}

DESIGN CONFIG: {design_config}

ROOT PATH: {root_path}

COMPLETE PROJECT FILES: {existing_files}

COMPLETED TASKS: {completed_tasks}

Perform comprehensive validation:
1. Check if all flow requirements are implemented
2. Verify proper integration between components
3. Assess code quality and best practices
4. Validate UI/UX against design config
5. Check for missing functionality
6. Evaluate error handling and edge cases
7. Assess documentation completeness

Return detailed validation results in JSON format:
{{
    "validation_status": "PASS/FAIL",
    "overall_completeness": "percentage (0-100)",
    "implemented_features": ["list of implemented features"],
    "missing_features": ["list of missing features"],
    "code_quality_issues": ["list of code quality concerns"],
    "integration_issues": ["list of integration problems"],
    "recommendations": ["list of improvement recommendations"],
    "critical_issues": ["list of critical issues that must be fixed"],
    "next_actions": ["specific tasks to complete the project"]
}}
""")
        ])
        
        response = await self.llm.ainvoke(
            prompt.format_messages(
                flow=state.flow,
                design_config=state.design_config,
                root_path=state.root_path,
                existing_files=existing_files,
                completed_tasks=state.completed_tasks or []
            )
        )
        
        return self._process_validation_response(response.content)
    
    def _get_complete_project_context(self, root_path: str) -> str:
        """Get comprehensive context from all project files"""
        try:
            files = self.file_manager.list_files(root_path)
            context = []
            
            # Project structure
            structure = []
            for file_path in files:
                rel_path = os.path.relpath(file_path, root_path)
                structure.append(rel_path)
            
            context.append(f"Project Structure:\n" + "\n".join(structure))
            
            # File contents (prioritize key files)
            priority_extensions = ['.py', '.js', '.html', '.css', '.json', '.md']
            priority_files = [f for f in files if any(f.endswith(ext) for ext in priority_extensions)]
            
            for file_path in priority_files[:20]:  # Limit to prevent token overflow
                content = self.file_manager.read_file(file_path)
                if content:
                    rel_path = os.path.relpath(file_path, root_path)
                    context.append(f"File: {rel_path}\n{content[:800]}...")
                    
            return "\n\n".join(context)
        except Exception as e:
            return f"Error reading project context: {e}"
    
    def _process_validation_response(self, response_content: str) -> Dict[str, Any]:
        """Process validation response"""
        try:
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {
                    "validation_status": "FAIL",
                    "overall_completeness": "0",
                    "missing_features": ["Could not parse validation response"],
                    "next_actions": ["Review validation process"]
                }
                
            return result
            
        except Exception as e:
            print(f"Error processing validation response: {e}")
            return {
                "validation_status": "FAIL",
                "overall_completeness": "0",
                "missing_features": [f"Validation error: {e}"],
                "next_actions": ["Fix validation process"]
            } 