"""Operational parameters for the multi-depot problem instance."""

WAREHOUSE_LOCATIONS = [
    {"id": "WH-1", "lat": 30.0925398, "lon": 31.3154756, "name": "Main Distribution Center"},
    {"id": "WH-2", "lat": 30.1105703, "lon": 31.3699689, "name": "Secondary Hub"},
    {"id": "WH-3", "lat": 30.103577, "lon": 31.3479518, "name": "Regional Warehouse"}
    # {"id": "WH-1", "lat": 31.2165913, "lon": 29.971778, "name": "Main Distribution Center"},
    # {"id": "WH-2", "lat": 30.964521, "lon": 29.888109, "name": "Secondary Hub"},
    # {"id": "WH-3", "lat": 31.1732091, "lon": 30.1538759, "name": "Regional Warehouse"}
]

VEHICLE_FLEET_SPECS = [
    {
        "type": "LightVan",
        "name": "Light Delivery Van",
        "capacity_weight_kg": 800,
        "capacity_volume_m3": 3.0,
        "max_distance_km": 100,
        "cost_per_km": 1,
        "fixed_cost": 300,
        "description": "Small van for local deliveries"
    },
    {
        "type": "MediumTruck",
        "name": "Medium Cargo Truck",
        "capacity_weight_kg": 1600,
        "capacity_volume_m3": 5.0,
        "max_distance_km": 150,
        "cost_per_km": 1.25,
        "fixed_cost": 625,
        "description": "Standard truck for medium loads"
    },
    {
        "type": "HeavyTruck",
        "name": "Heavy Cargo Truck",
        "capacity_weight_kg": 5000,
        "capacity_volume_m3": 12.0,
        "max_distance_km": 200,
        "cost_per_km": 1.5,
        "fixed_cost": 1200,
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
    'num_orders': 50,
    'num_warehouses': 2,
    'default_sku_distribution': [33, 33, 34],
    'default_vehicle_counts': {
        'LightVan': 3,
        'MediumTruck': 2,
        'HeavyTruck': 1
    },
    'min_items_per_order': 1,
    'max_items_per_order': 50,
    'max_orders': 500,
    'map_zoom_start': 10,
    'max_vehicles_per_warehouse': 50,
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
