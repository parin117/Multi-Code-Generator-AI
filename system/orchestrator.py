import asyncio
import os
from typing import Dict, Any, Optional
from core.llm_utils import get_gemini_llm
from core.state_manager import ProjectState
from agents.supervisor_agent import SupervisorAgent
from agents.database_agent import DatabaseAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent

class AutoCodeGenSystem:
    """Main orchestrator for the multi-agent code generation system"""
    
    def __init__(self):
        self.llm = get_gemini_llm()
        self.supervisor = SupervisorAgent(self.llm)
        self.database_agent = DatabaseAgent(self.llm)
        self.backend_agent = BackendAgent(self.llm)
        self.frontend_agent = FrontendAgent(self.llm)
        self.agents = {
            'supervisor': self.supervisor,
            'database': self.database_agent,
            'backend': self.backend_agent,
            'frontend': self.frontend_agent
        }
    
    async def run(self, flow: str, design_config: str, project_name: str) -> Dict[str, Any]:
        """Main execution loop for the code generation system"""
        
        # Initialize project state
        root_path = f"/Users/aaryagopani/Documents/MultiCode_Gen/projects/{project_name}"
        state = ProjectState(
            flow=flow,
            design_config=design_config,
            root_path=root_path
        )
        
        print(f"[System] Starting code generation for project: {project_name}")
        print(f"[System] Project path: {root_path}")
        
        # Ensure project directory exists
        os.makedirs(root_path, exist_ok=True)
        
        iteration = 0
        while iteration < state.max_iterations and not state.is_complete:
            iteration += 1
            state.iteration_count = iteration
            
            print(f"\n[System] Iteration {iteration}")
            print(f"[System] Completed tasks: {len(state.completed_tasks or [])}")
            print(f"[System] Pending tasks: {len(state.pending_tasks or [])}")
            
            # Get next task from supervisor
            task = await self.supervisor.assign_next_task(state)
            
            if not task:
                print("[System] No more tasks available. Project complete!")
                state.is_complete = True
                break
            
            print(f"[System] Executing task: {task['id']} - {task['description']}")
            print(f"[System] Assigned to: {task['agent']} agent")
            
            # Execute task with appropriate agent
            agent = self.agents.get(task['agent'])
            if not agent:
                print(f"[System] Error: Unknown agent type '{task['agent']}'")
                continue
            
            try:
                result = await agent.execute_task(task['description'], state)
                
                # Update state
                if state.completed_tasks is not None:
                    state.completed_tasks.append(task['id'])
                if state.pending_tasks is not None and task['id'] in state.pending_tasks:
                    state.pending_tasks.remove(task['id'])
                
                if state.agent_outputs is not None:
                    state.agent_outputs[task['id']] = result
                
                print(f"[System] Task {task['id']} completed successfully")
                print(f"[System] Summary: {result.get('summary', 'No summary provided')}")
                
                if result.get('created_files'):
                    print(f"[System] Created files: {', '.join(result['created_files'])}")
                
            except Exception as e:
                print(f"[System] Error executing task {task['id']}: {e}")
                # Move task back to pending for retry
                if state.completed_tasks is not None and task['id'] in state.completed_tasks:
                    state.completed_tasks.remove(task['id'])
                if state.pending_tasks is not None and task['id'] not in state.pending_tasks:
                    state.pending_tasks.append(task['id'])
        
        if iteration >= state.max_iterations:
            print(f"[System] Warning: Reached maximum iterations ({state.max_iterations})")
        
        # Generate final summary
        summary = self._generate_summary(state)
        
        return {
            "project_name": project_name,
            "root_path": root_path,
            "iterations": iteration,
            "completed_tasks": state.completed_tasks,
            "summary": summary,
            "is_complete": state.is_complete
        }
    
    def _generate_summary(self, state: ProjectState) -> Dict[str, Any]:
        """Generate comprehensive project summary"""
        total_files = 0
        file_types = {}
        
        # Count files by type
        if state.agent_outputs is not None:
            for task_id, output in state.agent_outputs.items():
                files = output.get('files', [])
                total_files += len(files)
            
            for file_info in files:
                file_path = file_info.get('path', '')
                if file_path:
                    ext = os.path.splitext(file_path)[1]
                    file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_tasks": len(state.completed_tasks or []),
            "total_files": total_files,
            "file_types": file_types,
            "project_structure": self._get_project_structure(state.root_path),
            "agent_contributions": {
                task_id: {
                    "agent": self._get_agent_for_task(task_id, state),
                    "files_created": len(output.get('files', [])),
                    "summary": output.get('summary', '')
                }
                for task_id, output in (state.agent_outputs or {}).items()
            }
        }
    
    def _get_agent_for_task(self, task_id: str, state: ProjectState) -> str:
        """Determine which agent handled a specific task"""
        if not hasattr(state, 'task_plan') or not state.task_plan:
            return "unknown"
        
        all_tasks = (
            state.task_plan.get('database_tasks', []) +
            state.task_plan.get('backend_tasks', []) +
            state.task_plan.get('frontend_tasks', [])
        )
        
        for task in all_tasks:
            if task.get('id') == task_id:
                return task.get('agent', 'unknown')
        
        return "unknown"
    
    def _get_project_structure(self, root_path: str) -> Dict[str, Any]:
        """Get the final project structure"""
        structure = {}
        
        try:
            for root, dirs, files in os.walk(root_path):
                rel_path = os.path.relpath(root, root_path)
                if rel_path == '.':
                    rel_path = ''
                
                structure[rel_path] = {
                    'directories': dirs,
                    'files': [f for f in files if not f.startswith('.')]
                }
        except Exception as e:
            structure['error'] = str(e)
        
        return structure 