"""
Unit Tests for MSA Reasoning Kernel CLI
======================================

Comprehensive unit tests for all CLI commands and functionality.
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
from reasoning_kernel.cli.export import export_to_json, export_to_markdown


class TestMSACliContext:
    """Test CLI context initialization and management"""

    @pytest.fixture
    def cli_context(self):
        """Create a CLI context for testing"""
        return MSACliContext(verbose=True)

    @pytest.mark.asyncio
    async def test_context_initialization(self, cli_context):
        """Test CLI context initialization"""
        # Test initial state
        assert cli_context.verbose is True
        assert cli_context.kernel_manager is None
        assert cli_context.msa_engine is None
        assert cli_context.session_counter == 0
        assert cli_context.daytona_service is None
        assert cli_context.ppl_executor is None
        assert cli_context.ui_manager is None

    @pytest.mark.asyncio
    async def test_context_initialize_cleanup(self, cli_context):
        """Test CLI context initialization and cleanup"""
        # Mock the initialization process
        with patch('reasoning_kernel.cli.core.KernelManager') as mock_kernel_manager, \
             patch('reasoning_kernel.cli.core.MSAEngine') as mock_msa_engine, \
             patch('reasoning_kernel.cli.core.DaytonaService') as mock_daytona_service, \
             patch('reasoning_kernel.cli.core.DaytonaPPLExecutor') as mock_ppl_executor, \
             patch('reasoning_kernel.cli.core.UIManager') as mock_ui_manager:

            # Setup mocks
            mock_kernel_instance = AsyncMock()
            mock_kernel_manager.return_value = mock_kernel_instance
            
            mock_msa_engine_instance = AsyncMock()
            mock_msa_engine.return_value = mock_msa_engine_instance
            
            mock_daytona_instance = Mock()
            mock_daytona_service.return_value = mock_daytona_instance
            
            mock_ppl_executor_instance = Mock()
            mock_ppl_executor.return_value = mock_ppl_executor_instance
            
            mock_ui_manager_instance = Mock()
            mock_ui_manager.return_value = mock_ui_manager_instance

            # Test initialization
            await cli_context.initialize()
            
            # Verify initialization calls
            mock_kernel_manager.assert_called_once()
            mock_msa_engine.assert_called_once_with(mock_kernel_instance)
            mock_daytona_service.assert_called_once()
            mock_ppl_executor.assert_called_once_with(mock_daytona_instance)
            mock_ui_manager.assert_called_once_with(verbose=True)

            # Test cleanup
            await cli_context.cleanup()
            
            # Verify cleanup calls
            mock_msa_engine_instance.cleanup.assert_called_once()
            mock_kernel_instance.cleanup.assert_called_once()


class TestMSACli:
    """Test CLI command execution and functionality"""

    @pytest.fixture
    def cli_instance(self):
        """Create a CLI instance for testing"""
        context = MSACliContext(verbose=True)
        return MSACli(context)

    def test_validate_environment_missing_keys(self):
        """Test environment validation with missing keys"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('reasoning_kernel.cli.core.UIManager') as mock_ui_manager:
                mock_ui_instance = Mock()
                mock_ui_manager.return_value = mock_ui_instance
                
                # Should exit with missing keys
                with pytest.raises(SystemExit):
                    MSACli._validate_environment(mock_ui_instance)
                
                # Verify error message
                mock_ui_instance.print_error.assert_called()
                mock_ui_instance.console.print.assert_called()

    def test_validate_environment_valid_keys(self):
        """Test environment validation with valid keys"""
        with patch.dict(os.environ, {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "test_endpoint",
            "AZURE_OPENAI_DEPLOYMENT": "test_deployment"
        }, clear=True):
            # Should not raise exception
            result = MSACli._validate_environment()
            assert result is None

    @pytest.mark.asyncio
    async def test_run_reasoning_missing_engine(self, cli_instance):
        """Test run_reasoning with missing engine"""
        cli_instance.context.msa_engine = None
        
        with pytest.raises(RuntimeError, match="MSA Engine not initialized"):
            await cli_instance.run_reasoning("test scenario")

    @pytest.mark.asyncio
    async def test_run_reasoning_knowledge_mode(self, cli_instance):
        """Test run_reasoning in knowledge mode"""
        # Setup mocks
        mock_engine = AsyncMock()
        mock_knowledge_extractor = AsyncMock()
        mock_knowledge_extractor.extract_scenario_knowledge.return_value = {
            "entities": {},
            "relationships": [],
            "causal_factors": []
        }
        
        cli_instance.context.msa_engine = mock_engine
        mock_engine.knowledge_extractor = mock_knowledge_extractor
        
        # Test knowledge mode
        result = await cli_instance.run_reasoning("test scenario", mode="knowledge")
        
        # Verify results
        assert result["mode"] == "knowledge"
        assert result["scenario"] == "test scenario"
        assert "knowledge_extraction" in result
        mock_knowledge_extractor.extract_scenario_knowledge.assert_called_once_with("test scenario")

    @pytest.mark.asyncio
    async def test_run_reasoning_both_mode(self, cli_instance):
        """Test run_reasoning in both mode"""
        # Setup mocks
        mock_engine = AsyncMock()
        mock_engine.knowledge_extractor = None
        mock_engine.reason_about_scenario = AsyncMock(return_value={"test": "result"})
        
        cli_instance.context.msa_engine = mock_engine
        
        # Test both mode
        result = await cli_instance.run_reasoning("test scenario", mode="both")
        
        # Verify results
        assert result["mode"] == "both"
        assert result["scenario"] == "test scenario"
        mock_engine.reason_about_scenario.assert_called_once_with(
            scenario="test scenario", 
            session_id=result["session_id"]
        )

    def test_format_output_json(self, cli_instance):
        """Test JSON output formatting"""
        test_result = {"test": "data", "nested": {"value": 123}}
        
        # Test JSON format
        output = cli_instance.format_output(test_result, "json")
        parsed = json.loads(output)
        assert parsed == test_result

    def test_format_output_text(self, cli_instance):
        """Test text output formatting"""
        test_result = {
            "session_id": "test-session",
            "mode": "both",
            "confidence_analysis": {"overall_confidence": 0.95}
        }
        
        # Test text format
        output = cli_instance.format_output(test_result, "text")
        assert "MSA REASONING ENGINE" in output
        assert "test-session" in output
        assert "0.950" in output


class TestSessionManager:
    """Test session management functionality"""

    @pytest.fixture
    def session_manager(self):
        """Create a session manager for testing"""
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            session_dir = os.path.join(temp_dir, "sessions")
            history_file = os.path.join(temp_dir, "history.json")
            manager = SessionManager(session_dir=session_dir, history_file=history_file)
            yield manager

    def test_session_creation(self, session_manager):
        """Test session creation"""
        session_id = session_manager.create_session("test-session", "Test session description")
        assert session_id == "test-session"
        
        # Verify session exists
        sessions = session_manager.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["id"] == "test-session"

    def test_session_loading(self, session_manager):
        """Test session loading"""
        # Create session first
        session_manager.create_session("test-session", "Test session")
        
        # Load session
        session_data = session_manager.load_session("test-session")
        assert session_data is not None
        assert session_data["id"] == "test-session"

    def test_session_deletion(self, session_manager):
        """Test session deletion"""
        # Create session first
        session_manager.create_session("test-session", "Test session")
        
        # Delete session
        result = session_manager.delete_session("test-session")
        assert result is True
        
        # Verify session is deleted
        sessions = session_manager.list_sessions()
        assert len(sessions) == 0

    def test_add_query_to_session(self, session_manager):
        """Test adding query to session"""
        # Create session first
        session_manager.create_session("test-session", "Test session")
        
        # Add query
        query = "Test query"
        result = {"mode": "both", "confidence": 0.95}
        success = session_manager.add_query_to_session("test-session", query, result)
        assert success is True
        
        # Verify query was added
        session_data = session_manager.load_session("test-session")
        assert len(session_data["queries"]) == 1
        assert session_data["queries"][0]["query"] == query

    def test_history_search(self, session_manager):
        """Test history search functionality"""
        # Create session and add queries
        session_manager.create_session("test-session", "Test session")
        
        query1 = "Climate change impact on agriculture"
        query2 = "Renewable energy benefits"
        result = {"mode": "both", "confidence": 0.95}
        
        session_manager.add_query_to_session("test-session", query1, result)
        session_manager.add_query_to_session("test-session", query2, result)
        
        # Search for climate
        matches = session_manager.search_history("climate")
        assert len(matches) == 1
        assert "climate" in matches[0]["query"].lower()

    def test_export_session_json(self, session_manager):
        """Test session export to JSON"""
        # Create session and add data
        session_manager.create_session("test-session", "Test session")
        query = "Test query"
        result = {"mode": "both", "confidence": 0.95}
        session_manager.add_query_to_session("test-session", query, result)
        
        # Export to JSON
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = session_manager.export_session("test-session", temp_path, "json")
            assert success is True
            
            # Verify file exists and contains data
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                data = json.load(f)
                assert data["id"] == "test-session"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_session_markdown(self, session_manager):
        """Test session export to Markdown"""
        # Create session and add data
        session_manager.create_session("test-session", "Test session")
        query = "Test query"
        result = {"mode": "both", "confidence": 0.95}
        session_manager.add_query_to_session("test-session", query, result)
        
        # Export to Markdown
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = session_manager.export_session("test-session", temp_path, "md")
            assert success is True
            
            # Verify file exists
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "test-session" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestBatchProcessor:
    """Test batch processing functionality"""

    @pytest.fixture
    def batch_processor(self):
        """Create a batch processor for testing"""
        return BatchProcessor(verbose=True)

    def test_load_queries_from_json_list(self, batch_processor):
        """Test loading queries from JSON list format"""
        # Create temporary JSON file
        queries = [
            {"id": "query-1", "query": "Test query 1", "mode": "both"},
            {"id": "query-2", "query": "Test query 2", "mode": "knowledge"}
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode='w', delete=False) as temp_file:
            json.dump(queries, temp_file)
            temp_path = temp_file.name
        
        try:
            loaded_queries = batch_processor.load_queries_from_file(temp_path)
            assert len(loaded_queries) == 2
            assert loaded_queries[0]["id"] == "query-1"
            assert loaded_queries[1]["query"] == "Test query 2"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_queries_from_json_object(self, batch_processor):
        """Test loading queries from JSON object with queries key"""
        # Create temporary JSON file
        data = {
            "queries": [
                {"id": "query-1", "query": "Test query 1", "mode": "both"},
                {"id": "query-2", "query": "Test query 2", "mode": "knowledge"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode='w', delete=False) as temp_file:
            json.dump(data, temp_file)
            temp_path = temp_file.name
        
        try:
            loaded_queries = batch_processor.load_queries_from_file(temp_path)
            assert len(loaded_queries) == 2
            assert loaded_queries[0]["id"] == "query-1"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_queries_from_text_file(self, batch_processor):
        """Test loading queries from text file"""
        # Create temporary text file
        content = """Test query 1
Test query 2
Test query 3"""
        
        with tempfile.NamedTemporaryFile(suffix=".txt", mode='w', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            loaded_queries = batch_processor.load_queries_from_file(temp_path)
            assert len(loaded_queries) == 3
            assert loaded_queries[0]["query"] == "Test query 1"
            assert loaded_queries[1]["query"] == "Test query 2"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_validate_batch_file_valid(self, batch_processor):
        """Test validation of valid batch file"""
        from reasoning_kernel.cli.batch import validate_batch_file
        
        # Create valid JSON file
        queries = [
            {"id": "query-1", "query": "Test query 1", "mode": "both"},
            {"id": "query-2", "query": "Test query 2", "mode": "knowledge"}
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode='w', delete=False) as temp_file:
            json.dump(queries, temp_file)
            temp_path = temp_file.name
        
        try:
            is_valid = validate_batch_file(temp_path)
            assert is_valid is True
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_validate_batch_file_invalid(self, batch_processor):
        """Test validation of invalid batch file"""
        from reasoning_kernel.cli.batch import validate_batch_file
        
        # Create invalid JSON file (missing query field)
        queries = [
            {"id": "query-1"},  # Missing query field
            {"id": "query-2", "query": "Test query 2"}
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".json", mode='w', delete=False) as temp_file:
            json.dump(queries, temp_file)
            temp_path = temp_file.name
        
        try:
            is_valid = validate_batch_file(temp_path)
            assert is_valid is False
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestExportFunctionality:
    """Test export functionality"""

    def test_export_to_json(self):
        """Test export to JSON functionality"""
        # Test data
        data = {
            "session_id": "test-session",
            "queries": [
                {"query": "Test query", "result": {"confidence": 0.95}}
            ]
        }
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch('reasoning_kernel.cli.export.UIManager') as mock_ui_manager:
                mock_ui_instance = Mock()
                mock_ui_manager.return_value = mock_ui_instance
                
                success = export_to_json(data, temp_path, mock_ui_instance)
                assert success is True
                
                # Verify file contents
                with open(temp_path, 'r') as f:
                    loaded_data = json.load(f)
                    assert loaded_data["session_id"] == "test-session"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_to_markdown(self):
        """Test export to Markdown functionality"""
        # Test data
        data = {
            "session_id": "test-session",
            "queries": [
                {"query": "Test query", "result": {"confidence": 0.95}}
            ]
        }
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch('reasoning_kernel.cli.export.UIManager') as mock_ui_manager:
                mock_ui_instance = Mock()
                mock_ui_manager.return_value = mock_ui_instance
                
                success = export_to_markdown(data, temp_path, mock_ui_instance)
                assert success is True
                
                # Verify file exists and contains content
                assert os.path.exists(temp_path)
                with open(temp_path, 'r') as f:
                    content = f.read()
                    assert "test-session" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])