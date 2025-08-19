import os
import json
import polars as pl
from datetime import datetime, timedelta
from supply import PyResource, PySKU, PyOperation, PyMultiStepProcess
from supply import get_all_operations
from supply import get_all_skus
from supply import PyDemand, PyDemandPlanner
from break_direct_cycles import break_direct_cycles
from supply import levelize_supply_chain

# Notes on the Swan dataset and workarounds
# ResourceKeys -> line_id@plant
# SkuKeys -> product@location
# Manufacturing Process_Key -> process_id@bom_id@product@plant
# Manufcaturing operations -> Process_Key@operation_id
# Transportation OperationKeys -> product@origin@destination@asset@mode


# 1. Transportation network has cycles. Cycles need to be removd from data or code to be fixed.


class ProcessLSCO:
    def __init__(self, folder_path):
        """Initialize with the path to the folder containing CSV files and JSON parameters.
        
        Args:
            folder_path (str): Path to the folder containing LSCO CSV files
        """
        self.folder_path = folder_path
        self.dataframes = {}
        self.horizon_start = None
        self.horizon_end = None
        self.load_parameters()
        self.separator = "@"
        
    def load_parameters(self):
        """Load parameters from parameter.json to define the planning horizon."""
        param_path = os.path.join(self.folder_path, "parameter.json")
        if not os.path.exists(param_path):
            print(f"Warning: Parameter file {param_path} not found. Using default horizon.")
            # Default horizon if file not found
            self.horizon_start = datetime.now().date()
            self.horizon_end = (datetime.now() + timedelta(days=365)).date()
            return
            
        try:
            with open(param_path, 'r') as f:
                params = json.load(f)
                
            # Extract horizon dates from parameters using the correct keys
            self.horizon_start = datetime.strptime(params.get("horizon_start", ""), "%Y-%m-%d").date()
            self.horizon_end = datetime.strptime(params.get("horizon_end", ""), "%Y-%m-%d").date()
            
            print(f"Loaded planning horizon: {self.horizon_start} to {self.horizon_end}")
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error reading parameter file: {e}")
            # Default horizon if file reading fails
            self.horizon_start = datetime.now().date()
            self.horizon_end = (datetime.now() + timedelta(days=365)).date()
            print(f"Using default horizon: {self.horizon_start} to {self.horizon_end}")
    
    def read_csv_to_dataframe(self, filename):
        """Read a CSV file into a Polars DataFrame.
        
        Args:
            filename (str): Name of the CSV file (without path)
            
        Returns:
            pl.DataFrame: The loaded DataFrame or None if file doesn't exist
        """
        file_path = os.path.join(self.folder_path, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found")
            return None
            
        df = pl.read_csv(file_path, comment_prefix="#")
        self.dataframes[filename] = df
        return df
    
    def load_production_lines(self):
        """Load production_line.csv, sort it, filter active records, and return as DataFrame.
        
        Returns:
            pl.DataFrame: The sorted production line DataFrame with only active records
        """
        df = self.read_csv_to_dataframe("production_line.csv")
        if df is not None:
            # Filter for active records if there's an 'active' column
            if "active" in df.columns:
                df = df.filter(pl.col("active") == True)
            # Otherwise, assume all records are active
            
            # Sort by line_id, plant, and valid_from_date
            df = df.sort(["line_id", "plant", "valid_from_date"])
            self.dataframes["production_line.csv"] = df
        return df
    
    def load_planning_policy(self):
        """Load planning_policy.csv, filter active records, and return as DataFrame."""
        df = self.read_csv_to_dataframe("planning_policy.csv")
        if df is not None:
            # Filter active records
            df = df.filter(pl.col("active") == True)
            self.dataframes["planning_policy.csv"] = df
        return df
    
    def load_sourcing_matrix(self):
        """Load sourcing_matrix.csv, filter active records, and return as DataFrame."""
        df = self.read_csv_to_dataframe("sourcing_matrix.csv")
        if df is not None:
            # Filter active records
            df = df.filter(pl.col("active") == True)
            self.dataframes["sourcing_matrix.csv"] = df

            df = break_direct_cycles(df)
        return df
    
    def load_vendors(self):
        """Load vendor.csv, filter active records, and return as DataFrame."""
        df = self.read_csv_to_dataframe("vendor.csv")
        if df is not None:
            # Filter active records
            df = df.filter(pl.col("active") == True)
            self.dataframes["vendor.csv"] = df
        return df
    
    def _date_range(self, start_date, end_date):
        """Generate a list of date strings between start and end dates.
        
        Args:
            start_date: Start date (datetime.date or string)
            end_date: End date (datetime.date or string)
            
        Returns:
            list: List of date strings in format YYYY-MM-DD
        """
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        return date_list
    
    def create_resources_from_production_lines(self, default_capacity=1000000.0):
        """Create Resource objects from the production line data.
        Sets capacity for each day in the horizon or from the earliest valid_from_date.
        
        Args:
            default_capacity (float): Default capacity to set for each resource
            
        Returns:
            dict: Dictionary of created resources with key 'line_id@plant'
        """
        if "production_line.csv" not in self.dataframes:
            self.load_production_lines()
            
        if "production_line.csv" not in self.dataframes:
            print("Error: production_line.csv could not be loaded")
            return {}
            
        df = self.dataframes["production_line.csv"]
        resources = {}
        
        # Convert to native Python format for processing
        records = df.to_dicts()
        
        # Group records by line@plant to handle multiple entries for the same resource
        resource_data = {}

        for record in records:
            line_id = record["line_id"]
            plant = record["plant"]
            resource_key = f"{line_id}{self.separator}{plant}"
            
            if resource_key not in resource_data:
                resource_data[resource_key] = []
            resource_data[resource_key].append(record)
        
        # Process each resource
        for resource_key, records in resource_data.items():
            # Create the resource
            resource = PyResource(resource_key)
            
            # Find the earliest valid_from_date
            earliest_date = min(
                datetime.strptime(r["valid_from_date"], "%Y-%m-%d").date() 
                for r in records
            )
            
            # Determine the effective start date (max of horizon start and earliest valid date)
            effective_start = max(self.horizon_start, earliest_date)
            
            # Generate dates from effective start to horizon end
            date_range = self._date_range(effective_start, self.horizon_end)
            
            # Set capacity for each day
            for date_str in date_range:
                current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                # Find the applicable record for this date
                applicable_record = None
                for record in sorted(records, key=lambda r: r["valid_from_date"], reverse=True):
                    record_date = datetime.strptime(record["valid_from_date"], "%Y-%m-%d").date()
                    if record_date <= current_date:
                        applicable_record = record
                        break
                
                if applicable_record:
                    try:
                        max_hours = float(applicable_record["max_hours"])
                        utilization = float(applicable_record["line_utilization"]) / 100.0
                        available_lines = float(applicable_record["available_lines"])
                        
                        # Calculate capacity as hours * utilization * lines. Send the decreased capacity to the resource.
                        # This is a simplification and can be chnaged given that utilization is being stored in the capapcity bucket below
                        capacity = max_hours * available_lines * utilization
                    except (ValueError, KeyError):
                        capacity = default_capacity
                else:
                    capacity = default_capacity
                
                # Set capacity for this date
                resource.set_capacity_with_line_utilization(date_str, capacity, utilization)
            
            # Store resource in our dictionary
            resources[resource_key] = resource
            
        print(f"Created {len(resources)} resources from production line data")
        return resources
    
    def create_skus_from_planning_policy(self):
        """Create SKUs from planning_policy.csv with key as product@location."""
        if "planning_policy.csv" not in self.dataframes:
            self.load_planning_policy()
            
        if "planning_policy.csv" not in self.dataframes:
            print("Error: planning_policy.csv could not be loaded")
            return {}
            
        df = self.dataframes["planning_policy.csv"]
        skus = {}
        
        # Convert to native Python format for processing
        records = df.to_dicts()
        
        for record in records:
            # Skip inactive records if active field exists
            if not record["active"]:
                continue
                
            product = record["product"]
            location = record["location"]
            
            # Create SKU with key as product@location
            sku_key = f"{product}{self.separator}{location}"
            
            # Create SKU using the PySKU.create method (product_name, location_name)
            sku = PySKU.create(product, location)
            
            # Store in our dictionary
            skus[sku_key] = sku
        
        print(f"Created {len(skus)} SKUs from planning policy data")
        return skus
    
    def create_skus_from_sourcing_matrix(self):
        """Create SKUs from sourcing_matrix.csv joined with vendor.csv."""
        if "sourcing_matrix.csv" not in self.dataframes:
            self.load_sourcing_matrix()
            
        if "vendor.csv" not in self.dataframes:
            self.load_vendors()
            
        if "sourcing_matrix.csv" not in self.dataframes or "vendor.csv" not in self.dataframes:
            print("Error: sourcing_matrix.csv or vendor.csv could not be loaded")
            return {}
            
        sourcing_df = self.dataframes["sourcing_matrix.csv"]
        vendor_df = self.dataframes["vendor.csv"]
        
        # Join sourcing_matrix with vendor on origin = vendor_id
        joined_df = sourcing_df.join(
            vendor_df,
            left_on="origin",
            right_on="vendor_id",
            how="inner"
        )
        
        skus = {}
        
        # Convert to native Python format for processing
        records = joined_df.to_dicts()
        
        for record in records:
            # Skip inactive records from either table
            if not record["active_right"] or not record["active"]:
                continue
                
            product = record["product"]
            origin = record["origin"]
            
            # Create SKU with key as product@origin
            sku_key = f"{product}{self.separator}{origin}"
            
            # Create SKU using the PySKU.create method (product_name, location_name)
            sku = PySKU.create(product, origin)
            sku.location_type = "VENDOR"

            # Store in our dictionary
            skus[sku_key] = sku
        
        print(f"Created {len(skus)} SKUs from sourcing matrix and vendor data")
        return skus
    
    def create_all_skus(self):
        """Create all SKUs from both planning policy and sourcing matrix."""
        skus_from_policy = self.create_skus_from_planning_policy()
        skus_from_sourcing = self.create_skus_from_sourcing_matrix()
        
        # Combine both dictionaries
        all_skus = {**skus_from_policy, **skus_from_sourcing}
        
        print(f"Created a total of {len(all_skus)} SKUs")
        return all_skus
    
    def load_all_csv_files(self):
        """Load all CSV files from the folder into DataFrames.
        
        Returns:
            dict: Dictionary of loaded DataFrames with filename as key
        """
        csv_files = [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            self.read_csv_to_dataframe(csv_file)
            
        return self.dataframes

    def create_multi_step_processes(self):
        """Create PyMultiStepProcess objects from line_capability.csv joined with bom.csv."""
        if "line_capability.csv" not in self.dataframes:
            self.load_line_capability()
        
        if "bom.csv" not in self.dataframes:
            self.load_bom()
        
        if "line_capability.csv" not in self.dataframes or "bom.csv" not in self.dataframes:
            print("Error: line_capability.csv or bom.csv could not be loaded")
            return {}
        
        # Filter active records
        line_capability_df = self.dataframes["line_capability.csv"]
        
        bom_df = self.dataframes["bom.csv"]
        
        # Convert to native Python format for processing
        records = line_capability_df.to_dicts()
        
        # Group records by the unique combination of (process_id, bom, plant, product)
        process_steps = {}
        
        # Default date values
        default_valid_from = "2020-01-01"
        default_valid_to = "2099-12-31"
 

        for record in records:
            process_id = record["process_id"]
            bom = record["bom"]
            plant = record["plant"]
            product = record["product"]
            
            # Ensure valid_from and valid_to have values
            if not record.get("valid_from_date") or record["valid_from_date"] == "":
                record["valid_from_date"] = default_valid_from
            
            if not record.get("valid_to_date") or record["valid_to_date"] == "":
                record["valid_to_date"] = default_valid_to
            
            # Create a composite key for the process
            process_key = f"{process_id}{self.separator}{bom}{self.separator}{product}{self.separator}{plant}"
            
            if process_key not in process_steps:
                process_steps[process_key] = []
            
            process_steps[process_key].append(record)
        
        # Create multi-step processes
        multi_step_processes = {}

        for process_key, steps in process_steps.items():
            # Extract components from the process key using the class separator
            key_parts = process_key.split(self.separator)
            process_id = key_parts[0]
            bom_id = key_parts[1]
            product = key_parts[2]
            plant = key_parts[3]
            
            # Collect all valid_from and valid_to date combinations for this process key
            effectivity_periods = set()
            for step in steps:
                effectivity_periods.add((step["valid_from_date"], step["valid_to_date"]))
            
            # Find the records with the earliest valid_from date
            min_valid_from = min(from_date for from_date, _ in effectivity_periods)
            
            # Sort steps by operation_id to help identify the sequence
            # Only use steps with the earliest valid_from date for constructing the process
            sorted_steps = sorted(
                [s for s in steps if s["valid_from_date"] == min_valid_from],
                key=lambda s: s["operation_id"]
            )
            
            # Create multi-step process. This API would change later.
            process = PyMultiStepProcess(process_key, 1, 1, 1)  # Default min_lot and increment
            
            # Find first step (the one without previous_operation)
            first_step = None
            for step in sorted_steps:
                if not step["previous_operation"]:
                    first_step = step
                    break
            
            if not first_step:
                print(f"Error: Could not find first step for process {process_key}")
                continue
            
            # Create a dictionary of steps by operation_id for easy lookup
            step_dict = {step["operation_id"]: step for step in sorted_steps}
            
            # Create operation steps in order
            created_steps = []
            current_step = first_step
            next_op_id = current_step["operation_id"]
            last_step_operation = None
            
            while next_op_id and next_op_id in step_dict:
                step_record = step_dict[next_op_id]
                
                # Create step key
                step_key = f"{process_key}{self.separator}{next_op_id}"
                
                # Determine lead time, min lot, and increment
                lead_time = 1  # Default lead time
                # TODO: how to handle lead time. Is batch process lead time in days. Can we round this off to upwards days
                #if step_record.get("batch_time"):
                #    try:
                #        lead_time = int(float(step_record["batch_time"]))
                #    except (ValueError, TypeError):
                #        pass
                
                min_lot = 0  # Default min lot
                if step_record.get("min_lot_qty"):
                    try:
                        min_lot = int(float(step_record["min_lot_qty"]))
                    except (ValueError, TypeError):
                        pass
                
                increment = 0  # Default increment
                if step_record.get("incremental_lot_qty"):
                    try:
                        increment = int(float(step_record["incremental_lot_qty"]))
                    except (ValueError, TypeError):
                        pass
                
                # Create operation for this step
                step_operation = PyOperation(step_key, lead_time=lead_time, min_lot=0, increment=0)
                
                # Get the resource for this step's line
                line_id = step_record["line"]
                resource_key = f"{line_id}{self.separator}{plant}"
                
                resource = PyResource(resource_key)
                
                # Add resource to operation
                quantity_per = 1.0
                if step_record["production_rate"]:
                    quantity_per = 1.0/step_record["production_rate"]
                else:
                    # TODO: how to handle batch process?
                    print(f"Warning: No production rate for step {step_key}. How to handle this likely batch process")
                
                step_operation.add_resource(resource, quantity_per=quantity_per)
                
                # For first step, add BOM components
                if not step_record["previous_operation"]:
                    # Find matching BOM records
                    bom_records = bom_df.filter(
                        (pl.col("bom_id") == bom_id) &
                        (pl.col("plant") == plant) &
                        (pl.col("product") == product)
                    ).to_dicts()
                    
                    for bom_record in bom_records:
                        input_product = bom_record["input_product"]
                        input_qty = float(bom_record["input_product_qty"])
                        product_qty = float(bom_record["product_qty"])
                        
                        # Create SKU for input product
                        input_sku = PySKU.create(input_product, plant)
                     
                        # Add as component to first step. We assume here that the ouptut would be always 1.0 units.
                        # Therefore adjusting the input component quantity per to match the output quantity per
                        step_operation.add_bom_component(input_sku, quantity_per=input_qty/product_qty)
                
                # For last step, add output product
                is_last_step = True
                for other_step in sorted_steps:
                    if other_step["previous_operation"] == step_record["operation_id"]:
                        is_last_step = False
                        break
                
                if is_last_step:
                    # Create SKU for output product
                    output_sku = PySKU.create(product, plant)
                    # Add output to last step
                    step_operation.add_output(output_sku, quantity_per=1.0)

                    # Only last step needs to have min lot and increment
                    step_operation.set_min_lot(min_lot)
                    step_operation.set_increment(increment)
                    
                    # Save reference to last step operation
                    last_step_operation = step_operation
                
                # Add step to multi-step process
                process.add_step(step_operation)
                created_steps.append(step_operation)
                
                # Find next step
                next_op_id = None
                for potential_next in sorted_steps:
                    if potential_next["previous_operation"] == step_record["operation_id"]:
                        next_op_id = potential_next["operation_id"]
                        break
            
            # Add all effectivity periods to the last step
            # TODO: We are assuming priority to be 1. This should come from data eventually
            priority = 1
            if last_step_operation and effectivity_periods:
                for i, (from_date, to_date) in enumerate(effectivity_periods, 1):
                    last_step_operation.add_period(priority, from_date, to_date)
            
            # Store the process
            multi_step_processes[process_key] = process
            
            print(f"Created multi-step process: {process_key} with {len(created_steps)} steps and {len(effectivity_periods)} effectivity periods")
        
        return multi_step_processes

    def load_line_capability(self):
        """Load line_capability.csv, filter active records, and return as DataFrame."""
        df = self.read_csv_to_dataframe("line_capability.csv")
        if df is not None:
            # Filter active records
            if "active" in df.columns:
                df = df.filter(pl.col("active") == True)
            self.dataframes["line_capability.csv"] = df
        return df

    def load_bom(self):
        """Load bom.csv, filter active records, and return as DataFrame."""
        df = self.read_csv_to_dataframe("bom.csv")
        if df is not None:
            # Filter active records
            if "active" in df.columns:
                df = df.filter(pl.col("active") == True)
            self.dataframes["bom.csv"] = df
        return df

    def create_transportation_resources(self):
        """Create transportation resources by joining transportation_lane and transportation_asset.
        
        Creates PyResource objects with key format origin@destination@asset@mode
        Sets capacity for each day in the planning horizon using the transportation_asset's capacity_weight.
        
        Returns:
            dict: Dictionary of created transportation resources
        """
        # Load transportation data files if not already loaded
        if "transportation_lane.csv" not in self.dataframes:
            self.read_csv_to_dataframe("transportation_lane.csv")
        
        if "transportation_asset.csv" not in self.dataframes:
            self.read_csv_to_dataframe("transportation_asset.csv")
        
        if "transportation_lane.csv" not in self.dataframes or "transportation_asset.csv" not in self.dataframes:
            print("Error: transportation_lane.csv or transportation_asset.csv could not be loaded")
            return {}
        
        # Filter for active lanes and assets
        lane_df = self.dataframes["transportation_lane.csv"]
        if "active" in lane_df.columns:
            lane_df = lane_df.filter(pl.col("active") == True)
        
        asset_df = self.dataframes["transportation_asset.csv"]
        if "active" in asset_df.columns:
            asset_df = asset_df.filter(pl.col("active") == True)
        
        # Join the dataframes on asset_id and mode_id
        joined_df = lane_df.join(
            asset_df,
            left_on=["asset", "mode"],
            right_on=["asset_id", "mode_id"],
            how="inner"
        )
        
        # Convert to native Python format for processing
        records = joined_df.to_dicts()
        
        # Create resources
        resources = {}
        horizon_start_str = self.horizon_start.strftime("%Y-%m-%d")
        horizon_end_str = self.horizon_end.strftime("%Y-%m-%d")
        
        for record in records:
            origin = record["origin"]
            destination = record["destination"]
            asset = record["asset"]
            mode = record["mode"]
            
            # Create resource key in the format origin@destination@asset@mode
            resource_key = f"{origin}{self.separator}{destination}{self.separator}{asset}{self.separator}{mode}"
            
            # Create the PyResource
            resource = PyResource(resource_key)
            
            # Get capacity weight from the asset record
            # TODO: This may be wrong. We could just unconstrain it to begin with
            try:
                capacity = float(record["capacity_weight"])
            except (ValueError, KeyError):
                print(f"Warning: Could not determine capacity for {resource_key}. Using default.")
                capacity = 1000000.0  # Default capacity
            
            # Generate dates from horizon start to horizon end
            date_range = self._date_range(self.horizon_start, self.horizon_end)
            
            # Set capacity for each day
            for date_str in date_range:
                resource.set_capacity(date_str, capacity)
            
            # Store resource in our dictionary
            resources[resource_key] = resource
        
        print(f"Created {len(resources)} transportation resources")
        return resources

    def create_transportation_network(self, transportation_resources=None):
        """Create transportation network by joining sourcing_matrix and transportation_lane.
        
        Creates PyOperation objects with key format product@origin@destination@asset@mode.
        These operations represent transportation activities in the network.
        
        Args:
            transportation_resources (dict, optional): Dictionary of transportation resources 
                                                      created by create_transportation_resources
        
        Returns:
            dict: Dictionary of created transportation operations
        """
        # Load required data files if not already loaded
        if "sourcing_matrix.csv" not in self.dataframes:
            self.load_sourcing_matrix()
        
        if "transportation_lane.csv" not in self.dataframes:
            self.read_csv_to_dataframe("transportation_lane.csv")
        
        if "sourcing_matrix.csv" not in self.dataframes or "transportation_lane.csv" not in self.dataframes:
            print("Error: sourcing_matrix.csv or transportation_lane.csv could not be loaded")
            return {}
        
        # Create transportation resources if not provided
        if transportation_resources is None:
            transportation_resources = self.create_transportation_resources()

        # Filter for active records
        sourcing_df = self.dataframes["sourcing_matrix.csv"]
        if "active" in sourcing_df.columns:
            sourcing_df = sourcing_df.filter(pl.col("active") == True)
        
        lane_df = self.dataframes["transportation_lane.csv"]
        if "active" in lane_df.columns:
            lane_df = lane_df.filter(pl.col("active") == True)
        
        # Join sourcing_matrix with transportation_lane on origin and destination
        joined_df = sourcing_df.join(
            lane_df,
            left_on=["origin", "destination"],
            right_on=["origin", "destination"],
            how="inner"
        )
        
        # Convert to native Python format for processing
        records = joined_df.to_dicts()
        operations = {}
        
        for record in records:
            product = record["product"]
            origin = record["origin"]
            destination = record["destination"]
            asset = record["asset"]
            mode = record["mode"]
            
            # Create the operation key
            operation_key = f"{product}{self.separator}{origin}{self.separator}{destination}{self.separator}{asset}{self.separator}{mode}"
            
            # Get lead time (service time) from the transportation lane
            lead_time = int(record.get("service_time", 1))
            
            # Get min_lot and increment from the sourcing matrix
            min_lot = 0
            if record.get("min_lot_qty") and record["min_lot_qty"] != "":
                try:
                    min_lot = int(float(record["min_lot_qty"]))
                except (ValueError, TypeError):
                    pass
            
            increment = 0
            if record.get("incremental_lot_qty") and record["incremental_lot_qty"] != "":
                try:
                    increment = int(float(record["incremental_lot_qty"]))
                except (ValueError, TypeError):
                    pass
            
            # Create the operation
            operation = PyOperation(operation_key, lead_time=lead_time, min_lot=min_lot, increment=increment)
            
            # Get priority from sourcing matrix
            priority = 1
            if record.get("source_priority") and record["source_priority"] != "":
                try:
                    priority = int(record["source_priority"])
                except (ValueError, TypeError):
                    pass
            
            # Get valid_from and valid_to dates
            valid_from = record.get("valid_from_date", "")
            valid_to = record.get("valid_to_date", "")
            
            # Add period with effectivity dates and priority
            operation.add_period(priority, valid_from if valid_from else None, valid_to if valid_to else None)
            
            # Connect to the transportation resource
            resource_key = f"{origin}{self.separator}{destination}{self.separator}{asset}{self.separator}{mode}"
            if resource_key in transportation_resources:
                resource = transportation_resources[resource_key]
                operation.add_resource(resource, quantity_per=1.0)
            else:
                print(f"Warning: Transportation resource {resource_key} not found for operation {operation_key}")
            
            # Create SKUs for the product at origin and destination
            origin_sku = PySKU.create(product, origin)
            destination_sku = PySKU.create(product, destination)
            
            # Add the SKUs as source and destination for the operation
            operation.add_consume_flow(origin_sku, quantity_per=1.0)
            operation.add_produce_flow(destination_sku, quantity_per=1.0)
            
            # Store operation in dictionary
            operations[operation_key] = operation
        
        print(f"Created {len(operations)} transportation operations")
        return operations

    def process_line_capability_with_step_sequence(self):
        """Process line capability data and add sequence IDs based on operation dependencies.
        
        The sequence_id is calculated based on these rules:
        1. Operations with no previous_operation get sequence_id = 1
        2. Operations with a previous_operation get sequence_id = previous_operation's sequence_id + 1
        """
        # Load and sort the data
        lc_df = self.load_line_capability()
        if lc_df is None:
            print("Error: Could not load line_capability.csv")
            return

        # Convert to Python objects for processing
        records = lc_df.to_dicts()
        
        # Group records by process
        process_groups = {}
        for record in records:
            key = (record["process_id"], record["bom"], record["plant"], record["product"])
            if key not in process_groups:
                process_groups[key] = []
            process_groups[key].append(record)

        # Process each group and assign sequence IDs
        all_records = []
        for group in process_groups.values():
            sequence_map = {}
            
            # First pass: assign sequence 1 to starting operations
            for record in group:
                if not record["previous_operation"]:
                    sequence_map[record["operation_id"]] = 1
            
            # Second pass: assign sequences based on previous operations
            count = 0
            error = False
            while len(sequence_map) < len(group):
                count += 1
                if count > 10:
                    key = (record["process_id"], record["bom"], record["plant"], record["product"])
                    print(f"Error in sequencing steps in process identified by key: {key}")
                    error = True
                    break

                for record in group:
                    op_id = record["operation_id"]
                    if op_id not in sequence_map and record["previous_operation"] in sequence_map:
                        sequence_map[op_id] = sequence_map[record["previous_operation"]] + 1
            
            # Add sequence_id to records
            for record in group:
                record["sequence_id"] = sequence_map[record["operation_id"]]  
                all_records.append(record)

        # Convert back to Polars DataFrame
        lc_df = pl.DataFrame(all_records)
        # Sort by process and sequence
        lc_df = lc_df.sort(["process_id", "bom", "plant", "product", "sequence_id"])
        # Store the processed DataFrame
        self.dataframes["line_capability.csv"] = lc_df        
        return lc_df


if __name__ == "__main__":
    processor = ProcessLSCO("tests/swan_dataset")    
    # Create resources
    resources = processor.create_resources_from_production_lines()
    # Create transportation resources
    print("Creating transportation resources")
    transport_resources = processor.create_transportation_resources()
    for resource in transport_resources.values():
        print(resource.name)
    print(f"Created {len(transport_resources)} transportation resources")
    
    # Create SKUs
    skus = processor.create_all_skus()
    print(f"Created {len(skus)} SKUs")
    
    # Process line capability with step sequence added to sort based on previous_operation
    line_capability_df = processor.process_line_capability_with_step_sequence()

    import debugpy
    debugpy.listen(5678)
    debugpy.wait_for_client()
    print("Waiting for debugger to attach...")

    # Create multi-step processes
    processes = processor.create_multi_step_processes()
    
    # Print created processes
    for key, process in processes.items():
        print(f"Process: {key}")

    for op in get_all_operations():
        print(op.name)

    print("Creating transportation network")

    
    operations = processor.create_transportation_network(transport_resources)
    for op in operations.values():
        print(op.name)

    horizon_start_str = processor.horizon_start.strftime("%Y-%m-%d")
    for sku in get_all_skus():
        sku.process_sources()
        # Initialize inventory for vendor skus at the start of the horizon
        if sku.location_type == "VENDOR":
            sku.add_on_hand(horizon_start_str, float("inf"))

    # Now draw the network
    # SWAN_100G_COCOA@D003, SWAN_100G_ALMOND@P002, SWAN_100G_COCOA@P001
    sku = PySKU.fetch("SWAN_100G_COCOA@D003")
    sc = sku.get_supply_chain("2025-01-31")
    for line in sc:
        print(line)

    
    planner = PyDemandPlanner()
    demand1 = PyDemand(id="D1",quantity=200.0,request_date="2025-01-30",max_lateness=0,sku=sku)
    #planner.plan_demand_list([demand1], trace_level=2)


    #for resource in resources.values():
    #    resource.print_all_capacity_buckets()
    #levelize_supply_chain()
    #for sku in get_all_skus():
    #    print(sku.name, sku.level)

