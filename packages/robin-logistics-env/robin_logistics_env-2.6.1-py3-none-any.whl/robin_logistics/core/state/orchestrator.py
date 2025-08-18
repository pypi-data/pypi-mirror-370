"""
Central orchestrator for ALL warehouse inventory and vehicle state management.
Single source of truth for the entire logistics system.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from ..models.vehicle import Vehicle
from ..models.warehouse import Warehouse
from ..models.order import Order


@dataclass
class SystemSnapshot:
    """Snapshot of entire system state for rollback purposes."""
    warehouse_inventories: Dict[str, Dict[str, int]]
    vehicle_loads: Dict[str, Dict[str, int]]
    vehicle_capacities: Dict[str, Tuple[float, float]]
    order_deliveries: Dict[str, Dict[str, int]]


class LogisticsOrchestrator:
    """
    SINGLE SOURCE OF TRUTH for all logistics operations.
    
    This class manages:
    - Warehouse inventory (ALL modifications go through here)
    - Vehicle loading/unloading (ALL state changes go through here)  
    - Order fulfillment tracking
    - Atomic operations with rollback
    - Constraint validation
    """
    
    def __init__(self, warehouses: Dict[str, Warehouse], vehicles: List[Vehicle], 
                 orders: Dict[str, Order], skus: Dict[str, Any]):
        """Initialize the orchestrator with all system entities."""
        self.warehouses = warehouses
        self.vehicles = {v.id: v for v in vehicles}
        self.orders = orders
        self.skus = skus
        
        self.warehouse_inventories = {}
        self.vehicle_loads = {}
        self.vehicle_capacities = {}
        self.order_deliveries = {}
        
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize all state from the base models."""
        for wh_id, warehouse in self.warehouses.items():
            self.warehouse_inventories[wh_id] = warehouse.inventory.copy()
        
        for vehicle_id, vehicle in self.vehicles.items():
            self.vehicle_loads[vehicle_id] = {}
            self.vehicle_capacities[vehicle_id] = (0.0, 0.0)
        
        for order_id in self.orders:
            self.order_deliveries[order_id] = {}
    
    def create_snapshot(self) -> SystemSnapshot:
        """Create a complete snapshot of system state for rollback."""
        return SystemSnapshot(
            warehouse_inventories={wh_id: inv.copy() for wh_id, inv in self.warehouse_inventories.items()},
            vehicle_loads={v_id: load.copy() for v_id, load in self.vehicle_loads.items()},
            vehicle_capacities=self.vehicle_capacities.copy(),
            order_deliveries={o_id: del_items.copy() for o_id, del_items in self.order_deliveries.items()}
        )
    
    def restore_snapshot(self, snapshot: SystemSnapshot):
        """Restore system state from snapshot and sync original objects."""
        self.warehouse_inventories = {wh_id: inv.copy() for wh_id, inv in snapshot.warehouse_inventories.items()}
        self.vehicle_loads = {v_id: load.copy() for v_id, load in snapshot.vehicle_loads.items()}
        self.vehicle_capacities = snapshot.vehicle_capacities.copy()
        self.order_deliveries = {o_id: del_items.copy() for o_id, del_items in snapshot.order_deliveries.items()}
        
        for wh_id, inventory in self.warehouse_inventories.items():
            if wh_id in self.warehouses:
                self.warehouses[wh_id].inventory = inventory.copy()
        
        for order_id, deliveries in self.order_deliveries.items():
            if order_id in self.orders:
                order = self.orders[order_id]
                if deliveries:
                    order._delivered_items = deliveries.copy()
                elif hasattr(order, '_delivered_items'):
                    delattr(order, '_delivered_items')
    
    def get_warehouse_inventory(self, warehouse_id: str, sku_id: str) -> int:
        """Get current warehouse inventory for a SKU."""
        return self.warehouse_inventories.get(warehouse_id, {}).get(sku_id, 0)
    
    def get_vehicle_load(self, vehicle_id: str, sku_id: str) -> int:
        """Get current vehicle load for a SKU."""
        return self.vehicle_loads.get(vehicle_id, {}).get(sku_id, 0)
    
    def get_vehicle_capacity_usage(self, vehicle_id: str) -> Tuple[float, float]:
        """Get current vehicle capacity usage (weight, volume)."""
        return self.vehicle_capacities.get(vehicle_id, (0.0, 0.0))
    
    def get_order_delivered(self, order_id: str, sku_id: str) -> int:
        """Get amount already delivered for an order."""
        return self.order_deliveries.get(order_id, {}).get(sku_id, 0)
    
    def validate_pickup_operation(self, vehicle_id: str, warehouse_id: str, 
                                  sku_id: str, quantity: int) -> Tuple[bool, str]:
        """Validate if a pickup operation is feasible."""
        available = self.get_warehouse_inventory(warehouse_id, sku_id)
        if available < quantity:
            return False, f"Insufficient inventory: need {quantity}, have {available}"
        
        if vehicle_id not in self.vehicles:
            return False, f"Vehicle {vehicle_id} not found"
        
        vehicle = self.vehicles[vehicle_id]
        sku = self.skus.get(sku_id)
        if not sku:
            return False, f"SKU {sku_id} not found"
        
        current_weight, current_volume = self.get_vehicle_capacity_usage(vehicle_id)
        additional_weight = sku.weight * quantity
        additional_volume = sku.volume * quantity
        
        if current_weight + additional_weight > vehicle.capacity_weight:
            return False, f"Weight capacity exceeded: {current_weight + additional_weight:.1f} > {vehicle.capacity_weight}"
        
        if current_volume + additional_volume > vehicle.capacity_volume:
            return False, f"Volume capacity exceeded: {current_volume + additional_volume:.3f} > {vehicle.capacity_volume}"
        
        return True, "Pickup operation is valid"
    
    def validate_delivery_operation(self, vehicle_id: str, order_id: str, 
                                    sku_id: str, quantity: int) -> Tuple[bool, str]:
        """Validate if a delivery operation is feasible."""
        vehicle_load = self.get_vehicle_load(vehicle_id, sku_id)
        if vehicle_load < quantity:
            return False, f"Vehicle doesn't have enough {sku_id}: need {quantity}, have {vehicle_load}"
        
        if order_id not in self.orders:
            return False, f"Order {order_id} not found"
        
        order = self.orders[order_id]
        if sku_id not in order.requested_items:
            return False, f"Order {order_id} doesn't need SKU {sku_id}"
        
        return True, "Delivery operation is valid"
    
    def execute_pickup(self, vehicle_id: str, warehouse_id: str, 
                       sku_id: str, quantity: int) -> Tuple[bool, str]:
        """Execute a pickup operation (ATOMIC)."""
        is_valid, msg = self.validate_pickup_operation(vehicle_id, warehouse_id, sku_id, quantity)
        if not is_valid:
            return False, msg
        
        sku = self.skus[sku_id]
        
        if warehouse_id not in self.warehouse_inventories:
            self.warehouse_inventories[warehouse_id] = {}
        self.warehouse_inventories[warehouse_id][sku_id] -= quantity
        
        warehouse = self.warehouses[warehouse_id]
        warehouse.inventory[sku_id] -= quantity
        
        if vehicle_id not in self.vehicle_loads:
            self.vehicle_loads[vehicle_id] = {}
        self.vehicle_loads[vehicle_id][sku_id] = self.vehicle_loads[vehicle_id].get(sku_id, 0) + quantity
        
        current_weight, current_volume = self.vehicle_capacities[vehicle_id]
        self.vehicle_capacities[vehicle_id] = (
            current_weight + sku.weight * quantity,
            current_volume + sku.volume * quantity
        )
        
        return True, f"Picked up {quantity} {sku_id} from {warehouse_id}"
    
    def execute_delivery(self, vehicle_id: str, order_id: str, 
                         sku_id: str, quantity: int) -> Tuple[bool, str]:
        """Execute a delivery operation (ATOMIC)."""
        is_valid, msg = self.validate_delivery_operation(vehicle_id, order_id, sku_id, quantity)
        if not is_valid:
            return False, msg
        
        sku = self.skus[sku_id]
        
        self.vehicle_loads[vehicle_id][sku_id] -= quantity
        if self.vehicle_loads[vehicle_id][sku_id] <= 0:
            del self.vehicle_loads[vehicle_id][sku_id]
        
        current_weight, current_volume = self.vehicle_capacities[vehicle_id]
        self.vehicle_capacities[vehicle_id] = (
            current_weight - sku.weight * quantity,
            current_volume - sku.volume * quantity
        )
        
        if order_id not in self.order_deliveries:
            self.order_deliveries[order_id] = {}
        self.order_deliveries[order_id][sku_id] = self.order_deliveries[order_id].get(sku_id, 0) + quantity
        
        order = self.orders[order_id]
        if not hasattr(order, '_delivered_items'):
            order._delivered_items = {}
        if sku_id not in order._delivered_items:
            order._delivered_items[sku_id] = 0
        order._delivered_items[sku_id] += quantity
        
        return True, f"Delivered {quantity} {sku_id} to {order_id}"
    
    def execute_unload(self, vehicle_id: str, warehouse_id: str, 
                       sku_id: str, quantity: int) -> Tuple[bool, str]:
        """Execute an unload operation (ATOMIC)."""
        vehicle_load = self.get_vehicle_load(vehicle_id, sku_id)
        if vehicle_load < quantity:
            return False, f"Vehicle doesn't have enough {sku_id}: need {quantity}, have {vehicle_load}"
        
        if warehouse_id not in self.warehouses:
            return False, f"Warehouse {warehouse_id} not found"
        
        sku = self.skus[sku_id]
        
        self.vehicle_loads[vehicle_id][sku_id] -= quantity
        if self.vehicle_loads[vehicle_id][sku_id] <= 0:
            del self.vehicle_loads[vehicle_id][sku_id]
        
        current_weight, current_volume = self.vehicle_capacities[vehicle_id]
        self.vehicle_capacities[vehicle_id] = (
            current_weight - sku.weight * quantity,
            current_volume - sku.volume * quantity
        )
        
        if warehouse_id not in self.warehouse_inventories:
            self.warehouse_inventories[warehouse_id] = {}
        self.warehouse_inventories[warehouse_id][sku_id] = self.warehouse_inventories[warehouse_id].get(sku_id, 0) + quantity
        
        warehouse = self.warehouses[warehouse_id]
        warehouse.inventory[sku_id] = warehouse.inventory.get(sku_id, 0) + quantity
        
        return True, f"Unloaded {quantity} {sku_id} to {warehouse_id}"
    
    def execute_route_operations(self, vehicle_id: str, pickup_operations: List[Dict], 
                                 delivery_operations: List[Dict]) -> Tuple[bool, str]:
        """Execute a complete route atomically with rollback on failure."""
        snapshot = self.create_snapshot()
        
        try:
            for pickup in pickup_operations:
                success, msg = self.execute_pickup(
                    vehicle_id, pickup['warehouse_id'], pickup['sku_id'], pickup['quantity']
                )
                if not success:
                    self.restore_snapshot(snapshot)
                    return False, f"Pickup failed: {msg}"
            
            for delivery in delivery_operations:
                success, msg = self.execute_delivery(
                    vehicle_id, delivery['order_id'], delivery['sku_id'], delivery['quantity']
                )
                if not success:
                    self.restore_snapshot(snapshot)
                    return False, f"Delivery failed: {msg}"
            
            return True, f"Route executed successfully for vehicle {vehicle_id}"
            
        except Exception as e:
            self.restore_snapshot(snapshot)
            return False, f"Route execution error: {e}"
    
    def reset_vehicle(self, vehicle_id: str):
        """Reset vehicle to empty state at home warehouse."""
        self.vehicle_loads[vehicle_id] = {}
        self.vehicle_capacities[vehicle_id] = (0.0, 0.0)
    
    def reset_all_vehicles(self):
        """Reset all vehicles to empty state."""
        for vehicle_id in self.vehicle_loads:
            self.reset_vehicle(vehicle_id)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get complete summary of system state."""
        return {
            'warehouse_inventories': self.warehouse_inventories,
            'vehicle_loads': self.vehicle_loads,
            'vehicle_capacities': self.vehicle_capacities,
            'order_deliveries': self.order_deliveries,
            'total_vehicles': len(self.vehicles),
            'total_warehouses': len(self.warehouses),
            'total_orders': len(self.orders)
        }
