# Text Conversion Utilities

This document describes the text conversion utilities (`html2text` and `pdf2text`) for converting HTML and PDF content to plain text.

## HTML to Text Conversion

The `html2text` function converts HTML content to plain text. It handles both raw HTML strings and base64 encoded content.

### Example Usage

```python
from llm_parser_filter.text_conversion import html2text

# Convert HTML content to plain text
plain_text = html2text(html_content)
```

Features:
- Automatically handles base64 encoded content
- Ignores images for cleaner output
- Preserves links while ignoring emphasis
- Handles UTF-8 encoding/decoding

## PDF to Text Conversion

The `pdf2text` function converts PDF content to plain text. It expects base64 encoded bytes as input.

### Example Usage

```python
from llm_parser_filter.text_conversion import pdf2text

# Convert PDF content to plain text
plain_text = pdf2text(pdf_content)
```

Features:
- Processes multi-page PDFs
- Extracts text from all pages
- Handles URL-safe base64 encoded PDF content
- Automatically handles base64 padding

## Function Details

### html2text

```python
def html2text(html_content: str | bytes) -> str
```

Parameters:
- `html_content`: HTML content as string or base64 encoded bytes

Returns:
- Plain text content as string

### pdf2text

```python
def pdf2text(pdf_content: bytes) -> str
```

Parameters:
- `pdf_content`: PDF content as base64 encoded bytes

Returns:
- Plain text content as string

## Error Handling

Both functions include comprehensive error handling:

- `html2text`:
  - Handles base64 decoding errors
  - Manages UTF-8 encoding/decoding
  - Logs errors with detailed messages

- `pdf2text`:
  - Handles URL-safe base64 decoding and padding
  - Processes PDFs with multiple pages
  - Logs errors with detailed messages
  - Skips pages without extractable text

## Dependencies

The utilities rely on the following external packages:
- `html2text`: For HTML to text conversion
- `pdfplumber`: For PDF text extraction

