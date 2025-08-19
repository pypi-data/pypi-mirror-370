import os
import json
import polars as pl
from datetime import datetime, timedelta
from supply import PyResource, PySKU, PyOperation, PyMultiStepProcess, PyDemandPlan, PyLocation
from supply import get_all_operations, get_all_skus, get_all_resources, set_periods, get_all_locations
from supply import calculate_landed_costs
from supply import get_all_demands
from supply import get_all_multi_step_processes
from supply import PyDemand, PyDemandPlanner
from break_direct_cycles import break_direct_cycles
from supply import levelize_supply_chain
from supply import merge_supply_chain_scenarios
from supply import PyScenario
from file_metadata import FileMetadata
from supply import set_log_level
from supply import start_web_service
from supply import PyScenario

import time
from D3scenario_visualize import generate_supply_chain_D3_html
from D3scenario_visualize import install_icons
from lsco_network_from_reports import ProcessNetworkLSCOReports
from lsco_network_from_reports import *


# Set log level to info
# There are 3 operation steps in a process PR1 at Plant PL1 with separate line resource  attached to each of them  e.g. PR1 - (O1 L1) , (O2,L2)  (O3,L3)
# There is a BOM B1 atatched to this process with two input Products (INP1, INP2)  and out output product OP1
# then in consumption report (for a period) how many records would i see. 2x3 ?
# Process, Operation, Line, Input Product, Output Product, BOM, Plant, Production Qty, Consumption Qty
# PR1, O1, L1, INP1, OP1,B1,PL1, 100, 100
# PR1, O1, L1, INP2, OP1,B1,PL1, 100, 100
# PR1, O2, L2, INP1, OP1,B1,PL1, 100, 100
# PR1, O2, L2, INP2, OP1,B1,PL1, 100, 100
# PR1, O3, L3, INP1, OP1,B1,PL1, 100, 100
# PR1, O3, L3, INP2, OP1,B1,PL1, 100, 100

# Production Report does not have input product 
# Process, Operation, Line, BOM, Plant, Production Qty, Line Utilization, Production Time(hrs)
# PR1, O1, L1, B1, PL1, 100, 100, 1
# PR1, O2, L2, B1, PL1, 100, 100, 1
# PR1, O3, L3, B1, PL1, 100, 100, 1

# Notes: 
# Join consumptions and prodution report on Process, Operation, Line, BOM, Plant, Solution ID, Period ID

# Manufacturing Static Network can be generated from the consumption report:
# To create static network from consumption report - use this key: process_key -> process, bom, plant
# Get all records for this key for the first unique period_id and solution_id combination:
# Now use the data from following columns for these records against this (process_key period id and solution id):
# input_product Production Qty, Line Utilization, Production Time(hrs)
# Process, Operation, Line, BOM, Plant, Production Qty, Line Utilization, Production Time(hrs)
# Process, Operation, Line, BOM, Plant, Production Qty, Line Utilization, Production Time(hrs)



def load_scenario(dataset_path, auto_scenario_id, enable_landed_cost=False):
    """Modified to return SKUs instead of deleting them"""
    start_time = time.time()
    processor = ProcessNetworkLSCOReports(dataset_path, auto_scenario_id=auto_scenario_id, enable_landed_cost=False)

    # Your existing LSCO loading logic here...
    # Get all required dataframes
    consumption_df = processor.dataframes.get("consumption_report.csv")
    production_df = processor.dataframes.get("production_report.csv")
    period_df = processor.dataframes.get("time_period.csv")
    demand_df = processor.dataframes.get("demand_flow_report.csv")
    on_hand_df = processor.dataframes.get("on_hand_stock.csv")
    lane_details_df = processor.dataframes.get("lane_details_report.csv")


    # Create manufacturing network
    mfg_network_map_object = processor.create_multi_step_process_objects_from_consumption_report(consumption_df, scenario_id=auto_scenario_id)
    print("Created multi step process objects from consumption report")
    skus = mfg_network_map_object['skus']
    resources = mfg_network_map_object['resources']
    processes = mfg_network_map_object['processes']
    operations = mfg_network_map_object['operations']

    # Generate manufacturing network
    processor.generate_manufacturing_network(consumption_df, skus, resources, processes, operations, scenario_id=auto_scenario_id)
    print("Generated manufacturing network")

    transport_network_map_object = processor.create_transportation_network(period_df, skus, resources, operations, lane_details_df, scenario_id=auto_scenario_id)
    print("Created transportation network")

    transport_df = transport_network_map_object['transportation_df']    
    skus = transport_network_map_object['skus']
    resources = transport_network_map_object['resources']
    operations = transport_network_map_object['operations']

    # Ensure alternate operations are created and static network is in place.
    for sku in skus.values():
        sku.process_sources()
    print("Processed sources")
    period_dict = processor.create_operation_plans(operations, production_df, period_df, lane_details_df, skus, scenario_id=auto_scenario_id)

    print("Created operation plans")
    # Now mark levels in supply chain and add consuming operations to the operations
    levelize_supply_chain(auto_scenario_id)
    print("Levelized supply chain")

    # Add on hand inventory to the skus
    processor.create_on_hand_inventory(skus, on_hand_df, period_dict)
    print("Created on hand inventory")

    # Add inventory on the most upstream skus. 
    # Note: Ideally this should be doe only for Vendor SKUs at best by identifying them from procurement report.
    # But for now, we are doing it for all skus. This creates extra infinite lots to stock that could mess up the
    # cost calculation. (Though we have tried to handle in in Rust)
    processor.add_inventory_on_most_upstream_skus(skus, period_dict)
    print("Added inventory on most upstream skus")

    processor.create_demand_plans(skus, period_dict, demand_df, scenario_id=auto_scenario_id)
    print("Created demand plans")
    end_time = time.time()
    print(f"Time taken to create set up network and flows: {end_time - start_time} seconds")

    return skus

    
if __name__ == "__main__":
    dataset_path = "tests/on_ga_alt_dataset"
    #dataset_path = "tests/experiments/on_metalbox"
    #dataset_path = "tests/experiments/on_mdlz_tdc"
    #dataset_path = "tests/experiments/on_lowes_rdc"
    #dataset_path, scenarios_to_compare = "tests/experiments/on_pepsico", ["Base"]

    # Get all distinct scenarios
    # dataset_path = "tests/experiments/on_mdlz_multi_scenario"
    #dataset_path = "tests/experiments/landed_cost/toy1"
    #dataset_path = "tests/experiments/landed_cost/no_foc"
    #dataset_path = "tests/experiments/landed_cost/pepsi_feasible"
    #dataset_path = "tests/experiments/landed_cost/multi_period"

    #dataset_path = "/Users/nitinsingal/Downloads/MDLZ ON"
    #dataset_path = "tests/experiments/empower/output_P147_S32_LaptopX_ChennaiX"
    #dataset_path = "tests/landed_cost_datasets/toy1"
    #dataset_path = "tests/experiments/empower/uber_single_period"

    #dataset_path = "tests/experiments/empower/output_high_on_hand"
    #dataset_path = "tests/experiments/empower/output_final_LaptopX_Laptop_high_OH"


    scenarios_to_compare = ProcessNetworkLSCOReports.get_distinct_scenarios(dataset_path)
    print(f"Scenarios to compare: {scenarios_to_compare}")
    for scenario_id in scenarios_to_compare:
        scen = PyScenario(scenario_id)

    #scenarios_to_compare = ["1.1", "1.2"]
    
    # Load scenarios
    scenario_skus = {}
    for scenario_id in scenarios_to_compare:
        print(f"Loading scenario {scenario_id}...")
        scenario_skus[scenario_id] = load_scenario(dataset_path, scenario_id, enable_landed_cost=False)

    # Create scenario-based data structure for comparison
    scenario_data_map = {}
    for scenario_id in scenarios_to_compare:
        scenario_data_map[scenario_id] = {}
    scenario_data_map["Combined"] = {}
    
    # Process SKUs from each scenario
    for scenario_id in scenarios_to_compare:
        print(f"Processing SKUs from scenario {scenario_id}...")
        count = 0
        for sku in scenario_skus[scenario_id].values():
            if sku.level == 1 and count < 10: 
                print(f"Processing {sku.name} from scenario {scenario_id}")
                result = sku.visualize_upstream_supply_chain(include_resources=False, include_flow_plans=False, include_operation_plans=False)
                json_data = json.loads(result)
                scenario_data_map[scenario_id][sku.name] = json_data
                count += 1

    
    # Generate merged visualizations for SKUs that exist in both scenarios
    if len(scenarios_to_compare) == 2:
        print("Generating merged visualizations...")
        
        # Find common SKUs between scenarios
        scenario_1, scenario_2 = scenarios_to_compare
        skus_1_names = set(scenario_data_map[scenario_1].keys())
        skus_2_names = set(scenario_data_map[scenario_2].keys())
        common_skus = skus_1_names.intersection(skus_2_names)
        
        print(f"Found {len(common_skus)} common SKUs between scenarios")
        
        for sku_name in common_skus:
            try:
                print(f"Creating merged visualization for {sku_name}")
                merged_result = merge_supply_chain_scenarios(sku_name, scenario_1, scenario_2, include_resources=False)
                merged_json_data = json.loads(merged_result)
                scenario_data_map["Combined"][sku_name] = merged_json_data
                
                # Analyze edge colors for this SKU
                edge_colors = {}
                for edge in merged_json_data['edges']:
                    color = edge['properties'].get('edge_color', 'unknown')
                    edge_colors[color] = edge_colors.get(color, 0) + 1
                
                print(f"  Edge color distribution for {sku_name}: {edge_colors}")
                
            except Exception as e:
                print(f"Error generating merged visualization for {sku_name}: {e}")
                continue
    else:
        print(f"Skipping merged visualizations - need exactly 2 scenarios, got {len(scenarios_to_compare)}")

    html_file_name = "ga_scenarios_comparison.html"
    if "pepsico" in dataset_path:
        html_file_name = "pepsico_scenarios_comparison.html"
    elif "metalbox" in dataset_path:
        html_file_name = "metalbox_scenarios_comparison.html"
    elif "mdlz" in dataset_path:
        html_file_name = "mdlz_scenarios_comparison.html"
    elif "lowes" in dataset_path:
        html_file_name = "lowes_scenarios_comparison.html"
    elif "toy1" in dataset_path:
        html_file_name = "landed_cost_toy1.html"
    elif "landed_cost/no_foc" in dataset_path:
        html_file_name = "landed_cost_no_foc.html"
    elif "landed_cost/multi_period" in dataset_path:
        html_file_name = "landed_cost_multi_period.html"
    elif "uber_masked" in dataset_path:
        html_file_name = "uber_masked_scenarios.html"
    elif "uber_single_period" in dataset_path:
        html_file_name = "uber_single_period.html"

    
    generate_supply_chain_D3_html(scenario_data_map, html_file_name)
    install_icons(f"{os.getcwd()}/icons")

    print(f"\nScenario comparison visualization created at: {html_file_name}")
    print("Open this file in your web browser to view the interactive supply chain comparison.")
    print(f"\nHow to use:")
    print(f"1. Select a scenario from the dropdown ({', '.join(scenarios_to_compare + ['Combined'] if len(scenarios_to_compare) == 2 else scenarios_to_compare)})")
    print("2. Enter a Product@Location")
    print("3. Click 'Load' to visualize the supply chain")
    
    if len(scenarios_to_compare) == 2 and 'common_skus' in locals():
        print(f"\nAvailable common SKUs: {list(common_skus)}")


