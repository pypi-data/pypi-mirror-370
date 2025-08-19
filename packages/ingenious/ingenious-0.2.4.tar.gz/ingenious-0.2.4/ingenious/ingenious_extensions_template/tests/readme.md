# Test Harness & Quality Assurance

This directory contains testing infrastructure for validating your AI workflows, prompts, and agent responses.

## 🎯 **Purpose**

The test harness enables:
- **🤖 Automated Testing** - Run workflows with sample data automatically
- **📊 Response Validation** - Check AI output quality and consistency
- **🔄 Regression Testing** - Ensure changes don't break existing functionality
- **📈 Performance Monitoring** - Track response times and token usage
- **🎛️ Prompt Tuning** - A/B test different prompt variations

## 🚀 **Quick Start**

### **Run Tests Immediately**
```bash
# Run the bike insights workflow test
cd tests
python run_tests.py

# Run batch tests with specific events
python run_tests_flat.py
```

### **Expected Output**
```
🧪 Running test for bike-insights workflow...
📊 Processing bike sales data for April 2023...
✅ Test completed successfully
📄 Results saved to functional_test_outputs/
```

## 📁 **Test Files Explained**

### **🐍 `run_tests.py` - Main Test Runner**
Comprehensive test execution with full workflow simulation:

```python
class RunBatches:
    async def run(self):
        # 1. Generate unique test thread ID
        thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # 2. Create realistic test payload
        test_payload = {
            "revision_id": "test_revision_001",
            "identifier": str(uuid.uuid4()),
            "stores": [...]  # Sample bike sales data
        }

        # 3. Execute chat service with bike-insights workflow
        chat_request = ChatRequest(
            thread_id=thread_id,
            user_prompt=json.dumps(test_payload),
            conversation_flow="bike-insights"
        )

        # 4. Get response and save results
        response = await chat_service.get_chat_response(chat_request)

        # 5. Generate test report
        self.save_test_output(response, thread_id)
```

### **⚡ `run_tests_flat.py` - Simplified Test Runner**
Lightweight testing for quick validation:

```python
# Direct API call without full framework setup
test_payload = {
    "revision_id": "test_revision_001",
    "identifier": str(uuid.uuid4()),
    "stores": [...]  # Minimal test data
}

# Execute workflow directly
response = await chat_service.get_chat_response(chat_request)
print(f"✅ Response: {response.response_text}")
```

## 🧪 **Creating Custom Tests**

### **1. Test Structure Template**
```python
#!/usr/bin/env python3
"""Test runner for [YOUR_WORKFLOW] workflow"""

import asyncio
import json
import uuid
from datetime import datetime

async def test_your_workflow():
    # Prepare test data
    test_data = {
        "revision_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "identifier": str(uuid.uuid4()),
        # Your domain-specific data here
        "your_data": {...}
    }

    # Create chat request
    chat_request = ChatRequest(
        thread_id=f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        user_prompt=json.dumps(test_data),
        conversation_flow="your_workflow_name"
    )

    # Execute and validate
    response = await chat_service.get_chat_response(chat_request)

    # Assertions
    assert response.response_text is not None
    assert len(response.response_text) > 100  # Meaningful response
    assert "error" not in response.response_text.lower()

    print(f"✅ Test passed: {chat_request.conversation_flow}")
    return response

if __name__ == "__main__":
    asyncio.run(test_your_workflow())
```

### **2. Data-Driven Testing**
```python
class TestDataManager:
    """Manage multiple test scenarios"""

    def get_test_scenarios(self):
        return [
            {
                "name": "high_sales_scenario",
                "description": "Test with high-volume sales data",
                "data": self.generate_high_sales_data(),
                "expected_keywords": ["growth", "success", "revenue"]
            },
            {
                "name": "low_rating_scenario",
                "description": "Test with poor customer reviews",
                "data": self.generate_low_rating_data(),
                "expected_keywords": ["concern", "improvement", "issue"]
            },
            {
                "name": "seasonal_scenario",
                "description": "Test with seasonal trends",
                "data": self.generate_seasonal_data(),
                "expected_keywords": ["seasonal", "trend", "pattern"]
            }
        ]

    def validate_response(self, response: str, expected_keywords: List[str]) -> bool:
        """Check if response contains expected analysis"""
        response_lower = response.lower()
        found_keywords = [kw for kw in expected_keywords if kw in response_lower]
        return len(found_keywords) >= len(expected_keywords) * 0.7  # 70% match
```

### **3. Performance Testing**
```python
import time
from typing import Dict, Any

class PerformanceMonitor:
    """Monitor workflow performance metrics"""

    async def run_performance_test(self, workflow_name: str, iterations: int = 5):
        results = {
            "workflow": workflow_name,
            "iterations": iterations,
            "response_times": [],
            "token_usage": [],
            "success_rate": 0
        }

        successful_runs = 0

        for i in range(iterations):
            start_time = time.time()

            try:
                response = await self.execute_workflow(workflow_name)
                end_time = time.time()

                # Record metrics
                response_time = end_time - start_time
                results["response_times"].append(response_time)

                # Extract token usage if available
                if hasattr(response, 'token_count'):
                    results["token_usage"].append(response.token_count)

                successful_runs += 1
                print(f"✅ Run {i+1}: {response_time:.2f}s")

            except Exception as e:
                print(f"❌ Run {i+1} failed: {e}")

        # Calculate success rate
        results["success_rate"] = successful_runs / iterations
        results["avg_response_time"] = sum(results["response_times"]) / len(results["response_times"])

        return results
```

## 📊 **Test Output Analysis**

### **Understanding Test Results**
```markdown
# Test Batch Results

## Configuration
- **Workflow:** bike-insights
- **Thread ID:** 20241204123045
- **Test Data:** bike_sales_april_2023.json

## Response Analysis
- **Response Length:** 2,847 characters
- **Processing Time:** 12.3 seconds
- **Token Usage:** 1,234 tokens
- **Agents Involved:** customer_sentiment_agent, fiscal_analysis_agent, summary

## Quality Checks
✅ Contains sales analysis
✅ Includes customer sentiment summary
✅ Provides actionable recommendations
⚠️  Could include more specific metrics

## Agent Responses
### Customer Sentiment Agent
- Positive sentiment: 67%
- Negative sentiment: 18%
- Neutral sentiment: 15%

### Fiscal Analysis Agent
- Total revenue: $2.4M
- Top product: Giant Defy Road Bike
- Best location: Sydney CBD

## Recommendations
1. Focus marketing on high-performing products
2. Address comfort concerns mentioned in reviews
3. Expand successful Sydney model to other cities
```

### **Automated Quality Scoring**
```python
class ResponseQualityEvaluator:
    """Evaluate AI response quality automatically"""

    def score_response(self, response: str, workflow: str) -> Dict[str, Any]:
        scores = {
            "completeness": 0,
            "relevance": 0,
            "actionability": 0,
            "clarity": 0,
            "overall": 0
        }

        # Check completeness (did it address all key areas?)
        if workflow == "bike-insights":
            required_sections = ["sales", "sentiment", "recommendations"]
            found_sections = sum(1 for section in required_sections
                               if section in response.lower())
            scores["completeness"] = found_sections / len(required_sections)

        # Check for specific insights vs generic responses
        specific_indicators = ["$", "%", "increased", "decreased", "specific product names"]
        specificity = sum(1 for indicator in specific_indicators
                         if indicator in response.lower())
        scores["relevance"] = min(specificity / 3, 1.0)  # Cap at 1.0

        # Check for actionable recommendations
        action_words = ["recommend", "suggest", "should", "could", "improve"]
        actionability = sum(1 for word in action_words
                          if word in response.lower())
        scores["actionability"] = min(actionability / 3, 1.0)

        # Overall score
        scores["overall"] = sum(scores.values()) / len(scores) * 100

        return scores
```

## 🔄 **Integration with Prompt Tuner**

### **A/B Testing Prompts**
```python
class PromptTester:
    """Test different prompt variations"""

    async def compare_prompts(self, base_prompt: str, variations: List[str], test_data: dict):
        results = []

        for i, variation in enumerate([base_prompt] + variations):
            # Update prompt in system
            await self.update_agent_prompt("summary", variation)

            # Run test
            response = await self.run_test_with_data(test_data)

            # Evaluate
            quality_score = self.evaluate_response(response)

            results.append({
                "prompt_id": f"variation_{i}",
                "prompt": variation[:100] + "..." if len(variation) > 100 else variation,
                "quality_score": quality_score,
                "response_length": len(response),
                "response": response
            })

        # Find best performing prompt
        best_prompt = max(results, key=lambda x: x["quality_score"])

        return {
            "best_prompt": best_prompt,
            "all_results": results,
            "improvement": best_prompt["quality_score"] - results[0]["quality_score"]
        }
```

## 🎛️ **Advanced Testing Features**

### **Regression Testing**
```bash
# Run regression tests against known good outputs
python -m pytest tests/regression/ -v

# Compare current outputs with baseline
python test_regression.py --baseline=outputs/baseline/ --current=outputs/current/
```

### **Load Testing**
```python
async def stress_test_workflow(workflow_name: str, concurrent_requests: int = 10):
    """Test workflow under load"""

    async def single_request():
        return await execute_workflow(workflow_name)

    # Run concurrent requests
    tasks = [single_request() for _ in range(concurrent_requests)]
    start_time = time.time()

    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()

    # Analyze results
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    print(f"📊 Load Test Results:")
    print(f"   Total requests: {concurrent_requests}")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(failed)}")
    print(f"   Total time: {end_time - start_time:.2f}s")
    print(f"   Avg per request: {(end_time - start_time) / concurrent_requests:.2f}s")
```

## 📚 **Related Documentation**

- **🌊 Workflows:** See `../services/README.md` for workflow development
- **📊 Sample Data:** See `../sample_data/README.md` for test data creation
- **🧠 Models:** See `../models/README.md` for data validation
- **📖 Configuration:** See project root for environment setup

---

**💡 Testing Best Practices:**
1. **🔄 Test Early, Test Often** - Run tests after every prompt change
2. **📊 Measure Quality** - Don't just check if it works, check if it works *well*
3. **🎯 Use Real Data** - Test with realistic, varied datasets
4. **📈 Track Trends** - Monitor performance over time
5. **🛡️ Edge Cases** - Test error conditions and unusual inputs
