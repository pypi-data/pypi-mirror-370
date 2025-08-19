#!/usr/bin/env python3
"""
Example Usage of Supply Chain API Client

This script demonstrates how to use the SupplyChainClient to interact with
the Supply Chain Planning API across different scenarios.
"""

from supply_chain_client import SupplyChainClient, SupplyChainAPIError
from supply_chain_client import (
    print_sku_summary, 
    print_operation_summary, 
    print_resource_summary, 
    print_demand_summary
)


def main():
    """Main example function"""
    print("Supply Chain API Client - Example Usage")
    print("=" * 50)
    
    # Initialize the client
    client = SupplyChainClient("http://localhost:8000")
    
    try:
        # 1. Health Check
        print("\n1. Checking API Health...")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Timestamp: {health['timestamp']}")
        
        # 2. List Available Scenarios
        print("\n2. Getting Available Scenarios...")
        scenarios_response = client.list_scenarios()
        scenarios = scenarios_response.get('scenarios', [])
        print(f"   Available scenarios: {scenarios}")
        
        # 3. Get Scenario Statistics
        print("\n3. Getting Scenario Statistics...")
        for scenario in scenarios[:2]:  # Limit to first 2 scenarios
            try:
                stats = client.get_scenario_stats(scenario)
                print(f"\n   Scenario '{scenario}' Statistics:")
                print(f"     SKUs: {stats['sku_count']}")
                print(f"     Operations: {stats['operation_count']}")
                print(f"     Operation Plans: {stats['operation_plan_count']}")
                print(f"     Demands: {stats['demand_count']}")
                print(f"     Resources: {stats['resource_count']}")
            except SupplyChainAPIError as e:
                print(f"     Error getting stats for {scenario}: {e}")
        
        # 4. Explore Base Scenario in Detail
        base_scenario = "Base"
        print(f"\n4. Exploring '{base_scenario}' Scenario in Detail...")
        
        # Get SKUs
        print(f"\n   4a. SKUs in '{base_scenario}':")
        skus = client.get_all_skus(base_scenario)
        if skus:
            print_sku_summary(skus[:10])  # Show first 10 SKUs
            if len(skus) > 10:
                print(f"   ... and {len(skus) - 10} more SKUs")
        else:
            print("     No SKUs found")
        
        # Get Operations
        print(f"\n   4b. Operations in '{base_scenario}':")
        operations = client.get_all_operations(base_scenario)
        if operations:
            print_operation_summary(operations[:10])  # Show first 10 operations
            if len(operations) > 10:
                print(f"   ... and {len(operations) - 10} more operations")
        else:
            print("     No operations found")
        
        # Get Resources
        print(f"\n   4c. Resources in '{base_scenario}':")
        resources = client.get_all_resources(base_scenario)
        if resources:
            print_resource_summary(resources[:10])  # Show first 10 resources
            if len(resources) > 10:
                print(f"   ... and {len(resources) - 10} more resources")
        else:
            print("     No resources found")
        
        # Get Demands
        print(f"\n   4d. Demands in '{base_scenario}':")
        demands = client.get_all_demands(base_scenario)
        if demands:
            print_demand_summary(demands[:10])  # Show first 10 demands
            if len(demands) > 10:
                print(f"   ... and {len(demands) - 10} more demands")
        else:
            print("     No demands found")
        
        # 5. Detailed SKU Analysis
        if skus:
            print(f"\n5. Detailed Analysis of First SKU...")
            first_sku = skus[0]
            sku_name = first_sku['name']
            
            try:
                # Get SKU details
                sku_details = client.get_sku(sku_name, base_scenario)
                print(f"   SKU Details for '{sku_name}':")
                print(f"     Product: {sku_details['product_name']}")
                print(f"     Location: {sku_details['location_name']}")
                print(f"     Type: {sku_details['location_type']}")
                print(f"     Level: {sku_details['level']}")
                print(f"     Consuming Operations: {len(sku_details.get('consuming_operations', []))}")
                print(f"     Producing Operations: {len(sku_details.get('producing_operations', []))}")
                
                # Get inventory profile
                inventory = client.get_inventory_profile(sku_name, base_scenario)
                print(f"     Inventory Profile: {len(inventory.get('inventory_profile', []))} entries")
                
            except SupplyChainAPIError as e:
                print(f"     Error getting SKU details: {e}")
        
        # 6. Detailed Operation Analysis
        if operations:
            print(f"\n6. Detailed Analysis of First Operation...")
            first_operation = operations[0]
            operation_name = first_operation['name']
            
            try:
                # Get operation details
                op_details = client.get_operation(operation_name, base_scenario)
                print(f"   Operation Details for '{operation_name}':")
                print(f"     Lead Time: {op_details['lead_time']} days")
                print(f"     Min Lot: {op_details['min_lot']}")
                print(f"     Increment: {op_details['increment']}")
                print(f"     Category: {op_details['category']}")
                print(f"     Upstream SKUs: {len(op_details.get('upstream_skus', []))}")
                print(f"     Upstream Resources: {len(op_details.get('upstream_resources', []))}")
                
                # Get operation plans
                op_plans = client.get_operation_plans(operation_name, base_scenario)
                print(f"     Operation Plans: {len(op_plans.get('plans', []))}")
                
            except SupplyChainAPIError as e:
                print(f"     Error getting operation details: {e}")
        
        # 7. Resource Capacity Analysis
        if resources:
            print(f"\n7. Resource Capacity Analysis...")
            first_resource = resources[0]
            resource_name = first_resource['name']
            
            try:
                capacity_info = client.get_resource_capacity(resource_name, base_scenario)
                capacity_buckets = capacity_info.get('capacity_buckets', [])
                print(f"   Resource '{resource_name}' has {len(capacity_buckets)} capacity buckets")
                
            except SupplyChainAPIError as e:
                print(f"     Error getting resource capacity: {e}")
        
        # 8. Product-Location Queries
        if skus:
            print(f"\n8. Product-Location Queries...")
            first_sku = skus[0]
            product_name = first_sku['product_name']
            location_name = first_sku['location_name']
            
            try:
                # Get products at location
                products_at_location = client.get_products_at_location(location_name, base_scenario)
                products = products_at_location.get('products', [])
                print(f"   Products at location '{location_name}': {len(products)}")
                if products:
                    print(f"     Examples: {products[:5]}")
                
                # Get locations for product
                locations_for_product = client.get_locations_for_product(product_name, base_scenario)
                locations = locations_for_product.get('locations', [])
                print(f"   Locations for product '{product_name}': {len(locations)}")
                if locations:
                    print(f"     Examples: {locations[:5]}")
                
            except SupplyChainAPIError as e:
                print(f"     Error in product-location queries: {e}")
        
        # 9. Supply Chain Visualization
        if skus:
            print(f"\n9. Supply Chain Visualization...")
            first_sku = skus[0]
            sku_name = first_sku['name']
            
            try:
                visualization = client.visualize_supply_chain(sku_name, base_scenario)
                graph = visualization.get('graph', {})
                nodes = graph.get('nodes', [])
                edges = graph.get('edges', [])
                print(f"   Supply chain for '{sku_name}':")
                print(f"     Nodes: {len(nodes)}")
                print(f"     Edges: {len(edges)}")
                
            except SupplyChainAPIError as e:
                print(f"     Error getting visualization: {e}")
        
        print(f"\n10. Example completed successfully!")
        
    except SupplyChainAPIError as e:
        print(f"\nAPI Error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        client.session.close()


def compare_scenarios():
    """Example function to compare data across scenarios"""
    print("\n" + "=" * 50)
    print("Scenario Comparison Example")
    print("=" * 50)
    
    client = SupplyChainClient("http://localhost:8000")
    
    try:
        # Get available scenarios
        scenarios_response = client.list_scenarios()
        scenarios = scenarios_response.get('scenarios', [])
        
        if len(scenarios) < 2:
            print("Need at least 2 scenarios for comparison")
            return
        
        print(f"\nComparing scenarios: {scenarios[:2]}")
        
        for scenario in scenarios[:2]:
            print(f"\n--- Scenario: {scenario} ---")
            
            # Get stats
            stats = client.get_scenario_stats(scenario)
            print(f"SKUs: {stats['sku_count']}")
            print(f"Operations: {stats['operation_count']}")
            print(f"Demands: {stats['demand_count']}")
            print(f"Resources: {stats['resource_count']}")
            
            # Get first few SKUs
            skus = client.get_all_skus(scenario)
            if skus:
                print(f"Sample SKUs: {[sku['name'] for sku in skus[:3]]}")
            
    except SupplyChainAPIError as e:
        print(f"API Error: {e}")
    finally:
        client.session.close()


if __name__ == "__main__":
    main()
    compare_scenarios() 