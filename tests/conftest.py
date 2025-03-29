"""
Shared test fixtures for the LLM Parser Filter package.
"""

import pytest
from datetime import datetime
import os
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_test_logging():
    """Setup test-specific logging configuration."""
    # Get project root (assuming tests/ is directly under project root)
    project_root = Path(__file__).parent.parent
    
    # Create logs directory in project root
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"test_run_{timestamp}.log"
    
    # Set environment variable for the logger
    os.environ['LLM_TOKEN_LOG_FILE'] = str(log_file)
    
    print(f"\nToken usage will be logged to: {log_file}")
    
    yield 