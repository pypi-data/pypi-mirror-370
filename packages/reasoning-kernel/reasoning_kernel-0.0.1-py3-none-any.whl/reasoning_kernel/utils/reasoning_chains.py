"""
Reasoning chain tracking and management for transparent AI reasoning
"""

from datetime import datetime
import json
import logging
import time
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ReasoningStep:
    """Individual step in a reasoning chain"""

    def __init__(self, step_id: str, step_type: str, description: str, data: Optional[Dict[str, Any]] = None):
        self.step_id = step_id
        self.step_type = step_type
        self.description = description
        self.timestamp = datetime.now()
        self.data = data or {}
        self.start_time = time.time()
        self.duration_ms = None

    def complete(self, result_data: Optional[Dict[str, Any]] = None):
        """Mark step as complete and record duration"""
        self.duration_ms = (time.time() - self.start_time) * 1000
        if result_data:
            self.data.update(result_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary for serialization"""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "data": self._serialize_data(self.data),
            "duration_ms": self.duration_ms,
        }

    def _serialize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize step data for JSON compatibility"""
        try:
            # Attempt to serialize to ensure JSON compatibility
            json.dumps(data, default=str)
            return data
        except (TypeError, ValueError):
            # If serialization fails, convert to strings
            return {k: str(v) for k, v in data.items()}


class ReasoningChain:
    """
    Tracks the complete reasoning process for transparency and explainability
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"chain_{int(time.time())}"
        self.steps: List[ReasoningStep] = []
        self.start_time = None
        self.end_time = None
        self.total_duration = None
        self.initial_scenario = None
        self.context = None
        self.final_result = None

    def start_reasoning(self, scenario: str, context: Optional[Dict[str, Any]] = None):
        """Initialize the reasoning chain"""
        self.start_time = datetime.now()
        self.initial_scenario = scenario
        self.context = context or {}

        # Add initial step
        init_step = ReasoningStep(
            "initialization",
            "start",
            f"Starting MSA reasoning for scenario: {scenario[:100]}{'...' if len(scenario) > 100 else ''}",
            {"scenario_length": len(scenario), "context_provided": bool(context), "session_id": self.session_id},
        )
        init_step.complete()
        self.steps.append(init_step)

        logger.info(f"Reasoning chain started for session {self.session_id}")

    def add_step(
        self, step_id: str, description: str, data: Optional[Dict[str, Any]] = None, step_type: str = "processing"
    ):
        """Add a new step to the reasoning chain"""
        step = ReasoningStep(step_id, step_type, description, data)
        step.complete(data)  # Mark as complete immediately for now
        self.steps.append(step)

        logger.debug(f"Added reasoning step {step_id}: {description}")

    def add_mode1_step(self, step_id: str, description: str, data: Optional[Dict[str, Any]] = None):
        """Add a Mode 1 (knowledge extraction) step"""
        self.add_step(step_id, description, data, "mode1_knowledge")

    def add_mode2_step(self, step_id: str, description: str, data: Optional[Dict[str, Any]] = None):
        """Add a Mode 2 (probabilistic synthesis) step"""
        self.add_step(step_id, description, data, "mode2_probabilistic")

    def add_integration_step(self, step_id: str, description: str, data: Optional[Dict[str, Any]] = None):
        """Add an integration step"""
        self.add_step(step_id, description, data, "integration")

    def add_error_step(self, step_id: str, error: Exception, description: Optional[str] = None):
        """Add an error step to the chain"""
        error_description = description or f"Error occurred: {str(error)}"
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_details": getattr(error, "args", []),
        }

        self.add_step(step_id, error_description, error_data, "error")
        logger.error(f"Added error step {step_id}: {error_description}")

    def complete_reasoning(self, final_result: Dict[str, Any], processing_time: float):
        """Complete the reasoning chain"""
        self.end_time = datetime.now()
        self.total_duration = processing_time
        self.final_result = final_result

        # Add completion step
        completion_step = ReasoningStep(
            "completion",
            "end",
            f"Reasoning completed successfully in {processing_time:.2f}s",
            {"total_steps": len(self.steps), "processing_time_seconds": processing_time, "success": True},
        )
        completion_step.complete()
        self.steps.append(completion_step)

        logger.info(f"Reasoning chain completed for session {self.session_id} in {processing_time:.2f}s")

    def get_chain(self) -> List[Dict[str, Any]]:
        """Get the complete reasoning chain as serializable data"""
        return [step.to_dict() for step in self.steps]

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the reasoning chain"""
        mode1_steps = len([s for s in self.steps if s.step_type == "mode1_knowledge"])
        mode2_steps = len([s for s in self.steps if s.step_type == "mode2_probabilistic"])
        integration_steps = len([s for s in self.steps if s.step_type == "integration"])
        error_steps = len([s for s in self.steps if s.step_type == "error"])

        total_duration_ms = sum([s.duration_ms for s in self.steps if s.duration_ms is not None])

        return {
            "session_id": self.session_id,
            "total_steps": len(self.steps),
            "mode1_steps": mode1_steps,
            "mode2_steps": mode2_steps,
            "integration_steps": integration_steps,
            "error_steps": error_steps,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_seconds": self.total_duration,
            "steps_duration_ms": total_duration_ms,
            "scenario_preview": (
                self.initial_scenario[:100] + "..."
                if self.initial_scenario and len(self.initial_scenario) > 100
                else self.initial_scenario
            ),
            "has_errors": error_steps > 0,
            "completed": self.end_time is not None,
        }

    def get_step_by_id(self, step_id: str) -> Optional[ReasoningStep]:
        """Get a specific step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_steps_by_type(self, step_type: str) -> List[ReasoningStep]:
        """Get all steps of a specific type"""
        return [step for step in self.steps if step.step_type == step_type]

    def has_errors(self) -> bool:
        """Check if the reasoning chain contains any errors"""
        return any(step.step_type == "error" for step in self.steps)

    def get_last_error(self) -> Optional[ReasoningStep]:
        """Get the most recent error step, if any"""
        error_steps = self.get_steps_by_type("error")
        return error_steps[-1] if error_steps else None

    def export_chain(self) -> Dict[str, Any]:
        """Export the complete reasoning chain with metadata"""
        return {
            "metadata": self.get_summary(),
            "reasoning_steps": self.get_chain(),
            "initial_context": {"scenario": self.initial_scenario, "context": self.context},
            "final_result": self.final_result,
            "export_timestamp": datetime.now().isoformat(),
        }


class ReasoningChainManager:
    """
    Manages multiple reasoning chains for session tracking
    """

    def __init__(self):
        self.active_chains: Dict[str, ReasoningChain] = {}
        self.completed_chains: Dict[str, ReasoningChain] = {}
        self.max_completed_chains = 100  # Limit memory usage

    def create_chain(self, session_id: Optional[str] = None) -> ReasoningChain:
        """Create a new reasoning chain"""
        chain = ReasoningChain(session_id)
        self.active_chains[chain.session_id] = chain
        return chain

    def get_chain(self, session_id: str) -> Optional[ReasoningChain]:
        """Get a reasoning chain by session ID"""
        return self.active_chains.get(session_id) or self.completed_chains.get(session_id)

    def complete_chain(self, session_id: str):
        """Mark a chain as completed and move it to completed chains"""
        if session_id in self.active_chains:
            chain = self.active_chains.pop(session_id)
            self.completed_chains[session_id] = chain

            # Limit memory usage
            if len(self.completed_chains) > self.max_completed_chains:
                # Remove oldest completed chain
                oldest_session = next(iter(self.completed_chains))
                del self.completed_chains[oldest_session]
                logger.debug(f"Removed oldest completed chain: {oldest_session}")

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_chains.keys())

    def get_completed_sessions(self) -> List[str]:
        """Get list of completed session IDs"""
        return list(self.completed_chains.keys())

    def cleanup_old_chains(self, max_age_hours: int = 24):
        """Remove old chains to manage memory"""
        current_time = datetime.now()

        # Clean up old active chains (these might be stuck)
        stale_active = []
        for session_id, chain in self.active_chains.items():
            if chain.start_time and (current_time - chain.start_time).total_seconds() > max_age_hours * 3600:
                stale_active.append(session_id)

        for session_id in stale_active:
            self.complete_chain(session_id)
            logger.warning(f"Moved stale active chain to completed: {session_id}")

        # Clean up old completed chains
        stale_completed = []
        for session_id, chain in self.completed_chains.items():
            if chain.end_time and (current_time - chain.end_time).total_seconds() > max_age_hours * 3600:
                stale_completed.append(session_id)

        for session_id in stale_completed:
            del self.completed_chains[session_id]
            logger.debug(f"Removed old completed chain: {session_id}")


# Global reasoning chain manager
reasoning_chain_manager = ReasoningChainManager()
