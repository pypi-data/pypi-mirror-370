"""
Metrics calculation module for comprehensive solution analysis.
"""

from typing import Dict, List, Any


class MetricsCalculator:
    """
    Centralized metrics and statistics calculation for solutions.
    Handles all performance metrics, costs, and fulfillment analysis.
    """
    
    def __init__(self, warehouses: Dict, vehicles: Dict, orders: Dict, skus: Dict, network_manager):
        """Initialize calculator with system components."""
        self.warehouses = warehouses
        self.vehicles = vehicles
        self.orders = orders
        self.skus = skus
        self.network_manager = network_manager
    
    def calculate_solution_cost(self, solution: Dict) -> float:
        """Calculate the total operational cost of a solution."""
        total_cost = 0.0
        routes = solution.get("routes", [])

        for route_info in routes:
            vehicle_id = route_info.get('vehicle_id')
            route = route_info.get('route', [])

            if vehicle_id and route and vehicle_id in self.vehicles:
                vehicle = self.vehicles[vehicle_id]
                total_cost += vehicle.fixed_cost
                route_distance = self.network_manager.get_route_distance(route)
                total_cost += route_distance * vehicle.cost_per_km

        return total_cost
    
    def get_solution_statistics(self, solution: Dict) -> Dict:
        """Get comprehensive solution statistics."""
        routes = solution.get('routes', [])

        vehicles_used = set()
        orders_served = set()
        total_distance = 0.0

        for route in routes:
            vehicle_id = route.get('vehicle_id')
            route_path = route.get('route', [])

            if vehicle_id and route_path:
                vehicles_used.add(vehicle_id)
                route_distance = self.network_manager.get_route_distance(route_path)
                total_distance += route_distance

                delivery_ops = route.get('delivery_operations', [])
                for delivery_op in delivery_ops:
                    order_id = delivery_op.get('order_id')
                    if order_id:
                        orders_served.add(order_id)

        total_cost = self.calculate_solution_cost(solution)
        fulfillment_summary = self.get_solution_fulfillment_summary(solution)

        total_vehicles = len(self.vehicles)
        total_orders = len(self.orders)

        vehicle_utilization_ratio = len(vehicles_used) / total_vehicles if total_vehicles > 0 else 0

        return {
            'total_routes': len(routes),
            'unique_vehicles_used': len(vehicles_used),
            'total_vehicles': total_vehicles,
            'unique_orders_served': len(orders_served),
            'total_orders': total_orders,
            'total_distance': total_distance,
            'total_cost': total_cost,
            'vehicle_utilization_ratio': vehicle_utilization_ratio,
            'orders_fulfillment_ratio': fulfillment_summary['average_fulfillment_rate'] / 100.0,
            'average_fulfillment_rate': fulfillment_summary['average_fulfillment_rate'],
            'fully_fulfilled_orders': fulfillment_summary['fully_fulfilled_orders']
        }
    
    def get_solution_fulfillment_summary(self, solution: Dict) -> Dict:
        """Get comprehensive fulfillment summary for entire solution."""
        routes = solution.get('routes', [])

        order_fulfillment = {}
        vehicles_used = set()
        total_distance = 0.0

        for order_id, order in self.orders.items():
            order_fulfillment[order_id] = {
                'requested': order.requested_items.copy(),
                'delivered': {},
                'remaining': {}
            }

        for route in routes:
            vehicle_id = route.get('vehicle_id')
            route_path = route.get('route', [])

            if vehicle_id and route_path:
                vehicles_used.add(vehicle_id)
                route_distance = self.network_manager.get_route_distance(route_path)
                total_distance += route_distance

                delivery_ops = route.get('delivery_operations', [])
                for delivery_op in delivery_ops:
                    order_id = delivery_op.get('order_id')
                    sku_id = delivery_op.get('sku_id')
                    quantity = delivery_op.get('quantity', 0)

                    if order_id in order_fulfillment and sku_id in order_fulfillment[order_id]['requested']:
                        if sku_id not in order_fulfillment[order_id]['delivered']:
                            order_fulfillment[order_id]['delivered'][sku_id] = 0
                        order_fulfillment[order_id]['delivered'][sku_id] += quantity

        total_fulfillment_rate = 0.0
        fully_fulfilled_orders = 0

        for order_id, fulfillment in order_fulfillment.items():
            total_requested = sum(fulfillment['requested'].values())
            total_delivered = sum(fulfillment['delivered'].values())

            for sku_id in fulfillment['requested']:
                requested = fulfillment['requested'][sku_id]
                delivered = fulfillment['delivered'].get(sku_id, 0)
                fulfillment['remaining'][sku_id] = max(0, requested - delivered)

            if total_requested > 0:
                fulfillment['fulfillment_rate'] = (total_delivered / total_requested) * 100
                total_fulfillment_rate += fulfillment['fulfillment_rate']

                if total_delivered >= total_requested:
                    fully_fulfilled_orders += 1
            else:
                fulfillment['fulfillment_rate'] = 100.0
                total_fulfillment_rate += 100.0
                fully_fulfilled_orders += 1

        avg_fulfillment_rate = total_fulfillment_rate / len(order_fulfillment) if order_fulfillment else 0

        total_cost = self.calculate_solution_cost(solution)

        return {
            'total_orders': len(self.orders),
            'orders_served': len([o for o in order_fulfillment.values() if sum(o['delivered'].values()) > 0]),
            'fully_fulfilled_orders': fully_fulfilled_orders,
            'total_vehicles': len(self.vehicles),
            'vehicles_used': len(vehicles_used),
            'total_distance': total_distance,
            'total_cost': total_cost,
            'average_fulfillment_rate': avg_fulfillment_rate,
            'order_fulfillment_details': order_fulfillment,
            'vehicle_utilization': (len(vehicles_used) / len(self.vehicles)) * 100 if self.vehicles else 0
        }
