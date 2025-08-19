import requests
import pandas as pd
from ..auth import BaseClient


class WorkspaceClient(BaseClient):
    """
    Workspace-related operations for Power BI.
    
    This class provides methods for managing and retrieving information
    about Power BI workspaces.
    """

    def get_workspace_by_id(self, workspace_id: str) -> pd.DataFrame:
        """
        Retrieve a specific Power BI workspace by its ID.   
        Args:
            workspace_id (str): The ID of the Power BI workspace.
        Returns:
            pd.DataFrame: DataFrame containing workspace metadata.
        """
        get_workspace_url = f"{self.base_url}/{workspace_id}"
        result = requests.get(url=get_workspace_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame([result.json()])
        return pd.DataFrame()

    def get_workspace_users_by_id(self, workspace_id: str) -> pd.DataFrame:
        """
        Get workspace users by workspace id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
        Returns:
            pd.DataFrame: DataFrame containing the workspace users.
        """
        get_workspace_users_url = f"{self.base_url}/{workspace_id}/users"
        result = requests.get(url=get_workspace_users_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame(result.json()["value"])
        return pd.DataFrame()

    def get_all_workspaces(self) -> pd.DataFrame:
        """
        Retrieve all Power BI workspaces accessible by the authenticated user.
        Returns:
            pd.DataFrame: A DataFrame containing metadata for all workspaces.
        """
        url = f"{self.base_url}"
        result = requests.get(url=url, headers=self.get_header())   
        if result.status_code == 200:
            df = pd.DataFrame(result.json()["value"])
            if not df.empty:
                df['id'] = df['id'].astype(str)  # Ensure workspace IDs are strings
            return df
        return pd.DataFrame()
