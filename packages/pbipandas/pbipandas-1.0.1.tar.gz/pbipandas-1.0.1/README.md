# pbipandas
![CI](https://github.com/hoangdinh2710/pbipandas/actions/workflows/ci.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/pbipandas.svg)](https://pypi.org/project/pbipandas/)

**pbipandas** is a powerful, modular Python client for the [Power BI REST API](https://learn.microsoft.com/en-us/rest/api/power-bi/) that helps you authenticate and retrieve data directly into **Pandas DataFrames**. 

✨ **Now with modular architecture for better maintainability and targeted functionality!**

---

## 🚀 Features

- 🗂️ **Comprehensive Metadata**: Get details for all Power BI items (datasets, dataflows, reports, refresh logs, datasources)
- 🔐 **Easy Authentication**: OAuth2 authentication using client credentials
- 📊 **Pandas Integration**: Seamless integration with Pandas DataFrames
- 🧩 **Modular Design**: Use specific modules or the unified client
- 📚 **Built-in Help**: Discover all functions with `client.info()`
- ⚡ **Bulk Operations**: Retrieve data across all workspaces efficiently
- 🔄 **Refresh Management**: Trigger and monitor dataset/dataflow refreshes
- 📝 **DAX Queries**: Execute DAX queries against datasets

---

## 📦 Installation

```bash
pip install pbipandas
```

Or for development:

```bash
git clone https://github.com/hoangdinh2710/pbipandas.git
cd pbipandas
pip install -e .
```

---

## 🔧 Quick Start

### 🆕 Discover All Functions
```python
import pbipandas

# Get comprehensive help about all available functions
pbipandas.info()
```

### 🎯 Option 1: Unified Client (Recommended for Most Users)
```python
from pbipandas import PowerBIClient

# Initialize client
client = PowerBIClient(tenant_id, client_id, client_secret)

# Get help about all available methods
client.info()

# Get all workspaces and datasets
workspaces = client.get_all_workspaces()
datasets = client.get_all_datasets()

# Execute DAX queries
result = client.execute_query(workspace_id, dataset_id, "EVALUATE VALUES(Table[Column])")

# Refresh operations
client.refresh_dataset(workspace_id, dataset_id)
refresh_history = client.get_dataset_refresh_history_by_id(workspace_id, dataset_id)

# Bulk operations across all workspaces
all_sources = client.get_all_dataset_sources()
all_tables = client.get_all_dataset_tables()

# Get measures for specific datasets across all workspaces
dataset_ids = ["dataset1", "dataset2", "dataset3"]
measures = client.get_measures_for_dataset_ids_across_workspaces(dataset_ids)
```

### 🧩 Option 2: Modular Approach (For Targeted Functionality)
```python
from pbipandas import WorkspaceClient, DatasetClient, BulkClient

# Use specific clients for targeted functionality
workspace_client = WorkspaceClient(tenant_id, client_id, client_secret)
workspaces = workspace_client.get_all_workspaces()

dataset_client = DatasetClient(tenant_id, client_id, client_secret)
dataset_client.refresh_dataset(workspace_id, dataset_id)
result = dataset_client.execute_query(workspace_id, dataset_id, "EVALUATE INFO.TABLES()")

bulk_client = BulkClient(tenant_id, client_id, client_secret)
all_datasets = bulk_client.get_all_datasets()
```

### 🔍 Option 3: Individual Operations
```python
from pbipandas import DatasetClient, extract_connection_details

# Just dataset operations
dataset_client = DatasetClient(tenant_id, client_id, client_secret)

# Get dataset metadata
metadata = dataset_client.get_dataset_by_id(workspace_id, dataset_id)
tables = dataset_client.get_dataset_tables_by_id(workspace_id, dataset_id)
columns = dataset_client.get_dataset_columns_by_id(workspace_id, dataset_id)

# Get measures for multiple datasets in workspace
dataset_ids = ["dataset1", "dataset2", "dataset3"]
measures = dataset_client.get_measures_for_datasets(workspace_id, dataset_ids)

# Refresh specific tables
dataset_client.refresh_tables_from_dataset(workspace_id, dataset_id, ["Table1", "Table2"])
```

## 📚 Available Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `PowerBIClient` | **All-in-one client** | Everything below combined |
| `WorkspaceClient` | **Workspace operations** | `get_all_workspaces()`, `get_workspace_users_by_id()` |
| `DatasetClient` | **Dataset operations** | `execute_query()`, `refresh_dataset()`, `get_dataset_*()`, `get_measures_for_datasets()` |
| `ReportClient` | **Report operations** | `get_report_by_id()`, `get_report_sources_by_id()` |
| `DataflowClient` | **Dataflow operations** | `refresh_dataflow()`, `get_dataflow_*()` |
| `BulkClient` | **Bulk data retrieval** | `get_all_*()` functions |

## 🎯 Common Use Cases

### 📊 Data Discovery & Analysis
```python
from pbipandas import PowerBIClient

client = PowerBIClient(tenant_id, client_id, client_secret)

# Get overview of all Power BI assets
workspaces = client.get_all_workspaces()
datasets = client.get_all_datasets()
reports = client.get_all_reports()

# Analyze data sources across organization
all_sources = client.get_all_dataset_sources()
print(f"Found {len(all_sources)} data sources across {all_sources['workspaceName'].nunique()} workspaces")
```

### 🔄 Automated Refresh Management
```python
# Monitor and trigger refreshes
refresh_history = client.get_all_dataset_refresh_history()
failed_refreshes = refresh_history[refresh_history['status'] == 'Failed']

# Refresh specific datasets
for workspace_id, dataset_id in failed_datasets:
    client.refresh_dataset(workspace_id, dataset_id)
```

### 📝 DAX Query Execution
```python
# Execute custom DAX queries
dax_query = """
EVALUATE 
TOPN(10, 
    ADDCOLUMNS(
        VALUES(Product[Category]),
        "Sales", [Total Sales]
    ),
    [Sales], DESC
)
"""
result = client.execute_query(workspace_id, dataset_id, dax_query)
```

### 🏗️ Schema Documentation
```python
# Document all dataset schemas
all_tables = client.get_all_dataset_tables()
all_columns = client.get_all_dataset_columns()
all_measures = client.get_all_dataset_measures()

# Create comprehensive data dictionary
schema_doc = all_columns.merge(all_tables, on=['datasetId', 'tableName'])
```

---

## 🏗️ Architecture

pbipandas uses a clean, modular architecture with proper inheritance:

```
pbipandas/
├── auth/           # Authentication (BaseClient)
├── utils/          # Utilities (connection helpers, info)
├── workspace/      # Workspace operations
├── dataset/        # Dataset operations + DAX queries
├── report/         # Report operations  
├── dataflow/       # Dataflow operations
├── bulks/          # Bulk retrieval across all workspaces
└── client.py       # Unified PowerBIClient
```

**Inheritance Structure:**
- `PowerBIClient` inherits from `WorkspaceClient`, `DatasetClient`, `ReportClient`, `DataflowClient`, and `BulkClient`
- `BulkClient` inherits from `BaseClient` and creates instances of individual clients for bulk operations
- All individual clients inherit from `BaseClient` for authentication

This design allows you to:
- **Import only what you need** for smaller footprint
- **Maintain code easily** with clear separation of concerns
- **Extend functionality** by adding new modules
- **Use familiar patterns** with consistent APIs across modules

---

## 🧪 Development

### Running Tests
```bash
pytest
```

### Linting and Formatting
```bash
flake8 .
black .
```

---

## 📄 License

[MIT License](LICENSE)

---

## 🔧 Prerequisites

- Python 3.7+
- Power BI Pro or Premium license
- Azure App Registration with Power BI API permissions
- Required credentials: `tenant_id`, `client_id`, `client_secret`

## 🛡️ Authentication Setup

1. Register an app in Azure Active Directory
2. Grant Power BI Service API permissions
3. Get your tenant ID, client ID, and client secret
4. Use with pbipandas:

```python
from pbipandas import PowerBIClient

client = PowerBIClient(
    tenant_id="your-tenant-id",
    client_id="your-client-id", 
    client_secret="your-client-secret"
)
```

## 🎓 Learning Resources

- **Built-in Help**: `pbipandas.info()` or `client.info()`
- **Power BI API**: [Official REST API Documentation](https://learn.microsoft.com/en-us/rest/api/power-bi/)

## 🙌 Contributing

Pull requests are welcome! Please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ✨ Reference

- [Power BI REST API Documentation](https://learn.microsoft.com/en-us/rest/api/power-bi/)
- [pandas Documentation](https://pandas.pydata.org/)
- [Azure App Registration Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
