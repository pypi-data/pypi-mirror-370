from supply import PySKU
from supply import PyOperation
from supply import PyResource
from supply import PyLocation
from supply import PyOperation as PyManufacturingProcess
from supply import PyOperation as PySourcingProcess
from supply import PyOperation as PyFulfillmentProcess
from supply import PyMultiStepProcess
from supply import PyDemand
from supply import PyDemandPlanner
from supply import reset_network
from supply import get_all_skus
from supply import get_all_operations
from supply import get_all_resources
from supply import get_all_demands
from supply import levelize_supply_chain
from supply import set_log_level
from supply import merge_supply_chain_scenarios

from D3scenario_visualize import generate_supply_chain_D3_html
from D3scenario_visualize import install_icons

# Set log level to info
set_log_level("info")

import polars as pl
import json
import os
import re

def create_laptop_supply_chain_scenario(scenario_id="Base"):
    """Create a laptop supply chain in the specified scenario"""
    
    # Create SKUs at different locations for this scenario
    laptop_dc = PySKU.create("Laptop", "DC", scenario_id)
    laptop_plant1 = PySKU.create("Laptop", "Plant1", scenario_id)
    laptop_plant2 = PySKU.create("Laptop", "Plant2", scenario_id)

    # Components at Plant1
    disk_plant1 = PySKU.create("Disk", "Plant1", scenario_id)
    cpu_plant1 = PySKU.create("CPU", "Plant1", scenario_id)
    memory_plant1 = PySKU.create("Memory", "Plant1", scenario_id)

    # Components at Plant2
    disk_plant2 = PySKU.create("Disk", "Plant2", scenario_id)
    cpu_plant2 = PySKU.create("CPU", "Plant2", scenario_id)
    memory_plant2 = PySKU.create("Memory", "Plant2", scenario_id)

    # Create assembly resources
    assembly_resource_plant1 = PyResource(f"Assembly_Resource_Plant1", scenario_id)
    assembly_resource_plant2 = PyResource(f"Assembly_Resource_Plant2", scenario_id)
    concurrent_resource_plant1 = PyResource(f"Concurrent_Resource_Plant1", scenario_id)

    # Set daily capacity for the resources (e.g., 100 units per day)
    for day in range(15, 32):  # Jan 15-31
        date = f"2024-01-{day}"
        assembly_resource_plant1.set_capacity(date, 500.0)
        assembly_resource_plant2.set_capacity(date, 500.0)
        concurrent_resource_plant1.set_capacity(date, 300.0)  # Different capacity for concurrent resource

    # Create assembly operations for both plants with resources
    laptop_assembly_plant1 = PyManufacturingProcess(f"Make_Laptop_Plant1", lead_time=2, min_lot=1, increment=1, scenario_id=scenario_id)
    laptop_assembly_plant1.add_produce_flow(laptop_plant1, quantity_per=1.0)
    laptop_assembly_plant1.add_bom_component(disk_plant1, quantity_per=1.0)
    laptop_assembly_plant1.add_bom_component(cpu_plant1, quantity_per=1.0)
    laptop_assembly_plant1.add_bom_component(memory_plant1, quantity_per=2.0)
    # This is to demonstrate a loop. Do not remove it.
    #laptop_assembly_plant1.add_bom_component(laptop_dc, quantity_per=1.0)

    laptop_assembly_plant1.add_resource_requirement(assembly_resource_plant1, quantity_per=1.0)  # Add first resource requirement
    laptop_assembly_plant1.add_resource_requirement(concurrent_resource_plant1, quantity_per=0.8)  # Add concurrent resource requirement
    laptop_assembly_plant1.category = "Manufacturing"

    laptop_assembly_plant2 = PyManufacturingProcess(f"Make_Laptop_Plant2", lead_time=3, min_lot=1, increment=1, scenario_id=scenario_id)
    laptop_assembly_plant2.add_output(laptop_plant2, quantity_per=1.0)
    laptop_assembly_plant2.add_bom_component(disk_plant2, quantity_per=1.0)
    laptop_assembly_plant2.add_bom_component(cpu_plant2, quantity_per=1.0)
    laptop_assembly_plant2.add_bom_component(memory_plant2, quantity_per=2.0)
    laptop_assembly_plant2.add_line(assembly_resource_plant2, quantity_per=1.0)
    laptop_assembly_plant2.add_period(2, None, None)
    laptop_assembly_plant2.category = "Manufacturing"

    # Create transport operations from plants to DC
    move_laptop_plant1_to_dc = PySourcingProcess(f"Move_Laptop_Plant1_to_DC", lead_time=1, min_lot=1, increment=1, scenario_id=scenario_id)
    move_laptop_plant1_to_dc.add_destination(laptop_dc, quantity_per=1.0)
    move_laptop_plant1_to_dc.add_consume_flow(laptop_plant1, quantity_per=1.0)
    move_laptop_plant1_to_dc.add_period(1, "2024-01-01", "2024-04-01")

    move_laptop_plant2_to_dc = PySourcingProcess(f"Move_Laptop_Plant2_to_DC", lead_time=1, min_lot=1, increment=1, scenario_id=scenario_id)
    move_laptop_plant2_to_dc.add_destination(laptop_dc, quantity_per=1.0)
    move_laptop_plant2_to_dc.add_source(laptop_plant2, quantity_per=1.0)
    move_laptop_plant2_to_dc.add_period(1, None, None)

    # NEW: Add bidirectional move operations between Plant1 and Plant2 (Base scenario only)
    move_laptop_plant1_to_plant2 = PySourcingProcess("Move_Laptop_Plant1_to_Plant2", lead_time=1, min_lot=1, increment=1, scenario_id=scenario_id)
    move_laptop_plant1_to_plant2.add_destination(laptop_plant2, quantity_per=1.0)
    move_laptop_plant1_to_plant2.add_consume_flow(laptop_plant1, quantity_per=1.0)
    move_laptop_plant1_to_plant2.add_period(1, "2024-01-01", "2024-04-01")
    move_laptop_plant1_to_plant2.category = "Distribution"

    move_laptop_plant2_to_plant1 = PySourcingProcess("Move_Laptop_Plant2_to_Plant1", lead_time=1, min_lot=1, increment=1, scenario_id=scenario_id)
    move_laptop_plant2_to_plant1.add_destination(laptop_plant1, quantity_per=1.0)
    move_laptop_plant2_to_plant1.add_source(laptop_plant2, quantity_per=1.0)
    move_laptop_plant2_to_plant1.add_period(1, None, None)
    move_laptop_plant2_to_plant1.category = "Distribution"


    # Add initial inventory
    disk_plant1.add_inventory("2024-01-15", 1000.0)
    cpu_plant1.add_inventory("2024-01-15", 250.0)
    memory_plant1.add_inventory("2024-01-15", 500.0)
    disk_plant2.add_inventory("2024-01-15", 1000.0)
    cpu_plant2.add_inventory("2024-01-15", 250.0)
    memory_plant2.add_inventory("2024-01-15", 500.0)
    
    return laptop_dc

def create_alternate_laptop_supply_chain_scenario(scenario_id="AlternateScenario"):
    """Create an alternate laptop supply chain similar to Base but with Plant3 instead of Plant2"""
    
    # Create SKUs - same products, Plant3 instead of Plant2
    laptop_dc = PySKU.create("Laptop", "DC", scenario_id)
    laptop_plant1 = PySKU.create("Laptop", "Plant1", scenario_id)
    laptop_plant3 = PySKU.create("Laptop", "Plant3", scenario_id)  # Plant3 instead of Plant2

    # Components at Plant1 (same as Base)
    disk_plant1 = PySKU.create("Disk", "Plant1", scenario_id)
    cpu_plant1 = PySKU.create("CPU", "Plant1", scenario_id)
    memory_plant1 = PySKU.create("Memory", "Plant1", scenario_id)

    # Components at Plant3 (same components as Plant2 in Base)
    disk_plant3 = PySKU.create("Disk", "Plant3", scenario_id)
    cpu_plant3 = PySKU.create("CPU", "Plant3", scenario_id)
    memory_plant3 = PySKU.create("Memory", "Plant3", scenario_id)

    # Create assembly resources with same names as Base (no scenario prefix)
    assembly_resource_plant1 = PyResource("Assembly_Resource_Plant1", scenario_id)
    assembly_resource_plant3 = PyResource("Assembly_Resource_Plant3", scenario_id)  # Plant3 resource

    # Set daily capacity (same as Base scenario)
    for day in range(15, 32):  # Jan 15-31
        date = f"2024-01-{day}"
        assembly_resource_plant1.set_capacity(date, 500.0)
        assembly_resource_plant3.set_capacity(date, 500.0)

    # Create assembly operations with same structure as Base (no scenario prefix)
    laptop_assembly_plant1 = PyManufacturingProcess("Make_Laptop_Plant1", lead_time=2, min_lot=1, increment=1, scenario_id=scenario_id)
    laptop_assembly_plant1.add_produce_flow(laptop_plant1, quantity_per=1.0)
    laptop_assembly_plant1.add_bom_component(disk_plant1, quantity_per=1.0)
    laptop_assembly_plant1.add_bom_component(cpu_plant1, quantity_per=1.0)
    laptop_assembly_plant1.add_bom_component(memory_plant1, quantity_per=2.0)  # Same as Base
    laptop_assembly_plant1.add_resource_requirement(assembly_resource_plant1, quantity_per=1.0)  # Add first resource requirement. No concurrent resource requirement is added here.
    laptop_assembly_plant1.category = "Manufacturing"

    # Plant3 assembly with same BOM as Plant2 in Base scenario
    laptop_assembly_plant3 = PyManufacturingProcess("Make_Laptop_Plant3", lead_time=3, min_lot=1, increment=1, scenario_id=scenario_id)
    laptop_assembly_plant3.add_output(laptop_plant3, quantity_per=1.0)
    laptop_assembly_plant3.add_bom_component(disk_plant3, quantity_per=1.0)
    laptop_assembly_plant3.add_bom_component(cpu_plant3, quantity_per=1.0)
    laptop_assembly_plant3.add_bom_component(memory_plant3, quantity_per=2.0)  # Same as Base
    laptop_assembly_plant3.add_line(assembly_resource_plant3, quantity_per=1.0)
    laptop_assembly_plant3.add_period(2, None, None)
    laptop_assembly_plant3.category = "Manufacturing"

    # Create transport operations (no scenario prefix)
    move_laptop_plant1_to_dc = PySourcingProcess("Move_Laptop_Plant1_to_DC", lead_time=1, min_lot=1, increment=1, scenario_id=scenario_id)
    move_laptop_plant1_to_dc.add_destination(laptop_dc, quantity_per=1.0)
    move_laptop_plant1_to_dc.add_consume_flow(laptop_plant1, quantity_per=1.0)
    move_laptop_plant1_to_dc.add_period(1, "2024-01-01", "2024-04-01")

    move_laptop_plant3_to_dc = PySourcingProcess("Move_Laptop_Plant3_to_DC", lead_time=1, min_lot=1, increment=1, scenario_id=scenario_id)
    move_laptop_plant3_to_dc.add_destination(laptop_dc, quantity_per=1.0)
    move_laptop_plant3_to_dc.add_source(laptop_plant3, quantity_per=1.0)
    move_laptop_plant3_to_dc.add_period(1, None, None)

    laptop_dc.add_producing_operation(move_laptop_plant1_to_dc)
    laptop_dc.add_producing_operation(move_laptop_plant3_to_dc)

    # Same inventory levels as Base scenario
    disk_plant1.add_inventory("2024-01-15", 1000.0)
    cpu_plant1.add_inventory("2024-01-15", 250.0)
    memory_plant1.add_inventory("2024-01-15", 500.0)
    disk_plant3.add_inventory("2024-01-15", 1000.0)  # Same as Plant2 in Base
    cpu_plant3.add_inventory("2024-01-15", 250.0)
    memory_plant3.add_inventory("2024-01-15", 500.0)
    
    return laptop_dc

# Reset network and create both scenarios
reset_network()

print("Creating Base Scenario...")
base_laptop_dc = create_laptop_supply_chain_scenario("Base")

print("Creating Alternate Scenario...")
alt_laptop_dc = create_alternate_laptop_supply_chain_scenario("AlternateScenario")

# Process sources for all SKUs in both scenarios
print("Processing sources for Base scenario...")
for sku in get_all_skus("Base"):
    sku.process_sources()

print("Processing sources for Alternate scenario...")
for sku in get_all_skus("AlternateScenario"):
    sku.process_sources()

levelize_supply_chain()

# Generate individual visualizations
print("Generating individual scenario visualizations...")

# Base scenario visualization
base_result = base_laptop_dc.visualize_upstream_supply_chain()
base_json_data = json.loads(base_result)
print(f"Base scenario has {len(base_json_data['nodes'])} nodes and {len(base_json_data['edges'])} edges")

# Alternate scenario visualization
alt_result = alt_laptop_dc.visualize_upstream_supply_chain()
alt_json_data = json.loads(alt_result)
print(f"Alternate scenario has {len(alt_json_data['nodes'])} nodes and {len(alt_json_data['edges'])} edges")

# Generate merged visualization
print("Generating merged scenario visualization...")
try:
    merged_result = merge_supply_chain_scenarios("Laptop@DC", "Base", "AlternateScenario")
    merged_json_data = json.loads(merged_result)
    print(f"Merged visualization has {len(merged_json_data['nodes'])} nodes and {len(merged_json_data['edges'])} edges")
    
    # Analyze edge colors
    edge_colors = {}
    for edge in merged_json_data['edges']:
        color = edge['properties'].get('edge_color', 'unknown')
        edge_colors[color] = edge_colors.get(color, 0) + 1
    
    print(f"Edge color distribution: {edge_colors}")
    
    # Analyze node colors
    node_colors = {}
    for node in merged_json_data['nodes']:
        color = node['properties'].get('node_color', 'unknown')
        node_colors[color] = node_colors.get(color, 0) + 1
    
    print(f"Node color distribution: {node_colors}")
    
    # Create the new scenario-based data structure
    scenario_data_map = {
        "Base": {
            "Laptop@DC": base_json_data
        },
        "AlternateScenario": {
            "Laptop@DC": alt_json_data  
        },
        "Combined": {
            "Laptop@DC": merged_json_data
        }
    }

    # Generate HTML visualization with the new structure
    html_file_name = "laptop_scenarios_comparison.html"
    html_file = generate_supply_chain_D3_html(scenario_data_map, html_file_name)
    print(f"\nComparison visualization created at: {html_file}")
    print("Open this file in your web browser to view the interactive supply chain comparison.")
    print("\nHow to use:")
    print("1. Select a scenario from the dropdown (Base, AlternateScenario, or Combined)")
    print("2. Enter 'Laptop@DC' in the Product@Location text box")
    print("3. Click 'Load' to visualize the supply chain")
    
    # Save merged JSON for further analysis
    with open("merged_scenario_graph.json", "w") as f:
        json.dump(merged_json_data, f, indent=2)
    print("Merged graph data saved to: merged_scenario_graph.json")

    print(merged_json_data)
    
except Exception as e:
    print(f"Error generating merged visualization: {e}")
    import traceback
    traceback.print_exc()

print("\nScenario comparison completed!")

#install_icons(f"{os.getcwd()}/icons")


