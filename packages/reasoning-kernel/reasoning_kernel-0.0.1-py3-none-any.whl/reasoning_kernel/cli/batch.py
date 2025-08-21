"""
Batch processing functionality for MSA Reasoning Engine CLI
Provides batch processing capabilities for handling multiple queries
"""
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from reasoning_kernel.cli.ui import UIManager


class BatchProcessor:
    """Handles batch processing of multiple queries"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.ui_manager = UIManager(verbose=verbose)
        self.results = []
        
    def load_queries_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load queries from a JSON or text file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == ".json":
                # Load from JSON file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    # List of queries
                    queries = data
                elif isinstance(data, dict):
                    if "queries" in data:
                        # Object with queries key
                        queries = data["queries"]
                    else:
                        # Single query object
                        queries = [data]
                else:
                    raise ValueError("Invalid JSON structure")
            else:
                # Load from text file (one query per line)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                queries = []
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line:  # Skip empty lines
                        queries.append({
                            "id": f"query-{i+1}",
                            "query": line,
                            "mode": "both"
                        })
            
            self.ui_manager.print_info(f"Loaded {len(queries)} queries from {file_path}")
            return queries
            
        except Exception as e:
            self.ui_manager.print_error(f"Failed to load queries from file: {e}")
            raise
    
    async def process_queries(
        self,
        queries: List[Dict[str, Any]],
        output_dir: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple queries in batch mode"""
        try:
            # Import CLI context and classes locally to avoid circular imports
            from reasoning_kernel.cli.core import MSACliContext, MSACli
            
            # Initialize CLI context
            cli_context = MSACliContext(verbose=self.verbose)
            msa_cli = None
            
            try:
                await cli_context.initialize()
                msa_cli = MSACli(cli_context)
                
                self.ui_manager.print_info(f"Processing {len(queries)} queries in batch mode...")
                
                # Process each query
                for i, query_data in enumerate(queries, 1):
                    try:
                        query_id = query_data.get("id", f"query-{i}")
                        query_text = query_data.get("query", "")
                        mode = query_data.get("mode", "both")
                        
                        if not query_text:
                            self.ui_manager.print_warning(f"Skipping query {i}: Empty query text")
                            continue
                        
                        self.ui_manager.print_info(f"Processing query {i}/{len(queries)}: {query_id}")
                        
                        # Run reasoning with progress indicator
                        task_id = self.ui_manager.start_progress(f"Processing {query_id}...")
                        try:
                            # Update progress during analysis
                            self.ui_manager.update_progress(task_id, 50, "Processing...")
                            
                            # Run reasoning
                            result = await msa_cli.run_reasoning(
                                scenario=query_text,
                                mode=mode,
                                output_format="json",
                                session_id=session_id,
                            )
                            
                            # Complete progress
                            self.ui_manager.update_progress(task_id, 100, "Analysis complete!")
                            
                            # Add query info to result
                            result["query_id"] = query_id
                            result["original_query"] = query_text
                            
                            # Save individual result if output directory specified
                            if output_dir:
                                self._save_individual_result(result, output_dir, query_id)
                            
                            self.results.append(result)
                            
                        finally:
                            self.ui_manager.stop_progress()
                            
                    except Exception as e:
                        self.ui_manager.print_error(f"Failed to process query {query_id}: {e}")
                        if self.verbose:
                            import traceback
                            traceback.print_exc()
                        # Continue with next query
                        continue
                
                self.ui_manager.print_success(f"Batch processing completed. Processed {len(self.results)} queries successfully.")
                
                # Save batch results if output directory specified
                if output_dir and self.results:
                    self._save_batch_results(self.results, output_dir)
                
                return self.results
                
            finally:
                if cli_context:
                    await cli_context.cleanup()
                    
        except Exception as e:
            self.ui_manager.print_error(f"Batch processing failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            raise
    
    def _save_individual_result(self, result: Dict[str, Any], output_dir: str, query_id: str):
        """Save individual result to file"""
        try:
            # Ensure directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save as JSON
            output_file = os.path.join(output_dir, f"{query_id}_result.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str, ensure_ascii=False)
            
            if self.verbose:
                self.ui_manager.print_debug(f"Saved individual result to: {output_file}")
                
        except Exception as e:
            self.ui_manager.print_warning(f"Failed to save individual result for {query_id}: {e}")
    
    def _save_batch_results(self, results: List[Dict[str, Any]], output_dir: str):
        """Save all batch results to file"""
        try:
            # Ensure directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Save as JSON
            output_file = os.path.join(output_dir, "batch_results.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            
            self.ui_manager.print_success(f"Batch results saved to: {output_file}")
                
        except Exception as e:
            self.ui_manager.print_warning(f"Failed to save batch results: {e}")


def validate_batch_file(file_path: str) -> bool:
    """Validate batch input file format"""
    try:
        processor = BatchProcessor()
        queries = processor.load_queries_from_file(file_path)
        
        # Basic validation
        if not queries:
            raise ValueError("No queries found in file")
        
        for i, query in enumerate(queries):
            if not isinstance(query, dict):
                raise ValueError(f"Query {i+1} is not a valid object")
            
            if "query" not in query and "text" not in query:
                raise ValueError(f"Query {i+1} missing required 'query' field")
        
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False