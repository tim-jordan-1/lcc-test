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

def print_tree(intersection_list: list[Intersection]):
    # First, build a dictionary of parent-child relationships
    tree_dict = {}
    root_node = None
    
    # Find the root node (node that only appears as upper_node but never as lower_node)
    all_upper = {i.upper_node.id for i in intersection_list}
    all_lower = {i.lower_node.id for i in intersection_list}
    root_id = list(all_upper - all_lower)[0]
    
    # Build the tree structure
    for intersection in intersection_list:
        parent_id = intersection.upper_node.id
        if parent_id not in tree_dict:
            tree_dict[parent_id] = []
        tree_dict[parent_id].append({
            'node': intersection.lower_node,
            'quadrant': intersection.quadrant_number,
            'link_type': 'Direct' if intersection.link_type == 1 else 'Indirect'
        })
    
    def print_node(node_id, level=0, prefix=""):
        # Find the node object
        node = None
        for intersection in intersection_list:
            if intersection.upper_node.id == node_id:
                node = intersection.upper_node
            elif intersection.lower_node.id == node_id:
                node = intersection.lower_node
            if node:
                break
        
        # Print node information
        indent = "    " * level
        print(f"{indent}{prefix}Node ID: {node.id}")
        print(f"{indent}├── Type: {node.type}")
        print(f"{indent}├── Original Bank Value: {node.original_bank_value}")
        print(f"{indent}├── Original Market Value: {node.original_market_value}")
        print(f"{indent}├── Original Cat Value: {node.original_categorisation_value}")
        print(f"{indent}├── Residual Bank Value: {node.residual_bank_value}")
        print(f"{indent}├── Residual Market Value: {node.residual_market_value}")
        print(f"{indent}└── Residual Cat Value: {node.residual_categorisation_value}")
        
        # Print children
        if node_id in tree_dict:
            for idx, child in enumerate(tree_dict[node_id]):
                print(f"{indent}    |")
                print(f"{indent}    ├── Q{child['quadrant']} ({child['link_type']})")
                print(f"{indent}    |")
                print_node(child['node'].id, level + 1)
    
    # Start printing from root
    print_node(root_id)

print_tree(intersection_list)

