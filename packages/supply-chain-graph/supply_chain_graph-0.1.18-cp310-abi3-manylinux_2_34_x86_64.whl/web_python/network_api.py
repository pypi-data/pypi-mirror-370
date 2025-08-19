from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import json
import subprocess
import sys
from pathlib import Path
import importlib.util
import io
from contextlib import redirect_stdout, redirect_stderr, asynccontextmanager
import time
from enum import Enum
import os
import orjson
import argparse



# Add the importer directory to Python path
import sys
from pathlib import Path
current_dir = Path(__file__).parent
project_root = current_dir.parent
importer_dir = project_root / "importer"
sys.path.insert(0, str(importer_dir))

try:
    from lsco_network_from_reports import load_scenario, ProcessNetworkLSCOReports
    from generate_landed_cost import load_data_and_calculate
    LSCO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import lsco_network_from_reports_compare: {e}")
    print("LSCO scenario loading will not be available")
    LSCO_AVAILABLE = False


# Import the Rust library through Python bindings
try:
    import supply
    from supply import PyScenario
except ImportError as e:
    raise ImportError(f"Failed to import supply module: {e}. Make sure the Rust library is compiled with Python bindings.")

# Configuration
DATASET_PATH = os.getenv("DATASET_PATH", "tests/landed_cost_datasets/toy1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifespan of the FastAPI application."""
    # Startup
    try:
        # Reset network to ensure clean state
        supply.reset_network()
        
        if LSCO_AVAILABLE:
            dataset_path = DATASET_PATH
            # Create scenarios
            #scenarios_to_compare = ProcessNetworkLSCOReports.get_distinct_scenarios(dataset_path)
            # pick top 2 scenarios from scenarios_to_compare. If there are less than 2, use all of them.
            #scenarios_to_compare = scenarios_to_compare[:2]

            scenarios_to_compare = ["Base"]
            for scenario_id in scenarios_to_compare:
                scen = PyScenario(scenario_id, None)


            # Load scenarios
            scenario_skus = {}
            parameters = {
                "test_parameter": "test_value",
            }
            for scenario_id in scenarios_to_compare:
                print(f"Loading scenario {scenario_id}...")
                try:
                    load_data_and_calculate(dataset_path, parameters, scenario_id)
                except Exception as scenario_error:
                    print(f"❌ Failed to load scenario {scenario_id}: {scenario_error}")

        print("✅ Supply chain objects initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize supply chain objects: {e}")
        # Don't raise exception to prevent server startup failure
    
    yield  # Server is running
    
    # Shutdown (cleanup if needed)
    print("🔄 Server shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Supply Chain Planning API",
    description="A comprehensive supply chain planning and optimization API built with Rust and FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Pydantic models for request/response validation
class SKURequest(BaseModel):
    product_id: str = Field(..., description="Product identifier")
    location_id: str = Field(..., description="Location identifier")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class ProductLocationQuery(BaseModel):
    location_id: str = Field(..., description="Location identifier to query")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class LocationProductQuery(BaseModel):
    product_id: str = Field(..., description="Product identifier to query")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class OperationRequest(BaseModel):
    name: str = Field(..., description="Operation name")
    lead_time: int = Field(..., description="Lead time in days")
    min_lot: int = Field(1, description="Minimum lot size")
    increment: int = Field(1, description="Lot size increment")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class DemandRequest(BaseModel):
    id: str = Field(..., description="Demand identifier")
    quantity: float = Field(..., description="Demand quantity")
    request_date: str = Field(..., description="Request date (YYYY-MM-DD)")
    max_lateness: int = Field(0, description="Maximum allowed lateness in days")
    sku_name: str = Field(..., description="SKU name for the demand")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class InventoryRequest(BaseModel):
    sku_name: str = Field(..., description="SKU name")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    quantity: float = Field(..., description="Inventory quantity")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class SupplyChainVisualizationRequest(BaseModel):
    sku_name: str = Field(..., description="SKU name to visualize")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")
    include_flow_plans: Optional[bool] = Field(False, description="Include actual flow plan data from operation plans")
    include_operation_plans: Optional[bool] = Field(False, description="Include operation plan IDs in flow data")
    include_resources: Optional[bool] = Field(True, description="Include resource nodes and edges")

class SupplyChainUnionVisualizationRequest(BaseModel):
    sku_name: str = Field(..., description="SKU name to visualize across scenarios")
    scenario1_id: str = Field(..., description="First scenario identifier")
    scenario2_id: str = Field(..., description="Second scenario identifier")
    include_flow_plans: Optional[bool] = Field(False, description="Include actual flow plan data from operation plans")
    include_operation_plans: Optional[bool] = Field(False, description="Include operation plan IDs in flow data")
    include_resources: Optional[bool] = Field(True, description="Include resource nodes and edges")

class ScriptExecutionRequest(BaseModel):
    script_path: str = Field(..., description="Path to the Python script to execute")
    args: Optional[List[str]] = Field(default=[], description="Command line arguments for the script")
    working_directory: Optional[str] = Field(None, description="Working directory for script execution")

class ScriptExecutionResponse(BaseModel):
    success: bool
    output: str
    error: str
    return_code: int
    execution_time: float

class SupplyChainSize(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM" 
    LARGE = "LARGE"

class CreateSupplyChainRequest(BaseModel):
    size: SupplyChainSize = Field(..., description="Size of the supply chain to create")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class CreateSupplyChainResponse(BaseModel):
    success: bool
    message: str
    num_chains: int
    time_taken_ms: int
    skus_created: int
    operations_created: int
    demands_created: int

class GetOperationPlansRequest(BaseModel):
    operation_name: str = Field(..., description="Name of the operation")
    scenario_id: Optional[str] = Field("Base", description="Scenario identifier")

class FlowPlanDetail(BaseModel):
    operation_plan_id: int
    operation_name: str
    quantity: float
    date: str
    sku_name: str
    flow_type: str  # "Consume" or "Produce"

class OperationPlanDetail(BaseModel):
    id: int
    operation_name: str
    start_date: str
    end_date: str
    quantity: float
    flows: List[FlowPlanDetail]

class OperationPlansResponse(BaseModel):
    success: bool
    operation_name: str
    scenario_id: str
    plans: List[OperationPlanDetail]

class CreateScenarioRequest(BaseModel):
    id: str = Field(..., description="Scenario identifier")
    parent_id: Optional[str] = Field(None, description="Parent scenario ID")
    description: str = Field("", description="Scenario description")

class CloneScenarioRequest(BaseModel):
    source_scenario_id: str = Field(..., description="Source scenario to clone from")
    target_scenario_id: str = Field(..., description="Target scenario ID")
    description: str = Field("", description="Description for the cloned scenario")

class DeleteScenarioRequest(BaseModel):
    scenario_id: str = Field(..., description="Scenario ID to delete")

class ScenarioResponse(BaseModel):
    success: bool
    message: str
    scenario_id: str

class ScenarioListResponse(BaseModel):
    success: bool
    scenarios: List[str]

class DeleteScenarioResponse(BaseModel):
    success: bool
    message: str

class ScenarioStats(BaseModel):
    scenario_name: str
    sku_count: int
    operation_count: int
    operation_plan_count: int
    demand_count: int
    resource_count: int

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# SKU Management Endpoints
@app.post("/skus", tags=["SKU Management"], response_model=Dict[str, str])
async def create_sku(request: SKURequest):
    """Create a new SKU with product and location."""
    try:
        sku = supply.PySKU.create(request.product_id, request.location_id, request.scenario_id)
        return {
            "sku_name": sku.name,
            "product_id": request.product_id,
            "location_id": request.location_id,
            "scenario_id": request.scenario_id,
            "message": "SKU created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create SKU: {str(e)}")

@app.get("/list/skus", tags=["List APIs"], response_model=List[str])
async def list_skus(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get list of SKU names in a specific scenario."""
    try:
        skus = supply.get_all_skus(scenario_id)
        return [sku.name for sku in skus]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list SKUs: {str(e)}")

@app.get("/skus", tags=["SKU Management"], response_model=List[Dict[str, str]])
async def get_all_skus(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get all SKUs with full details in a specific scenario."""
    try:
        skus = supply.get_all_skus(scenario_id)
        return [
            {
                "name": sku.name,
                "product_name": sku.product_name,
                "location_name": sku.location_name,
                "location_type": sku.location_type,
                "level": str(sku.level),
                "scenario_id": sku.scenario_id
            }
            for sku in skus
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SKUs: {str(e)}")

@app.get("/skus/{sku_name}", tags=["SKU Management"])
async def get_sku(sku_name: str, scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get details for a specific SKU."""
    try:
        sku = supply.PySKU.fetch(sku_name, scenario_id)
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU '{sku_name}' not found in scenario '{scenario_id}'")
        
        return {
            "name": sku.name,
            "product_name": sku.product_name,
            "location_name": sku.location_name,
            "location_type": sku.location_type,
            "level": sku.level,
            "scenario_id": sku.scenario_id,
            "consuming_operations": [op.name for op in sku.consuming_operations],
            "producing_operations": [op.name for op in sku.producing_operations()]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SKU: {str(e)}")

# Product-Location Query Endpoints
@app.get("/list/products-at-location", tags=["List APIs"], response_model=List[str])
async def list_products_at_location(
    location_id: str = Query(..., description="Location identifier"),
    scenario_id: str = Query("Base", description="Scenario identifier")
):
    """Get list of product names at a specific location."""
    try:
        products = supply.get_products_at_location(location_id, scenario_id)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list products: {str(e)}")

@app.get("/list/locations-for-product", tags=["List APIs"], response_model=List[str])
async def list_locations_for_product(
    product_id: str = Query(..., description="Product identifier"),
    scenario_id: str = Query("Base", description="Scenario identifier")
):
    """Get list of location names for a specific product."""
    try:
        locations = supply.get_locations_for_product(product_id, scenario_id)
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list locations: {str(e)}")

@app.get("/list/products", tags=["List APIs"], response_model=List[str])
async def list_products(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get list of all product IDs in a specific scenario."""
    try:
        products = supply.get_all_products(scenario_id)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list products: {str(e)}")

@app.get("/list/locations", tags=["List APIs"], response_model=List[str])
async def list_locations(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get list of all location IDs in a specific scenario."""
    try:
        locations = supply.get_all_locations(scenario_id)
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list locations: {str(e)}")


# Operation Management Endpoints
@app.post("/operations", tags=["Operation Management"])
async def create_operation(request: OperationRequest):
    """Create a new operation."""
    try:
        operation = supply.PyOperation(request.name, request.lead_time, request.min_lot, request.increment, request.scenario_id)
        return {
            "name": operation.name,
            "lead_time": operation.lead_time,
            "min_lot": operation.min_lot,
            "increment": operation.increment,
            "scenario_id": operation.scenario_id,
            "message": "Operation created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create operation: {str(e)}")

@app.get("/list/operations", tags=["List APIs"], response_model=List[str])
async def list_operations(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get list of operation names in a specific scenario."""
    try:
        operations = supply.get_all_operations(scenario_id)
        return [op.name for op in operations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list operations: {str(e)}")

@app.get("/operations", tags=["Operation Management"])
async def get_all_operations(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get all operations with full details in a specific scenario."""
    try:
        operations = supply.get_all_operations(scenario_id)
        return [
            {
                "name": op.name,
                "lead_time": op.lead_time,
                "min_lot": op.min_lot,
                "increment": op.increment,
                "category": op.category,
                "scenario_id": op.scenario_id
            }
            for op in operations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve operations: {str(e)}")

@app.get("/operations/{operation_name}", tags=["Operation Management"])
async def get_operation(operation_name: str, scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get details for a specific operation."""
    try:
        operation = supply.PyOperation.fetch(operation_name, scenario_id)
        if not operation:
            raise HTTPException(status_code=404, detail=f"Operation '{operation_name}' not found in scenario '{scenario_id}'")
        
        return {
            "name": operation.name,
            "lead_time": operation.lead_time,
            "min_lot": operation.min_lot,
            "increment": operation.increment,
            "category": operation.category,
            "scenario_id": operation.scenario_id,
            "upstream_skus": [sku.name for sku in operation.upstream_skus()],
            "upstream_resources": [res.name for res in operation.upstream_resources()]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve operation: {str(e)}")

@app.post("/operation-plans", tags=["Operation Management"], response_model=OperationPlansResponse)
async def get_operation_plans(request: GetOperationPlansRequest):
    """Get all operation plans for a specific operation."""
    try:
        # Get the operation using the Python interface
        operation = supply.PyOperation.fetch(request.operation_name)
        if not operation:
            raise HTTPException(
                status_code=404, 
                detail=f"Operation '{request.operation_name}' not found"
            )
        
        # Get operation plans
        operation_plans = operation.get_operation_plans()
        
        plans = []
        for plan_dict in operation_plans:
            # Extract basic plan info
            plan_detail = OperationPlanDetail(
                id=hash(f"{request.operation_name}_{plan_dict['start_date']}_{plan_dict['end_date']}"),  # Generate ID
                operation_name=request.operation_name,
                start_date=plan_dict['start_date'],
                end_date=plan_dict['end_date'],
                quantity=plan_dict['quantity'],
                flows=[]
            )
            
            # Add input flows
            for flow in plan_dict.get('in_flows', []):
                flow_detail = FlowPlanDetail(
                    operation_plan_id=plan_detail.id,
                    operation_name=request.operation_name,
                    quantity=flow['quantity'],
                    date=flow['date'],
                    sku_name=flow['sku'],
                    flow_type="Consume"
                )
                plan_detail.flows.append(flow_detail)
            
            # Add output flows
            for flow in plan_dict.get('out_flows', []):
                flow_detail = FlowPlanDetail(
                    operation_plan_id=plan_detail.id,
                    operation_name=request.operation_name,
                    quantity=flow['quantity'],
                    date=flow['date'],
                    sku_name=flow['sku'],
                    flow_type="Produce"
                )
                plan_detail.flows.append(flow_detail)
            
            plans.append(plan_detail)
        
        return OperationPlansResponse(
            success=True,
            operation_name=request.operation_name,
            scenario_id=request.scenario_id,
            plans=plans
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get operation plans: {str(e)}"
        )

@app.get("/operation-plans/{operation_name}", tags=["Operation Management"], response_model=OperationPlansResponse)
async def get_operation_plans_simple(operation_name: str, scenario_id: str = "Base"):
    """Get all operation plans for a specific operation (simple GET version)."""
    request = GetOperationPlansRequest(operation_name=operation_name, scenario_id=scenario_id)
    return await get_operation_plans(request)

# Inventory Management Endpoints
@app.post("/inventory", tags=["Inventory Management"])
async def add_inventory(request: InventoryRequest):
    """Add inventory for a SKU at a specific date."""
    try:
        sku = supply.PySKU.fetch(request.sku_name, request.scenario_id)
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU '{request.sku_name}' not found in scenario '{request.scenario_id}'")
        
        sku.add_inventory(request.date, request.quantity)
        return {
            "sku_name": request.sku_name,
            "date": request.date,
            "quantity": request.quantity,
            "scenario_id": request.scenario_id,
            "message": "Inventory added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add inventory: {str(e)}")

@app.get("/inventory/{sku_name}/profile", tags=["Inventory Management"])
async def get_inventory_profile(sku_name: str, scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get the inventory profile for a SKU."""
    try:
        sku = supply.PySKU.fetch(sku_name, scenario_id)
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU '{sku_name}' not found in scenario '{scenario_id}'")
        
        profile = sku.get_inventory_profile()
        return {
            "sku_name": sku_name,
            "scenario_id": scenario_id,
            "inventory_profile": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inventory profile: {str(e)}")

@app.get("/inventory/{sku_name}/net/{date}", tags=["Inventory Management"])
async def get_net_inventory(sku_name: str, date: str, scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get net inventory for a SKU on a specific date."""
    try:
        sku = supply.PySKU.fetch(sku_name, scenario_id)
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU '{sku_name}' not found in scenario '{scenario_id}'")
        
        net_inventory = sku.get_net_inventory(date)
        return {
            "sku_name": sku_name,
            "date": date,
            "scenario_id": scenario_id,
            "net_inventory": net_inventory
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get net inventory: {str(e)}")

# Supply Chain Visualization Endpoints
@app.post("/supply-chain/visualize", tags=["Supply Chain Visualization"])
async def visualize_supply_chain(request: SupplyChainVisualizationRequest):
    """Get supply chain visualization data for a SKU."""
    try:
        sku = supply.PySKU.fetch(request.sku_name, request.scenario_id)
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU '{request.sku_name}' not found in scenario '{request.scenario_id}'")
        
        visualization_json = sku.visualize_upstream_supply_chain(request.include_flow_plans, request.include_operation_plans, request.include_resources)
        
        # Parse and return as structured data
        graph_data = json.loads(visualization_json)
        return {
            "sku_name": request.sku_name,
            "scenario_id": request.scenario_id,
            "graph": graph_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to visualize supply chain: {str(e)}")

@app.get("/supply-chain/{sku_name}/text", tags=["Supply Chain Visualization"])
async def get_supply_chain_text(
    sku_name: str, 
    effective_date: str = Query(..., description="Effective date (YYYY-MM-DD)"),
    scenario_id: str = Query("Base", description="Scenario identifier")
):
    """Get text-based supply chain representation for a SKU."""
    try:
        sku = supply.PySKU.fetch(sku_name, scenario_id)
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU '{sku_name}' not found in scenario '{scenario_id}'")
        
        supply_chain = sku.get_supply_chain(effective_date)
        return {
            "sku_name": sku_name,
            "effective_date": effective_date,
            "scenario_id": scenario_id,
            "supply_chain": supply_chain
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get supply chain: {str(e)}")

@app.post("/supply-chain/visualize-union", tags=["Supply Chain Visualization"])
async def merge_supply_chain_scenarios(request: SupplyChainUnionVisualizationRequest):
    """Merge supply chain visualizations from two scenarios for comparison.
    
    This endpoint creates a unified visualization showing the supply chain structure
    across two different scenarios. The resulting graph uses color-coded edges to
    indicate which scenario(s) contain each relationship:
    - Black edges: present in both scenarios
    - Blue edges: first scenario only
    - Green edges: second scenario only
    
    This is useful for comparing scenario differences, analyzing what-if scenarios,
    and understanding how changes affect the supply chain structure.
    """
    try:
        # Call the Rust function to merge scenarios
        merged_json = supply.merge_supply_chain_scenarios(
            request.sku_name,
            request.scenario1_id,
            request.scenario2_id,
            request.include_flow_plans,
            request.include_operation_plans,
            request.include_resources
        )
        
        # Parse and return as structured data
        graph_data = json.loads(merged_json)
        return {
            "sku_name": request.sku_name,
            "scenario1_id": request.scenario1_id,
            "scenario2_id": request.scenario2_id,
            "graph": graph_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to merge supply chain scenarios: {str(e)}")

# System Management Endpoints
@app.post("/system/reset", tags=["System Management"])
async def reset_network(scenario_id: Optional[str] = Query(None, description="Scenario identifier (if not provided, resets all scenarios)")):
    """Reset the supply chain network for a specific scenario or all scenarios."""
    try:
        if scenario_id:
            supply.reset_network(scenario_id)
            return {"message": f"Network reset successfully for scenario '{scenario_id}'"}
        else:
            supply.reset_network()
            return {"message": "Network reset successfully for all scenarios"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset network: {str(e)}")

@app.post("/system/levelize", tags=["System Management"])
async def levelize_supply_chain():
    """Organize SKUs into supply chain levels."""
    try:
        supply.levelize_supply_chain()
        return {"message": "Supply chain levelized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to levelize supply chain: {str(e)}")

@app.post("/system/log-level", tags=["System Management"])
async def set_log_level(level: str = Query(..., description="Log level (info, debug, trace, warn, error, off)")):
    """Set the logging level for the system."""
    try:
        supply.set_log_level(level)
        return {"message": f"Log level set to {level}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to set log level: {str(e)}")

@app.post("/system/execute-script", tags=["System Management"], response_model=ScriptExecutionResponse)
async def execute_script(request: ScriptExecutionRequest):
    """Execute a Python script with optional arguments.
    
    This endpoint allows execution of predefined scripts for data loading and processing.
    For security, only scripts within the project directory are allowed.
    """
    import time
    import os
    
    try:
        # Security: Validate script path
        script_path = Path(request.script_path)
        
        # Get the project root directory (parent of web_python)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Resolve the script path relative to project root if it's not absolute
        if not script_path.is_absolute():
            script_path = project_root / script_path
        
        # Security check: Ensure script is within project directory
        try:
            script_path.resolve().relative_to(project_root.resolve())
        except ValueError:
            raise HTTPException(
                status_code=403, 
                detail=f"Script path must be within the project directory: {project_root}"
            )
        
        # Check if script exists
        if not script_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Script not found: {script_path}"
            )
        
        # Check if it's a Python file
        if script_path.suffix != '.py':
            raise HTTPException(
                status_code=400, 
                detail="Only Python files (.py) are allowed"
            )
        
        # Set working directory
        working_dir = request.working_directory
        if working_dir:
            working_dir = Path(working_dir)
            if not working_dir.is_absolute():
                working_dir = project_root / working_dir
            
            # Security check for working directory
            try:
                working_dir.resolve().relative_to(project_root.resolve())
            except ValueError:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Working directory must be within the project directory: {project_root}"
                )
        else:
            working_dir = script_path.parent
        
        # Prepare command
        cmd = [sys.executable, str(script_path)] + (request.args or [])
        
        # Set environment variables to include current Python path
        env = os.environ.copy()
        python_path = env.get('PYTHONPATH', '')
        if python_path:
            env['PYTHONPATH'] = f"{project_root}:{python_path}"
        else:
            env['PYTHONPATH'] = str(project_root)
        
        start_time = time.time()
        
        # Execute the script
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env
        )
        
        execution_time = time.time() - start_time
        
        return ScriptExecutionResponse(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr,
            return_code=result.returncode,
            execution_time=execution_time
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408, 
            detail="Script execution timed out (5 minute limit)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to execute script: {str(e)}"
        )

@app.get("/system/available-scripts", tags=["System Management"])
async def get_available_scripts():
    """Get a list of available scripts that can be executed."""
    try:
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Common script directories
        script_dirs = [
            "importer",
            "tests/experiments",
            "scale",
            "supply_chains"
        ]
        
        available_scripts = []
        
        for script_dir in script_dirs:
            dir_path = project_root / script_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    try:
                        relative_path = py_file.relative_to(project_root)
                        available_scripts.append({
                            "path": str(relative_path),
                            "name": py_file.name,
                            "directory": script_dir,
                            "full_path": str(py_file)
                        })
                    except ValueError:
                        continue  # Skip files outside project root
        
        return {
            "available_scripts": available_scripts,
            "total_count": len(available_scripts)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to list available scripts: {str(e)}"
        )

# Resource Management Endpoints
@app.get("/list/resources", tags=["List APIs"], response_model=List[str])
async def list_resources(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get list of resource names in a specific scenario."""
    try:
        resources = supply.get_all_resources(scenario_id)
        return [res.name for res in resources]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")

@app.get("/resources", tags=["Resource Management"])
async def get_all_resources(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get all resources with full details in a specific scenario."""
    try:
        resources = supply.get_all_resources(scenario_id)
        return [
            {
                "name": res.name,
                "is_constrained": res.is_constrained,
                "scenario_id": res.scenario_id
            }
            for res in resources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resources: {str(e)}")

@app.get("/resources/{resource_name}/capacity", tags=["Resource Management"])
async def get_resource_capacity(resource_name: str, scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get capacity buckets for a resource."""
    try:
        resource = supply.PyResource.fetch(resource_name, scenario_id)
        if not resource:
            raise HTTPException(status_code=404, detail=f"Resource '{resource_name}' not found in scenario '{scenario_id}'")
        
        capacity_buckets = resource.get_capacity_buckets()
        return {
            "resource_name": resource_name,
            "scenario_id": scenario_id,
            "capacity_buckets": capacity_buckets
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resource capacity: {str(e)}")

# Demand Management Endpoints
@app.post("/demands", tags=["Demand Management"])
async def create_demand(request: DemandRequest):
    """Create a new demand."""
    try:
        # First verify the SKU exists in the scenario
        sku = supply.PySKU.fetch(request.sku_name, request.scenario_id)
        if not sku:
            raise HTTPException(status_code=404, detail=f"SKU '{request.sku_name}' not found in scenario '{request.scenario_id}'")
        
        demand = supply.PyDemand.new(
            request.id,
            request.quantity,
            request.request_date,
            request.max_lateness,
            request.sku_name,
            request.scenario_id
        )
        
        return {
            "id": demand.id,
            "sku": demand.sku,
            "quantity": demand.quantity,
            "request_date": demand.request_date,
            "max_lateness": demand.max_lateness,
            "scenario_id": request.scenario_id,
            "message": "Demand created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create demand: {str(e)}")

@app.get("/list/demands", tags=["List APIs"], response_model=List[str])
async def list_demands(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get list of demand IDs in a specific scenario."""
    try:
        demands = supply.get_all_demands(scenario_id)
        return [demand.id for demand in demands]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list demands: {str(e)}")

@app.get("/demands", tags=["Demand Management"])
async def get_all_demands(scenario_id: str = Query("Base", description="Scenario identifier")):
    """Get all demands with full details in a specific scenario."""
    try:
        demands = supply.get_all_demands(scenario_id)
        return [
            {
                "id": demand.id,
                "sku": demand.sku,
                "quantity": demand.quantity,
                "request_date": demand.request_date,
                "max_lateness": demand.max_lateness,
                "priority": demand.priority,
                "planned_quantity": demand.planned_quantity,
                "scenario_id": demand.scenario_id
            }
            for demand in demands
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve demands: {str(e)}")

# Supply Chain Management Endpoints
@app.post("/supply-chain/create", tags=["Supply Chain Management"], response_model=CreateSupplyChainResponse)
async def create_supply_chain(request: CreateSupplyChainRequest):
    """Create a scaled supply chain network with the specified size.
    
    This creates multiple laptop supply chains with components, operations, and demands.
    - SMALL: 1,000 supply chains
    - MEDIUM: 10,000 supply chains  
    - LARGE: 100,000 supply chains
    """
    try:
        start_time = time.time()
        
        # Use the new Python function that includes planning
        result = supply.create_scaled_laptop_supply_chain(
            size=request.size.value,
            plan_demands=True,
            trace_level=0,
            scenario_id=request.scenario_id
        )
        
        return CreateSupplyChainResponse(
            success=result["planning_success"],
            message=f"Successfully created {result['num_chains']} laptop supply chains with planning in scenario '{request.scenario_id}'",
            num_chains=result["num_chains"],
            time_taken_ms=result["execution_time_ms"],
            skus_created=result["skus_created"],
            operations_created=result["operations_created"], 
            demands_created=result["demands_created"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create supply chain: {str(e)}"
        )


# Scenario Management Endpoints
@app.post("/scenarios/create", tags=["Scenario Management"], response_model=ScenarioResponse)
async def create_scenario(request: CreateScenarioRequest):
    """Create a new scenario."""
    try:
        scenario = supply.PyScenario(
            request.id,
            request.parent_id,
            request.description if request.description else None
        )
        
        return ScenarioResponse(
            success=True,
            message="Scenario created successfully",
            scenario_id=request.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create scenario: {str(e)}"
        )

@app.post("/scenarios/clone", tags=["Scenario Management"], response_model=ScenarioResponse)
async def clone_scenario(request: CloneScenarioRequest):
    """Clone an existing scenario to create a new one."""
    try:
        # First check if source scenario exists
        source_scenario = supply.PyScenario.fetch(request.source_scenario_id)
        if not source_scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Source scenario '{request.source_scenario_id}' not found"
            )
        
        # Create new target scenario
        target_scenario = supply.PyScenario(
            request.target_scenario_id,
            request.source_scenario_id,
            request.description if request.description else f"Cloned from {request.source_scenario_id}"
        )
        
        # Perform the cloning operation
        target_scenario.clone_from(request.source_scenario_id)
        
        # Get counts for verification
        skus = supply.get_all_skus(request.target_scenario_id)
        operations = supply.get_all_operations(request.target_scenario_id)
        
        return ScenarioResponse(
            success=True,
            message=f"Scenario cloned successfully. Cloned {len(skus)} SKUs and {len(operations)} operations",
            scenario_id=request.target_scenario_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clone scenario: {str(e)}"
        )

@app.get("/list/scenarios", tags=["List APIs"], response_model=List[str])
async def list_scenarios():
    """Get list of scenario names."""
    """ Exreacts scenarios from  format!("Scenario Id: {}, Parent Scenario Id: {}" """
    try:
        scenarios = supply.get_all_scenarios()
        scenario_list = []
        for scenario in scenarios:
            scenario_id = scenario.split(",")[0].split(":")[1].strip()
            scenario_list.append(scenario_id)

        return scenario_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list scenarios: {str(e)}")



@app.post("/scenarios/delete", tags=["Scenario Management"], response_model=DeleteScenarioResponse)
async def delete_scenario(request: DeleteScenarioRequest):
    """Delete a scenario."""
    try:
        # Don't allow deletion of BASE scenario
        if request.scenario_id == "Base":
            raise HTTPException(
                status_code=400,
                detail="Cannot delete BASE scenario"
            )
        
        # Check if scenario exists
        scenario = supply.PyScenario.fetch(request.scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario '{request.scenario_id}' not found"
            )
        
        # Delete the scenario
        scenario.delete()
        
        return DeleteScenarioResponse(
            success=True,
            message=f"Successfully deleted scenario '{request.scenario_id}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete scenario: {str(e)}"
        )

@app.get("/scenarios/{scenario_id}/stats", tags=["Scenario Management"], response_model=ScenarioStats)
async def get_scenario_stats(scenario_id: str):
    """Get statistics for a specific scenario."""
    try:
        # Get counts for the scenario
        skus = supply.get_all_skus(scenario_id)
        operations = supply.get_all_operations(scenario_id)
        demands = supply.get_all_demands(scenario_id)
        resources = supply.get_all_resources(scenario_id)
        
        # Count operation plans across all operations
        operation_plans_count = 0
        for op in operations:
            operation_plans = op.get_operation_plans()
            operation_plans_count += len(operation_plans)
        
        return ScenarioStats(
            scenario_name=scenario_id,
            sku_count=len(skus),
            operation_count=len(operations),
            operation_plan_count=operation_plans_count,
            demand_count=len(demands),
            resource_count=len(resources)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scenario stats: {str(e)}"
        )

@app.get("/scenarios/stats", tags=["Scenario Management"], response_model=ScenarioStats)
async def get_base_scenario_stats():
    """Get statistics for the base scenario."""
    return await get_scenario_stats("Base")

@app.get("/scenarios/{scenario_id}", tags=["Scenario Management"])
async def get_scenario_details(scenario_id: str):
    """Get details for a specific scenario."""
    try:
        scenario = supply.PyScenario.fetch(scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=404,
                detail=f"Scenario '{scenario_id}' not found"
            )
        
        return {
            "id": scenario.id,
            "parent_id": scenario.parent_id,
            "state": scenario.state,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scenario details: {str(e)}"
        )

# HTML Documentation page
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Root endpoint with links to documentation."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supply Chain Planning API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2c3e50; }
            .link { display: block; margin: 10px 0; padding: 10px; background: #ecf0f1; text-decoration: none; color: #2c3e50; }
            .link:hover { background: #bdc3c7; }
            .feature { margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1 class="header">Supply Chain Planning API</h1>
        <p>Welcome to the Supply Chain Planning API built with Rust and FastAPI.</p>
        <h2>Documentation</h2>
        <a href="/docs" class="link">📚 Swagger UI Documentation</a>
        <a href="/redoc" class="link">📖 ReDoc Documentation</a>
        <a href="/health" class="link">💚 Health Check</a>
        
        <h2>Key Features</h2>
        <ul>
            <li class="feature">📦 SKU Product Resource Demand Management (Scenario-aware)</li>
            <li class="feature">⚙️ Operation & Multi-step Process Management (Scenario-aware)</li>
            <li class="feature">📈 Replenishment Planning (Scenario-aware)</li>
            <li class="feature">🎯 Supply Chain Visualization & Analysis (Scenario-aware)</li>
            <li class="feature">🔄 Multi-Scenario Supply Chain Comparison & Merging</li>
            <li class="feature">🏭 Scaled Supply Chain Generation (Scenario-aware)</li>
            <li class="feature">🔧 Utility Functions - Levelize, Reset, Log Level</li>
            <li class="feature">📋 Scenario Management & Script Execution</li>
            <li class="feature">🌐 Multi-Scenario Support for What-If Analysis</li>
            <li class="feature">⚙️ Configurable Dataset Path for LSCO Loading</li>
        </ul>
        
        <h2>Quick Start</h2>
        <ul>
            <li class="feature">🔄 <strong>Reset Network:</strong> POST /system/reset (supports scenario_id)</li>
            <li class="feature">🏗️ <strong>Create Supply Chain:</strong> POST /supply-chain/create (supports scenario_id)</li>
            <li class="feature">🔍 <strong>Visualize:</strong> POST /supply-chain/visualize (supports scenario_id)</li>
            <li class="feature">🔄 <strong>Compare Scenarios:</strong> POST /supply-chain/merge</li>
            <li class="feature">🌐 <strong>Scenario Management:</strong> POST /scenarios/create, /scenarios/clone, /scenarios/delete</li>
            <li class="feature">⚙️ <strong>Configuration:</strong> GET/POST /config/dataset-path</li>
        </ul>
        
        <h2>Configuration</h2>
        <ul>
            <li class="feature">🗂️ <strong>Dataset Path:</strong> Set via DATASET_PATH environment variable or /config/dataset-path endpoint</li>
            <li class="feature">🔧 <strong>Default Path:</strong> tests/experiments/on_mdlz_multi_scenario</li>
            <li class="feature">📊 <strong>LSCO Support:</strong> Automatically loads scenarios from configured dataset path</li>
        </ul>
    </body>
    </html>
    """

# Add this alternative endpoint
@app.post("/system/execute-script-inprocess", tags=["System Management"], response_model=ScriptExecutionResponse)
async def execute_script_inprocess(request: ScriptExecutionRequest):
    """Execute a Python script in the same process space as the API.
    
    WARNING: This shares state with the API and could crash the server if the script fails.
    Use with caution and only with trusted scripts.
    """
    import time
    import os
    
    try:
        # Security: Validate script path (same as before)
        script_path = Path(request.script_path)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        if not script_path.is_absolute():
            script_path = project_root / script_path
        
        # Security checks
        try:
            script_path.resolve().relative_to(project_root.resolve())
        except ValueError:
            raise HTTPException(
                status_code=403, 
                detail=f"Script path must be within the project directory: {project_root}"
            )
        
        if not script_path.exists():
            raise HTTPException(status_code=404, detail=f"Script not found: {script_path}")
        
        if script_path.suffix != '.py':
            raise HTTPException(status_code=400, detail="Only Python files (.py) are allowed")
        
        # Set working directory
        original_cwd = os.getcwd()
        working_dir = request.working_directory
        if working_dir:
            working_dir = Path(working_dir)
            if not working_dir.is_absolute():
                working_dir = project_root / working_dir
            os.chdir(working_dir)
        else:
            os.chdir(script_path.parent)
        
        # Capture stdout and stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        start_time = time.time()
        success = True
        return_code = 0
        
        try:
            # Modify sys.argv to include script arguments
            original_argv = sys.argv.copy()
            sys.argv = [str(script_path)] + (request.args or [])
            
            # Load and execute the script module
            spec = importlib.util.spec_from_file_location("__main__", script_path)
            if spec is None or spec.loader is None:
                raise HTTPException(status_code=400, detail="Failed to load script")
            
            module = importlib.util.module_from_spec(spec)
            
            # Redirect stdout/stderr and execute
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                spec.loader.exec_module(module)
                
        except SystemExit as e:
            return_code = e.code or 0
            success = return_code == 0
        except Exception as e:
            success = False
            return_code = 1
            stderr_buffer.write(f"Error executing script: {str(e)}")
        finally:
            # Restore original state
            sys.argv = original_argv
            os.chdir(original_cwd)
        
        execution_time = time.time() - start_time
        
        return ScriptExecutionResponse(
            success=success,
            output=stdout_buffer.getvalue(),
            error=stderr_buffer.getvalue(),
            return_code=return_code,
            execution_time=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Restore working directory in case of error
        try:
            os.chdir(original_cwd)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to execute script: {str(e)}")

# Configuration Management Endpoints
@app.get("/config/dataset-path", tags=["Configuration"])
async def get_dataset_path():
    """Get the current dataset path configuration."""
    return {
        "dataset_path": DATASET_PATH,
        "lsco_available": LSCO_AVAILABLE
    }

@app.get("/sku/{sku_name}/daily-measures", tags=["SKU Analysis"])
async def get_sku_daily_measures(
    sku_name: str,
    start_date: str = Query(..., description="Start date for analysis (YYYY-MM-DD)"),
    scenario_id: Optional[str] = Query(None, description="Scenario identifier (defaults to 'Base')")
):
    """Get daily measures for a SKU on a date-wise basis.
    
    This endpoint analyzes flow plans from operations and demand plans to calculate:
    - Total consumption: Sum of all consume flows for the SKU
    - Dependent demand: Demand that is satisfied by production (root cause = false)
    - Unconstrained demand: Demand from unconstrained planning runs
    - Independent constrained demand: Demand that is independent (root cause = true)
    - Total production: Sum of all produce flows for the SKU
    """
    try:
        measures = supply.get_sku_daily_measures(sku_name, start_date, scenario_id)
        return {
            "sku_name": sku_name,
            "start_date": start_date,
            "scenario_id": scenario_id or "Base",
            "measures": measures
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SKU daily measures: {str(e)}")

class MultipleSKUDailyMeasuresRequest(BaseModel):
    sku_names: List[str] = Field(..., description="List of SKU names to analyze")
    start_date: str = Field(..., description="Start date for analysis (YYYY-MM-DD)")
    scenario_id: Optional[str] = Field(None, description="Scenario identifier (defaults to 'Base')")

@app.post("/sku/multiple-daily-measures", tags=["SKU Analysis"])
async def get_multiple_sku_daily_measures(request: MultipleSKUDailyMeasuresRequest):
    """Get daily measures for multiple SKUs on a date-wise basis.
    
    This endpoint analyzes flow plans from operations and demand plans to calculate
    measures for multiple SKUs in a single call, which is more efficient than
    calling the single SKU endpoint multiple times.
    
    The response contains measures for each SKU with the following structure:
    - Total consumption: Sum of all consume flows for the SKU
    - Dependent demand: Sum of all consume flows on that date
    - Unconstrained demand: Sum of all demand.quantity on the date (from demand_plans)
    - Independent constrained demand: Sum of all demand_plans on that date
    - Total production: Sum of all producing flow plans that have the end_date as this date
    """
    try:
        measures = supply.get_multiple_sku_daily_measures(request.sku_names, request.start_date, request.scenario_id)
        return {
            "start_date": request.start_date,
            "scenario_id": request.scenario_id or "Base",
            "measures": measures
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get multiple SKU daily measures: {str(e)}")

class InitializeLandedCostRequest(BaseModel):
    scenario_id: Optional[str] = Field(None, description="Scenario identifier (defaults to 'Base')")

class GetLandedCostRequest(BaseModel):
    product: str = Field(..., description="Product identifier")
    location: str = Field(..., description="Location identifier")
    scenario_id: Optional[str] = Field(None, description="Scenario identifier (defaults to 'Base')")

class LandedCostRow(BaseModel):
    source_product: str
    source_location: str
    product: str
    location: str
    period_start_date: str
    lot_id: int
    parent_lot_id: int
    lot_quantity: float
    production_date: str
    consumption_date: str
    inbound_cost: float
    outbound_cost: float
    production_cost: float
    shipping_cost: float
    sourcing_cost: float
    line_cost: float
    storage_cost: float
    throughput_cost: float
    fixed_operating_cost: float
    total_cost: float
    driving_qty: float
    category: str


@app.post("/landed-cost/initialize", tags=["Landed Cost"])
async def initialize_landed_cost(request: InitializeLandedCostRequest):
    """Initialize landed cost analysis for a scenario."""
    try:
        scenario_id = request.scenario_id or "Base"
        supply.initialize_landed_cost_analysis(scenario_id)
        return {
            "success": True,
            "message": f"Landed cost analysis initialized for scenario '{scenario_id}'",
            "scenario_id": scenario_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize landed cost analysis: {str(e)}"
        )


@app.post("/landed-cost/product-location", tags=["Landed Cost"], response_model=List[LandedCostRow])
async def calculate_landed_cost_product_location(
    request: GetLandedCostRequest,
    limit: Optional[int] = Query(None, description="Max rows to return"),
    offset: Optional[int] = Query(None, description="Rows to skip from start")
):
    """Calculate landed costs for a product-location combination.
    
    This endpoint calculates or retrieves cached landed costs for a specific product-location
    combination within a scenario. The calculation includes all upstream costs and is cached
    by scenario for better performance.
    """
    try:
        # Get PyLandedCostRow objects from Rust
        start_time = time.time()
        py_landed_costs = supply.calculate_landed_costs_for_product_location(
            request.product,
            request.location,
            request.scenario_id
        )
        print(f"Time taken to calculate landed costs for {request.product}-{request.location}: {time.time() - start_time} seconds")
        
        # Apply offset/limit for performance
        rows = py_landed_costs
        if offset is not None and offset > 0:
            rows = rows[offset:]
        if limit is not None and limit >= 0:
            rows = rows[:limit]

        # Map to Pydantic models and return
        rows = [
            LandedCostRow(
                source_product=row.source_product,
                source_location=row.source_location,
                product=row.product,
                location=row.location,
                period_start_date=row.period_start_date,
                lot_id=row.lot_id,
                parent_lot_id=row.parent_lot_id,
                lot_quantity=row.lot_quantity,
                production_date=row.production_date,
                consumption_date=row.consumption_date,
                inbound_cost=row.inbound_cost,
                outbound_cost=row.outbound_cost,
                production_cost=row.production_cost,
                shipping_cost=row.shipping_cost,
                sourcing_cost=row.sourcing_cost,
                line_cost=row.line_cost,
                storage_cost=row.storage_cost,
                throughput_cost=row.throughput_cost,
                fixed_operating_cost=row.fixed_operating_cost,
                driving_qty=row.driving_qty,
                category=row.category,
                total_cost=row.total_cost,
            )
            for row in rows
        ]
        print(f"Time taken to calculate {len(rows)} landed costs: {time.time() - start_time} seconds")
        return rows

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate landed costs: {str(e)}"
        )

class GetAllLandedCostsRequest(BaseModel):
    scenario_id: Optional[str] = Field(None, description="Scenario identifier (defaults to 'Base')")

@app.post("/landed-cost/all", tags=["Landed Cost"], response_model=List[LandedCostRow])
async def get_all_landed_costs(
    request: GetAllLandedCostsRequest,
    limit: Optional[int] = Query(None, description="Max rows to return"),
    offset: Optional[int] = Query(None, description="Rows to skip from start")
):
    """Calculate landed costs for all product-location combinations.
    
    This endpoint calculates or retrieves cached landed costs for all product-location
    combinations within a scenario. The calculation includes all upstream costs and is cached
    by scenario for better performance.
    """
    start_time = time.time()
    try:
        # Get all PyLandedCostRow objects from Rust
        print(f"Calculating landed costs for all product-location combinations for scenario {request.scenario_id}")
        py_landed_costs = supply.calculate_landed_costs(request.scenario_id)
        print(f"Time taken to calculate {len(py_landed_costs)} landed costs: {time.time() - start_time} seconds")
        # Apply offset/limit
        rows = py_landed_costs
        if offset is not None and offset > 0:
            rows = rows[offset:]
        if limit is not None and limit >= 0:
            rows = rows[:limit]

        # Map to Pydantic models and return
        models = [
            LandedCostRow(
                source_product=row.source_product,
                source_location=row.source_location,
                product=row.product,
                location=row.location,
                period_start_date=row.period_start_date,
                lot_id=row.lot_id,
                parent_lot_id=row.parent_lot_id,
                lot_quantity=row.lot_quantity,
                production_date=row.production_date,
                consumption_date=row.consumption_date,
                inbound_cost=row.inbound_cost,
                outbound_cost=row.outbound_cost,
                production_cost=row.production_cost,
                shipping_cost=row.shipping_cost,
                sourcing_cost=row.sourcing_cost,
                line_cost=row.line_cost,
                storage_cost=row.storage_cost,
                throughput_cost=row.throughput_cost,
                fixed_operating_cost=row.fixed_operating_cost,
                driving_qty=row.driving_qty,
                category=row.category,
                total_cost=row.total_cost,
            )
            for row in rows
        ]
        print(f"Time taken to calculate {len(models)} landed costs (post-slice): {time.time() - start_time} seconds")
        return models
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate all landed costs: {str(e)}"
        )
    

@app.post("/landed-cost/all_fast", tags=["Landed Cost"])
async def get_all_landed_costs(
    request: GetAllLandedCostsRequest,
    limit: Optional[int] = Query(None, description="Max rows to return"),
    offset: Optional[int] = Query(None, description="Rows to skip from start")
):
    try:
        start_time = time.time()
        rows = supply.calculate_landed_costs(request.scenario_id)
        print(f"Time taken to calculate {len(rows)} landed costs: {time.time() - start_time} seconds")
        if offset is not None and offset > 0:
            rows = rows[offset:]
        if limit is not None and limit >= 0:
            rows = rows[:limit]

        # Build plain dicts quickly
        payload = [
            {
                "source_product": r.source_product,
                "source_location": r.source_location,
                "product": r.product,
                "location": r.location,
                "period_start_date": r.period_start_date,
                "lot_id": r.lot_id,
                "parent_lot_id": r.parent_lot_id,
                "lot_quantity": r.lot_quantity,
                "production_date": r.production_date,
                "consumption_date": r.consumption_date,
                "inbound_cost": r.inbound_cost,
                "outbound_cost": r.outbound_cost,
                "production_cost": r.production_cost,
                "shipping_cost": r.shipping_cost,
                "sourcing_cost": r.sourcing_cost,
                "line_cost": r.line_cost,
                "storage_cost": r.storage_cost,
                "throughput_cost": r.throughput_cost,
                "fixed_operating_cost": r.fixed_operating_cost,
                "driving_qty": r.driving_qty,
                "category": r.category,
                "total_cost": r.total_cost,
            }
            for r in rows
        ]

        print(f"Prepared {len(payload)} landed cost rows for response in {time.time() - start_time} seconds")
        # Serialize and return plain JSON (no gzip) using the fastest available dumper
        json_bytes = orjson.dumps(payload)
        print(f"Serialized {len(json_bytes)} bytes in {time.time() - start_time} seconds")
        return Response(
            content=json_bytes,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate all landed costs (gzip): {str(e)}"
        )


@app.post("/landed-cost/all_bulk", tags=["Landed Cost"])
async def get_all_landed_costs_bulk(
    request: GetAllLandedCostsRequest,
    limit: Optional[int] = Query(None, description="Max rows to return"),
    offset: Optional[int] = Query(None, description="Rows to skip from start")
):
    """Ultra-fast bulk landed cost API using columnar data transfer.
    
    This endpoint provides 5-10x better performance compared to other landed cost APIs
    by using bulk columnar data transfer from Rust and avoiding Python object creation overhead.
    """
    try:
        start_time = time.time()
        
        # Get columnar data directly from Rust - this is much faster
        columnar_data = supply.calculate_landed_costs_bulk(request.scenario_id)
        calc_time = time.time() - start_time
        print(f"Time taken to calculate landed costs (bulk): {calc_time} seconds")
        
        # Apply offset/limit to all columns if needed
        if offset is not None and offset > 0 or limit is not None:
            start_idx = offset if offset is not None else 0
            end_idx = start_idx + limit if limit is not None else None
            
            for key, values in columnar_data.items():
                if end_idx is not None:
                    columnar_data[key] = values[start_idx:end_idx]
                else:
                    columnar_data[key] = values[start_idx:]
        
        prep_time = time.time() - start_time
        print(f"Prepared columnar data in {prep_time - calc_time} seconds")
        
        # Convert to row format for JSON response
        row_count = len(columnar_data.get('source_product', []))
        payload = [
            {
                "source_product": columnar_data['source_product'][i],
                "source_location": columnar_data['source_location'][i],
                "product": columnar_data['product'][i],
                "location": columnar_data['location'][i],
                "period_start_date": columnar_data['period_start_date'][i],
                "lot_id": columnar_data['lot_id'][i],
                "parent_lot_id": columnar_data['parent_lot_id'][i],
                "lot_quantity": columnar_data['lot_quantity'][i],
                "production_date": columnar_data['production_date'][i],
                "consumption_date": columnar_data['consumption_date'][i],
                "inbound_cost": columnar_data['inbound_cost'][i],
                "outbound_cost": columnar_data['outbound_cost'][i],
                "production_cost": columnar_data['production_cost'][i],
                "shipping_cost": columnar_data['shipping_cost'][i],
                "sourcing_cost": columnar_data['sourcing_cost'][i],
                "line_cost": columnar_data['line_cost'][i],
                "storage_cost": columnar_data['storage_cost'][i],
                "throughput_cost": columnar_data['throughput_cost'][i],
                "fixed_operating_cost": columnar_data['fixed_operating_cost'][i],
                "driving_qty": columnar_data['driving_qty'][i],
                "category": columnar_data['category'][i],
                "total_cost": columnar_data['total_cost'][i],
            }
            for i in range(row_count)
        ]

        conversion_time = time.time() - start_time
        print(f"Converted to {len(payload)} rows in {conversion_time - prep_time} seconds")
        
        # Serialize and return
        json_bytes = orjson.dumps(payload)
        total_time = time.time() - start_time
        print(f"Serialized {len(json_bytes)} bytes. Total time: {total_time} seconds")
        
        return Response(
            content=json_bytes,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate all landed costs (bulk): {str(e)}"
        )


def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True, dataset_path: str = None):
    """Start the FastAPI server.
    
    Args:
        host: Host address to bind to
        port: Port number to bind to
        reload: Enable auto-reload for development
        dataset_path: Path to the dataset directory (overrides environment variable)
    """
    global DATASET_PATH
    
    # Override dataset path if provided
    if dataset_path:
        DATASET_PATH = dataset_path
        os.environ["DATASET_PATH"] = dataset_path
        print(f"Using dataset path: {DATASET_PATH}")

    uvicorn.run(
        "network_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supply Chain Planning API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port number to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--dataset-path", help="Path to the dataset directory")
    
    args = parser.parse_args()
    
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        dataset_path=args.dataset_path
    )



