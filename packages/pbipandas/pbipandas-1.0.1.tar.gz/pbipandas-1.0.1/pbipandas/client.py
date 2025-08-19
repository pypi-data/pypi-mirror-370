from .workspace import WorkspaceClient
from .dataset import DatasetClient
from .report import ReportClient
from .dataflow import DataflowClient
from .bulks import BulkClient
from .utils import print_client_info, get_client_info


class PowerBIClient(WorkspaceClient, DatasetClient, ReportClient, DataflowClient, BulkClient):
    """
    PowerBIClient handles authentication and API calls to the Power BI REST API.
    
    This is the main client that combines all the specialized clients for different
    Power BI objects and operations.

    Attributes:
        tenant_id (str): Azure AD tenant ID.
        client_id (str): App's client ID registered in Azure.
        client_secret (str): App's client secret.
        access_token (str): Access token retrieved using client credentials.
    """
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize the client and retrieve an access token.

        Args:
            tenant_id (str): Azure AD tenant ID.
            client_id (str): Client/application ID.
            client_secret (str): Client/application secret.
        """
        # Initialize all parent classes with the same credentials
        super().__init__(tenant_id, client_id, client_secret)
    
    def info(self, return_string: bool = False):
        """
        Display comprehensive information about all available client methods.
        
        Args:
            return_string (bool): If True, returns the info as a string instead of printing.
            
        Returns:
            str or None: Information string if return_string=True, otherwise prints to console.
        """
        if return_string:
            return get_client_info()
        else:
            print_client_info()