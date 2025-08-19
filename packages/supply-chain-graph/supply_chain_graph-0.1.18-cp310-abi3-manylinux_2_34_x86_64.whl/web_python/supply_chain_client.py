#!/usr/bin/env python3
"""
Supply Chain API Client - Simplified Version

A lightweight Python client for the Supply Chain Planning API.
Includes health check, supply chain visualization, and list functionality.
"""

import requests
import json
from typing import Dict, Any, Optional, List

BASE_URL = "http://localhost:8000"

class SupplyChainAPIError(Exception):
    """Custom exception for API errors"""
    pass


class SupplyChainClient:
    """
    Lightweight client for Supply Chain Planning API
    
    Args:
        base_url: The base URL of the API (e.g., "http://localhost:8000")
        timeout: Request timeout in seconds (default: 30)
    """
    
    def __init__(self, base_url: str = BASE_URL, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data as dictionary
            
        Raises:
            SupplyChainAPIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params, json=data, timeout=self.timeout)
            else:
                raise SupplyChainAPIError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # Extract detailed error message from FastAPI response
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', str(e))
                raise SupplyChainAPIError(f"{error_detail}")
            except (ValueError, json.JSONDecodeError):
                # Fallback if response is not JSON
                raise SupplyChainAPIError(f"HTTP {response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise SupplyChainAPIError(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise SupplyChainAPIError(f"Invalid JSON response: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status
        
        Returns:
            Health status information
        """
        return self._make_request('GET', '/health')
    
    def visualize_supply_chain(self, sku_name: str, scenario_id: str = "Base") -> Dict[str, Any]:
        """
        Get supply chain visualization data for a SKU
        
        Args:
            sku_name: Name of the SKU to visualize
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            Supply chain graph data
        """
        data = {
            "sku_name": sku_name,
            "scenario_id": scenario_id
        }
        return self._make_request('POST', '/supply-chain/visualize', data=data)
    
    # List APIs
    def list_skus(self, scenario_id: str = "Base") -> List[str]:
        """
        Get list of SKU names in a scenario
        
        Args:
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of SKU names
        """
        params = {"scenario_id": scenario_id}
        return self._make_request('GET', '/list/skus', params=params)
    
    def list_operations(self, scenario_id: str = "Base") -> List[str]:
        """
        Get list of operation names in a scenario
        
        Args:
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of operation names
        """
        params = {"scenario_id": scenario_id}
        return self._make_request('GET', '/list/operations', params=params)
    
    def list_resources(self, scenario_id: str = "Base") -> List[str]:
        """
        Get list of resource names in a scenario
        
        Args:
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of resource names
        """
        params = {"scenario_id": scenario_id}
        return self._make_request('GET', '/list/resources', params=params)
    
    def list_demands(self, scenario_id: str = "Base") -> List[str]:
        """
        Get list of demand IDs in a scenario
        
        Args:
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of demand IDs
        """
        params = {"scenario_id": scenario_id}
        return self._make_request('GET', '/list/demands', params=params)
    
    def list_scenarios(self) -> List[str]:
        """
        Get list of scenario names
        
        Returns:
            List of scenario names
        """
        return self._make_request('GET', '/list/scenarios')
    
    def list_products_at_location(self, location_id: str, scenario_id: str = "Base") -> List[str]:
        """
        Get list of product names at a specific location
        
        Args:
            location_id: Location identifier
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of product names
        """
        params = {"location_id": location_id, "scenario_id": scenario_id}
        return self._make_request('GET', '/list/products', params=params)
    
    def list_locations_for_product(self, product_id: str, scenario_id: str = "Base") -> List[str]:
        """
        Get list of location names for a specific product
        
        Args:
            product_id: Product identifier
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of location names
        """
        params = {"product_id": product_id, "scenario_id": scenario_id}
        return self._make_request('GET', '/list/locations-for-product', params=params)

    def list_products(self, scenario_id: str = "Base") -> List[str]:
        """
        Get list of all product IDs in a scenario

        Args:
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of product IDs
        """
        params = {"scenario_id": scenario_id}
        return self._make_request('GET', '/list/products', params=params)

    def list_locations(self, scenario_id: str = "Base") -> List[str]:
        """
        Get list of all location IDs in a scenario

        Args:
            scenario_id: Scenario identifier (default: "Base")
            
        Returns:
            List of location IDs
        """
        params = {"scenario_id": scenario_id}
        return self._make_request('GET', '/list/locations', params=params)
    
    def get_sku_daily_measures(self, sku_name: str, start_date: str, scenario_id: Optional[str] = None) -> Dict:
        """
        Get daily measures for a SKU on a date-wise basis.
        
        Args:
            sku_name: Name of the SKU to analyze
            start_date: Start date for the analysis period (YYYY-MM-DD)
            scenario_id: Scenario identifier (optional, defaults to 'Base')
            
        Returns:
            Dictionary containing SKU daily measures with the following structure:
            {
                "sku_name": str,
                "start_date": str,
                "scenario_id": str,
                "measures": List[Dict] - Each dict contains:
                    - date: str (YYYY-MM-DD)
                    - total_consumption: float
                    - dependent_demand: float
                    - unconstrained_demand: float
                    - independent_constrained_demand: float
                    - total_production: float
            }
        """
        params = {"start_date": start_date}
        if scenario_id:
            params["scenario_id"] = scenario_id
            
        return self._make_request('GET', f'/sku/{sku_name}/daily-measures', params=params)
    
    def get_multiple_sku_daily_measures(self, sku_names: List[str], start_date: str, scenario_id: Optional[str] = None) -> Dict:
        """
        Get daily measures for multiple SKUs on a date-wise basis.
        
        Args:
            sku_names: List of SKU names to analyze
            start_date: Start date for the analysis period (YYYY-MM-DD)
            scenario_id: Scenario identifier (optional, defaults to 'Base')
            
        Returns:
            Dictionary containing measures for multiple SKUs with the following structure:
            {
                "start_date": str,
                "scenario_id": str,
                "measures": Dict[str, List[Dict]] - Dictionary mapping SKU names to their daily measures
                    Each measure dict contains:
                    - date: str (YYYY-MM-DD)
                    - total_consumption: float
                    - dependent_demand: float
                    - unconstrained_demand: float
                    - independent_constrained_demand: float
                    - total_production: float
            }
        """
        data = {
            "sku_names": sku_names,
            "start_date": start_date
        }
        if scenario_id:
            data["scenario_id"] = scenario_id
            
        return self._make_request('POST', '/sku/multiple-daily-measures', data=data)
    
    # Context Manager Support
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()




if __name__ == "__main__":
    # Example usage
    print("Supply Chain API Client - Simple Version")
    print("=" * 45)
    
    try:
        with SupplyChainClient("http://localhost:8000") as client:
            # Health check
            health = client.health_check()
            print(f"✅ API Status: {health['status']}")
            print(f"   Timestamp: {health['timestamp']}")
            
            # Example list operations
            print(f"\n📋 Testing List APIs...")
            try:
                scenarios = client.list_scenarios()
                print(f"   Scenarios: {scenarios}")
                
                skus = client.list_skus("Base")
                print(f"   SKUs in Base scenario: {len(skus)} items")
                if skus:
                    print(f"   First 3 SKUs: {skus[:3]}")
                
                operations = client.list_operations("Base")
                print(f"   Operations in Base scenario: {len(operations)} items")
                if operations:
                    print(f"   First 3 Operations: {operations[:3]}")
                    
            except SupplyChainAPIError as e:
                print(f"❌ List APIs failed: {e}")
            
            # Example visualization
            print(f"\n🔍 Testing Visualization...")
            try:
                viz = client.visualize_supply_chain("Liquor@India EU", "Base")
                print(f"   Visualization data retrieved successfully")
            except SupplyChainAPIError as e:
                print(f"❌ Visualization failed: {e}")
            
            # Example SKU daily measures
            print(f"\n📊 Testing SKU Daily Measures...")
            try:
                # Single SKU measures
                single_measures = client.get_sku_daily_measures("Liquor@India EU", "2024-01-01")
                print(f"   Single SKU measures retrieved successfully")
                
                # Multiple SKU measures
                multiple_measures = client.get_multiple_sku_daily_measures(
                    ["Liquor@India EU", "Liquor@India Plant"], 
                    "2024-01-01"
                )
                print(f"   Multiple SKU measures retrieved successfully")
                print(f"   Number of SKUs with measures: {len(multiple_measures['measures'])}")
                
            except SupplyChainAPIError as e:
                print(f"❌ SKU measures failed: {e}")
                
    except SupplyChainAPIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
 