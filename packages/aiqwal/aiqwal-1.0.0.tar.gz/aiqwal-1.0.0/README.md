# AIQWAL - AI Query Writer for Any Language

🌍 **Universal AI-powered SQL generator that works with ANY database in the world!**

[![PyPI version](https://badge.fury.io/py/aiqwal.svg)](https://badge.fury.io/py/aiqwal)
[![Python versions](https://img.shields.io/pypi/pyversions/aiqwal.svg)](https://pypi.org/project/aiqwal/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/aiqwal)](https://pepy.tech/project/aiqwal)

## 🚀 What is AIQWAL?

AIQWAL (AI Query Writer for Any Language) is a revolutionary Python library that converts natural language questions into SQL queries using AI, then executes them on **ANY database in the world**.

### ✨ Key Features

- 🤖 **AI-Powered**: Uses advanced language models.
- 🌍 **Universal Database Support**: Works with 15+ database types
- 🔄 **Auto-Adaptation**: Automatically converts SQL syntax for each database
- 🛡️ **Smart Validation**: Prevents dangerous operations and validates queries
- 🎯 **Zero Configuration**: Just provide a connection string!
- ⚡ **Production Ready**: Comprehensive error handling and logging

### 🎯 Supported Databases

| Database | Status | Connection Example |
|----------|--------|-------------------|
| **SQLite** | ✅ | `sqlite:///database.db` |
| **PostgreSQL** | ✅ | `postgresql://user:pass@host:5432/db` |
| **MySQL** | ✅ | `mysql://user:pass@host:3306/db` |
| **SQL Server** | ✅ | `mssql+pyodbc://user:pass@host/db` |
| **Oracle** | ✅ | `oracle+cx_oracle://user:pass@host:1521/db` |
| **Snowflake** | ✅ | `snowflake://user:pass@account/db` |
| **BigQuery** | ✅ | `bigquery://project/dataset` |
| **Redshift** | ✅ | `redshift+psycopg2://user:pass@host/db` |
| **MongoDB** | ✅ | `mongodb://host/db` (via SQL interface) |
| **Any SQLAlchemy DB** | ✅ | Any valid SQLAlchemy connection string |

## 🔧 Installation

```bash
# Basic installation
pip install aiqwal

# With all database drivers
pip install aiqwal[all]

# Development installation  
pip install aiqwal[dev]
```

### Prerequisites

1. **AI Model**: Download a compatible model (e.g., SQLCoder):
```bash
# Download SQLCoder model (recommended)
python -c "
import requests
url = 'https://huggingface.co/defog/sqlcoder-7b-2/resolve/main/sqlcoder-7b-q4_k_m.gguf'
response = requests.get(url)
with open('sqlcoder-7b-q4_k_m.gguf', 'wb') as f:
    f.write(response.content)
"
```

2. **Database Drivers**: Install drivers for your databases:
```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL  
pip install pymysql

# SQL Server
pip install pyodbc

# Oracle
pip install cx-oracle

# Snowflake
pip install snowflake-sqlalchemy

# BigQuery
pip install pybigquery
```

## 🚀 Quick Start

### Basic Usage

```python
from aiqwal import AIQWAL

# Connect to any database (SQLite example)
ai = AIQWAL('sqlite:///employees.db')

# Ask questions in natural language!
results = ai.query("Show me the top 10 highest paid employees")
print(results)
# [{'name': 'John Doe', 'salary': 95000}, ...]

# Works with complex queries too
results = ai.query("Find average salary by department for employees hired after 2020")
print(results)
```

### Different Databases

```python
# PostgreSQL
ai = AIQWAL('postgresql://user:password@localhost:5432/company')
results = ai.query("Show me monthly sales trends")

# MySQL
ai = AIQWAL('mysql://user:password@localhost:3306/ecommerce') 
results = ai.query("Find top selling products this quarter")

# SQL Server
ai = AIQWAL('mssql+pyodbc://user:password@server/database')
results = ai.query("Get customer retention rates by region")

# Snowflake
ai = AIQWAL('snowflake://user:password@account/database/schema')
results = ai.query("Analyze user engagement metrics")

# The same code works with ANY database!
```

### Advanced Usage

```python
from aiqwal import AIQWAL

# Initialize with custom model
ai = AIQWAL(
    connection_string='postgresql://user:pass@host/db',
    model_path='/path/to/your/model.gguf',
    auto_connect=True
)

# Generate SQL without executing (for review)
sql = ai.generate_sql_only("Find customers who haven't ordered in 30 days")
print(f"Generated SQL: {sql}")

# Execute raw SQL
results = ai.execute_sql("SELECT COUNT(*) FROM orders WHERE date > '2024-01-01'")

# Get database information
info = ai.get_database_info()
print(f"Connected to: {info['name']}")

# Get schema
schema = ai.get_schema()
print(f"Available tables: {list(schema.keys())}")
```

### CLI Usage

```bash
# Interactive mode
aiqwal interactive --db "postgresql://user:pass@host/db"

# Single query
aiqwal query --db "sqlite:///mydb.db" --query "Show top 10 sales"

# Generate SQL only
aiqwal generate --db "mysql://user:pass@host/db" --query "Find active users"
```

## 🎯 Real-World Examples

### E-commerce Analytics
```python
ai = AIQWAL('postgresql://user:pass@host/ecommerce_db')

# Sales analysis
sales = ai.query("Show monthly revenue trends for the last 12 months")

# Customer insights  
customers = ai.query("Find top 20 customers by total purchase value")

# Product performance
products = ai.query("Which products have the highest return rates?")
```

### HR Analytics
```python
ai = AIQWAL('mysql://user:pass@host/hr_system')

# Employee metrics
employees = ai.query("Show average salary by department and experience level")

# Hiring analysis
hiring = ai.query("What's our hiring trend by month for the last 2 years?")

# Retention insights
retention = ai.query("Calculate employee turnover rate by department")
```

### Financial Reporting
```python
ai = AIQWAL('mssql+pyodbc://user:pass@server/financial_db')

# Revenue analysis
revenue = ai.query("Break down revenue by product line and quarter")

# Expense tracking
expenses = ai.query("Show top expense categories for this fiscal year")

# Profitability
profit = ai.query("Calculate profit margins by business unit")
```

## 🔧 Configuration

### Model Configuration
```python
# Use different AI models
ai = AIQWAL(
    connection_string='your-db-connection',
    model_path='/path/to/codellama-sql.gguf',  # CodeLlama
    # model_path='/path/to/wizardcoder-sql.gguf',  # WizardCoder
)
```

### Database-Specific Options
```python
# SQL Server with specific driver
ai = AIQWAL(
    'mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server',
    auto_connect=True
)

# PostgreSQL with SSL
ai = AIQWAL(
    'postgresql://user:pass@host:5432/db?sslmode=require',
    auto_connect=True  
)
```

## 🛡️ Security & Safety

AIQWAL includes built-in safety features:

- **Query Validation**: Prevents dangerous operations (DROP, DELETE, etc.)
- **SQL Injection Protection**: Uses parameterized queries
- **Schema Validation**: Ensures queries reference valid tables/columns
- **Connection Security**: Supports SSL/TLS for database connections

```python
# These will be safely rejected:
ai.query("DROP TABLE users")  # ❌ Dangerous operation blocked
ai.query("DELETE FROM orders")  # ❌ Modification blocked  
ai.query("Show me customers")  # ✅ Safe SELECT query allowed
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Test specific database
pytest tests/test_postgresql.py

# Test with coverage
pytest --cov=aiqwal tests/

# Integration tests
pytest tests/test_integration.py
```

## 📊 Performance

AIQWAL is designed for production use:

- **Model Loading**: 2-5 seconds (cached after first use)
- **Query Generation**: 1-10 seconds (depending on complexity)  
- **Query Execution**: Database-dependent
- **Memory Usage**: ~500MB-2GB (model-dependent)

### Benchmarks

| Database | Connection Time | Query Generation | Simple Query | Complex Query |
|----------|----------------|------------------|--------------|---------------|
| SQLite | <100ms | 2-5s | <100ms | 100-500ms |
| PostgreSQL | 100-300ms | 2-5s | 50-200ms | 200-1s |
| MySQL | 100-300ms | 2-5s | 50-200ms | 200-1s |
| SQL Server | 200-500ms | 2-5s | 100-300ms | 300-2s |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/aiqwal.git
cd aiqwal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest
```

## 📚 Documentation

- [Full Documentation](https://aiqwal.readthedocs.io/)
- [API Reference](https://aiqwal.readthedocs.io/en/latest/api/)
- [Database Support](https://aiqwal.readthedocs.io/en/latest/databases/)
- [Examples](https://aiqwal.readthedocs.io/en/latest/examples/)

## 🐛 Troubleshooting

### Common Issues

**Model Loading Error:**
```python
# Ensure model file exists and is compatible
import os
print(os.path.exists('path/to/model.gguf'))
```

**Database Connection Error:**
```python  
# Test connection string
ai = AIQWAL('your-connection-string')
print(ai.test_connection())
```

**Query Generation Issues:**
```python
# Check database schema
schema = ai.get_schema()
print("Available tables:", list(schema.keys()))
```

### Getting Help

- 📚 [Documentation](https://aiqwal.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/yourusername/aiqwal/issues)
- 💬 [Discussions](https://github.com/yourusername/aiqwal/discussions)
- 📧 [Email Support](mailto:support@aiqwal.com)

## 📄 License

AIQWAL is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [SQLCoder](https://github.com/defog-ai/sqlcoder) for the excellent SQL generation model
- [llama.cpp](https://github.com/ggerganov/llama.cpp) for efficient model inference
- [SQLAlchemy](https://www.sqlalchemy.org/) for universal database connectivity
- The open-source community for continuous inspiration

## ⭐ Star History

If you find AIQWAL useful, please consider starring the repository!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/aiqwal&type=Date)](https://star-history.com/#yourusername/aiqwal&Date)

---

**Made with ❤️ by the AIQWAL team**

*Transform natural language into SQL queries for ANY database in the world!*