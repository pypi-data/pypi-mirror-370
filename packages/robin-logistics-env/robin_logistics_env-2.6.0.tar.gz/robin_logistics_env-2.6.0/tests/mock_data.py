"""Mock data generation for testing without solver dependency."""

import pandas as pd
from robin_logistics.core.models import Node, SKU, Order, Vehicle, Warehouse


def create_mock_nodes():
    """Create mock road network nodes."""
    nodes_data = [
        {'node_id': 1, 'lat': 30.0925398, 'lon': 31.3154756},  # Warehouse 1
        {'node_id': 2, 'lat': 30.1105703, 'lon': 31.3699689},  # Warehouse 2  
        {'node_id': 3, 'lat': 30.103577, 'lon': 31.3479518},   # Order 1
        {'node_id': 4, 'lat': 30.095, 'lon': 31.325},          # Order 2
        {'node_id': 5, 'lat': 30.108, 'lon': 31.355},          # Order 3
    ]
    return pd.DataFrame(nodes_data)


def create_mock_edges():
    """Create mock road network edges."""
    edges_data = [
        {'start_node': 1, 'end_node': 2, 'distance_km': 5.2},
        {'start_node': 1, 'end_node': 3, 'distance_km': 3.1},
        {'start_node': 1, 'end_node': 4, 'distance_km': 2.8},
        {'start_node': 2, 'end_node': 1, 'distance_km': 5.2},
        {'start_node': 2, 'end_node': 3, 'distance_km': 4.5},
        {'start_node': 2, 'end_node': 5, 'distance_km': 2.1},
        {'start_node': 3, 'end_node': 1, 'distance_km': 3.1},
        {'start_node': 3, 'end_node': 2, 'distance_km': 4.5},
        {'start_node': 3, 'end_node': 4, 'distance_km': 1.5},
        {'start_node': 3, 'end_node': 5, 'distance_km': 3.2},
        {'start_node': 4, 'end_node': 1, 'distance_km': 2.8},
        {'start_node': 4, 'end_node': 2, 'distance_km': 4.0},
        {'start_node': 4, 'end_node': 3, 'distance_km': 1.5},
        {'start_node': 5, 'end_node': 1, 'distance_km': 3.5},
        {'start_node': 5, 'end_node': 2, 'distance_km': 2.1},
        {'start_node': 5, 'end_node': 3, 'distance_km': 3.2},
    ]
    return pd.DataFrame(edges_data)


def create_mock_skus():
    """Create mock SKU objects."""
    return [
        SKU('Light_Item', 5.0, 0.02),   # 5kg, 0.02m³
        SKU('Medium_Item', 15.0, 0.06), # 15kg, 0.06m³  
        SKU('Heavy_Item', 30.0, 0.12),  # 30kg, 0.12m³
    ]


def create_mock_warehouses(nodes_df):
    """Create mock warehouse objects."""
    # Create warehouse locations
    wh1_node = Node(1, 30.0925398, 31.3154756)
    wh2_node = Node(2, 30.1105703, 31.3699689)
    
    # Create warehouses
    wh1 = Warehouse('WH-1', wh1_node)
    wh2 = Warehouse('WH-2', wh2_node)
    
    # Set initial inventory
    wh1.inventory = {
        'Light_Item': 100,
        'Medium_Item': 80,
        'Heavy_Item': 50
    }
    
    wh2.inventory = {
        'Light_Item': 80,
        'Medium_Item': 60,
        'Heavy_Item': 40
    }
    
    return [wh1, wh2]


def create_mock_vehicles(warehouses):
    """Create mock vehicle objects."""
    vehicles = []
    
    # Vehicles for WH-1
    vehicles.append(Vehicle('LightVan_WH-1_1', 'LightVan', 'WH-1',
                           capacity_weight_kg=800, capacity_volume_m3=6.0,
                           max_distance_km=300, cost_per_km=0.5, fixed_cost=50))
    
    vehicles.append(Vehicle('MediumTruck_WH-1_1', 'MediumTruck', 'WH-1',
                           capacity_weight_kg=2000, capacity_volume_m3=15.0,
                           max_distance_km=500, cost_per_km=0.8, fixed_cost=100))
    
    # Vehicles for WH-2
    vehicles.append(Vehicle('LightVan_WH-2_1', 'LightVan', 'WH-2',
                           capacity_weight_kg=800, capacity_volume_m3=6.0,
                           max_distance_km=300, cost_per_km=0.5, fixed_cost=50))
    
    # Assign vehicles to warehouses
    warehouses[0].vehicles = [vehicles[0], vehicles[1]]  # WH-1
    warehouses[1].vehicles = [vehicles[2]]               # WH-2
    
    return vehicles


def create_mock_orders():
    """Create mock order objects."""
    orders = []
    
    # Order 1 - to node 3
    order1 = Order('ORD-1', Node(3, 30.103577, 31.3479518))
    order1.requested_items = {
        'Light_Item': 5,
        'Medium_Item': 3
    }
    orders.append(order1)
    
    # Order 2 - to node 4  
    order2 = Order('ORD-2', Node(4, 30.095, 31.325))
    order2.requested_items = {
        'Medium_Item': 8,
        'Heavy_Item': 2
    }
    orders.append(order2)
    
    # Order 3 - to node 5
    order3 = Order('ORD-3', Node(5, 30.108, 31.355))
    order3.requested_items = {
        'Light_Item': 10,
        'Heavy_Item': 1
    }
    orders.append(order3)
    
    return orders


def create_mock_environment():
    """Create a complete mock environment for testing."""
    from robin_logistics import LogisticsEnvironment
    
    # Create mock data
    nodes_df = create_mock_nodes()
    edges_df = create_mock_edges()
    warehouses = create_mock_warehouses(nodes_df)
    orders = create_mock_orders()
    skus = create_mock_skus()
    vehicles = create_mock_vehicles(warehouses)
    
    # Create environment with mock data
    env = LogisticsEnvironment()
    
    # Replace environment data with mock data
    env.nodes = {node.id: node for node in [Node(row['node_id'], row['lat'], row['lon']) for _, row in nodes_df.iterrows()]}
    env.warehouses = {wh.id: wh for wh in warehouses}
    env.orders = {order.id: order for order in orders}
    env.skus = {sku.id: sku for sku in skus}
    
    # Reinitialize network manager and orchestrator with mock data
    env.network_manager = env.network_manager.__class__(env.nodes, edges_df)
    env.orchestrator = env.orchestrator.__class__(
        warehouses=env.warehouses,
        vehicles=vehicles,
        orders=env.orders,
        skus=env.skus
    )
    
    # Reinitialize validator and metrics calculator
    vehicles_dict = {v.id: v for v in vehicles}
    env.validator = env.validator.__class__(
        env.warehouses, vehicles_dict, env.orders, env.skus, env.network_manager
    )
    env.metrics_calculator = env.metrics_calculator.__class__(
        env.warehouses, vehicles_dict, env.orders, env.skus, env.network_manager
    )
    
    return env


def create_mock_solution():
    """Create a mock solution for testing validation."""
    return {
        'routes': [
            {
                'vehicle_id': 'LightVan_WH-1_1',
                'route': [1, 3, 4, 1],  # WH-1 -> Order1 -> Order2 -> WH-1
                'distance': 8.9,
                'pickup_operations': [
                    {'warehouse_id': 'WH-1', 'sku_id': 'Light_Item', 'quantity': 5},
                    {'warehouse_id': 'WH-1', 'sku_id': 'Medium_Item', 'quantity': 11}
                ],
                'delivery_operations': [
                    {'order_id': 'ORD-1', 'sku_id': 'Light_Item', 'quantity': 5},
                    {'order_id': 'ORD-1', 'sku_id': 'Medium_Item', 'quantity': 3},
                    {'order_id': 'ORD-2', 'sku_id': 'Medium_Item', 'quantity': 8}
                ]
            },
            {
                'vehicle_id': 'MediumTruck_WH-1_1', 
                'route': [1, 4, 2, 5, 1],  # WH-1 -> Order2 -> WH-2 -> Order3 -> WH-1
                'distance': 12.6,
                'pickup_operations': [
                    {'warehouse_id': 'WH-1', 'sku_id': 'Heavy_Item', 'quantity': 2},
                    {'warehouse_id': 'WH-2', 'sku_id': 'Light_Item', 'quantity': 10},
                    {'warehouse_id': 'WH-2', 'sku_id': 'Heavy_Item', 'quantity': 1}
                ],
                'delivery_operations': [
                    {'order_id': 'ORD-2', 'sku_id': 'Heavy_Item', 'quantity': 2},
                    {'order_id': 'ORD-3', 'sku_id': 'Light_Item', 'quantity': 10},
                    {'order_id': 'ORD-3', 'sku_id': 'Heavy_Item', 'quantity': 1}
                ]
            }
        ]
    }


def create_invalid_solution():
    """Create an invalid solution for testing validation."""
    return {
        'routes': [
            {
                'vehicle_id': 'LightVan_WH-1_1',
                'route': [1, 3, 6, 1],  # Invalid: node 6 doesn't exist
                'distance': 10.0,
                'pickup_operations': [],
                'delivery_operations': []
            }
        ]
    }
