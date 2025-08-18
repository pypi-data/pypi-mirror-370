"""
Mock solvers that generate different types of solutions for testing environment validation.
These solvers test various edge cases and validation scenarios.
"""

def valid_mock_solver(env):
    """
    Generates a valid solution for testing environment validation.
    Uses simple but correct logic.
    """
    solution = {'routes': []}
    
    order_ids = env.get_all_order_ids()
    vehicle_ids = env.get_available_vehicles()
    road_network = env.get_road_network_data()
    adjacency_list = road_network['adjacency_list']
    
    # Simple assignment: one order per vehicle
    for i, order_id in enumerate(order_ids[:len(vehicle_ids)]):
        vehicle_id = vehicle_ids[i]
        order_location = env.get_order_location(order_id)
        home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
        
        # Create simple round trip
        route = create_simple_path(home_warehouse, order_location, adjacency_list)
        
        if route:
            solution['routes'].append({
                'vehicle_id': vehicle_id,
                'route': route,
                'distance': env.get_route_distance(route)
            })
    
    return solution


def invalid_route_solver(env):
    """
    Generates solution with invalid routes for testing validation.
    """
    vehicle_ids = env.get_available_vehicles()
    
    return {
        'routes': [
            {
                'vehicle_id': vehicle_ids[0] if vehicle_ids else 'fake_vehicle',
                'route': [1, 999, 1],  # Node 999 doesn't exist
                'distance': 0
            }
        ]
    }


def capacity_violation_solver(env):
    """
    Generates solution that violates vehicle capacity constraints.
    """
    vehicle_ids = env.get_available_vehicles()
    order_ids = env.get_all_order_ids()
    
    if not vehicle_ids or not order_ids:
        return {'routes': []}
    
    home_warehouse = env.get_vehicle_home_warehouse(vehicle_ids[0])
    
    # Create route that's too long for vehicle capacity
    return {
        'routes': [
            {
                'vehicle_id': vehicle_ids[0],
                'route': [home_warehouse] * 1000 + [home_warehouse],  # Impossibly long route
                'distance': 99999  # Exceeds any reasonable vehicle max_distance
            }
        ]
    }


def wrong_warehouse_solver(env):
    """
    Generates solution where vehicles don't start/end at home warehouse.
    """
    vehicle_ids = env.get_available_vehicles()
    
    if not vehicle_ids:
        return {'routes': []}
    
    return {
        'routes': [
            {
                'vehicle_id': vehicle_ids[0],
                'route': [2, 3, 4, 2],  # Doesn't start/end at vehicle's home warehouse
                'distance': 10
            }
        ]
    }


def empty_solution_solver(env):
    """
    Generates empty solution for testing edge cases.
    """
    return {'routes': []}


def malformed_solution_solver(env):
    """
    Generates malformed solution for testing error handling.
    """
    return {
        'routes': [
            {
                # Missing vehicle_id
                'route': [1, 2, 3, 1],
                'distance': 10
            },
            {
                'vehicle_id': 'valid_vehicle',
                # Missing route
                'distance': 5
            }
        ]
    }


def partial_fulfillment_solver(env):
    """
    Generates solution with detailed pickup/delivery operations for testing fulfillment tracking.
    """
    solution = {'routes': []}
    
    order_ids = env.get_all_order_ids()
    vehicle_ids = env.get_available_vehicles()
    road_network = env.get_road_network_data()
    adjacency_list = road_network['adjacency_list']
    
    if not order_ids or not vehicle_ids:
        return solution
    
    # Create route with detailed operations
    vehicle_id = vehicle_ids[0]
    order_id = order_ids[0]
    order_location = env.get_order_location(order_id)
    home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
    
    route = create_simple_path(home_warehouse, order_location, adjacency_list)
    
    if route:
        # Get order requirements for realistic operations
        requirements = env.get_order_requirements(order_id)
        
        pickup_ops = []
        delivery_ops = []
        
        for sku_id, quantity in requirements.items():
            # Find warehouse with this SKU
            warehouses_with_sku = env.get_warehouses_with_sku(sku_id, quantity)
            if warehouses_with_sku:
                pickup_ops.append({
                    'warehouse_id': warehouses_with_sku[0],
                    'sku_id': sku_id,
                    'quantity': quantity
                })
                
                # Partial delivery (deliver only half)
                delivery_ops.append({
                    'order_id': order_id,
                    'sku_id': sku_id,
                    'quantity': max(1, quantity // 2)
                })
        
        solution['routes'].append({
            'vehicle_id': vehicle_id,
            'route': route,
            'distance': env.get_route_distance(route),
            'pickup_operations': pickup_ops,
            'delivery_operations': delivery_ops
        })
    
    return solution


def create_simple_path(start, end, adjacency_list):
    """
    Simple BFS pathfinding for mock solvers.
    """
    if start == end:
        return [start, start]  # Simple round trip
    
    from collections import deque
    
    # Find path to destination
    queue = deque([(start, [start])])
    visited = {start}
    path_to_end = None
    
    while queue and len(queue) < 1000:  # Prevent infinite loops
        current, path = queue.popleft()
        
        if len(path) > 20:  # Reasonable path limit
            continue
        
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                new_path = path + [neighbor_int]
                
                if neighbor_int == end:
                    path_to_end = new_path
                    break
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, new_path))
        
        if path_to_end:
            break
    
    if not path_to_end:
        return None  # No path found
    
    # Find path back to start
    queue = deque([(end, [end])])
    visited = {end}
    path_to_start = None
    
    while queue and len(queue) < 1000:
        current, path = queue.popleft()
        
        if len(path) > 20:
            continue
        
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                new_path = path + [neighbor_int]
                
                if neighbor_int == start:
                    path_to_start = new_path
                    break
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, new_path))
        
        if path_to_start:
            break
    
    if not path_to_start:
        return None  # No path back
    
    # Combine paths
    return path_to_end + path_to_start[1:]  # Avoid duplicate end node


# Dictionary of all mock solvers for easy testing
MOCK_SOLVERS = {
    'valid': valid_mock_solver,
    'invalid_route': invalid_route_solver,
    'capacity_violation': capacity_violation_solver,
    'wrong_warehouse': wrong_warehouse_solver,
    'empty_solution': empty_solution_solver,
    'malformed_solution': malformed_solution_solver,
    'partial_fulfillment': partial_fulfillment_solver
}
