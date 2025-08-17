# AI Features Guide

Complete guide to CSV Data Cleaner's AI-powered features - from setup to advanced usage patterns.

## 🤖 Overview

**Note**: AI features are available in both Basic and Pro versions. Basic version includes core AI functionality with upgrade prompts for advanced features. Pro version offers enhanced AI capabilities and priority support.

CSV Cleaner's AI features provide intelligent, automated data cleaning capabilities that learn from your data and improve over time. The AI system can analyze your data, suggest cleaning operations, and even execute them automatically.

### Key AI Capabilities
- **Intelligent Data Analysis**: AI analyzes your data structure and quality
- **Smart Suggestions**: Get context-aware cleaning recommendations
- **Automatic Execution**: Execute AI suggestions with confidence
- **Learning System**: AI learns from your feedback to improve suggestions
- **Multi-Provider Support**: OpenAI, Anthropic, and local LLM support

## 🚀 Getting Started with AI

### 1. Setup AI Provider

#### OpenAI (Recommended for Beginners)
```bash
# Configure OpenAI
csv-cleaner ai-configure set --provider openai --api-key YOUR_OPENAI_API_KEY

# Verify configuration
csv-cleaner ai-configure validate
```

#### Anthropic Claude
```bash
# Configure Anthropic
csv-cleaner ai-configure set --provider anthropic --api-key YOUR_ANTHROPIC_API_KEY

# Verify configuration
csv-cleaner ai-configure validate
```

#### Local Models (Advanced)
```bash
# Configure local model (requires Ollama)
csv-cleaner ai-configure set --provider local --model llama3.1:8b

# Verify local setup
csv-cleaner ai-configure validate
```

### 2. Test AI Connection
```bash
# Test AI provider connection
csv-cleaner ai-configure test

# Test with sample data
csv-cleaner ai-suggest sample.csv --test
```

## 🧠 AI-Powered Data Analysis

### Basic Analysis
```bash
# Get comprehensive data analysis
csv-cleaner ai-analyze input.csv

# Save analysis to file
csv-cleaner ai-analyze input.csv --output analysis.json

# Get analysis in specific format
csv-cleaner ai-analyze input.csv --format markdown
```

### Focused Analysis
```bash
# Focus on data quality issues
csv-cleaner ai-analyze input.csv --focus "data_quality"

# Focus on outliers and anomalies
csv-cleaner ai-analyze input.csv --focus "outliers"

# Focus on data patterns
csv-cleaner ai-analyze input.csv --focus "patterns"

# Multiple focus areas
csv-cleaner ai-analyze input.csv --focus "data_quality,outliers,patterns"
```

### Analysis Output Examples

#### Data Quality Analysis
```json
{
  "data_quality": {
    "missing_values": {
      "total_missing": 150,
      "missing_percentage": 2.5,
      "columns_with_missing": ["email", "phone", "address"]
    },
    "duplicates": {
      "total_duplicates": 25,
      "duplicate_percentage": 0.4
    },
    "data_types": {
      "issues": ["date_column_has_strings", "numeric_column_has_text"]
    }
  }
}
```

#### Outlier Analysis
```json
{
  "outliers": {
    "numerical_columns": {
      "age": {
        "outliers_count": 12,
        "outlier_percentage": 0.2,
        "outlier_range": [120, 150]
      },
      "salary": {
        "outliers_count": 8,
        "outlier_percentage": 0.1,
        "outlier_range": [500000, 1000000]
      }
    }
  }
}
```

## 💡 AI-Powered Suggestions

### Get Cleaning Suggestions
```bash
# Get AI suggestions for data cleaning
csv-cleaner ai-suggest input.csv

# Save suggestions to file
csv-cleaner ai-suggest input.csv --output suggestions.json

# Get suggestions with specific focus
csv-cleaner ai-suggest input.csv --focus "data_quality"
```

### Suggestion Types

#### Data Quality Suggestions
```bash
# Focus on data quality improvements
csv-cleaner ai-suggest input.csv --focus "data_quality"

# Examples of suggestions:
# - Remove duplicate rows (25 duplicates found)
# - Fill missing values in email column (50 missing)
# - Standardize phone number format
# - Fix date format inconsistencies
```

#### Outlier Handling Suggestions
```bash
# Focus on outlier management
csv-cleaner ai-suggest input.csv --focus "outliers"

# Examples of suggestions:
# - Cap age values at 100 (12 outliers detected)
# - Remove salary outliers above 95th percentile
# - Flag suspicious data points for review
```

#### Data Type Suggestions
```bash
# Focus on data type improvements
csv-cleaner ai-suggest input.csv --focus "data_types"

# Examples of suggestions:
# - Convert date strings to datetime objects
# - Convert numeric strings to integers/floats
# - Standardize categorical variables
```

### Suggestion Output Format
```json
{
  "suggestions": [
    {
      "id": "suggestion_001",
      "type": "remove_duplicates",
      "description": "Remove 25 duplicate rows found in the dataset",
      "confidence": 0.95,
      "impact": "high",
      "operations": [
        {
          "operation": "remove_duplicates",
          "parameters": {
            "subset": null,
            "keep": "first"
          }
        }
      ]
    },
    {
      "id": "suggestion_002",
      "type": "fill_missing",
      "description": "Fill missing values in email column (50 missing values)",
      "confidence": 0.88,
      "impact": "medium",
      "operations": [
        {
          "operation": "fill_missing",
          "parameters": {
            "columns": ["email"],
            "method": "drop",
            "reason": "Email is required field"
          }
        }
      ]
    }
  ]
}
```

## 🤖 AI-Powered Automatic Cleaning

### Execute AI Suggestions
```bash
# Execute all AI suggestions automatically
csv-cleaner ai-clean input.csv output.csv

# Preview execution plan without modifying files
csv-cleaner ai-clean input.csv output.csv --dry-run

# Auto-confirm all suggestions
csv-cleaner ai-clean input.csv output.csv --auto-confirm
```

### Selective Execution
```bash
# Execute only high-confidence suggestions
csv-cleaner ai-clean input.csv output.csv --min-confidence 0.8

# Execute only specific suggestion types
csv-cleaner ai-clean input.csv output.csv --suggestion-types "remove_duplicates,fill_missing"

# Limit number of suggestions to execute
csv-cleaner ai-clean input.csv output.csv --max-suggestions 5
```

### Interactive Execution
```bash
# Interactive mode - confirm each suggestion
csv-cleaner ai-clean input.csv output.csv --interactive

# Interactive with custom prompts
csv-cleaner ai-clean input.csv output.csv --interactive --prompt-style "detailed"
```

### Execution Modes

#### Safe Mode (Default)
```bash
# Safe mode - creates backup before execution
csv-cleaner ai-clean input.csv output.csv --safe-mode

# Backup options
csv-cleaner ai-clean input.csv output.csv --backup-dir "./backups"
```

#### Aggressive Mode
```bash
# Aggressive mode - executes all suggestions
csv-cleaner ai-clean input.csv output.csv --aggressive

# With high confidence threshold
csv-cleaner ai-clean input.csv output.csv --aggressive --min-confidence 0.9
```

#### Conservative Mode
```bash
# Conservative mode - only high-impact, high-confidence suggestions
csv-cleaner ai-clean input.csv output.csv --conservative

# With manual confirmation for each
csv-cleaner ai-clean input.csv output.csv --conservative --interactive
```

## 🎯 Advanced AI Features

### Custom AI Prompts
```bash
# Use custom prompt for analysis
csv-cleaner ai-analyze input.csv --custom-prompt "Focus on data quality issues specific to e-commerce data"

# Use custom prompt for suggestions
csv-cleaner ai-suggest input.csv --custom-prompt "Prioritize suggestions that improve data accuracy for machine learning"
```

### AI Model Selection
```bash
# Use specific model for analysis
csv-cleaner ai-analyze input.csv --model "gpt-4"

# Use different models for different tasks
csv-cleaner ai-suggest input.csv --model "claude-3-5-sonnet-20241022"
```

### Batch AI Processing
```bash
# Process multiple files with AI
csv-cleaner batch-ai-clean "*.csv" --operations "ai-suggest,ai-clean"

# Batch with custom configuration
csv-cleaner batch-ai-clean --config batch_ai_config.json
```

### AI Learning and Feedback

#### Provide Feedback
```bash
# Rate AI suggestions
csv-cleaner ai-feedback --suggestion-id "suggestion_001" --rating 5 --comment "Great suggestion!"

# Provide detailed feedback
csv-cleaner ai-feedback --suggestion-id "suggestion_002" --rating 2 --comment "This would break my data"
```

#### View AI Learning History
```bash
# View feedback history
csv-cleaner ai-feedback --history

# Export learning data
csv-cleaner ai-feedback --export learning_data.json
```

## ⚙️ AI Configuration

### Provider Configuration
```bash
# Show current AI configuration
csv-cleaner ai-configure show

# Set default provider
csv-cleaner ai-configure set --default-provider openai

# Configure multiple providers
csv-cleaner ai-configure set --provider openai --api-key KEY1
csv-cleaner ai-configure set --provider anthropic --api-key KEY2
```

### Model Configuration
```bash
# Set default model
csv-cleaner ai-configure set --default-model "gpt-4o-mini"

# Configure model parameters
csv-cleaner ai-configure set --model-params "temperature=0.3,max_tokens=2000"

# Set cost limits
csv-cleaner ai-configure set --cost-limit 10.0
```

### Advanced Configuration
```bash
# Set retry policy
csv-cleaner ai-configure set --retry-policy "exponential_backoff"

# Set timeout settings
csv-cleaner ai-configure set --timeout 30

# Configure fallback behavior
csv-cleaner ai-configure set --fallback-provider anthropic
```

## 📊 AI Performance Monitoring

### Monitor AI Usage
```bash
# Show AI usage statistics
csv-cleaner ai-stats

# Show cost breakdown
csv-cleaner ai-stats --costs

# Export usage report
csv-cleaner ai-stats --export usage_report.json
```

### Performance Metrics
```bash
# Monitor AI response times
csv-cleaner ai-stats --response-times

# Monitor suggestion accuracy
csv-cleaner ai-stats --accuracy

# Monitor cost efficiency
csv-cleaner ai-stats --cost-efficiency
```

## 🔒 AI Security and Privacy

### Data Privacy
```bash
# Enable data anonymization
csv-cleaner ai-analyze input.csv --anonymize

# Use local processing only
csv-cleaner ai-configure set --privacy-mode local

# Set data retention policy
csv-cleaner ai-configure set --data-retention 7
```

### Security Settings
```bash
# Enable encryption for AI communications
csv-cleaner ai-configure set --encrypt-communications

# Set API key rotation policy
csv-cleaner ai-configure set --key-rotation 30

# Enable audit logging
csv-cleaner ai-configure set --audit-logging
```

## 🆘 AI Troubleshooting

### Common AI Issues

#### Connection Issues
```bash
# Test AI provider connection
csv-cleaner ai-configure test

# Check API key validity
csv-cleaner ai-configure validate

# Test with different provider
csv-cleaner ai-configure test --provider anthropic
```

#### Performance Issues
```bash
# Check AI response times
csv-cleaner ai-stats --response-times

# Optimize model selection
csv-cleaner ai-configure set --default-model "gpt-4o-mini"

# Enable caching
csv-cleaner ai-configure set --enable-caching
```

#### Cost Issues
```bash
# Monitor costs
csv-cleaner ai-stats --costs

# Set cost limits
csv-cleaner ai-configure set --cost-limit 5.0

# Use cheaper models
csv-cleaner ai-configure set --default-model "gpt-3.5-turbo"
```

### Debug AI Operations
```bash
# Enable debug mode
csv-cleaner ai-analyze input.csv --debug

# Show detailed AI logs
csv-cleaner ai-analyze input.csv --verbose

# Export debug information
csv-cleaner ai-analyze input.csv --debug --export debug_info.json
```

## 📚 Best Practices

### AI Usage Best Practices
1. **Start Small**: Begin with basic analysis before complex cleaning
2. **Review Suggestions**: Always review AI suggestions before execution
3. **Provide Feedback**: Help AI learn by providing feedback on suggestions
4. **Monitor Costs**: Keep track of AI usage costs
5. **Use Appropriate Models**: Choose models based on task complexity

### Performance Optimization
1. **Use Caching**: Enable caching for repeated operations
2. **Batch Operations**: Process multiple files together
3. **Optimize Prompts**: Use clear, specific prompts for better results
4. **Monitor Usage**: Track AI usage patterns and optimize accordingly

### Security Best Practices
1. **Secure API Keys**: Store API keys securely
2. **Data Anonymization**: Anonymize sensitive data before AI analysis
3. **Audit Logging**: Enable audit logging for compliance
4. **Regular Updates**: Keep AI models and configurations updated

## 🚀 Next Steps

1. **Try [AI Tutorials](../tutorials/ai-tutorials.md)** for practical examples
2. **Check [CLI Reference](cli-reference.md)** for complete AI command documentation
3. **Read [Performance Guide](../technical/performance.md)** for AI optimization tips
4. **Explore [Advanced Tutorials](../tutorials/advanced-tutorials.md)** for complex AI workflows

---

*For technical details about AI implementation, see the [Architecture Overview](../technical/architecture.md) and [API Reference](../technical/api-reference.md).*
