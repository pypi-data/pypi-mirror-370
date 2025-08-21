"""
Integration Tests for MSA Reasoning Kernel CLI
============================================

Comprehensive integration tests for CLI with external services.
"""

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
from reasoning_kernel.services.daytona_service import DaytonaService, SandboxConfig
from reasoning_kernel.services.daytona_ppl_executor import DaytonaPPLExecutor


class TestCLIIntegration:
    """Test CLI integration with external services"""

    @pytest.fixture
    def mock_kernel_components(self):
        """Create mock kernel components for testing"""
        # Mock Semantic Kernel
        mock_kernel = AsyncMock()
        mock_kernel.initialize = AsyncMock()
        mock_kernel.cleanup = AsyncMock()
        
        # Mock MSA Engine
        mock_msa_engine = AsyncMock()
        mock_msa_engine.initialize = AsyncMock()
        mock_msa_engine.cleanup = AsyncMock()
        mock_msa_engine.reason_about_scenario = AsyncMock(return_value={
            "mode": "both",
            "confidence_analysis": {"overall_confidence": 0.95}
        })
        
        return mock_kernel, mock_msa_engine

    @pytest.mark.asyncio
    async def test_cli_context_full_initialization(self, mock_kernel_components):
        """Test full CLI context initialization with all services"""
        mock_kernel, mock_msa_engine = mock_kernel_components
        
        # Create CLI context
        cli_context = MSACliContext(verbose=True)
        
        # Mock all service initializations
        with patch('reasoning_kernel.cli.core.KernelManager') as mock_kernel_manager, \
             patch('reasoning_kernel.cli.core.MSAEngine') as mock_msa_engine_class, \
             patch('reasoning_kernel.cli.core.DaytonaService') as mock_daytona_service, \
             patch('reasoning_kernel.cli.core.DaytonaPPLExecutor') as mock_ppl_executor, \
             patch('reasoning_kernel.cli.core.UIManager') as mock_ui_manager:

            # Setup mocks
            mock_kernel_manager.return_value = mock_kernel
            mock_msa_engine_class.return_value = mock_msa_engine
            
            mock_daytona_instance = Mock()
            mock_daytona_instance.is_available.return_value = True
            mock_daytona_service.return_value = mock_daytona_instance
            
            mock_ppl_executor_instance = Mock()
            mock_ppl_executor.return_value = mock_ppl_executor_instance
            
            mock_ui_instance = Mock()
            mock_ui_manager.return_value = mock_ui_instance

            # Test initialization
            await cli_context.initialize()
            
            # Verify all components were initialized
            assert cli_context.kernel_manager == mock_kernel
            assert cli_context.msa_engine == mock_msa_engine
            assert cli_context.daytona_service == mock_daytona_instance
            assert cli_context.ppl_executor == mock_ppl_executor_instance
            assert cli_context.ui_manager == mock_ui_instance
            
            # Verify initialization calls
            mock_kernel.initialize.assert_called_once()
            mock_msa_engine.initialize.assert_called_once()
            mock_daytona_service.assert_called_once()
            mock_ppl_executor.assert_called_once_with(mock_daytona_instance)

    @pytest.mark.asyncio
    async def test_cli_context_cleanup_with_errors(self, mock_kernel_components):
        """Test CLI context cleanup with service errors"""
        mock_kernel, mock_msa_engine = mock_kernel_components
        
        # Create CLI context
        cli_context = MSACliContext(verbose=True)
        cli_context.kernel_manager = mock_kernel
        cli_context.msa_engine = mock_msa_engine
        
        # Mock Daytona service with error
        mock_daytona_service = Mock()
        mock_daytona_service.cleanup_sandbox.side_effect = Exception("Cleanup error")
        cli_context.daytona_service = mock_daytona_service
        
        # Mock UI manager
        mock_ui_manager = Mock()
        cli_context.ui_manager = mock_ui_manager
        
        # Test cleanup - should not raise exception
        await cli_context.cleanup()
        
        # Verify cleanup calls were made
        mock_msa_engine.cleanup.assert_called_once()
        mock_kernel.cleanup.assert_called_once()
        mock_daytona_service.cleanup_sandbox.assert_called_once()
        
        # Verify error was handled gracefully
        mock_ui_manager.print_warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_cli_run_reasoning_with_session_tracking(self, mock_kernel_components):
        """Test CLI reasoning with session tracking"""
        mock_kernel, mock_msa_engine = mock_kernel_components
        
        # Create CLI context and instance
        cli_context = MSACliContext(verbose=True)
        cli_context.msa_engine = mock_msa_engine
        cli_context.ui_manager = Mock()
        
        cli_instance = MSACli(cli_context)
        
        # Mock session manager
        with patch('reasoning_kernel.cli.core.session_manager') as mock_session_manager:
            mock_session_manager.add_query_to_session = Mock(return_value=True)
            
            # Test run reasoning
            result = await cli_instance.run_reasoning("test scenario", session_id="test-session-123")
            
            # Verify session tracking
            mock_session_manager.add_query_to_session.assert_called_once()
            call_args = mock_session_manager.add_query_to_session.call_args
            assert call_args[0][0] == "test-session-123"
            assert call_args[0][1] == "test scenario"

    @pytest.mark.asyncio
    async def test_cli_run_reasoning_visualization(self, mock_kernel_components):
        """Test CLI reasoning with visualization enabled"""
        mock_kernel, mock_msa_engine = mock_kernel_components
        
        # Create CLI context and instance
        cli_context = MSACliContext(verbose=True)
        cli_context.msa_engine = mock_msa_engine
        cli_context.ui_manager = Mock()
        
        # Mock pipeline for visualization
        mock_pipeline = Mock()
        mock_msa_engine.pipeline = mock_pipeline
        
        cli_instance = MSACli(cli_context)
        
        # Mock visualization function
        with patch('reasoning_kernel.cli.core.visualize_pipeline_execution') as mock_visualize:
            mock_visualize.return_value = Mock(final_result={"test": "result"})
            
            # Test run reasoning with visualization
            result = await cli_instance.run_reasoning("test scenario", visualize=True)
            
            # Verify visualization was called
            mock_visualize.assert_called_once()
            assert "test" in result


class TestSessionIntegration:
    """Test session management integration"""

    @pytest.fixture
    def session_manager(self):
        """Create a session manager for testing"""
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            session_dir = os.path.join(temp_dir, "sessions")
            history_file = os.path.join(temp_dir, "history.json")
            manager = SessionManager(session_dir=session_dir, history_file=history_file)
            yield manager

    def test_session_lifecycle_integration(self, session_manager):
        """Test complete session lifecycle integration"""
        session_id = "integration-test-session"
        description = "Integration test session"
        
        # Test session creation
        created_id = session_manager.create_session(session_id, description)
        assert created_id == session_id
        
        # Test session listing
        sessions = session_manager.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["id"] == session_id
        assert sessions[0]["description"] == description
        
        # Test session loading
        loaded_session = session_manager.load_session(session_id)
        assert loaded_session is not None
        assert loaded_session["id"] == session_id
        
        # Test adding queries
        query = "Test integration query"
        result = {"mode": "both", "confidence": 0.92}
        success = session_manager.add_query_to_session(session_id, query, result)
        assert success is True
        
        # Verify query was added
        updated_session = session_manager.load_session(session_id)
        assert len(updated_session["queries"]) == 1
        assert updated_session["queries"][0]["query"] == query
        
        # Test session export
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = session_manager.export_session(session_id, temp_path, "json")
            assert success is True
            assert os.path.exists(temp_path)
            
            # Verify exported data
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
                assert exported_data["id"] == session_id
                assert len(exported_data["queries"]) == 1
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        # Test session deletion
        success = session_manager.delete_session(session_id)
        assert success is True
        
        # Verify session is deleted
        sessions = session_manager.list_sessions()
        assert len(sessions) == 0

    def test_history_integration(self, session_manager):
        """Test history tracking integration"""
        # Add multiple sessions and queries
        session_manager.create_session("session-1", "First session")
        session_manager.create_session("session-2", "Second session")
        
        query1 = "First query in session 1"
        query2 = "Second query in session 1"
        query3 = "Query in session 2"
        
        result = {"mode": "both", "confidence": 0.85}
        
        session_manager.add_query_to_session("session-1", query1, result)
        session_manager.add_query_to_session("session-1", query2, result)
        session_manager.add_query_to_session("session-2", query3, result)
        
        # Test history retrieval
        history = session_manager.get_history()
        assert "queries" in history
        assert len(history["queries"]) == 3
        
        # Test history search
        matches = session_manager.search_history("first")
        assert len(matches) == 1
        assert "First" in matches[0]["query"]
        
        # Test history export
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = session_manager.export_history(temp_path, "json")
            assert success is True
            assert os.path.exists(temp_path)
            
            # Verify exported data
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
                assert "queries" in exported_data
                assert len(exported_data["queries"]) == 3
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestBatchIntegration:
    """Test batch processing integration"""

    @pytest.fixture
    def batch_processor(self):
        """Create a batch processor for testing"""
        return BatchProcessor(verbose=True)

    @pytest.mark.asyncio
    async def test_batch_processing_integration(self, batch_processor):
        """Test complete batch processing integration"""
        # Create test queries
        queries = [
            {"id": "batch-1", "query": "First batch query", "mode": "both"},
            {"id": "batch-2", "query": "Second batch query", "mode": "knowledge"},
            {"id": "batch-3", "query": "Third batch query", "mode": "both"}
        ]
        
        # Mock CLI context and components
        with patch('reasoning_kernel.cli.batch.MSACliContext') as mock_context_class, \
             patch('reasoning_kernel.cli.batch.MSACli') as mock_cli_class:
            
            # Setup mocks
            mock_context = AsyncMock()
            mock_context_class.return_value = mock_context
            
            mock_cli = Mock()
            mock_cli.run_reasoning = AsyncMock(return_value={
                "mode": "both",
                "confidence_analysis": {"overall_confidence": 0.90}
            })
            mock_cli_class.return_value = mock_cli
            
            # Test batch processing
            results = await batch_processor.process_queries(queries)
            
            # Verify results
            assert len(results) == 3
            for result in results:
                assert "query_id" in result
                assert "original_query" in result
                assert "mode" in result
                assert "confidence_analysis" in result

    def test_batch_file_processing_integration(self, batch_processor):
        """Test batch file processing integration"""
        # Create test JSON file
        queries = [
            {"id": "file-1", "query": "File query 1", "mode": "both"},
            {"id": "file-2", "query": "File query 2", "mode": "knowledge"}
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode='w', delete=False) as temp_file:
            json.dump(queries, temp_file)
            temp_path = temp_file.name
        
        try:
            # Test loading from file
            loaded_queries = batch_processor.load_queries_from_file(temp_path)
            assert len(loaded_queries) == 2
            assert loaded_queries[0]["id"] == "file-1"
            assert loaded_queries[1]["query"] == "File query 2"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDaytonaIntegration:
    """Test Daytona service integration"""

    @pytest.fixture
    def daytona_service(self):
        """Create Daytona service for testing"""
        config = SandboxConfig(
            cpu_limit=2,
            memory_limit_mb=512,
            execution_timeout=30
        )
        return DaytonaService(config)

    def test_daytona_service_initialization(self, daytona_service):
        """Test Daytona service initialization"""
        # Verify configuration
        assert daytona_service.config.cpu_limit == 2
        assert daytona_service.config.memory_limit_mb == 512
        assert daytona_service.config.execution_timeout == 30
        
        # Verify default values
        assert daytona_service.daytona_client is None
        assert daytona_service.current_sandbox is None

    @pytest.mark.asyncio
    async def test_daytona_sandbox_lifecycle(self, daytona_service):
        """Test Daytona sandbox lifecycle with mocking"""
        # Mock API-based sandbox creation
        with patch.object(daytona_service, '_create_sandbox_via_api') as mock_create:
            mock_sandbox = {
                "id": "test-sandbox-123",
                "status": "ready",
                "created_at": 1234567890
            }
            mock_create.return_value = mock_sandbox
            
            # Test sandbox creation
            result = await daytona_service.create_sandbox()
            assert result is True
            assert daytona_service.current_sandbox == mock_sandbox
            
            # Test sandbox cleanup
            with patch.object(daytona_service, '_cleanup_sandbox_core') as mock_cleanup:
                result = await daytona_service.cleanup_sandbox()
                assert result is True
                assert daytona_service.current_sandbox is None

    @pytest.mark.asyncio
    async def test_daytona_code_execution(self, daytona_service):
        """Test Daytona code execution with mocking"""
        # Mock local execution fallback
        with patch.object(daytona_service, '_execute_locally_with_timeout') as mock_execute:
            mock_result = Mock()
            mock_result.exit_code = 0
            mock_result.stdout = "Hello, World!"
            mock_result.stderr = ""
            mock_result.execution_time = 0.1
            mock_result.status = "completed"
            mock_execute.return_value = mock_result
            
            # Test code execution
            result = await daytona_service.execute_code("print('Hello, World!')")
            
            # Verify result
            assert result.exit_code == 0
            assert result.stdout == "Hello, World!"
            assert result.status == "completed"

    def test_daytona_service_status(self, daytona_service):
        """Test Daytona service status reporting"""
        status = daytona_service.get_status()
        
        # Verify status structure
        assert "daytona_available" in status
        assert "sandbox_active" in status
        assert "config" in status
        assert "enhanced_features" in status
        
        # Verify enhanced features
        enhanced = status["enhanced_features"]
        assert enhanced["retry_logic"] is True
        assert enhanced["structured_errors"] is True
        assert enhanced["timeout_handling"] is True


class TestPPLExecutorIntegration:
    """Test PPL executor integration"""

    @pytest.fixture
    def ppl_executor(self):
        """Create PPL executor for testing"""
        # Mock Daytona service
        mock_daytona = Mock()
        mock_daytona.execute_code = AsyncMock(return_value=Mock(
            exit_code=0,
            stdout="PPL execution result",
            stderr="",
            execution_time=0.1,
            status="completed"
        ))
        
        return DaytonaPPLExecutor(mock_daytona)

    @pytest.mark.asyncio
    async def test_ppl_execution_integration(self, ppl_executor):
        """Test PPL program execution integration"""
        from reasoning_kernel.services.daytona_ppl_executor import PPLProgram, PPLFramework
        
        # Create test PPL program
        program = PPLProgram(
            code="import numpyro; print('PPL test')",
            framework=PPLFramework.NUMPYRO,
            entry_point="main"
        )
        
        # Test execution
        result = await ppl_executor.execute_ppl_program(program)
        
        # Verify result
        assert result.exit_code == 0
        assert "PPL execution result" in result.stdout
        assert result.status == "completed"
        
        # Verify Daytona service was called
        ppl_executor.daytona_service.execute_code.assert_called_once()

    def test_ppl_program_validation(self, ppl_executor):
        """Test PPL program validation"""
        from reasoning_kernel.services.daytona_ppl_executor import PPLProgram, PPLFramework
        
        # Test valid program
        valid_program = PPLProgram(
            code="valid code",
            framework=PPLFramework.NUMPYRO,
            entry_point="main"
        )
        
        # Should not raise exception
        assert valid_program.code == "valid code"
        assert valid_program.framework == PPLFramework.NUMPYRO
        assert valid_program.entry_point == "main"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])