"""
Solution validation module for comprehensive route and operation validation.
"""

from typing import Dict, List, Tuple, Optional, Any


class SolutionValidator:
    """
    Comprehensive solution validation for all constraints and business logic.
    Separated from environment for better modularity and testing.
    """
    
    def __init__(self, warehouses: Dict, vehicles: Dict, orders: Dict, skus: Dict, network_manager):
        """Initialize validator with system components."""
        self.warehouses = warehouses
        self.vehicles = vehicles
        self.orders = orders
        self.skus = skus
        self.network_manager = network_manager
    
    def validate_solution_business_logic(self, solution: Dict) -> Tuple[bool, str]:
        """Validate solution business logic."""
        if not solution or 'routes' not in solution:
            return False, "Solution must contain routes"

        routes = solution['routes']
        if not isinstance(routes, list):
            return False, "Routes must be a list"

        assigned_vehicles = set()

        for route in routes:
            vehicle_id = route.get('vehicle_id')
            if not vehicle_id:
                return False, "Each route must have a vehicle_id"

            if vehicle_id in assigned_vehicles:
                return False, f"Vehicle {vehicle_id} assigned to multiple routes"

            assigned_vehicles.add(vehicle_id)

            if vehicle_id not in self.vehicles:
                return False, f"Unknown vehicle {vehicle_id}"

        return True, "Solution business logic is valid"
    
    def validate_route_physical(self, route: List[int]) -> Tuple[bool, str]:
        """Validate that a route follows the actual road network."""
        if not route or len(route) < 2:
            return False, "Route must have at least 2 nodes"

        for i in range(len(route) - 1):
            if not self.network_manager.has_edge(route[i], route[i+1]):
                return False, f"No road connection from node {route[i]} to {route[i+1]}"

        return True, "Route follows road network"
    
    def validate_single_route(self, vehicle_id: str, route: List[int], 
                             pickup_operations: List[Dict] = None, 
                             delivery_operations: List[Dict] = None) -> Tuple[bool, str]:
        """
        Validate a single route against ALL constraints including feasibility.
        """
        if vehicle_id not in self.vehicles:
            return False, f"Unknown vehicle {vehicle_id}"
            
        vehicle = self.vehicles[vehicle_id]
        
        warehouse_node_id = None
        for wh in self.warehouses.values():
            if wh.id == vehicle.home_warehouse_id:
                warehouse_node_id = wh.location.id
                break
                
        if warehouse_node_id is None:
            return False, f"Warehouse {vehicle.home_warehouse_id} not found for vehicle {vehicle_id}"

        if not route or len(route) < 2:
            return False, "Route must have at least 2 nodes"

        if route[0] != warehouse_node_id or route[-1] != warehouse_node_id:
            return False, f"Route must start and end at home warehouse node {warehouse_node_id}"

        is_physical_valid, physical_msg = self.validate_route_physical(route)
        if not is_physical_valid:
            return False, physical_msg

        route_distance = self.network_manager.get_route_distance(route)
        if route_distance > vehicle.max_distance:
            return False, f"Route distance {route_distance:.2f} km exceeds vehicle max distance {vehicle.max_distance} km"

        if pickup_operations is not None and delivery_operations is not None:
            feasible, feasible_msg = self.validate_route_feasibility(
                vehicle_id, pickup_operations, delivery_operations
            )
            if not feasible:
                return False, feasible_msg

        return True, "Route is valid"
    
    def validate_route_feasibility(self, vehicle_id: str, pickup_operations: List[Dict], 
                                  delivery_operations: List[Dict]) -> Tuple[bool, str]:
        """
        Validate that a route's operations can actually be executed.
        """
        from ..state.orchestrator import LogisticsOrchestrator
        
        if vehicle_id not in self.vehicles:
            return False, f"Vehicle {vehicle_id} not found"
            
        vehicle = self.vehicles[vehicle_id]
        current_weight = 0.0
        current_volume = 0.0
        
        for pickup in pickup_operations:
            warehouse_id = pickup.get('warehouse_id')
            sku_id = pickup.get('sku_id')
            quantity = pickup.get('quantity', 0)
            
            if warehouse_id not in self.warehouses:
                return False, f"Warehouse {warehouse_id} not found"
                
            if sku_id not in self.skus:
                return False, f"SKU {sku_id} not found"
                
            sku = self.skus[sku_id]
            additional_weight = sku.weight * quantity
            additional_volume = sku.volume * quantity
            
            if current_weight + additional_weight > vehicle.capacity_weight:
                return False, f"Weight capacity exceeded: {current_weight + additional_weight:.1f} > {vehicle.capacity_weight}"
            
            if current_volume + additional_volume > vehicle.capacity_volume:
                return False, f"Volume capacity exceeded: {current_volume + additional_volume:.3f} > {vehicle.capacity_volume}"
                
            current_weight += additional_weight
            current_volume += additional_volume
        
        vehicle_inventory = {}
        for pickup in pickup_operations:
            sku_id = pickup.get('sku_id')
            quantity = pickup.get('quantity', 0)
            vehicle_inventory[sku_id] = vehicle_inventory.get(sku_id, 0) + quantity
        
        for delivery in delivery_operations:
            order_id = delivery.get('order_id')
            sku_id = delivery.get('sku_id')
            quantity = delivery.get('quantity', 0)
            
            if order_id not in self.orders:
                return False, f"Order {order_id} not found"
                
            if sku_id not in vehicle_inventory:
                return False, f"Vehicle doesn't have SKU {sku_id} for delivery"
                
            if vehicle_inventory[sku_id] < quantity:
                return False, f"Vehicle doesn't have enough {sku_id}: need {quantity}, have {vehicle_inventory[sku_id]}"
                
            vehicle_inventory[sku_id] -= quantity
            current_weight -= self.skus[sku_id].weight * quantity
            current_volume -= self.skus[sku_id].volume * quantity

        return True, "Route operations are feasible"
    
    def validate_solution_complete(self, solution: Dict) -> Tuple[bool, str]:
        """Comprehensive solution validation."""
        is_business_valid, business_msg = self.validate_solution_business_logic(solution)
        if not is_business_valid:
            return False, f"Business logic validation failed: {business_msg}"

        for i, route in enumerate(solution.get('routes', [])):
            vehicle_id = route.get('vehicle_id')
            route_path = route.get('route', [])

            if not vehicle_id or not route_path:
                return False, f"Route {i} missing vehicle_id or route path"

            is_valid, error_msg = self.validate_single_route(vehicle_id, route_path)
            if not is_valid:
                return False, f"Route {i} validation failed: {error_msg}"

        return True, "Solution is completely valid"
