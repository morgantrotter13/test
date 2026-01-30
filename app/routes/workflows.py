"""
API routes for workflow management and execution.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.workflow.engine import workflow_engine
from app.prompt_engine.factory import (
    workflow_runner,
    content_workflow,
    prompt_registry
)


router = APIRouter()


class WorkflowExecuteRequest(BaseModel):
    """Request model for executing a workflow."""
    variables: Optional[Dict[str, Any]] = None


class WorkflowCreateRequest(BaseModel):
    """Request model for creating a workflow."""
    name: str
    definition: Dict[str, Any]


class ContentCreationRequest(BaseModel):
    """Request model for content creation workflow."""
    # Brand analysis inputs
    brand_name: str
    industry: str
    target_audience: str
    brand_values: str
    brand_info: str
    
    # Strategy inputs
    content_goals: str
    platform: str
    post_frequency: Optional[str] = None
    content_themes: Optional[str] = None
    
    # Post generation inputs
    post_topic: str
    tone: Optional[str] = "professional"
    post_type: Optional[str] = "standard"
    include_cta: Optional[bool] = True


@router.get("/")
async def list_workflows() -> Dict[str, List[str]]:
    """List all available workflows."""
    return {"workflows": workflow_engine.list_workflows()}


@router.get("/content-creation")
async def get_content_workflow() -> Dict[str, Any]:
    """Get the content creation workflow definition."""
    workflow_def = content_workflow.definition
    return {
        "name": workflow_def.name,
        "description": workflow_def.description,
        "version": workflow_def.version,
        "steps": [
            {
                "step_id": step.step_id,
                "step_type": step.step_type.value,
                "prompt_name": step.prompt_name,
                "variables": step.variables
            }
            for step in workflow_def.steps
        ],
        "required_variables": content_workflow.get_required_variables()
    }


@router.post("/content-creation/execute")
async def execute_content_creation(
    request: ContentCreationRequest
) -> Dict[str, Any]:
    """Execute the content creation workflow: brand analysis → strategy → post generation."""
    try:
        # Prepare variables for the workflow
        variables = {
            "brand_name": request.brand_name,
            "industry": request.industry,
            "target_audience": request.target_audience,
            "brand_values": request.brand_values,
            "brand_info": request.brand_info,
            "content_goals": request.content_goals,
            "platform": request.platform,
            "post_frequency": request.post_frequency or "daily",
            "content_themes": request.content_themes or "",
            "post_topic": request.post_topic,
            "tone": request.tone,
            "platform": request.platform,
            "post_type": request.post_type,
            "include_cta": request.include_cta
        }
        
        # Execute the workflow
        try:
            result = workflow_runner.run(content_workflow, variables)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Workflow runner error:\n{error_trace}")
            raise HTTPException(
                status_code=500,
                detail=f"Workflow runner failed: {str(e)}"
            )
        
        if not result.success:
            error_details = ', '.join(result.errors) if result.errors else "Unknown error"
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {error_details}"
            )
        
        # Extract outputs from each step
        brand_analysis_output = result.step_results.get("brand_analysis", "")
        strategy_output = result.step_results.get("strategy", "")
        post_output = result.step_results.get("post_generation", "")
        
        return {
            "success": True,
            "workflow_name": result.workflow_name,
            "results": {
                "brand_analysis": {
                    "step_id": "brand_analysis",
                    "output": brand_analysis_output,
                    "rendered_prompt": result.context.get("brand_analysis_rendered_prompt")
                },
                "strategy": {
                    "step_id": "strategy",
                    "output": strategy_output,
                    "rendered_prompt": result.context.get("strategy_rendered_prompt")
                },
                "post_generation": {
                    "step_id": "post_generation",
                    "output": post_output,
                    "rendered_prompt": result.context.get("post_generation_rendered_prompt")
                }
            },
            # Final output is the LLM response from the last step; include the rendered prompt
            "final_output": result.get_final_output(),
            "final_rendered_prompt": result.context.get("post_generation_rendered_prompt"),
            "context": result.context
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        # Log full traceback for debugging
        traceback_str = traceback.format_exc()
        print(f"Workflow execution error:\n{traceback_str}")
        raise HTTPException(
            status_code=500, 
            detail=f"Workflow execution failed: {error_detail}"
        )


@router.get("/{workflow_name}")
async def get_workflow(workflow_name: str) -> Dict[str, Any]:
    """Get a specific workflow by name."""
    workflow = workflow_engine.get_workflow(workflow_name)
    if workflow is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' not found")
    return {"name": workflow_name, "definition": workflow}


@router.post("/{workflow_name}/execute")
async def execute_workflow(
    workflow_name: str,
    request: WorkflowExecuteRequest
) -> Dict[str, Any]:
    """Execute a workflow with given variables."""
    try:
        result = workflow_engine.execute_workflow(workflow_name, request.variables)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.post("/")
async def create_workflow(request: WorkflowCreateRequest) -> Dict[str, str]:
    """Create a new workflow."""
    workflow_engine.add_workflow(request.name, request.definition)
    return {"message": f"Workflow '{request.name}' created successfully", "name": request.name}


@router.post("/reload")
async def reload_workflows() -> Dict[str, str]:
    """Reload all workflows from the filesystem."""
    workflow_engine.reload_workflows()
    return {"message": "Workflows reloaded successfully"}
