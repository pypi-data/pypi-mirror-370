from supply import PySKU
from supply import PyOperation
from supply import PyResource
from supply import PyLocation
from supply import PyOperation as PyManufacturingProcess
from supply import PyOperation as PySourcingProcess
from supply import PyOperation as PyFulfillmentProcess
from supply import get_all_skus
from supply import levelize_supply_chain
from supply import set_log_level
import json
import os
import shutil


# Copy icons (files with .png extension) to the target directory from the icons directory in the current directory
def install_icons(target_dir):
    """Install the icons for the supply chain network visualization.
    
    Copies all .png files from the 'icons' directory (located in the same directory
    as this script) to the specified target directory.
    
    Args:
        target_dir: Path to the target directory where icons will be copied
    """
    # Create the target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(current_dir, "icons")
    
    # Check if icons directory exists
    if not os.path.exists(icons_dir):
        print(f"Warning: Icons directory not found at {icons_dir}")
        return
    
    # Copy all PNG files from icons directory to target directory
    icons_copied = 0
    for filename in os.listdir(icons_dir):
        if filename.lower().endswith('.png'):
            source_path = os.path.join(icons_dir, filename)
            target_path = os.path.join(target_dir, filename)
            shutil.copy2(source_path, target_path)
            icons_copied += 1
    print(f"Copied {icons_copied} icon files to {target_dir}")


def generate_supply_chain_D3_html(scenario_data_map, output_file="graph.html"):
    """Generate an HTML file with D3.js visualization of the supply chain network.
    
    Args:
        scenario_data_map: Dictionary mapping scenario names to their product@location data
                          Format: {"ScenarioName": {"Product@Location": graph_data, ...}, ...}
        output_file: Path to the output HTML file
        
    Returns:
        Absolute path to the generated HTML file
    """
    # Process the scenario map data
    processed_scenario_map = {}
    for scenario_name, products_data in scenario_data_map.items():
        processed_scenario_map[scenario_name] = {}
        for product_location, sku_data in products_data.items():
            processed_scenario_map[scenario_name][product_location] = prepare_data_for_d3(sku_data)
    
    # Generate the HTML content
    html_content = create_html_content(processed_scenario_map)
    
    # Write the HTML content to a file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"HTML content written to {output_file}")
    
    return os.path.abspath(output_file)

def prepare_data_for_d3(json_data):
    """Convert the JSON data to D3-friendly format with edge color support and icons."""
    
    # Define icon mapping based on node types
    ICON_MAP = {
        "productlocation": "product.png",
        "resource": "resource.png",
        "basicoperation": "operation.png",
        "manufacturing": "operation.png",
        "default": "default.png",
        "distribution": "distribution.png",
    }
    ICONS_PATH = "icons"
    
    nodes = []
    links = []
    
    # Convert nodes with icon support
    for node in json_data.get('nodes', []):
        node_type = str(node.get("node_type", "")).lower()
        if node_type == "basicoperation":
            node_type = node.get("properties", {}).get("category", "operation")

        icon_file = ICON_MAP.get(node_type, ICON_MAP["default"])
        
        d3_node = {
            'id': node['id'],
            'name': node['name'],
            'type': node['node_type'],
            'properties': node.get('properties', {}),
            'iconUrl': f"{ICONS_PATH}/{icon_file}"
        }
        nodes.append(d3_node)
    
    # Convert edges/links with color support
    for edge in json_data.get('edges', []):
        # Get edge color from properties, default to 'default' if not found
        edge_color = edge.get('properties', {}).get('edge_color', 'default')
        
        # Map color names to actual hex colors
        color_map = {
            'black': '#000000',    # Both scenarios
            'blue': '#0066cc',     # First scenario only  
            'green': '#00cc66',    # Second scenario only
            'red': '#cc0000',      # Alternative color
            'default': '#999999'   # Default/unknown
        }
        
        # Use mapped color or default if color not in map
        stroke_color = color_map.get(edge_color, color_map['default'])
        
        d3_link = {
            'source': edge['source_id'],
            'target': edge['target_id'],
            'type': edge['edge_type'],
            'properties': edge.get('properties', {}),
            'color': stroke_color,  # Add color for D3 rendering
            'edge_color': edge_color,  # Keep original color name
            'scenarios': edge.get('properties', {}).get('scenarios', '')
        }
        links.append(d3_link)
    
    return {
        'nodes': nodes,
        'links': links
    }

def create_html_content(scenario_data_map):
    """Generate the HTML content with D3 visualization."""
    
    # Create the HTML structure
    html_content = create_html_structure()
    
    # Insert the scenario map data
    html_content = html_content.replace('{{GRAPH_DATA}}', json.dumps(scenario_data_map))
    
    return html_content

def create_html_structure():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supply Chain Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px;
            text-align: center;
        }
        
        .header h1 {
            margin: 5px 0;
            font-size: 24px;
        }
        
        .header p {
            margin: 0;
            font-size: 14px;
        }
        
        .controls {
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            text-align: left;
        }
        
        .controls label {
            font-weight: bold;
            margin-right: 5px;
            font-size: 14px;
        }
        
        .controls select, .controls input {
            padding: 8px 12px;
            margin: 0 10px 0 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .controls button {
            padding: 8px 16px;
            margin: 0 5px;
            border: 1px solid #007bff;
            background-color: #007bff;
            color: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .controls button:hover {
            background-color: #0056b3;
        }
        
        .legend {
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            font-size: 12px;
        }
        
        .legend-item {
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 5px;
        }
        
        .legend-color {
            display: inline-block;
            width: 20px;
            height: 3px;
            margin-right: 5px;
            vertical-align: middle;
        }
        
        .legend-icon {
            width: 24px;
            height: 24px;
            margin-right: 8px;
            object-fit: contain;
            vertical-align: middle;
        }
        
        #graph-container {
            width: 100%;
            height: 800px;
            position: relative;
            overflow: hidden;
        }
        
        .tooltip {
            position: absolute;
            text-align: left;
            padding: 8px;
            font-size: 12px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            z-index: 1000;
            max-width: 200px;
            word-wrap: break-word;
        }
        
        .node {
            cursor: pointer;
        }
        
        .node image {
            pointer-events: none;
        }
        
        .node text {
            font-size: 10px;
            text-anchor: middle;
            fill: #333;
            pointer-events: none;
        }
        
        .link {
            fill: none;
            stroke-width: 2px;
            stroke-opacity: 0.8;
        }
        
        .link:hover {
            stroke-width: 3px;
            stroke-opacity: 1.0;
        }
        
        .arrow {
            fill: inherit;
        }
        
        .zoom-controls {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 100;
        }
        
        .zoom-controls button {
            display: block;
            width: 30px;
            height: 30px;
            margin-bottom: 5px;
            border: 1px solid #ccc;
            background: white;
            border-radius: 3px;
            cursor: pointer;
            font-size: 16px;
            line-height: 1;
        }
        
        .zoom-controls button:hover {
            background-color: #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sonata - The Supply Chain Network Visualizer</h1>
            <h3>Blue Green Analysis</h3>
        </div>
        
        <div class="controls">
            <label for="scenario-select">Scenario:</label>
            <select id="scenario-select">
                <option value="">Select a scenario...</option>
            </select>
            
            <label for="product-location-input">Product@Location:</label>
            <input type="text" id="product-location-input" placeholder="e.g., Laptop@DC" 
                   style="width: 200px;">
            
            <label for="layout-select">Layout:</label>
            <select id="layout-select">
                <option value="force">Force</option>
                <option value="hierarchical">Hierarchical</option>
            </select>
            
            <button onclick="loadProductLocation()">Load</button>
            <button onclick="resetView()">Reset View</button>
            <button onclick="fitToScreen()">Fit to Screen</button>
            <button onclick="toggleLabels()">Toggle Labels</button>
        </div>
        
        <div class="legend">
            <strong>Edge Colors (Scenario Comparison):</strong>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #000000;"></span>
                Both Scenarios
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #0066cc;"></span>
                First Scenario Only
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #00cc66;"></span>
                Second Scenario Only
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #999999;"></span>
                Default/Single Scenario
            </div>
            <br><br>
            <strong>Node Types:</strong>
            <div class="legend-item">
                <img src="icons/product.png" class="legend-icon" alt="Product Location">
                Product Location
            </div>
            <div class="legend-item">
                <img src="icons/operation.png" class="legend-icon" alt="Operation">
                Operation
            </div>
            <div class="legend-item">
                <img src="icons/distribution.png" class="legend-icon" alt="Distribution">
                Distribution
            </div>
            <div class="legend-item">
                <img src="icons/resource.png" class="legend-icon" alt="Resource">
                Resource
            </div>
        </div>
        
        <div id="graph-container">
            <div class="zoom-controls">
                <button onclick="zoomIn()">+</button>
                <button onclick="zoomOut()">-</button>
            </div>
        </div>
    </div>
    
    <script>
        // Data will be embedded here by Python - Format: {scenario: {product@location: graph_data}}
        const scenarioData = {{GRAPH_DATA}};
        
        // Debug: Log the data to console
        console.log('Scenario data loaded:', scenarioData);
        console.log('Available scenarios:', Object.keys(scenarioData));
        
        // Set up dimensions and margins
        const margin = {top: 20, right: 20, bottom: 20, left: 20};
        const containerElement = document.getElementById('graph-container');
        const width = containerElement.clientWidth - margin.left - margin.right;
        const height = containerElement.clientHeight - margin.top - margin.bottom;
        
        // Create SVG
        const svg = d3.select("#graph-container")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);
        
        // Create main group for zooming/panning
        const g = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        
        // Define arrow markers for different edge colors
        const defs = svg.append("defs");
        
        const colors = ['#000000', '#0066cc', '#00cc66', '#cc0000', '#999999'];
        colors.forEach(color => {
            defs.append("marker")
                .attr("id", "arrow-" + color.substring(1))
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("class", "arrow")
                .attr("d", "M0,-5L10,0L0,5")
                .style("fill", color);
        });
        
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", function(event) {
                g.attr("transform", event.transform);
            });
        
        // Apply zoom to SVG
        svg.call(zoom);
        
        // Create tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        let currentData = null;
        let labelsVisible = true;
        let links, nodes, nodeLabels, simulation;
        let currentLayout = 'force';
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active && currentLayout === 'force') simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active && currentLayout === 'force') simulation.alphaTarget(0);
            if (currentLayout === 'force') {
                d.fx = null;
                d.fy = null;
            }
        }
        
        // Get target node for positioning
        function getTargetNode(data) {
            const targetProductLocation = document.getElementById('product-location-input').value.trim();
            if (!targetProductLocation) return null;
            
            return data.nodes.find(node => node.name === targetProductLocation);
        }
        
        // Position target node to the right
        function positionTargetNode(data) {
            const targetNode = getTargetNode(data);
            if (targetNode) {
                targetNode.fx = width * 0.8; // Position on the right side
                targetNode.fy = height / 2;  // Center vertically
            }
        }
        
        // Initialize the visualization with force layout
        function initForceLayout(data) {
            console.log('Initializing force layout with data:', data);
            
            // Position target node to the right
            positionTargetNode(data);
            
            // Create simulation
            simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links)
                    .id(d => d.id)
                    .distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide(40))
                .on("tick", function() {
                    links
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    nodes.attr("transform", function(d) {
                        return "translate(" + d.x + "," + d.y + ")";
                    });
                });
        }
        
        // Initialize hierarchical layout
        function initHierarchicalLayout(data) {
            console.log('Initializing hierarchical layout with data:', data);
            
            // Stop any existing simulation
            if (simulation) {
                simulation.stop();
            }
            
            // Create hierarchy based on node levels (if available) or node types
            const nodesByLevel = {};
            const targetNode = getTargetNode(data);
            
            data.nodes.forEach(node => {
                // Use level from properties, or assign based on node type and distance from target
                let level = 0;
                if (node.properties && node.properties.level) {
                    level = parseInt(node.properties.level);
                } else {
                    // Assign level based on node type
                    switch (node.type) {
                        case 'ProductLocation':
                            level = node === targetNode ? 0 : 1;
                            break;
                        case 'BasicOperation':
                            level = 2;
                            break;
                        case 'Resource':
                            level = 3;
                            break;
                        default:
                            level = 1;
                    }
                }
                
                if (!nodesByLevel[level]) {
                    nodesByLevel[level] = [];
                }
                nodesByLevel[level].push(node);
            });
            
            // Calculate positions
            const levels = Object.keys(nodesByLevel).map(l => parseInt(l)).sort((a, b) => a - b);
            const levelSpacing = width / (levels.length + 1);
            
            levels.forEach((level, levelIndex) => {
                const nodesInLevel = nodesByLevel[level];
                const nodeSpacing = height / (nodesInLevel.length + 1);
                
                nodesInLevel.forEach((node, nodeIndex) => {
                    // For level 0 (target), position on the right
                    if (level === 0 && node === targetNode) {
                        node.x = width * 0.85;
                        node.y = height / 2;
                    } else {
                        // Position other levels from right to left
                        node.x = width - levelSpacing * (levelIndex + 1);
                        node.y = nodeSpacing * (nodeIndex + 1);
                    }
                    
                    // Fix positions for hierarchical layout
                    node.fx = node.x;
                    node.fy = node.y;
                });
            });
            
            // Update link and node positions
            setTimeout(() => {
                links
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                nodes.attr("transform", function(d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });
            }, 100);
        }
        
        // Initialize the visualization
        function initVisualization(data) {
            console.log('Initializing visualization with data:', data);
            currentData = data;
            currentLayout = document.getElementById('layout-select').value || 'force';
            
            // Clear existing elements
            g.selectAll("*").remove();
            
            // Stop any existing simulation
            if (simulation) {
                simulation.stop();
            }
            
            // Create links with edge color support and arrows
            links = g.append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(data.links)
                .enter().append("line")
                .attr("class", "link")
                .style("stroke", d => d.color || "#999999")
                .style("stroke-width", 2)
                .style("stroke-opacity", 0.8)
                .attr("marker-end", function(d) {
                    const color = d.color || "#999999";
                    return "url(#arrow-" + color.substring(1) + ")";
                })
                .on("mouseover", function(event, d) {
                    d3.select(this)
                        .style("stroke-width", 3)
                        .style("stroke-opacity", 1.0);
                    
                    let tooltipContent = "<strong>" + d.type + "</strong><br/>";
                    if (d.scenarios) {
                        tooltipContent += "Scenarios: " + d.scenarios + "<br/>";
                    }
                    if (d.edge_color && d.edge_color !== 'default') {
                        tooltipContent += "Color: " + d.edge_color + "<br/>";
                    }
                    if (d.properties && d.properties.quantity) {
                        tooltipContent += "Quantity: " + d.properties.quantity;
                    }
                    
                    tooltip.transition().duration(200).style("opacity", .9);
                    tooltip.html(tooltipContent)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                })
                .on("mouseout", function(event, d) {
                    d3.select(this)
                        .style("stroke-width", 2)
                        .style("stroke-opacity", 0.8);
                    
                    tooltip.transition().duration(500).style("opacity", 0);
                });
            
            // Create node groups
            nodes = g.append("g")
                .attr("class", "nodes")
                .selectAll("g")
                .data(data.nodes)
                .enter().append("g")
                .attr("class", "node")
                .style("cursor", "pointer")
                .on("mouseover", function(event, d) {
                    let tooltipContent = "<strong>" + d.name + "</strong><br/>Type: " + d.type;
                    if (d.properties) {
                        Object.entries(d.properties).forEach(function(entry) {
                            const key = entry[0];
                            const value = entry[1];
                            if (key !== 'type') {
                                tooltipContent += "<br/>" + key + ": " + value;
                            }
                        });
                    }
                    
                    tooltip.transition().duration(200).style("opacity", .9);
                    tooltip.html(tooltipContent)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                })
                .on("mouseout", function(event, d) {
                    tooltip.transition().duration(500).style("opacity", 0);
                })
                .on("click", function(event, d) {
                    console.log('Node clicked:', d.name);
                    highlightConnections(d);
                    event.stopPropagation();
                });
            
            // Get target product location for highlighting
            const targetProductLocation = document.getElementById('product-location-input').value.trim();
            
            // Add a background circle to make the node easier to click
            nodes.append("circle")
                .attr("r", 15)
                .style("fill", function(d) {
                    // Subtle blue background for target node
                    return d.name === targetProductLocation ? "rgba(0, 123, 255, 0.15)" : "transparent";
                })
                .style("stroke", function(d) {
                    // Blue border for target node
                    return d.name === targetProductLocation ? "#007bff" : "none";
                })
                .style("stroke-width", function(d) {
                    return d.name === targetProductLocation ? "2px" : "0px";
                })
                .style("pointer-events", "all");
            
            // Add icons to nodes
            nodes.append("image")
                .attr("xlink:href", d => d.iconUrl || "icons/default.png")
                .attr("x", -12)
                .attr("y", -12)
                .attr("width", 24)
                .attr("height", 24)
                .style("pointer-events", "none");
            
            // Add labels to nodes
            nodeLabels = nodes.append("text")
                .attr("dy", 25)
                .text(d => d.name.length > 20 ? d.name.substring(0, 17) + '...' : d.name)
                .style("display", labelsVisible ? "block" : "none")
                .style("pointer-events", "none");
            
            // Apply drag behavior to nodes
            nodes.call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
            
            // Add click handler to SVG background to reset highlighting
            svg.on("click", function(event) {
                if (event.target === this) {
                    console.log('SVG background clicked');
                    resetHighlighting();
                }
            });
            
            // Initialize the appropriate layout
            if (currentLayout === 'hierarchical') {
                initHierarchicalLayout(data);
            } else {
                initForceLayout(data);
            }
        }
        
        // Switch layout function
        function switchLayout() {
            if (!currentData) return;
            
            const newLayout = document.getElementById('layout-select').value;
            if (newLayout === currentLayout) return;
            
            currentLayout = newLayout;
            console.log('Switching to layout:', currentLayout);
            
            if (currentLayout === 'hierarchical') {
                initHierarchicalLayout(currentData);
            } else {
                initForceLayout(currentData);
            }
        }
        
        // Load product location function
        function loadProductLocation() {
            const scenario = document.getElementById('scenario-select').value;
            const productLocation = document.getElementById('product-location-input').value.trim();
            
            if (!scenario) {
                alert('Please select a scenario first.');
                return;
            }
            
            if (!productLocation) {
                alert('Please enter a Product@Location name.');
                return;
            }
            
            // Check if this scenario and product@location exists
            if (scenarioData[scenario] && scenarioData[scenario][productLocation]) {
                console.log('Loading scenario:', scenario, 'for product@location:', productLocation);
                
                // Initialize visualization
                initVisualization(scenarioData[scenario][productLocation]);
            } else {
                const availableProducts = scenarioData[scenario] ? Object.keys(scenarioData[scenario]).join(', ') : 'none';
                alert(`Product@Location "${productLocation}" not found in scenario "${scenario}". Available: ${availableProducts}`);
            }
        }
        
        // Highlight connections function
        function highlightConnections(selectedNode) {
            console.log('Highlighting connections for node:', selectedNode.name);
            
            // Dim all links but keep them visible
            if (links) {
                links.style("opacity", 0.2)
                     .style("stroke-width", 1);
                
                // Highlight connected links
                links.filter(function(link) {
                        const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                        const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                        return sourceId === selectedNode.id || targetId === selectedNode.id;
                    })
                    .style("opacity", 1)
                    .style("stroke-width", 4);
            }
        }
        
        // Reset highlighting function
        function resetHighlighting() {
            console.log('Resetting highlighting');
            if (links) {
                links.style("opacity", 0.8)
                     .style("stroke-width", 2);
            }
        }
        
        // Control functions
        function resetView() {
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }
        
        function fitToScreen() {
            if (!currentData) return;
            
            const bounds = g.node().getBBox();
            const fullWidth = width;
            const fullHeight = height;
            const scale = Math.min(fullWidth / bounds.width, fullHeight / bounds.height) * 0.9;
            const translate = [fullWidth / 2 - scale * (bounds.x + bounds.width / 2), 
                            fullHeight / 2 - scale * (bounds.y + bounds.height / 2)];
            
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
        }
        
        function toggleLabels() {
            labelsVisible = !labelsVisible;
            if (nodeLabels) {
                nodeLabels.style("display", labelsVisible ? "block" : "none");
            }
        }
        
        function zoomIn() {
            svg.transition().call(zoom.scaleBy, 1.5);
        }
        
        function zoomOut() {
            svg.transition().call(zoom.scaleBy, 1 / 1.5);
        }
        
        // Populate scenario selector
        function populateScenarioSelector() {
            console.log('Populating scenario selector');
            const select = document.getElementById('scenario-select');
            
            // Clear existing options except the first one
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            // Add options for each scenario
            Object.keys(scenarioData).forEach(function(scenarioName) {
                console.log('Adding scenario option:', scenarioName);
                const option = document.createElement('option');
                option.value = scenarioName;
                option.textContent = scenarioName;
                select.appendChild(option);
            });
        }
        
        // Add event listener for layout changes
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded, initializing...');
            populateScenarioSelector();
            
            // Add event listener for layout selector
            document.getElementById('layout-select').addEventListener('change', switchLayout);
        });
        
        // Also initialize immediately in case DOMContentLoaded already fired
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                populateScenarioSelector();
                document.getElementById('layout-select').addEventListener('change', switchLayout);
            });
        } else {
            populateScenarioSelector();
            document.getElementById('layout-select').addEventListener('change', switchLayout);
        }
    </script>
</body>
</html>
    """
