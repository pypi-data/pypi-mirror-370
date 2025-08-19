import os
import json
import polars as pl
from datetime import datetime, timedelta
from supply import PyResource, PySKU, PyOperation, PyMultiStepProcess, PyDemandPlan, PyLocation, PyDemand
from supply import get_all_operations, get_all_skus, get_all_resources, set_periods, get_all_locations
from supply import calculate_landed_costs, calculate_landed_costs_bulk
from supply import levelize_supply_chain
from supply import PyScenario
from importer.file_metadata import FileMetadata
from supply import set_log_level
from supply import PyScenario

import time

# Set log level to info
try:
    set_log_level("INFO")
except Exception as e:
    print(f"Log level already set")

# This is common code that is triggered both from the generate_landed_cost.py and generate_graph.py
# The only difference is that generate_landed_cost.py enables landed cost calculations
# Also from Landed Cost the "run" function get all scenarios in every frame and then process them one ny one
# For graphs we also use this class to read the csvs for the required scenario only
class ProcessNetworkLSCOReports:
    def __init__(self, folder_path, auto_scenario_id="Base", enable_landed_cost=False):
        """Initialize with the path to the folder containing CSV files and JSON parameters.
        
        Args:
            folder_path (str): Path to the folder containing LSCO CSV files
            auto_scenario_id (str): Scenario ID to process
            enable_landed_cost (bool): Whether to enable landed cost calculations
        """
        self.folder_path = folder_path
        self.separator = "@"
        self.auto_scenario_id = auto_scenario_id
        self.enable_landed_cost = enable_landed_cost
        self.on_hand_inventory_date = "1970-01-01"
        
        # Load all required CSV files upfront
        self.dataframes = {}
        if folder_path is None:
            return
        
        self.required_files = [
            "consumption_report.csv",
            "production_report.csv",
            "time_period.csv",
            "demand_flow_report.csv",
            "on_hand_stock.csv",
            "lane_details_report.csv",
            "location_product_flow_report.csv" if self.enable_landed_cost else None,
            "production_line_utilization_report.csv" if self.enable_landed_cost else None,
            "location_flow_report.csv" if self.enable_landed_cost else None,
            "procurement_report.csv" if self.enable_landed_cost else None,
            "execution_parameters.csv" if self.enable_landed_cost else None
        ]
        
        for file in self.required_files:
            if file is not None:
                self.read_csv_to_dataframe(file)

    def read_csv_to_dataframe(self, filename: str) -> pl.DataFrame:
        """Read a CSV file into a Polars DataFrame using predefined metadata.
        
        Args:
            filename (str): Name of the CSV file (without path)
            
        Returns:
            pl.DataFrame: The loaded DataFrame or None if file doesn't exist
            
        Raises:
            ValueError: If required columns are missing from the file
        """
        file_path = os.path.join(self.folder_path, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found")
            return None
            
        # Get file configuration
        file_config = FileMetadata.get_file_config(filename)
        
        try:
            # Read CSV with specified data types
            df = pl.read_csv(
                file_path,
                schema_overrides=file_config['dtypes']
            )
            
            # Validate required columns
            missing_cols = [
                col for col in file_config['required_columns'] 
                if col not in df.columns
            ]
            if missing_cols:
                raise ValueError(
                    f"Missing required columns in {filename}: {missing_cols}"
                )
            
            # Filter by scenario if applicable
            if self.auto_scenario_id != None:
                if "auto_scenario_id" in df.columns:
                    df = df.filter(pl.col("auto_scenario_id") == self.auto_scenario_id)
            else:
                print(f"Note: auto_scenario_id is None. Reading all scenarios.")
                
            self.dataframes[filename] = df
            return df
            
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            raise


    # This function may need to change. We may decide to read active scenarios from auto scenario
    def get_distinct_scenarios(folder_path) -> list[str]:
        # Read all rows of kpi.csv
        try:
            kpi_df = pl.read_csv(os.path.join(folder_path, "kpi.csv"))
        except Exception as e:
            print(f"Error reading kpi.csv. Assuming only Base scenario: {str(e)}")
            return ["Base"]
        # Get all unique scenario_ids
        scenario_ids = kpi_df["auto_scenario_id"].unique()
        # convert to string
        scenario_ids = [str(scenario_id) for scenario_id in scenario_ids]
        return scenario_ids



    def create_multi_step_process_objects_from_consumption_report(self, consumption_df: pl.DataFrame, scenario_id: str) -> dict:
        """Load consumption_report.csv and create PyOperation, PyMultiStepProcess, PySKU, and PyResource objects.
        At the end of this we know how many steps are there in each process, so that we can generate the manufacturing network
        Currently the order of the steps is not important.
        Note: We do not need to process all records. Ideally we just need one period per process.

        
        Args:
            consumption_df (pl.DataFrame): The consumption report DataFrame
        Returns:
            dict: Dictionary containing created objects with the following keys:
                  - 'skus': Dictionary of PySKU objects
                  - 'resources': Dictionary of PyResource objects
                  - 'processes': Dictionary of PyMultiStepProcess objects
                  - 'operations': Dictionary of PyOperation objects
        """
        
        if consumption_df is None:
            print("Error: consumption_report.csv could not be loaded")
            return {
                'consumption_df': None,
                'skus': {},
                'resources': {},
                'processes': {},
                'operations': {}
            }
        
        # Dictionaries to store created objects
        skus = {}
        resources = {}
        processes = {}
        operations = {}
        
        # Process each row to create objects
        for row in consumption_df.iter_rows(named=True):
            plant = row["plant"]
            product = row["product"]
            input_product = row["input_product"]
            line = row["line"]
            process_id = row["process_id"]
            operation_id = row["operation_id"]
            bom = row["bom"]
            
            # Create SKUs:
            # 1. Product SKU: product@plant
            product_sku_key = f"{product}{self.separator}{plant}"
            if product_sku_key not in skus:
                sku = PySKU.create(product, plant, scenario_id)
                skus[product_sku_key] = sku
            
            # 2. Input Product SKU: input_product@plant
            if input_product and input_product.strip():  # Only create if input_product exists
                input_sku_key = f"{input_product}{self.separator}{plant}"
                if input_sku_key not in skus:
                    sku = PySKU.create(input_product, plant, scenario_id)
                    skus[input_sku_key] = sku
            
            # Create Resource: line@plant
            resource_key = f"{line}{self.separator}{plant}"
            if resource_key not in resources and line and line.strip():
                resource = PyResource(resource_key, scenario_id)
                resources[resource_key] = resource
            
            # Create MultiStepProcess: process@bom@plant
            process_key = f"{process_id}{self.separator}{bom}{self.separator}{product}{self.separator}{plant}"
            if process_key not in processes and process_id and process_id.strip():
                # Using default values for lead_time (1), min_lot (1), and increment (1)
                process = PyMultiStepProcess(process_key, 1, 1, 1, scenario_id)
                processes[process_key] = process
            
            # Create Operation: process@operation@bom@plant
            operation_key = f"{process_id}{self.separator}{operation_id}{self.separator}{bom}{self.separator}{product}{self.separator}{plant}"
            if operation_key not in operations and operation_id and operation_id.strip():
                # Using default values for lead_time (1), min_lot (1), and increment (1)
                operation = PyOperation(operation_key, 0, 0, 0, scenario_id)
                operation.category = "Manufacturing"
                
                # Add the operation to the appropriate process
                if process_key in processes:
                    processes[process_key].add_step(operation)
                
                # Connect operation to resource
                if resource_key in resources:
                    operation.add_resource(resources[resource_key], 1.0)

                operations[operation_key] = operation

        
        return {
            'consumption_df': consumption_df,
            'skus': skus,
            'resources': resources,
            'processes': processes,
            'operations': operations
        }
    
    def generate_manufacturing_network(self, consumption_df: pl.DataFrame, skus: dict, resources: dict, 
                                    processes: dict, operations: dict, scenario_id: str):
        """_summary_

        Args:
            consumption_df (_type_): _description_
            skus (_type_): _description_
            resources (_type_): _description_
            processes (_type_): _description_
        """
        for row in consumption_df.iter_rows(named=True):
            plant = row["plant"]
            product = row["product"]
            input_product = row["input_product"]
            line = row["line"]
            process_id = row["process_id"]
            operation_id = row["operation_id"]
            bom = row["bom"]


            process_key = f"{process_id}{self.separator}{bom}{self.separator}{product}{self.separator}{plant}"
            if process_key not in processes:
                continue
            
            # Create Operation: process@operation@bom@plant
            operation_key = f"{process_id}{self.separator}{operation_id}{self.separator}{bom}{self.separator}{product}{self.separator}{plant}"
            if operation_key not in operations:
                continue

            operation = operations[operation_key]
            process = processes[process_key]
            is_first_step = process.is_first_step(operation)
            is_last_step = process.is_last_step(operation)

            # Add input/output flows if relevant
            if input_product and input_product.strip():
                input_sku_key = f"{input_product}{self.separator}{plant}"
                if input_sku_key in skus:
                    # Add consumption flow
                    consumption_qty = float(row["consumption_qty"]) if row["consumption_qty"] else 1.0
                    production_qty = float(row["production_qty"]) if row["production_qty"] else 1.0
                    # Calculate quantity per
                    qty_per = consumption_qty / production_qty if production_qty > 0 else 1.0
                    if is_first_step:
                        operation.add_bom_component(skus[input_sku_key], qty_per)
            
            # For the producing operation, add the output
            if product and product.strip():
                product_sku_key = f"{product}{self.separator}{plant}"
                if product_sku_key in skus:
                    # Add produce flow
                    if is_last_step:
                        operation.add_produce_flow(skus[product_sku_key], 1.0)


    def create_transportation_network(self, period_df, skus, resources, operations, lane_details_df, scenario_id: str):
        """Create transportation network from lane_details_report.csv.
        
        Args:
            skus (dict): Dictionary of existing SKUs
            resources (dict): Dictionary to store created resources
            operations (dict): Dictionary to store created operations
        """
        # Do we need internal movements? If we need them then the period needs to be part of the node names (e.g. product@plant@period)
        lane_details_df = lane_details_df.filter(pl.col('mode') != 'Internal')

        if lane_details_df is None or lane_details_df.is_empty():
            print("No lane details report data found")
            return
                
        # Convert to datetime and calculate lead time
        lane_details_df = lane_details_df.with_columns([
            pl.col('departure_date').str.strptime(pl.Datetime, format='%Y-%m-%d %H:%M:%S.%3f', strict=False),
            pl.col('arrival_date').str.strptime(pl.Datetime, format='%Y-%m-%d %H:%M:%S.%3f', strict=False)
        ])

        period_dict = self.get_period_dict(period_df)
        
        # Iterate through rows
        for row in lane_details_df.iter_rows(named=True):
            # Create source and destination SKUs
            product = row['product']
            origin = row['origin']
            destination = row['destination']
            
            # Create SKU keys
            source_sku_key = f"{product}{self.separator}{origin}"            
            # Create SKUs if they don't exist
            if source_sku_key not in skus:
                skus[source_sku_key] = PySKU.create(product, origin, scenario_id)

            dest_sku_key = f"{product}{self.separator}{destination}"
            if dest_sku_key not in skus:
                skus[dest_sku_key] = PySKU.create(product, destination, scenario_id)
            
            # Calculate lead time in days
            departure_date = period_dict[row['departure_period']]['start_date']
            arrival_date = period_dict[row['arrival_period']]['start_date']
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
            arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d')
            if departure_date is None or arrival_date is None:
                lead_time = 0
            else:
                lead_time = (arrival_date - departure_date).days
                if lead_time < 0:
                    lead_time = 0
            
            # Create operation key and resource key
            asset = row['asset']
            mode = row['mode']
            service = row['service']
            
            operation_key = f"{product}{self.separator}{origin}{self.separator}{destination}{self.separator}{asset}{self.separator}{mode}{self.separator}{service}"
            resource_key = f"{origin}{self.separator}{destination}{self.separator}{asset}{self.separator}{mode}{self.separator}{service}"
            
            # Create transportation operation if it doesn't exist
            if operation_key not in operations:
                operation = PyOperation(operation_key, lead_time, 0, 0, scenario_id)
                operation.category = "Distribution"
                # Add consume and produce flows
                operation.add_consume_flow(skus[source_sku_key], 1.0)
                operation.add_produce_flow(skus[dest_sku_key], 1.0)
                operations[operation_key] = operation

            # Create transportation resource if it doesn't exist
            if resource_key not in resources:
                resource = PyResource(resource_key, scenario_id)
                resources[resource_key] = resource
            
            # TODO Check this: Optimize Network does not need to connect transportation operations to resources
            #if resource_key in resources:
            #    operations[operation_key].add_resource(resources[resource_key], 1.0)

            # Set up cost structure if landed cost is enabled
            if self.enable_landed_cost:
                try:
                    flow_qty = float(row['flow_qty'])
                    transportation_cost = float(row['transportation_cost'])
                    variable_cost = float(row['variable_cost'])
                    fixed_cost = float(row['fixed_cost'])
                    unit_cost = (transportation_cost) / flow_qty if flow_qty > 0 else 0.0
                    # convert it to yyyy-mm-dd format
                    departure_date = departure_date.strftime('%Y-%m-%d')
                    operation.set_cost_structure(start_date=departure_date, unit_setup_cost=0.0, unit_cost=unit_cost)  # fixed_cost = 0.0 for transportation
                except Exception as e:
                    print(f"Warning: Could not set up shipping cost structure for operation {operation_key}: {str(e)}")


        print(f"\nTransportation Network Summary:")
        print(f"SKUs created/updated: {len(skus)}")
        print(f"Resources created: {len(resources)}")
        print(f"Operations created: {len(operations)}")

        return {
            'transportation_df': lane_details_df,
            'skus': skus,
            'resources': resources,
            'operations': operations
        }


    def convert_date_format(self, period_dict: dict) -> dict:
        """Convert dates in period_dict from dd/mm/yyyy to yyyy-mm-dd format.
        
        Args:
            period_dict (dict): Dictionary with period dates
            
        Returns:
            dict: Updated period dictionary with converted dates
        """
        # Create a new dictionary to store converted dates
        converted_dict = {}
        
        for period_id, dates in period_dict.items():
            start_date = dates['start_date']
            end_date = dates['end_date']
            
            # Check if dates are in dd/mm/yyyy format
            if '/' in start_date:
                # Convert dates from dd/mm/yyyy to yyyy-mm-dd
                start_datetime = datetime.strptime(start_date, '%m/%d/%Y')
                end_datetime = datetime.strptime(end_date, '%m/%d/%Y')
                
                converted_dict[period_id] = {
                    'start_date': start_datetime.strftime('%Y-%m-%d'),
                    'end_date': end_datetime.strftime('%Y-%m-%d')
                }
            else:
                # If dates are already in correct format, keep them as is
                converted_dict[period_id] = dates

        if self.enable_landed_cost:
            # Store the period information in the global period storage
            set_periods(converted_dict)
            pass
            
        return converted_dict
    
    def setup_production_costs(self, operations: dict, prod_df: pl.DataFrame, period_dict: dict):
        """Set up production costs from production_report
        
        Args:
            operations (dict): Dictionary of operations
            prod_df (pl.DataFrame): Production report dataframe
        """
        if not self.enable_landed_cost:
            return

        if prod_df is None or prod_df.is_empty():
            print("No production report data found for cost setup")
            return

        # Process each production record
        for row in prod_df.iter_rows(named=True):
            try:
                # Get required fields
                process_id = row['process_id']
                operation_id = row['operation_id']
                bom = row['bom']
                product = row['product']
                plant = row['plant']
                period = str(row['period'])
                production_qty = float(row['production_qty'])
                production_cost = float(row['production_cost'])
                # Create operation key
                operation_key = f"{process_id}{self.separator}{operation_id}{self.separator}{bom}{self.separator}{product}{self.separator}{plant}"
                if operation_key in operations:
                    operation = operations[operation_key]
                    # Calculate unit cost
                    unit_cost = production_cost / production_qty if production_qty > 0 else 0.0
                    # Filter for the specific period and get the start date
                    start_date = period_dict[period]['start_date']
                    # Set up cost structure on the operation
                    operation.set_cost_structure(start_date=start_date, unit_setup_cost=0.0, unit_cost=unit_cost)  # setup_cost = 0.0 for now
            except Exception as e:
                print(f"Warning: Could not set up production cost structure for operation {operation_key}: {str(e)}")
        print("Completed setting up production costs")


    def get_period_dict(self, period_df: pl.DataFrame):
        period_dict = {}
        if period_df is not None:
            for row in period_df.iter_rows(named=True):
                period_id = row['period_id']
                start_date = row['start_datetime'][:10]
                end_date = row['end_datetime'][:10]
                period_dict[period_id] = {'start_date': start_date, 'end_date': end_date}
            period_dict = self.convert_date_format(period_dict)
        return period_dict


    def create_operation_plans(self, operations: dict, prod_df: pl.DataFrame, period_df: pl.DataFrame, transport_df: pl.DataFrame, skus: dict, resources: dict, scenario_id: str) -> dict:
        """Create manufacturing operation plans from production_report.csv."""
        # Convert period_df to dictionary
        period_dict = {}

        if period_df is not None:
            for row in period_df.iter_rows(named=True):
                period_id = row['period_id']
                start_date = row['start_datetime'][:10]
                end_date = row['end_datetime'][:10]
                period_dict[period_id] = {'start_date': start_date, 'end_date': end_date}
            
            period_dict = self.convert_date_format(period_dict)
 
        # Process manufacturing operation plans
        if prod_df is not None and not prod_df.is_empty():
            # Create operation plans for manufacturing
            for row in prod_df.iter_rows(named=True):
                if row['process_id'] == "":
                    row['process_id'] = "DefaultProcess"
                if row['operation_id'] == "":
                    row['operation_id'] = "DefaultOperation"

                operation_key = f"{row['process_id']}{self.separator}{row['operation_id']}{self.separator}{row['bom']}{self.separator}{row['product']}{self.separator}{row['plant']}"
                
                #To find start date of the operation, use the period_id from the production_report.csv and find the start_date from period_details.csv
                period_id = str(row['period'])
                period_start_date = period_dict[period_id]['start_date']
                # When we vectorize the production report, we will make it more efficient and use actual end date
                # by converting the production_time to hours(actually floored to days) and adding it to the start date
                # but that could disturb pegging since the donwstream transportation may want to start at period start
                production_end_date = period_start_date
                if operation_key in operations:
                    operation = operations[operation_key]
                    operation.create_operation_plan(period_start_date, production_end_date, float(row['production_qty']))
                else:
                    # This is the case when no data was found in consumption_df owing to BOM being absent
                    # In this case we will create an operation plan with a lead time of 0
                    operation = PyOperation(operation_key, 0, 0, 0, scenario_id)
                    operations[operation_key] = operation
                    operation.category = "Manufacturing"
                    product_sku_key = f"{row['product']}{self.separator}{row['plant']}"
                    if product_sku_key in skus:
                        operation.add_produce_flow(skus[product_sku_key], 1.0)
                        skus[product_sku_key].process_sources()
                        operation.create_operation_plan(period_start_date, production_end_date, float(row['production_qty']))

                    # now also attach the resource to the operation. No need to check if these resources exost or not
                    resource_key = f"{row['line']}{self.separator}{row['plant']}"
                    res = PyResource(resource_key, scenario_id)
                    operation.add_resource(res, 1.0)
                    resources[resource_key] = res
    
        # Now we need to create operation plans for transportation     
        for row in transport_df.iter_rows(named=True):
            operation_key = f"{row['product']}{self.separator}{row['origin']}{self.separator}{row['destination']}{self.separator}{row['asset']}{self.separator}{row['mode']}{self.separator}{row['service']}"
            transport_start_date = row['departure_date'][:10] # TODO: Evaluate if we need to use departure_period.start_date
            transport_end_date = row['arrival_date'][:10] # TODO: Evaluate if we need to use arrival_period.start_date
            if operation_key in operations:
                operation = operations[operation_key]
                operation.create_operation_plan(transport_start_date, transport_end_date, float(row['flow_qty']))

        print(f"\nOperation Plans Summary:")
        total_plans = sum(len(op.get_operation_plans()) for op in operations.values())
        print(f"Total operation plans created: {total_plans}")
        return period_dict


    def create_demand_plans(self, skus: dict, period_dict: dict, demand_df: pl.DataFrame, scenario_id: str):
        """Create demands and demand plans from demand_flow_report.csv.
        
        Args:
            skus (dict): Dictionary of SKUs keyed by 'product@location'
        """
        if demand_df is None:
            return
        
        
        # Track created demands to avoid duplicates
        created_demands = set()
        
        # if demand column is not present then add this column demand and copy it from  demand_satisfied
        if not 'demand' in demand_df.columns:
            demand_df = demand_df.with_columns([
                pl.col('demand_satisfied').alias('demand')
            ])
        
        # Process each demand row
        for row in demand_df.iter_rows(named=True):
            product = row['product']
            location = row['location']
            period_id = str(row['period'])
            quantity = float(row['demand'])
            demand_satisfied = float(row['demand_satisfied'])
            # Skip if quantity is 0
            if quantity == 0:
                continue
            # Create SKU key
            sku_key = f"{product}{self.separator}{location}"
            # Skip if SKU doesn't exist
            if sku_key not in skus:
                continue
            # Create unique demand ID
            demand_id = f"D_{product}_{location}_{period_id}"
            # Skip if already created
            if demand_id in created_demands:
                continue
            # Get request date from period dictionary
            request_date = period_dict[period_id]['start_date']
            # Create demand with default max_lateness of 0
            demand_sku = skus[sku_key]
            demand = PyDemand(id=demand_id,quantity=quantity,request_date=request_date,max_lateness=0,sku=demand_sku, scenario_id=scenario_id)
            demand_plan = demand.create_demand_plan(demand_satisfied, request_date)
            demand_sku.add_demand_plan(demand_plan)
            created_demands.add(demand)
        
        print(f"\nDemand Plans Summary:")
        print(f"Total demands created: {len(created_demands)}")


    def earliest_period_start(self, period_dict):
        return min(period_dict.values(), key=lambda x: x['start_date'])['start_date']

    def add_inventory_on_most_upstream_skus(self, skus, period_dict):
        earliest_period_start = self.earliest_period_start(period_dict)
        for sku in skus.values():
            if len(sku.producing_operations()) == 0:
                sku.add_on_hand(earliest_period_start, float("inf"))

    def create_on_hand_inventory(self, skus: dict, on_hand_df: pl.DataFrame, period_dict: dict):
        """Create on-hand inventory from on_hand_stock.csv.
        
        Args:
            skus (dict): Dictionary of SKUs keyed by 'product@location'
        """
        if on_hand_df is None:
            print("Warning: on_hand_stock.csv not found")
            return
    
        # Find first period start date
        first_period_start_date = self.earliest_period_start(period_dict)

        # Process each on-hand row
        for row in on_hand_df.iter_rows(named=True):
            product = row['product']
            location = row['location']
            quantity = float(row['qty'])

            try:
                date = row['date']
            except:
                date = "1970-01-01"
            
            # Create SKU key
            sku_key = f"{product}{self.separator}{location}"
            
            # Skip if SKU doesn't exist
            if sku_key not in skus:
                print(f"Warning: Product Location {sku_key} not found for on-hand inventory. Creating it now.")
                sku = PySKU.create(product, location, scenario_id=self.auto_scenario_id)
                skus[sku_key] = sku
            
            # Add on-hand inventory to SKU
            sku = skus[sku_key]
            sku.add_on_hand(first_period_start_date, quantity)


    def sku_costs(self, loc_prod_df: pl.DataFrame, skus: dict, period_dict: dict, storage_cost_driver: str):
        """Set up handling costs from location_product_flow_report.csv.
        Note that transportation costs to customer locatiosn are not handled here since
        location_product_flow_report has information only about products at Warehouse locations.
        
        Args:
            skus (dict): Dictionary of SKUs
            period_dict (dict): Dictionary mapping period IDs to dates
        """
        if not self.enable_landed_cost:
            return

        if loc_prod_df is None or loc_prod_df.is_empty():
            print("No location product flow report data found for cost setup")
            return
        

        # Process each record
        for row in loc_prod_df.iter_rows(named=True):
            try:
                # Get required fields
                product = row['product']
                location = row['location']
                period = str(row['period'])
                
                # Get quantities and costs
                inbound_qty = float(row['inbound_qty'])
                outbound_qty = float(row['outbound_qty'])
                throughput_qty = float(row['throughput_qty'])
                inbound_handling_cost = float(row['inbound_handling_cost'])
                outbound_handling_cost = float(row['outbound_handling_cost'])
                throughput_cost = float(row['throughput_cost'])
                storage_cost = 0.0
                if storage_cost_driver == "average_storage_cost":
                    storage_cost = float(row['average_storage_cost'])
                else:
                    storage_cost = float(row['ending_storage_cost'])

                #if storage_cost > 0.0:
                #    print(f"Storage cost for {product}@{location}@{period} is {storage_cost}")

                # Calculate unit costs
                unit_inbound_cost = inbound_handling_cost / inbound_qty if inbound_qty > 0 else 0.0
                unit_outbound_cost = outbound_handling_cost / outbound_qty if outbound_qty > 0 else 0.0
                unit_throughput_cost = throughput_cost / throughput_qty if throughput_qty > 0 else 0.0

                start_date = period_dict[period]['start_date']
                # Create SKU key and get SKU
                sku_key = f"{product}{self.separator}{location}"
                if sku_key in skus:
                    sku = skus[sku_key]
                    # Set up cost structure on the SKU
                    sku.set_cost_structure(start_date=start_date, unit_inbound_cost=unit_inbound_cost, unit_outbound_cost=unit_outbound_cost, unit_throughput_cost=unit_throughput_cost, storage_cost=storage_cost)
                else:
                    # This is for cases where SKU is isolated - no BOM/no operation producing it. Just Add on Hand inventory
                    sku = PySKU.create(product, location, scenario_id=self.auto_scenario_id)
                    skus[sku_key] = sku
                    sku.set_cost_structure(start_date=start_date, unit_inbound_cost=unit_inbound_cost, unit_outbound_cost=unit_outbound_cost, unit_throughput_cost=unit_throughput_cost, storage_cost=storage_cost)

            except Exception as e:
                print(f"Warning: Could not set up handling costs for SKU {product}@{location}: {str(e)}")
        print("Completed setting up handling costs")


    def setup_resource_costs(self, prod_line_util_df: pl.DataFrame, resources: dict, period_dict: dict):
        """Set up resource costs from production_line_utilization_report.csv.
        
        Args:
            resources (dict): Dictionary of Resources
            period_dict (dict): Dictionary mapping period IDs to dates
        """
        if prod_line_util_df is None:
            print("No production line utilization report data found for resource cost setup")
            return

        # Process each record
        for row in prod_line_util_df.iter_rows(named=True):
            try:
                # Get required fields
                plant = row['plant']
                line = row['line']
                period = str(row['period'])
                # Get quantities and costs
                production_qty = float(row['production_qty'])
                fixed_cost = float(row['fixed_cost'])
                variable_cost = float(row['variable_cost'])
                unit_cost = (variable_cost + fixed_cost) / production_qty if production_qty > 0 else 0.0
                # Create resource key
                resource_key = f"{line}{self.separator}{plant}"
                if resource_key in resources:
                    resource = resources[resource_key]
                    start_date = period_dict[period]['start_date']
                    # There is no sepecrate speical logic for fixed cost. So just pass in in unit cost
                    resource.set_cost_structure(start_date=start_date, unit_fixed_cost=0.0, unit_cost=unit_cost)
            except Exception as e:
                print(f"Warning: Could not set up resource costs for resource {resource_key}: {str(e)}")
        print("Completed setting up resource costs")


    def setup_location_costs(self, locations_df: pl.DataFrame, period_dict: dict):
        """Set up location costs from location_flow_report.csv.
        
        Args:
            locations_df (pl.DataFrame): Location flow report dataframe
            period_dict (dict): Dictionary mapping period IDs to dates
        """
        if locations_df is None:
            print("No location flow report data found for location cost setup")
            return
        
        locations = {}
        all_locations = get_all_locations(scenario_id=self.auto_scenario_id)


        # Process each record
        for row in locations_df.iter_rows(named=True):
            try:
                # Get required fields
                location = row['location']
                period = str(row['period'])
                location =PyLocation.fetch(location, self.auto_scenario_id)
                # Get quantities and costs
                inbound_qty = float(row['inbound_qty'])
                outbound_qty = float(row['outbound_qty'])
                unit_cost = float(row['fixed_operating_cost']) / (inbound_qty + outbound_qty) if inbound_qty + outbound_qty > 0 else 0.0
                start_date = period_dict[period]['start_date']  
                location.set_cost_structure(start_date=start_date, unit_cost=unit_cost)  # This is fixed operating cost
            except Exception as e:
                print(f"Warning: Could not set up location costs for location {location}: {str(e)}")
        print("Completed setting up location costs")


    def setup_sourcing_costs(self, procurement_df: pl.DataFrame, period_dict: dict):
        """Set up sourcing costs from procurement_report.csv.
        
        Args:
            procurement_df (pl.DataFrame): Procurement report dataframe
            period_dict (dict): Dictionary mapping period IDs to dates
        """
        if procurement_df is None:
            print("No procurement report data found for sourcing cost setup")
            return
        

        # Process each record
        for row in procurement_df.iter_rows(named=True):
            try:
                # Get required fields
                product = row['product']
                location = row['vendor']
                period = str(row['period'])
                sourcing_qty = float(row['sourcing_qty'])
                sourcing_cost = float(row['sourcing_cost']) 
                unit_sourcing_cost = sourcing_cost / sourcing_qty if sourcing_qty > 0 else 0.0
                start_date = period_dict[period]['start_date']
                sku = PySKU.create(product, location, scenario_id=self.auto_scenario_id)
                # Set up cost structure on the SKU since this is a vendor SKU
                sku.set_cost_structure(start_date=start_date, unit_inbound_cost=0.0, unit_outbound_cost=0.0, unit_throughput_cost=0.0, storage_cost=0.0)
                sku.set_sourcing_cost(start_date, unit_sourcing_cost)
            except Exception as e:
                print(f"Warning: Could not set up sourcing costs for SKU {product}@{location}: {str(e)}")
        print("Completed setting up sourcing costs")


# This is a helper function to summarize the landed costs
def summarize_landed_costs(landed_costs_df: pl.DataFrame) -> pl.DataFrame:
    """Create a summary of total costs across all records, grouped by target type (Demand/Stock).
    
    Args:
        landed_costs_df: DataFrame containing detailed landed cost data
        
    Returns:
        pl.DataFrame: DataFrame with Cost type, Target type, and total Value
    """
    # List of costs to summarize
    costs = [
        ('Inbound Cost', 'inbound_cost'),
        ('Outbound Cost', 'outbound_cost'),
        ('Throughput Cost', 'throughput_cost'),
        ('Storage Cost', 'storage_cost'),
        ('Production Cost', 'production_cost'),
        ('Line Cost', 'line_cost'),
        ('Shipment Cost', 'shipping_cost'),
        ('Procurement Cost', 'sourcing_cost'),
        ('Fixed Operating Cost', 'fixed_operating_cost'),
        ('Total Cost', 'total_cost'),
        ('Total Target Quantity (Demand + Stock)', 'target_quantity')
    ]
    
    # Get unique target types (Demand, Stock)
    target_types = landed_costs_df['target_type'].unique().to_list()
    
    # Create summary data for each target type
    summary_data = []
    
    for target_type in target_types:
        # Filter data for this target type
        filtered_df = landed_costs_df.filter(pl.col('target_type') == target_type)
        
        # Calculate sums for each cost type
        for cost_name, col_name in costs:
            value = filtered_df.filter(pl.col(col_name).is_finite())[col_name].sum()
            summary_data.append({
                'Target': target_type,
                'Cost': cost_name,
                'Value': f"{value:,.3f}"
            })
    
    # Add Combined target if there are multiple target types
    if len(target_types) > 1:
        for cost_name, col_name in costs:
            # Calculate total across all target types
            total_value = landed_costs_df.filter(pl.col(col_name).is_finite())[col_name].sum()
            summary_data.append({
                'Target': 'Combined',
                'Cost': cost_name,
                'Value': f"{total_value:,.3f}"
            })
    
    # Create summary DataFrame
    summary_df = pl.DataFrame(summary_data)
    
    return summary_df

def group_landed_costs_by_period(landed_costs_df: pl.DataFrame) -> pl.DataFrame:
    """Group landed costs between PID=0 records and aggregate costs efficiently.
    
    Args:
        landed_costs_df: DataFrame containing detailed landed cost data
        
    Returns:
        pl.DataFrame: Aggregated DataFrame with costs summed between PID=0 records
    """
    # Create a group ID column based on cumulative sum of PID == "0"
    df_with_groups = (
        landed_costs_df
        .with_columns([
            pl.col("parent_id").eq(0).cum_sum().alias("group_id")
        ])
    )
    
    # List of columns to sum
    sum_columns = [
        'inbound_cost', 'outbound_cost', 'throughput_cost',
        'storage_cost', 'production_cost', 'line_cost',
        'shipping_cost', 'sourcing_cost', 'fixed_operating_cost',
        'total_cost'
    ]
    
    # Create aggregation expressions
    agg_exprs = [
        pl.col('product').first(),
        pl.col('location').first(),
        pl.col('period_start_date').first(),
        pl.col('target_quantity').first(),
        pl.col('target_type').first(),
    ] + [pl.col(col).sum() for col in sum_columns]
    
    # Group and aggregate
    result_df = (
        df_with_groups
        .group_by('group_id')
        .agg(agg_exprs)
        .sort('group_id')
        .drop('group_id')
    )

    print("Total target quantity costs by period: ", result_df.sum())
    
    return result_df

def convert_landed_costs_to_df(landed_costs):
    """Convert landed costs to a Polars DataFrame efficiently.
    
    Args:
        landed_costs: Either List of landed cost objects (legacy) or Dict of columnar data (new bulk format)
        
    Returns:
        pl.DataFrame: DataFrame containing landed cost data
    """
    # Check if this is the new bulk format (dict) or legacy format (list)
    if isinstance(landed_costs, dict):
        # Fast path: Direct DataFrame creation from columnar data
        return pl.DataFrame({
            'source_product': landed_costs['source_product'],
            'source_location': landed_costs['source_location'],
            'source_quantity': landed_costs['lot_quantity'],
            'product': landed_costs['product'],
            'location': landed_costs['location'],
            'period_start_date': landed_costs['period_start_date'],
            'id': landed_costs['lot_id'],
            'parent_id': landed_costs['parent_lot_id'],
            'inbound_cost': landed_costs['inbound_cost'],
            'outbound_cost': landed_costs['outbound_cost'],
            'throughput_cost': landed_costs['throughput_cost'],
            'storage_cost': landed_costs['storage_cost'],
            'production_cost': landed_costs['production_cost'],
            'line_cost': landed_costs['line_cost'],
            'shipping_cost': landed_costs['shipping_cost'],
            'sourcing_cost': landed_costs['sourcing_cost'],
            'fixed_operating_cost': landed_costs['fixed_operating_cost'],
            'total_cost': landed_costs['total_cost'],
            'target_quantity': landed_costs['driving_qty'],
            'source_production_date': landed_costs['production_date'],
            'source_consumption_date': landed_costs['consumption_date'],
            'target_type': landed_costs['category']
        })
    
    # Legacy path: Row-by-row processing (kept for backwards compatibility)
    # Pre-allocate lists for each column
    n = len(landed_costs)
    source_products = []
    source_locations = []
    lot_quantities = []
    products = []
    locations = []
    period_start_dates = []
    lot_ids = []
    parent_lot_ids = []
    inbound_costs = []
    outbound_costs = []
    throughput_costs = []
    storage_costs = []
    production_costs = []
    line_costs = []
    shipping_costs = []
    sourcing_costs = []
    fixed_operating_costs = []
    total_costs = []
    target_quantities = []
    production_dates = []
    consumption_dates = []
    target_categories = []

    # Fill lists in a single pass
    for row in landed_costs:
        source_products.append(str(row.source_product))
        source_locations.append(str(row.source_location))
        lot_quantities.append(float(row.lot_quantity))
        products.append(str(row.product))
        locations.append(str(row.location))
        period_start_dates.append(str(row.period_start_date))
        lot_ids.append(str(row.lot_id))
        parent_lot_ids.append(str(row.parent_lot_id))
        inbound_costs.append(float(row.inbound_cost))
        outbound_costs.append(float(row.outbound_cost))
        throughput_costs.append(float(row.throughput_cost))
        storage_costs.append(float(row.storage_cost))
        production_costs.append(float(row.production_cost))
        line_costs.append(float(row.line_cost))
        shipping_costs.append(float(row.shipping_cost))
        sourcing_costs.append(float(row.sourcing_cost))
        fixed_operating_costs.append(float(row.fixed_operating_cost))
        total_costs.append(float(row.total_cost))
        target_quantities.append(float(row.driving_qty))
        production_dates.append(str(row.production_date))
        consumption_dates.append(str(row.consumption_date))
        target_categories.append(str(row.category))
    
    # Create DataFrame in one shot with pre-allocated columns
    return pl.DataFrame({
        'source_product': source_products,
        'source_location': source_locations,
        'source_quantity': lot_quantities,
        'product': products,
        'location': locations,
        'period_start_date': period_start_dates,
        'id': lot_ids,
        'parent_id': parent_lot_ids,
        'inbound_cost': inbound_costs,
        'outbound_cost': outbound_costs,
        'throughput_cost': throughput_costs,
        'storage_cost': storage_costs,
        'production_cost': production_costs,
        'line_cost': line_costs,
        'shipping_cost': shipping_costs,
        'sourcing_cost': sourcing_costs,
        'fixed_operating_cost': fixed_operating_costs,
        'total_cost': total_costs,
        'target_quantity': target_quantities,
        'source_production_date': production_dates,
        'source_consumption_date': consumption_dates,
        'target_type': target_categories
    })

def write_landed_costs_details_to_csv(landed_costs_details_df: pl.DataFrame):
    """Write landed costs DataFrame to CSV with summary totals.
    
    Args:
        landed_costs_df: Polars DataFrame containing landed cost data
    """
    # Format decimal columns to 3 decimal places
    decimal_columns = [
        'inbound_cost', 'outbound_cost', 'throughput_cost',
        'storage_cost', 'production_cost', 'line_cost',
        'shipping_cost', 'sourcing_cost', 'fixed_operating_cost',
        'total_cost', 'source_quantity', 'target_quantity'
    ]
    
    formatted_df = landed_costs_details_df.with_columns([
        pl.col(col).round(3) for col in decimal_columns
    ])
    
    # Write main data to CSV
    formatted_df.write_csv('landed_costs_details.csv')
    
    print(f"Landed costs written to landed_costs_details.csv")


def write_landed_costs_by_period_to_csv(landed_costs_by_period_df: pl.DataFrame):
    """Write landed costs by period DataFrame to CSV.
    
    Args:
        landed_costs_by_period_df: Polars DataFrame containing landed cost data
    """
    # Format decimal columns to 3 decimal places
    decimal_columns = [
        'inbound_cost', 'outbound_cost', 'throughput_cost',
        'storage_cost', 'production_cost', 'line_cost',
        'shipping_cost', 'sourcing_cost', 'fixed_operating_cost',
        'total_cost', 'target_quantity'
    ]
    
    formatted_df = landed_costs_by_period_df.with_columns([
        pl.col(col).round(3) for col in decimal_columns
    ])
    
    formatted_df.write_csv('landed_costs_by_period.csv')
    print(f"Landed costs by period written to landed_costs_by_period.csv")


# This automatically happens in studio
def load_input_data(dataset_path, auto_scenario_id, enable_landed_cost=True):
    processor = ProcessNetworkLSCOReports(dataset_path, auto_scenario_id=auto_scenario_id, enable_landed_cost=enable_landed_cost)

    # Get all required dataframes
    consumption_df = processor.dataframes.get("consumption_report.csv")
    production_df = processor.dataframes.get("production_report.csv")
    period_df = processor.dataframes.get("time_period.csv")
    demand_df = processor.dataframes.get("demand_flow_report.csv")
    on_hand_df = processor.dataframes.get("on_hand_stock.csv")
    lane_details_df = processor.dataframes.get("lane_details_report.csv")

    if processor.enable_landed_cost:
        loc_prod_df = processor.dataframes.get("location_product_flow_report.csv")
        prod_line_util_df = processor.dataframes.get("production_line_utilization_report.csv")
        locations_df = processor.dataframes.get("location_flow_report.csv")
        procurement_df = processor.dataframes.get("procurement_report.csv")
        execution_parameters_df = processor.dataframes.get("execution_parameters.csv")

    return processor, consumption_df, production_df, period_df, demand_df, on_hand_df, lane_details_df, loc_prod_df, prod_line_util_df, locations_df, procurement_df, execution_parameters_df


def load_scenario(processor, consumption_df, production_df, period_df, demand_df, on_hand_df, lane_details_df, loc_prod_df, prod_line_util_df, locations_df, procurement_df, auto_scenario_id, enable_landed_cost=False):
    """Modified to return landed costs"""

    # Create manufacturing network
    start_time = time.time()
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


    period_dict = processor.create_operation_plans(operations, production_df, period_df, lane_details_df, skus, resources, scenario_id=auto_scenario_id)

    # Set up production costs if landed cost is enabled
    if processor.enable_landed_cost:
        processor.sku_costs(loc_prod_df, skus, period_dict, "ending_storage_cost") # This could be "storage_cost" or "ending_storage_cost" or 
        processor.setup_resource_costs(prod_line_util_df, resources, period_dict)     
        processor.setup_production_costs(operations, production_df, period_dict)
        # Assumes locations are already created. Just calculate and set the unit_operating_cost for each location
        processor.setup_location_costs(locations_df, period_dict)
        processor.setup_sourcing_costs(procurement_df, period_dict)


    print("Created operation plans")
    # Now mark levels in supply chain and add consuming operations to the operations
    levelize_supply_chain(auto_scenario_id)
    print("Levelized supply chain")

    # Add on hand inventory to the skus
    # What if this causes upstream recursion to stop and therefore under report the cost of demand
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
    print(f"Time taken to create network and flows: {end_time - start_time} seconds")

    landed_costs = None
    if processor.enable_landed_cost:
        time_start = time.time()
        print(f"Calculating landed costs for scenario {auto_scenario_id}")
        # Use bulk API for 5-10x faster performance
        landed_costs = calculate_landed_costs_bulk(auto_scenario_id)
        time_end = time.time()
        print(f"Time taken to calculate landed costs: {time_end - time_start} seconds")


    # Return SKUs for processing instead of deleting them
    return landed_costs
