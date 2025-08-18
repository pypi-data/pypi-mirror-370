
class Vehicle:
    """Represents a single delivery vehicle with dynamic state."""

    def __init__(self, vehicle_id, v_type, home_warehouse_id, **kwargs):
        """
        Initialize a Vehicle.

        Args:
            vehicle_id: Unique identifier for the vehicle
            v_type: Type/category of the vehicle
            home_warehouse_id: ID of the warehouse where the vehicle is based
            **kwargs: Additional vehicle specifications
        """
        self.id = vehicle_id
        self.type = v_type
        self.home_warehouse_id = home_warehouse_id
        self.capacity_weight = float(kwargs['capacity_weight_kg'])
        self.capacity_volume = float(kwargs['capacity_volume_m3'])
        self.max_distance = float(kwargs['max_distance_km'])
        self.cost_per_km = float(kwargs['cost_per_km'])
        self.fixed_cost = float(kwargs['fixed_cost'])

    def __repr__(self):
        return f"Vehicle({self.id} from {self.home_warehouse_id})"