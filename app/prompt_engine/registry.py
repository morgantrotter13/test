"""
Prompt Registry - Centralized registry for managing prompts.
"""
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from app.prompt_engine.engine import PromptEngine


@dataclass
class PromptMetadata:
    """Metadata for a registered prompt."""
    name: str
    description: str
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    version: str = "1.0.0"


class PromptRegistry:
    """Registry for managing and discovering prompts."""
    
    def __init__(self, prompt_engine: PromptEngine):
        """
        Initialize the prompt registry.
        
        Args:
            prompt_engine: The prompt engine instance to use
        """
        self.prompt_engine = prompt_engine
        self._registry: Dict[str, PromptMetadata] = {}
        self._validators: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
    
    def register(
        self,
        name: str,
        description: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        version: str = "1.0.0",
        validator: Optional[Callable[[Dict[str, Any]], bool]] = None
    ):
        """
        Register a prompt in the registry.
        
        Args:
            name: Prompt name
            description: Description of what the prompt does
            category: Category for grouping prompts
            tags: List of tags for searching
            version: Version of the prompt
            validator: Optional function to validate input variables
        """
        metadata = PromptMetadata(
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            version=version
        )
        self._registry[name] = metadata
        
        if validator:
            self._validators[name] = validator
    
    def get_metadata(self, name: str) -> Optional[PromptMetadata]:
        """
        Get metadata for a prompt.
        
        Args:
            name: Prompt name
            
        Returns:
            PromptMetadata or None if not found
        """
        return self._registry.get(name)
    
    def list_prompts(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None
    ) -> list[PromptMetadata]:
        """
        List registered prompts with optional filtering.
        
        Args:
            category: Filter by category
            tag: Filter by tag
            
        Returns:
            List of PromptMetadata matching the filters
        """
        prompts = list(self._registry.values())
        
        if category:
            prompts = [p for p in prompts if p.category == category]
        
        if tag:
            prompts = [p for p in prompts if tag in (p.tags or [])]
        
        return prompts
    
    def validate_input(self, name: str, variables: Dict[str, Any]) -> bool:
        """
        Validate input variables for a prompt.
        
        Args:
            name: Prompt name
            variables: Variables to validate
            
        Returns:
            True if valid, False otherwise
        """
        if name not in self._validators:
            return True  # No validator means always valid
        
        validator = self._validators[name]
        return validator(variables)
    
    def get_prompt(self, name: str) -> Optional[str]:
        """Get prompt content from the engine."""
        return self.prompt_engine.get_prompt(name)
    
    def render_prompt(
        self,
        name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Render a prompt with validation.
        
        Args:
            name: Prompt name
            variables: Variables to inject
            
        Returns:
            Rendered prompt or None if not found/invalid
        """
        # Check if prompt exists in the engine (file-based check)
        prompt_content = self.prompt_engine.get_prompt(name)
        if prompt_content is None:
            raise ValueError(f"Prompt '{name}' not found. Available prompts: {', '.join(self.prompt_engine.list_prompts())}")
        
        # Check if registered (optional, for metadata)
        if name not in self._registry:
            # Prompt exists but not registered - still allow rendering but warn
            pass
        
        variables = variables or {}
        if not self.validate_input(name, variables):
            raise ValueError(f"Invalid input variables for prompt '{name}'")
        
        return self.prompt_engine.render_prompt(name, variables)
