"""
Headless execution mode for Robin Logistics Environment.
Runs solvers without dashboard and saves organized results to directories.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from .environment import LogisticsEnvironment

class HeadlessRunner:
    """Run solvers in headless mode and save organized results."""

    def __init__(self, config: Optional[Dict] = None, output_base_dir: str = "results"):
        """
        Initialize headless runner.

        Args:
            config: Optional configuration for environment generation
            output_base_dir: Base directory for all result outputs
        """
        self.config = config
        self.output_base_dir = output_base_dir
        self.env = None
        self.current_run_dir = None

    def setup_environment(self, seed: Optional[int] = None):
        """Set up the logistics environment."""
        if self.config:
            self.env = LogisticsEnvironment()
            if seed is not None:
                self.env.set_random_seed(seed)
            self.env.generate_scenario_from_config(self.config)
        else:
            self.env = LogisticsEnvironment(self.config)
            if seed is not None:
                self.env.set_random_seed(seed)
                self.env.generate_new_scenario(seed)

    def run_solver(self, solver_function: Callable, solver_name: str = "unknown_solver",
                   run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a solver and save organized results.
        All simulation happens centrally with live tracking.

        Args:
            solver_function: Function that takes environment and returns solution
            solver_name: Name of the solver for file organization
            run_id: Optional run identifier, otherwise uses timestamp

        Returns:
            Dictionary containing run results and file paths
        """
        if self.env is None:
            self.setup_environment()

        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.current_run_dir = os.path.join(self.output_base_dir, f"{solver_name}_{run_id}")
        os.makedirs(self.current_run_dir, exist_ok=True)

        start_time = time.time()

        try:
            # Get initial system state
            initial_state = {
                'warehouses': len(self.env.warehouses),
                'vehicles': len(self.env.get_all_vehicles()),
                'orders': len(self.env.orders),
                'skus': len(self.env.skus)
            }
            
            # Run solver
            solution = solver_function(self.env)
            execution_time = time.time() - start_time

            # Get final system state after solver execution
            final_state = {
                'warehouses': len(self.env.warehouses),
                'vehicles': len(self.env.get_all_vehicles()),
                'orders': len(self.env.orders),
                'skus': len(self.env.skus)
            }

            # Validate solution
            is_valid, validation_message = self.env.validate_solution_complete(solution)

            # Calculate metrics
            statistics = self.env.get_solution_statistics(solution)
            fulfillment_summary = self.env.get_solution_fulfillment_summary(solution)

            run_results = {
                'solver_name': solver_name,
                'run_id': run_id,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'is_valid': is_valid,
                'validation_message': validation_message,
                'solution': solution,
                'statistics': statistics,
                'fulfillment_summary': fulfillment_summary,
                'environment_config': {
                    'num_warehouses': len(self.env.warehouses),
                    'num_vehicles': len(self.env.get_all_vehicles()),
                    'num_orders': len(self.env.orders),
                    'random_seed': self.env.get_current_seed()
                },
                'simulation_states': {
                    'initial': initial_state,
                    'final': final_state
                }
            }

            file_paths = self._save_results(run_results)

            return {
                'run_results': run_results,
                'output_directory': self.current_run_dir,
                'file_paths': file_paths
            }

        except Exception as e:
            execution_time = time.time() - start_time
            error_results = {
                'solver_name': solver_name,
                'run_id': run_id,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'is_valid': False,
                'validation_message': f"Solver execution failed: {e}"
            }

            error_file = os.path.join(self.current_run_dir, "error_report.txt")
            with open(error_file, 'w') as f:
                f.write(f"Solver Execution Error Report\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"Solver: {solver_name}\n")
                f.write(f"Run ID: {run_id}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Execution Time: {execution_time:.2f} seconds\n\n")
                f.write(f"Error: {e}\n")

            return {
                'run_results': error_results,
                'output_directory': self.current_run_dir,
                'error': str(e)
            }

    def _save_results(self, run_results: Dict[str, Any]) -> Dict[str, str]:
        """Save all result files and return file paths."""
        file_paths = {}

        summary_file = os.path.join(self.current_run_dir, "solution_summary.txt")
        self._save_solution_summary(run_results, summary_file)
        file_paths['summary'] = summary_file

        route_file = os.path.join(self.current_run_dir, "route_details.txt")
        self._save_route_details(run_results, route_file)
        file_paths['routes'] = route_file

        metrics_file = os.path.join(self.current_run_dir, "metrics.txt")
        self._save_metrics(run_results, metrics_file)
        file_paths['metrics'] = metrics_file

        validation_file = os.path.join(self.current_run_dir, "validation_report.txt")
        self._save_validation_report(run_results, validation_file)
        file_paths['validation'] = validation_file

        fulfillment_file = os.path.join(self.current_run_dir, "fulfillment_analysis.txt")
        self._save_fulfillment_analysis(run_results, fulfillment_file)
        file_paths['fulfillment'] = fulfillment_file

        json_file = os.path.join(self.current_run_dir, "raw_data.json")
        self._save_json_data(run_results, json_file)
        file_paths['json'] = json_file

        # Save simulation state tracking
        state_file = os.path.join(self.current_run_dir, "simulation_states.txt")
        self._save_simulation_states(run_results, state_file)
        file_paths['states'] = state_file

        return file_paths

    def _save_solution_summary(self, run_results: Dict[str, Any], file_path: str):
        """Save high-level solution summary."""
        with open(file_path, 'w') as f:
            f.write("ROBIN LOGISTICS - SOLUTION SUMMARY\n")
            f.write("="*50 + "\n\n")

            f.write(f"Solver: {run_results['solver_name']}\n")
            f.write(f"Run ID: {run_results['run_id']}\n")
            f.write(f"Timestamp: {run_results['timestamp']}\n")
            f.write(f"Execution Time: {run_results['execution_time']:.2f} seconds\n\n")

            f.write(f"VALIDATION STATUS: {'VALID' if run_results['is_valid'] else 'INVALID'}\n")
            f.write(f"Message: {run_results['validation_message']}\n\n")

            if 'statistics' in run_results:
                stats = run_results['statistics']
                f.write("KEY METRICS:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Routes: {stats.get('total_routes', 'N/A')}\n")
                f.write(f"Vehicles Used: {stats.get('unique_vehicles_used', 'N/A')}/{stats.get('total_vehicles', 'N/A')}\n")
                f.write(f"Orders Served: {stats.get('unique_orders_served', 'N/A')}/{stats.get('total_orders', 'N/A')}\n")
                f.write(f"Total Distance: {stats.get('total_distance', 0):.2f} km\n")
                f.write(f"Total Cost: ${stats.get('total_cost', 0):.2f}\n")
                f.write(f"Vehicle Utilization: {stats.get('vehicle_utilization_ratio', 0)*100:.1f}%\n")
                f.write(f"Order Fulfillment: {stats.get('average_fulfillment_rate', 0):.1f}%\n")

    def _save_route_details(self, run_results: Dict[str, Any], file_path: str):
        """Save detailed route information."""
        with open(file_path, 'w') as f:
            f.write("ROUTE DETAILS\n")
            f.write("="*50 + "\n\n")

            solution = run_results.get('solution', {})
            routes = solution.get('routes', [])

            for i, route in enumerate(routes, 1):
                f.write(f"ROUTE {i}:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Vehicle: {route.get('vehicle_id', 'Unknown')}\n")
                f.write(f"Route Path: {route.get('route', [])}\n")
                f.write(f"Distance: {route.get('distance', 0):.2f} km\n")

                pickup_ops = route.get('pickup_operations', [])
                if pickup_ops:
                    f.write("Pickup Operations:\n")
                    for pickup in pickup_ops:
                        f.write(f"  - Warehouse {pickup.get('warehouse_id')}: {pickup.get('quantity')}x {pickup.get('sku_id')}\n")

                delivery_ops = route.get('delivery_operations', [])
                if delivery_ops:
                    f.write("Delivery Operations:\n")
                    for delivery in delivery_ops:
                        f.write(f"  - Order {delivery.get('order_id')}: {delivery.get('quantity')}x {delivery.get('sku_id')}\n")

                f.write("\n")

    def _save_metrics(self, run_results: Dict[str, Any], file_path: str):
        """Save comprehensive metrics."""
        with open(file_path, 'w') as f:
            f.write("COMPREHENSIVE METRICS\n")
            f.write("="*50 + "\n\n")

            stats = run_results.get('statistics', {})

            f.write("OPERATIONAL METRICS:\n")
            f.write("-" * 20 + "\n")
            for key, value in stats.items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.3f}\n")
                else:
                    f.write(f"{key}: {value}\n")

            f.write("\nENVIRONMENT CONFIGURATION:\n")
            f.write("-" * 30 + "\n")
            env_config = run_results.get('environment_config', {})
            for key, value in env_config.items():
                f.write(f"{key}: {value}\n")

    def _save_validation_report(self, run_results: Dict[str, Any], file_path: str):
        """Save validation report."""
        with open(file_path, 'w') as f:
            f.write("VALIDATION REPORT\n")
            f.write("="*50 + "\n\n")

            f.write(f"Overall Status: {'VALID' if run_results['is_valid'] else 'INVALID'}\n")
            f.write(f"Message: {run_results['validation_message']}\n\n")

            solution = run_results.get('solution', {})
            routes = solution.get('routes', [])

            f.write("INDIVIDUAL ROUTE VALIDATION:\n")
            f.write("-" * 30 + "\n")

            for i, route in enumerate(routes, 1):
                vehicle_id = route.get('vehicle_id')
                route_path = route.get('route', [])

                if self.env and vehicle_id and route_path:
                    is_valid, message = self.env.validate_single_route(vehicle_id, route_path)
                    f.write(f"Route {i} ({vehicle_id}): {'VALID' if is_valid else 'INVALID'}\n")
                    if not is_valid:
                        f.write(f"  Error: {message}\n")
                else:
                    f.write(f"Route {i}: ⚠️ Cannot validate (missing data)\n")

    def _save_fulfillment_analysis(self, run_results: Dict[str, Any], file_path: str):
        """Save order fulfillment analysis."""
        with open(file_path, 'w') as f:
            f.write("ORDER FULFILLMENT ANALYSIS\n")
            f.write("="*50 + "\n\n")

            fulfillment = run_results.get('fulfillment_summary', {})

            f.write("FULFILLMENT SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Orders: {fulfillment.get('total_orders', 0)}\n")
            f.write(f"Orders Served: {fulfillment.get('orders_served', 0)}\n")
            f.write(f"Fully Fulfilled: {fulfillment.get('fully_fulfilled_orders', 0)}\n")
            f.write(f"Average Fulfillment Rate: {fulfillment.get('average_fulfillment_rate', 0):.1f}%\n\n")

            order_details = fulfillment.get('order_fulfillment_details', {})
            if order_details:
                f.write("ORDER-BY-ORDER DETAILS:\n")
                f.write("-" * 25 + "\n")

                for order_id, details in order_details.items():
                    fulfillment_rate = details.get('fulfillment_rate', 0)
                    f.write(f"\n{order_id}: {fulfillment_rate:.1f}% fulfilled\n")

                    requested = details.get('requested', {})
                    delivered = details.get('delivered', {})
                    remaining = details.get('remaining', {})

                    for sku_id in requested:
                        req = requested.get(sku_id, 0)
                        del_qty = delivered.get(sku_id, 0)
                        rem = remaining.get(sku_id, 0)
                        f.write(f"  {sku_id}: {del_qty}/{req} delivered ({rem} remaining)\n")

    def _save_json_data(self, run_results: Dict[str, Any], file_path: str):
        """Save raw data as JSON for programmatic access."""
        json_data = dict(run_results)

        try:
            with open(file_path, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
        except (TypeError, ValueError) as e:
            simplified_data = {
                'solver_name': run_results.get('solver_name'),
                'run_id': run_results.get('run_id'),
                'execution_time': run_results.get('execution_time'),
                'timestamp': run_results.get('timestamp'),
                'is_valid': run_results.get('is_valid'),
                'validation_message': run_results.get('validation_message'),
                'statistics': run_results.get('statistics', {}),
                'environment_config': run_results.get('environment_config', {})
            }
            with open(file_path, 'w') as f:
                json.dump(simplified_data, f, indent=2, default=str)

    def _save_simulation_states(self, run_results: Dict[str, Any], file_path: str):
        """Save simulation state tracking information."""
        with open(file_path, 'w') as f:
            f.write("SIMULATION STATE TRACKING\n")
            f.write("="*50 + "\n\n")

            initial_state = run_results.get('simulation_states', {}).get('initial', {})
            final_state = run_results.get('simulation_states', {}).get('final', {})
            initial_progress = run_results.get('simulation_states', {}).get('initial_progress', {})
            final_progress = run_results.get('simulation_states', {}).get('final_progress', {})

            f.write("INITIAL STATE:\n")
            f.write("-" * 20 + "\n")
            for key, value in initial_state.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            f.write("FINAL STATE:\n")
            f.write("-" * 20 + "\n")
            for key, value in final_state.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            f.write("INITIAL PROGRESS:\n")
            f.write("-" * 20 + "\n")
            for key, value in initial_progress.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            f.write("FINAL PROGRESS:\n")
            f.write("-" * 20 + "\n")
            for key, value in final_progress.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

    def _print_summary(self, run_results: Dict[str, Any]):
        """Print a summary to console."""
        stats = run_results.get('statistics', {})
        print(f"Status: {'VALID' if run_results['is_valid'] else 'INVALID'}")
        print(f"Time: {run_results['execution_time']:.2f}s")
        print(f"Vehicles: {stats.get('unique_vehicles_used', 0)}/{stats.get('total_vehicles', 0)}")
        print(f"Orders: {stats.get('unique_orders_served', 0)}/{stats.get('total_orders', 0)}")
        print(f"Distance: {stats.get('total_distance', 0):.1f} km")
        print(f"Cost: ${stats.get('total_cost', 0):.2f}")
        print(f"Fulfillment: {stats.get('average_fulfillment_rate', 0):.1f}%")
        print(f"Results: {self.current_run_dir}")

def run_headless_solver(solver_function: Callable, solver_name: str = "solver",
                       config: Optional[Dict] = None, output_dir: str = "results",
                       seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Convenience function to run a solver in headless mode.

    Args:
        solver_function: Function that takes environment and returns solution
        solver_name: Name for file organization
        config: Optional environment configuration
        output_dir: Output directory
        seed: Optional random seed

    Returns:
        Run results dictionary
    """
    runner = HeadlessRunner(config, output_dir)
    runner.setup_environment(seed)
    return runner.run_solver(solver_function, solver_name)
