# LLM Parser Filter

A Python library that provides simple REPL-friendly LLM parser and filter functions using LangChain. It supports both OpenAI and Anthropic models with built-in token usage tracking and rate limiting.

## Features

- **Structured Data Parsing**: Extract structured data from text using LLMs
- **Text Filtering**: Filter text based on custom criteria
- **Token Usage Tracking**: Built-in logging of token consumption
- **Rate Limiting**: Prevent API quota issues with configurable rate limits
- **Multiple LLM Providers**: Support for OpenAI and Anthropic
- **Type Safety**: Full type hints support

## Installation

```bash
uv pip install llm-parser-filter
```

## Usage

### Parser Example

```python
from llm_parser_filter import get_parser

# Create a parser that extracts name and age
parser = get_parser("Extract name and age from the text")

# Parse text
result = parser("John is 25 years old")
print(result)  # {'name': 'John', 'age': 25}
```

### Filter Example

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

Both `get_parser` and `get_filter` accept these parameters:

- `prompt`: The instruction for parsing/filtering
- `model`: Model to use (default: "gpt-3.5-turbo")
- `provider`: "openai" or "anthropic" (default: "openai")
- `temperature`: Model temperature (default: 0.0)
- `log_file`: Path to token usage log file (optional)

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-parser-filter.git
cd llm-parser-filter

# Install dependencies
uv pip install -e ".[test]"

# Run tests
uv run pytest tests/
```

## License

MIT License