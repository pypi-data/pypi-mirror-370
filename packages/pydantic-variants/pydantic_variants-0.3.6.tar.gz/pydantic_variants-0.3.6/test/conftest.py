"""
Pytest configuration and shared fixtures for pydantic_variants tests.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# Import all fixtures
from test.fixtures import *
