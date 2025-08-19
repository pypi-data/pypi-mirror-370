def get_client_info():
    """
    Display comprehensive information about all available PbiPandas client functions.
    
    Returns:
        str: Formatted information about all available methods grouped by functionality.
    """
    
    info_text = """
🔋 PbiPandas Client Information
═══════════════════════════════════════════════════════════════════════════════

📊 AUTHENTICATION & SETUP
──────────────────────────
• PowerBIClient(tenant_id, client_id, client_secret)  - Main client with all functionality
• BaseClient(tenant_id, client_id, client_secret)     - Base authentication only
• get_token()                                          - Retrieve OAuth2 access token
• get_header()                                         - Get authenticated headers

🏢 WORKSPACE OPERATIONS
───────────────────────
• get_workspace_by_id(workspace_id)                   - Get specific workspace details
• get_workspace_users_by_id(workspace_id)             - Get users in workspace
• get_all_workspaces()                                - Get all accessible workspaces

📈 DATASET OPERATIONS
─────────────────────
Query & Execution:
• execute_query(workspace_id, dataset_id, query)      - Execute DAX queries

Basic Info:
• get_dataset_by_id(workspace_id, dataset_id)         - Get dataset metadata
• get_dataset_sources_by_id(workspace_id, dataset_id) - Get dataset data sources
• get_dataset_users_by_id(workspace_id, dataset_id)   - Get dataset users

Refresh Operations:
• refresh_dataset(workspace_id, dataset_id, body)     - Refresh entire dataset
• refresh_tables_from_dataset(workspace_id, dataset_id, table_list) - Refresh specific tables
• refresh_objects_from_dataset(workspace_id, dataset_id, objects)   - Refresh specific objects
• get_dataset_refresh_history_by_id(workspace_id, dataset_id, top_n) - Get refresh history

Schema & Metadata:
• get_dataset_tables_by_id(workspace_id, dataset_id)  - Get all tables in dataset
• get_dataset_columns_by_id(workspace_id, dataset_id) - Get all columns in dataset
• get_dataset_measures_by_id(workspace_id, dataset_id) - Get all measures in dataset
• get_measures_for_datasets(workspace_id, dataset_id_list) - Get measures for multiple datasets in workspace
• get_dataset_calc_dependencies_by_id(workspace_id, dataset_id) - Get calculation dependencies

Configuration:
• update_dataset_parameters(workspace_id, dataset_id, parameters) - Update dataset parameters

📋 REPORT OPERATIONS
────────────────────
• get_report_by_id(workspace_id, report_id)           - Get report metadata
• get_report_sources_by_id(workspace_id, report_id)   - Get report data sources

🌊 DATAFLOW OPERATIONS
──────────────────────
• get_dataflow_by_id(workspace_id, dataflow_id)       - Get dataflow metadata
• refresh_dataflow(workspace_id, dataflow_id)         - Trigger dataflow refresh
• get_dataflow_refresh_history_by_id(workspace_id, dataflow_id) - Get refresh history
• get_dataflow_sources_by_id(workspace_id, dataflow_id) - Get dataflow sources

📦 BULK OPERATIONS (Get All Data)
─────────────────────────────────
Core Objects:
• get_all_workspaces()                                - All workspaces
• get_all_datasets()                                  - All datasets across workspaces
• get_all_reports()                                   - All reports across workspaces
• get_all_dataflows()                                 - All dataflows across workspaces

Refresh History:
• get_all_dataset_refresh_history()                   - All dataset refresh history
• get_all_dataflow_refresh_history()                  - All dataflow refresh history

Users & Access:
• get_all_dataset_users()                             - All dataset user permissions

Data Sources:
• get_all_dataset_sources()                           - All dataset data sources
• get_all_dataflow_sources()                          - All dataflow data sources
• get_all_report_sources()                            - All report data sources

Schema Information:
• get_all_dataset_tables()                            - All tables across all datasets
• get_all_dataset_columns()                           - All columns across all datasets
• get_all_dataset_measures()                          - All measures across all datasets
• get_measures_for_dataset_ids_across_workspaces(dataset_id_list)   - Measures for specific dataset IDs across workspaces
• get_all_dataset_calc_dependencies()                 - All calculation dependencies

🛠️ UTILITY FUNCTIONS
────────────────────
• extract_connection_details(connection_obj)          - Parse connection details
• info()                                              - Show this information

💡 USAGE EXAMPLES
────────────────
# Basic setup
client = PowerBIClient(tenant_id, client_id, client_secret)

# Get workspace info
workspaces = client.get_all_workspaces()

# Execute DAX query
result = client.execute_query(workspace_id, dataset_id, "EVALUATE VALUES(Table[Column])")

# Get measures for specific datasets across all workspaces
dataset_ids = ["dataset1", "dataset2", "dataset3"]
measures = client.get_measures_for_dataset_ids_across_workspaces(dataset_ids)

# Bulk operations
all_datasets = client.get_all_datasets()
all_sources = client.get_all_dataset_sources()

# Modular approach
from pbipandas import DatasetClient, BulkClient
dataset_client = DatasetClient(tenant_id, client_id, client_secret)
bulk_client = BulkClient(tenant_id, client_id, client_secret)

🔗 MORE HELP
───────────
• Check REFACTORING_GUIDE.md for detailed module documentation
• All methods return pandas DataFrames (except refresh operations)
• Use client.method_name? in Jupyter for detailed docstrings

═══════════════════════════════════════════════════════════════════════════════
"""
    return info_text


def print_client_info():
    """Print the client information to console."""
    print(get_client_info())
