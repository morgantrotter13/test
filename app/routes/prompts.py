"""
API routes for prompt management and execution.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.prompt_engine.engine import prompt_engine
from app.prompt_engine.factory import prompt_registry


router = APIRouter()


class PromptRenderRequest(BaseModel):
    """Request model for rendering a prompt."""
    variables: Optional[Dict[str, Any]] = None


class PromptCreateRequest(BaseModel):
    """Request model for creating a prompt."""
    name: str
    content: str


@router.get("/")
async def list_prompts() -> Dict[str, Any]:
    """List all available prompts with metadata."""
    prompts = prompt_engine.list_prompts()
    metadata_list = []
    for prompt_name in prompts:
        metadata = prompt_registry.get_metadata(prompt_name)
        if metadata:
            metadata_list.append({
                "name": metadata.name,
                "description": metadata.description,
                "category": metadata.category,
                "tags": metadata.tags,
                "version": metadata.version
            })
        else:
            metadata_list.append({"name": prompt_name})
    
    return {"prompts": metadata_list}


@router.get("/registry")
async def list_registered_prompts(
    category: Optional[str] = None,
    tag: Optional[str] = None
) -> Dict[str, Any]:
    """List registered prompts with optional filtering."""
    prompts = prompt_registry.list_prompts(category=category, tag=tag)
    return {
        "prompts": [
            {
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "tags": p.tags,
                "version": p.version
            }
            for p in prompts
        ]
    }


@router.get("/{prompt_name}")
async def get_prompt(prompt_name: str) -> Dict[str, Any]:
    """Get a specific prompt by name with metadata."""
    prompt = prompt_engine.get_prompt(prompt_name)
    if prompt is None:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")
    
    metadata = prompt_registry.get_metadata(prompt_name)
    response = {
        "name": prompt_name,
        "content": prompt
    }
    
    if metadata:
        response.update({
            "description": metadata.description,
            "category": metadata.category,
            "tags": metadata.tags,
            "version": metadata.version
        })
    
    return response


@router.post("/{prompt_name}/render")
async def render_prompt(
    prompt_name: str,
    request: PromptRenderRequest
) -> Dict[str, Any]:
    """Render a prompt with variables using the registry."""
    try:
        rendered = prompt_registry.render_prompt(prompt_name, request.variables)
        if rendered is None:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")
        
        return {
            "prompt_name": prompt_name,
            "rendered_prompt": rendered,
            "variables": request.variables or {}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/")
async def create_prompt(request: PromptCreateRequest) -> Dict[str, str]:
    """Create a new prompt."""
    prompt_engine.add_prompt(request.name, request.content)
    return {"message": f"Prompt '{request.name}' created successfully", "name": request.name}


@router.post("/reload")
async def reload_prompts() -> Dict[str, str]:
    """Reload all prompts from the filesystem."""
    prompt_engine.reload_prompts()
    return {"message": "Prompts reloaded successfully"}
