# Custom API Routes & Endpoints

This directory is for creating **custom REST API endpoints** that extend the core Insight Ingenious API with your domain-specific functionality.

## 🎯 **Purpose**

Custom API routes enable:
- **🔌 Domain-Specific Endpoints** - Create APIs tailored to your business logic
- **📊 Data Processing APIs** - Add endpoints for data validation and transformation
- **🚀 Workflow Shortcuts** - Create simplified interfaces for common operations
- **🔗 External Integrations** - Build APIs for third-party system integration
- **📈 Analytics Endpoints** - Expose custom metrics and reporting APIs

## 🚀 **Quick Example**

Here's how to add a custom endpoint for bike sales analytics:

### **1. Create Your Route File (`bike_analytics.py`)**
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from models.bikes import RootModel, RootModel_Store
from ingenious.models.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1/bikes", tags=["Bike Analytics"])

class SalesAnalyticsRequest(BaseModel):
    """Request model for sales analytics"""
    stores: List[RootModel_Store]
    date_range: str = "last_30_days"
    include_sentiment: bool = True

class SalesAnalyticsResponse(BaseModel):
    """Response model for sales analytics"""
    total_sales: int
    revenue: float
    top_products: List[Dict[str, Any]]
    sentiment_summary: Dict[str, float]
    recommendations: List[str]

@router.post("/analytics", response_model=SalesAnalyticsResponse)
async def get_sales_analytics(request: SalesAnalyticsRequest):
    """
    🧠 Analyze bike sales data and return comprehensive insights

    This endpoint processes bike sales data and returns:
    - Sales volume and revenue metrics
    - Top performing products
    - Customer sentiment analysis
    - Actionable business recommendations
    """
    try:
        # Process the data
        bike_data = RootModel(stores=request.stores)

        # Calculate metrics
        total_sales = sum(
            sum(sale.quantity_sold for sale in store.bike_sales)
            for store in bike_data.stores
        )

        # Get AI-powered insights using the bike-insights workflow
        chat_request = ChatRequest(
            user_prompt=bike_data.json(),
            conversation_flow="bike-insights",
            thread_id=f"api_call_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # Execute workflow (you'd get chat_service from dependency injection)
        # ai_response = await chat_service.get_chat_response(chat_request)

        return SalesAnalyticsResponse(
            total_sales=total_sales,
            revenue=calculate_revenue(bike_data),
            top_products=get_top_products(bike_data),
            sentiment_summary=analyze_sentiment(bike_data),
            recommendations=["Focus on top performers", "Address comfort issues"]
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def bike_analytics_health():
    """Health check for bike analytics service"""
    return {"status": "healthy", "service": "bike_analytics"}
```

### **2. Register Your Routes**
Create or update `__init__.py`:
```python
from fastapi import FastAPI
from .bike_analytics import router as bike_router

def register_custom_routes(app: FastAPI):
    """Register all custom API routes"""
    app.include_router(bike_router)

    # Add more routers here
    # app.include_router(customer_router)
    # app.include_router(inventory_router)
```

## 🛠️ **API Development Patterns**

### **Data Validation Endpoints**
```python
@router.post("/validate-sales-data")
async def validate_sales_data(data: Dict[str, Any]):
    """✅ Validate bike sales data structure"""
    try:
        # Use your Pydantic models for validation
        validated_data = RootModel(**data)
        return {
            "valid": True,
            "stores_count": len(validated_data.stores),
            "total_sales": sum(len(store.bike_sales) for store in validated_data.stores)
        }
    except ValidationError as e:
        return {
            "valid": False,
            "errors": e.errors(),
            "message": "Data validation failed"
        }
```

### **Workflow Trigger Endpoints**
```python
@router.post("/trigger-analysis/{workflow_name}")
async def trigger_workflow(
    workflow_name: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """🚀 Trigger AI workflow asynchronously"""

    # Validate workflow exists
    if workflow_name not in ["bike-insights", "customer_analysis"]:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Queue background processing
    task_id = str(uuid.uuid4())
    background_tasks.add_task(
        process_workflow_async,
        task_id=task_id,
        workflow_name=workflow_name,
        data=data
    )

    return {
        "task_id": task_id,
        "status": "queued",
        "workflow": workflow_name,
        "message": "Analysis started. Check status with /status/{task_id}"
    }

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """📊 Check status of background workflow"""
    # Implementation depends on your background task system
    return {
        "task_id": task_id,
        "status": "completed",  # queued, running, completed, failed
        "result_url": f"/results/{task_id}"
    }
```

### **Export & Integration Endpoints**
```python
@router.get("/export/sales-report")
async def export_sales_report(
    format: str = "csv",
    date_from: str = None,
    date_to: str = None
):
    """📊 Export sales data in various formats"""

    if format not in ["csv", "json", "excel"]:
        raise HTTPException(status_code=400, detail="Unsupported format")

    # Get data from your workflow
    sales_data = await get_sales_data(date_from, date_to)

    if format == "csv":
        csv_content = sales_data.to_csv()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sales_report.csv"}
        )
    elif format == "json":
        return sales_data.dict()

@router.post("/webhooks/external-system")
async def handle_external_webhook(payload: Dict[str, Any]):
    """🔗 Handle webhooks from external systems"""

    # Transform external data format to your models
    transformed_data = transform_external_to_internal(payload)

    # Trigger appropriate workflow
    if payload.get("event_type") == "new_sales":
        await trigger_sales_analysis(transformed_data)

    return {"status": "processed", "event_type": payload.get("event_type")}
```

## 🧪 **Testing Your Custom APIs**

### **API Test Examples**
```python
import pytest
from fastapi.testclient import TestClient

def test_sales_analytics_endpoint():
    """Test bike sales analytics API"""

    test_data = {
        "stores": [
            {
                "name": "Test Store",
                "location": "Sydney",
                "bike_sales": [
                    {
                        "product_code": "EB-TEST-2023",
                        "quantity_sold": 5,
                        "sale_date": "2023-04-01",
                        "year": 2023,
                        "month": "April",
                        "customer_review": {
                            "rating": 4.5,
                            "comment": "Great bike!"
                        }
                    }
                ],
                "bike_stock": []
            }
        ]
    }

    response = client.post("/api/v1/bikes/analytics", json=test_data)

    assert response.status_code == 200
    result = response.json()
    assert result["total_sales"] == 5
    assert "recommendations" in result

def test_data_validation_endpoint():
    """Test data validation API"""

    # Valid data
    valid_response = client.post("/api/v1/bikes/validate-sales-data", json=valid_data)
    assert valid_response.json()["valid"] is True

    # Invalid data
    invalid_data = {"invalid": "structure"}
    invalid_response = client.post("/api/v1/bikes/validate-sales-data", json=invalid_data)
    assert invalid_response.json()["valid"] is False
```

### **Manual Testing with cURL**
```bash
# Test analytics endpoint
curl -X POST http://localhost:80/api/v1/bikes/analytics \
  -H "Content-Type: application/json" \
  -d @../sample_data/bike_sales_april_2023.json

# Test validation endpoint
curl -X POST http://localhost:80/api/v1/bikes/validate-sales-data \
  -H "Content-Type: application/json" \
  -d '{"stores": []}'

# Test workflow trigger
curl -X POST http://localhost:80/api/v1/bikes/trigger-analysis/bike-insights \
  -H "Content-Type: application/json" \
  -d @../sample_data/bike_sales_april_2023.json
```

## 📊 **API Documentation**

### **Automatic Documentation**
Your custom APIs will automatically appear in the FastAPI documentation:
- **📖 Interactive Docs:** http://localhost:80/docs
- **📋 API Schema:** http://localhost:80/redoc

### **Documentation Best Practices**
```python
@router.post("/complex-analysis")
async def complex_analysis(
    data: AnalysisRequest,
    include_predictions: bool = False,
    confidence_threshold: float = 0.8
) -> AnalysisResponse:
    """
    🧠 Perform complex business analysis using AI workflows

    This endpoint combines multiple AI agents to provide comprehensive analysis:

    **Features:**
    - Multi-agent processing for different data aspects
    - Configurable confidence thresholds
    - Optional predictive modeling
    - Real-time insights generation

    **Parameters:**
    - `data`: Input data following the defined schema
    - `include_predictions`: Whether to include future trend predictions
    - `confidence_threshold`: Minimum confidence for including insights (0.0-1.0)

    **Returns:**
    - Comprehensive analysis report
    - Actionable recommendations
    - Quality scores and confidence metrics

    **Example Usage:**
    ```python
    import requests

    response = requests.post("/api/v1/bikes/complex-analysis", json={
        "stores": [...],
        "analysis_type": "comprehensive"
    })
    ```
    """
    # Implementation here
```

## 🔧 **Integration Patterns**

### **Database Integration**
```python
from ingenious.db.chat_history_repository import ChatHistoryRepository

@router.get("/conversation-history/{thread_id}")
async def get_conversation_history(
    thread_id: str,
    chat_repo: ChatHistoryRepository = Depends()
):
    """📚 Get conversation history for a thread"""

    messages = await chat_repo.get_thread_messages(thread_id)
    return {
        "thread_id": thread_id,
        "message_count": len(messages),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at
            }
            for msg in messages
        ]
    }
```

### **File Storage Integration**
```python
from ingenious.files.files_repository import FileRepository

@router.post("/upload-sales-data")
async def upload_sales_data(
    file: UploadFile,
    file_repo: FileRepository = Depends()
):
    """📁 Upload and process sales data file"""

    # Save uploaded file
    file_path = await file_repo.save_file(
        container="sales-data",
        file_name=file.filename,
        content=await file.read()
    )

    # Process the file
    if file.filename.endswith('.json'):
        # Parse and validate JSON data
        content = await file_repo.read_file("sales-data", file.filename)
        sales_data = RootModel.parse_raw(content)

        # Trigger analysis workflow
        analysis_result = await trigger_sales_analysis(sales_data)

        return {
            "file_path": file_path,
            "status": "processed",
            "analysis_id": analysis_result.task_id
        }
```

## 📚 **Related Documentation**

- **🌊 Workflows:** See `../services/README.md` for workflow integration
- **🧠 Models:** See `../models/README.md` for request/response models
- **📊 Sample Data:** See `../sample_data/README.md` for test data
- **📖 FastAPI Docs:** [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)

---

**💡 Pro Tips:**
1. **🔒 Add Authentication** - Secure your APIs with proper auth
2. **📊 Include Monitoring** - Add logging and metrics collection
3. **🚀 Use Background Tasks** - For long-running AI workflows
4. **📖 Document Everything** - Write clear API documentation
5. **🧪 Test Thoroughly** - Include unit and integration tests
