"""
Shared test fixtures for the LLM Parser Filter package.
"""

import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_openai():
    """Mock OpenAI LLM responses."""
    with patch('llm_parser_filter.ChatOpenAI') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_anthropic():
    """Mock Anthropic LLM responses."""
    with patch('llm_parser_filter.ChatAnthropic') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance 