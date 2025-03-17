# LLM Parser Filter

A simple, REPL-friendly package for LLM-based text parsing and filtering.

## Installation

```bash
pip install llm-parser-filter
```

## Usage

The package provides two main functions:

### Parser

```python
from llm_parser_filter import get_parser

# Create a parser function
parse_email = get_parser(
    prompt="Extract the following information from the email: sender, date, subject, and main topic",
    model="gpt-4o",  # or "claude-3-opus-20240229"
    provider="openai"  # or "anthropic"
)

# Use the parser
result = parse_email("""
From: john@example.com
Date: 2024-03-15
Subject: Meeting Tomorrow
Content: Let's discuss the project tomorrow at 2 PM.
""")
print(result)
# Output: {"sender": "john@example.com", "date": "2024-03-15", "subject": "Meeting Tomorrow", "topic": "Project meeting"}
```

### Filter

```python
from llm_parser_filter import get_filter

# Create a filter function
is_urgent = get_filter(
    prompt="Determine if this email is urgent based on its content and subject",
    model="gpt-4o",
    provider="openai"
)

# Use the filter
is_urgent_email = is_urgent("""
Subject: URGENT: System Down
Content: The production system is down. Immediate action required.
""")
print(is_urgent_email)  # True
```

## Environment Variables

The package uses standard environment variables for API keys:

- For OpenAI: `OPENAI_API_KEY`
- For Anthropic: `ANTHROPIC_API_KEY`

## Features

- Simple, REPL-friendly interface
- Support for both OpenAI and Anthropic models
- Configurable temperature and model selection
- Error handling with descriptive messages
- Type hints for better IDE support