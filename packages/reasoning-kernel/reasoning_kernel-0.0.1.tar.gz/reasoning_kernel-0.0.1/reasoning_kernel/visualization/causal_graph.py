"""
Causal Graph Visualization System
================================

Interactive visual maps of cause-effect relationships with what-if scenario exploration.
"""

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    # Simple fallback implementation
    class SimpleGraph:
        def __init__(self):
            self.nodes = {}
            self.edges = []
        
        def add_node(self, node_id, **attrs):
            self.nodes[node_id] = attrs
        
        def add_edge(self, source, target, **attrs):
            edge_data = {'source': source, 'target': target}
            edge_data.update(attrs)
            self.edges.append(edge_data)
        
        def get_edge_data(self, source, target):
            for edge in self.edges:
                if edge['source'] == source and edge['target'] == target:
                    return edge
            return None
        
        def number_of_nodes(self):
            return len(self.nodes)
        
        def number_of_edges(self):
            return len(self.edges)
    
    nx = type('NetworkX', (), {
        'DiGraph': SimpleGraph,
        'is_directed_acyclic_graph': lambda g: True,
        'strongly_connected_components': lambda g: [list(g.nodes.keys())],
        'weakly_connected_components': lambda g: [list(g.nodes.keys())],
        'betweenness_centrality': lambda g: {node: 0.5 for node in g.nodes},
        'in_degree_centrality': lambda g: {node: 0.5 for node in g.nodes},
        'out_degree_centrality': lambda g: {node: 0.5 for node in g.nodes},
        'descendants': lambda g, node: [],
        'all_simple_paths': lambda g, source, target, cutoff=None: []
    })()
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog


logger = structlog.get_logger(__name__)

@dataclass
class CausalNode:
    """Represents a node in the causal graph"""
    id: str
    label: str
    node_type: str  # 'cause', 'effect', 'mediator', 'confounder'
    confidence: float
    value: Optional[float] = None
    uncertainty: Optional[float] = None
    description: Optional[str] = None
    evidence_strength: float = 0.0

@dataclass
class CausalEdge:
    """Represents a causal relationship between nodes"""
    source: str
    target: str
    strength: float  # Causal strength (-1 to 1)
    confidence: float
    edge_type: str  # 'direct', 'indirect', 'confounded'
    mechanism: Optional[str] = None
    time_lag: Optional[float] = None

@dataclass
class CausalGraph:
    """Complete causal graph structure"""
    nodes: List[CausalNode]
    edges: List[CausalEdge]
    scenario_name: str
    confidence_score: float
    uncertainty_sources: List[str]
    generated_at: str

class CausalGraphGenerator:
    """Generates interactive causal graphs from reasoning results"""
    
    def __init__(self):
        self.nx_graph = None
        
    def create_graph_from_reasoning(self, reasoning_result: Dict[str, Any]) -> CausalGraph:
        """Create causal graph from MSA reasoning output"""
        
        # Extract entities and relationships from reasoning
        entities = self._extract_entities(reasoning_result)
        relationships = self._extract_relationships(reasoning_result)
        
        # Build nodes
        nodes = []
        for entity in entities:
            node = CausalNode(
                id=entity['id'],
                label=entity['name'],
                node_type=entity.get('type', 'unknown'),
                confidence=entity.get('confidence', 0.5),
                value=entity.get('value'),
                uncertainty=entity.get('uncertainty'),
                description=entity.get('description'),
                evidence_strength=entity.get('evidence_strength', 0.0)
            )
            nodes.append(node)
        
        # Build edges
        edges = []
        for rel in relationships:
            edge = CausalEdge(
                source=rel['source'],
                target=rel['target'],
                strength=rel.get('strength', 0.5),
                confidence=rel.get('confidence', 0.5),
                edge_type=rel.get('type', 'direct'),
                mechanism=rel.get('mechanism'),
                time_lag=rel.get('time_lag')
            )
            edges.append(edge)
        
        # Create NetworkX graph for analysis
        self.nx_graph = self._build_networkx_graph(nodes, edges)
        
        graph = CausalGraph(
            nodes=nodes,
            edges=edges,
            scenario_name=reasoning_result.get('scenario', 'Unknown Scenario'),
            confidence_score=reasoning_result.get('confidence', 0.5),
            uncertainty_sources=reasoning_result.get('uncertainty_sources', []),
            generated_at=reasoning_result.get('timestamp', 'unknown')
        )
        
        logger.info("Causal graph generated", 
                   nodes=len(nodes), edges=len(edges), 
                   confidence=graph.confidence_score)
        
        return graph
    
    def _extract_entities(self, reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from reasoning result"""
        entities = []
        
        # Look for entities in different stages
        if 'parsing_result' in reasoning_result:
            parsed = reasoning_result['parsing_result']
            if 'entities' in parsed:
                for entity in parsed['entities']:
                    entities.append({
                        'id': entity.get('name', '').replace(' ', '_').lower(),
                        'name': entity.get('name', 'Unknown'),
                        'type': entity.get('type', 'entity'),
                        'confidence': entity.get('confidence', 0.7),
                        'description': entity.get('description', ''),
                        'evidence_strength': entity.get('importance', 0.5)
                    })
        
        # Extract from graph stage
        if 'graph_result' in reasoning_result:
            graph_data = reasoning_result['graph_result']
            if 'nodes' in graph_data:
                for node in graph_data['nodes']:
                    entities.append({
                        'id': node.get('id', '').replace(' ', '_').lower(),
                        'name': node.get('label', 'Unknown'),
                        'type': node.get('type', 'variable'),
                        'confidence': node.get('confidence', 0.6),
                        'description': node.get('description', ''),
                        'evidence_strength': node.get('centrality', 0.5)
                    })
        
        # Deduplicate entities
        unique_entities = {}
        for entity in entities:
            entity_id = entity['id']
            if entity_id not in unique_entities:
                unique_entities[entity_id] = entity
            else:
                # Merge information
                existing = unique_entities[entity_id]
                existing['confidence'] = max(existing['confidence'], entity['confidence'])
                if not existing['description'] and entity['description']:
                    existing['description'] = entity['description']
        
        return list(unique_entities.values())
    
    def _extract_relationships(self, reasoning_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract causal relationships from reasoning result"""
        relationships = []
        
        # Extract from parsing stage
        if 'parsing_result' in reasoning_result:
            parsed = reasoning_result['parsing_result']
            if 'relationships' in parsed:
                for rel in parsed['relationships']:
                    relationships.append({
                        'source': rel.get('source', '').replace(' ', '_').lower(),
                        'target': rel.get('target', '').replace(' ', '_').lower(),
                        'type': 'direct',
                        'strength': rel.get('strength', 0.5),
                        'confidence': rel.get('confidence', 0.6),
                        'mechanism': rel.get('type', 'causal')
                    })
        
        # Extract from graph stage
        if 'graph_result' in reasoning_result:
            graph_data = reasoning_result['graph_result']
            if 'edges' in graph_data:
                for edge in graph_data['edges']:
                    relationships.append({
                        'source': edge.get('source', '').replace(' ', '_').lower(),
                        'target': edge.get('target', '').replace(' ', '_').lower(),
                        'type': edge.get('type', 'direct'),
                        'strength': edge.get('weight', 0.5),
                        'confidence': edge.get('confidence', 0.6),
                        'mechanism': edge.get('label', 'influences')
                    })
        
        return relationships
    
    def _build_networkx_graph(self, nodes: List[CausalNode], edges: List[CausalEdge]):
        """Build NetworkX graph for analysis"""
        G = nx.DiGraph() if NETWORKX_AVAILABLE else nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            G.add_node(node.id, **asdict(node))
        
        # Add edges
        for edge in edges:
            if edge.source in G.nodes and edge.target in G.nodes:
                G.add_edge(edge.source, edge.target, **asdict(edge))
        
        return G
    
    def analyze_causal_structure(self) -> Dict[str, Any]:
        """Analyze causal graph structure"""
        if not self.nx_graph:
            return {}
        
        analysis = {
            'node_count': self.nx_graph.number_of_nodes(),
            'edge_count': self.nx_graph.number_of_edges(),
            'is_acyclic': nx.is_directed_acyclic_graph(self.nx_graph),
            'strongly_connected_components': len(list(nx.strongly_connected_components(self.nx_graph))),
            'weakly_connected_components': len(list(nx.weakly_connected_components(self.nx_graph)))
        }
        
        # Calculate centrality measures
        try:
            if NETWORKX_AVAILABLE:
                analysis['betweenness_centrality'] = nx.betweenness_centrality(self.nx_graph)
                analysis['in_degree_centrality'] = nx.in_degree_centrality(self.nx_graph)
                analysis['out_degree_centrality'] = nx.out_degree_centrality(self.nx_graph)
            else:
                # Simple fallback centrality measures
                analysis['betweenness_centrality'] = {node: 0.5 for node in self.nx_graph.nodes}
                analysis['in_degree_centrality'] = {node: 0.5 for node in self.nx_graph.nodes}
                analysis['out_degree_centrality'] = {node: 0.5 for node in self.nx_graph.nodes}
        except Exception as e:
            logger.warning(f"Could not calculate centrality measures: {e}")
            analysis['betweenness_centrality'] = {}
            analysis['in_degree_centrality'] = {}
            analysis['out_degree_centrality'] = {}
        
        return analysis
    
    def simulate_intervention(self, node_id: str, new_value: float) -> Dict[str, Any]:
        """Simulate what-if scenario by intervening on a node"""
        if not self.nx_graph or node_id not in self.nx_graph.nodes:
            return {'error': 'Invalid node or graph not initialized'}
        
        # Simple intervention simulation
        affected_nodes = []
        
        # Find all nodes reachable from the intervention node
        try:
            if NETWORKX_AVAILABLE:
                reachable = nx.descendants(self.nx_graph, node_id)
                for target_node in reachable:
                    # Calculate effect based on path strength
                    paths = list(nx.all_simple_paths(self.nx_graph, node_id, target_node, cutoff=3))
                    if paths:
                        # Use strongest path
                        strongest_effect = 0
                        for path in paths:
                            effect = 1.0
                            for i in range(len(path) - 1):
                                edge_data = self.nx_graph.get_edge_data(path[i], path[i+1])
                                if edge_data:
                                    effect *= edge_data.get('strength', 0.5)
                            strongest_effect = max(strongest_effect, abs(effect))
                        
                        affected_nodes.append({
                            'node_id': target_node,
                            'effect_size': strongest_effect * (new_value - 0.5),  # Assuming baseline of 0.5
                            'confidence': min([self.nx_graph.get_edge_data(path[i], path[i+1]).get('confidence', 0.5) 
                                             for path in paths for i in range(len(path)-1)] or [0.5])
                        })
            else:
                # Simple fallback - simulate effect on connected nodes
                for edge in self.nx_graph.edges:
                    if edge['source'] == node_id:
                        affected_nodes.append({
                            'node_id': edge['target'],
                            'effect_size': edge.get('strength', 0.5) * (new_value - 0.5),
                            'confidence': edge.get('confidence', 0.7)
                        })
        except Exception as e:
            logger.error(f"Error in intervention simulation: {e}")
            return {'error': 'An internal error occurred during intervention simulation.'}
        
        return {
            'intervention_node': node_id,
            'intervention_value': new_value,
            'affected_nodes': affected_nodes,
            'total_affected': len(affected_nodes)
        }
    
    def export_for_visualization(self, graph: CausalGraph) -> Dict[str, Any]:
        """Export graph in format suitable for web visualization"""
        
        # Convert to format for D3.js or similar
        vis_data = {
            'nodes': [
                {
                    'id': node.id,
                    'label': node.label,
                    'type': node.node_type,
                    'confidence': node.confidence,
                    'value': node.value or 0.5,
                    'uncertainty': node.uncertainty or 0.1,
                    'description': node.description or '',
                    'evidence_strength': node.evidence_strength,
                    'size': min(50, max(10, node.evidence_strength * 40)),  # Node size based on evidence
                    'color': self._get_node_color(node.node_type, node.confidence)
                }
                for node in graph.nodes
            ],
            'links': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'strength': edge.strength,
                    'confidence': edge.confidence,
                    'type': edge.edge_type,
                    'mechanism': edge.mechanism or '',
                    'width': max(1, abs(edge.strength) * 5),  # Edge width based on strength
                    'color': self._get_edge_color(edge.strength, edge.confidence),
                    'dashArray': '5,5' if edge.confidence < 0.5 else 'none'  # Dashed for low confidence
                }
                for edge in graph.edges
            ],
            'metadata': {
                'scenario_name': graph.scenario_name,
                'confidence_score': graph.confidence_score,
                'uncertainty_sources': graph.uncertainty_sources,
                'generated_at': graph.generated_at,
                'node_count': len(graph.nodes),
                'edge_count': len(graph.edges)
            }
        }
        
        return vis_data
    
    def _get_node_color(self, node_type: str, confidence: float) -> str:
        """Get color for node based on type and confidence"""
        base_colors = {
            'cause': '#ff6b6b',      # Red
            'effect': '#4ecdc4',     # Teal  
            'mediator': '#45b7d1',   # Blue
            'confounder': '#f9ca24', # Yellow
            'variable': '#6c5ce7',   # Purple
            'entity': '#a0a0a0'      # Gray
        }
        
        base_color = base_colors.get(node_type, '#a0a0a0')
        
        # Adjust opacity based on confidence
        opacity = max(0.3, confidence)
        
        # Convert hex to rgba
        hex_color = base_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"
    
    def _get_edge_color(self, strength: float, confidence: float) -> str:
        """Get color for edge based on strength and confidence"""
        if strength > 0:
            # Positive relationship - green
            intensity = int(255 * confidence)
            return f"rgba(46, 204, 113, {confidence})"
        else:
            # Negative relationship - red  
            intensity = int(255 * confidence)
            return f"rgba(231, 76, 60, {confidence})"