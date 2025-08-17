import pytest
import yaml
from pathlib import Path

# Import the components we need to test
import prompt_forge
from prompt_forge import AydieException, InvalidPromptFileError

# --- Test Fixtures ---
# Fixtures are a powerful feature of pytest. They provide a fixed baseline
# upon which tests can reliably and repeatedly execute.

@pytest.fixture
def valid_prompts_yaml(tmp_path: Path) -> Path:
    """
    A pytest fixture that creates a temporary, valid prompts.yml file.
    This file is created in a temporary directory managed by pytest.
    """
    content = """
            - id: test_summarize_v1
            template: "Summarize this: {text}"
            author: "tester"
            version: "1.0"
            - id: test_classify_v1
            template: "Classify this: {text}"
            model_parameters:
                temperature: 0.5
            """
            
    file_path = tmp_path / "prompts.yml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def duplicate_id_yaml(tmp_path: Path) -> Path:
    """Fixture for a YAML file with duplicate prompt IDs."""
    content = """
            - id: duplicate_id
            template: "First template"
            - id: duplicate_id
            template: "Second template"
            """
            
    file_path = tmp_path / "duplicate.yml"
    file_path.write_text(content)
    return file_path


# --- Test Cases ---

def test_load_success(valid_prompts_yaml: Path):
    """ 
    Tests the happy path: successfully loading a valid repository.
    """
    repo = prompt_forge.load(valid_prompts_yaml)
    assert isinstance(repo, prompt_forge.PromptRepository)
    assert len(repo.prompts) == 2
    
    # Check the first prompt
    summarize_prompt = repo.get("test_summarize_v1")
    assert isinstance(summarize_prompt, prompt_forge.Prompt)
    assert summarize_prompt.id == "test_summarize_v1"
    assert summarize_prompt.author == "tester"
    assert summarize_prompt.fill(text="hello") == "Summarize this: hello"
    
    # Check the second prompt
    classify_prompt = repo.get("test_classify_v1")
    assert classify_prompt.model_parameters == {"temperature": 0.5}
    
def test_load_file_not_found():
    """
    Tests that loading a non-existent file raises FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        prompt_forge.load("non_existent_file.yml")


def test_load_malformed_yaml(malformed_prompts_yaml: Path):
    """
    Tests that a file with a missing required field raises InvalidPromptFileError.
    """
    with pytest.raises(InvalidPromptFileError) as excinfo:
        prompt_forge.load(malformed_prompts_yaml)
    # Check that the error message is helpful.
    assert "missing the required 'id' or 'template' field" in str(excinfo.value)


def test_load_duplicate_id_yaml(duplicate_id_yaml: Path):
    """
    Tests that a file with duplicate prompt IDs raises InvalidPromptFileError.
    """
    with pytest.raises(InvalidPromptFileError) as excinfo:
        prompt_forge.load(duplicate_id_yaml)
    assert "Duplicate prompt ID 'duplicate_id' found" in str(excinfo.value)


def test_load_invalid_yaml_syntax(tmp_path: Path):
    """
    Tests that a file with invalid YAML syntax raises a YAMLError.
    """
    invalid_yaml_content = "key: value\n- not a valid structure"
    file_path = tmp_path / "invalid.yml"
    file_path.write_text(invalid_yaml_content)

    with pytest.raises(yaml.YAMLError):
        prompt_forge.load(file_path)