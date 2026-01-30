"""
Factory for initializing prompt engine components with registered prompts.
"""
from app.prompt_engine.engine import PromptEngine
from app.prompt_engine.registry import PromptRegistry
from app.prompt_engine.workflow import (
    Workflow,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowStepType
)
from app.prompt_engine.runner import WorkflowRunner


def create_prompt_registry(prompts_dir: str = None) -> PromptRegistry:
    """
    Create and initialize a prompt registry with all prompts registered.
    
    Args:
        prompts_dir: Directory containing prompt files
        
    Returns:
        Initialized PromptRegistry
    """
    engine = PromptEngine(prompts_dir)
    registry = PromptRegistry(engine)
    
    # Register all prompts with metadata
    registry.register(
        name="brand_analysis",
        description="Analyzes a brand's voice, messaging, and positioning",
        category="analysis",
        tags=["brand", "analysis", "strategy"],
        version="1.0.0"
    )
    
    registry.register(
        name="strategy",
        description="Creates content strategy based on brand analysis",
        category="strategy",
        tags=["content", "strategy", "planning"],
        version="1.0.0"
    )
    
    registry.register(
        name="post_generation",
        description="Generates social media posts based on brand and strategy",
        category="generation",
        tags=["content", "generation", "social-media"],
        version="1.0.0"
    )
    
    # Register existing prompts
    registry.register(
        name="greeting",
        description="Welcome greeting message",
        category="communication",
        tags=["greeting", "welcome"],
        version="1.0.0"
    )
    
    registry.register(
        name="setup_instructions",
        description="Setup instructions for new users",
        category="communication",
        tags=["setup", "instructions"],
        version="1.0.0"
    )
    
    registry.register(
        name="email_template",
        description="Email template with customizable content",
        category="communication",
        tags=["email", "template"],
        version="1.0.0"
    )
    
    return registry


def create_content_workflow(registry: PromptRegistry) -> Workflow:
    """
    Create the brand analysis → strategy → post generation workflow.
    
    Args:
        registry: Prompt registry to use
        
    Returns:
        Configured Workflow
    """
    definition = WorkflowDefinition(
        name="content_creation",
        description="Complete content creation workflow: brand analysis → strategy → post generation",
        steps=[
            WorkflowStep(
                step_id="brand_analysis",
                step_type=WorkflowStepType.PROMPT,
                prompt_name="brand_analysis",
                model="gpt-4o-mini",
                variables={
                    "brand_name": "{{ brand_name }}",
                    "industry": "{{ industry }}",
                    "target_audience": "{{ target_audience }}",
                    "brand_values": "{{ brand_values }}",
                    "brand_info": "{{ brand_info }}"
                }
            ),
            WorkflowStep(
                step_id="strategy",
                step_type=WorkflowStepType.PROMPT,
                prompt_name="strategy",
                model="gpt-4o-mini",
                variables={
                    "brand_analysis_output": "{{ brand_analysis_output }}",
                    "content_goals": "{{ content_goals }}",
                    "platform": "{{ platform }}",
                    "post_frequency": "{{ post_frequency }}",
                    "content_themes": "{{ content_themes }}"
                }
            ),
            WorkflowStep(
                step_id="post_generation",
                step_type=WorkflowStepType.PROMPT,
                prompt_name="post_generation",
                model="gpt-4o-mini",
                variables={
                    "brand_analysis_output": "{{ brand_analysis_output }}",
                    "strategy_output": "{{ strategy_output }}",
                    "post_topic": "{{ post_topic }}",
                    "tone": "{{ tone }}",
                    "platform": "{{ platform }}",
                    "post_type": "{{ post_type }}",
                    "include_cta": "{{ include_cta }}"
                }
            )
        ],
        version="1.0.0"
    )
    
    return Workflow(definition, registry)


def create_workflow_runner(registry: PromptRegistry) -> WorkflowRunner:
    """
    Create a workflow runner.
    
    Args:
        registry: Prompt registry to use
        
    Returns:
        WorkflowRunner instance
    """
    return WorkflowRunner(registry)


# Global instances
_prompt_engine = PromptEngine()
_prompt_registry = create_prompt_registry()
_workflow_runner = create_workflow_runner(_prompt_registry)
_content_workflow = create_content_workflow(_prompt_registry)

# Export global instances
prompt_registry = _prompt_registry
workflow_runner = _workflow_runner
content_workflow = _content_workflow
