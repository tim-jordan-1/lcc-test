from dataclasses import dataclass
import json
import math
from enum import Enum
from graphviz import Digraph

class LinkType(Enum):
    DIRECT = 1
    INDIRECT = 2
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

@dataclass
class ProductResult:
    product_id: str
    lcc: str
    lbvr1: int
    lbvr2: int
    lmvr1: int
    lmvr2: int
    final_lbvr: int
    final_lmvr: int


@dataclass
class Node:
    id: str
    type: str
    original_bank_value: int
    original_market_value: int
    original_categorisation_value: int
    residual_bank_value: int
    residual_market_value: int
    residual_categorisation_value: int
    
class NodeTree:
    def __init__(self):
        self.tree = dict()
        
    def add_node_at_quadrant(self, node: Node, quadrant: int):
        try:
            self.tree[quadrant][node.id] = node
        except KeyError:
            self.tree[quadrant] = {node.id: node}
    
    def get_node_at_quadrant(self, id: str,quadrant: int):
        node = None
        try:
            node = self.tree[quadrant][id]
        except KeyError:
            raise Exception(f"Node with id {id} not found at quadrant {quadrant}")
        return node
    
    def get_primary_node(self):
        return list(self.tree.get(-1).values())[0]
    
    def get_quadrant_nodes(self, quadrant:int):
        res = []
        if quadrant in self.tree.keys():
            res = list(self.tree.get(quadrant).values())
        return res
    
@dataclass
class Intersection:
    upper_node: Node
    lower_node: Node
    quadrant_number: int
    link_type: int # 1 for direct, 2 for indirect
    number_of_intersections: int
    process_order: int
    priority_table_order: int
    
    
test = {
    "indirect": [1,2,3],
    "direct": [4,5,6]
}

filtered_test = {}
for key in test:
    filtered_test[key] = [x for x in test[key] if x not in [3,4]]
test = filtered_test


intersection_list = [
    Intersection(upper_node=Node(id = '1-2KDVAPB',
type = 'CHARGE',
original_bank_value = 15000,
original_market_value = 30000,
original_categorisation_value = 45000,
residual_bank_value = 15000,
residual_market_value = 30000,
residual_categorisation_value = 4500 
                                 ),
                 lower_node=Node(id = 'test',
type = 'PRODUCT',
original_bank_value = 4536,
original_market_value = 45336,
original_categorisation_value = 45366,
residual_bank_value = 4536,
residual_market_value = 45336,
residual_categorisation_value = 5600 ),
                 quadrant_number = 1,
                 link_type = 2,
                 number_of_intersections = 1,
                 process_order = 1,
                 priority_table_order = 1),
Intersection(upper_node=Node(id = 'root',
type = 'PRODUCT',
original_bank_value = 544564,
original_market_value = 30000,
original_categorisation_value = 45000,
residual_bank_value = 15000,
residual_market_value = 30000,
residual_categorisation_value = 4500 ),
             lower_node=Node(id = '1-2KDVAPB',
type = 'CHARGE',
original_bank_value = 15000,
original_market_value = 30000,
original_categorisation_value = 45000,
residual_bank_value = 15000,
residual_market_value = 30000,
residual_categorisation_value = 4500 ),
             quadrant_number = 1,
             link_type = 1,
             number_of_intersections = 1,
             process_order = 1,
             priority_table_order = 1)
]


def visualize_tree(intersection_list):
    # Create a mapping of nodes and their children
    node_children = {}
    nodes_map = {}  # Map to store node objects
    intersection_map = {}  # Map to store intersection information
    
    # First, find the root node by looking at the first intersection
    root = intersection_list[0].upper_node.id if intersection_list else None
    
    # Process intersections from bottom to top
    for intersection in intersection_list:
        upper_id = intersection.upper_node.id
        lower_id = intersection.lower_node.id
        
        # Store node objects
        nodes_map[upper_id] = intersection.upper_node
        nodes_map[lower_id] = intersection.lower_node
        
        # Store intersection information
        if upper_id not in intersection_map:
            intersection_map[upper_id] = []
        intersection_map[upper_id].append(intersection)
        
        if upper_id not in node_children:
            node_children[upper_id] = []
        node_children[upper_id].append((lower_id, intersection.link_type))

    def print_tree(node_id, prefix="", last=True):
        # Get node object
        node = nodes_map[node_id]
        
        # Format node information
        node_info = (
            f"{node_id}\n"
            f"{prefix}    │  Original Bank Value: {node.original_bank_value}\n"
            f"{prefix}    │  Original Market Value: {node.original_market_value}\n"
            f"{prefix}    │  Original Categorisation Value: {node.original_categorisation_value}\n"
            f"{prefix}    │  Residual Bank Value: {node.residual_bank_value}\n"
            f"{prefix}    │  Residual Market Value: {node.residual_market_value}\n"
            f"{prefix}    │  Residual Categorisation Value: {node.residual_categorisation_value}"
        )
        
        # Add intersection information if available
        if node_id in intersection_map:
            for intersection in intersection_map[node_id]:
                node_info += (
                    f"\n{prefix}    │  Intersection Info:\n"
                    f"{prefix}    │    Quadrant: {intersection.quadrant_number}\n"
                    f"{prefix}    │    Link Type: {intersection.link_type}\n"
                    f"{prefix}    │    Number of Intersections: {intersection.number_of_intersections}\n"
                    f"{prefix}    │    Process Order: {intersection.process_order}\n"
                    f"{prefix}    │    Priority Table Order: {intersection.priority_table_order}"
                )
        
        # Print current node
        connector = "└── " if last else "├── "
        print(f"{prefix}{connector}{node_info}")
        
        if node_id in node_children:
            children = node_children[node_id]
            for i, (child, link_type) in enumerate(children):
                is_last = i == len(children) - 1
                new_prefix = prefix + ("    " if last else "│   ")
                # Add link type indicator
                link_indicator = "(D)" if link_type == 1 else "(I)"
                print(f"{new_prefix}│  {link_indicator}")
                print_tree(child, new_prefix, is_last)

    if root:
        print_tree(root)

def visualize_tree_graphviz(intersection_list, output_file="treetest"):
    """
    Creates a visual representation of the tree using Graphviz.
    Args:
        intersection_list: List of Intersection objects
        output_file: Name of the output file (without extension)
    """
    # Create a new directed graph
    dot = Digraph(comment='Tree Visualization')
    dot.attr(rankdir='TB')  # Top to bottom direction
    
    # Process intersections to build the tree
    nodes_set = set()
    
    # Add all nodes first
    for index, intersection in enumerate(intersection_list):  # Use enumerate to get the index
        upper_node = intersection.upper_node
        lower_node = intersection.lower_node
        
        # Add upper node with detailed information
        upper_label = (
            f"{upper_node.id}\\n"
            f"Original Bank Value: {upper_node.original_bank_value}\\n"
            f"Original Market Value: {upper_node.original_market_value}\\n"
            f"Original Categorisation Value: {upper_node.original_categorisation_value}\\n"
            f"Residual Bank Value: {upper_node.residual_bank_value}\\n"
            f"Residual Market Value: {upper_node.residual_market_value}\\n"
            f"Residual Categorisation Value: {upper_node.residual_categorisation_value}"
        )
        if upper_node.id not in nodes_set:
            dot.node(upper_node.id, upper_label)
            nodes_set.add(upper_node.id)
        
        # Add lower node with detailed information
        lower_label = (
            f"{lower_node.id}\\n"
            f"Original Bank Value: {lower_node.original_bank_value}\\n"
            f"Original Market Value: {lower_node.original_market_value}\\n"
            f"Original Categorisation Value: {lower_node.original_categorisation_value}\\n"
            f"Residual Bank Value: {lower_node.residual_bank_value}\\n"
            f"Residual Market Value: {lower_node.residual_market_value}\\n"
            f"Residual Categorisation Value: {lower_node.residual_categorisation_value}"
        )
        if lower_node.id not in nodes_set:
            print(lower_node.id)
            print(lower_node.id, lower_label)
            dot.node(lower_node.id, lower_label)
            nodes_set.add(lower_node.id)
        
        # Add edge with link type and index as order
        link_style = 'solid' if intersection.link_type == 1 else 'dashed'
        link_label = f"{'D' if intersection.link_type == 1 else 'I'} (Index: {index})"  # Use index instead of process order
        dot.edge(upper_node.id, lower_node.id, label=link_label, style=link_style)
    
    # Render the graph
    try:
        dot.render(output_file, view=True, format='pdf', cleanup=True)
    except Exception as e:
        print(f"Error rendering graph: {e}")
        print("Make sure Graphviz is installed on your system")

def visualize_tree_from_json(json_data, output_file="tree_from_json"):
    """
    Creates a visual representation of the tree using Graphviz from quadrants.json format.
    Args:
        json_data: Dictionary containing quadrant information
        output_file: Name of the output file (without extension)
    """
    # Create a new directed graph
    dot = Digraph(comment='Tree Visualization')
    dot.attr(rankdir='TB')  # Top to bottom direction
    
    # Track added nodes to avoid duplicates
    nodes_set = set()
    
    # Helper function to create node label
    def create_node_label(node):
        return (
            f"{node['id']}\\n"
            f"Type: {node['type']}\\n"
            f"Original Bank Value: {node['originalBankValue']}\\n"
            f"Original Market Value: {node['originalMarketValue']}\\n"
            f"Original Categorisation Value: {node['originalCategoorisationValue']}\\n"
            f"Residual Bank Value: {node['residualBankValue']}\\n"
            f"Residual Market Value: {node['residualMarketValue']}\\n"
            f"Residual Categorisation Value: {node['residualCategorisationValue']}\\n"
            f"Pre Q1 Residual Bank Value: {node['preQ1ResidualBankValue']}\\n"
            f"Pre Q1 Residual Market Value: {node['preQ1ResidualMarketValue']}"
        )
    
    # First, add all nodes from each quadrant
    for quadrant_key, quadrant_data in json_data.items():
        for node in quadrant_data['nodes']:
            if node['id'] not in nodes_set:
                dot.node(node['id'], create_node_label(node))
                nodes_set.add(node['id'])
    
    # Then add all edges from prioritised links
    for quadrant_key, quadrant_data in json_data.items():
        for index, link in enumerate(quadrant_data.get('prioritisedLinks', [])):
            node1 = link['node1']  # child node
            node2 = link['node2']  # parent node
            
            # Add nodes if they haven't been added yet
            for node in [node1, node2]:
                if node['id'] not in nodes_set:
                    dot.node(node['id'], create_node_label(node))
                    nodes_set.add(node['id'])
            
            # Add edge with link type and index
            link_style = 'solid' if link['linkType'] == 'DIRECT' else 'dashed'
            link_label = f"{'D' if link['linkType'] == 'DIRECT' else 'I'} (Order: {index})"
            dot.edge(node2['id'], node1['id'], label=link_label, style=link_style)
    
    # Render the graph
    try:
        dot.render(output_file, view=True, format='pdf', cleanup=True)
    except Exception as e:
        print(f"Error rendering graph: {e}")
        print("Make sure Graphviz is installed on your system")

with open('quadrants.json', 'r') as f:
    quadrants_data = json.load(f)
    
visualize_tree_from_json(quadrants_data)
