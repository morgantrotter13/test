"""
Workflow System - Define and manage prompt workflows within prompt_engine.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from app.prompt_engine.registry import PromptRegistry


class WorkflowStepType(str, Enum):
    """Types of workflow steps."""
    PROMPT = "prompt"
    CONDITION = "condition"
    TRANSFORM = "transform"


@dataclass
class WorkflowStep:
    """Represents a step in a workflow."""
    step_id: str
    step_type: WorkflowStepType
    prompt_name: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    condition: Optional[str] = None
    transform: Optional[Callable] = None
    next_step: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""
    name: str
    description: str
    steps: List[WorkflowStep]
    version: str = "1.0.0"


class Workflow:
    """Workflow for chaining prompts together."""
    
    def __init__(self, definition: WorkflowDefinition, registry: PromptRegistry):
        """
        Initialize a workflow.
        
        Args:
            definition: Workflow definition
            registry: Prompt registry to use
        """
        self.definition = definition
        self.registry = registry
        self._step_map = {step.step_id: step for step in definition.steps}
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a workflow step by ID."""
        return self._step_map.get(step_id)
    
    def get_steps(self) -> List[WorkflowStep]:
        """Get all workflow steps in order."""
        return self.definition.steps
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that all prompts in the workflow are registered.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        for step in self.definition.steps:
            if step.step_type == WorkflowStepType.PROMPT:
                if not step.prompt_name:
                    return False, f"Step '{step.step_id}' missing prompt_name"
                
                if not self.registry.get_metadata(step.prompt_name):
                    return False, f"Prompt '{step.prompt_name}' not registered in step '{step.step_id}'"
        
        return True, None
    
    def get_required_variables(self) -> List[str]:
        """
        Get list of required variable names for this workflow.
        
        Returns:
            List of variable names
        """
        required = set()
        for step in self.definition.steps:
            # Extract variable names from step variables
            for var_name in step.variables.keys():
                if isinstance(step.variables[var_name], str) and step.variables[var_name].startswith("{{"):
                    # This is a template variable reference
                    var_ref = step.variables[var_name].strip("{}").strip()
                    required.add(var_ref)
            # Also check for direct variable usage in conditions
            if step.condition:
                # Simple extraction - could be enhanced
                pass
        
        return list(required)
