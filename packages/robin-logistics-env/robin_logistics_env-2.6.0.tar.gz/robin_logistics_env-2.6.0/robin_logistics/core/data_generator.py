"""Data generation utilities for the multi-depot vehicle routing problem."""

import random
import pandas as pd
import os
from .models.node import Node
from .models.sku import SKU
from .models.order import Order
from .models.vehicle import Vehicle
from .models.warehouse import Warehouse
from . import config

def generate_problem_instance():
    """
    Generate a default problem instance using default configuration.

    Returns:
        tuple: (nodes_df, edges_df, warehouses, orders, skus, vehicles)
    """
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
    edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))

    default_config = {
        'num_orders': config.DEFAULT_SETTINGS['num_orders'],
        'num_warehouses': config.DEFAULT_SETTINGS['num_warehouses'],
        'sku_percentages': config.DEFAULT_SETTINGS['default_sku_distribution'],
        'warehouse_configs': [
            {
                'vehicle_counts': config.DEFAULT_SETTINGS['default_vehicle_counts'],
                'sku_inventory_percentages': config.DEFAULT_WAREHOUSE_SKU_ALLOCATIONS[0]
            },
            {
                'vehicle_counts': config.DEFAULT_SETTINGS['default_vehicle_counts'],
                'sku_inventory_percentages': config.DEFAULT_WAREHOUSE_SKU_ALLOCATIONS[1]
            }
        ],
        'distance_control': config.DEFAULT_SETTINGS['distance_control']
    }

    problem_data = generate_scenario_from_config(config, nodes_df, edges_df, default_config)

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

    return nodes_df_final, edges_df_final, warehouses, orders, skus, all_vehicles

from .utils.distance import DistanceUtils

def _generate_orders_with_distance_control(custom_config, warehouses, skus, all_node_ids, nodes_df):
    """Generate orders with sophisticated distance control and density management."""
    orders = []
    num_orders = custom_config.get('num_orders', 15)
    min_items = custom_config.get('min_items_per_order', 3)
    max_items = custom_config.get('max_items_per_order', 8)

    distance_config = custom_config.get('distance_control', {})
    radius_km = distance_config.get('radius_km', 50)
    density_strategy = distance_config.get('density_strategy', 'clustered')
    clustering_factor = distance_config.get('clustering_factor', 0.7)
    ring_count = distance_config.get('ring_count', 3)

    centroid_lat, centroid_lon = calculate_warehouse_centroid(warehouses)

    available_nodes = filter_nodes_by_circle(nodes_df, centroid_lat, centroid_lon, radius_km)

    if len(available_nodes) < num_orders:
        adjusted_orders = len(available_nodes)
        num_orders = adjusted_orders

    if num_orders == 0:
        return orders, {
            'requested_orders': custom_config.get('num_orders', 15),
            'actual_orders': 0,
            'distance_constraint': radius_km,
            'nodes_within_range': 0,
            'constraint_respected': False,
            'centroid': (centroid_lat, centroid_lon)
        }

    selected_nodes = generate_orders_with_density_control(
        available_nodes, num_orders, density_strategy, clustering_factor, ring_count
    )

    for i, node_info in enumerate(selected_nodes):
        dest_node = Node(int(node_info['node_id']), float(node_info['lat']), float(node_info['lon']))
        order = Order(f"ORD-{i+1}", dest_node)

        num_skus = random.randint(min_items, max_items)
        selected_skus = random.sample(skus, min(num_skus, len(skus)))

        sku_percentages = custom_config.get('sku_percentages', [33.33, 33.33, 33.34])

        for j, sku in enumerate(selected_skus):
            if j < len(sku_percentages):
                base_quantity = int(sku_percentages[j] / 10)
                if base_quantity <= 0:
                    quantity = 0
                else:
                    quantity = random.randint(base_quantity, base_quantity * 2)
                if quantity > 0:
                    order.requested_items[sku.id] = quantity

        orders.append(order)

    generation_metadata = {
        'requested_orders': custom_config.get('num_orders', 15),
        'actual_orders': len(orders),
        'distance_constraint': radius_km,
        'nodes_within_range': len(available_nodes),
        'constraint_respected': len(orders) == custom_config.get('num_orders', 15),
        'centroid': (centroid_lat, centroid_lon),
        'density_strategy': density_strategy,
        'clustering_factor': clustering_factor,
        'ring_count': ring_count
    }

    return orders, generation_metadata

def calculate_warehouse_centroid(warehouses):
    """Calculate the geographic centroid of selected warehouses."""
    if not warehouses:
        raise ValueError("No warehouses specified")

    total_lat = 0
    total_lon = 0
    total_weight = 0

    for warehouse in warehouses:
        weight = len(warehouse.vehicles)
        total_lat += warehouse.location.lat * weight
        total_lon += warehouse.location.lon * weight
        total_weight += weight

    if total_weight == 0:
        centroid_lat = sum(w.location.lat for w in warehouses) / len(warehouses)
        centroid_lon = sum(w.location.lon for w in warehouses) / len(warehouses)
    else:
        centroid_lat = total_lat / total_weight
        centroid_lon = total_lon / total_weight

    return centroid_lat, centroid_lon

def filter_nodes_by_circle(nodes_df, centroid_lat, centroid_lon, radius_km):
    """Filter nodes within specified radius of centroid."""
    available_nodes = []

    for _, node_row in nodes_df.iterrows():
        node_lat, node_lon = node_row['lat'], node_row['lon']

        distance = DistanceUtils.haversine_km(node_lat, node_lon, centroid_lat, centroid_lon)

        if distance <= radius_km:
            available_nodes.append({
                'node_id': node_row['node_id'],
                'lat': node_lat,
                'lon': node_lon,
                'distance_from_centroid': distance
            })

    return available_nodes

def generate_orders_with_density_control(available_nodes, num_orders, density_strategy, clustering_factor, ring_count):
    """Generate orders with controlled geographic density."""

    if len(available_nodes) < num_orders:
        return available_nodes

    if density_strategy == 'uniform':
        return uniform_distribution(available_nodes, num_orders)
    elif density_strategy == 'clustered':
        return clustered_distribution(available_nodes, num_orders, clustering_factor)
    elif density_strategy == 'ring_based':
        return ring_based_distribution(available_nodes, num_orders, ring_count)
    else:
        return uniform_distribution(available_nodes, num_orders)

def uniform_distribution(available_nodes, num_orders):
    """Uniform distribution across available nodes."""
    return random.sample(available_nodes, num_orders)

def clustered_distribution(available_nodes, num_orders, clustering_factor=0.7):
    """Clustered distribution with more orders near centroid."""
    weights = [1 / (node['distance_from_centroid'] + 0.1) for node in available_nodes]

    adjusted_weights = [w ** (1 + clustering_factor) for w in weights]

    total_weight = sum(adjusted_weights)
    normalized_weights = [w / total_weight for w in adjusted_weights]

    import numpy as np
    try:
        selected_indices = np.random.choice(len(available_nodes), num_orders, p=normalized_weights, replace=False)
        return [available_nodes[i] for i in selected_indices]
    except ImportError:
        return random.sample(available_nodes, num_orders)

def ring_based_distribution(available_nodes, num_orders, ring_count=3):
    """Distribute orders in concentric rings around centroid."""
    if ring_count > num_orders:
        ring_count = num_orders

    max_distance = max(node['distance_from_centroid'] for node in available_nodes)
    ring_boundaries = [max_distance * i / ring_count for i in range(ring_count + 1)]

    ring_nodes = [[] for _ in range(ring_count)]
    for node in available_nodes:
        for i in range(ring_count):
            if ring_boundaries[i] <= node['distance_from_centroid'] < ring_boundaries[i + 1]:
                ring_nodes[i].append(node)
                break

    orders_per_ring = num_orders // ring_count
    remaining_orders = num_orders % ring_count

    selected_nodes = []
    for i, ring in enumerate(ring_nodes):
        orders_in_ring = orders_per_ring + (1 if i < remaining_orders else 0)
        if orders_in_ring > 0 and ring:
            selected = random.sample(ring, min(orders_in_ring, len(ring)))
            selected_nodes.extend(selected)

    return selected_nodes

def generate_scenario_from_config(base_config, nodes_df_raw, edges_df_raw, custom_config):
    """Generate problem instance from dashboard configuration."""

    random_seed = custom_config.get('random_seed')
    if random_seed is not None:
        random.seed(random_seed)
        try:
            import numpy as np
            np.random.seed(random_seed)
        except ImportError:
            pass

    nodes_df = nodes_df_raw.copy()
    nodes_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)

    all_node_ids = set(nodes_df['node_id'].tolist())

    existing_edges = []
    if edges_df_raw is not None and not edges_df_raw.empty:
        edges_df = edges_df_raw.copy()

        if 'u' in edges_df.columns and 'v' in edges_df.columns:
            edges_df.rename(columns={'u': 'start_node', 'v': 'end_node'}, inplace=True)

        for _, edge in edges_df.iterrows():
            start_node = int(edge['start_node'])
            end_node = int(edge['end_node'])

            if 'length' in edges_df.columns:
                distance_km = float(edge['length']) / 1000
            elif 'distance_km' in edges_df.columns:
                distance_km = float(edge['distance_km'])
            else:
                if start_node in nodes_df['node_id'].values and end_node in nodes_df['node_id'].values:
                    start_row = nodes_df[nodes_df['node_id'] == start_node].iloc[0]
                    end_row = nodes_df[nodes_df['node_id'] == end_node].iloc[0]
                    distance_km = DistanceUtils.haversine_km(start_row['lat'], start_row['lon'],
                                                     end_row['lat'], end_row['lon'])
                else:
                    continue

            existing_edges.append({
                'start_node': start_node,
                'end_node': end_node,
                'distance_km': distance_km
            })

    outgoing_node_ids = set()
    incoming_node_ids = set()
    for edge in existing_edges:
        outgoing_node_ids.add(edge['start_node'])
        incoming_node_ids.add(edge['end_node'])
    bidirectional_candidate_nodes = outgoing_node_ids.intersection(incoming_node_ids)

    all_edges = existing_edges

    nodes_df_final = nodes_df[['node_id', 'lat', 'lon']].copy()
    edges_df_final = pd.DataFrame(all_edges)

    nodes = []
    for _, row in nodes_df_final.iterrows():
        nodes.append(Node(int(row['node_id']), float(row['lat']), float(row['lon'])))

    skus = []
    for s in base_config.SKU_DEFINITIONS:
        try:
            sku = SKU(
                sku_id=s['sku_id'],
                weight_kg=s['weight_kg'],
                volume_m3=s['volume_m3']
            )
            skus.append(sku)
        except Exception:
            continue

    warehouses = []
    num_warehouses = custom_config.get('num_warehouses', len(base_config.WAREHOUSE_LOCATIONS))
    num_warehouses_to_use = min(num_warehouses, len(base_config.WAREHOUSE_LOCATIONS))

    used_nodes = set()

    for i in range(num_warehouses_to_use):
        wh_id = base_config.WAREHOUSE_LOCATIONS[i]['id']
        wh_lat = base_config.WAREHOUSE_LOCATIONS[i]['lat']
        wh_lon = base_config.WAREHOUSE_LOCATIONS[i]['lon']

        closest_node = None
        min_distance = float('inf')

        for node in nodes:
            if node.id in used_nodes:
                continue
            if node.id not in bidirectional_candidate_nodes:
                continue

            distance = DistanceUtils.haversine_km(wh_lat, wh_lon, node.lat, node.lon)
            if distance < min_distance:
                min_distance = distance
                closest_node = node

        if closest_node:
            wh = Warehouse(wh_id, closest_node)
            used_nodes.add(closest_node.id)

            if i < len(custom_config.get('warehouse_configs', [])):
                warehouse_config = custom_config['warehouse_configs'][i]
                vehicle_counts = warehouse_config.get('vehicle_counts', {})
            else:
                vehicle_counts = base_config.DEFAULT_SETTINGS.get('default_vehicle_counts', {})

            for vehicle_type, count in vehicle_counts.items():
                vehicle_specs = None
                for spec in base_config.VEHICLE_FLEET_SPECS:
                    if spec['type'] == vehicle_type:
                        vehicle_specs = spec
                        break

                if vehicle_specs:
                    for j in range(count):
                        v_id = f"{vehicle_type}_{wh_id}_{j+1}"
                        try:
                            vehicle = Vehicle(v_id, vehicle_type, wh_id, **vehicle_specs)
                            wh.vehicles.append(vehicle)
                        except Exception:
                            continue

            warehouses.append(wh)

    orders, generation_metadata = _generate_orders_with_distance_control(
        custom_config, warehouses, skus, bidirectional_candidate_nodes, nodes_df
    )

    if 'warehouse_configs' in custom_config:
        for i, warehouse_config in enumerate(custom_config['warehouse_configs']):
            if i >= len(warehouses):
                break

            warehouse = warehouses[i]
            if 'sku_inventory_percentages' in warehouse_config:
                actual_sku_demand = {}
                for order in orders:
                    for sku_id, quantity in order.requested_items.items():
                        if sku_id not in actual_sku_demand:
                            actual_sku_demand[sku_id] = 0
                        actual_sku_demand[sku_id] += quantity

                for j, sku in enumerate(skus):
                    if j < len(warehouse_config['sku_inventory_percentages']):
                        warehouse_supply_percentage = warehouse_config['sku_inventory_percentages'][j]

                        actual_demand = actual_sku_demand.get(sku.id, 0)

                        warehouse_inventory = (warehouse_supply_percentage / 100.0) * actual_demand

                        warehouse.inventory[sku.id] = max(0, int(round(warehouse_inventory)))
                    else:
                        warehouse.inventory[sku.id] = 0
            else:
                for sku in skus:
                    warehouse.inventory[sku.id] = 50

    return {
        'nodes': nodes,
        'edges_df': edges_df_final,
        'warehouses': warehouses,
        'orders': (orders, generation_metadata),
        'skus': skus
    }