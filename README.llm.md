# LLM Parser Filter Usage Guide

This guide explains how to extract structured fields from unstructured data using the LLM Parser Filter library. Whether you're working with HTML documents, PDF files, or raw text, you'll learn how to efficiently convert them into structured, machine-readable fields.

## When to Use Each Parser

### HTML and PDF Parsers (Recommended)

Use these specialized parsers to extract structured fields from HTML or PDF content. They automatically handle format conversion and optimize token usage:

```python
from llm_parser_filter import get_html_parser, get_pdf_parser

# Extract fields from HTML content - use when you have:
# - HTML strings
# - Base64 encoded HTML
# - Web page content
html_parser = get_html_parser("Extract name and age fields")
result = html_parser("""
<html>
    <body>
        <h1>User Profile</h1>
        <p>Name: John Smith</p>
        <p>Age: 25 years old</p>
    </body>
</html>
""")
print(result)  # {'name': 'John Smith', 'age': 25}

# Extract fields from PDF content - use when you have:
# - Raw PDF bytes
# - Base64 encoded PDF
# - PDF file content
pdf_parser = get_pdf_parser("Extract invoice fields: date, amount, company")
result = pdf_parser(pdf_content)
print(result)  # {'date': '2024-03-15', 'amount': 499.99, 'company': 'Acme Corp'}
```

Key features:
- Automatic format detection (raw or base64)
- Efficient extraction of structured fields
- Multi-page PDF support
- HTML structure handling

### Generic Text Parser

Use the generic parser to extract structured fields from plain text or when you need custom preprocessing:

```python
from llm_parser_filter import get_parser

# Best for extracting fields from:
# - Plain text
# - Pre-processed content
# - Custom text formats
parser = get_parser("Extract name and age fields from the text")
result = parser("John is 25 years old")
print(result)  # {'name': 'John', 'age': 25}
```

Note: For HTML or PDF content, prefer the specialized parsers to avoid token overhead.

### Text Filtering

Use filters to classify or categorize text based on field content:

```python
from llm_parser_filter import get_filter

# Common field-based classifications:
# - Sentiment detection
# - Content categorization
# - Priority assessment
# - Topic identification
filter_fn = get_filter("Check if the text contains urgent action items")
is_positive = filter_fn("This is great!")
print(is_positive)  # True
```

## Configuration Options

All parsers and filters accept these parameters:
- `prompt`: The instruction for field extraction or filtering
- `model`: Model to use (default: "gpt-3.5-turbo")
- `provider`: "openai" or "anthropic" (default: "openai")
- `temperature`: Model temperature (default: 0.0)

## Best Practices

1. **Choose the Right Parser**:
   - HTML documents → `get_html_parser`
   - PDF documents → `get_pdf_parser`
   - Plain text → `get_parser`

2. **Write Clear Field Extraction Prompts**:
   ```python
   # Good: Specific fields and formats
   parser = get_parser("Extract these fields: full_name (string), age (number), is_student (boolean)")
   
   # Bad: Vague fields
   parser = get_parser("Get name and age")
   ```

3. **Handle Multiple Document Formats**:
   ```python
   # HTML parser handles both raw and base64
   html_parser = get_html_parser("Extract user profile fields: name, email, role")
   result1 = html_parser(raw_html_string)
   result2 = html_parser(base64_encoded_html)
   
   # PDF parser is equally flexible
   pdf_parser = get_pdf_parser("Extract invoice fields: number, date, total")
   result1 = pdf_parser(pdf_bytes)
   result2 = pdf_parser(base64_encoded_pdf)
   ```

4. **Use Filters for Field-Based Classification**:
   ```python
   # Create specific field checkers
   has_contact = get_filter("Check if the text contains contact information (email or phone)")
   has_price = get_filter("Check if the text mentions a price or amount")
   
   # Apply to any text
   needs_followup = has_contact("Please call me at 555-0123")  # True
   is_commercial = has_price("The service costs $99.99")  # True
   ``` 