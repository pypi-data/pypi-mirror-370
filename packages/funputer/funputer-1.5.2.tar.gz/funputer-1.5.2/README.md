# FunPuter - Intelligent Imputation Analysis

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/funputer.svg)](https://pypi.org/project/funputer/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)]
[![Test Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen.svg)](#documentation)

**Intelligent imputation analysis with automatic data validation and metadata inference**

FunPuter analyzes your data and recommends the best imputation methods based on data patterns, missing mechanisms, and metadata constraints. Get intelligent suggestions with confidence scores to handle missing data professionally.

## 🚀 Quick Start

### Installation

```bash
pip install funputer
```

### 30-Second Example

**Auto-Inference Mode** (Zero Configuration)
```python
import funputer

# Point to your CSV - FunPuter figures out everything automatically
suggestions = funputer.analyze_imputation_requirements("your_data.csv")

# Get intelligent suggestions with confidence scores
for suggestion in suggestions:
    if suggestion.missing_count > 0:
        print(f"📊 {suggestion.column_name}: {suggestion.proposed_method}")
        print(f"   Confidence: {suggestion.confidence_score:.3f}")
        print(f"   Reason: {suggestion.rationale}")
        print(f"   Missing: {suggestion.missing_count} ({suggestion.missing_percentage:.1f}%)")
```

**Production Mode** (Full Control)
```python
import funputer
from funputer.models import ColumnMetadata

# Define your data structure with constraints
metadata = [
    ColumnMetadata('customer_id', 'integer', unique_flag=True, nullable=False),
    ColumnMetadata('age', 'integer', min_value=18, max_value=100),
    ColumnMetadata('income', 'float', min_value=0),
    ColumnMetadata('category', 'categorical', allowed_values='A,B,C'),
]

# Get production-grade suggestions
suggestions = funputer.analyze_dataframe(your_dataframe, metadata)
```

## 🎯 Key Features

- **🤖 Automatic Metadata Inference** - Intelligent data type and constraint detection
- **📊 Missing Data Analysis** - MCAR, MAR, MNAR mechanism detection  
- **⚡ Data Validation** - Real-time constraint checking and validation
- **🎯 Smart Recommendations** - Context-aware imputation method suggestions
- **📈 Confidence Scoring** - Transparent reliability estimates for each recommendation
- **🛡️ Pre-flight Checks** - Comprehensive data validation before analysis
- **💻 CLI & Python API** - Flexible usage via command line or programmatic access

## 📊 Data Validation System

Comprehensive validation runs automatically to prevent crashes and guide your workflow:

- **File validation**: Format detection, encoding, accessibility
- **Structure validation**: Column analysis, data type inference  
- **Memory estimation**: Resource usage prediction
- **Advisory recommendations**: Guided workflow suggestions

**Independent Usage:**
```bash
# Basic validation check
funputer preflight -d your_data.csv

# With custom options  
funputer preflight -d data.csv --sample-rows 5000 --encoding utf-8

# JSON report output
funputer preflight -d data.csv --json-out report.json
```

**Exit Codes:**
- `0`: Ready for analysis
- `2`: OK with warnings (can proceed)
- `10`: Hard error (cannot proceed)

## 💻 Command Line Interface

```bash
# Generate metadata template from your data
funputer init -d data.csv -o metadata.csv

# Analyze with auto-inference  
funputer analyze -d data.csv

# Analyze with custom metadata
funputer analyze -d data.csv -m metadata.csv --verbose

# Data quality check first
funputer preflight -d data.csv
```

## 📚 Usage Examples

### Basic Analysis

```python
import funputer

# Simple analysis with auto-inference
suggestions = funputer.analyze_imputation_requirements("sales_data.csv")

# Display recommendations
for suggestion in suggestions:
    print(f"Column: {suggestion.column_name}")
    print(f"Method: {suggestion.proposed_method}")  
    print(f"Confidence: {suggestion.confidence_score:.3f}")
    print(f"Missing: {suggestion.missing_count} values")
    print()
```

### Advanced Configuration

```python
from funputer.models import ColumnMetadata, AnalysisConfig
from funputer.analyzer import ImputationAnalyzer

# Custom metadata with business rules
metadata = [
    ColumnMetadata('product_id', 'string', unique_flag=True, max_length=10),
    ColumnMetadata('price', 'float', min_value=0, max_value=10000),
    ColumnMetadata('category', 'categorical', allowed_values='Electronics,Books,Clothing'),
    ColumnMetadata('rating', 'float', min_value=1.0, max_value=5.0),
]

# Custom analysis configuration
config = AnalysisConfig(
    missing_percentage_threshold=0.3,  # 30% threshold
    skip_columns=['internal_id'],
    outlier_threshold=0.1
)

# Run analysis
analyzer = ImputationAnalyzer(config)
suggestions = analyzer.analyze_dataframe(df, metadata)
```

### Industry-Specific Examples

**E-commerce Analytics**
```python
metadata = [
    ColumnMetadata('customer_id', 'integer', unique_flag=True, nullable=False),
    ColumnMetadata('age', 'integer', min_value=13, max_value=120),
    ColumnMetadata('purchase_amount', 'float', min_value=0),
    ColumnMetadata('customer_segment', 'categorical', allowed_values='Premium,Standard,Basic'),
]
suggestions = funputer.analyze_dataframe(customer_df, metadata)
```

**Healthcare Data**  
```python
metadata = [
    ColumnMetadata('patient_id', 'integer', unique_flag=True, nullable=False),
    ColumnMetadata('age', 'integer', min_value=0, max_value=150),
    ColumnMetadata('blood_pressure', 'integer', min_value=50, max_value=300),
    ColumnMetadata('diagnosis', 'categorical', nullable=False),
]
config = AnalysisConfig(missing_threshold=0.05)  # Low tolerance for healthcare
suggestions = funputer.analyze_dataframe(patient_df, metadata, config)
```

**Financial Risk Assessment**
```python  
metadata = [
    ColumnMetadata('application_id', 'integer', unique_flag=True, nullable=False),
    ColumnMetadata('credit_score', 'integer', min_value=300, max_value=850),
    ColumnMetadata('debt_to_income', 'float', min_value=0.0, max_value=10.0),
    ColumnMetadata('loan_purpose', 'categorical', allowed_values='home,auto,personal,business'),
]
# Skip sensitive columns
config = AnalysisConfig(skip_columns=['ssn', 'account_number'])
suggestions = funputer.analyze_dataframe(loan_df, metadata, config)
```

## ⚙️ Requirements

- **Python**: 3.9 or higher
- **Dependencies**: pandas, numpy, scipy, pydantic, click, pyyaml

## 🔧 Installation from Source

```bash
git clone https://github.com/RajeshRamachander/funputer.git
cd funputer
pip install -e .
```

## 📚 Documentation

- **API Reference**: Complete docstrings and type hints throughout the codebase
- **Examples**: See usage examples above and in the codebase
- **Test Coverage**: 84% coverage with comprehensive test suite

## 📄 License  

Proprietary License - Source code is available for inspection but not for derivative works.

---

**Focus**: Get intelligent imputation recommendations, not complex infrastructure.