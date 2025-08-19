import requests
import pandas as pd
from ..auth import BaseClient
from ..utils import extract_connection_details


class DatasetClient(BaseClient):
    """
    Dataset-related operations for Power BI.
    
    This class provides methods for managing datasets, including refresh operations,
    parameter updates, and retrieving dataset metadata.
    """

    def get_dataset_by_id(self, workspace_id: str, dataset_id: str) -> pd.DataFrame:
        """
        Retrieve a specific dataset by its ID from a Power BI workspace.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            pd.DataFrame: DataFrame containing dataset metadata.
        """
        get_dataset_url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}"
        result = requests.get(url=get_dataset_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame([result.json()])
        return pd.DataFrame()

    def get_datasets_by_id(self, workspace_id: str) -> pd.DataFrame:
        """
        Retrieve all datasets in a specific Power BI workspace.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
        Returns:
            pd.DataFrame: DataFrame containing all datasets in the specified workspace.
        """
        get_datasets_url = f"{self.base_url}/{workspace_id}/datasets"
        result = requests.get(url=get_datasets_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame(result.json()["value"])
        return pd.DataFrame()

    def refresh_dataset(self, workspace_id: str, dataset_id: str, body: dict = None) -> None:
        """
        Trigger a refresh for a specific dataset.

        Args:
            workspace_id (str): The Power BI workspace ID.
            dataset_id (str): The dataset ID.
            body (dict): Optional request body for partial refresh.
        """
        url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/refreshes"
        
        result = requests.post(url, headers=self.get_header(), json=body)

        if result.status_code == 202:
            print(f"Start refreshing dataset {dataset_id}")
        else:
            print(
                f"Failed to refresh dataset {dataset_id}. Status code: {result.status_code}"
            )

    def refresh_tables_from_dataset(self, workspace_id: str, dataset_id: str, table_list: list) -> None:
        """
        Trigger a refresh for a specific list of table in a dataset.
        Args:
            workspace_id (str): The Power BI workspace ID.
            dataset_id (str): The dataset ID.
            table_list (list): The list of table names to refresh.
        """
        body = {
            "objects": [{"table": table} for table in table_list]
        }
        self.refresh_dataset(workspace_id, dataset_id, body)

    def refresh_objects_from_dataset(self, workspace_id: str, dataset_id: str, objects: list) -> None:
        """
        Trigger a refresh for specific objects in a dataset.
        Args:
            workspace_id (str): The Power BI workspace ID.
            dataset_id (str): The dataset ID.
            objects (list): A list of objects to refresh, e.g., [{"table": "Sales"}, {"table": "Customers", "partition": "Customers-2025"}]
        """
        body = {
            "objects": objects
        }
        self.refresh_dataset(workspace_id, dataset_id, body)

    def update_dataset_parameters(
        self, workspace_id: str, dataset_id: str, parameters: dict
    ) -> requests.Response:
        """
        Update parameters for a specific dataset.
        Args:
            workspace_id (str): The Power BI workspace ID.
            dataset_id (str): The dataset ID.
            parameters (dict): A dictionary of parameters to update.
        Returns:
            requests.Response: The HTTP response containing the result of the update operation.
        """
        url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/Default.UpdateParameters"
        body = {
            "updateDetails": [
                {
                    "name": key,
                    "newValue": value,
                }
                for key, value in parameters.items()
            ]
        }
        result = requests.post(url, headers=self.get_header(), json=body)
        return result

    def get_dataset_refresh_history_by_id(self, workspace_id: str, dataset_id: str, top_n: int = 10) -> pd.DataFrame:
        """
        Get dataset refresh history by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
            top_n (int): The number of most recent refreshes to retrieve. Default is 10.
        Returns:
            pd.DataFrame: DataFrame containing the dataset refresh history.
        """
        get_dataset_refresh_history_url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/refreshes?$top={top_n}"
        result = requests.get(url=get_dataset_refresh_history_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame(result.json()["value"])
        return pd.DataFrame()

    def execute_query(
        self, workspace_id: str, dataset_id: str, query: str
    ) -> requests.Response:
        """
        Execute a DAX query against a Power BI dataset.

        Args:
            workspace_id (str): The Power BI workspace ID.
            dataset_id (str): The dataset ID.
            query (str): The DAX query to execute.

        Returns:
            requests.Response: The HTTP response containing the query results.
        """
        url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/executeQueries"
        body = {
            "queries": [{"query": query}],
            "serializerSettings": {"includeNulls": True},
        }
        result = requests.post(url, headers=self.get_header(), json=body)
        return result

    def get_dataset_sources_by_id(self, workspace_id: str, dataset_id: str) -> pd.DataFrame:
        """
        Get dataset sources by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            pd.DataFrame: DataFrame containing the dataset sources with connection details.
        """
        get_dataset_source_url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/datasources"
        result = requests.get(url=get_dataset_source_url, headers=self.get_header())
        if result.status_code == 200:
            df = pd.DataFrame(result.json()["value"])
            if not df.empty:
                df[["server", "database", "connectionString", "url", "path"]] = df["connectionDetails"].apply(extract_connection_details)
            return df
        return pd.DataFrame()

    def get_dataset_users_by_id(self, workspace_id: str, dataset_id: str) -> pd.DataFrame:
        """
        Get dataset users by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            pd.DataFrame: DataFrame containing the dataset users.
        """
        get_dataset_users_url = f"{self.base_url}/{workspace_id}/datasets/{dataset_id}/users"
        result = requests.get(url=get_dataset_users_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame(result.json()["value"])
        return pd.DataFrame()

    def get_dataset_tables_by_id(self, workspace_id: str, dataset_id: str) -> pd.DataFrame:
        """
        Get dataset tables by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            pd.DataFrame: DataFrame containing the dataset tables metadata.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
        query_body = {
            "queries": [{"query": "EVALUATE INFO.VIEW.TABLES()"}],
            "serializerSettings": {"includeNulls": True},
        }
        result = requests.post(url, headers=self.get_header(), json=query_body)
        if result.status_code == 200:
            df = pd.DataFrame.from_dict(result.json()["results"][0]["tables"][0]["rows"])
            if not df.empty:
                df.columns = [col.replace('[', '').replace(']', '') for col in df.columns]
            return df
        return pd.DataFrame()

    def get_dataset_columns_by_id(self, workspace_id: str, dataset_id: str) -> pd.DataFrame:
        """
        Get dataset columns by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            pd.DataFrame: DataFrame containing the dataset columns metadata.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
        query_body = {
            "queries": [{"query": "EVALUATE INFO.VIEW.COLUMNS()"}],
            "serializerSettings": {"includeNulls": True},
        }
        result = requests.post(url, headers=self.get_header(), json=query_body)
        if result.status_code == 200:
            df = pd.DataFrame.from_dict(result.json()["results"][0]["tables"][0]["rows"])
            if not df.empty:
                df.columns = [col.replace('[', '').replace(']', '') for col in df.columns]
            return df
        return pd.DataFrame()

    def get_dataset_measures_by_id(self, workspace_id: str, dataset_id: str) -> pd.DataFrame:
        """
        Get dataset measures by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            pd.DataFrame: DataFrame containing the dataset measures metadata.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
        query_body = {
            "queries": [{"query": "EVALUATE INFO.VIEW.MEASURES()"}],
            "serializerSettings": {"includeNulls": True},
        }
        result = requests.post(url, headers=self.get_header(), json=query_body)

        if result.status_code == 200:
            df = pd.DataFrame.from_dict(result.json()["results"][0]["tables"][0]["rows"])
            if not df.empty:
                df.columns = [col.replace('[', '').replace(']', '') for col in df.columns]
            return df
        return pd.DataFrame()

    def get_dataset_calc_dependencies_by_id(self, workspace_id: str, dataset_id: str) -> pd.DataFrame:
        """
        Get dataset calculation dependencies by dataset id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            dataset_id (str): The ID of the Power BI dataset.
        Returns:
            pd.DataFrame: DataFrame containing the dataset calculation dependencies.
        """
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/executeQueries"
        query_body = {
            "queries": [{"query": "EVALUATE INFO.CALCDEPENDENCY()"}],
            "serializerSettings": {"includeNulls": True},
        }
        result = requests.post(url, headers=self.get_header(), json=query_body)
        if result.status_code == 200:
            df = pd.DataFrame.from_dict(result.json()["results"][0]["tables"][0]["rows"])
            if not df.empty:
                df.columns = [col.replace('[', '').replace(']', '') for col in df.columns]
            return df
        return pd.DataFrame()
