"""
Clean solver implementations using the centralized orchestrator.
"""

from typing import Dict, List, Tuple, Optional
from collections import deque

def orchestrator_solver(env):
    """
    Clean solver implementation using the centralized orchestrator.
    Demonstrates proper use of single source of truth for all operations.
    """
    solution = {'routes': []}
    
    road_network = env.get_road_network_data()
    adjacency_list = road_network['adjacency_list']
    
    order_ids = env.get_all_order_ids()
    available_vehicles = env.get_available_vehicles()
    
    for i, order_id in enumerate(order_ids):
        if i >= len(available_vehicles):
            break
            
        vehicle_id = available_vehicles[i]
        route_data = create_orchestrator_route(env, vehicle_id, order_id, adjacency_list)
        
        if route_data:
            pickup_ops = route_data.get('pickup_operations', [])
            delivery_ops = route_data.get('delivery_operations', [])
            
            is_valid, error_msg = env.validate_single_route(
                vehicle_id, route_data['route'], pickup_ops, delivery_ops
            )
            
            if is_valid:
                solution['routes'].append(route_data)
    
    return solution

def create_orchestrator_route(env, vehicle_id: str, order_id: str, adjacency_list: Dict) -> Optional[Dict]:
    """
    Create a route using orchestrator for feasibility checking.
    Demonstrates proper route planning with centralized state management.
    """
    vehicle = env.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        return None
        
    order_requirements = env.get_order_requirements(order_id)
    if not order_requirements:
        return None
    
    home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
    order_location = env.get_order_location(order_id)
    
    if not home_warehouse or not order_location:
        return None
    
    pickup_operations = []
    total_weight = 0.0
    total_volume = 0.0
    
    for sku_id, required_quantity in order_requirements.items():
        available_warehouses = []
        for wh_id in env.warehouses.keys():
            available_qty = env.orchestrator.get_warehouse_inventory(wh_id, sku_id)
            if available_qty >= required_quantity:
                available_warehouses.append((wh_id, available_qty))
        
        if not available_warehouses:
            return None
        
        chosen_warehouse = None
        if any(wh_id == vehicle.home_warehouse_id for wh_id, _ in available_warehouses):
            chosen_warehouse = vehicle.home_warehouse_id
        else:
            chosen_warehouse = available_warehouses[0][0]
        
        sku_details = env.get_sku_details(sku_id)
        if sku_details:
            item_weight = sku_details['weight'] * required_quantity
            item_volume = sku_details['volume'] * required_quantity
            
            if (total_weight + item_weight > vehicle.capacity_weight or
                total_volume + item_volume > vehicle.capacity_volume):
                return None
            
            total_weight += item_weight
            total_volume += item_volume
        
        pickup_operations.append({
            'warehouse_id': chosen_warehouse,
            'sku_id': sku_id,
            'quantity': required_quantity
        })
    
    delivery_operations = []
    for sku_id, quantity in order_requirements.items():
        delivery_operations.append({
            'order_id': order_id,
            'sku_id': sku_id,
            'quantity': quantity
        })
    
    route_path = create_simple_route_path(home_warehouse, order_location, adjacency_list)
    if not route_path:
        return None
    
    route_distance = env.get_route_distance(route_path)
    
    return {
        'vehicle_id': vehicle_id,
        'route': route_path,
        'distance': route_distance,
        'pickup_operations': pickup_operations,
        'delivery_operations': delivery_operations,
        'order_id': order_id
    }

def create_simple_route_path(home_warehouse: int, order_location: int, adjacency_list: Dict) -> Optional[List[int]]:
    """Create a simple route path: home -> order -> home."""
    path_to_order = find_shortest_path(home_warehouse, order_location, adjacency_list)
    if not path_to_order:
        return None
    
    path_to_home = find_shortest_path(order_location, home_warehouse, adjacency_list)
    if not path_to_home:
        return None
    
    full_route = path_to_order + path_to_home[1:]
    return full_route

def find_shortest_path(start_node: int, end_node: int, adjacency_list: Dict, max_path_length: int = 500) -> Optional[List[int]]:
    """Find shortest path using Breadth-First Search."""
    if start_node == end_node:
        return [start_node]
    
    queue = deque([(start_node, [start_node])])
    visited = {start_node}
    
    while queue:
        current, path = queue.popleft()
        
        if len(path) >= max_path_length:
            continue
            
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                new_path = path + [neighbor_int]
                
                if neighbor_int == end_node:
                    return new_path
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, new_path))
    
    return None

def test_solver(env):
    """Default solver implementation for testing and demonstration."""
    return orchestrator_solver(env)