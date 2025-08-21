"""
Configuration and fixtures for CLI tests
"""

import pytest
import tempfile
import os


@pytest.fixture(scope="session")
def test_temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def temp_file():
    """Create a temporary file for tests"""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_environment():
    """Create a mock environment for tests"""
    # Store original environment
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["AZURE_OPENAI_API_KEY"] = "test_key"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "test_endpoint"
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = "test_deployment"
    os.environ["DAYTONA_API_KEY"] = "test_daytona_key"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_config_files():
    """Create mock configuration files for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock config directory structure
        config_dir = os.path.join(temp_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Create mock default config
        default_config = {
            "DEFAULT_MODEL": "test-model",
            "MAX_TOKENS": 1000,
            "TEMPERATURE": 0.7
        }
        
        default_config_path = os.path.join(config_dir, "default_config.json")
        import json
        with open(default_config_path, 'w') as f:
            json.dump(default_config, f)
        
        # Create mock user config
        user_config = {
            "CUSTOM_SETTING": "test-value",
            "USER_MODEL": "custom-model"
        }
        
        user_config_path = os.path.join(config_dir, "user_config.json")
        with open(user_config_path, 'w') as f:
            json.dump(user_config, f)
        
        yield {
            "config_dir": config_dir,
            "default_config_path": default_config_path,
            "user_config_path": user_config_path
        }


def pytest_configure(config):
    """Configure pytest settings and markers"""
    # Add custom markers
    config.addinivalue_line("markers", "cli: CLI-related tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "acceptance: User acceptance tests")
    config.addinivalue_line("markers", "mock: Mock-based tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add markers based on test file names
        if "unit" in item.fspath.basename:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)
        elif "performance" in item.fspath.basename:
            item.add_marker(pytest.mark.performance)
        elif "acceptance" in item.fspath.basename:
            item.add_marker(pytest.mark.acceptance)
        elif "mock" in item.fspath.basename:
            item.add_marker(pytest.mark.mock)
        
        # Add CLI marker to all CLI tests
        item.add_marker(pytest.mark.cli)
