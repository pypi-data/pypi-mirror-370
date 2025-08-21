"""
Interactive Probability Visualization for Complex Decision Scenarios
===================================================================

This module provides comprehensive probability visualization capabilities including:
- Interactive decision trees with probability distributions
- Monte Carlo simulation visualizations
- Bayesian network representations
- Uncertainty quantification displays
- Real-time probability updates based on user input
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog


logger = structlog.get_logger(__name__)

class VisualizationType(Enum):
    DECISION_TREE = "decision_tree"
    PROBABILITY_DISTRIBUTION = "probability_distribution"
    MONTE_CARLO = "monte_carlo"
    BAYESIAN_NETWORK = "bayesian_network"
    UNCERTAINTY_BANDS = "uncertainty_bands"
    INTERACTIVE_SLIDER = "interactive_slider"

@dataclass
class ProbabilityNode:
    """Node in a probability visualization"""
    id: str
    label: str
    probability: float
    value: Optional[float] = None
    children: Optional[List['ProbabilityNode']] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class DecisionScenario:
    """Complex decision scenario with multiple outcomes"""
    scenario_id: str
    title: str
    description: str
    decision_points: List[Dict[str, Any]]
    outcomes: List[Dict[str, Any]]
    probabilities: Dict[str, float]
    expected_values: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]

@dataclass
class VisualizationConfig:
    """Configuration for probability visualizations"""
    visualization_type: VisualizationType
    width: int = 800
    height: int = 600
    interactive: bool = True
    color_scheme: str = "viridis"
    animation_enabled: bool = True
    show_confidence_intervals: bool = True
    monte_carlo_samples: int = 10000

class InteractiveProbabilityVisualizer:
    """
    Interactive probability visualizer for complex decision scenarios
    """
    
    def __init__(self):
        """Initialize the probability visualizer"""
        self.scenarios: Dict[str, DecisionScenario] = {}
        self.visualizations: Dict[str, Dict[str, Any]] = {}
        logger.info("Interactive probability visualizer initialized")
    
    def create_decision_tree_visualization(self, 
                                         scenario: DecisionScenario,
                                         config: VisualizationConfig) -> Dict[str, Any]:
        """
        Create an interactive decision tree visualization
        
        Args:
            scenario: Decision scenario to visualize
            config: Visualization configuration
            
        Returns:
            Plotly-compatible visualization data
        """
        logger.info("Creating decision tree visualization", scenario_id=scenario.scenario_id)
        
        # Build tree structure
        tree_data = self._build_decision_tree(scenario)
        
        # Create interactive Plotly tree
        visualization = {
            "type": "tree",
            "data": {
                "nodes": tree_data["nodes"],
                "links": tree_data["links"]
            },
            "layout": {
                "title": f"Decision Tree: {scenario.title}",
                "width": config.width,
                "height": config.height,
                "font": {"size": 12},
                "showlegend": True,
                "hovermode": "closest"
            },
            "config": {
                "displayModeBar": True,
                "modeBarButtonsToAdd": ["pan2d", "zoomIn2d", "zoomOut2d"],
                "responsive": True
            },
            "interactivity": {
                "hover_info": "probability+value+outcome",
                "click_actions": ["highlight_path", "show_details"],
                "zoom_enabled": True,
                "pan_enabled": True
            }
        }
        
        return visualization
    
    def create_probability_distribution_visualization(self,
                                                    distributions: Dict[str, List[float]],
                                                    config: VisualizationConfig) -> Dict[str, Any]:
        """
        Create interactive probability distribution visualization
        
        Args:
            distributions: Dictionary of distribution data
            config: Visualization configuration
            
        Returns:
            Plotly-compatible visualization data
        """
        logger.info("Creating probability distribution visualization", 
                   num_distributions=len(distributions))
        
        traces = []
        for name, data in distributions.items():
            # Calculate histogram data
            hist_data, bin_edges = np.histogram(data, bins=50, density=True)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            trace = {
                "type": "scatter",
                "mode": "lines+markers",
                "name": name,
                "x": bin_centers.tolist(),
                "y": hist_data.tolist(),
                "fill": "tonexty" if len(traces) > 0 else "tozeroy",
                "hovertemplate": f"{name}<br>Value: %{{x:.3f}}<br>Probability Density: %{{y:.3f}}<extra></extra>",
                "opacity": 0.7
            }
            traces.append(trace)
        
        # Add confidence intervals if enabled
        if config.show_confidence_intervals:
            for name, data in distributions.items():
                percentiles = np.percentile(data, [2.5, 97.5])
                traces.append({
                    "type": "scatter",
                    "mode": "lines",
                    "name": f"{name} CI",
                    "x": [percentiles[0], percentiles[0], percentiles[1], percentiles[1]],
                    "y": [0, max(np.histogram(data, bins=50, density=True)[0]), 
                          max(np.histogram(data, bins=50, density=True)[0]), 0],
                    "fill": "toself",
                    "fillcolor": "rgba(255,0,0,0.2)",
                    "line": {"color": "rgba(255,0,0,0.8)", "dash": "dash"},
                    "showlegend": False
                })
        
        visualization = {
            "type": "probability_distribution",
            "data": traces,
            "layout": {
                "title": "Interactive Probability Distributions",
                "xaxis": {"title": "Value", "showgrid": True},
                "yaxis": {"title": "Probability Density", "showgrid": True},
                "width": config.width,
                "height": config.height,
                "hovermode": "x unified",
                "legend": {"x": 0.7, "y": 1}
            },
            "interactivity": {
                "crossfilter_enabled": True,
                "brush_selection": True,
                "statistics_panel": True
            }
        }
        
        return visualization
    
    def create_monte_carlo_visualization(self,
                                       simulation_data: Dict[str, Any],
                                       config: VisualizationConfig) -> Dict[str, Any]:
        """
        Create Monte Carlo simulation visualization
        
        Args:
            simulation_data: Monte Carlo simulation results
            config: Visualization configuration
            
        Returns:
            Interactive Monte Carlo visualization
        """
        logger.info("Creating Monte Carlo visualization", 
                   samples=config.monte_carlo_samples)
        
        # Extract simulation results
        outcomes = simulation_data.get("outcomes", [])
        probabilities = simulation_data.get("probabilities", [])
        convergence_data = simulation_data.get("convergence", [])
        
        # Create subplot structure
        visualization = {
            "type": "monte_carlo",
            "data": {
                "scatter_plot": {
                    "type": "scatter",
                    "mode": "markers",
                    "x": list(range(len(outcomes))),
                    "y": outcomes,
                    "marker": {
                        "size": 4,
                        "color": probabilities,
                        "colorscale": config.color_scheme,
                        "showscale": True,
                        "colorbar": {"title": "Probability"}
                    },
                    "name": "Monte Carlo Samples",
                    "hovertemplate": "Sample: %{x}<br>Outcome: %{y:.3f}<br>Probability: %{marker.color:.3f}<extra></extra>"
                },
                "convergence_plot": {
                    "type": "scatter",
                    "mode": "lines",
                    "x": list(range(len(convergence_data))),
                    "y": convergence_data,
                    "name": "Convergence",
                    "line": {"color": "red", "width": 2},
                    "hovertemplate": "Iteration: %{x}<br>Running Average: %{y:.3f}<extra></extra>"
                }
            },
            "layout": {
                "title": "Monte Carlo Simulation Results",
                "width": config.width,
                "height": config.height,
                "showlegend": True,
                "grid": {
                    "rows": 2, "columns": 1,
                    "subplots": [["xy"], ["x2y2"]]
                },
                "xaxis": {"title": "Sample Number"},
                "yaxis": {"title": "Outcome Value"},
                "xaxis2": {"title": "Iteration"},
                "yaxis2": {"title": "Running Average"}
            },
            "interactivity": {
                "animation_frame": "iteration" if config.animation_enabled else None,
                "play_button": config.animation_enabled,
                "slider_control": True,
                "sample_size_control": True
            }
        }
        
        return visualization
    
    def create_bayesian_network_visualization(self,
                                            network_structure: Dict[str, Any],
                                            config: VisualizationConfig) -> Dict[str, Any]:
        """
        Create interactive Bayesian network visualization
        
        Args:
            network_structure: Bayesian network structure and probabilities
            config: Visualization configuration
            
        Returns:
            Interactive network visualization
        """
        logger.info("Creating Bayesian network visualization")
        
        nodes = network_structure.get("nodes", [])
        edges = network_structure.get("edges", [])
        
        # Position nodes using force-directed layout
        node_positions = self._calculate_network_layout(nodes, edges)
        
        # Create network visualization
        visualization = {
            "type": "bayesian_network",
            "data": {
                "nodes": [
                    {
                        "id": node["id"],
                        "label": node["name"],
                        "x": node_positions[node["id"]][0],
                        "y": node_positions[node["id"]][1],
                        "size": node.get("probability", 0.5) * 30 + 10,
                        "color": self._probability_to_color(node.get("probability", 0.5)),
                        "metadata": node.get("metadata", {})
                    }
                    for node in nodes
                ],
                "edges": [
                    {
                        "source": edge["source"],
                        "target": edge["target"],
                        "weight": edge.get("strength", 0.5),
                        "color": self._strength_to_color(edge.get("strength", 0.5)),
                        "type": edge.get("type", "arrow")
                    }
                    for edge in edges
                ]
            },
            "layout": {
                "title": "Interactive Bayesian Network",
                "width": config.width,
                "height": config.height,
                "showlegend": True
            },
            "interactivity": {
                "node_drag": True,
                "edge_highlight": True,
                "probability_update": True,
                "evidence_setting": True,
                "inference_panel": True
            }
        }
        
        return visualization
    
    def create_uncertainty_visualization(self,
                                       uncertainty_data: Dict[str, Any],
                                       config: VisualizationConfig) -> Dict[str, Any]:
        """
        Create uncertainty quantification visualization
        
        Args:
            uncertainty_data: Uncertainty analysis results
            config: Visualization configuration
            
        Returns:
            Interactive uncertainty visualization
        """
        logger.info("Creating uncertainty quantification visualization")
        
        scenarios = uncertainty_data.get("scenarios", [])
        
        traces = []
        for i, scenario in enumerate(scenarios):
            mean_values = scenario.get("mean", [])
            lower_bound = scenario.get("lower_ci", [])
            upper_bound = scenario.get("upper_ci", [])
            x_values = scenario.get("x_values", list(range(len(mean_values))))
            
            # Main line
            traces.append({
                "type": "scatter",
                "mode": "lines+markers",
                "name": scenario.get("name", f"Scenario {i+1}"),
                "x": x_values,
                "y": mean_values,
                "line": {"width": 3},
                "hovertemplate": "%{fullData.name}<br>X: %{x}<br>Mean: %{y:.3f}<extra></extra>"
            })
            
            # Uncertainty bands
            traces.append({
                "type": "scatter",
                "mode": "lines",
                "name": "Upper CI",
                "x": x_values,
                "y": upper_bound,
                "line": {"width": 0},
                "showlegend": False,
                "hoverinfo": "skip"
            })
            
            traces.append({
                "type": "scatter",
                "mode": "lines",
                "name": "Lower CI", 
                "x": x_values,
                "y": lower_bound,
                "fill": "tonexty",
                "fillcolor": f"rgba({50 + i*50}, {100 + i*30}, {200 - i*40}, 0.3)",
                "line": {"width": 0},
                "showlegend": False,
                "hoverinfo": "skip"
            })
        
        visualization = {
            "type": "uncertainty_bands",
            "data": traces,
            "layout": {
                "title": "Uncertainty Quantification",
                "xaxis": {"title": "Parameter Value", "showgrid": True},
                "yaxis": {"title": "Outcome Value", "showgrid": True},
                "width": config.width,
                "height": config.height,
                "hovermode": "x unified"
            },
            "interactivity": {
                "parameter_sliders": True,
                "confidence_level_control": True,
                "scenario_toggle": True
            }
        }
        
        return visualization
    
    def generate_interactive_controls(self, 
                                    scenario: DecisionScenario,
                                    visualization_type: VisualizationType) -> Dict[str, Any]:
        """
        Generate interactive controls for probability visualization
        
        Args:
            scenario: Decision scenario
            visualization_type: Type of visualization
            
        Returns:
            Interactive control configuration
        """
        controls = {
            "sliders": [],
            "dropdowns": [],
            "checkboxes": [],
            "buttons": []
        }
        
        # Add probability sliders for each decision point
        for decision_point in scenario.decision_points:
            controls["sliders"].append({
                "id": f"prob_{decision_point['id']}",
                "label": f"Probability: {decision_point['name']}",
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "value": decision_point.get("probability", 0.5),
                "marks": {0: "0%", 0.5: "50%", 1: "100%"}
            })
        
        # Add outcome value sliders
        for outcome in scenario.outcomes:
            controls["sliders"].append({
                "id": f"value_{outcome['id']}",
                "label": f"Value: {outcome['name']}",
                "min": outcome.get("min_value", -100),
                "max": outcome.get("max_value", 100),
                "step": 1,
                "value": outcome.get("expected_value", 0),
                "marks": {}
            })
        
        # Add visualization type dropdown
        controls["dropdowns"].append({
            "id": "viz_type",
            "label": "Visualization Type",
            "options": [
                {"label": "Decision Tree", "value": "decision_tree"},
                {"label": "Probability Distribution", "value": "probability_distribution"},
                {"label": "Monte Carlo", "value": "monte_carlo"},
                {"label": "Bayesian Network", "value": "bayesian_network"},
                {"label": "Uncertainty Bands", "value": "uncertainty_bands"}
            ],
            "value": visualization_type.value
        })
        
        # Add display options
        controls["checkboxes"].extend([
            {
                "id": "show_confidence",
                "label": "Show Confidence Intervals",
                "checked": True
            },
            {
                "id": "enable_animation",
                "label": "Enable Animations",
                "checked": True
            },
            {
                "id": "show_statistics",
                "label": "Show Statistics Panel",
                "checked": False
            }
        ])
        
        # Add action buttons
        controls["buttons"].extend([
            {
                "id": "reset_view",
                "label": "Reset View",
                "type": "secondary"
            },
            {
                "id": "export_data",
                "label": "Export Data",
                "type": "primary"
            },
            {
                "id": "run_simulation",
                "label": "Run New Simulation",
                "type": "success"
            }
        ])
        
        return controls
    
    def update_visualization(self,
                           visualization_id: str,
                           parameter_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update visualization based on parameter changes
        
        Args:
            visualization_id: ID of visualization to update
            parameter_updates: New parameter values
            
        Returns:
            Updated visualization data
        """
        logger.info("Updating visualization", 
                   visualization_id=visualization_id,
                   num_updates=len(parameter_updates))
        
        if visualization_id not in self.visualizations:
            logger.error("Visualization not found", visualization_id=visualization_id)
            return {}
        
        # Apply parameter updates and recalculate
        updated_data = self._recalculate_visualization(
            self.visualizations[visualization_id],
            parameter_updates
        )
        
        # Update stored visualization
        self.visualizations[visualization_id].update(updated_data)
        
        return updated_data
    
    # Helper methods
    
    def _build_decision_tree(self, scenario: DecisionScenario) -> Dict[str, Any]:
        """Build tree structure from decision scenario"""
        nodes = []
        links = []
        
        # Root node
        root = {
            "id": "root",
            "name": scenario.title,
            "probability": 1.0,
            "value": 0,
            "level": 0
        }
        nodes.append(root)
        
        # Decision nodes
        for i, decision in enumerate(scenario.decision_points):
            node = {
                "id": decision["id"],
                "name": decision["name"],
                "probability": decision.get("probability", 0.5),
                "value": decision.get("value", 0),
                "level": 1,
                "type": "decision"
            }
            nodes.append(node)
            
            links.append({
                "source": "root",
                "target": decision["id"],
                "probability": node["probability"]
            })
        
        # Outcome nodes
        for i, outcome in enumerate(scenario.outcomes):
            node = {
                "id": outcome["id"],
                "name": outcome["name"],
                "probability": outcome.get("probability", 1.0 / len(scenario.outcomes)),
                "value": outcome.get("value", 0),
                "level": 2,
                "type": "outcome"
            }
            nodes.append(node)
            
            # Connect to relevant decision points
            for decision_id in outcome.get("depends_on", []):
                links.append({
                    "source": decision_id,
                    "target": outcome["id"],
                    "probability": node["probability"]
                })
        
        return {"nodes": nodes, "links": links}
    
    def _calculate_network_layout(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Tuple[float, float]]:
        """Calculate force-directed layout for network nodes"""
        # Simple spring-embedder layout
        positions = {}
        num_nodes = len(nodes)
        
        # Initialize random positions
        for i, node in enumerate(nodes):
            angle = 2 * np.pi * i / num_nodes
            radius = 200
            positions[node["id"]] = (
                radius * np.cos(angle),
                radius * np.sin(angle)
            )
        
        # Simple force-directed adjustment (simplified)
        for _ in range(50):  # iterations
            forces = {node_id: [0, 0] for node_id in positions}
            
            # Repulsive forces
            for i, node1_id in enumerate(positions):
                for j, node2_id in enumerate(positions):
                    if i != j:
                        dx = positions[node1_id][0] - positions[node2_id][0]
                        dy = positions[node1_id][1] - positions[node2_id][1]
                        dist = max(np.sqrt(dx*dx + dy*dy), 1)
                        force = 1000 / (dist * dist)
                        forces[node1_id][0] += force * dx / dist
                        forces[node1_id][1] += force * dy / dist
            
            # Attractive forces for connected nodes
            for edge in edges:
                dx = positions[edge["target"]][0] - positions[edge["source"]][0]
                dy = positions[edge["target"]][1] - positions[edge["source"]][1]
                dist = max(np.sqrt(dx*dx + dy*dy), 1)
                force = 0.01 * dist
                forces[edge["source"]][0] += force * dx / dist
                forces[edge["source"]][1] += force * dy / dist
                forces[edge["target"]][0] -= force * dx / dist
                forces[edge["target"]][1] -= force * dy / dist
            
            # Update positions
            for node_id in positions:
                positions[node_id] = (
                    positions[node_id][0] + 0.1 * forces[node_id][0],
                    positions[node_id][1] + 0.1 * forces[node_id][1]
                )
        
        return positions
    
    def _probability_to_color(self, probability: float) -> str:
        """Convert probability to color"""
        # Red to green gradient
        red = int(255 * (1 - probability))
        green = int(255 * probability)
        return f"rgb({red}, {green}, 0)"
    
    def _strength_to_color(self, strength: float) -> str:
        """Convert edge strength to color"""
        alpha = 0.3 + 0.7 * strength
        return f"rgba(0, 0, 255, {alpha})"
    
    def _recalculate_visualization(self, 
                                 current_viz: Dict[str, Any],
                                 updates: Dict[str, Any]) -> Dict[str, Any]:
        """Recalculate visualization data based on parameter updates"""
        # This would contain the logic to update the visualization
        # based on new parameter values
        logger.info("Recalculating visualization with updates", updates=updates)
        
        # Return updated data structure
        return {
            "data_updated": True,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "parameters": updates
        }