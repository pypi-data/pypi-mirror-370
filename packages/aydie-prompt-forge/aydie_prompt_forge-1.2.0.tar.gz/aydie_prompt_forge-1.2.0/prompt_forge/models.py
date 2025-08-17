import dataclasses
from typing import Any, Dict, List, Optional

@dataclasses.dataclass(frozen=True)
class Prompt:
    """ 
    Represents a single, versioned prompt template.

    This class is a dataclass, which means it's primarily for storing data.
    The `frozen=True` argument makes instances of this class immutable,
    This is for data-holding objects to prevent accidental changes.

    Attributes:
        id (str): A unique identifier for the prompt (e.g., 'summarize_article_v1').
        template (str): The raw prompt text, with placeholders for variables.
        version (Optional[str]): The version of the prompt (e.g., '1.0').
        author (Optional[str]): The person who created or last edited the prompt.
        description (Optional[str]): A brief explanation of what the prompt does.
        tags (Optional[List[str]]): A list of tags for categorization (e.g., ['summarization', 'production']).
        model_parameters (Optional[Dict[str, Any]]): A dictionary of parameters to be
            sent to the LLM API, such as temperature, max_tokens, etc.
    """
    id: str
    template: str
    version: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    model_parameters: Optional[Dict[str, Any]] = None
    
    def fill(self, **kwargs: Any) -> str:
        """
        Fills the prompt template with the provided keyword arguments.

        This method uses Python's standard string formatting to replace
        placeholders in the template. For example, a placeholder like
        `{article_text}` would be replaced by the value of the
        `article_text` keyword argument.

        Args:
            **kwargs: The key-value pairs to use for filling the template.

        Returns:
            The formatted prompt string with placeholders replaced.

        Raises:
            KeyError: If a placeholder in the template is not provided
                      as a keyword argument.
        """
        return self.template.format(**kwargs)
    
    
@dataclasses.dataclass
class PromptRepository:
    """ 
    Represents a collection of prompts loaded from a source file.
    
    This class acts as a container and manager for multiple Prompt objects,
    making it easy to access them by their unique ID.
    
    Attributes:
        prompts (Dict[str, Prompt]): A dictionary mapping prompt IDs to their corresponding Prompt objects.
    """
    prompts: Dict[str, Prompt]
    
    def get(self, prompt_id: str) -> Optional[Prompt]:
        """ 
        Retrieves a prompt by it's unique ID
        
        Args: 
            prompt_id: The ID of the prompt to retrieve.
        Returns: 
            The prompt object if found, otherwise None.
        """
        return self.prompts.get(prompt_id)