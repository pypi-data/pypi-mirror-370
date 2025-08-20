"""
pytest configuration file for xl_docx processors tests
"""
import pytest
import sys
import os

# Add the parent directory to the path so we can import the processors
sys.path.insert(0, r'D:\git\xilong\py-docx\src')

# Test configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add slow marker to tests that might take longer
        if "complex" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add integration marker to tests that test full workflows
        if "full_process" in item.name or "compile" in item.name:
            item.add_marker(pytest.mark.integration) 