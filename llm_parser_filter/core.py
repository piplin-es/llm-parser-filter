"""
Core functionality for LLM-based parsing and filtering.
"""

from typing import Any, Dict, Optional, Union

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_parser(
    prompt: str,
    model: str = "gpt-4o",
    provider: str = "openai",
    temperature: float = 0.0,
) -> Any:
    """
    Create a parser that extracts structured data from text using an LLM.
    
    Args:
        prompt: The prompt to use for parsing
        model: The model to use (default: "gpt-4o")
        provider: The LLM provider to use ("openai" or "anthropic")
        temperature: The temperature to use for generation (default: 0.0)
        
    Returns:
        A function that takes text and returns structured data
        
    Raises:
        ValueError: If provider is not supported or parsing fails
    """
    # Create the LLM
    if provider == "openai":
        llm = ChatOpenAI(model=model, temperature=temperature)
    elif provider == "anthropic":
        llm = ChatAnthropic(model=model, temperature=temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    

    system_prompt = f"""
    You are a parser that extracts structured data from text.
    The output should be a valid JSON object.
    The fields should be extracted according to the following request:

    {prompt}
    """

    # Create the prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{text}")
    ])
    
    # Create the output parser
    parser = JsonOutputParser()
    
    # Create the chain
    chain = prompt_template | llm | parser
    
    def parse(text: str) -> Dict[str, Any]:
        """Parse text into structured data."""
        try:
            return chain.invoke({"prompt": prompt, "text": text})
        except Exception as e:
            raise ValueError(f"Failed to parse text: {str(e)}")
    
    return parse

def get_filter(
    prompt: str,
    model: str = "gpt-4o",
    provider: str = "openai",
    temperature: float = 0.0,
) -> Any:
    """
    Create a filter that determines if text meets certain criteria using an LLM.
    
    Args:
        prompt: The prompt to use for filtering
        model: The model to use (default: "gpt-4o")
        provider: The LLM provider to use ("openai" or "anthropic")
        temperature: The temperature to use for generation (default: 0.0)
        
    Returns:
        A function that takes text and returns a boolean
        
    Raises:
        ValueError: If provider is not supported or filtering fails
    """
    # Create the LLM
    if provider == "openai":
        llm = ChatOpenAI(model=model, temperature=temperature)
    elif provider == "anthropic":
        llm = ChatAnthropic(model=model, temperature=temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    system_prompt = f"""
    You are a filter that determines if text meets certain criteria.
    The output should be a boolean: true or false.
    The criteria should be extracted according to the following request:

    {prompt}
    """
    # Create the prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{text}")
    ])
    
    # Create the output parser
    parser = JsonOutputParser()
    
    # Create the chain
    chain = prompt_template | llm | parser
    
    def filter_text(text: str) -> bool:
        """Filter text based on criteria."""
        try:
            result = chain.invoke({"prompt": prompt, "text": text})
            # Convert result to boolean, handling case-insensitive strings
            if isinstance(result, str):
                return result.lower() in ("yes", "true", "1")
            return bool(result)
        except Exception as e:
            raise ValueError(f"Failed to filter text: {str(e)}")
    
    return filter_text 