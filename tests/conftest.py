"""
Pytest configuration and fixtures
"""
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_configure(config):
    """Configure pytest"""
    os.environ['FLASK_ENV'] = 'test'
    os.environ['TESTING'] = 'True'
