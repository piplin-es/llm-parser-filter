"""
Core functionality for LLM-based parsing and filtering.
"""

from typing import Any, Dict, Optional, Union, Callable
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.rate_limiters import InMemoryRateLimiter

import json
from datetime import datetime
import os
from pathlib import Path

DEFAULT_LOG_FILE = "llm_token_usage.log"

rate_limiter = InMemoryRateLimiter(
    requests_per_second=500,      # Allow 1 request per second
    check_every_n_seconds=0.1,  # Check every 100 milliseconds
    max_bucket_size=5,          # Allow bursts of up to 5 requests
)

class TokenUsageLogger(BaseCallbackHandler):
    """Callback handler for logging token usage."""
    
    def __init__(self, function_name: str, log_file: Optional[str] = None):
        """Initialize the handler with function name and log file path."""
        super().__init__()
        self.function_name = function_name
        
        # Use explicitly provided log_file, or environment variable, or default
        self.log_file = log_file or os.getenv('LLM_TOKEN_LOG_FILE') or DEFAULT_LOG_FILE
        print(f"TokenUsageLogger initialized with log file: {self.log_file}")
        
        # Ensure the directory exists
        log_dir = os.path.dirname(self.log_file)
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    def log_to_file(self, data: Dict[str, Any]) -> None:
        """Write log entry to file."""
        try:
            with open(self.log_file, 'a') as f:
                log_entry = json.dumps(data) + '\n'
                f.write(log_entry)
                print(f"Logged entry: {log_entry}")
        except Exception as e:
            print(f"Failed to write to log file {self.log_file}: {e}")
            print(f"Attempted to log: {json.dumps(data)}")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Log errors when they occur."""
        error_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error",
            "function": self.function_name,
            "error": str(error),
            "error_type": type(error).__name__
        }
        self.log_to_file(error_log)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Log token usage when LLM call ends."""
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            usage_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "token_usage",
                "function": self.function_name,
                "model": response.llm_output.get("model_name", "unknown"),
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }
            self.log_to_file(usage_log)

def create_llm(
    model: str,
    provider: str,
    temperature: float,
    function_name: str,
    log_file: Optional[str] = None,
) -> BaseChatModel:
    """
    Create and configure an LLM instance with appropriate callbacks.
    
    Args:
        model: The model identifier to use
        provider: The provider to use ("openai" or "anthropic")
        temperature: The temperature setting for generation
        function_name: Name of the function using this LLM (for logging)
        log_file: Optional path to the log file
        
    Returns:
        Configured LLM instance
        
    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    callbacks = [TokenUsageLogger(function_name=function_name, log_file=log_file)]
    
    if provider == "openai":
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            callbacks=callbacks,
            openai_api_key=api_key,  # Explicitly passing the API key,
            rate_limiter=rate_limiter
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            callbacks=callbacks
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def get_parser(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    provider: str = "openai",
    temperature: float = 0.0,
    log_file: Optional[str] = None,
) -> Callable[[str], Dict[str, Any]]:
    """
    Create a parser that extracts structured data from text using an LLM.
    
    Args:
        prompt: The prompt to use for parsing
        model: The model to use (default: "gpt-3.5-turbo")
        provider: The LLM provider to use ("openai" or "anthropic")
        temperature: The temperature to use for generation (default: 0.0)
        log_file: The path to the log file for token usage logging
        
    Returns:
        A function that takes text and returns structured data
        
    Raises:
        ValueError: If provider is not supported or parsing fails
    """
    llm = create_llm(
        model=model,
        provider=provider,
        temperature=temperature,
        function_name="parser",
        log_file=log_file
    )
    
    # Create message templates
    system_template = """You are a parser that extracts structured data from text.
    The output should be a valid JSON object.
    The fields should be extracted according to the following request:

    {prompt}"""
    
    human_template = "{text}"
    
    # Create the prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
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
    model: str = "gpt-3.5-turbo",
    provider: str = "openai",
    temperature: float = 0.0,
    log_file: Optional[str] = None,
) -> Callable[[str], bool]:
    """
    Create a filter that determines if text meets certain criteria using an LLM.
    
    Args:
        prompt: The prompt to use for filtering
        model: The model to use (default: "gpt-3.5-turbo")
        provider: The LLM provider to use ("openai" or "anthropic")
        temperature: The temperature to use for generation (default: 0.0)
        log_file: The path to the log file for token usage logging
        
    Returns:
        A function that takes text and returns a boolean
        
    Raises:
        ValueError: If provider is not supported or filtering fails
    """
    llm = create_llm(
        model=model,
        provider=provider,
        temperature=temperature,
        function_name="filter",
        log_file=log_file
    )
    
    # Create message templates
    system_template = """You are a filter that determines if text meets certain criteria.
    The output should be a boolean: true or false. It's also should be valid JSON.
    The criteria should be extracted according to the following request:

    {prompt}"""
    
    human_template = "{text}"
    
    # Create the prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])
    
    # Create the output parser
    parser = StrOutputParser()
    
    # Create the chain
    chain = prompt_template | llm | parser
    
    def filter_text(text: str) -> bool:
        """Filter text based on criteria."""
        try:
            result = chain.invoke({"prompt": prompt, "text": text})
            # Convert result to boolean, handling case-insensitive strings
            if isinstance(result, str):
                return result.strip().lower() in ("yes", "true", "1")
            return bool(result)
        except Exception as e:
            raise ValueError(f"Failed to filter text: {str(e)}")
    
    return filter_text

def get_html_parser(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    provider: str = "openai",
    temperature: float = 0.0,
    log_file: Optional[str] = None,
) -> Callable[[Union[str, bytes]], Dict[str, Any]]:
    """
    Create a parser that extracts structured data from HTML content using an LLM.
    The HTML is first converted to plain text before parsing.
    
    Args:
        prompt: The prompt to use for parsing
        model: The model to use (default: "gpt-3.5-turbo")
        provider: The LLM provider to use ("openai" or "anthropic")
        temperature: The temperature to use for generation (default: 0.0)
        log_file: The path to the log file for token usage logging
        
    Returns:
        A function that takes HTML content (as string or base64 bytes) and returns structured data
        
    Raises:
        ValueError: If provider is not supported or parsing fails
    """
    from .text_conversion import html2text
    standard_parser = get_parser(prompt, model, provider, temperature, log_file)
    
    def parse_html(html_content: Union[str, bytes]) -> Dict[str, Any]:
        """Parse HTML content into structured data."""
        try:
            # Convert HTML to plain text
            plain_text = html2text(html_content)
            # Parse the plain text
            return standard_parser(plain_text)
        except Exception as e:
            raise ValueError(f"Failed to parse HTML content: {str(e)}")
    
    return parse_html

def get_pdf_parser(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    provider: str = "openai",
    temperature: float = 0.0,
    log_file: Optional[str] = None,
) -> Callable[[bytes], Dict[str, Any]]:
    """
    Create a parser that extracts structured data from PDF content using an LLM.
    The PDF is first converted to plain text before parsing.
    
    Args:
        prompt: The prompt to use for parsing
        model: The model to use (default: "gpt-3.5-turbo")
        provider: The LLM provider to use ("openai" or "anthropic")
        temperature: The temperature to use for generation (default: 0.0)
        log_file: The path to the log file for token usage logging
        
    Returns:
        A function that takes PDF content (as base64 bytes) and returns structured data
        
    Raises:
        ValueError: If provider is not supported or parsing fails
    """
    from .text_conversion import pdf2text
    standard_parser = get_parser(prompt, model, provider, temperature, log_file)
    
    def parse_pdf(pdf_content: bytes) -> Dict[str, Any]:
        """Parse PDF content into structured data."""
        try:
            # Convert PDF to plain text
            plain_text = pdf2text(pdf_content)
            # Parse the plain text
            return standard_parser(plain_text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF content: {str(e)}")
    
    return parse_pdf 