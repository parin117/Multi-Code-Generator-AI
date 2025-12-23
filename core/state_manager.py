from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field

@dataclass
class ProjectState:
    """Central state for the multi-agent system"""
    flow: str
    design_config: str
    root_path: str
    current_task: Optional[str] = None
    completed_tasks: Optional[List[str]] = None
    pending_tasks: Optional[List[str]] = None
    agent_outputs: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    iteration_count: int = 0
    max_iterations: int = 500
    is_complete: bool = False
    task_plan: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []
        if self.pending_tasks is None:
            self.pending_tasks = []
        if self.agent_outputs is None:
            self.agent_outputs = {}
        if self.validation_results is None:
            self.validation_results = {}

# Move State class here (top-level)
class State(BaseModel):
    flow: str = Field(description="Project flow requirements")
    design_config: str = Field(description="Design configuration")
    root_path: str = Field(description="Project root path")
    current_task: Optional[Union[str, dict]] = Field(default=None, description="Current task")
    completed_tasks: List[str] = Field(default_factory=list, description="Completed tasks")
    pending_tasks: List[str] = Field(default_factory=list, description="Pending tasks")
    agent_outputs: Dict[str, Any] = Field(default_factory=dict, description="Agent outputs")
    validation_results: Dict[str, Any] = Field(default_factory=dict, description="Validation results")
    iteration_count: int = Field(default=0, description="Current iteration")
    max_iterations: int = Field(default=500, description="Maximum iterations")
    is_complete: bool = Field(default=False, description="Project completion status")
    task_plan: Optional[Dict[str, Any]] = Field(default=None, description="Task plan") 