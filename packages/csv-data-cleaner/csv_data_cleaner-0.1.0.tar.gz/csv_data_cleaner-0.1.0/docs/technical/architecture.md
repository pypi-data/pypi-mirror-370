# Architecture Overview

Comprehensive technical architecture documentation for CSV Data Cleaner - understanding the system design, components, and data flow.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CSV Data Cleaner                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    CLI      │  │     API     │  │   Library   │         │
│  │  Interface  │  │  Interface  │  │  Interface  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                    Core Engine                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Cleaner   │  │    AI       │  │ Validation  │         │
│  │   Engine    │  │   Agent     │  │   Engine    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                  Library Wrappers                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pandas    │  │  PyJanitor  │  │ Feature     │         │
│  │  Wrapper    │  │  Wrapper    │  │ Engine      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  MissingNo  │  │   Dedupe    │  │   Custom    │         │
│  │  Wrapper    │  │  Wrapper    │  │  Wrappers   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                  External Libraries                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pandas    │  │  PyJanitor  │  │ Feature     │         │
│  │             │  │             │  │ Engine      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  MissingNo  │  │   Dedupe    │  │   OpenAI    │         │
│  │             │  │             │  │  Anthropic  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### 1. Interface Layer

#### CLI Interface (`csv_cleaner/cli/`)
- **Purpose**: Command-line interface for user interactions
- **Key Components**:
  - `main.py`: Entry point and command routing
  - `commands.py`: Command implementations
- **Responsibilities**:
  - Parse command-line arguments
  - Route commands to appropriate handlers
  - Handle user input/output
  - Manage configuration

#### API Interface (Future)
- **Purpose**: RESTful API for programmatic access
- **Key Components**:
  - FastAPI-based web service
  - JSON-based request/response handling
- **Responsibilities**:
  - HTTP request handling
  - Authentication and authorization
  - Rate limiting and monitoring

### 2. Core Engine

#### Cleaner Engine (`csv_cleaner/core/cleaner.py`)
- **Purpose**: Main data processing engine
- **Key Responsibilities**:
  - Coordinate data cleaning operations
  - Manage data flow between components
  - Handle error recovery and logging
  - Optimize performance through parallel processing

#### AI Agent (`csv_cleaner/core/ai_agent.py`)
- **Purpose**: AI-powered data analysis and suggestions
- **Key Responsibilities**:
  - Analyze data quality and structure
  - Generate intelligent cleaning suggestions
  - Execute AI-powered cleaning operations
  - Learn from user feedback

#### Validation Engine (`csv_cleaner/core/validator.py`)
- **Purpose**: Data validation and quality assessment
- **Key Responsibilities**:
  - Schema validation
  - Data quality metrics calculation
  - Anomaly detection
  - Report generation

### 3. Library Management

#### Library Manager (`csv_cleaner/core/library_manager.py`)
- **Purpose**: Manage external library dependencies
- **Key Responsibilities**:
  - Initialize library wrappers
  - Handle library availability checks
  - Manage feature gates for optional libraries
  - Provide unified interface to libraries

#### Wrapper System (`csv_cleaner/wrappers/`)
- **Purpose**: Abstract external library interfaces
- **Key Components**:
  - `pandas_wrapper.py`: Pandas operations wrapper
  - `pyjanitor_wrapper.py`: PyJanitor operations wrapper
  - `feature_engine_wrapper.py`: Feature-engine operations wrapper
  - `missingno_wrapper.py`: MissingNo visualization wrapper
  - `dedupe_wrapper.py`: Dedupe deduplication wrapper

### 4. Configuration Management

#### Configuration System (`csv_cleaner/core/config.py`)
- **Purpose**: Manage application configuration
- **Key Responsibilities**:
  - Load and validate configuration
  - Manage AI provider settings
  - Handle feature flags
  - Store user preferences

#### Feature Gates (`csv_cleaner/feature_gate.py`)
- **Purpose**: Control feature availability
- **Key Responsibilities**:
  - Enable/disable features based on configuration
  - Manage experimental features
  - Control library availability

## 🔄 Data Flow

### 1. Basic Cleaning Flow

```
Input CSV → Validation → Cleaner Engine → Library Wrappers → Output CSV
     ↓           ↓            ↓              ↓              ↓
   File I/O   Quality     Operations    External      File I/O
              Check       Selection     Libraries
```

### 2. AI-Powered Flow

```
Input CSV → AI Analysis → Suggestions → User Review → Execution → Output CSV
     ↓          ↓            ↓            ↓           ↓          ↓
   Data      AI Agent    AI Agent     CLI/API    Cleaner    Results
  Loading    Analysis   Generation   Interface   Engine
```

### 3. Validation Flow

```
Input CSV → Schema Check → Quality Metrics → Anomaly Detection → Report
     ↓           ↓              ↓               ↓              ↓
   Loading    Validation    Calculation     Detection      Generation
```

## 🏛️ Design Patterns

### 1. Wrapper Pattern
- **Purpose**: Abstract external library interfaces
- **Implementation**: Each external library has a wrapper class
- **Benefits**:
  - Consistent interface across libraries
  - Easy to add new libraries
  - Graceful handling of missing dependencies
- **Current Wrappers**:
  - `PandasWrapper`: 9 basic operations (remove_duplicates, fill_missing, etc.)
  - `PyJanitorWrapper`: 8 advanced operations (clean_names, remove_empty, etc.)
  - `FeatureEngineWrapper`: 6 feature engineering operations (advanced_imputation, etc.)
  - `MissingnoWrapper`: 5 visualization operations (missing_matrix, etc.)
  - `DedupeWrapper`: 1 ML-based deduplication operation

### 2. Strategy Pattern
- **Purpose**: Select cleaning operations dynamically
- **Implementation**: Different cleaning strategies for different data types
- **Benefits**:
  - Flexible operation selection
  - Easy to extend with new operations
  - Testable individual strategies

### 3. Factory Pattern
- **Purpose**: Create appropriate wrapper instances
- **Implementation**: Library manager creates wrappers based on availability
- **Benefits**:
  - Centralized object creation
  - Easy to manage dependencies
  - Consistent initialization

### 4. Observer Pattern
- **Purpose**: Monitor cleaning progress and performance
- **Implementation**: Progress callbacks and performance monitoring
- **Benefits**:
  - Real-time progress updates
  - Performance optimization
  - User feedback

## 🔧 Technical Implementation

### 1. Error Handling

#### Exception Hierarchy
```python
class CSVCleanerError(Exception):
    """Base exception for CSV Cleaner"""
    pass

class ValidationError(CSVCleanerError):
    """Data validation errors"""
    pass

class AIError(CSVCleanerError):
    """AI-related errors"""
    pass

class LibraryError(CSVCleanerError):
    """External library errors"""
    pass
```

#### Error Recovery
- **Graceful Degradation**: Continue processing when possible
- **Fallback Mechanisms**: Use alternative methods when primary fails
- **Detailed Logging**: Comprehensive error logging for debugging

### 2. Performance Optimization

#### Parallel Processing
```python
# Parallel operation execution
with ParallelProcessor(max_workers=4) as processor:
    results = processor.map(clean_operation, data_chunks)
```

#### Memory Management
```python
# Chunked processing for large files
for chunk in pd.read_csv(file, chunksize=10000):
    process_chunk(chunk)
```

#### Caching
```python
# Cache expensive operations
@lru_cache(maxsize=128)
def expensive_operation(data_hash):
    return compute_expensive_result(data_hash)
```

### 3. Configuration Management

#### Configuration Sources
1. **Default Configuration**: Built-in sensible defaults
2. **User Configuration**: User-specific settings
3. **Environment Variables**: System-level configuration
4. **Command Line**: Runtime configuration

#### Configuration Validation
```python
# Validate configuration on load
def validate_config(config):
    required_fields = ['ai_provider', 'default_operations']
    for field in required_fields:
        if field not in config:
            raise ConfigurationError(f"Missing required field: {field}")
```

## 🔒 Security Considerations

### 1. Data Privacy
- **Local Processing**: Sensitive data processed locally when possible
- **Data Anonymization**: Optional data anonymization for AI analysis
- **Secure Storage**: Encrypted storage of configuration and API keys

### 2. API Security
- **API Key Management**: Secure storage and rotation of API keys
- **Rate Limiting**: Prevent abuse of external APIs
- **Input Validation**: Validate all user inputs

### 3. Audit Logging
- **Operation Logging**: Log all data processing operations
- **Access Logging**: Track who accessed what data
- **Error Logging**: Comprehensive error logging for security analysis

## 📊 Performance Characteristics

### 1. Scalability
- **Horizontal Scaling**: Parallel processing across multiple cores
- **Vertical Scaling**: Memory and CPU optimization
- **Chunked Processing**: Handle files larger than available memory

### 2. Performance Metrics
- **Processing Speed**: Operations per second
- **Memory Usage**: Peak memory consumption
- **I/O Efficiency**: File read/write performance
- **AI Response Time**: Time for AI operations

### 3. Optimization Strategies
- **Lazy Loading**: Load data only when needed
- **Batch Processing**: Process multiple operations together
- **Caching**: Cache expensive computations
- **Compression**: Compress intermediate data

## 🔄 Integration Points

### 1. External Libraries
- **Pandas**: Core data manipulation (9 operations)
- **PyJanitor**: Advanced data cleaning (8 operations)
- **Feature-engine**: Feature engineering (6 operations)
- **MissingNo**: Missing data visualization (5 operations)
- **Dedupe**: ML-based deduplication (1 operation)

### 2. AI Providers
- **OpenAI**: GPT models for analysis and suggestions
- **Anthropic**: Claude models for analysis and suggestions
- **Local Models**: Ollama-based local models

### 3. Data Sources/Sinks
- **File Systems**: Local CSV file access
- **Databases**: Not currently supported
- **Cloud Storage**: Not currently supported
- **APIs**: Not currently supported

## 🧪 Testing Strategy

### 1. Unit Testing
- **Component Testing**: Test individual components in isolation
- **Mock Testing**: Mock external dependencies
- **Edge Case Testing**: Test boundary conditions

### 2. Integration Testing
- **End-to-End Testing**: Test complete workflows
- **Performance Testing**: Test performance under load
- **Compatibility Testing**: Test with different data formats

### 3. AI Testing
- **Suggestion Testing**: Test AI suggestion quality
- **Execution Testing**: Test AI execution accuracy
- **Learning Testing**: Test AI learning capabilities

## 🚀 Deployment Architecture

### 1. Local Deployment
- **Single Machine**: All components on one machine
- **Virtual Environment**: Isolated Python environment
- **Configuration**: Local configuration files

### 2. Container Deployment (Future)
- **Docker**: Containerized deployment (planned)
- **Kubernetes**: Orchestrated deployment (planned)
- **Microservices**: Service-based architecture (planned)

### 3. Cloud Deployment (Future)
- **Serverless**: Function-based deployment (planned)
- **Container Services**: Managed container services (planned)
- **Hybrid**: Combination of local and cloud components (planned)

## 📈 Monitoring and Observability

### 1. Logging
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Rotation**: Automatic log file management

### 2. Metrics
- **Performance Metrics**: Processing time, memory usage
- **Business Metrics**: Operations performed, data processed
- **Error Metrics**: Error rates, failure patterns

### 3. Tracing
- **Operation Tracing**: Track individual operations
- **Performance Tracing**: Identify bottlenecks
- **Error Tracing**: Trace error propagation

## 🔮 Future Architecture

### 1. Planned Enhancements
- **Microservices**: Break into smaller, focused services
- **Event-Driven**: Event-based architecture for scalability
- **Real-time Processing**: Stream processing capabilities

### 2. Integration Roadmap
- **Database Integration**: Direct database connections
- **Cloud Integration**: Native cloud service integration
- **API Ecosystem**: Comprehensive API for integrations

### 3. AI Enhancements
- **Custom Models**: Support for custom AI models
- **Federated Learning**: Distributed AI learning
- **Real-time AI**: Real-time AI processing

---

*For implementation details, see the [API Reference](api-reference.md) and [Development Guide](../development/developer-guide.md).*
