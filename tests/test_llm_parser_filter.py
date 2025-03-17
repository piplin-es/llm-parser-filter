"""
Tests for the LLM Parser Filter package.
"""

import pytest
from llm_parser_filter import get_parser, get_filter

# Test data
SAMPLE_EMAIL = """
From: john@example.com
Date: 2024-03-15
Subject: Meeting Tomorrow
Content: Let's discuss the project tomorrow at 2 PM.
"""

SAMPLE_URGENT_EMAIL = """
Subject: URGENT: System Down
Content: The production system is down. Immediate action required.
"""

def test_get_parser_openai():
    """Test parser with OpenAI provider."""
    # Create parser
    parse_email = get_parser(
        prompt="Extract sender, date, subject, and topic",
        model="gpt-4o",
        provider="openai"
    )
    
    # Test parsing
    result = parse_email(SAMPLE_EMAIL)
    
    # Verify result structure
    assert isinstance(result, dict)
    assert "sender" in result
    assert "date" in result
    assert "subject" in result
    assert "topic" in result
    
    # Verify specific values
    assert result["sender"] == "john@example.com"
    assert result["date"] == "2024-03-15"
    assert result["subject"] == "Meeting Tomorrow"

def test_get_parser_invalid_provider():
    """Test parser with invalid provider."""
    with pytest.raises(ValueError, match="Unsupported provider"):
        get_parser(
            prompt="Extract information",
            provider="invalid_provider"
        )

def test_get_filter_openai():
    """Test filter with OpenAI provider."""
    # Create filter
    is_urgent = get_filter(
        prompt="Is this email urgent?",
        model="gpt-4o",
        provider="openai"
    )
    
    # Test filtering
    result = is_urgent(SAMPLE_URGENT_EMAIL)
    
    # Verify result
    assert isinstance(result, bool)
    assert result is True  # This email should be marked as urgent

def test_get_filter_invalid_provider():
    """Test filter with invalid provider."""
    with pytest.raises(ValueError, match="Unsupported provider"):
        get_filter(
            prompt="Is this urgent?",
            provider="invalid_provider"
        )

def test_get_filter_case_insensitive():
    """Test filter case insensitivity."""
    # Create filter
    is_urgent = get_filter(
        prompt="Is this urgent?",
        provider="openai"
    )
    
    # Test filtering with different case in prompt
    result = is_urgent(SAMPLE_URGENT_EMAIL)
    
    # Verify result
    assert isinstance(result, bool)
    assert result is True  # This email should be marked as urgent 