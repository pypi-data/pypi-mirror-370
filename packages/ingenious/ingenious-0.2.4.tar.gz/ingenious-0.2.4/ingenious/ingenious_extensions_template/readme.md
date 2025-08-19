# Insight Ingenious Extensions Template

Welcome to your **Insight Ingenious** project! This template provides everything you need to build, customize, and deploy AI-powered multi-agent conversation workflows.

## 🚀 **Quick Start**

### **1. Initial Setup**
After running `uv run ingen init`, you should have:
- ✅ `.env.example` - Environment variables template for pydantic-settings configuration
- ✅ This project structure with sample workflows

**Configuration Steps:**
1. Copy the environment template: `cp .env.example .env`
2. Edit `.env` with your API keys and configuration
3. Validate your setup: `ingen validate`

### **2. Test the Built-in Bike Insights Workflow**

The template includes a complete **bike sales analysis workflow** that you can test immediately:

```bash
# 1. Start the server (make sure you've configured .env first)
uv run ingen serve

# 2. Test the bike insights workflow
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Analyze bike sales trends for April 2023",
    "conversation_flow": "bike-insights"
  }'
```

**Requirements:** Your `.env` file must have the required `INGENIOUS_MODELS__0__*` configuration for the AI model to work.

## 📁 **Project Structure**

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| **📁 models/** | Custom data models | `bikes.py` - Sample bike sales models |
| **📁 sample_data/** | Test data files | `bike_sales_april_2023.json` - Sample dataset |
| **📁 services/** | Multi-agent workflows | `bike_insights/` - Complete workflow example |
| **📁 templates/** | Agent prompts | `bike_lookup_agent_prompt.jinja` - Sample prompt |
| **📁 tests/** | Test harness | `run_tests.py` - Automated testing |
| **📁 api/** | Custom API routes | Add your own REST endpoints |

## 🧠 **Understanding the Bike-Insights Workflow**

This sample workflow demonstrates a complete multi-agent system:

### **Agents Involved:**
- **📊 Customer Sentiment Agent** - Analyzes customer reviews and ratings
- **💰 Fiscal Analysis Agent** - Processes sales data and trends
- **🔍 Bike Lookup Agent** - Retrieves product information using tools
- **📝 Summary Agent** - Generates comprehensive reports
- **🤖 User Proxy** - Orchestrates agent interactions

### **Data Flow:**
1. **Input:** JSON payload with bike sales data
2. **Processing:** Multiple agents analyze different aspects simultaneously
3. **Tools:** Bike price lookup function for real-time data
4. **Output:** Comprehensive analysis report with insights and recommendations

### **Sample Input Data Structure:**
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
          "customer_review": {
            "rating": 4.0,
            "comment": "Great bike for commuting!"
          }
        }
      ],
      "bike_stock": [...]
    }
  ]
}
```

## 🛠️ **Customizing the Workflow**

### **Modify the Bike Insights Workflow:**

1. **📝 Update Prompts:** Edit files in `templates/prompts/`
   - `customer_sentiment_agent_prompt.jinja` - Change how reviews are analyzed
   - `fiscal_analysis_agent_prompt.jinja` - Modify sales analysis approach
   - `summary_prompt.jinja` - Customize final report format

2. **🔧 Add New Agents:**
   - Create new prompt files in `templates/prompts/`
   - Register them in `services/chat_services/multi_agent/conversation_flows/bike_insights/bike_insights.py`

3. **📊 Modify Data Models:**
   - Edit `models/bikes.py` to change data structure
   - Update sample data in `sample_data/bike_sales_april_2023.json`

### **Create Your Own Workflow:**

1. **Copy the bike-insights structure:**
   ```bash
   # Note: Directory name uses underscores (bike_insights) but API uses hyphens (bike-insights)
   cp -r services/chat_services/multi_agent/conversation_flows/bike_insights \
         services/chat_services/multi_agent/conversation_flows/your_workflow
   ```

2. **Update the conversation flow file:**
   - Rename the class and methods
   - Modify agent registration and tools
   - Update data processing logic

3. **Create custom data models in `models/` folder**

4. **Add sample data to `sample_data/` folder**

## 🧪 **Testing Your Workflows**

### **Run Tests:**
```bash
# Run the built-in test harness
cd tests
python run_tests.py
```

### **Test Individual Components:**
```bash
# Test data model validation
python -c "
from models.bikes import RootModel
import json
with open('sample_data/bike_sales_april_2023.json') as f:
    data = json.load(f)
    model = RootModel(**data)
    print('✅ Data model validation passed')
"
```

## 🌐 **Web Interface**

Access your workflows through the web interface:

- **💬 Chat Interface:** http://localhost:80/chainlit
- **🔧 Prompt Tuner:** http://localhost:80/prompt-tuner
- **📖 API Documentation:** http://localhost:80/docs

## 📚 **Next Steps**

### **🎯 Learn More:**
- [📖 Configuration Guide](../docs/getting-started/configuration.md) - Environment variable setup
- [🔌 Extensions Guide](../docs/extensions/README.md) - Advanced customization
- [🌐 API Integration](../docs/guides/api-integration.md) - REST API usage

### **📝 Configuration Migration:**
If you have existing YAML configuration files (`config.yml`, `profiles.yml`) from an older version:
```bash
# Migrate your existing configuration
uv run python scripts/migrate_config.py --yaml-file config.yml --output .env
uv run python scripts/migrate_config.py --yaml-file profiles.yml --output .env --append
```

### **🚀 Advanced Features:**
- **🔍 Knowledge Base Search** - Add Azure Cognitive Search integration
- **📊 Database Queries** - Connect to SQL databases
- **📄 Document Processing** - Analyze PDFs and documents

### **💡 Example Projects to Build:**
- **📈 Financial Analysis** - Stock/crypto analysis workflows
- **🏥 Healthcare Insights** - Patient data analysis
- **🛒 E-commerce Analytics** - Customer behavior analysis
- **📱 Social Media Monitoring** - Sentiment tracking workflows

## 🆘 **Need Help?**

- **📋 Workflow Requirements:** Check `uv run ingen workflows`
- **✅ Configuration Validation:** Run `uv run ingen validate`
- **🔧 Configuration Issues:** See [Troubleshooting Guide](../docs/troubleshooting/README.md)
- **💻 Development:** Review [Development Guide](../docs/development/README.md)
- **🐛 Issues:** Check the [GitHub Issues](https://github.com/Insight-Services-APAC/ingenious/issues)

---

**🎉 Happy Building!** You now have a powerful foundation for creating AI-powered multi-agent workflows. Start by exploring the bike insights example, then customize it for your specific use case.
