from typing import Optional
import base64
import html2text as h2t
import pdfplumber
from io import BytesIO
import logging

def html2text(html_content: str | bytes) -> str:
    """
    Convert HTML content to plain text.
    
    Args:
        html_content: HTML content as string or base64 encoded bytes
        
    Returns:
        str: Plain text content
    """
    try:
        # If content is base64 encoded bytes, decode it first
        if isinstance(html_content, bytes):
            html_content = base64.b64decode(html_content).decode('utf-8')
        
        # Convert HTML to text using html2text
        h = h2t.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = True
        return h.handle(html_content)
    except Exception as e:
        logging.error(f"Error converting HTML to text: {str(e)}")
        raise

def pdf2text(pdf_content: bytes) -> str:
    """
    Convert PDF content to plain text.
    
    Args:
        pdf_content: PDF content as base64 encoded bytes
        
    Returns:
        str: Plain text content
    """
    try:
        # Decode base64 content
        # Gmail API uses URL-safe base64, so we need to handle padding
        standard_base64_data = pdf_content.replace("-", "+").replace("_", "/")
        missing_padding = len(standard_base64_data) % 4
        if missing_padding:
            standard_base64_data += '=' * (4 - missing_padding)
        
        pdf_bytes = base64.b64decode(standard_base64_data, validate=True)
        
        # Convert PDF to text using pdfplumber
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        logging.error(f"Error converting PDF to text: {str(e)}")
        raise 