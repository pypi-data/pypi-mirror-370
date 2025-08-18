"""Operational parameters for the multi-depot problem instance."""

WAREHOUSE_LOCATIONS = [
    {"id": "WH-1", "lat": 30.0925398, "lon": 31.3154756, "name": "Main Distribution Center"},
    {"id": "WH-2", "lat": 30.1105703, "lon": 31.3699689, "name": "Secondary Hub"},
    {"id": "WH-3", "lat": 30.103577, "lon": 31.3479518, "name": "Regional Warehouse"}
]

VEHICLE_FLEET_SPECS = [
    {
        "type": "LightVan",
        "name": "Light Delivery Van",
        "capacity_weight_kg": 800,
        "capacity_volume_m3": 6.0,
        "max_distance_km": 300,
        "cost_per_km": 0.5,
        "fixed_cost": 50,
        "description": "Small van for local deliveries"
    },
    {
        "type": "MediumTruck",
        "name": "Medium Cargo Truck",
        "capacity_weight_kg": 2000,
        "capacity_volume_m3": 15.0,
        "max_distance_km": 500,
        "cost_per_km": 0.8,
        "fixed_cost": 100,
        "description": "Standard truck for medium loads"
    },
    {
        "type": "HeavyTruck",
        "name": "Heavy Cargo Truck",
        "capacity_weight_kg": 5000,
        "capacity_volume_m3": 40.0,
        "max_distance_km": 800,
        "cost_per_km": 1.2,
        "fixed_cost": 200,
        "description": "Large truck for heavy loads"
    }
]

SKU_DEFINITIONS = [
    {
        'sku_id': 'Light_Item',
        'weight_kg': 5.0,
        'volume_m3': 0.02
    },
    {
        'sku_id': 'Medium_Item',
        'weight_kg': 15.0,
        'volume_m3': 0.06
    },
    {
        'sku_id': 'Heavy_Item',
        'weight_kg': 30.0,
        'volume_m3': 0.12
    }
]

DEFAULT_SETTINGS = {
    'num_orders': 15,
    'num_warehouses': 2,
    'default_sku_distribution': [33, 33, 34],
    'default_vehicle_counts': {
        'LightVan': 2,
        'MediumTruck': 1,
        'HeavyTruck': 0
    },
    'min_items_per_order': 1,
    'max_items_per_order': 50,
    'max_orders': 50,
    'map_zoom_start': 10,
    'max_vehicles_per_warehouse': 10,
    'random_seed': None,
    'distance_control': {
        'radius_km': 15,
        'density_strategy': 'clustered',
        'clustering_factor': 0.7,
        'ring_count': 3,
        'min_node_distance': 0.5,
        'max_orders_per_km2': 0.1
    }
}

DEFAULT_WAREHOUSE_SKU_ALLOCATIONS = [
    [50, 50, 50],
    [50, 50, 50],
    [0, 0, 0]
]
