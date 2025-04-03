import pytest
import os
import traceback
from llm_parser_filter import html2text, pdf2text


def test_html2text_with_base64():
    """Test html2text function with base64 encoded content."""
    # Example HTML content
    html_content = """
    <html>
        <body>
            <h1>Test Heading</h1>
            <p>This is a test paragraph.</p>
        </body>
    </html>
    """
    
    # Convert to base64
    import base64
    base64_content = base64.b64encode(html_content.encode('utf-8'))
    
    # Test conversion
    text = html2text(base64_content)
    
    assert isinstance(text, str)
    assert "Test Heading" in text
    assert "test paragraph" in text

def test_pdf2text_with_invalid_data():
    """Test pdf2text function with invalid data."""
    with pytest.raises(Exception):
        pdf2text(b"invalid pdf data")

def test_html2text_preserves_links():
    """Test that html2text preserves links in the output."""
    html_content = """
    <html>
        <body>
            <p>Check out our <a href="https://example.com">website</a> and 
            <a href="https://docs.example.com">documentation</a>.</p>
        </body>
    </html>
    """
    
    # Test conversion
    text = html2text(html_content)
    
    # Verify links are preserved in markdown format
    assert isinstance(text, str)
    assert "[website](https://example.com)" in text
    assert "[documentation](https://docs.example.com)" in text
    assert "Check out our" in text  # Regular text is preserved 