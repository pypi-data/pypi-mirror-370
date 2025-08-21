"""
Test script for export functionality
"""
import json
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from reasoning_kernel.cli.session import SessionManager
from reasoning_kernel.cli.export import export_to_json, export_to_markdown, export_to_pdf
from reasoning_kernel.cli.ui import UIManager


def test_export_functionality():
    """Test export functionality with sample data"""
    print("Testing export functionality...")
    
    # Create sample data
    sample_data = {
        "session_id": "test-session-123",
        "description": "Test session for export functionality",
        "created_at": "2025-01-01T12:00:00Z",
        "queries": [
            {
                "query": "Test query 1",
                "timestamp": "2025-01-01T12:01:00Z",
                "result": {
                    "mode": "both",
                    "confidence_analysis": {
                        "overall_confidence": 0.95
                    }
                }
            }
        ]
    }
    
    # Create output directory
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize UI manager
    ui_manager = UIManager(verbose=True)
    
    # Test JSON export
    json_path = os.path.join(output_dir, "test_export.json")
    success = export_to_json(sample_data, json_path, ui_manager)
    if success:
        print("✓ JSON export successful")
        # Verify file exists and can be read
        with open(json_path, 'r') as f:
            loaded_data = json.load(f)
        if loaded_data["session_id"] == sample_data["session_id"]:
            print("✓ JSON export data verification successful")
        else:
            print("✗ JSON export data verification failed")
    else:
        print("✗ JSON export failed")
    
    # Test Markdown export
    md_path = os.path.join(output_dir, "test_export.md")
    success = export_to_markdown(sample_data, md_path, ui_manager)
    if success:
        print("✓ Markdown export successful")
        # Verify file exists
        if os.path.exists(md_path):
            print("✓ Markdown export file creation successful")
        else:
            print("✗ Markdown export file creation failed")
    else:
        print("✗ Markdown export failed")
    
    # Test PDF export (if WeasyPrint is available)
    pdf_path = os.path.join(output_dir, "test_export.pdf")
    try:
        success = export_to_pdf(sample_data, pdf_path, ui_manager)
        if success:
            print("✓ PDF export successful")
            # Verify file exists
            if os.path.exists(pdf_path):
                print("✓ PDF export file creation successful")
            else:
                print("✗ PDF export file creation failed")
        else:
            print("✗ PDF export failed")
    except Exception as e:
        print(f"⚠ PDF export not available: {e}")
    
    print("Export functionality test completed.")


def test_session_export():
    """Test session export functionality"""
    print("\nTesting session export functionality...")
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Create a test session
    session_id = "test-export-session"
    description = "Test session for export"
    
    try:
        # Create session
        created_id = session_manager.create_session(session_id, description)
        print(f"✓ Session created: {created_id}")
        
        # Add a test query
        test_query = "Test query for export"
        test_result = {
            "mode": "both",
            "confidence_analysis": {
                "overall_confidence": 0.85
            }
        }
        
        success = session_manager.add_query_to_session(session_id, test_query, test_result)
        if success:
            print("✓ Query added to session")
        else:
            print("✗ Failed to add query to session")
        
        # Test session export to JSON
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        json_path = os.path.join(output_dir, "session_export.json")
        success = session_manager.export_session(session_id, json_path, "json")
        if success:
            print("✓ Session JSON export successful")
        else:
            print("✗ Session JSON export failed")
        
        # Test session export to Markdown
        md_path = os.path.join(output_dir, "session_export.md")
        success = session_manager.export_session(session_id, md_path, "md")
        if success:
            print("✓ Session Markdown export successful")
        else:
            print("✗ Session Markdown export failed")
        
        # Test history export
        history_json_path = os.path.join(output_dir, "history_export.json")
        success = session_manager.export_history(history_json_path, "json")
        if success:
            print("✓ History JSON export successful")
        else:
            print("✗ History JSON export failed")
        
        # Clean up test session
        session_manager.delete_session(session_id)
        print("✓ Test session cleaned up")
        
    except Exception as e:
        print(f"✗ Session export test failed: {e}")


if __name__ == "__main__":
    test_export_functionality()
    test_session_export()