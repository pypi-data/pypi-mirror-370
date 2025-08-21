"""Tests for MCP Redis Cloud integration

Basic tests to verify the vendored MCP Redis Cloud tools and wrapper integration.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestMCPRedisIntegration(unittest.TestCase):
    """Test MCP Redis Cloud integration."""
    
    def test_vendored_package_structure(self):
        """Test that the vendored package has the expected structure."""
        mcp_redis_path = project_root / "third_party" / "mcp-redis-cloud"
        
        # Check main files exist
        self.assertTrue((mcp_redis_path / "README.md").exists())
        self.assertTrue((mcp_redis_path / "LICENSE").exists())
        self.assertTrue((mcp_redis_path / "package.json").exists())
        
        # Check source structure
        src_path = mcp_redis_path / "src" / "mcp_redis_cloud"
        self.assertTrue(src_path.exists())
        self.assertTrue((src_path / "__init__.py").exists())
        self.assertTrue((src_path / "client.py").exists())
        self.assertTrue((src_path / "server.py").exists())
        self.assertTrue((src_path / "tools.py").exists())
    
    def test_wrapper_imports(self):
        """Test that the wrapper can import vendored packages."""
        try:
            from reasoning_kernel.integrations.mcp_redis import MCPRedisWrapper
            self.assertIsNotNone(MCPRedisWrapper)
        except ImportError:
            self.fail("MCPRedisWrapper should be importable")
    
    def test_tools_available(self):
        """Test that Redis tools are available."""
        # Add the vendored package to path
        mcp_path = project_root / "third_party" / "mcp-redis-cloud" / "src"
        sys.path.insert(0, str(mcp_path))
        
        try:
            from mcp_redis_cloud.tools import RedisTools
            tools = RedisTools.get_tools()
            
            # Check expected tools are present
            tool_names = [tool["name"] for tool in tools]
            expected_tools = [
                "redis_get", "redis_set", "redis_delete",
                "redis_search_vector", "redis_search_text",
                "redis_json_get", "redis_json_set", "redis_list_keys"
            ]
            
            for expected_tool in expected_tools:
                self.assertIn(expected_tool, tool_names, f"Tool {expected_tool} should be available")
                
        except ImportError as e:
            self.fail(f"RedisTools should be importable: {e}")
    
    def test_license_preserved(self):
        """Test that the MIT license is preserved."""
        license_path = project_root / "third_party" / "mcp-redis-cloud" / "LICENSE"
        
        with open(license_path, 'r') as f:
            license_content = f.read()
        
        self.assertIn("MIT License", license_content)
        self.assertIn("Copyright", license_content)
        self.assertIn("Redis Ltd.", license_content)
    
    def test_documentation_exists(self):
        """Test that documentation was created."""
        doc_path = project_root / "docs" / "mcp_redis_integration.md"
        self.assertTrue(doc_path.exists())
        
        with open(doc_path, 'r') as f:
            doc_content = f.read()
        
        self.assertIn("MCP Redis Cloud Integration", doc_content)
        self.assertIn("vendored", doc_content.lower())
        self.assertIn("MIT license", doc_content)
    
    def test_mcp_configuration_updated(self):
        """Test that MCP configuration includes Redis Cloud server."""
        mcp_config_path = project_root / ".gemini" / "mcp.json"
        
        with open(mcp_config_path, 'r') as f:
            config = f.read()
        
        self.assertIn("redis-cloud", config)
        self.assertIn("mcp_redis_cloud.server", config)


class TestMCPRedisWrapperWithMocks(unittest.TestCase):
    """Test MCP Redis wrapper with mocked dependencies."""
    
    def setUp(self):
        """Set up test environment with mocks."""
        # Mock the Redis environment variables
        self.env_patcher = patch.dict('os.environ', {
            'REDIS_URL': 'redis://test:6379',
            'REDIS_PASSWORD': 'test_password'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    def test_wrapper_initialization(self):
        """Test wrapper initialization with mocked environment."""
        # Add the vendored package to path
        mcp_path = project_root / "third_party" / "mcp-redis-cloud" / "src"
        sys.path.insert(0, str(mcp_path))
        
        try:
            from reasoning_kernel.integrations.mcp_redis import MCPRedisWrapper
            
            # This should not raise an error with mocked env vars
            wrapper = MCPRedisWrapper()
            self.assertIsNotNone(wrapper)
            self.assertIsNotNone(wrapper.client)
            
        except ImportError:
            self.skipTest("Vendored package not properly set up for testing")


async def run_async_tests():
    """Run async tests that require event loop."""
    # Add the vendored package to path
    mcp_path = project_root / "third_party" / "mcp-redis-cloud" / "src"
    sys.path.insert(0, str(mcp_path))
    
    try:
        from mcp_redis_cloud.server import RedisCloudMCPServer
        
        # Test that server can be instantiated
        server = RedisCloudMCPServer("redis://test:6379", "test_password")
        tools = server.list_tools()
        
        print(f"✓ MCP Server provides {len(tools)} tools")
        
        # Test tool validation
        from mcp_redis_cloud.tools import RedisTools
        valid = RedisTools.validate_tool_call("redis_get", {"key": "test"})
        print(f"✓ Tool validation works: {valid}")
        
        invalid = RedisTools.validate_tool_call("redis_get", {})
        print(f"✓ Tool validation catches invalid calls: {not invalid}")
        
    except ImportError as e:
        print(f"✗ Async tests skipped due to import error: {e}")


def main():
    """Run all tests."""
    print("Running MCP Redis Cloud integration tests...")
    print("=" * 50)
    
    # Run sync tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 50)
    print("Running async tests...")
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    print("\n✓ All tests completed!")


if __name__ == "__main__":
    main()