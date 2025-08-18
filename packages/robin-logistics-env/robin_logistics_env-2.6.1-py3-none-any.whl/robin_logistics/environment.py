"""
Main interface for hackathon contestants.
Provides clean access to problem data, inventory tracking, and constraint validation.
"""

import pandas as pd
import os
from typing import Dict, List, Tuple, Optional, Any

from .core.models import Node, SKU, Order, Vehicle, Warehouse
from .core.state.orchestrator import LogisticsOrchestrator
from .core.data_generator import generate_problem_instance, generate_scenario_from_config
from .core.validation import SolutionValidator
from .core.metrics import MetricsCalculator
from .core.network import NetworkManager

class LogisticsEnvironment:
    """
    Main interface for hackathon contestants.
    Provides clean access to problem data, inventory tracking, and constraint validation.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the logistics environment."""
        self._current_seed = None
        self.validator = None
        self.metrics_calculator = None
        self.network_manager = None

        self._load_problem_instance()
        self._reset_vehicle_states()

    def _load_problem_instance(self):
        """Load and initialize the problem instance."""
        nodes_df, edges_df, warehouses, orders, skus, vehicles = generate_problem_instance()
        self._initialize_environment(nodes_df, edges_df, warehouses, orders, skus, vehicles)
        self._current_seed = None

    def _initialize_environment(self, nodes_df, edges_df, warehouses, orders, skus, vehicles):
        """Initialize the environment with problem data."""
        if nodes_df is None or nodes_df.empty:
            raise ValueError("nodes_df cannot be None or empty")
        if edges_df is None:
            raise ValueError("edges_df cannot be None")
        if not warehouses:
            raise ValueError("warehouses cannot be empty")
        if not orders:
            raise ValueError("orders cannot be empty")
        if not skus:
            raise ValueError("skus cannot be empty")
        if not vehicles:
            raise ValueError("vehicles cannot be empty")

        required_node_cols = ['node_id', 'lat', 'lon']
        if not all(col in nodes_df.columns for col in required_node_cols):
            raise ValueError(f"nodes_df must contain columns: {required_node_cols}")

        if not all(-90 <= lat <= 90 for lat in nodes_df['lat']):
            raise ValueError("Latitude values must be between -90 and 90")
        if not all(-180 <= lon <= 180 for lon in nodes_df['lon']):
            raise ValueError("Longitude values must be between -180 and 180")

        self.nodes = {}
        for _, row in nodes_df.iterrows():
            node = Node(
                node_id=row['node_id'],
                lat=row['lat'],
                lon=row['lon']
            )
            self.nodes[node.id] = node

        self.warehouses = {warehouse.id: warehouse for warehouse in warehouses}
        self.orders = {order.id: order for order in orders}
        self.skus = {sku.id: sku for sku in skus}
        
        self.network_manager = NetworkManager(self.nodes, edges_df)
        
        self.orchestrator = LogisticsOrchestrator(
            warehouses=self.warehouses,
            vehicles=vehicles,
            orders=self.orders,
            skus=self.skus
        )
        
        vehicles_dict = {v.id: v for v in self.get_all_vehicles()}
        self.validator = SolutionValidator(
            self.warehouses, vehicles_dict, self.orders, self.skus, self.network_manager
        )
        self.metrics_calculator = MetricsCalculator(
            self.warehouses, vehicles_dict, self.orders, self.skus, self.network_manager
        )
        
        self._validate_environment()



    def _validate_environment(self):
        """Validate the environment configuration."""
        if not self.warehouses:
            raise ValueError("No warehouses defined")
        if not self.orders:
            raise ValueError("No orders defined")
        if not self.skus:
            raise ValueError("No SKUs defined")
        all_vehicles = self.get_all_vehicles()
        if not all_vehicles:
            raise ValueError("No vehicles defined")

        for warehouse in self.warehouses.values():
            if warehouse.location.id not in self.nodes:
                raise ValueError(f"Warehouse {warehouse.id} location {warehouse.location.id} not in road network")

        for order in self.orders.values():
            if order.destination.id not in self.nodes:
                raise ValueError(f"Order {order.id} destination {order.destination.id} not in road network")

    def _reset_vehicle_states(self):
        """Reset vehicle load, weight, volume, and location states using central orchestrator."""
        if hasattr(self, 'orchestrator'):
            self.orchestrator.reset_all_vehicles()



    def get_all_vehicles(self):
        """Get all vehicles from all warehouses."""
        all_vehicles = []
        for warehouse in self.warehouses.values():
            all_vehicles.extend(warehouse.vehicles)
        return all_vehicles

    def get_vehicle_by_id(self, vehicle_id):
        """Get vehicle by ID."""
        for warehouse in self.warehouses.values():
            for vehicle in warehouse.vehicles:
                if vehicle.id == vehicle_id:
                    return vehicle
        return None

    def get_warehouse_by_id(self, warehouse_id):
        """Get warehouse by ID."""
        return self.warehouses.get(warehouse_id)

    def get_road_network_data(self) -> Dict:
        """Get complete road network data for pathfinding."""
        return self.network_manager.get_road_network_data()



    def get_distance(self, node1: int, node2: int) -> Optional[float]:
        """
        Get direct distance between two connected nodes.
        Returns None if no direct connection exists.
        """
        return self.network_manager.get_distance(node1, node2)

    def get_route_distance(self, route: List[int]) -> float:
        """
        Calculate total distance for a route (list of node IDs).
        Uses actual road network distances from edges.
        """
        return self.network_manager.get_route_distance(route)

    def get_all_order_ids(self) -> List[str]:
        """Get list of all order IDs."""
        return list(self.orders.keys())

    def get_available_vehicles(self) -> List[str]:
        """Get list of all available vehicle IDs."""
        all_vehicles = self.get_all_vehicles()
        return [v.id for v in all_vehicles]

    def get_order_location(self, order_id: str) -> int:
        """Get the delivery location node ID for an order."""
        if order_id in self.orders:
            return self.orders[order_id].destination.id
        raise ValueError(f"Order {order_id} not found")

    def get_vehicle_home_warehouse(self, vehicle_id: str) -> int:
        """Get the home warehouse node ID for a vehicle."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if vehicle:
            warehouse_id = vehicle.home_warehouse_id

            for warehouse in self.warehouses.values():
                if warehouse.id == warehouse_id:
                    return warehouse.location.id

            raise ValueError(f"Warehouse {warehouse_id} not found for vehicle {vehicle_id}")
        raise ValueError(f"Vehicle {vehicle_id} not found")

    def get_order_requirements(self, order_id: str) -> Dict[str, int]:
        """Get SKU requirements for an order."""
        if order_id in self.orders:
            return self.orders[order_id].requested_items.copy()
        return {}

    def get_warehouse_inventory(self, warehouse_id: str) -> Dict[str, int]:
        """Get current inventory levels for a specific warehouse from central orchestrator."""
        return self.orchestrator.warehouse_inventories.get(warehouse_id, {})

    def get_vehicle_current_load(self, vehicle_id: str) -> Dict[str, int]:
        """Get current SKU quantities loaded on a vehicle from central orchestrator."""
        return self.orchestrator.vehicle_loads.get(vehicle_id, {})

    def get_vehicle_current_capacity(self, vehicle_id: str) -> Tuple[float, float]:
        """Get current weight and volume usage for a vehicle from central orchestrator."""
        return self.orchestrator.get_vehicle_capacity_usage(vehicle_id)

    def get_vehicle_remaining_capacity(self, vehicle_id: str) -> Tuple[float, float]:
        """Get remaining weight and volume capacity for a vehicle from central orchestrator."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return 0.0, 0.0
        
        current_weight, current_volume = self.orchestrator.get_vehicle_capacity_usage(vehicle_id)
        remaining_weight = max(0.0, vehicle.capacity_weight - current_weight)
        remaining_volume = max(0.0, vehicle.capacity_volume - current_volume)
        return remaining_weight, remaining_volume

    def get_order_fulfillment_status(self, order_id: str) -> Dict[str, Dict[str, int]]:
        """Get detailed fulfillment status for an order."""
        if order_id not in self.orders:
            return {}

        order = self.orders[order_id]
        result = {
            'requested': order.requested_items.copy(),
            'delivered': getattr(order, '_delivered_items', {}),
            'remaining': {}
        }

        for sku_id in order.requested_items:
            requested = order.requested_items[sku_id]
            delivered = result['delivered'].get(sku_id, 0)
            result['remaining'][sku_id] = max(0, requested - delivered)

        return result

    def get_warehouses_with_sku(self, sku_id: str, min_quantity: int = 1) -> List[str]:
        """Find all warehouses that have a specific SKU in stock."""
        warehouses_with_sku = []

        for warehouse_id, warehouse in self.warehouses.items():
            if sku_id in warehouse.inventory and warehouse.inventory[sku_id] >= min_quantity:
                warehouses_with_sku.append(warehouse_id)

        return warehouses_with_sku

    def get_sku_details(self, sku_id: str) -> Optional[Dict]:
        """Get SKU specifications (weight, volume)."""
        if sku_id in self.skus:
            sku = self.skus[sku_id]
            return {
                'id': sku.id,
                'weight': sku.weight,
                'volume': sku.volume
            }
        return None

    def pickup_sku_from_warehouse(self, vehicle_id: str, warehouse_id: str, sku_id: str, quantity: int) -> bool:
        """
        Pick up SKU from warehouse and load onto vehicle.
        NOW USES CENTRAL ORCHESTRATOR - Single source of truth.

        Args:
            vehicle_id: ID of the vehicle
            warehouse_id: ID of the warehouse
            sku_id: ID of the SKU to pick up
            quantity: Quantity to pick up

        Returns:
            True if successful, False otherwise
        """
        success, _ = self.orchestrator.execute_pickup(vehicle_id, warehouse_id, sku_id, quantity)
        return success

    def deliver_sku_to_order(self, vehicle_id: str, order_id: str, sku_id: str, quantity: int) -> bool:
        """
        Deliver SKU from vehicle to order.
        NOW USES CENTRAL ORCHESTRATOR - Single source of truth.

        Args:
            vehicle_id: ID of the vehicle
            order_id: ID of the order
            sku_id: ID of the SKU to deliver
            quantity: Quantity to deliver

        Returns:
            True if successful, False otherwise
        """
        success, _ = self.orchestrator.execute_delivery(vehicle_id, order_id, sku_id, quantity)
        return success

    def unload_sku_to_warehouse(self, vehicle_id: str, warehouse_id: str, sku_id: str, quantity: int) -> bool:
        """
        Unload SKU from vehicle to a warehouse.
        NOW USES CENTRAL ORCHESTRATOR - Single source of truth.

        Args:
            vehicle_id: ID of the vehicle
            warehouse_id: ID of the warehouse to unload to
            sku_id: ID of the SKU to unload
            quantity: Quantity to unload

        Returns:
            True if successful, False otherwise
        """
        success, _ = self.orchestrator.execute_unload(vehicle_id, warehouse_id, sku_id, quantity)
        return success





    def execute_route(self, vehicle_id: str, route: List[int], 
                      pickup_operations: List[Dict], 
                      delivery_operations: List[Dict]) -> Tuple[bool, str]:
        """
        Execute a single route with pickup and delivery operations.
        
        This method validates and executes a route using the centralized orchestrator.
        Handles both simple and complex multi-warehouse routes.
        
        Args:
            vehicle_id: ID of the vehicle
            route: List of node IDs in the route
            pickup_operations: List of pickup operation dictionaries
            delivery_operations: List of delivery operation dictionaries
            
        Returns:
            Tuple of (success, message)
        """
        is_valid, error_msg = self.validate_single_route(
            vehicle_id, route, pickup_operations, delivery_operations
        )
        if not is_valid:
            return False, f"Route validation failed: {error_msg}"
        
        for pickup in pickup_operations:
            success = self.pickup_sku_from_warehouse(
                vehicle_id, pickup['warehouse_id'], pickup['sku_id'], pickup['quantity']
            )
            if not success:
                return False, f"Pickup failed for {pickup['sku_id']} from {pickup['warehouse_id']}"
        
        for delivery in delivery_operations:
            success = self.deliver_sku_to_order(
                vehicle_id, delivery['order_id'], delivery['sku_id'], delivery['quantity']
            )
            if not success:
                return False, f"Delivery failed for {delivery['sku_id']} to {delivery['order_id']}"
        
        return True, "Route executed successfully"

    def execute_solution(self, solution: Dict) -> Tuple[bool, str]:
        """
        Execute a complete solution by running all routes.
        
        This method takes a validated solution and actually executes all the
        pickup and delivery operations to update the system state.
        
        Args:
            solution: Dictionary with 'routes' list
            
        Returns:
            Tuple of (success, message)
        """
        if not solution or 'routes' not in solution:
            return False, "Invalid solution: no routes found"
        
        routes = solution['routes']
        if not routes:
            return False, "No routes to execute"
        
        executed_routes = 0
        failed_routes = 0
        
        for route in routes:
            vehicle_id = route.get('vehicle_id')
            pickup_ops = route.get('pickup_operations', [])
            delivery_ops = route.get('delivery_operations', [])
            route_path = route.get('route', [])
            
            if not vehicle_id or not route_path:
                failed_routes += 1
                continue
            
            success, msg = self.execute_route(
                vehicle_id, route_path, pickup_ops, delivery_ops
            )
            
            if success:
                executed_routes += 1
            else:
                failed_routes += 1
        
        if failed_routes == 0:
            return True, f"Successfully executed all {executed_routes} routes"
        elif executed_routes > 0:
            return True, f"Executed {executed_routes} routes, {failed_routes} failed"
        else:
            return False, f"All {failed_routes} routes failed to execute"

    def set_random_seed(self, seed: int):
        """Set random seed for reproducible scenarios."""
        self._current_seed = seed

    def get_current_seed(self) -> Optional[int]:
        """Get current random seed."""
        return self._current_seed

    def generate_new_scenario(self, seed: Optional[int] = None):
        """Generate a new problem scenario."""
        if seed is not None:
            self.set_random_seed(seed)
        self._load_problem_instance()
        self._reset_vehicle_states()

    def generate_scenario_from_config(self, config: Dict):
        """Generate scenario from dashboard configuration."""
        if 'random_seed' in config and config['random_seed'] is not None:
            self._current_seed = config['random_seed']
        else:
            self._current_seed = None

        from .core import config as core_config

        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
        edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))

        problem_data = generate_scenario_from_config(core_config, nodes_df, edges_df, config)

        nodes = problem_data['nodes']
        edges_df_final = problem_data['edges_df']
        warehouses = problem_data['warehouses']
        orders, _ = problem_data['orders']
        skus = problem_data['skus']

        all_vehicles = []
        for warehouse in warehouses:
            all_vehicles.extend(warehouse.vehicles)

        nodes_df_final = pd.DataFrame([
            {'node_id': node.id, 'lat': node.lat, 'lon': node.lon}
            for node in nodes
        ])

        self._initialize_environment(nodes_df_final, edges_df_final, warehouses, orders, skus, all_vehicles)
        self._reset_vehicle_states()

    def validate_route_physical(self, route: List[int]) -> Tuple[bool, str]:
        """Validate that a route follows the actual road network."""
        return self.validator.validate_route_physical(route)

    def validate_single_route(self, vehicle_id: str, route: List[int], 
                               pickup_operations: List[Dict] = None, 
                               delivery_operations: List[Dict] = None) -> Tuple[bool, str]:
        """
        Validate a single route against ALL constraints including feasibility.
        """
        return self.validator.validate_single_route(vehicle_id, route, pickup_operations, delivery_operations)

    def validate_route_feasibility(self, vehicle_id: str, pickup_operations: List[Dict], 
                                   delivery_operations: List[Dict]) -> Tuple[bool, str]:
        """
        Validate that a route's operations can actually be executed.
        """
        return self.validator.validate_route_feasibility(vehicle_id, pickup_operations, delivery_operations)

    def validate_solution_business_logic(self, solution: Dict) -> Tuple[bool, str]:
        """Validate solution business logic."""
        return self.validator.validate_solution_business_logic(solution)

    def validate_solution_complete(self, solution: Dict) -> Tuple[bool, str]:
        """Comprehensive solution validation."""
        return self.validator.validate_solution_complete(solution)

    def calculate_solution_cost(self, solution: Dict) -> float:
        """Calculate the total operational cost of a solution."""
        return self.metrics_calculator.calculate_solution_cost(solution)

    def get_solution_statistics(self, solution: Dict) -> Dict:
        """Get comprehensive solution statistics."""
        return self.metrics_calculator.get_solution_statistics(solution)

    def get_solution_fulfillment_summary(self, solution: Dict) -> Dict:
        """Get comprehensive fulfillment summary for entire solution."""
        return self.metrics_calculator.get_solution_fulfillment_summary(solution)

    def set_solver(self, solver_function):
        """Set the solver function for the environment."""
        self._solver_function = solver_function

    def launch_dashboard(self):
        """Launch the dashboard with the current solver."""
        if not hasattr(self, '_solver_function'):
            raise ValueError("No solver set. Call set_solver() first.")
        
        import subprocess
        import sys
        import os
        
        # Get the dashboard file path
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.py')
        
        if not os.path.exists(dashboard_path):
            raise FileNotFoundError(f"Dashboard not found at: {dashboard_path}")
        
        print("Launching Robin Logistics Dashboard...")
        print("Local URL: http://localhost:8501")
        print("To stop the dashboard, press Ctrl+C in this terminal")
        
        try:
            # Launch Streamlit with the dashboard
            cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", "8501"]
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to launch dashboard: {e}")
            print("Make sure Streamlit is installed: pip install streamlit")
        except KeyboardInterrupt:
            print("\nDashboard stopped by user")
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Check your Python environment and dependencies")

    def run_headless(self, run_id: str = "run_001"):
        """Run the solver headlessly and save results."""
        if not hasattr(self, '_solver_function'):
            raise ValueError("No solver set. Call set_solver() first.")
        
        from .headless import HeadlessRunner
        runner = HeadlessRunner()
        results = runner.run_solver(self._solver_function, "custom_solver", run_id)
        return results













