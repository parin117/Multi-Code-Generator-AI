import asyncio
import os
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from core.llm_utils import get_gemini_llm
from core.state_manager import ProjectState, State
from agents.supervisor_agent import SupervisorAgent
from agents.database_agent import DatabaseAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.documentation_agent import DocumentationAgent
from agents.flow_validator_agent import FlowValidatorAgent

def get_next_task(state):
    """Get next available task based on dependencies"""
    if state.task_plan is None:
        return None
    
    all_tasks = (
        state.task_plan.get('database_tasks', []) +
        state.task_plan.get('backend_tasks', []) +
        state.task_plan.get('frontend_tasks', [])
    )
    
    for task in all_tasks:
        task_id = task['id']
        if (task_id not in state.completed_tasks and 
            task_id not in state.pending_tasks):
            dependencies = task.get('dependencies', [])
            if all(dep in state.completed_tasks for dep in dependencies):
                return task
    return None

class WorkflowAutoCodeGenSystem:
    """LangGraph-based multi-agent system orchestrator (matches original code.py)"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.llm = get_gemini_llm()
        
        # Initialize agents
        self.supervisor = SupervisorAgent(self.llm)
        self.database_agent = DatabaseAgent(self.llm)
        self.backend_agent = BackendAgent(self.llm)
        self.frontend_agent = FrontendAgent(self.llm)
        self.documentation_agent = DocumentationAgent(self.llm)
        self.flow_validator = FlowValidatorAgent(self.llm)
        
        # Create workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """Create the LangGraph workflow"""
        
        # Create workflow graph
        workflow = StateGraph(State)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("database", self._database_node)
        workflow.add_node("backend", self._backend_node)
        workflow.add_node("frontend", self._frontend_node)
        workflow.add_node("documentation", self._documentation_node)
        workflow.add_node("validator", self._validator_node)
        
        # Add edges
        workflow.set_entry_point("supervisor")
        
        # Conditional routing from supervisor
        workflow.add_conditional_edges("supervisor", self._route_from_supervisor)
        
        # All agents route back to supervisor
        workflow.add_edge("database", "supervisor")
        workflow.add_edge("backend", "supervisor")
        workflow.add_edge("frontend", "supervisor")
        workflow.add_edge("documentation", "supervisor")
        
        # Validator can end or go back to supervisor
        workflow.add_conditional_edges("validator", self._route_from_validator)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _supervisor_node(self, state: State) -> Dict[str, Any]:
        """Supervisor node logic"""
        print(f"🎯 Supervisor: Iteration {state.iteration_count}")
        
        # Convert state to ProjectState for compatibility
        project_state = ProjectState(
            flow=state.flow,
            design_config=state.design_config,
            root_path=state.root_path,
            completed_tasks=state.completed_tasks,
            pending_tasks=state.pending_tasks,
            agent_outputs=state.agent_outputs,
            iteration_count=state.iteration_count,
            max_iterations=state.max_iterations
        )
        
        if state.task_plan is not None:
            project_state.task_plan = state.task_plan
        
        # If no plan, create one
        if state.task_plan is None:
            state.task_plan = await self.supervisor.analyze_and_plan(project_state)
        
        # Find next available task
        next_task = get_next_task(state)
        if next_task:
            # Add to pending_tasks
            if next_task['id'] not in state.pending_tasks:
                state.pending_tasks.append(next_task['id'])
            print(f"📋 Supervisor: Assigning task to {next_task['agent']}: {next_task['description'][:100]}...")
            return {
                "current_task": next_task,
                "iteration_count": state.iteration_count + 1,
                "task_plan": state.task_plan,
                "pending_tasks": state.pending_tasks
            }
        # If no more tasks, trigger validation
        print("✅ Supervisor: All tasks completed, triggering final validation")
        return {"current_task": "validate", "iteration_count": state.iteration_count + 1}
    
    async def _database_node(self, state: State) -> Dict[str, Any]:
        """Database agent node"""
        print("🗄️ Database Agent: Executing task")
        
        if not state.current_task:
            return {"agent_outputs": {**state.agent_outputs, "database": "No task assigned"}}
        
        project_state = ProjectState(
            flow=state.flow,
            design_config=state.design_config,
            root_path=state.root_path,
            completed_tasks=state.completed_tasks
        )
        
        if isinstance(state.current_task, dict):
            task_desc = state.current_task.get('description', str(state.current_task))
            task_id = state.current_task.get('id', f"db_task_{len(state.completed_tasks)}")
        else:
            task_desc = str(state.current_task)
            task_id = f"db_task_{len(state.completed_tasks)}"
        
        result = await self.database_agent.execute_task(task_desc, project_state)
        
        # Update completed tasks
        completed_tasks = state.completed_tasks + [task_id]
        
        # Remove from pending
        pending_tasks = [t for t in state.pending_tasks if t != task_id]
        
        print(f"✅ Database Agent: Task completed - {result.get('summary', 'Done')}")
        
        return {
            "agent_outputs": {**state.agent_outputs, "database": result},
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "current_task": None
        }
    
    async def _backend_node(self, state: State) -> Dict[str, Any]:
        """Backend agent node"""
        print("⚙️ Backend Agent: Executing task")
        
        if not state.current_task:
            return {"agent_outputs": {**state.agent_outputs, "backend": "No task assigned"}}
        
        project_state = ProjectState(
            flow=state.flow,
            design_config=state.design_config,
            root_path=state.root_path,
            completed_tasks=state.completed_tasks
        )
        
        if isinstance(state.current_task, dict):
            task_desc = state.current_task.get('description', str(state.current_task))
            task_id = state.current_task.get('id', f"be_task_{len(state.completed_tasks)}")
        else:
            task_desc = str(state.current_task)
            task_id = f"be_task_{len(state.completed_tasks)}"
        
        result = await self.backend_agent.execute_task(task_desc, project_state)
        
        # Update completed tasks
        completed_tasks = state.completed_tasks + [task_id]
        
        # Remove from pending
        pending_tasks = [t for t in state.pending_tasks if t != task_id]
        
        print(f"✅ Backend Agent: Task completed - {result.get('summary', 'Done')}")
        
        return {
            "agent_outputs": {**state.agent_outputs, "backend": result},
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "current_task": None
        }
    
    async def _frontend_node(self, state: State) -> Dict[str, Any]:
        """Frontend agent node"""
        print("🎨 Frontend Agent: Executing task")
        
        if not state.current_task:
            return {"agent_outputs": {**state.agent_outputs, "frontend": "No task assigned"}}
        
        project_state = ProjectState(
            flow=state.flow,
            design_config=state.design_config,
            root_path=state.root_path,
            completed_tasks=state.completed_tasks
        )
        
        if isinstance(state.current_task, dict):
            task_desc = state.current_task.get('description', str(state.current_task))
            task_id = state.current_task.get('id', f"fe_task_{len(state.completed_tasks)}")
        else:
            task_desc = str(state.current_task)
            task_id = f"fe_task_{len(state.completed_tasks)}"
        
        result = await self.frontend_agent.execute_task(task_desc, project_state)
        
        # Update completed tasks
        completed_tasks = state.completed_tasks + [task_id]
        
        # Remove from pending
        pending_tasks = [t for t in state.pending_tasks if t != task_id]
        
        print(f"✅ Frontend Agent: Task completed - {result.get('summary', 'Done')}")
        
        return {
            "agent_outputs": {**state.agent_outputs, "frontend": result},
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "current_task": None
        }
    
    async def _documentation_node(self, state: State) -> Dict[str, Any]:
        """Documentation agent node"""
        print("📚 Documentation Agent: Executing task")
        
        if not state.current_task:
            return {"agent_outputs": {**state.agent_outputs, "documentation": "No task assigned"}}
        
        project_state = ProjectState(
            flow=state.flow,
            design_config=state.design_config,
            root_path=state.root_path,
            completed_tasks=state.completed_tasks
        )
        
        if isinstance(state.current_task, dict):
            task_desc = state.current_task.get('description', str(state.current_task))
            task_id = state.current_task.get('id', f"doc_task_{len(state.completed_tasks)}")
        else:
            task_desc = str(state.current_task)
            task_id = f"doc_task_{len(state.completed_tasks)}"
        
        result = await self.documentation_agent.execute_task(task_desc, project_state)
        
        # Update completed tasks
        completed_tasks = state.completed_tasks + [task_id]
        
        # Remove from pending
        pending_tasks = [t for t in state.pending_tasks if t != task_id]
        
        print(f"✅ Documentation Agent: Task completed - {result.get('summary', 'Done')}")
        
        return {
            "agent_outputs": {**state.agent_outputs, "documentation": result},
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "current_task": None
        }
    
    async def _validator_node(self, state: State) -> Dict[str, Any]:
        """Validator agent node"""
        print("🔍 Validator Agent: Validating implementation")
        
        project_state = ProjectState(
            flow=state.flow,
            design_config=state.design_config,
            root_path=state.root_path,
            completed_tasks=state.completed_tasks
        )
        
        validation_result = await self.flow_validator.validate_implementation(project_state)
        
        is_complete = validation_result.get('validation_status') == 'PASS'
        
        print(f"📊 Validation Result: {validation_result.get('validation_status')} - {validation_result.get('overall_completeness')}% complete")
        
        if not is_complete:
            # Add missing tasks back to pending
            missing_tasks = validation_result.get('next_actions', [])
            print(f"⚠️ Missing tasks: {missing_tasks}")
        
        return {
            "validation_results": validation_result,
            "is_complete": is_complete,
            "current_task": None
        }
    
    def _route_from_supervisor(self, state: State) -> str:
        """Route from supervisor to appropriate agent"""
        if state.iteration_count >= state.max_iterations:
            print("⏰ Max iterations reached, ending")
            return END
        current_task = state.current_task
        if current_task == "validate":
            return "validator"
        elif isinstance(current_task, dict):
            agent = current_task.get('agent', '').lower()
            if agent == 'database':
                return "database"
            elif agent == 'backend':
                return "backend"
            elif agent == 'frontend':
                return "frontend"
            elif agent == 'documentation':
                return "documentation"
        if current_task is None:
            return "validator"
        return END
    
    def _route_from_validator(self, state: State) -> str:
        """Route from validator"""
        if state.is_complete or state.iteration_count >= state.max_iterations:
            print("🎉 Project completed!")
            return END
        else:
            print("🔄 Validation failed, continuing development")
            return "supervisor"
    
    async def generate_project(self, flow: str, design_config: str, root_path: str) -> Dict[str, Any]:
        """Generate complete project using multi-agent system"""
        
        print("🚀 Starting Auto Code Generation System")
        print(f"📁 Project Path: {root_path}")
        
        # Ensure root directory exists
        from core.file_manager import FileManager
        FileManager.ensure_directory(root_path)
        
        # Initialize state
        initial_state = {
            "flow": flow,
            "design_config": design_config,
            "root_path": root_path,
            "completed_tasks": [],
            "pending_tasks": [],
            "agent_outputs": {},
            "validation_results": {},
            "iteration_count": 0,
            "max_iterations": 500,
            "is_complete": False,
            "current_task": None
        }
        
        # Run workflow
        config = {"configurable": {"thread_id": "main"}, "recursion_limit": 150}
        
        try:
            final_state = None
            async for state in self.workflow.astream(initial_state, config=config):  # type: ignore
                final_state = state
                # Print progress
                for node, data in state.items():
                    if isinstance(data, dict) and 'iteration_count' in data:
                        print(f"📍 Progress: Iteration {data['iteration_count']}")
            
            # Extract final results
            if final_state:
                last_state = list(final_state.values())[-1]
                return {
                    "success": True,
                    "completed_tasks": last_state.get('completed_tasks', []),
                    "agent_outputs": last_state.get('agent_outputs', {}),
                    "validation_results": last_state.get('validation_results', {}),
                    "is_complete": last_state.get('is_complete', False),
                    "iterations": last_state.get('iteration_count', 0)
                }
            else:
                return {"success": False, "error": "No final state received"}
                
        except Exception as e:
            print(f"❌ Error in workflow execution: {e}")
            return {"success": False, "error": str(e)}

def generate_project_with_graph(project_name: str, flow: str, design_config: str):
    """
    Top-level function to generate a project using the LangGraph-based workflow system.
    Sets up the project directory, instantiates the system, and runs the workflow.
    Returns the result of the workflow.
    """
    import asyncio
    root_path = f"/Users/aaryagopani/Documents/MultiCode_Gen/projects/{project_name}"
    system = WorkflowAutoCodeGenSystem()
    return asyncio.run(system.generate_project(flow, design_config, root_path)) 