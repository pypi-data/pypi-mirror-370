"""
Session management for MSA Reasoning Engine CLI
Provides functionality for tracking, saving, and loading reasoning sessions
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from reasoning_kernel.cli.ui import UIManager

# Add import for export functionality
from reasoning_kernel.cli.export import export_to_json, export_to_markdown, export_to_pdf

# Configure logging
logger = logging.getLogger(__name__)

# Default session directory
DEFAULT_SESSION_DIR = os.path.expanduser("~/.msa/sessions")
DEFAULT_HISTORY_FILE = os.path.expanduser("~/.msa/history.json")


class SessionManager:
    """Manages reasoning sessions and history tracking"""
    
    def __init__(self, session_dir: Optional[str] = None, history_file: Optional[str] = None):
        self.session_dir = session_dir or DEFAULT_SESSION_DIR
        self.history_file = history_file or DEFAULT_HISTORY_FILE
        self.ui_manager = UIManager()
        
        # Create session directory if it doesn't exist
        Path(self.session_dir).mkdir(parents=True, exist_ok=True)
        
        # Create history file if it doesn't exist
        if not os.path.exists(self.history_file):
            self._initialize_history_file()
    
    def _initialize_history_file(self):
        """Initialize the history file with an empty structure"""
        try:
            history_data = {
                "sessions": [],
                "queries": [],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to initialize history file: {e}")
    
    def create_session(self, session_id: str, description: str = "") -> str:
        """Create a new session and return its ID"""
        try:
            # Create session directory
            session_path = os.path.join(self.session_dir, session_id)
            Path(session_path).mkdir(parents=True, exist_ok=True)
            
            # Create session metadata
            session_metadata = {
                "id": session_id,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "queries": [],
                "results": []
            }
            
            # Save session metadata
            metadata_file = os.path.join(session_path, "metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(session_metadata, f, indent=2)
            
            # Add to history
            self._add_session_to_history(session_metadata)
            
            self.ui_manager.print_success(f"Session '{session_id}' created successfully")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions"""
        try:
            sessions = []
            if os.path.exists(self.session_dir):
                for session_id in os.listdir(self.session_dir):
                    session_path = os.path.join(self.session_dir, session_id)
                    if os.path.isdir(session_path):
                        metadata_file = os.path.join(session_path, "metadata.json")
                        if os.path.exists(metadata_file):
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                sessions.append(metadata)
                            except Exception as e:
                                logger.warning(f"Failed to read metadata for session {session_id}: {e}")
                                # Add session without metadata
                                sessions.append({
                                    "id": session_id,
                                    "description": "Metadata unavailable",
                                    "created_at": "Unknown"
                                })
            return sessions
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session by ID"""
        try:
            session_path = os.path.join(self.session_dir, session_id)
            metadata_file = os.path.join(session_path, "metadata.json")
            
            if not os.path.exists(metadata_file):
                self.ui_manager.print_error(f"Session '{session_id}' not found")
                return None
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            self.ui_manager.print_success(f"Session '{session_id}' loaded successfully")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            self.ui_manager.print_error(f"Failed to load session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID"""
        try:
            session_path = os.path.join(self.session_dir, session_id)
            
            if not os.path.exists(session_path):
                self.ui_manager.print_error(f"Session '{session_id}' not found")
                return False
            
            # Remove session directory
            import shutil
            shutil.rmtree(session_path)
            
            # Remove from history
            self._remove_session_from_history(session_id)
            
            self.ui_manager.print_success(f"Session '{session_id}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            self.ui_manager.print_error(f"Failed to delete session: {e}")
            return False
    
    def add_query_to_session(self, session_id: str, query: str, result: Dict[str, Any]) -> bool:
        """Add a query and its result to a session"""
        try:
            session_path = os.path.join(self.session_dir, session_id)
            metadata_file = os.path.join(session_path, "metadata.json")
            
            if not os.path.exists(metadata_file):
                self.ui_manager.print_error(f"Session '{session_id}' not found")
                return False
            
            # Load existing metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Add query and result
            query_entry = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
            metadata["queries"].append(query_entry)
            metadata["results"].append(result)
            
            # Save updated metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Add to history
            self._add_query_to_history(query_entry)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add query to session: {e}")
            return False
    
    def _add_session_to_history(self, session_metadata: Dict[str, Any]):
        """Add a session to the history file"""
        try:
            # Load existing history
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history_data = json.load(f)
            else:
                history_data = {
                    "sessions": [],
                    "queries": [],
                    "last_updated": datetime.now().isoformat()
                }
            
            # Check if session already exists in history
            existing_session = None
            for session in history_data["sessions"]:
                if session["id"] == session_metadata["id"]:
                    existing_session = session
                    break
            
            if existing_session:
                # Update existing session
                existing_session.update(session_metadata)
            else:
                # Add new session
                history_data["sessions"].append(session_metadata)
            
            # Update last_updated timestamp
            history_data["last_updated"] = datetime.now().isoformat()
            
            # Save history
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to add session to history: {e}")
    
    def _remove_session_from_history(self, session_id: str):
        """Remove a session from the history file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history_data = json.load(f)
                
                # Remove session from history
                history_data["sessions"] = [
                    session for session in history_data["sessions"] 
                    if session["id"] != session_id
                ]
                
                # Update last_updated timestamp
                history_data["last_updated"] = datetime.now().isoformat()
                
                # Save history
                with open(self.history_file, 'w') as f:
                    json.dump(history_data, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Failed to remove session from history: {e}")
    
    def _add_query_to_history(self, query_entry: Dict[str, Any]):
        """Add a query to the history file"""
        try:
            # Load existing history
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history_data = json.load(f)
            else:
                history_data = {
                    "sessions": [],
                    "queries": [],
                    "last_updated": datetime.now().isoformat()
                }
            
            # Add query to history
            history_data["queries"].append(query_entry)
            
            # Update last_updated timestamp
            history_data["last_updated"] = datetime.now().isoformat()
            
            # Save history
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to add query to history: {e}")
    
    def search_history(self, query_text: str) -> List[Dict[str, Any]]:
        """Search history for queries containing the given text"""
        try:
            if not os.path.exists(self.history_file):
                return []
            
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            # Search in queries
            matching_queries = []
            for query_entry in history_data.get("queries", []):
                if query_text.lower() in query_entry.get("query", "").lower():
                    matching_queries.append(query_entry)
            
            return matching_queries
            
        except Exception as e:
            logger.error(f"Failed to search history: {e}")
            return []
    
    def get_history(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get the complete history or a limited number of recent entries"""
        try:
            if not os.path.exists(self.history_file):
                return {"sessions": [], "queries": [], "last_updated": datetime.now().isoformat()}
            
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            if limit:
                # Limit the number of queries returned
                history_data["queries"] = history_data.get("queries", [])[-limit:]
            
            return history_data
            
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return {"sessions": [], "queries": [], "last_updated": datetime.now().isoformat()}

    def export_session(self, session_id: str, output_path: str, format_type: str) -> bool:
        """Export a session to specified format"""
        try:
            session_data = self.load_session(session_id)
            if not session_data:
                self.ui_manager.print_error(f"Session '{session_id}' not found")
                return False
            
            # Export based on format
            if format_type == "json":
                return export_to_json(session_data, output_path, self.ui_manager)
            elif format_type == "md":
                return export_to_markdown(session_data, output_path, self.ui_manager)
            elif format_type == "pdf":
                return export_to_pdf(session_data, output_path, self.ui_manager)
            else:
                self.ui_manager.print_error(f"Unsupported export format: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            self.ui_manager.print_error(f"Failed to export session: {e}")
            return False

    def export_history(self, output_path: str, format_type: str, limit: Optional[int] = None) -> bool:
        """Export history to specified format"""
        try:
            history_data = self.get_history(limit)
            
            # Export based on format
            if format_type == "json":
                return export_to_json(history_data, output_path, self.ui_manager)
            elif format_type == "md":
                return export_to_markdown(history_data, output_path, self.ui_manager)
            elif format_type == "pdf":
                return export_to_pdf(history_data, output_path, self.ui_manager)
            else:
                self.ui_manager.print_error(f"Unsupported export format: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            self.ui_manager.print_error(f"Failed to export history: {e}")
            return False


# Global session manager instance
session_manager = SessionManager()