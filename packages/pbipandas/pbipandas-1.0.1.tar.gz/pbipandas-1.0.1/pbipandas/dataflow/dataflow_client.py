import requests
import pandas as pd
from ..auth import BaseClient
from ..utils import extract_connection_details


class DataflowClient(BaseClient):
    """
    Dataflow-related operations for Power BI.
    
    This class provides methods for managing dataflows, including refresh operations
    and retrieving dataflow metadata.
    """

    def get_dataflow_by_id(self, workspace_id: str, dataflow_id: str) -> pd.DataFrame:
        """
        Retrieve a specific dataflow by its ID from a Power BI workspace.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataflow_id (str): The ID of the Power BI dataflow.
        Returns:
            pd.DataFrame: DataFrame containing dataflow metadata.
        """
        get_dataflow_url = f"{self.base_url}/{workspace_id}/dataflows/{dataflow_id}"
        result = requests.get(url=get_dataflow_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame([result.json()])
        return pd.DataFrame()
    
    def get_dataflows_by_id(self, workspace_id: str) -> pd.DataFrame:
        """        
        Retrieve all dataflows in a specific Power BI workspace.
        
        Args:
            workspace_id (str): The ID of the Power BI workspace.                   
        Returns:    
            pd.DataFrame: DataFrame containing all dataflows in the specified workspace.
        """
        get_dataflows_url = f"{self.base_url}/{workspace_id}/dataflows"
        result = requests.get(url=get_dataflows_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame(result.json()["value"])
        return pd.DataFrame()
        

    def refresh_dataflow(self, workspace_id: str, dataflow_id: str) -> None:
        """
        Trigger a refresh for a specific dataflow.

        Args:
            workspace_id (str): The Power BI workspace ID.
            dataflow_id (str): The dataflow ID.
        """
        url = f"{self.base_url}/{workspace_id}/dataflows/{dataflow_id}/refreshes"
        result = requests.post(url, headers=self.get_header())
        if result.status_code == 200:
            print(f"Start refreshing dataflow {dataflow_id}")
        else:
            print(
                f"Failed to refresh dataflow {dataflow_id}. Status code: {result.status_code}"
            )

    def get_dataflow_refresh_history_by_id(self, workspace_id: str, dataflow_id: str) -> pd.DataFrame:
        """
        Get dataflow refresh history by dataflow id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataflow_id (str): The ID of the Power BI dataflow.
        Returns:
            pd.DataFrame: DataFrame containing the dataflow refresh history.
        """
        get_dataflow_refresh_history_url = f"{self.base_url}/{workspace_id}/dataflows/{dataflow_id}/transactions"
        result = requests.get(url=get_dataflow_refresh_history_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame(result.json()["value"])
        return pd.DataFrame()

    def get_dataflow_sources_by_id(self, workspace_id: str, dataflow_id: str) -> pd.DataFrame:
        """
        Get dataflow sources by dataflow id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataflow_id (str): The ID of the Power BI dataflow.
        Returns:
            pd.DataFrame: DataFrame containing the dataflow sources with connection details.
        """
        get_dataflow_source_url = f"{self.base_url}/{workspace_id}/dataflows/{dataflow_id}/datasources"
        result = requests.get(url=get_dataflow_source_url, headers=self.get_header())
        if result.status_code == 200:
            df = pd.DataFrame(result.json()["value"])
            if not df.empty:
                df[["server", "database", "connectionString", "url", "path"]] = df["connectionDetails"].apply(extract_connection_details)
            return df
        return pd.DataFrame()
