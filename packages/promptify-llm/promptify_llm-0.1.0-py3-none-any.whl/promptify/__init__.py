# promptify/__init__.py

__version__ = "0.1.0"

# A dictionary holding the prompt templates for different models
_PROMPT_TEMPLATES = {
    "default": "{user_prompt}",
    
    "llama2": """[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt} [/INST]""",
    
    "mistral": "[INST] {user_prompt} [/INST]",

    "alpaca": """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{user_prompt}

### Response:
""",
    
    "zephyr": """<|system|>
{system_prompt}</s>
<|user|>
{user_prompt}</s>
<|assistant|>
""",
}

class TemplateNotFoundError(Exception):
    """Custom exception for when a template is not found."""
    pass

def format_prompt(
    model: str, 
    user_prompt: str, 
    system_prompt: str = "You are a helpful assistant."
) -> str:
    """
    Formats a prompt for a given model using its specific template.

    Args:
        model (str): The name of the model to format the prompt for (e.g., 'llama2', 'mistral').
        user_prompt (str): The user's input or question.
        system_prompt (str, optional): The system message or context. 
                                     Defaults to "You are a helpful assistant.".

    Returns:
        str: The fully formatted prompt ready to be sent to the LLM.
        
    Raises:
        TemplateNotFoundError: If the specified model template is not found.
    """
    template = _PROMPT_TEMPLATES.get(model)
    
    if template is None:
        raise TemplateNotFoundError(
            f"Model template '{model}' not found. "
            f"Available templates: {list(_PROMPT_TEMPLATES.keys())}"
        )
        
    # Fill the template with the provided prompts
    return template.format(user_prompt=user_prompt, system_prompt=system_prompt)

def get_available_templates() -> list:
    """Returns a list of all available model template names."""
    return list(_PROMPT_TEMPLATES.keys())