# This is the main entry point for "cost to server" analysis.
# Also referred to Landed Cost Analysis. The idea is to find the cost to serve demand as well
# as cost to create unpeggged inventory generated from over-production 
# This run function should be in the cost to serve note 
# It is sitting in this repo to be able to test the code locally in this package


from typing import Dict, Any
import polars as pl
import time
from polars import DataFrame
from datetime import datetime, timedelta
from supply import PyScenario
from supply import set_log_level
import os

# Local imports - since these files are in the same directory
from importer.file_metadata import FileMetadata
from importer.lsco_network_from_reports import (
    ProcessNetworkLSCOReports,
    load_input_data,
    load_scenario,
    write_landed_costs_details_to_csv,
    convert_landed_costs_to_df,
    summarize_landed_costs,
    group_landed_costs_by_period,
    write_landed_costs_by_period_to_csv
)



def run(
    inputs: Dict[str, DataFrame],
    parameters: Dict[str, Any],
    configs: Dict[str, Any]
) -> Dict[str, DataFrame]:

    # Extract all dataframes
    consumption_df = inputs["consumption_report"]
    production_df = inputs["production_report"]
    period_df = inputs["time_period"]
    demand_df = inputs["demand_flow_report"]
    if "on_hand_stock" in inputs:
        on_hand_df = inputs["on_hand_stock"]
    else:
        on_hand_df = None
    lane_details_df = inputs["lane_details_report"]
    loc_prod_df = inputs["location_product_flow_report"]
    prod_line_util_df = inputs["production_line_utilization_report"]
    locations_df = inputs["location_flow_report"]
    procurement_df = inputs["procurement_report"]

    # Get scenario IDs from execution_summary_df if available
    scenario_ids = []
    if "execution_parameters" in inputs and inputs["execution_parameters"] is not None:
        execution_parameters_df = inputs["execution_parameters"]
        scenario_ids = execution_parameters_df.get_column("auto_scenario_id").unique().to_list()
        print(f"Found {len(scenario_ids)} scenarios in execution parameters: {scenario_ids}")
    else:
        print("Warning: execution_parameters not found or is None. Using 'Base' as the only scenario.")
        scenario_ids = ["Base"]

    # Initialize empty DataFrames to store results from all scenarios
    all_landed_costs_df = None
    all_landed_costs_by_period_df = None
    all_summary_df = None

    start_time = time.time()

    for scenario_id in scenario_ids:
        print(f"\nProcessing scenario: {scenario_id}")
        
        # Only filter if there are multiple scenarios
        if len(scenario_ids) > 1:
            # Filter dataframes for current scenario
            # Note: period_df doesn't have scenario_id
            scenario_consumption_df = consumption_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_production_df = production_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_demand_df = demand_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_lane_details_df = lane_details_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_loc_prod_df = loc_prod_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_prod_line_util_df = prod_line_util_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_locations_df = locations_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_procurement_df = procurement_df.filter(pl.col("auto_scenario_id") == scenario_id)
            scenario_execution_parameters_df = execution_parameters_df.filter(pl.col("auto_scenario_id") == scenario_id)

            # Check if any of the filtered dataframes are empty
            if scenario_demand_df.is_empty():
                print(f"Warning: No data found for scenario {scenario_id} in demand flow report. Skipping scenario.")
                continue
        else:
            # Use original dataframes if there's only one scenario
            scenario_consumption_df = consumption_df
            scenario_production_df = production_df
            scenario_demand_df = demand_df
            scenario_lane_details_df = lane_details_df
            scenario_loc_prod_df = loc_prod_df
            scenario_prod_line_util_df = prod_line_util_df
            scenario_locations_df = locations_df
            scenario_procurement_df = procurement_df
            scenario_execution_parameters_df = execution_parameters_df

        # Initialize processor for this scenario
        processor = ProcessNetworkLSCOReports(folder_path=None, auto_scenario_id=scenario_id, enable_landed_cost=True)

        # Calculate landed costs for this scenario
        # Also pass execution_parameters_df to the load_scenario function later
        landed_costs = load_scenario(
            processor,
            scenario_consumption_df,
            scenario_production_df,
            period_df,  # period_df is not filtered as it doesn't have scenario_id
            scenario_demand_df,
            on_hand_df,  # on_hand_df might be None
            scenario_lane_details_df,
            scenario_loc_prod_df,
            scenario_prod_line_util_df,
            scenario_locations_df,
            scenario_procurement_df,
            scenario_id,
            enable_landed_cost=True
        )

        print(f"Size of landed_costs: {len(landed_costs)}")

        print(f"=== Cost To Serve Analysis for Scenario {scenario_id} ===")
        
        # Convert to DataFrame and add scenario_id column as first column
        time_start = time.time()
        landed_costs_df = convert_landed_costs_to_df(landed_costs)
        landed_costs_df = landed_costs_df.with_columns(pl.lit(scenario_id).alias("auto_scenario_id"))
        # Reorder columns to put auto_scenario_id first
        landed_costs_df = landed_costs_df.select(["auto_scenario_id"] + [col for col in landed_costs_df.columns if col != "auto_scenario_id"])
        time_end = time.time()
        print(f"Time taken to convert landed costs to DataFrame: {time_end - time_start} seconds")
        
        # Create grouped by period DataFrame
        time_start = time.time()
        landed_costs_by_period_df = group_landed_costs_by_period(landed_costs_df)
        landed_costs_by_period_df = landed_costs_by_period_df.with_columns(pl.lit(scenario_id).alias("auto_scenario_id"))
        # Reorder columns to put auto_scenario_id first
        landed_costs_by_period_df = landed_costs_by_period_df.select(["auto_scenario_id"] + [col for col in landed_costs_by_period_df.columns if col != "auto_scenario_id"])
        time_end = time.time()
        print(f"Time taken to group by period: {time_end - time_start} seconds")
        
        # Create summary DataFrame
        time_start = time.time()
        summary_df = summarize_landed_costs(landed_costs_by_period_df)
        summary_df = summary_df.with_columns(pl.lit(scenario_id).alias("auto_scenario_id"))
        # Reorder columns to put auto_scenario_id first
        summary_df = summary_df.select(["auto_scenario_id"] + [col for col in summary_df.columns if col != "auto_scenario_id"])
        time_end = time.time()
        print(f"Time taken to create summary: {time_end - time_start} seconds")

        # Append to combined results
        if all_landed_costs_df is None:
            all_landed_costs_df = landed_costs_df
            all_landed_costs_by_period_df = landed_costs_by_period_df
            all_summary_df = summary_df
        else:
            all_landed_costs_df = pl.concat([all_landed_costs_df, landed_costs_df])
            all_landed_costs_by_period_df = pl.concat([all_landed_costs_by_period_df, landed_costs_by_period_df])
            all_summary_df = pl.concat([all_summary_df, summary_df])

    end_time = time.time()
    print(f"\nTotal time taken for all scenarios: {end_time - start_time} seconds")
    
    return {
        "landed_costs_details": all_landed_costs_df,
        "landed_costs_summary": all_summary_df,
        "landed_costs_by_period": all_landed_costs_by_period_df
    }



def load_data_and_calculate(dataset_path, parameters, scenario_id):

    scenario_skus = {}
    #dataset_path = "tests/landed_cost_datasets/toy1"
    #dataset_path = "/Users/<user_name>/Downloads/MDLZ ON"
    
    print(f"Loading scenario {scenario_id}...")
    processor, consumption_df, production_df, period_df, demand_df, on_hand_df, lane_details_df, loc_prod_df, prod_line_util_df, locations_df, procurement_df, execution_parameters_df = load_input_data(dataset_path, scenario_id)

    inputs = {}

    inputs["consumption_report"] = consumption_df
    inputs["production_report"] = production_df
    inputs["time_period"] = period_df
    inputs["demand_flow_report"] = demand_df
    inputs["on_hand_stock"] = on_hand_df
    inputs["lane_details_report"] = lane_details_df
    inputs["location_product_flow_report"] = loc_prod_df
    inputs["production_line_utilization_report"] = prod_line_util_df
    inputs["location_flow_report"] = locations_df
    inputs["procurement_report"] = procurement_df
    inputs["execution_parameters"] = execution_parameters_df

    outputs = run(inputs, parameters, None)
    return outputs
    
    


if __name__ == "__main__":

    DATASET_PATH = os.getenv("DATASET_PATH", "tests/landed_cost_datasets/toy1")
    #DATASET_PATH = os.getenv("DATASET_PATH", "tests/experiments/landed_cost/exxon_multi_sim")
    #DATASET_PATH = os.getenv("DATASET_PATH", "tests/experiments/landed_cost/sp_test")
    #DATASET_PATH = os.getenv("DATASET_PATH", "tests/experiments/landed_cost/ccc_large")

    parameters = {
        "test_parameter": "test_value",
    }
    scenario_id= "Base" # Currently hardcoded to Base. Read from one of the input files
    
    outputs = load_data_and_calculate(DATASET_PATH, parameters, None)


    #write_landed_costs_details_to_csv(outputs["landed_costs_details"])
    #write_landed_costs_by_period_to_csv(outputs["landed_costs_by_period"])
    outputs["landed_costs_summary"].write_csv('landed_costs_summary.csv')
    print(f"Landed costs summary written to landed_costs_summary.csv")


    
