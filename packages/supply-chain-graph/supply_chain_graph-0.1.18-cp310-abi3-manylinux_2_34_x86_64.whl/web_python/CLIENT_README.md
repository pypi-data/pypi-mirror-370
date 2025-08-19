# Supply Chain API Python Client

A Python client library for interacting with the Supply Chain Planning API. This client provides scenario-aware methods to retrieve information about SKUs, operations, resources, demands, and scenarios.

## Features

- **Scenario-aware**: All methods support specifying scenario IDs for multi-scenario analysis
- **Comprehensive Coverage**: Access to all major API endpoints
- **Error Handling**: Custom exceptions and proper error handling
- **Type Hints**: Full type annotations for better IDE support
- **Context Manager**: Supports `with` statement for automatic session cleanup
- **Helper Functions**: Built-in formatting functions for displaying data

## Installation

1. Install dependencies:
```bash
pip install -r requirements_client.txt
```

2. Ensure the Supply Chain API server is running:
```bash
cd supply_plan/web_python
python network_api.py
```

## Quick Start

```python
from supply_chain_client import SupplyChainClient

# Create client
client = SupplyChainClient("http://localhost:8000")

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")

# Get all SKUs in Base scenario
skus = client.get_all_skus("Base")
print(f"Found {len(skus)} SKUs")

# Get scenario statistics
stats = client.get_scenario_stats("Base")
print(f"SKUs: {stats['sku_count']}, Operations: {stats['operation_count']}")
```

## API Methods

### Health and System
- `health_check()` - Check API health status
- `get_available_scripts()` - Get list of available scripts

### Scenario Management
- `list_scenarios()` - Get all available scenarios
- `get_scenario_details(scenario_id)` - Get scenario details
- `get_scenario_stats(scenario_id)` - Get scenario statistics

### SKU Management
- `get_all_skus(scenario_id)` - Get all SKUs in a scenario
- `get_sku(sku_name, scenario_id)` - Get specific SKU details
- `get_inventory_profile(sku_name, scenario_id)` - Get inventory profile
- `get_net_inventory(sku_name, date, scenario_id)` - Get net inventory for a date

### Operation Management
- `get_all_operations(scenario_id)` - Get all operations in a scenario
- `get_operation(operation_name, scenario_id)` - Get specific operation details
- `get_operation_plans(operation_name, scenario_id)` - Get operation plans

### Resource Management
- `get_all_resources(scenario_id)` - Get all resources in a scenario
- `get_resource_capacity(resource_name, scenario_id)` - Get resource capacity buckets

### Demand Management
- `get_all_demands(scenario_id)` - Get all demands in a scenario

### Supply Chain Visualization
- `visualize_supply_chain(sku_name, scenario_id)` - Get supply chain graph data
- `get_supply_chain_text(sku_name, effective_date, scenario_id)` - Get text representation

### Product-Location Queries
- `get_products_at_location(location_id, scenario_id)` - Get products at a location
- `get_locations_for_product(product_id, scenario_id)` - Get locations for a product
- `list_products(scenario_id)` - Get all product IDs in a scenario
- `list_locations(scenario_id)` - Get all location IDs in a scenario

## Usage Examples

### Basic Usage
```python
from supply_chain_client import SupplyChainClient

# Using context manager (recommended)
with SupplyChainClient("http://localhost:8000") as client:
    # Get all scenarios
    scenarios = client.list_scenarios()
    print(f"Available scenarios: {scenarios['scenarios']}")
    
    # Get SKUs from specific scenario
    skus = client.get_all_skus("Production")
    print(f"Found {len(skus)} SKUs in Production scenario")
```

### Scenario Comparison
```python
def compare_scenarios(client, scenario1, scenario2):
    """Compare statistics between two scenarios"""
    stats1 = client.get_scenario_stats(scenario1)
    stats2 = client.get_scenario_stats(scenario2)
    
    print(f"Scenario Comparison:")
    print(f"  {scenario1}: {stats1['sku_count']} SKUs, {stats1['operation_count']} Operations")
    print(f"  {scenario2}: {stats2['sku_count']} SKUs, {stats2['operation_count']} Operations")

with SupplyChainClient() as client:
    compare_scenarios(client, "Base", "Alternative")
```

### SKU Analysis
```python
def analyze_sku(client, sku_name, scenario_id="Base"):
    """Perform detailed analysis of a specific SKU"""
    # Get SKU details
    sku = client.get_sku(sku_name, scenario_id)
    print(f"SKU: {sku['name']}")
    print(f"  Product: {sku['product_name']}")
    print(f"  Location: {sku['location_name']}")
    print(f"  Level: {sku['level']}")
    
    # Get inventory profile
    inventory = client.get_inventory_profile(sku_name, scenario_id)
    profile = inventory['inventory_profile']
    print(f"  Inventory entries: {len(profile)}")
    
    # Get supply chain visualization
    viz = client.visualize_supply_chain(sku_name, scenario_id)
    graph = viz['graph']
    print(f"  Supply chain nodes: {len(graph['nodes'])}")
    print(f"  Supply chain edges: {len(graph['edges'])}")

with SupplyChainClient() as client:
    analyze_sku(client, "Laptop@DC")
```

### Resource Capacity Analysis
```python
def analyze_resource_capacity(client, scenario_id="Base"):
    """Analyze resource capacity across all resources"""
    resources = client.get_all_resources(scenario_id)
    
    for resource in resources:
        resource_name = resource['name']
        capacity_info = client.get_resource_capacity(resource_name, scenario_id)
        buckets = capacity_info['capacity_buckets']
        print(f"Resource {resource_name}: {len(buckets)} capacity buckets")

with SupplyChainClient() as client:
    analyze_resource_capacity(client)
```

## Helper Functions

The client includes several helper functions for displaying data:

```python
from supply_chain_client import (
    print_sku_summary,
    print_operation_summary, 
    print_resource_summary,
    print_demand_summary
)

with SupplyChainClient() as client:
    skus = client.get_all_skus("Base")
    print_sku_summary(skus)  # Formatted table output
```

## Error Handling

```python
from supply_chain_client import SupplyChainClient, SupplyChainAPIError

try:
    with SupplyChainClient() as client:
        sku = client.get_sku("NonExistent@SKU")
except SupplyChainAPIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

### Client Configuration
```python
# Custom configuration
client = SupplyChainClient(
    base_url="http://my-api-server:8080",
    timeout=60  # 60 second timeout
)
```

### Default Values
- Base URL: `http://localhost:8000`
- Timeout: 30 seconds
- Default scenario: `"Base"`

## Running the Examples

1. **Basic Example**: Demonstrates all major functionality
```bash
python example_client_usage.py
```

2. **Interactive Usage**: Use the client directly
```bash
python supply_chain_client.py
```

## API Compatibility

This client is designed to work with the Supply Chain Planning API v1.0.0. All endpoints support scenario-aware operations.

### Supported Scenarios
- All methods accept a `scenario_id` parameter
- Default scenario is `"Base"`
- Use `list_scenarios()` to get available scenarios

## Development

### Adding New Methods
To add new API methods:

1. Add the method to `SupplyChainClient` class
2. Use the `_make_request()` helper for HTTP calls
3. Include proper type hints and documentation
4. Add error handling with `SupplyChainAPIError`

### Testing
Test the client against a running API server:

```bash
# Start the API server
python network_api.py

# Run the example in another terminal
python example_client_usage.py
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Ensure the API server is running on the specified URL
2. **Timeout Error**: Increase the timeout parameter for large datasets
3. **404 Errors**: Check that the scenario_id exists using `list_scenarios()`
4. **JSON Decode Error**: Verify the API server is returning valid JSON responses

### Debug Mode
Enable detailed logging by modifying the client:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = SupplyChainClient("http://localhost:8000")
``` 