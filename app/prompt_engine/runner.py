"""
Workflow Runner - Execute workflows and chain prompts together.
"""
from typing import Dict, Any, Optional, List
from app.prompt_engine.workflow import Workflow, WorkflowStepType
from app.prompt_engine.registry import PromptRegistry
from app.llm.client import llm_client
from app.config import settings


class WorkflowResult:
    """Result of a workflow execution."""
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.step_results: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.success: bool = True
    
    def add_step_result(self, step_id: str, result: Any):
        """Add a result for a workflow step."""
        self.step_results[step_id] = result
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def get_final_output(self) -> Optional[str]:
        """Get the final output from the last step."""
        if not self.step_results:
            return None
        
        # Get the last step result
        last_step_id = list(self.step_results.keys())[-1]
        last_result = self.step_results[last_step_id]
        
        if isinstance(last_result, dict) and "output" in last_result:
            return last_result["output"]
        elif isinstance(last_result, str):
            return last_result
        
        return str(last_result)


class WorkflowRunner:
    """Runner for executing workflows."""
    
    def __init__(self, registry: PromptRegistry):
        """
        Initialize the workflow runner.
        
        Args:
            registry: Prompt registry to use
        """
        self.registry = registry
    
    def run(
        self,
        workflow: Workflow,
        initial_variables: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Execute a workflow with given initial variables.
        
        Args:
            workflow: Workflow to execute
            initial_variables: Initial variables to pass to the workflow
            
        Returns:
            WorkflowResult containing execution results
        """
        result = WorkflowResult(workflow.definition.name)
        context = initial_variables.copy() if initial_variables else {}
        
        # Validate workflow before execution
        is_valid, error_msg = workflow.validate()
        if not is_valid:
            result.add_error(f"Workflow validation failed: {error_msg}")
            return result
        
        steps = workflow.get_steps()
        
        print(f"Executing workflow '{workflow.definition.name}' with {len(steps)} steps")
        print(f"Initial context keys: {list(context.keys())}")
        
        for step in steps:
            print(f"Executing step: {step.step_id} (prompt: {step.prompt_name})")
            try:
                step_result = self._execute_step(step, context, result)
                
                if step_result is None:
                    continue
                
                # Store step result
                result.add_step_result(step.step_id, step_result)
                
                # Update context with step result for next steps
                # Use both step_id_output and step_id for flexibility
                context[f"{step.step_id}_output"] = step_result
                context[f"{step.step_id}_result"] = step_result
                # Also add a simplified key if step_id matches expected pattern
                if step.step_id == "brand_analysis":
                    context["brand_analysis_output"] = step_result
                elif step.step_id == "strategy":
                    context["strategy_output"] = step_result
                elif step.step_id == "post_generation":
                    context["post_generation_output"] = step_result
                
                # If step has a transform, apply it
                if step.transform:
                    transformed = step.transform(step_result)
                    context[f"{step.step_id}_transformed"] = transformed
                    result.add_step_result(f"{step.step_id}_transformed", transformed)
            
            except Exception as e:
                import traceback
                error_msg = f"Error in step '{step.step_id}': {str(e)}"
                result.add_error(error_msg)
                # Log full traceback for debugging
                print(f"Step execution error:\n{traceback.format_exc()}")
                # Break on error to stop workflow execution
                break
        
        result.context = context
        return result
    
    def _execute_step(
        self,
        step: 'WorkflowStep',
        context: Dict[str, Any],
        result: WorkflowResult
    ) -> Optional[Any]:
        """
        Execute a single workflow step.
        
        Args:
            step: Workflow step to execute
            context: Current execution context
            result: Workflow result object
            
        Returns:
            Step execution result
        """
        if step.step_type == WorkflowStepType.PROMPT:
            return self._execute_prompt_step(step, context)
        
        elif step.step_type == WorkflowStepType.CONDITION:
            return self._execute_condition_step(step, context)
        
        elif step.step_type == WorkflowStepType.TRANSFORM:
            return self._execute_transform_step(step, context)
        
        return None
    
    def _execute_prompt_step(
        self,
        step: 'WorkflowStep',
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Execute a prompt step."""
        if not step.prompt_name:
            return None
        
        # Merge step variables with context
        # Resolve template variables from context
        step_variables = {}
        for key, value in step.variables.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Template variable - resolve from context
                # Extract variable name from {{ var_name }} or {{var_name}}
                var_name = value.replace("{{", "").replace("}}", "").strip()
                # Try to get from context, fallback to original value
                resolved_value = context.get(var_name, value)
                step_variables[key] = resolved_value
            else:
                step_variables[key] = value
        
        # Add all context variables as well (for direct access in templates)
        # But don't override step-specific variables
        for key, value in context.items():
            if key not in step_variables:
                step_variables[key] = value
        
        # Render the prompt template
        try:
            rendered = self.registry.render_prompt(step.prompt_name, step_variables)
            if rendered is None:
                raise ValueError(f"Failed to render prompt '{step.prompt_name}' - returned None")
        except Exception as e:
            raise ValueError(f"Failed to render prompt '{step.prompt_name}': {str(e)}") from e

        # Keep the rendered template in context for transparency
        context_key = f"{step.step_id}_rendered_prompt"
        context[context_key] = rendered

        # If an LLM key is configured, send the rendered prompt to the model
        if settings.OPENAI_API_KEY:
            llm_output = llm_client.generate(
                prompt=rendered,
                model=step.model,
                temperature=step.temperature,
                max_tokens=step.max_tokens,
            )
            # Keep the rendered prompt in context for transparency
            return llm_output

        # Fallback: return rendered template when no LLM key is set
        return rendered
    
    def _execute_condition_step(
        self,
        step: 'WorkflowStep',
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Execute a condition step."""
        # Simple condition evaluation - can be enhanced
        if step.condition:
            # Evaluate condition using context variables
            try:
                # Simple string-based condition evaluation
                # For production, use a proper expression evaluator
                condition_result = eval(step.condition, {"__builtins__": {}}, context)
                return condition_result
            except Exception:
                return False
        return None
    
    def _execute_transform_step(
        self,
        step: 'WorkflowStep',
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Execute a transform step."""
        if step.transform:
            # Get the previous step's output
            previous_output = context.get("previous_output")
            return step.transform(previous_output)
        return None
