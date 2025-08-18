import yaml
from pathlib import Path
from typing import Any, Dict, List, Union

from .models import Prompt, PromptRepository
from .exceptions import InvalidPromptFileError

def load(file_path: Union[str, Path]) -> PromptRepository:
    """
    Loads a prompt repository from a YAML file.

    This function reads a specified YAML file, parses its contents,
    and constructs a PromptRepository object containing all the prompts
    defined in the file.

    Args:
        file_path: The path to the YAML file (can be a string or a Path object).

    Returns:
        A PromptRepository instance containing the loaded prompts.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
        yaml.YAMLError: If the file is not valid YAML.
        InvalidPromptFileError: If the YAML file is not structured correctly (e.g.,
                                not a list of dictionaries, or a required field like
                                'id' or 'template' is missing).
    """
    # Ensure the file_path is a Path object for consistent handling.
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Error: The file '{path}' was not found.")

    # Read the file content and parse it using PyYAML.
    # We use a try-except block to catch potential parsing errors.
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        # Re-raise the YAML error with a more informative message.
        raise yaml.YAMLError(f"Error parsing YAML file '{path}': {e}") from e

    # --- Data Validation ---
    if not isinstance(data, list):
        raise InvalidPromptFileError(f"Error: The YAML file '{path}' should contain a list of prompts.")

    prompts: Dict[str, Prompt] = {}
    for item in data:
        if not isinstance(item, dict):
            raise InvalidPromptFileError(f"Error: Found an item in '{path}' that is not a dictionary.")

        # Check for required fields.
        if 'id' not in item or 'template' not in item:
            raise InvalidPromptFileError(f"Error: A prompt in '{path}' is missing the required 'id' or 'template' field.")

        # Create a Prompt object using the dictionary data.
        # The **item syntax unpacks the dictionary into keyword arguments.
        try:
            prompt = Prompt(**item)
            if prompt.id in prompts:
                raise InvalidPromptFileError(f"Error: Duplicate prompt ID '{prompt.id}' found in '{path}'.")
            prompts[prompt.id] = prompt
        except TypeError as e:
            # This catches errors if the YAML contains keys that don't match
            # the Prompt dataclass fields.
            raise InvalidPromptFileError(f"Error: A prompt in '{path}' has an invalid field: {e}") from e

    return PromptRepository(prompts=prompts)