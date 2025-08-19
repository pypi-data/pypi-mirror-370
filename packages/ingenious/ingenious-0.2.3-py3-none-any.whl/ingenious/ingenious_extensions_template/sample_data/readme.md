# Sample Data Directory

This directory contains sample datasets for testing and developing your AI workflows.

## 📊 **Available Sample Data**

### **🚴 Bike Sales Data (`bike_sales_april_2023.json`)**
Complete dataset for the **bike-insights** workflow demonstration:

- **📈 Sales Records:** 1000+ bike sales transactions
- **🏪 Multiple Stores:** Sydney, Melbourne, Brisbane locations
- **⭐ Customer Reviews:** Ratings and detailed feedback
- **📦 Inventory Data:** Stock levels and product specifications
- **🔄 Realistic Patterns:** Seasonal trends and customer behavior

**Data Structure:**
```json
{
  "stores": [
    {
      "name": "Bike World Sydney",
      "location": "NSW",
      "bike_sales": [
        {
          "product_code": "EB-SPECIALIZED-2023-TV",
          "quantity_sold": 5,
          "sale_date": "2023-04-01",
          "year": 2023,
          "month": "April",
          "customer_review": {
            "rating": 4.0,
            "comment": "Great bike for commuting!"
          }
        }
      ],
      "bike_stock": [
        {
          "bike": {
            "brand": "Specialized",
            "model": "Turbo Vado",
            "year": 2023,
            "price": 3200.0,
            "battery_capacity": 0.7,
            "motor_power": 350.0
          },
          "quantity": 12
        }
      ]
    }
  ]
}
```

### **📋 Event Configuration (`events.yml`)**
Test event definitions for the test harness:

```yaml
- identifier: '04'
  event_type: default
  file_name: bike_sales_april_2023.json
  response_content: no response generated
  conversation_flow: "bike-insights"
  identifier_group: "week1"
```

## 🧪 **Using Sample Data**

### **1. Test the Bike Insights Workflow**
```bash
# Direct API test with sample data
curl -X POST http://localhost:8081/api/v1/chat \
  -H "Content-Type: application/json" \
  -d @sample_data/bike_sales_april_2023.json \
  --data-urlencode "conversation_flow=bike-insights"
```

### **2. Run Automated Tests**
```bash
cd ../tests
python run_tests.py
```

### **3. Validate Data Models**
```python
from models.bikes import RootModel
import json

# Load and validate sample data
with open('sample_data/bike_sales_april_2023.json') as f:
    data = json.load(f)
    bike_data = RootModel(**data)
    print(f"✅ Loaded {len(bike_data.stores)} stores")
```

## 📝 **Creating Your Own Sample Data**

### **1. Follow the Data Model Structure**
- Reference `../models/bikes.py` for required fields
- Use Pydantic models for validation
- Include realistic test scenarios

### **2. Sample Data Best Practices**
```python
# ✅ Good: Realistic data with variety
{
  "stores": [
    {
      "name": "Sydney Bikes",
      "location": "NSW",
      "bike_sales": [
        {
          "product_code": "EB-TREK-2023-POWERFLY",
          "quantity_sold": 3,
          "sale_date": "2023-04-15",
          "customer_review": {
            "rating": 4.8,
            "comment": "Excellent battery life and smooth ride"
          }
        }
      ]
    }
  ]
}

# ❌ Avoid: Minimal or unrealistic data
{
  "stores": [{"name": "test", "location": "test", "bike_sales": []}]
}
```

### **3. Data Categories to Include**
- **📊 Positive Examples** - High ratings, good sales
- **⚠️ Edge Cases** - Low ratings, unusual patterns
- **🔄 Variety** - Different locations, products, time periods
- **📈 Trends** - Seasonal patterns, product popularity

## 🎯 **Sample Data for Different Workflows**

### **📊 Classification Agent**
```json
{
  "user_input": "I love this product, fast delivery!",
  "category": "positive_feedback",
  "confidence": 0.95
}
```

### **🔍 Knowledge Base Agent**
```json
{
  "query": "bike maintenance tips",
  "expected_topics": ["maintenance", "repair", "service"]
}
```

### **💾 SQL Agent**
```json
{
  "query": "Show top selling bikes by location",
  "expected_tables": ["sales", "products", "locations"]
}
```

## 🛠️ **Data Generation Tools**

### **Generate Test Data with AI**
```python
# Use Insight Ingenious to generate sample data
prompt = """
Generate realistic bike sales data for testing:
- 5 different stores across Australia
- 20 sales transactions per store
- Mix of electric, road, and mountain bikes
- Customer reviews with ratings 1-5
- Realistic product codes and pricing
"""
```

### **Data Validation Script**
```python
#!/usr/bin/env python3
"""Validate all sample data files"""

import json
import yaml
from pathlib import Path
from models.bikes import RootModel

def validate_sample_data():
    sample_dir = Path(__file__).parent

    # Validate JSON files
    for json_file in sample_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
                RootModel(**data)
            print(f"✅ {json_file.name} - Valid")
        except Exception as e:
            print(f"❌ {json_file.name} - Error: {e}")

    # Validate YAML files
    for yaml_file in sample_dir.glob("*.yml"):
        try:
            with open(yaml_file) as f:
                yaml.safe_load(f)
            print(f"✅ {yaml_file.name} - Valid YAML")
        except Exception as e:
            print(f"❌ {yaml_file.name} - Error: {e}")

if __name__ == "__main__":
    validate_sample_data()
```

## 🔄 **Updating Sample Data**

### **Version Control Best Practices**
- **📝 Document Changes** - Add comments explaining updates
- **🔄 Maintain Compatibility** - Don't break existing tests
- **📊 Add Variety** - Include new scenarios and edge cases
- **✅ Test Changes** - Run validation after updates

### **Performance Considerations**
- **📦 File Size** - Keep individual files under 10MB
- **⚡ Loading Speed** - Large datasets should be chunked
- **💾 Memory Usage** - Consider lazy loading for big files

## 📚 **Related Documentation**

- **🔧 Data Models:** See `../models/README.md`
- **🧪 Testing:** See `../tests/README.md`
- **🌊 Workflows:** See `../services/README.md`
- **📖 Configuration:** See project root `config.yml`

---

**💡 Tip:** Start with the existing bike sales data to understand the structure, then create your own datasets following the same patterns!
