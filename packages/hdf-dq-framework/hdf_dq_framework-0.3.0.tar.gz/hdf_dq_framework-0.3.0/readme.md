# HDF DQ Framework

A powerful Data Quality Framework for PySpark DataFrames using Great Expectations validation rules, designed for the HDF Data Pipeline ecosystem.

## Overview

The DQ Framework provides a simple and efficient way to filter DataFrames based on data quality rules. It separates qualified data from bad data, allowing you to handle data quality issues systematically in your data pipelines.

### Key Features

- **Easy Integration**: Simple API that works with existing PySpark workflows
- **Great Expectations**: Leverages the power of Great Expectations for data validation
- **Flexible Rules**: Support for JSON string, dictionary, or list-based rule configuration
- **Dual Output**: Returns both qualified and bad rows as separate DataFrames
- **Detailed Validation**: Optional validation details for debugging and monitoring

## Quick Start

```python
from pyspark.sql import SparkSession
from dq_framework import DQFramework

# Initialize Spark session
spark = SparkSession.builder.appName("DQ_Example").getOrCreate()

# Create sample data
data = [
    (1, "John", 25, "john@email.com"),
    (2, "Jane", -5, "invalid-email"),  # Bad data: negative age, invalid email
    (3, "Bob", 30, "bob@email.com"),
    (4, None, 35, "alice@email.com"),  # Bad data: null name
]
columns = ["id", "name", "age", "email"]
df = spark.createDataFrame(data, columns)

# Define quality rules
quality_rules = [
    {
        "expectation_type": "expect_column_values_to_not_be_null",
        "kwargs": {"column": "name"}
    },
    {
        "expectation_type": "expect_column_values_to_be_between",
        "kwargs": {"column": "age", "min_value": 0, "max_value": 120}
    },
    {
        "expectation_type": "expect_column_values_to_match_regex",
        "kwargs": {"column": "email", "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
    }
]

# Initialize DQ Framework
dq = DQFramework()

# Filter data
qualified_df, bad_df = dq.filter_dataframe(
    dataframe=df,
    quality_rules=quality_rules,
    include_validation_details=True
)

# Show results
print("Qualified Data:")
qualified_df.show()

print("Bad Data:")
bad_df.show()
```

## API Reference

### DQFramework

The main class for data quality processing.

#### Methods

- **`filter_dataframe(dataframe, quality_rules, columns=None, include_validation_details=False)`**
  - Filters a DataFrame based on quality rules
  - Returns tuple of (qualified_df, bad_df)

### RuleProcessor

Handles the processing of Great Expectations rules.

## Dependencies

### Core Dependencies

- **PySpark** ^3.0.0: For DataFrame operations
- **Great Expectations** ^0.15.0: For validation logic
- **typing-extensions** ^4.0.0: For enhanced type hints
