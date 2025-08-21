/**
 * Interactive Probability Visualization Frontend
 * =============================================
 * 
 * JavaScript module for rendering interactive probability visualizations
 * using Plotly.js and custom controls.
 */

class ProbabilityVisualizer {
    constructor() {
        this.visualizations = new Map();
        this.activeVisualization = null;
        this.plotlyConfig = {
            displayModeBar: true,
            modeBarButtonsToAdd: ['pan2d', 'zoomIn2d', 'zoomOut2d'],
            responsive: true,
            toImageButtonOptions: {
                format: 'png',
                filename: 'probability_visualization',
                height: 600,
                width: 800,
                scale: 1
            }
        };
        
        this.initializeEventHandlers();
    }

    /**
     * Initialize event handlers for interactive controls
     */
    initializeEventHandlers() {
        // Parameter slider changes
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('probability-slider')) {
                this.handleParameterUpdate(e);
            }
        });

        // Visualization type changes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('viz-type-select')) {
                this.handleVisualizationTypeChange(e);
            }
        });

        // Control button clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('viz-control-btn')) {
                this.handleControlButtonClick(e);
            }
        });
    }

    /**
     * Create decision tree visualization
     */
    async createDecisionTree(scenario, config, containerId) {
        try {
            const response = await fetch('/api/v2/probability-visualization/create-decision-tree', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario, config })
            });

            const result = await response.json();
            
            if (result.success) {
                await this.renderDecisionTree(result.visualization, containerId);
                this.createControls(result.controls, `${containerId}-controls`);
                this.visualizations.set(result.visualization_id, {
                    type: 'decision_tree',
                    data: result.visualization,
                    containerId: containerId
                });
                
                return result.visualization_id;
            }
        } catch (error) {
            console.error('Failed to create decision tree:', error);
            throw error;
        }
    }

    /**
     * Create probability distribution visualization
     */
    async createProbabilityDistribution(distributions, config, containerId) {
        try {
            const response = await fetch('/api/v2/probability-visualization/create-probability-distribution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ distributions, config })
            });

            const result = await response.json();
            
            if (result.success) {
                await this.renderProbabilityDistribution(result.visualization, containerId);
                this.visualizations.set(result.visualization_id, {
                    type: 'probability_distribution',
                    data: result.visualization,
                    containerId: containerId
                });
                
                return result.visualization_id;
            }
        } catch (error) {
            console.error('Failed to create probability distribution:', error);
            throw error;
        }
    }

    /**
     * Create Monte Carlo visualization
     */
    async createMonteCarlo(simulationData, config, containerId) {
        try {
            const response = await fetch('/api/v2/probability-visualization/create-monte-carlo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ simulation_data: simulationData, config })
            });

            const result = await response.json();
            
            if (result.success) {
                await this.renderMonteCarlo(result.visualization, containerId);
                this.visualizations.set(result.visualization_id, {
                    type: 'monte_carlo',
                    data: result.visualization,
                    containerId: containerId
                });
                
                return result.visualization_id;
            }
        } catch (error) {
            console.error('Failed to create Monte Carlo visualization:', error);
            throw error;
        }
    }

    /**
     * Create Bayesian network visualization
     */
    async createBayesianNetwork(networkStructure, config, containerId) {
        try {
            const response = await fetch('/api/v2/probability-visualization/create-bayesian-network', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ network_structure: networkStructure, config })
            });

            const result = await response.json();
            
            if (result.success) {
                await this.renderBayesianNetwork(result.visualization, containerId);
                this.visualizations.set(result.visualization_id, {
                    type: 'bayesian_network',
                    data: result.visualization,
                    containerId: containerId
                });
                
                return result.visualization_id;
            }
        } catch (error) {
            console.error('Failed to create Bayesian network:', error);
            throw error;
        }
    }

    /**
     * Create uncertainty bands visualization
     */
    async createUncertaintyBands(uncertaintyData, config, containerId) {
        try {
            const response = await fetch('/api/v2/probability-visualization/create-uncertainty-bands', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uncertainty_data: uncertaintyData, config })
            });

            const result = await response.json();
            
            if (result.success) {
                await this.renderUncertaintyBands(result.visualization, containerId);
                this.visualizations.set(result.visualization_id, {
                    type: 'uncertainty_bands',
                    data: result.visualization,
                    containerId: containerId
                });
                
                return result.visualization_id;
            }
        } catch (error) {
            console.error('Failed to create uncertainty visualization:', error);
            throw error;
        }
    }

    /**
     * Render decision tree using network layout
     */
    async renderDecisionTree(visualizationData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) throw new Error(`Container ${containerId} not found`);

        // Create network graph layout for decision tree
        const nodes = visualizationData.data.nodes;
        const links = visualizationData.data.links;

        // Calculate node positions
        const nodePositions = this.calculateTreeLayout(nodes, links);

        // Create traces for nodes
        const nodeTrace = {
            x: nodes.map(node => nodePositions[node.id]?.x || 0),
            y: nodes.map(node => nodePositions[node.id]?.y || 0),
            mode: 'markers+text',
            marker: {
                size: nodes.map(node => 15 + (node.probability || 0.5) * 20),
                color: nodes.map(node => node.probability || 0.5),
                colorscale: 'Viridis',
                showscale: true,
                colorbar: { title: 'Probability' }
            },
            text: nodes.map(node => node.name),
            textposition: 'middle center',
            hovertemplate: '<b>%{text}</b><br>Probability: %{marker.color:.3f}<br>Value: %{customdata}<extra></extra>',
            customdata: nodes.map(node => node.value || 0),
            type: 'scatter'
        };

        // Create traces for edges
        const edgeTraces = links.map(link => {
            const sourcePos = nodePositions[link.source];
            const targetPos = nodePositions[link.target];
            
            return {
                x: [sourcePos.x, targetPos.x, null],
                y: [sourcePos.y, targetPos.y, null],
                mode: 'lines',
                line: {
                    width: 2,
                    color: `rgba(0,0,255,${0.3 + 0.7 * link.probability})`
                },
                hoverinfo: 'none',
                showlegend: false,
                type: 'scatter'
            };
        });

        const layout = {
            ...visualizationData.layout,
            showlegend: false,
            hovermode: 'closest',
            margin: { t: 50, l: 50, r: 50, b: 50 },
            xaxis: { showgrid: false, zeroline: false, showticklabels: false },
            yaxis: { showgrid: false, zeroline: false, showticklabels: false }
        };

        await Plotly.newPlot(containerId, [nodeTrace, ...edgeTraces], layout, this.plotlyConfig);
    }

    /**
     * Render probability distribution
     */
    async renderProbabilityDistribution(visualizationData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) throw new Error(`Container ${containerId} not found`);

        await Plotly.newPlot(
            containerId, 
            visualizationData.data, 
            visualizationData.layout, 
            this.plotlyConfig
        );

        // Add crossfilter interactivity if enabled
        if (visualizationData.interactivity?.crossfilter_enabled) {
            this.addCrossfilterControls(containerId);
        }
    }

    /**
     * Render Monte Carlo simulation
     */
    async renderMonteCarlo(visualizationData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) throw new Error(`Container ${containerId} not found`);

        // Create subplot layout
        const traces = [
            visualizationData.data.scatter_plot,
            visualizationData.data.convergence_plot
        ];

        const layout = {
            ...visualizationData.layout,
            grid: { rows: 2, columns: 1, pattern: 'independent' }
        };

        await Plotly.newPlot(containerId, traces, layout, this.plotlyConfig);

        // Add animation controls if enabled
        if (visualizationData.interactivity?.animation_frame) {
            this.addAnimationControls(containerId);
        }
    }

    /**
     * Render Bayesian network
     */
    async renderBayesianNetwork(visualizationData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) throw new Error(`Container ${containerId} not found`);

        const nodes = visualizationData.data.nodes;
        const edges = visualizationData.data.edges;

        // Create node trace
        const nodeTrace = {
            x: nodes.map(node => node.x),
            y: nodes.map(node => node.y),
            mode: 'markers+text',
            marker: {
                size: nodes.map(node => node.size),
                color: nodes.map(node => node.color),
                line: { width: 2, color: 'black' }
            },
            text: nodes.map(node => node.label),
            textposition: 'middle center',
            hovertemplate: '<b>%{text}</b><br>Metadata: %{customdata}<extra></extra>',
            customdata: nodes.map(node => JSON.stringify(node.metadata)),
            type: 'scatter'
        };

        // Create edge traces
        const edgeTraces = edges.map(edge => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);
            
            return {
                x: [sourceNode.x, targetNode.x, null],
                y: [sourceNode.y, targetNode.y, null],
                mode: 'lines',
                line: { width: 2, color: edge.color },
                hoverinfo: 'none',
                showlegend: false,
                type: 'scatter'
            };
        });

        const layout = {
            ...visualizationData.layout,
            showlegend: false,
            hovermode: 'closest',
            xaxis: { showgrid: false, zeroline: false, showticklabels: false },
            yaxis: { showgrid: false, zeroline: false, showticklabels: false }
        };

        await Plotly.newPlot(containerId, [nodeTrace, ...edgeTraces], layout, this.plotlyConfig);

        // Add node drag interactivity
        if (visualizationData.interactivity?.node_drag) {
            this.addNodeDragInteractivity(containerId);
        }
    }

    /**
     * Render uncertainty bands
     */
    async renderUncertaintyBands(visualizationData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) throw new Error(`Container ${containerId} not found`);

        await Plotly.newPlot(
            containerId, 
            visualizationData.data, 
            visualizationData.layout, 
            this.plotlyConfig
        );

        // Add parameter sliders if enabled
        if (visualizationData.interactivity?.parameter_sliders) {
            this.addParameterSliders(containerId);
        }
    }

    /**
     * Create interactive controls
     */
    createControls(controlsConfig, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = ''; // Clear existing controls

        const controlsHTML = `
            <div class="probability-controls">
                <div class="controls-section sliders">
                    <h4>Parameters</h4>
                    ${controlsConfig.sliders.map(slider => `
                        <div class="control-item">
                            <label for="${slider.id}">${slider.label}</label>
                            <input type="range" 
                                   id="${slider.id}" 
                                   class="probability-slider"
                                   min="${slider.min}" 
                                   max="${slider.max}" 
                                   step="${slider.step}" 
                                   value="${slider.value}">
                            <span class="slider-value">${slider.value}</span>
                        </div>
                    `).join('')}
                </div>

                <div class="controls-section dropdowns">
                    <h4>Options</h4>
                    ${controlsConfig.dropdowns.map(dropdown => `
                        <div class="control-item">
                            <label for="${dropdown.id}">${dropdown.label}</label>
                            <select id="${dropdown.id}" class="viz-type-select">
                                ${dropdown.options.map(option => `
                                    <option value="${option.value}" ${option.value === dropdown.value ? 'selected' : ''}>
                                        ${option.label}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    `).join('')}
                </div>

                <div class="controls-section checkboxes">
                    <h4>Display Options</h4>
                    ${controlsConfig.checkboxes.map(checkbox => `
                        <div class="control-item">
                            <label>
                                <input type="checkbox" 
                                       id="${checkbox.id}" 
                                       class="viz-checkbox"
                                       ${checkbox.checked ? 'checked' : ''}>
                                ${checkbox.label}
                            </label>
                        </div>
                    `).join('')}
                </div>

                <div class="controls-section buttons">
                    <h4>Actions</h4>
                    ${controlsConfig.buttons.map(button => `
                        <button id="${button.id}" 
                                class="viz-control-btn btn-${button.type}">
                            ${button.label}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;

        container.innerHTML = controlsHTML;

        // Add event handlers for slider value updates
        controlsConfig.sliders.forEach(slider => {
            const sliderElement = document.getElementById(slider.id);
            const valueElement = sliderElement.nextElementSibling;
            
            sliderElement.addEventListener('input', (e) => {
                valueElement.textContent = e.target.value;
            });
        });
    }

    /**
     * Handle parameter updates
     */
    async handleParameterUpdate(event) {
        const parameterId = event.target.id;
        const newValue = parseFloat(event.target.value);
        
        // Find the visualization that owns this parameter
        const visualizationId = this.findVisualizationByParameter(parameterId);
        if (!visualizationId) return;

        try {
            const response = await fetch('/api/v2/probability-visualization/update-visualization', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    visualization_id: visualizationId,
                    parameters: { [parameterId]: newValue }
                })
            });

            const result = await response.json();
            
            if (result.success) {
                await this.refreshVisualization(visualizationId);
            }
        } catch (error) {
            console.error('Failed to update visualization:', error);
        }
    }

    /**
     * Handle visualization type changes
     */
    handleVisualizationTypeChange(event) {
        const newType = event.target.value;
        // Implementation for switching visualization types
        console.log('Visualization type changed to:', newType);
    }

    /**
     * Handle control button clicks
     */
    handleControlButtonClick(event) {
        const buttonId = event.target.id;
        
        switch (buttonId) {
            case 'reset_view':
                this.resetVisualizationView();
                break;
            case 'export_data':
                this.exportVisualizationData();
                break;
            case 'run_simulation':
                this.runNewSimulation();
                break;
            default:
                console.log('Button clicked:', buttonId);
        }
    }

    /**
     * Calculate tree layout positions
     */
    calculateTreeLayout(nodes, links) {
        const positions = {};
        const levels = {};
        
        // Group nodes by level
        nodes.forEach(node => {
            const level = node.level || 0;
            if (!levels[level]) levels[level] = [];
            levels[level].push(node);
        });
        
        // Position nodes
        Object.keys(levels).forEach(level => {
            const levelNodes = levels[level];
            const y = -parseInt(level) * 100;
            
            levelNodes.forEach((node, index) => {
                const totalWidth = (levelNodes.length - 1) * 150;
                const x = -totalWidth/2 + index * 150;
                positions[node.id] = { x, y };
            });
        });
        
        return positions;
    }

    /**
     * Add crossfilter controls
     */
    addCrossfilterControls(containerId) {
        // Implementation for crossfilter controls
        console.log('Adding crossfilter controls to:', containerId);
    }

    /**
     * Add animation controls
     */
    addAnimationControls(containerId) {
        // Implementation for animation controls
        console.log('Adding animation controls to:', containerId);
    }

    /**
     * Add parameter sliders
     */
    addParameterSliders(containerId) {
        // Implementation for dynamic parameter sliders
        console.log('Adding parameter sliders to:', containerId);
    }

    /**
     * Add node drag interactivity
     */
    addNodeDragInteractivity(containerId) {
        // Implementation for node dragging in Bayesian networks
        console.log('Adding node drag interactivity to:', containerId);
    }

    /**
     * Utility methods
     */
    findVisualizationByParameter(parameterId) {
        // Find which visualization owns this parameter
        for (const [vizId, vizData] of this.visualizations) {
            // Logic to match parameter to visualization
            return vizId; // Simplified
        }
        return null;
    }

    async refreshVisualization(visualizationId) {
        const vizData = this.visualizations.get(visualizationId);
        if (!vizData) return;

        // Re-render the visualization with updated data
        const response = await fetch(`/api/v2/probability-visualization/visualization/${visualizationId}`);
        const result = await response.json();
        
        if (result.success) {
            const { type, containerId } = vizData;
            
            switch (type) {
                case 'decision_tree':
                    await this.renderDecisionTree(result.visualization, containerId);
                    break;
                case 'probability_distribution':
                    await this.renderProbabilityDistribution(result.visualization, containerId);
                    break;
                // Add other visualization types
            }
        }
    }

    resetVisualizationView() {
        if (this.activeVisualization) {
            Plotly.relayout(this.activeVisualization.containerId, {
                'xaxis.autorange': true,
                'yaxis.autorange': true
            });
        }
    }

    exportVisualizationData() {
        if (this.activeVisualization) {
            const data = this.activeVisualization.data;
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'visualization_data.json';
            a.click();
            URL.revokeObjectURL(url);
        }
    }

    runNewSimulation() {
        // Implementation for running new simulation
        console.log('Running new simulation...');
    }
}

// Initialize the visualizer when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.probabilityVisualizer = new ProbabilityVisualizer();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProbabilityVisualizer;
}