import json
import networkx as nx
from pyvis.network import Network
jsonPath = "E:/projects/mh/houdini-ai/data/"

def apply_css_override(temp_html="network_temp.html", output_html="network.html"):
    with open(temp_html, "r") as f:
        html_content = f.read()
    
    css_override = """
    <style>
    #config {
        position: absolute !important;
        top: 10px !important;
        right: 10px !important;
    }
    </style>
    """
    
    html_modified = html_content.replace("</head>", css_override + "\n</head>")
    
    with open(output_html, "w") as f:
        f.write(html_modified)

def build_network_from_json(json_filepath):
    """
    Reads a JSON file with node and edge definitions and returns a directed NetworkX graph.
    
    The JSON input is expected to follow the format in graphdata1.json.
    Each node should have: 'name', 'type', 'path', 'inputs', 'outputs'
    and a 'position' as a list [x, y].
    Each edge is a two-element list with source and destination node paths.
    """
    with open(json_filepath, 'r') as f:
        data = json.load(f)
    
    # Build a mapping from node path to node name for establishing edges.
    path_to_name = {node["path"]: node["name"] for node in data.get("nodes", [])}
    
    # Create a directed graph for the node network.
    graph = nx.DiGraph()
    
    # Add nodes with their attributes.
    for node in data.get("nodes", []):
        attr = {
            "type": node["type"],
            "path": node["path"],
            "inputs": node["inputs"],
            "outputs": node["outputs"],
            "position": node.get("position"),  # always a list [x, y]
            "reference": node.get("reference")  # additional attribute for reference
        }
        graph.add_node(node["name"], **attr)
    
    # Add edges using the mapping.
    for edge in data.get("edges", []):
        src_path, dst_path = edge
        src_name = path_to_name.get(src_path, src_path)
        dst_name = path_to_name.get(dst_path, dst_path)
        graph.add_edge(src_name, dst_name)
    
    return graph

# Add a new function that encapsulates all network drawing operations.
def draw_network(graph):
    # Create a pyvis network.
    net = Network(notebook=False, height="1080", width="100%")
    # net.show_buttons(filter_=['physics', 'nodes', 'edges', 'layout'])
    # net.show_buttons(filter_=['physics'])
    net.from_nx(graph)
    
    # Define mapping constants (adjust these values as needed)
    position_scale = 100        # Scale factor from Houdini units to screenspace
    position_offset_x = 1000      # X-axis offset for visualization
    position_offset_y = 500       # Y-axis offset for visualization
    
    for node in net.nodes:
        pos = graph.nodes[node["id"]].get("position")
        if pos and len(pos) >= 2:
            orig_x, orig_y = pos[0], pos[1]
            x = position_offset_x + (orig_x * position_scale)
            y = position_offset_y - (orig_y * position_scale)
            node["x"] = x
            node["y"] = y
            # node["fixed"] = True
        
        # Set the node label and appearance.
        node["label"] = node["id"]
        node["shape"] = "box"
        node["font"] = {
            "size": 20,    # Simulate boldness by increasing font size
            "face": "Arial",
            "color": "#000000"
        }
        node_type = graph.nodes[node["id"]].get("type", "")
        node["title"] = f"Type: {node_type}" if node_type else ""
        node["size"] = 25  # Increase node size for better visibility

    # In draw_network(), after net.from_nx(graph), add the following:
    
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -2000,
          "centralGravity": 0.1,
          "springLength": 10,
          "springConstant": 0.001,
          "damping": 0.9,
          "avoidOverlap":0
        },
        "minVelocity": 0.75,
        "stabilization": {
          "enabled": false,
          "iterations": 1000
        }
      }
    }
    """)
        
    # Save network visualization to a temporary HTML file.
    net.show("network_temp.html", notebook=False)    

def main():
    graph = build_network_from_json(jsonPath + "graph-bmi.json")
    draw_network(graph)
    # Optionally apply CSS override to reposition the buttons.
    # apply_css_override()

# For Houdini, 'main()' is typically called from the Python node's script.
main()