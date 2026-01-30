"""
Debug routes for troubleshooting.
"""
from fastapi import APIRouter
from app.prompt_engine.factory import prompt_registry, content_workflow, workflow_runner

router = APIRouter()


@router.get("/prompts")
async def list_all_prompts():
    """List all available prompts."""
    prompts = prompt_registry.prompt_engine.list_prompts()
    return {
        "prompts": prompts,
        "count": len(prompts)
    }


@router.get("/prompts/{prompt_name}")
async def get_prompt_content(prompt_name: str):
    """Get a specific prompt's content."""
    content = prompt_registry.prompt_engine.get_prompt(prompt_name)
    if content is None:
        return {"error": f"Prompt '{prompt_name}' not found"}
    return {
        "name": prompt_name,
        "content": content,
        "registered": prompt_name in [p.name for p in prompt_registry.list_prompts()]
    }


@router.get("/workflow/validate")
async def validate_workflow():
    """Validate the content creation workflow."""
    is_valid, error_msg = content_workflow.validate()
    return {
        "valid": is_valid,
        "error": error_msg,
        "steps": [
            {
                "step_id": step.step_id,
                "prompt_name": step.prompt_name,
                "prompt_exists": prompt_registry.prompt_engine.get_prompt(step.prompt_name) is not None if step.prompt_name else False
            }
            for step in content_workflow.get_steps()
        ]
    }


@router.post("/test/render")
async def test_render_prompt(prompt_name: str, variables: dict = None):
    """Test rendering a prompt with variables."""
    try:
        rendered = prompt_registry.render_prompt(prompt_name, variables or {})
        return {
            "success": True,
            "rendered": rendered
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
