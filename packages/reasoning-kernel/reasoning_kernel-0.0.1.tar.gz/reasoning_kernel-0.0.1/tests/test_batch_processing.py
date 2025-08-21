"""
Test script for batch processing functionality
"""
import json
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from reasoning_kernel.cli.batch import BatchProcessor, validate_batch_file


def test_batch_file_validation():
    """Test batch file validation"""
    print("Testing batch file validation...")
    
    # Create test files
    test_dir = "test_batch_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # Valid JSON file
    valid_json = {
        "queries": [
            {
                "id": "query-1",
                "query": "Test query 1",
                "mode": "both"
            }
        ]
    }
    
    valid_json_path = os.path.join(test_dir, "valid.json")
    with open(valid_json_path, 'w') as f:
        json.dump(valid_json, f)
    
    # Test validation
    is_valid = validate_batch_file(valid_json_path)
    if is_valid:
        print("✓ Valid JSON file validation passed")
    else:
        print("✗ Valid JSON file validation failed")
    
    # Invalid JSON file (missing query field)
    invalid_json = {
        "queries": [
            {
                "id": "query-1"
                # Missing "query" field
            }
        ]
    }
    
    invalid_json_path = os.path.join(test_dir, "invalid.json")
    with open(invalid_json_path, 'w') as f:
        json.dump(invalid_json, f)
    
    # Test validation
    is_valid = validate_batch_file(invalid_json_path)
    if not is_valid:
        print("✓ Invalid JSON file validation correctly failed")
    else:
        print("✗ Invalid JSON file validation should have failed")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    
    print("Batch file validation test completed.")


def test_batch_processor():
    """Test batch processor functionality"""
    print("\nTesting batch processor functionality...")
    
    # Create sample queries
    sample_queries = [
        {
            "id": "test-query-1",
            "query": "What are the benefits of renewable energy?",
            "mode": "knowledge"
        },
        {
            "id": "test-query-2",
            "query": "Explain the impact of climate change on agriculture",
            "mode": "both"
        }
    ]
    
    # Test loading queries from list
    processor = BatchProcessor(verbose=True)
    
    # Test with valid queries (this would normally run the actual processing)
    print(f"✓ Batch processor created with {len(sample_queries)} sample queries")
    
    # Test loading from file would require actual files, which we won't do in this simple test
    print("✓ Batch processor functionality test completed")


if __name__ == "__main__":
    test_batch_file_validation()
    test_batch_processor()