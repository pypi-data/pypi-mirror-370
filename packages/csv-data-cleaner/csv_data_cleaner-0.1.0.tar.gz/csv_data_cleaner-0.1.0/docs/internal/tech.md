# **Technical Specification Document**
## **CSV Data Cleaner - Self-Contained Tool with AI Agent**

---

## **1. System Architecture**

### **1.1 High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    CSV Data Cleaner                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    CLI      │  │ Interactive │  │  Data       │        │
│  │ Interface   │  │    Mode     │  │  Profiler   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Core Engine                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Library     │  │   AI Agent  │  │ Config      │        │
│  │ Wrapper     │  │   Engine    │  │ Manager     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Library Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Pandas    │  │ PyJanitor   │  │ Feature-    │        │
│  │             │  │             │  │ Engine      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Missingno  │  │   Dedupe    │  │  Cleanlab   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   CSV       │  │   Excel     │  │   JSON      │        │
│  │   Files     │  │   Files     │  │   Files     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### **1.2 Core Components**

- **CLI Interface**: Command-line interface using Click/Typer
- **Interactive Mode**: Step-by-step guided interface
- **Library Wrapper**: Unified interface to multiple libraries
- **AI Agent**: Intelligent suggestion and automation engine
- **Data Profiler**: Data quality analysis and reporting
- **Configuration Manager**: Settings and preferences management

---

## **2. Library Integration Strategy**

### **2.1 Core Libraries**

#### **Data Processing**
- **Pandas**: Primary data manipulation and analysis
- **NumPy**: Numerical operations and statistical computations
- **Polars**: High-performance DataFrame library for large datasets

#### **Data Cleaning**
- **PyJanitor**: Fluent API for data cleaning operations
- **Feature-Engine**: Advanced imputation and transformation
- **Dedupe**: Machine learning-based entity resolution
- **Cleanlab**: Automated data quality assessment

#### **Visualization & Analysis**
- **Missingno**: Missing data pattern visualization
- **Matplotlib/Seaborn**: Statistical data visualization
- **Autoviz**: Automated data visualization

#### **Validation & Quality**
- **Great Expectations**: Data quality validation framework
- **Cerberus**: Schema validation
- **Marshmallow**: Data serialization and validation

### **2.1.1 Standardized Library Dependencies**

**Core Dependencies (Required)**:
- **Pandas**: Industry standard for data manipulation
- **NumPy**: Numerical operations and statistical computations
- **PyJanitor**: Fluent API for data cleaning operations

**Advanced Dependencies (Optional)**:
- **Feature-Engine**: Advanced imputation and transformation
- **Dedupe**: Machine learning-based entity resolution
- **Missingno**: Missing data pattern visualization
- **Cleanlab**: Automated data quality assessment

**Performance Dependencies (Optional)**:
- **Polars**: High-performance alternative for large datasets

**AI Dependencies (Optional)**:
- **OpenAI**: GPT models for intelligent suggestions
- **Anthropic**: Claude models for intelligent suggestions
- **Ollama**: Local model support

**Validation Dependencies (Optional)**:
- **Great Expectations**: Data quality validation framework

### **2.2 Library Wrapper Architecture**

```python
class LibraryWrapper:
    """Unified interface to multiple data cleaning libraries"""

    def __init__(self):
        self.libraries = {
            'pandas': PandasWrapper(),
            'pyjanitor': PyJanitorWrapper(),
            'feature_engine': FeatureEngineWrapper(),
            'dedupe': DedupeWrapper(),
            'missingno': MissingnoWrapper(),
            'polars': PolarsWrapper()
        }

    def get_optimal_library(self, task: CleaningTask, data_profile: DataProfile) -> str:
        """Intelligently select the best library for a given task"""
        scores = {}
        for lib_name, wrapper in self.libraries.items():
            score = self.calculate_library_score(lib_name, task, data_profile)
            scores[lib_name] = score
        return max(scores, key=scores.get)

    def execute_cleaning(self, df: pd.DataFrame, options: CleaningOptions) -> pd.DataFrame:
        """Execute cleaning operations using optimal libraries"""
        result_df = df.copy()
        for operation in options.operations:
            optimal_lib = self.get_optimal_library(operation, self.profile_data(result_df))
            result_df = self.libraries[optimal_lib].execute(operation, result_df)
        return result_df
```

---

## **3. AI Integration Design**

### **3.1 AI Agent Architecture**

```python
class AIAgent:
    """AI-powered intelligent cleaning agent"""

    def __init__(self, config: AIConfig):
        self.llm_providers = {
            'openai': OpenAIProvider(config.openai_api_key),
            'anthropic': AnthropicProvider(config.anthropic_api_key),
            'local': LocalProvider(config.local_model_path)
        }
        self.active_provider = self.llm_providers[config.default_provider]
        self.suggestion_cache = SuggestionCache()
        self.learning_engine = LearningEngine()

    def analyze_and_suggest(self, df: pd.DataFrame, profile: DataProfile) -> List[CleaningSuggestion]:
        """Analyze data and generate intelligent cleaning suggestions"""

        # Check cache first
        cache_key = self.generate_cache_key(df, profile)
        if cached_suggestions := self.suggestion_cache.get(cache_key):
            return cached_suggestions

        # Generate AI suggestions
        prompt = self.create_analysis_prompt(df, profile)
        response = self.active_provider.generate(prompt)
        suggestions = self.parse_ai_response(response)

        # Apply learning from previous feedback
        suggestions = self.learning_engine.apply_learning(suggestions, profile)

        # Cache results
        self.suggestion_cache.set(cache_key, suggestions)

        return suggestions
```

### **3.2 Natural Language Processing**

```python
class NaturalLanguageProcessor:
    """Natural language interface for user interactions"""

    def parse_user_request(self, request: str) -> List[CleaningAction]:
        """Convert natural language to cleaning actions"""

        # Common patterns
        patterns = {
            r"remove duplicates": {"tool": "remove_duplicates", "params": {}},
            r"fix dates? in (\w+)": {"tool": "fix_dates", "params": {"columns": ["\\1"]}},
            r"standardize (\w+)": {"tool": "standardize_text", "params": {"columns": ["\\1"]}},
            r"validate emails?": {"tool": "validate_emails", "params": {"action": "flag"}},
            r"handle missing values?": {"tool": "handle_missing", "params": {"strategy": "auto"}}
        }

        actions = []
        for pattern, action in patterns.items():
            if re.search(pattern, request, re.IGNORECASE):
                actions.append(CleaningAction(**action))

        return actions
```

---

## **4. Performance Optimization**

### **4.1 Memory Management**

```python
class MemoryManager:
    """Memory optimization for large datasets"""

    def __init__(self):
        self.memory_threshold = 1024 * 1024 * 1024  # 1GB
        self.chunk_size = 10000

    def optimize_memory_usage(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize memory usage of DataFrame"""

        # Downcast numeric types
        df = self.downcast_numeric_types(df)

        # Optimize string columns
        df = self.optimize_string_columns(df)

        # Optimize datetime columns
        df = self.optimize_datetime_columns(df)

        return df

    def process_in_chunks(self, file_path: str, chunk_size: int = None) -> Iterator[pd.DataFrame]:
        """Process large files in chunks"""
        chunk_size = chunk_size or self.chunk_size

        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            yield self.optimize_memory_usage(chunk)
```

### **4.2 Parallel Processing**

```python
class ParallelProcessor:
    """Parallel processing for data cleaning operations"""

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, os.cpu_count() + 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def parallel_clean(self, df: pd.DataFrame, operations: List[CleaningOperation]) -> pd.DataFrame:
        """Execute cleaning operations in parallel where possible"""

        # Group operations by column to enable parallel processing
        column_operations = self.group_operations_by_column(operations)

        # Process independent columns in parallel
        futures = []
        for column, ops in column_operations.items():
            if self.can_process_in_parallel(ops):
                future = self.executor.submit(self.process_column, df[column], ops)
                futures.append((column, future))

        # Wait for parallel operations to complete
        results = {}
        for column, future in futures:
            results[column] = future.result()

        # Apply results to DataFrame
        for column, result in results.items():
            df[column] = result

        return df
```

### **4.3 Caching Strategy**

```python
class CacheManager:
    """Intelligent caching for repeated operations"""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or Path.home() / '.csv_cleaner' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = LRUCache(maxsize=100)

    def get_cache_key(self, df: pd.DataFrame, operation: CleaningOperation) -> str:
        """Generate cache key for operation"""
        df_hash = hashlib.md5(df.to_string().encode()).hexdigest()
        op_hash = hashlib.md5(str(operation).encode()).hexdigest()
        return f"{df_hash}_{op_hash}"

    def get_cached_result(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Get cached result if available"""
        # Check memory cache first
        if result := self.memory_cache.get(cache_key):
            return result

        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        if cache_file.exists():
            result = pd.read_parquet(cache_file)
            self.memory_cache[cache_key] = result
            return result

        return None
```

---

## **5. Error Handling and Validation**

### **5.1 Error Handling Strategy**

```python
class ErrorHandler:
    """Comprehensive error handling and recovery"""

    def __init__(self):
        self.error_log = []
        self.recovery_strategies = self.setup_recovery_strategies()

    def handle_operation_error(self, operation: CleaningOperation, error: Exception, df: pd.DataFrame) -> pd.DataFrame:
        """Handle errors during cleaning operations"""

        error_info = {
            'operation': operation,
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.now(),
            'data_shape': df.shape
        }

        self.error_log.append(error_info)

        # Try recovery strategy
        if recovery_strategy := self.recovery_strategies.get(type(error)):
            try:
                return recovery_strategy(operation, error, df)
            except Exception as recovery_error:
                self.log_recovery_failure(error, recovery_error)

        # Fallback to safe operation
        return self.safe_fallback(operation, df)

    def safe_fallback(self, operation: CleaningOperation, df: pd.DataFrame) -> pd.DataFrame:
        """Safe fallback when operation fails"""

        if operation.type == 'remove_duplicates':
            return df.drop_duplicates()
        elif operation.type == 'handle_missing':
            return df.dropna()
        else:
            return df
```

### **5.2 Data Validation**

```python
class DataValidator:
    """Data validation and quality checks"""

    def __init__(self):
        self.validation_rules = self.load_validation_rules()

    def validate_data(self, df: pd.DataFrame, rules: List[ValidationRule] = None) -> ValidationResult:
        """Validate data against rules"""

        rules = rules or self.validation_rules
        results = []

        for rule in rules:
            try:
                is_valid = self.apply_validation_rule(df, rule)
                results.append(ValidationResult(
                    rule=rule,
                    is_valid=is_valid,
                    details=self.get_validation_details(df, rule)
                ))
            except Exception as e:
                results.append(ValidationResult(
                    rule=rule,
                    is_valid=False,
                    error=str(e)
                ))

        return ValidationSummary(results=results)
```

---

## **6. Configuration Management**

### **6.1 Configuration Schema**

```python
@dataclass
class Config:
    """Application configuration"""

    # Core settings
    default_encoding: str = 'utf-8'
    max_memory_usage: int = 1024 * 1024 * 1024  # 1GB
    chunk_size: int = 10000
    parallel_processing: bool = True
    max_workers: int = 4

    # AI settings
    ai_enabled: bool = False
    default_llm_provider: str = 'openai'
    ai_api_keys: Dict[str, str] = field(default_factory=dict)
    ai_cost_limit: float = 10.0  # USD per operation

    # Library settings
    preferred_libraries: Dict[str, List[str]] = field(default_factory=dict)
    library_timeouts: Dict[str, int] = field(default_factory=dict)

    # Performance settings
    enable_caching: bool = True
    cache_size: int = 100
    enable_profiling: bool = False

    # Output settings
    output_format: str = 'csv'
    include_metadata: bool = True
    generate_reports: bool = True
```

### **6.2 Configuration Management**

```python
class ConfigurationManager:
    """Configuration management and persistence"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or Path.home() / '.csv_cleaner' / 'config.yaml'
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()

    def load_config(self) -> Config:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return Config(**config_data)
        else:
            return Config()

    def save_config(self, config: Config):
        """Save configuration to file"""
        config_data = asdict(config)
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
```

---

## **7. Package Structure**

```
csv-cleaner/
├── csv_cleaner/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   ├── config.py
│   │   └── session.py
│   ├── wrappers/
│   │   ├── __init__.py
│   │   ├── pandas_wrapper.py
│   │   ├── pyjanitor_wrapper.py
│   │   ├── feature_engine_wrapper.py
│   │   └── dedupe_wrapper.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── providers.py
│   │   └── learning.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── commands.py
│   └── utils/
│       ├── __init__.py
│       ├── profiler.py
│       ├── validator.py
│       └── cache.py
├── tests/
├── docs/
├── examples/
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## **8. Build Configuration**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "csv-cleaner"
version = "1.0.0"
description = "Self-contained CSV data cleaning tool with AI capabilities"
authors = [{name = "Faizal", email = "jai.crys@gmail.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Information Analysis",
]

dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "pyjanitor>=0.24.0",
    "feature-engine>=1.6.0",
    "missingno>=0.5.0",
    "dedupe>=2.1.0",
    "cleanlab>=2.5.0",
    "great-expectations>=0.17.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "click>=8.1.0",
    "pyyaml>=6.0",
    "tqdm>=4.65.0",
]

[project.optional-dependencies]
ai = [
    "openai>=1.0.0",
    "anthropic>=0.7.0",
    "ollama>=0.1.0",
]
performance = [
    "polars>=0.19.0",
    "dask>=2023.0.0",
]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
csv-cleaner = "csv_cleaner.cli.main:main"
```

---

## **9. Testing Strategy**

### **9.1 Test Architecture**

```python
class TestSuite:
    """Comprehensive test suite for CSV cleaner"""

    def __init__(self):
        self.test_data = self.generate_test_data()
        self.performance_benchmarks = self.setup_benchmarks()

    def run_all_tests(self) -> TestResults:
        """Run complete test suite"""

        results = TestResults()

        # Unit tests
        results.unit_tests = self.run_unit_tests()

        # Integration tests
        results.integration_tests = self.run_integration_tests()

        # Performance tests
        results.performance_tests = self.run_performance_tests()

        # AI tests
        if self.config.ai_enabled:
            results.ai_tests = self.run_ai_tests()

        return results
```

### **9.2 Performance Testing**

```python
class PerformanceTester:
    """Performance testing and benchmarking"""

    def __init__(self):
        self.benchmark_datasets = self.create_benchmark_datasets()

    def run_performance_benchmarks(self) -> PerformanceResults:
        """Run performance benchmarks"""

        results = PerformanceResults()

        for dataset_name, dataset in self.benchmark_datasets.items():
            dataset_results = self.benchmark_dataset(dataset_name, dataset)
            results.datasets[dataset_name] = dataset_results

        return results

    def benchmark_dataset(self, name: str, df: pd.DataFrame) -> DatasetBenchmark:
        """Benchmark performance on specific dataset"""

        benchmark = DatasetBenchmark(name=name, size=len(df))

        # Test basic operations
        benchmark.duplicate_removal = self.time_operation(
            lambda: df.drop_duplicates()
        )

        benchmark.missing_value_handling = self.time_operation(
            lambda: df.dropna()
        )

        benchmark.data_type_conversion = self.time_operation(
            lambda: df.astype(str)
        )

        return benchmark
```

---

## **10. Key Technical Decisions**

### **10.1 Library Selection Rationale**

- **Pandas**: Industry standard for data manipulation, extensive ecosystem
- **PyJanitor**: Fluent API for data cleaning, reduces boilerplate code
- **Feature-Engine**: Advanced transformations, scikit-learn compatibility
- **Dedupe**: ML-based entity resolution, handles fuzzy matching
- **Missingno**: Specialized missing data visualization
- **Polars**: High-performance alternative for large datasets

### **10.2 Architecture Decisions**

- **Wrapper Pattern**: Unified interface to multiple libraries
- **AI Optional**: Graceful fallback when AI is unavailable
- **Caching Strategy**: Memory and disk caching for performance
- **Parallel Processing**: Multi-threading for I/O operations
- **Error Recovery**: Comprehensive error handling with fallbacks

### **10.3 Performance Optimizations**

- **Memory Management**: Efficient data type optimization
- **Chunked Processing**: Handle large files without memory issues
- **Library Selection**: AI-powered optimal library selection
- **Caching**: Intelligent caching of repeated operations
- **Parallel Processing**: Multi-threaded operations where possible

### **10.4 Standardized Performance Targets**

- **Small datasets (≤100K rows)**: Process in <2 minutes
- **Medium datasets (100K-1M rows)**: Process in <5 minutes
- **Large datasets (1M+ rows)**: Process in <10 minutes
- **Memory usage**: Efficient handling up to 1GB datasets
- **Startup time**: Tool ready in <2 seconds
- **AI response time**: AI suggestions in <10 seconds

---

## **11. Cross-References and Documentation Links**

### **Related Documents**
- **Product Requirements Document (PRD)**: `../prd.md` - Detailed product requirements and user stories
- **Development Plan**: `../plan.md` - Comprehensive development timeline and tasks
- **Technical Specification**: `tech.md` - This document - Technical architecture and implementation details

### **Documentation Structure**
```
docs/
├── prd.md          # Product Requirements Document
├── plan.md         # Development Plan and Timeline
└── tech.md         # Technical Specification (this document)
```

### **Key Sections by Document**
- **PRD**: User stories, functional requirements, success metrics
- **Plan**: Implementation timeline, resource requirements, risk management
- **Tech**: Architecture design, library integration, performance optimization

---

This technical specification provides a comprehensive blueprint for implementing the CSV data cleaner with detailed architecture, library integrations, performance optimizations, and deployment strategies. The design emphasizes modularity, extensibility, and maintainability while leveraging existing industry-standard libraries for robust functionality.
