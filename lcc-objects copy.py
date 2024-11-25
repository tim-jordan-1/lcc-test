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

def visualize_tree_graphviz(intersection_list, output_file="tree"):
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
    for intersection in intersection_list:
        upper_id = intersection.upper_node.id
        lower_id = intersection.lower_node.id
        
        # Add nodes if they don't exist
        if upper_id not in nodes_set:
            dot.node(upper_id, upper_id)
            nodes_set.add(upper_id)
        if lower_id not in nodes_set:
            dot.node(lower_id, lower_id)
            nodes_set.add(lower_id)
        
        # Add edge with link type
        link_style = 'solid' if intersection.link_type == 1 else 'dashed'
        link_label = 'D' if intersection.link_type == 1 else 'I'
        dot.edge(upper_id, lower_id, label=link_label, style=link_style)
    
    # Render the graph
    try:
        dot.render(output_file, view=True, format='pdf', cleanup=True)
    except Exception as e:
        print(f"Error rendering graph: {e}")
        print("Make sure Graphviz is installed on your system")

visualize_tree(intersection_list)
# visualize_tree_graphviz(intersection_list)


# tree = {
#     -1: {
#         'root': Node(id = 'root',
# type = 'PRODUCT',
# original_bank_value = 544564,
# original_market_value = 30000,
# original_categorisation_value = 45000,
# residual_bank_value = 15000,
# residual_market_value = 30000,
# residual_categorisation_value = 4500 )
#     },
#     0: {
#         '1-2KDVAPB': Node(id = '1-2KDVAPB',
# type = 'CHARGE',
# original_bank_value = 15000,
# original_market_value = 30000,
# original_categorisation_value = 45000,
# residual_bank_value = 15000,
# residual_market_value = 30000,
# residual_categorisation_value = 4500 ),
#         'test': Node(id = 'test',
# type = 'PRODUCT',
# original_bank_value = 4536,
# original_market_value = 45336,
# original_categorisation_value = 45366,
# residual_bank_value = 4536,
# residual_market_value = 45336,
# residual_categorisation_value = 5600 )
#     }
# }