from .client import PowerBIClient
from .workspace import WorkspaceClient
from .dataset import DatasetClient
from .report import ReportClient
from .dataflow import DataflowClient
from .bulks import BulkClient
from .auth import BaseClient
from .utils import extract_connection_details, get_client_info, print_client_info

# Convenience function for getting help without creating a client
def info():
    """Display comprehensive information about all available PbiPandas functions."""
    print_client_info()

__version__ = "1.0.0"
__all__ = [
    'PowerBIClient',        # Convenience class with all functionality
    'WorkspaceClient',      # Workspace-specific operations
    'DatasetClient',        # Dataset-specific operations
    'ReportClient',         # Report-specific operations
    'DataflowClient',       # Dataflow-specific operations
    'BulkClient',          # Bulk data retrieval operations
    'BaseClient',          # Base authentication class
    'extract_connection_details',  # Utility function
    'info',                # Help function
    'get_client_info',     # Get info as string
    'print_client_info'    # Print info to console
]
