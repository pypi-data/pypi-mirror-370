# Templates & Prompts

This directory contains **Jinja2 templates** and **AI agent prompts** that define how your AI agents communicate and analyze data.

## 🎯 **Purpose**

Templates serve multiple critical functions:
- **🤖 Agent Prompts** - Define how AI agents analyze and respond to data
- **📄 HTML Templates** - Custom web interface components (if needed)
- **📊 Report Templates** - Structured output formats for AI responses
- **🔄 Dynamic Content** - Variable substitution in prompts and outputs

## 📁 **Template Structure**

```
templates/
├── prompts/                           # AI Agent Prompts
│   ├── bike_lookup_agent_prompt.jinja    # Product lookup agent
│   ├── customer_sentiment_agent_prompt.jinja # Review analysis
│   ├── fiscal_analysis_agent_prompt.jinja    # Sales analysis
│   └── summary_prompt.jinja              # Final report generation
├── html/                              # Web Interface (optional)
│   ├── custom_dashboard.html             # Custom analytics dashboard
│   └── report_templates.html            # Report layouts
└── reports/                           # Output Format Templates
    ├── sales_report.md.jinja             # Markdown report format
    └── executive_summary.html.jinja      # Executive summary layout
```

## 🤖 **Understanding Agent Prompts**

### **Example: Customer Sentiment Agent**
```jinja
{# templates/prompts/customer_sentiment_agent_prompt.jinja #}

### ROLE
You are a **Customer Experience Analyst** specializing in extracting insights from customer reviews and feedback data.

### OBJECTIVE
Analyze customer reviews for bike sales data and provide:
1. **Sentiment Distribution** - Percentage breakdown (Positive/Negative/Neutral)
2. **Key Themes** - Most common topics in reviews
3. **Pain Points** - Specific issues customers mention
4. **Recommendations** - Actionable steps to improve customer satisfaction

### ANALYSIS APPROACH
- Focus on **specific feedback** rather than general statements
- Identify **recurring patterns** across multiple reviews
- Quantify sentiment where possible (e.g., "67% positive")
- Highlight **actionable insights** for business improvement

### INPUT DATA
The data contains bike sales with customer reviews:
```json
{
  "stores": [...],
  "bike_sales": [
    {
      "customer_review": {
        "rating": 4.2,
        "comment": "Great bike for commuting, but seat could be more comfortable"
      }
    }
  ]
}
```

### OUTPUT FORMAT
Structure your analysis as:

## 🌟 Customer Sentiment Analysis

### Sentiment Distribution
- **Positive:** XX% (ratings 4-5)
- **Neutral:** XX% (rating 3)
- **Negative:** XX% (ratings 1-2)

### 🔍 Key Themes Identified
1. **Product Quality** - [specific mentions]
2. **Comfort & Ergonomics** - [specific feedback]
3. **Value for Money** - [price-related comments]

### ⚠️ Areas for Improvement
- [Specific issue 1] - mentioned in X% of reviews
- [Specific issue 2] - recurring theme across locations

### 🎯 Recommendations
1. **Short-term:** [immediate actions]
2. **Medium-term:** [process improvements]
3. **Long-term:** [strategic changes]

Remember: Focus on **specific, actionable insights** rather than generic observations.
```

### **Example: Fiscal Analysis Agent**
```jinja
{# templates/prompts/fiscal_analysis_agent_prompt.jinja #}

### ROLE
You are a **Business Intelligence Analyst** specializing in retail sales analysis and revenue optimization.

### TASK
Analyze the provided bike sales data and generate insights about:
1. **Sales Performance** - Volume, revenue, trends
2. **Product Analysis** - Best/worst performers
3. **Geographic Insights** - Location-based patterns
4. **Growth Opportunities** - Revenue optimization recommendations

### ANALYTICAL FRAMEWORK
- Calculate **key metrics** (total sales, average order value, etc.)
- Identify **top performers** by various dimensions
- Spot **trends and patterns** in the data
- Provide **data-driven recommendations**

### INPUT PROCESSING
The data will be provided as a structured table. Look for:
- Sales volumes by product and location
- Revenue patterns across time periods
- Product performance variations
- Geographic distribution insights

### OUTPUT STRUCTURE

## 💰 Financial Performance Analysis

### 📊 Key Metrics
- **Total Sales Volume:** [X units]
- **Total Revenue:** $[X]
- **Average Order Value:** $[X]
- **Top Performing Period:** [timeframe]

### 🏆 Product Performance
#### Top Performers
1. **[Product Name]** - [X units, $Y revenue]
2. **[Product Name]** - [X units, $Y revenue]

#### Underperformers
- **[Product Name]** - [reason for low performance]

### 🌍 Geographic Analysis
- **Highest Revenue Location:** [location] - $[amount]
- **Growth Opportunities:** [locations with potential]

### 🚀 Strategic Recommendations
1. **Product Focus:** [which products to emphasize]
2. **Market Expansion:** [geographic opportunities]
3. **Inventory Optimization:** [stock recommendations]

Ensure all insights are **quantified** and **actionable**.
```

## 🛠️ **Customizing Prompts**

### **Best Practices for Prompt Engineering**

```jinja
{# ✅ Good prompt structure #}

### ROLE
[Clear, specific role definition]

### CONTEXT
[Background information the agent needs]

### TASK
[Specific, measurable objectives]

### INPUT FORMAT
[Description of expected data structure]

### OUTPUT FORMAT
[Exact structure you want in response]

### CONSTRAINTS
[Limitations, requirements, style guidelines]

### EXAMPLES
[Sample inputs and expected outputs]
```

### **Variable Substitution**
```jinja
{# Use Jinja2 variables for dynamic content #}

### ANALYSIS PARAMETERS
- **Analysis Date:** {{ analysis_date | default('today') }}
- **Data Source:** {{ data_source | default('unknown') }}
- **Confidence Threshold:** {{ confidence_threshold | default(0.8) }}

{% if include_predictions %}
### PREDICTIVE ANALYSIS
Please include future trend predictions based on historical patterns.
{% endif %}

{% for metric in required_metrics %}
- Analyze {{ metric.name }}: {{ metric.description }}
{% endfor %}
```

### **Conditional Logic**
```jinja
{# Adapt prompts based on data characteristics #}

{% if data_size == "large" %}
### SAMPLING APPROACH
Due to large dataset size, focus on:
- Representative sampling across all stores
- Key trend identification rather than exhaustive analysis
{% else %}
### COMPREHENSIVE ANALYSIS
With this dataset size, provide detailed analysis of:
- Every transaction and review
- Granular patterns and outliers
{% endif %}

{% if analysis_type == "emergency" %}
⚠️ **URGENT ANALYSIS REQUIRED**
Focus on immediate actionable insights only. Skip detailed explanations.
{% endif %}
```

## 📊 **Report Templates**

### **Markdown Report Template**
```jinja
{# templates/reports/executive_summary.md.jinja #}

# 📈 Executive Sales Summary
**Generated:** {{ timestamp }}
**Period:** {{ analysis_period }}
**Analyst:** {{ agent_name }}

## 🎯 Key Findings

{% for finding in key_findings %}
### {{ finding.title }}
{{ finding.description }}

**Impact:** {{ finding.impact }}
**Confidence:** {{ finding.confidence }}%
{% endfor %}

## 📊 Performance Metrics

| Metric | Value | Change | Target |
|--------|-------|--------|--------|
{% for metric in performance_metrics %}
| {{ metric.name }} | {{ metric.value }} | {{ metric.change }} | {{ metric.target }} |
{% endfor %}

## 🚀 Recommendations

{% for rec in recommendations %}
### {{ rec.priority | upper }}: {{ rec.title }}
{{ rec.description }}

**Expected Impact:** {{ rec.impact }}
**Timeline:** {{ rec.timeline }}
**Resources Required:** {{ rec.resources }}
{% endfor %}

---
*Report generated by Insight Ingenious AI Platform*
```

### **HTML Dashboard Template**
```html
<!-- templates/html/analytics_dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ dashboard_title | default('Sales Analytics') }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="dashboard-container">
        <h1>{{ dashboard_title }}</h1>

        <div class="metrics-grid">
            {% for metric in key_metrics %}
            <div class="metric-card">
                <h3>{{ metric.name }}</h3>
                <div class="metric-value">{{ metric.value }}</div>
                <div class="metric-change {{ 'positive' if metric.change > 0 else 'negative' }}">
                    {{ metric.change }}%
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="charts-section">
            {% for chart in charts %}
            <div class="chart-container">
                <h3>{{ chart.title }}</h3>
                <div id="{{ chart.id }}"></div>
                <script>
                    Plotly.newPlot('{{ chart.id }}', {{ chart.data | tojson }}, {{ chart.layout | tojson }});
                </script>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
```

## 🧪 **Testing Your Templates**

### **Template Validation Script**
```python
#!/usr/bin/env python3
"""Validate all template files for syntax and completeness"""

from jinja2 import Environment, FileSystemLoader, TemplateError
from pathlib import Path

def validate_templates():
    """Validate all Jinja2 templates"""
    template_dir = Path(__file__).parent
    env = Environment(loader=FileSystemLoader(template_dir))

    errors = []

    # Test all .jinja files
    for template_file in template_dir.rglob("*.jinja"):
        try:
            template = env.get_template(str(template_file.relative_to(template_dir)))

            # Test with sample data
            sample_data = {
                "analysis_date": "2024-01-15",
                "data_source": "bike_sales_april_2023.json",
                "stores": [{"name": "Test Store", "location": "NSW"}],
                "key_findings": [{"title": "Test Finding", "description": "Test"}]
            }

            rendered = template.render(**sample_data)
            print(f"✅ {template_file.name} - Valid")

        except TemplateError as e:
            error_msg = f"❌ {template_file.name} - Error: {e}"
            print(error_msg)
            errors.append(error_msg)

    return len(errors) == 0

if __name__ == "__main__":
    if validate_templates():
        print("\n🎉 All templates valid!")
    else:
        print("\n⚠️ Some templates have errors. Please fix before deploying.")
```

### **Prompt Testing Framework**
```python
class PromptTester:
    """Test prompt effectiveness with sample data"""

    def test_prompt_quality(self, prompt_name: str, test_data: dict):
        """Test if prompt produces quality responses"""

        # Load and render prompt
        env = Environment(loader=FileSystemLoader('templates/prompts'))
        template = env.get_template(f"{prompt_name}.jinja")
        rendered_prompt = template.render(**test_data)

        # Test criteria
        quality_checks = {
            "has_clear_role": "### ROLE" in rendered_prompt,
            "has_output_format": "### OUTPUT" in rendered_prompt or "##" in rendered_prompt,
            "has_examples": "example" in rendered_prompt.lower() or "sample" in rendered_prompt.lower(),
            "appropriate_length": 200 < len(rendered_prompt) < 2000,
            "no_template_errors": "{{" not in rendered_prompt and "}}" not in rendered_prompt
        }

        # Calculate quality score
        passed_checks = sum(quality_checks.values())
        quality_score = passed_checks / len(quality_checks)

        return {
            "prompt_name": prompt_name,
            "quality_score": quality_score,
            "checks": quality_checks,
            "rendered_length": len(rendered_prompt),
            "suggestions": self.get_improvement_suggestions(quality_checks)
        }

    def get_improvement_suggestions(self, checks: dict) -> List[str]:
        suggestions = []
        if not checks["has_clear_role"]:
            suggestions.append("Add a clear ### ROLE section")
        if not checks["has_output_format"]:
            suggestions.append("Define expected output format")
        if not checks["has_examples"]:
            suggestions.append("Include examples for clarity")
        return suggestions
```

## 🔄 **Prompt Versioning & A/B Testing**

### **Version Management**
```
templates/prompts/
├── customer_sentiment_agent_prompt.jinja          # Current version
├── versions/
│   ├── customer_sentiment_agent_prompt_v1.jinja  # Previous versions
│   ├── customer_sentiment_agent_prompt_v2.jinja
│   └── customer_sentiment_agent_prompt_v3.jinja
└── experiments/
    ├── customer_sentiment_detailed.jinja         # Experimental versions
    └── customer_sentiment_brief.jinja
```

### **A/B Testing Setup**
```python
async def ab_test_prompts(base_prompt: str, variants: List[str], test_data: dict):
    """Compare different prompt versions"""

    results = []

    for i, prompt_version in enumerate([base_prompt] + variants):
        # Run test with this prompt version
        response = await run_agent_with_prompt(prompt_version, test_data)

        # Evaluate response quality
        quality_score = evaluate_response_quality(response)

        results.append({
            "version": f"v{i}",
            "prompt": prompt_version,
            "response": response,
            "quality_score": quality_score,
            "response_length": len(response),
            "key_metrics": extract_metrics(response)
        })

    # Find best performing version
    best_version = max(results, key=lambda x: x["quality_score"])

    return {
        "winner": best_version,
        "all_results": results,
        "improvement": best_version["quality_score"] - results[0]["quality_score"]
    }
```

## 📚 **Related Documentation**

- **🌊 Workflows:** See `../services/README.md` for using templates in workflows
- **🧪 Testing:** See `../tests/README.md` for prompt testing strategies
- **🧠 Models:** See `../models/README.md` for data structure templates
- **📖 Jinja2 Docs:** [https://jinja.palletsprojects.com/](https://jinja.palletsprojects.com/)

---

**💡 Prompt Engineering Tips:**
1. **🎯 Be Specific** - Clear, detailed instructions work better than vague requests
2. **📊 Request Structure** - Ask for formatted output (tables, lists, sections)
3. **🔢 Include Examples** - Show the AI exactly what you want
4. **⚡ Test Iterations** - Small changes can dramatically improve results
5. **📈 Measure Quality** - Use consistent criteria to evaluate prompt effectiveness
