"""
Tests for the LLM Parser Filter package.
"""

import pytest
from llm_parser_filter import get_parser, get_filter, get_html_parser, get_pdf_parser
import os
from pathlib import Path
import json
import base64


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
        prompt="Extract sender, date, subject, and topic"
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
        provider="openai",
        model="gpt-4o"
    )
    
    # Test filtering with different case in prompt
    result = is_urgent(SAMPLE_URGENT_EMAIL)
    
    # Verify result
    assert isinstance(result, bool)
    assert result is True  # This email should be marked as urgent

def test_invoice_parser():
    """Test parsing invoice emails."""
    # Create parser
    invoice_parser = get_parser(
        prompt="""Extract the following information from the invoice email:
        - Invoice Date: The date of the invoice (in YYYY-MM-DD format if possible)
        - Company Name: The company that issued the invoice
        - Amount: The total amount charged (numeric value only)
        - Currency: The currency of the amount (USD, EUR, etc.)
        
        Return the information in JSON format with these exact keys:
        {"date": "YYYY-MM-DD", "company": "Company Name", "amount": 123.45, "currency": "USD"}
        
        If any information is missing, use null for that field."""
    )
    
    # Test email with all information
    complete_email = """
    From: billing@acme.com
    Date: March 15, 2024
    Subject: Invoice #12345 for Services

    Dear Customer,

    Please find attached invoice #12345 from Acme Corp for services rendered.
    
    Amount Due: $499.99
    Due Date: 2024-03-30

    Thank you for your business.
    Best regards,
    Acme Corp
    """
    
    result = invoice_parser(complete_email)
    
    # Verify structure and types
    assert isinstance(result, dict)
    assert "date" in result
    assert "company" in result
    assert "amount" in result
    assert "currency" in result
    
    # Verify specific values
    assert result["date"] == "2024-03-15"  # Should normalize the date
    assert result["company"] == "Acme Corp"
    assert result["amount"] == 499.99
    assert result["currency"] == "USD"
    
    # Test email with missing information
    incomplete_email = """
    Subject: Payment Reminder
    
    Hello,
    
    This is a reminder about the outstanding payment of 299.50 EUR.
    
    Regards,
    """
    
    result = invoice_parser(incomplete_email)
    
    # Verify handling of missing information
    assert result["date"] is None  # Missing date should be null
    assert result["company"] is None  # Missing company should be null
    assert result["amount"] == 299.50
    assert result["currency"] == "EUR"

def test_parser():
    """Test parser with real OpenAI API"""
    parser = get_parser("Extract name and age")
    result = parser("John is 25 years old")
    
    assert isinstance(result, dict)
    assert "name" in result
    assert "age" in result
    assert result["name"] == "John"
    assert result["age"] == 25

def test_filter():
    """Test filter with real OpenAI API"""
    filter_fn = get_filter("Check if text is positive")
    result = filter_fn("This is great!")
    
    assert isinstance(result, bool)
    assert result is True
    
    result = filter_fn("This is terrible!")
    assert result is False

def test_token_logging():
    """Test that token usage is logged correctly"""
    parser = get_parser("Extract name and age")
    parser("John is 25 years old")
    
    # Get the log file path from environment
    log_file = Path(os.getenv('LLM_TOKEN_LOG_FILE'))
    
    # Check that log file exists and contains token usage
    assert log_file.exists()
    with open(log_file) as f:
        logs = [json.loads(line) for line in f]
    assert len(logs) > 0
    assert logs[0]["type"] == "token_usage"
    assert "prompt_tokens" in logs[0]
    assert "completion_tokens" in logs[0]
    assert "total_tokens" in logs[0]
    assert logs[0]["function"] == "parser"

def test_html_parser():
    """Test HTML parser with real OpenAI API"""
    html_parser = get_html_parser("Extract name and age")
    
    # Test with raw HTML string
    html_content = """
    <html>
        <body>
            <h1>User Profile</h1>
            <p>Name: John Smith</p>
            <p>Age: 25 years old</p>
        </body>
    </html>
    """
    result = html_parser(html_content)
    
    assert isinstance(result, dict)
    assert "name" in result
    assert "age" in result
    assert result["name"] == "John Smith"
    assert result["age"] == 25
    
    # Test with base64 encoded HTML
    encoded_html = base64.b64encode(html_content.encode('utf-8'))
    result = html_parser(encoded_html)
    
    assert isinstance(result, dict)
    assert result["name"] == "John Smith"
    assert result["age"] == 25

def test_pdf_parser():
    """Test PDF parser with real OpenAI API"""
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    # Create a PDF in memory
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, "John Smith is 25 years old")
    c.save()
    
    # Get raw PDF bytes
    pdf_bytes = pdf_buffer.getvalue()
    
    # Test with raw PDF bytes
    pdf_parser = get_pdf_parser("Extract name and age")
    result = pdf_parser(pdf_bytes)
    
    # Verify results for raw bytes
    assert isinstance(result, dict)
    assert "name" in result
    assert "age" in result
    assert result["name"] == "John Smith"
    assert result["age"] == 25
    
    # Test with base64 encoded PDF
    pdf_base64 = base64.b64encode(pdf_bytes)
    result = pdf_parser(pdf_base64)
    
    # Verify results for base64
    assert isinstance(result, dict)
    assert "name" in result
    assert "age" in result
    assert result["name"] == "John Smith"
    assert result["age"] == 25
    
    # Test with URL-safe base64 encoded PDF
    pdf_base64_urlsafe = base64.urlsafe_b64encode(pdf_bytes)
    result = pdf_parser(pdf_base64_urlsafe)
    
    # Verify results for URL-safe base64
    assert isinstance(result, dict)
    assert "name" in result
    assert "age" in result
    assert result["name"] == "John Smith"
    assert result["age"] == 25
    
    # Test with invalid PDF content
    with pytest.raises(ValueError):
        pdf_parser(b"invalid pdf data") 