import sys
import os
import pytest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for testing
os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
os.environ["DEBUG"] = "True"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
