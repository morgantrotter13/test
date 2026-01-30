"""
Workflow Engine - Orchestrates multiple prompts in a workflow.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from app.prompt_engine.engine import prompt_engine
from app.config import settings


class StepType(str, Enum):
    """Types of workflow steps."""
    PROMPT = "prompt"
    CONDITION = "condition"
    LOOP = "loop"
    MERGE = "merge"


class WorkflowStep:
    """Represents a single step in a workflow."""
    
    def __init__(
        self,
        step_id: str,
        step_type: StepType,
        prompt_name: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        condition: Optional[str] = None,
        next_step: Optional[str] = None,
        merge_strategy: Optional[str] = None
    ):
        self.step_id = step_id
        self.step_type = step_type
        self.prompt_name = prompt_name
        self.variables = variables or {}
        self.condition = condition
        self.next_step = next_step
        self.merge_strategy = merge_strategy


class WorkflowEngine:
    """Engine for executing workflows that orchestrate multiple prompts."""
    
    def __init__(self, workflows_dir: Optional[str] = None):
        """
        Initialize the workflow engine.
        
        Args:
            workflows_dir: Directory containing workflow JSON files. Defaults to settings.WORKFLOWS_DIR.
        """
        self.workflows_dir = Path(workflows_dir or settings.WORKFLOWS_DIR)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        self._workflow_cache: Dict[str, Dict[str, Any]] = {}
        self._load_workflows()
    
    def _load_workflows(self):
        """Load all workflow files from the workflows directory."""
        if not self.workflows_dir.exists():
            return
        
        for file_path in self.workflows_dir.glob("*.json"):
            workflow_name = file_path.stem
            with open(file_path, "r", encoding="utf-8") as f:
                self._workflow_cache[workflow_name] = json.load(f)
    
    def get_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow by name.
        
        Args:
            workflow_name: Name of the workflow (filename without .json extension)
            
        Returns:
            Workflow definition or None if not found
        """
        return self._workflow_cache.get(workflow_name)
    
    def list_workflows(self) -> List[str]:
        """
        List all available workflow names.
        
        Returns:
            List of workflow names
        """
        return list(self._workflow_cache.keys())
    
    def execute_workflow(
        self,
        workflow_name: str,
        initial_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow with given initial variables.
        
        Args:
            workflow_name: Name of the workflow to execute
            initial_variables: Initial variables to pass to the workflow
            
        Returns:
            Dictionary containing workflow execution results
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        context = initial_variables or {}
        results = {}
        steps = workflow.get("steps", [])
        
        for step_def in steps:
            step_id = step_def.get("id")
            step_type = StepType(step_def.get("type", "prompt"))
            
            if step_type == StepType.PROMPT:
                prompt_name = step_def.get("prompt")
                if not prompt_name:
                    continue
                
                # Merge step variables with context
                step_variables = {**context, **step_def.get("variables", {})}
                
                # Render the prompt
                rendered_prompt = prompt_engine.render_prompt(
                    prompt_name,
                    step_variables
                )
                
                if rendered_prompt:
                    results[step_id] = {
                        "type": "prompt",
                        "prompt_name": prompt_name,
                        "rendered_prompt": rendered_prompt,
                        "variables": step_variables
                    }
                    
                    # Update context with results (for use in subsequent steps)
                    context[f"{step_id}_result"] = rendered_prompt
            
            elif step_type == StepType.MERGE:
                # Merge results from previous steps
                merge_strategy = step_def.get("strategy", "concat")
                sources = step_def.get("sources", [])
                
                merged_content = self._merge_results(results, sources, merge_strategy)
                results[step_id] = {
                    "type": "merge",
                    "merged_content": merged_content,
                    "strategy": merge_strategy
                }
                context[f"{step_id}_result"] = merged_content
        
        return {
            "workflow_name": workflow_name,
            "results": results,
            "final_context": context
        }
    
    def _merge_results(
        self,
        results: Dict[str, Any],
        sources: List[str],
        strategy: str
    ) -> str:
        """
        Merge results from multiple steps.
        
        Args:
            results: Dictionary of step results
            sources: List of step IDs to merge
            strategy: Merge strategy ('concat', 'join', etc.)
            
        Returns:
            Merged content string
        """
        content_parts = []
        for source_id in sources:
            if source_id in results:
                result = results[source_id]
                if "rendered_prompt" in result:
                    content_parts.append(result["rendered_prompt"])
                elif "merged_content" in result:
                    content_parts.append(result["merged_content"])
        
        if strategy == "concat":
            return "\n\n".join(content_parts)
        elif strategy == "join":
            return " ".join(content_parts)
        else:
            return "\n".join(content_parts)
    
    def reload_workflows(self):
        """Reload all workflows from the filesystem."""
        self._workflow_cache.clear()
        self._load_workflows()
    
    def add_workflow(self, workflow_name: str, workflow_def: Dict[str, Any]):
        """
        Add or update a workflow.
        
        Args:
            workflow_name: Name of the workflow
            workflow_def: Workflow definition dictionary
        """
        workflow_file = self.workflows_dir / f"{workflow_name}.json"
        with open(workflow_file, "w", encoding="utf-8") as f:
            json.dump(workflow_def, f, indent=2)
        self._workflow_cache[workflow_name] = workflow_def


# Global workflow engine instance
workflow_engine = WorkflowEngine()
