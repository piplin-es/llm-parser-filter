# LLM Parser Filter

A Python library that extracts structured fields from unstructured data using LLMs. Whether you're working with HTML, PDFs, or plain text, it provides specialized parsers to efficiently convert your unstructured content into structured fields. Built on LangChain, it supports both OpenAI and Anthropic models with built-in token usage tracking and rate limiting.

## Features

- **Specialized Format Parsers**: Extract structured fields from HTML and PDF content
- **Structured Data Parsing**: Convert any unstructured text into structured fields
- **Text Filtering**: Filter and classify text based on custom criteria
- **Token Usage Tracking**: Built-in logging of token consumption
- **Rate Limiting**: Prevent API quota issues with configurable rate limits
- **Multiple LLM Providers**: Support for OpenAI and Anthropic
- **Type Safety**: Full type hints support

## Installation

```bash
# Install using uv
uv pip install git+https://github.com/piplin-es/llm-parser-filter.git
```

## Usage

### HTML and PDF Parsing

The library provides specialized parsers that efficiently handle HTML and PDF content by automatically converting them to plain text before processing:

```python
from llm_parser_filter import get_html_parser, get_pdf_parser

# Parse information from HTML
html_parser = get_html_parser("Extract name and age")
html_content = """
<html>
    <body>
        <h1>User Profile</h1>
        <p>Name: John Smith</p>
        <p>Age: 25 years old</p>
    </body>
</html>
"""
result = html_parser(html_content)  # Accepts both raw HTML and base64 encoded
print(result)  # {'name': 'John Smith', 'age': 25}

# Parse information from PDF
pdf_parser = get_pdf_parser("Extract name and age")
result = pdf_parser(pdf_content)  # Accepts both raw bytes and base64 encoded
print(result)  # {'name': 'John Smith', 'age': 25}
```

The specialized parsers support:
- Automatic format detection and conversion
- Both raw content and base64 encoded input
- Multi-page PDF processing
- Token-efficient processing by stripping formatting before LLM processing

### Generic Text Parsing

For plain text or when you need full control over the input processing, use the generic parser:

```python
from llm_parser_filter import get_parser

parser = get_parser("Extract name and age from the text")
result = parser("John is 25 years old")
print(result)  # {'name': 'John', 'age': 25}

# Note: For HTML or PDF content, prefer get_html_parser or get_pdf_parser
# to avoid token overhead from raw formats
```

### Text Filtering

Create filters to classify or categorize text based on custom criteria:

```python
from llm_parser_filter import get_filter

# Create a sentiment filter
filter_fn = get_filter("Check if the text expresses positive sentiment")

# Filter text
is_positive = filter_fn("This is great!")
print(is_positive)  # True
```

### Token Usage Logging

Token usage is automatically logged. You can specify a custom log file:

```python
parser = get_parser(
    "Extract name and age",
    log_file="path/to/logs/usage.log"
)
```

Or use environment variable:
```bash
export LLM_TOKEN_LOG_FILE="path/to/logs/usage.log"
```

### API Keys

Set your API keys as environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

## Configuration

All parser functions (`get_html_parser`, `get_pdf_parser`, `get_parser`) and `get_filter` accept these parameters:

- `prompt`: The instruction for parsing/filtering
- `model`: Model to use (default: "gpt-3.5-turbo")
- `provider`: "openai" or "anthropic" (default: "openai")
- `temperature`: Model temperature (default: 0.0)
- `log_file`: Path to token usage log file (optional)

## License

MIT License