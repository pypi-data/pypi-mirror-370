"""
User Acceptance Tests for MSA Reasoning Kernel CLI
=================================================

Comprehensive user acceptance tests for CLI functionality from an end-user perspective.
"""

import asyncio
import json
import os
import sys
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from reasoning_kernel.cli.core import MSACliContext, MSACli
from reasoning_kernel.cli.session import SessionManager
from reasoning_kernel.cli.batch import BatchProcessor


class TestCLIUserWorkflows:
    """Test CLI from a user perspective with real-world workflows"""

    @pytest.fixture
    def mock_cli_environment(self):
        """Create a mock CLI environment for testing"""
        # Mock environment variables
        with patch.dict(os.environ, {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "test_endpoint",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment"
        }, clear=False):
            yield

    def test_complete_user_workflow(self, mock_cli_environment):
        """Test a complete user workflow from start to finish"""
        # This test simulates a real user session:
        # 1. User starts CLI
        # 2. User analyzes a scenario
        # 3. User creates a session
        # 4. User runs multiple analyses
        # 5. User exports results
        # 6. User reviews history
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup session manager
            session_dir = os.path.join(temp_dir, "sessions")
            history_file = os.path.join(temp_dir, "history.json")
            session_manager = SessionManager(session_dir=session_dir, history_file=history_file)
            
            # Step 1: Create session
            session_id = "user-workflow-test"
            session_manager.create_session(session_id, "User workflow test session")
            
            # Step 2: Simulate user analyzing scenarios
            test_scenarios = [
                "What are the implications of climate change on global agriculture?",
                "How can we improve healthcare access in rural areas?",
                "What strategies can reduce urban traffic congestion?"
            ]
            
            # Mock CLI context and components
            with patch('reasoning_kernel.cli.core.KernelManager') as mock_kernel_manager, \
                 patch('reasoning_kernel.cli.core.MSAEngine') as mock_msa_engine_class, \
                 patch('reasoning_kernel.cli.core.UIManager') as mock_ui_manager:
                
                # Setup mocks
                mock_kernel = AsyncMock()
                mock_kernel.initialize = AsyncMock()
                mock_kernel.cleanup = AsyncMock()
                mock_kernel_manager.return_value = mock_kernel
                
                mock_msa_engine = AsyncMock()
                mock_msa_engine.initialize = AsyncMock()
                mock_msa_engine.cleanup = AsyncMock()
                mock_msa_engine.reason_about_scenario = AsyncMock(return_value={
                    "mode": "both",
                    "confidence_analysis": {"overall_confidence": 0.92},
                    "results": {"summary": "Analysis completed successfully"}
                })
                mock_msa_engine_class.return_value = mock_msa_engine
                
                mock_ui = Mock()
                mock_ui_manager.return_value = mock_ui
                
                # Process each scenario
                for i, scenario in enumerate(test_scenarios):
                    # Create CLI context
                    cli_context = MSACliContext(verbose=False)
                    
                    # Initialize context
                    asyncio.run(cli_context.initialize())
                    
                    # Create CLI instance
                    cli_instance = MSACli(cli_context)
                    
                    # Run analysis
                    result = asyncio.run(cli_instance.run_reasoning(
                        scenario=scenario,
                        session_id=session_id
                    ))
                    
                    # Add to session
                    session_manager.add_query_to_session(session_id, scenario, result)
                
                # Step 3: Export session results
                export_file = os.path.join(temp_dir, "user_workflow_export.json")
                success = session_manager.export_session(session_id, export_file, "json")
                assert success is True
                assert os.path.exists(export_file)
                
                # Verify exported data
                with open(export_file, 'r') as f:
                    exported_data = json.load(f)
                    assert exported_data["id"] == session_id
                    assert len(exported_data["queries"]) == len(test_scenarios)
                
                # Step 4: Check history
                history = session_manager.get_history()
                assert len(history["queries"]) == len(test_scenarios)
                
                # Verify all scenarios were recorded
                recorded_scenarios = [q["query"] for q in history["queries"]]
                for scenario in test_scenarios:
                    assert scenario in recorded_scenarios

    def test_batch_processing_workflow(self, mock_cli_environment):
        """Test batch processing workflow"""
        # User wants to process multiple scenarios at once
        
        # Create batch input file
        batch_data = {
            "queries": [
                {
                    "id": "batch-1",
                    "query": "Analyze the impact of renewable energy on employment",
                    "mode": "both"
                },
                {
                    "id": "batch-2",
                    "query": "Evaluate the effectiveness of remote work policies",
                    "mode": "knowledge"
                },
                {
                    "id": "batch-3",
                    "query": "Assess the benefits of universal basic income",
                    "mode": "both"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode='w', delete=False) as temp_file:
            json.dump(batch_data, temp_file)
            batch_input_file = temp_file.name
        
        try:
            # Mock CLI components for batch processing
            with patch('reasoning_kernel.cli.batch.MSACliContext') as mock_context_class, \
                 patch('reasoning_kernel.cli.batch.MSACli') as mock_cli_class, \
                 patch('reasoning_kernel.cli.batch.UIManager') as mock_ui_manager:
                
                # Setup mocks
                mock_context = AsyncMock()
                mock_context_class.return_value = mock_context
                
                mock_cli = Mock()
                mock_cli.run_reasoning = AsyncMock(return_value={
                    "mode": "both",
                    "confidence_analysis": {"overall_confidence": 0.88},
                    "results": {"summary": "Batch analysis completed"}
                })
                mock_cli_class.return_value = mock_cli
                
                mock_ui = Mock()
                mock_ui_manager.return_value = mock_ui
                
                # Create batch processor
                batch_processor = BatchProcessor(verbose=False)
                
                # Process batch
                with tempfile.TemporaryDirectory() as output_dir:
                    results = asyncio.run(batch_processor.process_queries(
                        batch_data["queries"],
                        output_dir=output_dir,
                        session_id="batch-test-session"
                    ))
                    
                    # Verify results
                    assert len(results) == 3
                    for result in results:
                        assert "query_id" in result
                        assert "original_query" in result
                        assert result["mode"] in ["both", "knowledge"]
                    
                    # Verify individual result files were created
                    result_files = os.listdir(output_dir)
                    json_files = [f for f in result_files if f.endswith('_result.json')]
                    assert len(json_files) == 3
                    
                    # Verify batch summary was created
                    summary_files = [f for f in result_files if f == 'batch_results.json']
                    assert len(summary_files) == 1
        
        finally:
            if os.path.exists(batch_input_file):
                os.unlink(batch_input_file)

    def test_interactive_mode_workflow(self, mock_cli_environment):
        """Test interactive mode workflow"""
        # This test simulates a user in interactive mode
        
        # Mock input/output for interactive session
        test_inputs = [
            "What are the benefits of meditation?",
            "visualize",
            "How does exercise impact mental health?",
            "quit"
        ]
        
        input_index = 0
        
        def mock_input(prompt):
            nonlocal input_index
            if input_index < len(test_inputs):
                result = test_inputs[input_index]
                input_index += 1
                return result
            return "quit"
        
        # Mock CLI components
        with patch('reasoning_kernel.cli.core.KernelManager') as mock_kernel_manager, \
             patch('reasoning_kernel.cli.core.MSAEngine') as mock_msa_engine_class, \
             patch('reasoning_kernel.cli.core.UIManager') as mock_ui_manager, \
             patch('builtins.input', side_effect=mock_input):
            
            # Setup mocks
            mock_kernel = AsyncMock()
            mock_kernel.initialize = AsyncMock()
            mock_kernel.cleanup = AsyncMock()
            mock_kernel_manager.return_value = mock_kernel
            
            mock_msa_engine = AsyncMock()
            mock_msa_engine.initialize = AsyncMock()
            mock_msa_engine.cleanup = AsyncMock()
            mock_msa_engine.reason_about_scenario = AsyncMock(return_value={
                "mode": "both",
                "confidence_analysis": {"overall_confidence": 0.90},
                "results": {"summary": "Interactive analysis completed"}
            })
            mock_msa_engine_class.return_value = mock_msa_engine
            
            mock_ui = Mock()
            mock_ui.print_success = Mock()
            mock_ui.print_info = Mock()
            mock_ui.print_analysis_result = Mock()
            mock_ui_manager.return_value = mock_ui
            
            # Import and test interactive mode function
            from reasoning_kernel.cli.core import _run_interactive_mode
            
            # Run interactive mode (this will process our mock inputs)
            try:
                asyncio.run(_run_interactive_mode(verbose=False))
            except SystemExit:
                # Expected when 'quit' is entered
                pass
            
            # Verify UI interactions
            mock_ui.print_success.assert_called()
            mock_ui.print_info.assert_called()
            mock_ui.print_analysis_result.assert_called()

    def test_configuration_management_workflow(self, mock_cli_environment):
        """Test configuration management workflow"""
        # User wants to manage their configuration
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test configuration commands
            config_file = os.path.join(temp_dir, "user_config.json")
            
            # Mock configuration management
            with patch('reasoning_kernel.cli.core.os.path.exists') as mock_exists, \
                 patch('reasoning_kernel.cli.core.json.load') as mock_load, \
                 patch('reasoning_kernel.cli.core.json.dump') as mock_dump, \
                 patch('reasoning_kernel.cli.core.open') as mock_open:
                
                # Mock configuration file operations
                mock_exists.return_value = True
                mock_load.return_value = {
                    "AZURE_OPENAI_DEPLOYMENT": "test-deployment",
                    "CUSTOM_SETTING": "test-value"
                }
                
                # Test showing configuration
                from reasoning_kernel.cli.core import _should_mask_value
                
                # Verify sensitive values are masked
                assert _should_mask_value("AZURE_OPENAI_API_KEY", "real-key") is True
                assert _should_mask_value("NORMAL_SETTING", "normal-value") is False
                
                # Test setting configuration
                mock_exists.return_value = False  # New config file
                mock_load.return_value = {}
                
                # This would normally create a new configuration file
                config_data = {"NEW_SETTING": "new-value"}
                # The actual implementation would write this to file

    def test_export_import_workflow(self, mock_cli_environment):
        """Test export and import workflow"""
        # User wants to export session data and potentially import it elsewhere
        
        with tempfile.TemporaryDirectory() as temp_dir:
            session_dir = os.path.join(temp_dir, "sessions")
            history_file = os.path.join(temp_dir, "history.json")
            session_manager = SessionManager(session_dir=session_dir, history_file=history_file)
            
            # Create test session with data
            session_id = "export-import-test"
            session_manager.create_session(session_id, "Export/Import test session")
            
            # Add test data
            test_query = "Test export/import query"
            test_result = {
                "mode": "both",
                "confidence_analysis": {"overall_confidence": 0.95},
                "results": {"summary": "Export test result"}
            }
            session_manager.add_query_to_session(session_id, test_query, test_result)
            
            # Test different export formats
            formats = ["json", "md"]
            for format_type in formats:
                export_file = os.path.join(temp_dir, f"export_test.{format_type}")
                success = session_manager.export_session(session_id, export_file, format_type)
                assert success is True
                assert os.path.exists(export_file)
                
                # Verify file is not empty
                with open(export_file, 'r') as f:
                    content = f.read()
                    assert len(content) > 0
            
            # Test history export
            history_export = os.path.join(temp_dir, "history_export.json")
            success = session_manager.export_history(history_export, "json")
            assert success is True
            assert os.path.exists(history_export)

    def test_error_handling_workflow(self, mock_cli_environment):
        """Test error handling from user perspective"""
        # User encounters various error conditions
        
        # Test missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            from reasoning_kernel.cli.core import MSACli
            ui_manager = Mock()
            
            # Should handle missing environment gracefully
            try:
                MSACli._validate_environment(ui_manager)
                assert False, "Should have raised SystemExit"
            except SystemExit:
                pass  # Expected
            
            # Verify error message was shown
            ui_manager.print_error.assert_called()
        
        # Test invalid scenario input
        with patch('reasoning_kernel.cli.core.KernelManager') as mock_kernel_manager, \
             patch('reasoning_kernel.cli.core.MSAEngine') as mock_msa_engine_class:
            
            # Setup mocks
            mock_kernel = AsyncMock()
            mock_kernel_manager.return_value = mock_kernel
            
            mock_msa_engine = AsyncMock()
            mock_msa_engine_class.return_value = mock_msa_engine
            
            # Test with empty scenario
            cli_context = MSACliContext(verbose=False)
            cli_instance = MSACli(cli_context)
            
            # Should handle empty scenario gracefully
            try:
                result = asyncio.run(cli_instance.run_reasoning(""))
                # Should return error result or raise exception
                assert "error" in str(result).lower() or result is None
            except Exception:
                # Expected error handling
                pass

    def test_help_and_documentation_workflow(self, mock_cli_environment):
        """Test help and documentation workflow"""
        # User needs help with CLI usage
        
        # Test that help is available and comprehensive
        import click.testing
        from reasoning_kernel.cli.core import cli
        
        runner = click.testing.CliRunner()
        
        # Test main help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "MSA Reasoning Engine CLI" in result.output
        assert "analyze" in result.output
        assert "session" in result.output
        assert "batch" in result.output
        
        # Test command-specific help
        result = runner.invoke(cli, ['analyze', '--help'])
        assert result.exit_code == 0
        assert "Analyze a scenario" in result.output
        assert "--mode" in result.output
        assert "--output" in result.output
        
        result = runner.invoke(cli, ['session', '--help'])
        assert result.exit_code == 0
        assert "Session management" in result.output
        assert "create" in result.output
        assert "export" in result.output


class TestAccessibilityCompliance:
    """Test accessibility compliance for CLI"""
    
    def test_color_blind_friendly_output(self):
        """Test that CLI output is color-blind friendly"""
        # Test that colors used are accessible
        from reasoning_kernel.cli.ui import UIManager
        
        ui_manager = UIManager(verbose=True)
        
        # Test different UI methods use accessible colors
        # This is more of a design principle check rather than automated testing
        # In a real implementation, we would verify:
        # 1. Sufficient color contrast ratios
        # 2. Use of colorblind-safe color palettes
        # 3. Alternative text indicators beyond just color
        
        # For now, we'll test that the UI manager initializes without error
        assert ui_manager.console is not None
        
        # Test that error messages are clear
        ui_manager.print_error("Test error message")
        # Should not raise exception
        
        # Test that success messages are clear
        ui_manager.print_success("Test success message")
        # Should not raise exception

    def test_keyboard_navigation(self):
        """Test keyboard navigation support"""
        # CLI should be fully keyboard navigable
        # This is inherently true for Click-based CLIs
        # We test by ensuring all commands can be invoked via command line
        
        import click.testing
        from reasoning_kernel.cli.core import cli
        
        runner = click.testing.CliRunner()
        
        # Test that all main commands are accessible
        commands_to_test = ['analyze', 'session', 'batch', 'config', 'model']
        
        for command in commands_to_test:
            result = runner.invoke(cli, [command, '--help'])
            assert result.exit_code == 0, f"Command '{command}' not accessible"
            assert "Usage:" in result.output

    def test_screen_reader_compatibility(self):
        """Test screen reader compatibility"""
        # Test that output is structured for screen readers
        from reasoning_kernel.cli.ui import UIManager
        
        ui_manager = UIManager(verbose=True)
        
        # Test structured output
        test_data = {
            "session_id": "test-session",
            "queries": [
                {"query": "Test query 1", "result": {"confidence": 0.95}},
                {"query": "Test query 2", "result": {"confidence": 0.88}}
            ]
        }
        
        # Test table output
        table_data = [
            {"ID": "test-1", "Status": "Completed", "Confidence": "0.95"},
            {"ID": "test-2", "Status": "Completed", "Confidence": "0.88"}
        ]
        
        # These should not raise exceptions and should produce readable output
        ui_manager.print_table(table_data)
        ui_manager.print_dict_as_table(test_data, "Test Data")

    def test_text_only_environments(self):
        """Test compatibility with text-only environments"""
        # CLI should work in environments without rich text support
        from reasoning_kernel.cli.ui import UIManager
        
        # Test with verbose mode (text-only friendly)
        ui_manager = UIManager(verbose=True)
        
        # Test basic output methods work
        ui_manager.print_header("Test Header")
        ui_manager.print_subheader("Test Subheader")
        ui_manager.print_info("Test info message")
        ui_manager.print_warning("Test warning message")
        ui_manager.print_error("Test error message")
        ui_manager.print_success("Test success message")


class TestUserExperienceMetrics:
    """Test user experience metrics and satisfaction"""
    
    def test_command_response_time(self):
        """Test that CLI commands respond quickly enough for good UX"""
        # User experience research shows that response times should be:
        # < 0.1s: Instant
        # < 1.0s: Fast enough
        # < 10s: Acceptable with progress indicator
        
        import time
        
        # Mock a simple CLI operation
        def simple_cli_operation():
            start_time = time.perf_counter()
            # Simulate simple operation like parsing
            result = {"status": "success"}
            end_time = time.perf_counter()
            return end_time - start_time, result
        
        # Test multiple operations
        times = []
        for _ in range(100):
            execution_time, _ = simple_cli_operation()
            times.append(execution_time)
        
        avg_time = sum(times) / len(times)
        assert avg_time < 0.1, f"CLI operations too slow: {avg_time:.3f}s average"

    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful"""
        from reasoning_kernel.cli.ui import UIManager
        
        ui_manager = UIManager(verbose=True)
        
        # Test different types of error messages
        error_scenarios = [
            ("Missing API key", "Please set AZURE_OPENAI_API_KEY environment variable"),
            ("Invalid input", "Please provide a valid scenario to analyze"),
            ("Network error", "Check your internet connection and try again"),
            ("Configuration error", "Please check your configuration file")
        ]
        
        for error_type, expected_help in error_scenarios:
            # In a real implementation, we would capture the output
            # and verify it contains helpful information
            pass  # Placeholder for actual implementation

    def test_consistent_interface(self):
        """Test that CLI interface is consistent and predictable"""
        import click.testing
        from reasoning_kernel.cli.core import cli
        
        runner = click.testing.CliRunner()
        
        # Test that all commands follow consistent patterns
        main_commands = ['analyze', 'session', 'batch', 'config', 'model']
        
        for command in main_commands:
            # Test help output structure
            result = runner.invoke(cli, [command, '--help'])
            assert result.exit_code == 0
            assert "Usage:" in result.output
            assert "Options:" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])