from polars import DataType, Utf8, Float64, Int64, Date

class FileMetadata:
    """Metadata configuration for data files"""
    
    # Define column types and other metadata for each file
    FILE_CONFIGS = {
        'lane_details_report.csv': {
            'dtypes': {
                'asset': Utf8,
                'asset_name': Utf8,
                'mode': Utf8,
                'carrier': Utf8,
                'service': Utf8,
                'flow_qty': Float64,
                'distance': Float64,
                'fixed_cost': Float64,
                'mode_name': Utf8,
                'auto_scenario_id': Utf8,
                'variable_cost': Float64,
                'transportation_cost': Float64,
                'product': Utf8,
                'departure_period': Utf8,
                'arrival_period': Utf8,
                'origin': Utf8,
                'destination': Utf8,
                'flow_dimwt': Float64,
            },
            'required_columns': [
                'origin', 'destination', 'flow_qty', 'departure_period', 
                'arrival_period', 'asset', 'transportation_cost', 
                'fixed_cost', 'variable_cost'
            ]
        },
        'demand_flow_report.csv': {
            'dtypes': {
                'product': Utf8,
                'location': Utf8,
                'period': Utf8,
                'auto_scenario_id': Utf8,
                'demand_shortfall': Float64,
                'unmet_demand': Float64,
                'demand_satisfied': Float64,
                'demand_shortfall_penalty': Float64,
                'unmet_demand_penalty': Float64,

            },
            'required_columns': ['product', 'location', 'auto_scenario_id', 'demand_satisfied', 'period']
        },
        'consumption_report.csv': {
            'dtypes': {
                'auto_scenario_id': Utf8,
                'product': Utf8,
                'plant': Utf8,
                'line': Utf8,
                'process_id': Utf8,
                'operation_id': Utf8,
                'bom': Utf8,
                'input_product': Utf8,
                'period': Utf8,
            },
            'required_columns': ['auto_scenario_id', 'product', 'plant', 'line', 'process_id', 'operation_id', 'bom', 'period']
        },
        'production_report.csv': {
            'dtypes': {
                'auto_scenario_id': Utf8,
                'product': Utf8,
                'plant': Utf8,
                'line': Utf8,
                'process_id': Utf8,
                'operation_id': Utf8,
                'bom': Utf8,
                'production_cost': Float64,
                'production_time': Float64,
                'utilization': Float64,

            },
            'required_columns': ['auto_scenario_id', 'product', 'plant', 'line', 'process_id', 'operation_id', 'bom', 'production_cost']
        },
        'location_product_flow_report.csv': {
            'dtypes': {
                'auto_scenario_id': Utf8,
                'product': Utf8,
                'location': Utf8,
                'period': Utf8,
                'inbound_qty': Float64,
                'outbound_qty': Float64,
                'throughput_qty': Float64,
                'production_qty': Float64,
                'consumption_qty': Float64,
                'inbound_handling_cost': Float64,
                'outbound_handling_cost': Float64,
                'throughput_cost': Float64,
                'average_inventory': Float64, # Currently not used
                'average_storage_cost': Float64,
                'ending_storage_cost': Float64,
                'ending_stock': Float64,
                'beginning_stock': Float64,
            },
            'required_columns': ['auto_scenario_id', 'product', 'location', 'period', 'inbound_qty', 'outbound_qty', 'throughput_qty', 'average_inventory', 'average_storage_cost', 'ending_storage_cost']
        },
        'production_line_utilization_report.csv': {
            'dtypes': {
                'auto_scenario_id': Utf8,
                'plant': Utf8,
                'line': Utf8,
                'period': Utf8,
                'production_qty': Float64,
                'fixed_cost': Float64,
                'variable_cost': Float64,
            },
            'required_columns': ['auto_scenario_id', 'plant', 'line', 'period', 'production_qty', 'fixed_cost', 'variable_cost']
        },
        'time_period.csv': {
            'dtypes': {
                'period_id': Utf8,
                'period_name': Utf8,
                'start_datetime': Utf8,
                'end_datetime': Utf8,
            },
            'required_columns': ['period_id', 'period_name', 'start_datetime', 'end_datetime']
        },
        'location_flow_report.csv': {
            'dtypes': {
                'auto_scenario_id': Utf8,
                'location': Utf8,
                'period': Utf8,
                'inbound_qty': Float64,
                'outbound_qty': Float64,
                'fixed_operating_cost': Float64,
            },
            'required_columns': ['auto_scenario_id', 'location', 'period', 'inbound_qty', 'outbound_qty', 'fixed_operating_cost']
        },
        'procurement_report.csv': {
            'dtypes': {
                'auto_scenario_id': Utf8,
                'vendor': Utf8,
                'product': Utf8,
                'period': Utf8,
                'sourcing_qty': Float64,
                'sourcing_cost': Float64,
            },
            'required_columns': ['auto_scenario_id', 'vendor', 'product', 'period', 'sourcing_qty', 'sourcing_cost']
        },
        'on_hand_stock.csv': {
            'dtypes': {
                'product': Utf8,
                'location': Utf8,
                'date': Utf8,
                'qty': Float64,
            },
            'required_columns': ['product', 'location', 'qty']
        }
        # Add configurations for other files...
    }
    
    @classmethod
    def get_file_config(cls, filename: str) -> dict:
        """Get configuration for a specific file"""
        return cls.FILE_CONFIGS.get(filename, {'dtypes': {}, 'required_columns': []}) 