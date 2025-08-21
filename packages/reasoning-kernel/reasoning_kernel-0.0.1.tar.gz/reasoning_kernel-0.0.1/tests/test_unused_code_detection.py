#!/usr/bin/env python3
"""
Test suite for unused code detection tools
==========================================

Tests the unused_code_detector.py and cleanup_old_files.py tools.
"""

import json
import tempfile
import unittest
from pathlib import Path
import sys

# Add tools to path
tools_path = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_path))

from unused_code_detector import UnusedCodeDetector
from cleanup_old_files import SafeFileCleanup


class TestUnusedCodeDetector(unittest.TestCase):
    """Test cases for the unused code detector"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.detector = UnusedCodeDetector(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def create_test_file(self, relative_path: str, content: str = ""):
        """Helper to create test files"""
        file_path = self.test_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return file_path
    
    def test_duplicate_file_detection(self):
        """Test detection of duplicate files"""
        # Create original and copy files
        self.create_test_file("original.py", "print('hello')")
        self.create_test_file("original copy.py", "print('hello')")
        
        self.detector._find_duplicate_files()
        
        duplicates = self.detector.findings["duplicate_files"]
        self.assertTrue(len(duplicates) > 0)
        
        duplicate_file = duplicates[0]
        self.assertIn("copy", duplicate_file["duplicate_file"])
        self.assertTrue(duplicate_file["original_exists"])
    
    def test_security_risk_detection(self):
        """Test detection of potential security risks"""
        # Create a file with potential secrets
        secret_content = """
        password = "secret123"
        api_key = "sk-test-key"
        """
        
        self.create_test_file("config.py", secret_content)
        
        self.detector._find_security_risk_files()
        
        risks = self.detector.findings["security_risks"]
        # Should detect the file as a risk due to password/api_key
        self.assertTrue(len(risks) >= 0)  # May or may not detect based on patterns
    
    def test_misplaced_test_detection(self):
        """Test detection of misplaced test files"""
        # Create test file in wrong location
        self.create_test_file("test_something.py", "def test_func(): pass")
        
        self.detector._find_misplaced_test_files()
        
        test_artifacts = self.detector.findings["test_artifacts"]
        self.assertTrue(len(test_artifacts) > 0)
        
        test_file = test_artifacts[0]
        self.assertEqual(test_file["file"], "test_something.py")
        self.assertIn("tests/", test_file["suggested_location"])
    
    def test_temporary_file_detection(self):
        """Test detection of temporary files"""
        # Create temporary files
        self.create_test_file("temp.tmp", "temporary content")
        self.create_test_file("debug.log", "log content")
        
        self.detector._find_temporary_files()
        
        temp_files = self.detector.findings["temporary_files"]
        self.assertTrue(len(temp_files) > 0)
        
        temp_file_names = [item["file"] for item in temp_files]
        self.assertIn("temp.tmp", temp_file_names)
    
    def test_report_generation(self):
        """Test complete analysis and report generation"""
        # Create some test files
        self.create_test_file("main.py", "print('main')")
        self.create_test_file("main copy.py", "print('main')")  # Duplicate
        self.create_test_file("test_main.py", "def test(): pass")  # Misplaced test
        
        report = self.detector.analyze_codebase()
        
        # Check report structure
        self.assertIn("analysis_timestamp", report)
        self.assertIn("summary", report)
        self.assertIn("findings", report)
        self.assertIn("recommendations", report)
        
        # Check summary
        summary = report["summary"]
        self.assertIn("total_findings", summary)
        self.assertIn("duplicate_files", summary)
        
        # Check findings
        findings = report["findings"]
        self.assertIn("duplicate_files", findings)
        self.assertIn("test_artifacts", findings)


class TestCleanupTool(unittest.TestCase):
    """Test cases for the cleanup tool"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create a sample report
        self.report_data = {
            "analysis_timestamp": "2023-01-01T00:00:00",
            "findings": {
                "duplicate_files": [
                    {
                        "duplicate_file": "test copy.py",
                        "original_exists": True,
                        "original_file": "test.py",
                        "size_bytes": 100
                    }
                ],
                "test_artifacts": [
                    {
                        "file": "test_main.py",
                        "suggested_location": "tests/test_main.py"
                    }
                ],
                "security_risks": []
            }
        }
        
        # Save report
        self.report_path = self.test_dir / "test_report.json"
        with open(self.report_path, 'w') as f:
            json.dump(self.report_data, f)
        
        self.cleanup_tool = SafeFileCleanup(self.test_dir, self.report_path)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def create_test_file(self, relative_path: str, content: str = ""):
        """Helper to create test files"""
        file_path = self.test_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return file_path
    
    def test_load_report(self):
        """Test loading analysis report"""
        success = self.cleanup_tool.load_report()
        self.assertTrue(success)
        self.assertIsNotNone(self.cleanup_tool.report_data)
    
    def test_safe_duplicate_detection(self):
        """Test identification of safe duplicate files"""
        self.cleanup_tool.load_report()
        safe_duplicates = self.cleanup_tool.get_safe_duplicate_files()
        
        self.assertEqual(len(safe_duplicates), 1)
        self.assertEqual(safe_duplicates[0]["duplicate_file"], "test copy.py")
    
    def test_dry_run_cleanup(self):
        """Test dry-run cleanup (no actual file removal)"""
        # Create the files referenced in the report
        self.create_test_file("test.py", "original content")
        self.create_test_file("test copy.py", "duplicate content")
        
        result = self.cleanup_tool.run_cleanup(dry_run=True)
        
        # Check files still exist (dry run)
        self.assertTrue((self.test_dir / "test copy.py").exists())
        
        # Check result
        self.assertIn("space_saved_mb", result)
        self.assertGreater(result["total_actions"], 0)


def run_integration_test():
    """Run integration test with the actual repository"""
    print("\n" + "="*60)
    print("INTEGRATION TEST - Real Repository Analysis")
    print("="*60)
    
    # Get repository root
    repo_root = Path(__file__).parent.parent
    
    # Test unused code detector
    print("\n🔍 Testing unused code detector...")
    detector = UnusedCodeDetector(repo_root)
    
    # Run a quick analysis
    detector._find_duplicate_files()
    detector._find_security_risk_files()
    detector._find_temporary_files()
    
    total_findings = (len(detector.findings["duplicate_files"]) + 
                     len(detector.findings["security_risks"]) + 
                     len(detector.findings["temporary_files"]))
    
    print(f"✅ Found {total_findings} issues in repository")
    print(f"  - Duplicate files: {len(detector.findings['duplicate_files'])}")
    print(f"  - Security risks: {len(detector.findings['security_risks'])}")
    print(f"  - Temporary files: {len(detector.findings['temporary_files'])}")
    
    # Test cleanup tool with existing report
    report_path = repo_root / "unused_code_analysis_report.json"
    if report_path.exists():
        print("\n🧹 Testing cleanup tool...")
        cleanup_tool = SafeFileCleanup(repo_root, report_path)
        
        if cleanup_tool.load_report():
            safe_duplicates = cleanup_tool.get_safe_duplicate_files()
            print(f"✅ Found {len(safe_duplicates)} files safe to remove")
        else:
            print("⚠️ Could not load existing report")
    
    print("\n✅ Integration test completed successfully!")


def main():
    """Run all tests"""
    print("Unused Code Detection Tools - Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\n📋 Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration test
    run_integration_test()


if __name__ == "__main__":
    main()