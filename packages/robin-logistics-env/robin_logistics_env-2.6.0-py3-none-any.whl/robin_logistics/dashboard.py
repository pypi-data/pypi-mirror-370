"""Dashboard interface for the Robin Logistics Environment."""

import streamlit as st
import pandas as pd
import folium
import os
import traceback
from robin_logistics.core import config as config_module
from robin_logistics import LogisticsEnvironment
from robin_logistics.core.data_generator import generate_scenario_from_config
from robin_logistics.core.config import (
    SKU_DEFINITIONS,
    WAREHOUSE_LOCATIONS,
    VEHICLE_FLEET_SPECS,
    DEFAULT_SETTINGS,
    DEFAULT_WAREHOUSE_SKU_ALLOCATIONS
)

def main():
    """Main dashboard entry point."""
    try:
        env = LogisticsEnvironment()
    except Exception as e:
        st.error(f"Failed to create environment: {e}")
        st.info("Make sure you're running from the project root directory")
        return

    run_dashboard(env)

def run_dashboard(env, solver_function=None):
    """Main dashboard function."""
    st.set_page_config(
        page_title="Robin Logistics Environment",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    col1, col2 = st.columns([2, 6])

    with col1:
        logo_path = os.path.join(os.path.dirname(__file__), "Robin colored logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
        else:
            st.markdown("## 🚛")

    with col2:
        st.markdown("# Robin Logistics Environment")
        st.markdown("### Configure and solve multi-depot vehicle routing problems with real-world constraints.")
        st.markdown("---")

    if solver_function:
        current_solver = solver_function
    else:
        from robin_logistics.solvers import test_solver
        current_solver = test_solver

    st.header("🏗️ Fixed Infrastructure")

    st.subheader("📦 SKU Types")
    sku_data = [
        {
            'SKU ID': sku_info['sku_id'],
            'Weight (kg)': sku_info['weight_kg'],
            'Volume (m³)': sku_info['volume_m3']
        }
        for sku_info in SKU_DEFINITIONS
    ]
    if sku_data:
        st.dataframe(pd.DataFrame(sku_data), use_container_width=True)

    st.subheader("🚚 Vehicle Fleet Specifications")
    vehicle_data = [
        {
            'Type': vehicle_spec['type'],
            'Name': vehicle_spec['name'],
            'Weight Capacity (kg)': vehicle_spec['capacity_weight_kg'],
            'Volume Capacity (m³)': vehicle_spec['capacity_volume_m3'],
            'Max Distance (km)': vehicle_spec['max_distance_km'],
            'Cost per km': f"${vehicle_spec['cost_per_km']:.2f}",
            'Fixed Cost': f"${vehicle_spec['fixed_cost']:.2f}",
            'Description': vehicle_spec['description']
        }
        for vehicle_spec in VEHICLE_FLEET_SPECS
    ]
    if vehicle_data:
        st.dataframe(pd.DataFrame(vehicle_data), use_container_width=True)

    st.subheader("🏭 Warehouse Locations")
    warehouse_data = [
        {
            'ID': warehouse['id'],
            'Name': warehouse['name'],
            'Latitude': f"{warehouse['lat']:.4f}",
            'Longitude': f"{warehouse['lon']:.4f}"
        }
        for warehouse in WAREHOUSE_LOCATIONS
    ]
    if warehouse_data:
        st.dataframe(pd.DataFrame(warehouse_data), use_container_width=True)

    st.divider()

    tab1, tab2, tab3 = st.tabs(["🌍 Geographic Control", "📦 Supply Configuration", "🚚 Vehicle Fleet"])

    with tab1:
        st.subheader("🌍 Geographic Control")

        num_orders = st.number_input(
            "Number of Orders",
            min_value=5,
            max_value=DEFAULT_SETTINGS.get('max_orders', 50),
            value=DEFAULT_SETTINGS['num_orders'],
            key="main_num_orders"
        )

        min_items_per_order = st.number_input(
            "Min Items per Order",
            min_value=1,
            max_value=DEFAULT_SETTINGS['max_items_per_order'],
            value=DEFAULT_SETTINGS['min_items_per_order'],
            key="main_min_items_per_order"
        )

        max_items_per_order = st.number_input(
            "Max Items per Order",
            min_value=1,
            max_value=DEFAULT_SETTINGS['max_items_per_order'],
            value=DEFAULT_SETTINGS['max_items_per_order'],
            key="main_max_items_per_order"
        )

        radius_km = st.slider(
            "Radius (km)",
            min_value=5,
            max_value=100,
            value=DEFAULT_SETTINGS['distance_control']['radius_km'],
            step=5,
            key="main_radius_km"
        )

        density_strategy = st.selectbox(
            "Distribution Strategy",
            ["clustered", "uniform", "ring"],
            index=0,
            key="main_density_strategy"
        )

        if density_strategy == "clustered":
            clustering_factor = st.slider(
                "Clustering Factor",
                min_value=0.0,
                max_value=2.0,
                value=DEFAULT_SETTINGS['distance_control']['clustering_factor'],
                step=0.1,
                key="main_clustering_factor"
            )
        elif density_strategy == "ring":
            ring_count = st.slider(
                "Ring Count",
                min_value=2,
                max_value=5,
                value=DEFAULT_SETTINGS['distance_control']['ring_count'],
                key="main_ring_count"
            )

        st.subheader("📊 SKU Distribution (%)")
        sku_names = [sku_info['sku_id'] for sku_info in SKU_DEFINITIONS]

        sku_percentages = []
        for i, sku_name in enumerate(sku_names):
            default_val = int(DEFAULT_SETTINGS['default_sku_distribution'][i]) if i < len(DEFAULT_SETTINGS['default_sku_distribution']) else 0
            percentage = st.slider(
                f"{sku_name}",
                min_value=0,
                max_value=100,
                value=default_val,
                step=1,
                key=f"demand_sku_{i}_percentage"
            )
            sku_percentages.append(percentage)

        total_percentage = sum(sku_percentages)
        if total_percentage == 100:
            st.success(f"Total: {total_percentage}% (Valid)")
        else:
            st.error(f"Total: {total_percentage}% (Must equal 100%)")

    with tab2:
        st.subheader("📦 Supply Configuration")

        selected_warehouse_indices = []
        default_n = min(DEFAULT_SETTINGS['num_warehouses'], len(WAREHOUSE_LOCATIONS))
        cols = st.columns(3)
        for idx, wh in enumerate(WAREHOUSE_LOCATIONS):
            with cols[idx % 3]:
                use_wh = st.checkbox(
                    f"Use {wh['id']} ({wh['name']})",
                    value=(idx < default_n),
                    key=f"use_wh_{wh['id']}"
                )
                if use_wh:
                    selected_warehouse_indices.append(idx)

        if not selected_warehouse_indices:
            st.error("Please select at least one warehouse")
            st.stop()

        num_warehouses = len(selected_warehouse_indices)
        warehouse_tabs = st.tabs([f"{WAREHOUSE_LOCATIONS[idx]['id']} ({WAREHOUSE_LOCATIONS[idx]['name']})" for idx in selected_warehouse_indices])
        warehouse_configs = []

        for tab_idx, warehouse_idx in enumerate(selected_warehouse_indices):
            with warehouse_tabs[tab_idx]:
                st.write(f"**{WAREHOUSE_LOCATIONS[warehouse_idx]['id']} ({WAREHOUSE_LOCATIONS[warehouse_idx]['name']}) Configuration**")

                st.subheader("📦 SKU Inventory Distribution")
                sku_inventory_percentages = []

                for j in range(len(sku_names)):
                    current_key = f"warehouse_{warehouse_idx}_sku_{j}_percentage"
                    default_value = DEFAULT_WAREHOUSE_SKU_ALLOCATIONS[warehouse_idx][j] if warehouse_idx < len(DEFAULT_WAREHOUSE_SKU_ALLOCATIONS) else 0
                    current_value = st.session_state.get(current_key, default_value)
                    percentage = st.slider(
                        f"{sku_names[j]} %",
                        min_value=0,
                        max_value=100,
                        value=int(current_value),
                        step=1,
                        key=current_key
                    )
                    sku_inventory_percentages.append(percentage)

                st.write("**📊 SKU Division:**")
                for j, sku_name in enumerate(sku_names):
                    st.write(f"• {sku_name}: {sku_inventory_percentages[j]}% of this SKU's demand")

                warehouse_configs.append({
                    'sku_inventory_percentages': sku_inventory_percentages
                })

        st.subheader("📊 Warehouse Allocation Summary")
        coverage_messages = []
        coverage_ok = True
        for j in range(len(sku_names)):
            sku_demand_percentage = sku_percentages[j]
            total_supply_percentage = sum(cfg['sku_inventory_percentages'][j] for cfg in warehouse_configs)
            effective_supply = (total_supply_percentage / 100.0) * sku_demand_percentage

            demand = sku_percentages[j]
            delta = effective_supply - demand
            if delta < 0:
                coverage_ok = False
                coverage_messages.append(f"❌ **{sku_names[j]}**: Understocked by {-delta:.1f}% (Supply {effective_supply:.1f}%, Demand {demand}%)")
            elif delta > 0:
                coverage_messages.append(f"⚠️ **{sku_names[j]}**: Overstocked by {delta:.1f}% (Supply {effective_supply:.1f}%, Demand {demand}%)")

        if coverage_ok:
            st.success("✅ All SKU demand is covered across warehouses (overstock allowed)")
        else:
            for msg in coverage_messages:
                st.markdown(msg)

    with tab3:
        st.subheader("🚚 Vehicle Fleet Configuration")

        for warehouse_idx in selected_warehouse_indices:
            warehouse_id = WAREHOUSE_LOCATIONS[warehouse_idx]['id']
            warehouse_name = WAREHOUSE_LOCATIONS[warehouse_idx]['name']

            st.write(f"**{warehouse_name} Vehicle Fleet:**")

            vehicle_counts = {}
            for vehicle_spec in VEHICLE_FLEET_SPECS:
                vehicle_type = vehicle_spec['type']
                current_count = DEFAULT_SETTINGS['default_vehicle_counts'].get(vehicle_type, 0)
                count = st.number_input(
                    f"Number of {vehicle_type}",
                    min_value=0,
                    max_value=DEFAULT_SETTINGS.get('max_vehicles_per_warehouse', 10),
                    value=current_count,
                    key=f"warehouse_{warehouse_idx}_vehicle_{vehicle_type}"
                )
                vehicle_counts[vehicle_type] = count

            warehouse_configs[warehouse_idx - min(selected_warehouse_indices)]['vehicle_counts'] = vehicle_counts

    st.divider()

    st.header("⚙️ Configuration Summary")
    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric("Orders", num_orders)
        st.metric("Warehouses", num_warehouses)
        st.metric("Radius", f"{radius_km} km")

    with summary_col2:
        st.write("**🌍 Geographic Control:**")
        st.write(f"• Strategy: {density_strategy}")
        if density_strategy == "clustered":
            st.write(f"• Clustering Factor: {clustering_factor}")
        elif density_strategy == "ring":
            st.write(f"• Ring Count: {ring_count}")
        st.write(f"• Radius: {radius_km} km")

        st.write("**🚚 Vehicle Fleet:**")
        vehicle_type_counts = {}
        for config in warehouse_configs:
            if 'vehicle_counts' in config:
                for vehicle_type, count in config['vehicle_counts'].items():
                    vehicle_type_counts[vehicle_type] = vehicle_type_counts.get(vehicle_type, 0) + count
        for vehicle_type, count in vehicle_type_counts.items():
            if count > 0:
                st.write(f"• {vehicle_type}: {count}")

    with summary_col3:
        st.write("**Configuration Status:**")
        all_valid = True
        validation_messages = []
        for j, sku_name in enumerate(sku_names):
            sku_demand = sku_percentages[j]
            total_supply_percentage = sum(cfg['sku_inventory_percentages'][j] for cfg in warehouse_configs)
            effective_supply = (total_supply_percentage / 100.0) * sku_demand
            if effective_supply < sku_demand:
                all_valid = False
                validation_messages.append(f"❌ **{sku_name}**: Supply {effective_supply:.1f}% < Demand {sku_demand}%")

        if all_valid:
            st.success("✅ Configuration Valid - All SKU demand is covered")
        else:
            st.error("❌ Configuration Invalid - Some SKU demand is not covered")
            for msg in validation_messages:
                st.markdown(msg)

    st.divider()
    st.subheader("🎲 Seed Control")

    use_seed = st.checkbox("Use Fixed Seed (Reproducible results)")

    if use_seed:
        seed_value = st.number_input(
            "Seed Value",
            min_value=1,
            max_value=999999,
            value=42
        )
    else:
        seed_value = None

    if st.button("Run Simulation", type="primary", key="run_sim"):
        st.info("Configuration captured! Generating scenario and running solver...")

        custom_config = {
            'num_orders': num_orders,
            'min_items_per_order': min_items_per_order,
            'max_items_per_order': max_items_per_order,
            'sku_percentages': sku_percentages,
            'warehouse_configs': warehouse_configs,
            'num_warehouses': num_warehouses,
            'random_seed': seed_value if use_seed else None,
            'distance_control': {
                'radius_km': radius_km,
                'density_strategy': density_strategy,
                'clustering_factor': clustering_factor if density_strategy == "clustered" else DEFAULT_SETTINGS['distance_control']['clustering_factor'],
                'ring_count': ring_count if density_strategy == "ring" else DEFAULT_SETTINGS['distance_control']['ring_count']
            }
        }

        try:
            env.generate_scenario_from_config(custom_config)
            st.session_state['env'] = env
            st.success("✅ Environment generated successfully!")

            solution = current_solver(env)
            if solution and solution.get('routes'):
                st.success("🎯 Solver completed successfully!")
                
                execution_success, execution_msg = env.execute_solution(solution)
                if execution_success:
                    st.success(f"✅ Solution executed: {execution_msg}")
                    st.session_state['solution'] = solution
                else:
                    st.error(f"❌ Solution execution failed: {execution_msg}")
                    st.session_state['solution'] = solution
            else:
                st.error("❌ Solver failed or returned no routes")
                st.session_state['solution'] = None

        except Exception as e:
            st.error(f"An error occurred during simulation: {str(e)}")
            st.error(f"Exception type: {type(e).__name__}")
            st.session_state['solution'] = None

    if st.session_state.get('solution'):
        solution = st.session_state['solution']
        env = st.session_state['env']
        st.divider()
        st.subheader("Solution Analysis")

        tab1, tab2, tab3 = st.tabs([
            "📊 Solution Overview",
            "📦 Item-Level Tracking",
            "🚛 Route Analysis"
        ])

        with tab1:
            st.subheader("📊 Solution Overview")

            current_seed = env.get_current_seed()
            if current_seed is not None:
                st.info(f"🔒 **Current Seed**: {current_seed} (Reproducible results)")
            else:
                st.info("🔀 **Current Seed**: Random (New scenario each time)")

            st.write("🔍 **SOLUTION VALIDATION**")

            is_valid_logic, logic_error = env.validate_solution_business_logic(solution)
            if is_valid_logic:
                st.success("✅ Business Logic: Valid")
            else:
                st.error(f"❌ Business Logic: {logic_error}")

            is_valid_complete, complete_error = env.validate_solution_complete(solution)
            if is_valid_complete:
                st.success("✅ Complete Solution: Valid")
            else:
                st.error(f"❌ Complete Solution: {complete_error}")

            stats = env.get_solution_statistics(solution)

            st.divider()
            st.write("📈 **CORE METRICS**")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Routes", stats.get('total_routes', 0))
            with col2:
                st.metric("Orders Served", f"{stats.get('unique_orders_served', 0)}/{stats.get('total_orders', 0)}")
            with col3:
                st.metric("Vehicles Used", f"{stats.get('unique_vehicles_used', 0)}/{stats.get('total_vehicles', 0)}")
            with col4:
                fulfillment_pct = stats.get('orders_fulfillment_ratio', 0) * 100
                st.metric("Fulfillment Rate", f"{fulfillment_pct:.1f}%")

            st.divider()
            st.write("💰 **COST & DISTANCE ANALYSIS**")

            total_cost = stats.get('total_cost', 0)
            total_distance = stats.get('total_distance', 0)
            orders_served = stats.get('unique_orders_served', 0)
            total_orders = stats.get('total_orders', 0)

            avg_cost_per_order = total_cost / orders_served if orders_served > 0 else 0
            avg_distance_per_order = total_distance / orders_served if orders_served > 0 else 0
            avg_cost_per_km = total_cost / total_distance if total_distance > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Cost", f"${total_cost:.2f}")
                st.caption(f"Avg: ${avg_cost_per_order:.2f}/order")
            with col2:
                st.metric("Total Distance", f"{total_distance:.2f} km")
                st.caption(f"Avg: {avg_distance_per_order:.2f} km/order")
            with col3:
                st.metric("Cost Efficiency", f"${avg_cost_per_km:.2f}/km")
                st.caption(f"Total: {total_cost:.2f} / {total_distance:.2f} km")

            st.divider()
            st.write("🚚 **VEHICLE PERFORMANCE**")

            total_routes = stats.get('total_routes', 0)
            total_vehicles = stats.get('total_vehicles', 0)
            vehicle_utilization = (total_routes / total_vehicles * 100) if total_vehicles > 0 else 0
            avg_route_distance = total_distance / total_routes if total_routes > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Vehicle Utilization", f"{vehicle_utilization:.1f}%")
                st.caption(f"{total_routes} routes / {total_vehicles} vehicles")
            with col2:
                st.metric("Avg Route Distance", f"{avg_route_distance:.2f} km")
                st.caption(f"Total: {total_distance:.2f} km")
            with col3:
                st.metric("Route Efficiency", f"{orders_served}/{total_routes}")
                st.caption(f"Orders per route")

            st.divider()
            st.subheader("🗺️ Solution Map")

            if env.warehouses and env.orders:
                all_lats = [wh.location.lat for wh in env.warehouses.values()] + [order.destination.lat for order in env.orders.values()]
                all_lons = [wh.location.lon for wh in env.warehouses.values()] + [order.destination.lon for order in env.orders.values()]

                center_lat = sum(all_lats) / len(all_lats)
                center_lon = sum(all_lons) / len(all_lons)

                m = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=10
                )

                for warehouse in env.warehouses.values():
                    folium.Marker(
                        [warehouse.location.lat, warehouse.location.lon],
                        popup=f"🏭 {warehouse.id}",
                        icon=folium.Icon(color='blue', icon='warehouse')
                    ).add_to(m)

                for order_id, order in env.orders.items():
                    delivered_items = sum(getattr(order, '_delivered_items', {}).values())
                    requested_items = sum(order.requested_items.values())
                    fulfillment_rate = (delivered_items / requested_items * 100) if requested_items > 0 else 0

                    if fulfillment_rate >= 100:
                        icon_color = 'green'
                        icon_type = 'check'
                    elif fulfillment_rate > 0:
                        icon_color = 'orange'
                        icon_type = 'minus'
                    else:
                        icon_color = 'red'
                        icon_type = 'times'

                    folium.Marker(
                        [order.destination.lat, order.destination.lon],
                        popup=f"📦 {order_id}<br>Fulfillment: {fulfillment_rate:.1f}%",
                        icon=folium.Icon(color=icon_color, icon=icon_type)
                    ).add_to(m)

                if solution.get('routes'):
                    colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink']
                    for i, route in enumerate(solution['routes']):
                        route_color = colors[i % len(colors)]
                        route_coords = []

                        for node_id in route['route']:
                            if node_id in env.nodes:
                                node = env.nodes[node_id]
                                route_coords.append([node.lat, node.lon])
                            elif node_id in env.warehouses:
                                warehouse = env.warehouses[node_id]
                                route_coords.append([warehouse.location.lat, warehouse.location.lon])
                            elif node_id in env.orders:
                                order = env.orders[node_id]
                                route_coords.append([order.destination.lat, order.destination.lon])

                        if len(route_coords) >= 2:
                            folium.PolyLine(
                                route_coords,
                                color=route_color,
                                weight=3,
                                opacity=0.8,
                                popup=f"Route: {route['vehicle_id']}"
                            ).add_to(m)

                legend_html = '''
                <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: 120px;
                            background-color: white; border:2px solid grey; z-index:9999;
                            font-size:14px; padding: 10px; border-radius: 5px;">
                <p><b>Legend</b></p>
                <p>🏭 Warehouse</p>
                <p>🟢 Order (100% Fulfilled)</p>
                <p>🟠 Order (Partially Fulfilled)</p>
                <p>🔴 Order (Unfulfilled)</p>
                <p>🔵 Route Lines</p>
                </div>
                '''
                m.get_root().html.add_child(folium.Element(legend_html))
                st.components.v1.html(m._repr_html_(), height=500, scrolling=False)

        with tab2:
            st.subheader("📦 Item-Level Tracking")

            st.write("**🏭 Warehouse Inventory Status:**")
            sku_distribution = {}
            for warehouse in env.warehouses.values():
                for sku_id, quantity in warehouse.inventory.items():
                    sku_distribution.setdefault(sku_id, {})[warehouse.id] = quantity

            if sku_distribution:
                warehouse_ids = [wh.id for wh in env.warehouses.values()]
                sku_data = []
                for sku_id, warehouse_data in sku_distribution.items():
                    row = {'SKU': sku_id}
                    for wh_id in warehouse_ids:
                        row[wh_id] = warehouse_data.get(wh_id, 0)
                    sku_data.append(row)

                df = pd.DataFrame(sku_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            st.write("**📋 Order Fulfillment Status:**")
            fulfillment_data = []
            for order_id, order in env.orders.items():
                requested_items = sum(order.requested_items.values())
                delivered_items = sum(getattr(order, '_delivered_items', {}).values())
                fulfillment_rate = (delivered_items / requested_items * 100) if requested_items > 0 else 0

                if fulfillment_rate >= 100:
                    status = "✅ Fully Fulfilled"
                elif fulfillment_rate > 0:
                    status = "⚠️ Partially Fulfilled"
                else:
                    status = "❌ Unfulfilled"

                fulfillment_data.append({
                    'Order ID': order_id,
                    'Requested': requested_items,
                    'Delivered': delivered_items,
                    'Rate (%)': f"{fulfillment_rate:.1f}",
                    'Status': status
                })

            if fulfillment_data:
                df = pd.DataFrame(fulfillment_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()
                st.write("**📊 Fulfillment Summary:**")
                fully_fulfilled = sum(1 for item in fulfillment_data if "Fully" in item['Status'])
                partially_fulfilled = sum(1 for item in fulfillment_data if "Partially" in item['Status'])
                unfulfilled = sum(1 for item in fulfillment_data if "Unfulfilled" in item['Status'])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Fully Fulfilled", fully_fulfilled)
                with col2:
                    st.metric("⚠️ Partially Fulfilled", partially_fulfilled)
                with col3:
                    st.metric("❌ Unfulfilled", unfulfilled)

                st.divider()
                st.write("**🔍 Detailed Order Analysis:**")

                order_options = [order_id for order_id, _ in env.orders.items()]
                selected_order = st.selectbox(
                    "Select Order to Analyze:",
                    options=order_options,
                    key="selected_order_analysis"
                )

                if selected_order:
                    order = env.orders[selected_order]
                    st.write(f"**📦 Order: {selected_order}**")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Items", sum(order.requested_items.values()))
                    with col2:
                        delivered_total = sum(getattr(order, '_delivered_items', {}).values())
                        st.metric("Delivered Items", delivered_total)
                    with col3:
                        fulfillment_rate = (delivered_total / sum(order.requested_items.values()) * 100) if sum(order.requested_items.values()) > 0 else 0
                        st.metric("Fulfillment Rate", f"{fulfillment_rate:.1f}%")
                    with col4:
                        st.metric("Destination", f"{order.destination.lat:.4f}, {order.destination.lon:.4f}")

                    st.divider()
                    st.write("**📋 Item Details:**")

                    item_details = []
                    for sku_id, requested_qty in order.requested_items.items():
                        delivered_qty = getattr(order, '_delivered_items', {}).get(sku_id, 0)
                        remaining_qty = requested_qty - delivered_qty

                        sku_info = next((s for s in SKU_DEFINITIONS if s['sku_id'] == sku_id), None)
                        if sku_info:
                            weight_kg = sku_info['weight_kg']
                            volume_m3 = sku_info['volume_m3']

                            item_details.append({
                                'SKU': sku_id,
                                'Requested': requested_qty,
                                'Delivered': delivered_qty,
                                'Remaining': remaining_qty,
                                'Weight (kg)': f"{weight_kg * requested_qty:.1f}",
                                'Volume (m³)': f"{volume_m3 * requested_qty:.3f}",
                                'Status': '✅ Complete' if delivered_qty >= requested_qty else '⚠️ Partial' if delivered_qty > 0 else '❌ Pending'
                            })

                    if item_details:
                        item_df = pd.DataFrame(item_details)
                        st.dataframe(item_df, use_container_width=True, hide_index=True)

                        st.divider()
                        st.write("**📊 Item Summary:**")

                        total_requested = sum(order.requested_items.values())
                        total_delivered = sum(getattr(order, '_delivered_items', {}).values())
                        total_weight = sum(float(item['Weight (kg)']) for item in item_details)
                        total_volume = sum(float(item['Volume (m³)']) for item in item_details)

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Weight", f"{total_weight:.1f} kg")
                        with col2:
                            st.metric("Total Volume", f"{total_volume:.3f} m³")
                        with col3:
                            st.metric("Items Delivered", f"{total_delivered}/{total_requested}")
                        with col4:
                            st.metric("Completion", f"{(total_delivered/total_requested*100):.1f}%" if total_requested > 0 else "0%")
                    else:
                        st.info("No item details available for this order.")

        with tab3:
            st.subheader("🚛 Route Analysis")

            if solution.get('routes'):
                st.write("**📋 Route Summary:**")
                route_data = []
                for route in solution['routes']:
                    pickup_items = sum(op.get('quantity', 0) for op in route.get('pickup_operations', []))
                    delivery_items = sum(op.get('quantity', 0) for op in route.get('delivery_operations', []))
                    
                    vehicle = env.get_vehicle_by_id(route['vehicle_id'])
                    distance_utilization = "N/A"
                    if vehicle and hasattr(vehicle, 'max_distance'):
                        distance_utilization = f"{(route.get('distance', 0) / vehicle.max_distance) * 100:.1f}%"
                    
                    route_data.append({
                        'Vehicle': route['vehicle_id'],
                        'Nodes': len(route['route']),
                        'Distance (km)': f"{route.get('distance', 0):.1f}",
                        'Distance Utilization': distance_utilization,
                        'Pickup Items': pickup_items,
                        'Delivery Items': delivery_items
                    })

                df = pd.DataFrame(route_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()
                st.write("**🔍 Detailed Route Analysis:**")

                vehicle_options = [route['vehicle_id'] for route in solution['routes']]
                selected_vehicle = st.selectbox(
                    "Select Vehicle to Analyze:",
                    options=vehicle_options,
                    key="selected_vehicle_analysis"
                )

                if selected_vehicle:
                    selected_route = next((route for route in solution['routes'] if route['vehicle_id'] == selected_vehicle), None)

                    if selected_route:
                        st.write(f"**🚚 Vehicle: {selected_vehicle}**")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Distance", f"{selected_route.get('distance', 0):.1f} km")
                        with col2:
                            st.metric("Route Nodes", len(selected_route['route']))
                        with col3:
                            pickup_items = sum(op.get('quantity', 0) for op in selected_route.get('pickup_operations', []))
                            delivery_items = sum(op.get('quantity', 0) for op in selected_route.get('delivery_operations', []))
                            st.metric("Delivered Items", delivery_items)
                        with col4:
                            vehicle = env.get_vehicle_by_id(selected_vehicle)
                            if vehicle and hasattr(vehicle, 'max_distance'):
                                distance_utilization = (selected_route.get('distance', 0) / vehicle.max_distance) * 100
                                st.metric("Distance Utilization", f"{distance_utilization:.1f}%")
                            else:
                                st.metric("Distance Utilization", "N/A")

                        st.divider()
                        st.write("**🗺️ Route Map & Progression Analysis**")

                        if env.warehouses and env.orders:
                            all_lats = [wh.location.lat for wh in env.warehouses.values()] + [order.destination.lat for order in env.orders.values()]
                            all_lons = [wh.location.lon for wh in env.warehouses.values()] + [order.destination.lon for order in env.orders.values()]

                            center_lat = sum(all_lats) / len(all_lats)
                            center_lon = sum(all_lons) / len(all_lons)

                            m = folium.Map(
                                location=[center_lat, center_lon],
                                zoom_start=11
                            )

                            for warehouse in env.warehouses.values():
                                folium.Marker(
                                    [warehouse.location.lat, warehouse.location.lon],
                                    popup=f"🏭 {warehouse.id}",
                                    icon=folium.Icon(color='blue', icon='warehouse')
                                ).add_to(m)

                            for order_id, order in env.orders.items():
                                delivered_items = sum(getattr(order, '_delivered_items', {}).values())
                                requested_items = sum(order.requested_items.values())
                                fulfillment_rate = (delivered_items / requested_items * 100) if requested_items > 0 else 0

                                if fulfillment_rate >= 100:
                                    icon_color = 'green'
                                    icon_type = 'check'
                                elif fulfillment_rate > 0:
                                    icon_color = 'orange'
                                    icon_type = 'minus'
                                else:
                                    icon_color = 'red'
                                    icon_type = 'times'

                                folium.Marker(
                                    [order.destination.lat, order.destination.lon],
                                    popup=f"📦 {order_id}<br>Fulfillment: {fulfillment_rate:.1f}%",
                                    icon=folium.Icon(color=icon_color, icon=icon_type)
                                ).add_to(m)

                            route_coords = []
                            for node_id in selected_route['route']:
                                if node_id in env.nodes:
                                    node = env.nodes[node_id]
                                    route_coords.append([node.lat, node.lon])
                                elif node_id in env.warehouses:
                                    warehouse = env.warehouses[node_id]
                                    route_coords.append([warehouse.location.lat, warehouse.location.lon])
                                elif node_id in env.orders:
                                    order = env.orders[node_id]
                                    route_coords.append([order.destination.lat, order.destination.lon])

                            if len(route_coords) >= 2:
                                folium.PolyLine(
                                    route_coords,
                                    color='blue',
                                    weight=5,
                                    opacity=0.8,
                                    popup=f"Route: {selected_vehicle}"
                                ).add_to(m)

                                for i, coord in enumerate(route_coords):
                                    if i == 0:
                                        folium.CircleMarker(
                                            coord, radius=12, color='green', fill=True,
                                            popup=f"START: Step {i+1}"
                                        ).add_to(m)
                                    elif i == len(route_coords) - 1:
                                        folium.CircleMarker(
                                            coord, radius=12, color='red', fill=True,
                                            popup=f"END: Step {i+1}"
                                        ).add_to(m)
                                    else:
                                        folium.CircleMarker(
                                            coord, radius=8, color='blue', fill=True,
                                            popup=f"Step {i+1}"
                                        ).add_to(m)

                            legend_html = '''
                            <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: 140px;
                                        background-color: white; border:2px solid grey; z-index:9999;
                                        font-size:14px; padding: 10px; border-radius: 5px;">
                            <p><b>Route Legend</b></p>
                            <p>🏭 Warehouse</p>
                            <p>🟢 Order (100% Fulfilled)</p>
                            <p>🟠 Order (Partially Fulfilled)</p>
                            <p>🔴 Order (Unfulfilled)</p>
                            <p>🔵 Selected Route</p>
                            <p>🟢 Start | 🔴 End | 🔵 Steps</p>
                            </div>
                            '''
                            m.get_root().html.add_child(folium.Element(legend_html))
                            st.components.v1.html(m._repr_html_(), height=500, scrolling=False)

                        st.divider()
                        st.write("**📊 Route Progression Metrics**")

                        progression_data = []
                        current_weight = 0
                        current_volume = 0
                        current_distance = 0
                        current_cost = 0

                        vehicle_specs = None
                        for spec in VEHICLE_FLEET_SPECS:
                            if spec['type'] in selected_vehicle:
                                vehicle_specs = spec
                                break

                        if vehicle_specs:
                            max_weight = vehicle_specs['capacity_weight_kg']
                            max_volume = vehicle_specs['capacity_volume_m3']
                            cost_per_km = vehicle_specs['cost_per_km']
                            fixed_cost = vehicle_specs['fixed_cost']
                        else:
                            st.error(f"**❌ No vehicle specs found for {selected_vehicle}**")
                            st.write(f"Available vehicle types: {[spec['type'] for spec in VEHICLE_FLEET_SPECS]}")
                            st.stop()

                        node_operations = {}

                        warehouse_node_id = None
                        if selected_route['route']:
                            warehouse_node_id = selected_route['route'][0]

                        for op in selected_route.get('pickup_operations', []):
                            if warehouse_node_id:
                                if warehouse_node_id not in node_operations:
                                    node_operations[warehouse_node_id] = {'pickup': [], 'delivery': []}
                                node_operations[warehouse_node_id]['pickup'].append(op)

                        for op in selected_route.get('delivery_operations', []):
                            order_id = op.get('order_id')
                            if order_id and order_id in env.orders:
                                order = env.orders[order_id]
                                if hasattr(order, 'destination'):
                                    closest_node = None
                                    min_dist = float('inf')
                                    for node_id in selected_route['route']:
                                        if node_id in getattr(env, 'nodes', {}):
                                            node = env.nodes[node_id]
                                            dist = ((node.lat - order.destination.lat)**2 + (node.lon - order.destination.lon)**2)**0.5
                                            if dist < min_dist:
                                                min_dist = dist
                                                closest_node = node_id

                                    if closest_node:
                                        if closest_node not in node_operations:
                                            node_operations[closest_node] = {'pickup': [], 'delivery': []}
                                        node_operations[closest_node]['delivery'].append(op)

                        for i, node_id in enumerate(selected_route['route']):
                            if i > 0:
                                prev_node = selected_route['route'][i-1]
                                segment_distance = env.get_distance(prev_node, node_id)
                                current_distance += segment_distance
                                current_cost += segment_distance * cost_per_km

                            if node_id in node_operations:
                                for op in node_operations[node_id].get('pickup', []):
                                    sku_id = op.get('sku_id')
                                    quantity = op.get('quantity', 0)
                                    sku_info = next((s for s in SKU_DEFINITIONS if s['sku_id'] == sku_id), None)
                                    if sku_info:
                                        weight_change = sku_info['weight_kg'] * quantity
                                        volume_change = sku_info['volume_m3'] * quantity
                                        current_weight += weight_change
                                        current_volume += volume_change

                                for op in node_operations[node_id].get('delivery', []):
                                    sku_id = op.get('sku_id')
                                    quantity = op.get('quantity', 0)
                                    sku_info = next((s for s in SKU_DEFINITIONS if s['sku_id'] == sku_id), None)
                                    if sku_info:
                                        weight_change = sku_info['weight_kg'] * quantity
                                        volume_change = sku_info['volume_m3'] * quantity
                                        current_weight -= weight_change
                                        current_volume -= volume_change

                            weight_utilization = (current_weight / max_weight * 100) if max_weight > 0 else 0
                            volume_utilization = (current_volume / max_volume * 100) if max_volume > 0 else 0

                            warehouse_match = None
                            for wh in env.warehouses.values():
                                if hasattr(wh, 'location') and wh.location.id == node_id:
                                    warehouse_match = wh
                                    break

                            order_match = None
                            for order in env.orders.values():
                                if hasattr(order, 'destination') and order.destination.id == node_id:
                                    order_match = order
                                    break

                            if warehouse_match:
                                node_name = f"🏭 {warehouse_match.id}"
                                node_type = "Warehouse"
                            elif order_match:
                                node_name = f"📦 {order_match.id}"
                                node_type = "Order"
                            elif node_id in env.nodes:
                                node_name = f"📍 Node {node_id}"
                                node_type = "Road Node"
                            else:
                                node_name = f"📍 Node {node_id}"
                                node_type = "Unknown"

                            if (node_id in node_operations or
                                warehouse_match is not None or
                                order_match is not None or
                                i % 10 == 0 or
                                i == len(selected_route['route']) - 1):

                                operation_details = ""

                                if (i == len(selected_route['route']) - 1 and warehouse_match is not None):
                                    operation_details += " (return)"
                                    current_weight = 0.0
                                    current_volume = 0.0
                                elif node_id in node_operations:
                                    # Count total items, not operations
                                    pickup_items = sum(op.get('quantity', 0) for op in node_operations[node_id].get('pickup', []))
                                    delivery_items = sum(op.get('quantity', 0) for op in node_operations[node_id].get('delivery', []))

                                    if pickup_items > 0:
                                        operation_details += f" (+{pickup_items} pickup)"
                                    if delivery_items > 0:
                                        operation_details += f" (-{delivery_items} delivery)"

                                display_location = node_name + operation_details

                                final_weight_utilization = (current_weight / max_weight * 100) if max_weight > 0 else 0
                                final_volume_utilization = (current_volume / max_volume * 100) if max_volume > 0 else 0

                                # Calculate distance utilization at this step
                                vehicle = env.get_vehicle_by_id(selected_vehicle)
                                distance_utilization = "N/A"
                                if vehicle and hasattr(vehicle, 'max_distance'):
                                    distance_utilization = f"{(current_distance / vehicle.max_distance) * 100:.1f}%"
                                
                                progression_data.append({
                                    'Step': i + 1,
                                    'Location': display_location,
                                    'Type': node_type,
                                    'Distance (km)': f"{current_distance:.2f}",
                                    'Distance Util (%)': distance_utilization,
                                    'Weight (kg)': f"{max(0.0, current_weight):.1f}",
                                    'Volume (m³)': f"{max(0.0, current_volume):.3f}",
                                    'Weight Util (%)': f"{max(0.0, final_weight_utilization):.1f}",
                                    'Volume Util (%)': f"{max(0.0, final_volume_utilization):.1f}",
                                    'Cost ($)': f"{current_cost:.2f}"
                                })

                        if progression_data:
                            progression_df = pd.DataFrame(progression_data)
                            st.dataframe(progression_df, use_container_width=True, hide_index=True)
                        else:
                            st.error("**❌ No progression data generated**")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Max Weight Capacity", f"{max_weight} kg")
                            if progression_data:
                                peak_weight = max(progression_data, key=lambda x: float(x['Weight (kg)']))
                                st.caption(f"Peak: {peak_weight['Weight (kg)']} kg")
                        with col2:
                            st.metric("Max Volume Capacity", f"{max_volume} m³")
                            if progression_data:
                                peak_volume = max(progression_data, key=lambda x: float(x['Volume (m³)']))
                                st.caption(f"Peak: {peak_volume['Volume (m³)']} m³")
                        with col3:
                            st.metric("Total Distance", f"{current_distance:.2f} km")
                            st.caption(f"Cost: ${current_cost:.2f}")
                        with col4:
                            if progression_data:
                                peak_weight_util = max(progression_data, key=lambda x: float(x['Weight Util (%)']))
                                peak_volume_util = max(progression_data, key=lambda x: float(x['Volume Util (%)']))
                                st.metric("Peak Utilization", f"{max(float(peak_weight_util['Weight Util (%)']), float(peak_volume_util['Volume Util (%)'])):.1f}%")
                                st.caption("Highest capacity usage")
                        


            else:
                st.info("No routes available for analysis.")

    st.divider()
    st.header("📖 How to Use")
    st.write("""
    1. **🏗️ Review Infrastructure**: Examine the fixed SKU types, vehicle fleet, and warehouse locations above
    2. **🌍 Configure Geographic Control**: Set radius, distribution strategy, and clustering parameters
    3. **📦 Configure Supply**: Set inventory distribution across warehouses
    4. **🚚 Configure Vehicle Fleet**: Set vehicle counts per warehouse
    5. **🚀 Run Simulation**: Click "Run Simulation" to generate and solve the problem
    6. **📊 Analyze Results**: Use the comprehensive analysis tabs for detailed insights

    **💡 Tip**: Start with smaller problems (5-10 orders) to test your solver, then scale up!
    """)

if __name__ == "__main__":
    if 'env' not in st.session_state or st.session_state.get('env') is None:
        try:
            st.session_state['env'] = LogisticsEnvironment()
        except Exception as e:
            st.error(f"Failed to create environment: {str(e)}")
            st.stop()

    if 'solution' not in st.session_state:
        st.session_state['solution'] = None

    run_dashboard(st.session_state['env'])
