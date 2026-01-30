"""
Prompt Engine - Loads and manages prompts from text files.
"""
import os
from pathlib import Path
from typing import Dict, Optional, Any
from jinja2 import Template, Environment, FileSystemLoader
from app.config import settings


class PromptEngine:
    """Engine for loading and rendering prompts from text files."""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize the prompt engine.
        
        Args:
            prompts_dir: Directory containing prompt files. Defaults to settings.PROMPTS_DIR.
        """
        # Resolve path relative to project root if relative path is provided
        if prompts_dir is None:
            prompts_dir = settings.PROMPTS_DIR
        
        self.prompts_dir = Path(prompts_dir)
        # If relative path, resolve from project root (where app/ directory is)
        if not self.prompts_dir.is_absolute():
            # Get the project root (parent of app/ directory)
            import os
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent  # app/prompt_engine/engine.py -> project root
            self.prompts_dir = project_root / self.prompts_dir
        
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment for template rendering
        self.env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        self._prompt_cache: Dict[str, str] = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompt files from the prompts directory."""
        if not self.prompts_dir.exists():
            return
        
        for file_path in self.prompts_dir.glob("*.txt"):
            prompt_name = file_path.stem
            with open(file_path, "r", encoding="utf-8") as f:
                self._prompt_cache[prompt_name] = f.read()
    
    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Get a prompt by name.
        
        Args:
            prompt_name: Name of the prompt (filename without .txt extension)
            
        Returns:
            Prompt content or None if not found
        """
        return self._prompt_cache.get(prompt_name)
    
    def list_prompts(self) -> list[str]:
        """
        List all available prompt names.
        
        Returns:
            List of prompt names
        """
        return list(self._prompt_cache.keys())
    
    def render_prompt(
        self, 
        prompt_name: str, 
        variables: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Render a prompt with variables using Jinja2 templating.
        
        Args:
            prompt_name: Name of the prompt to render
            variables: Dictionary of variables to inject into the prompt
            
        Returns:
            Rendered prompt string or None if prompt not found
        """
        prompt_template = self.get_prompt(prompt_name)
        if prompt_template is None:
            return None
        
        try:
            template = Template(prompt_template)
            rendered = template.render(**(variables or {}))
            return rendered
        except Exception as e:
            # Re-raise with more context
            raise ValueError(
                f"Failed to render prompt '{prompt_name}': {str(e)}\n"
                f"Variables provided: {list((variables or {}).keys())}"
            ) from e
    
    def reload_prompts(self):
        """Reload all prompts from the filesystem."""
        self._prompt_cache.clear()
        self._load_prompts()
    
    def add_prompt(self, prompt_name: str, content: str):
        """
        Add or update a prompt.
        
        Args:
            prompt_name: Name of the prompt
            content: Prompt content
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(content)
        self._prompt_cache[prompt_name] = content


# Global prompt engine instance
prompt_engine = PromptEngine()
