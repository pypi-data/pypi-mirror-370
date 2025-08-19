import requests
import pandas as pd
from ..auth import BaseClient
from ..utils import extract_connection_details


class ReportClient(BaseClient):
    """
    Report-related operations for Power BI.
    
    This class provides methods for managing and retrieving information
    about Power BI reports.
    """

    def get_report_by_id(self, workspace_id: str, report_id: str) -> pd.DataFrame:
        """
        Retrieve a specific report by its ID from a Power BI workspace.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            report_id (str): The ID of the Power BI report.
        Returns:
            pd.DataFrame: DataFrame containing report metadata.
        """
        get_report_url = f"{self.base_url}/{workspace_id}/reports/{report_id}"
        result = requests.get(url=get_report_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame([result.json()])
        return pd.DataFrame()

    def get_reports_by_id(self, workspace_id: str) -> pd.DataFrame:
        """
        Retrieve all reports in a specific Power BI workspace.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
        Returns:
            pd.DataFrame: DataFrame containing all reports in the specified workspace.
        """
        get_reports_url = f"{self.base_url}/{workspace_id}/reports"
        result = requests.get(url=get_reports_url, headers=self.get_header())
        if result.status_code == 200:
            return pd.DataFrame(result.json()["value"])
        return pd.DataFrame()

    def get_report_sources_by_id(self, workspace_id: str, report_id: str) -> pd.DataFrame:
        """
        Get report sources by report id.
        Args:
            workspace_id (str): The ID of the Power BI workspace.
            report_id (str): The ID of the Power BI report.
        Returns:
            pd.DataFrame: DataFrame containing the report sources with connection details.
        """
        get_report_source_url = f"{self.base_url}/{workspace_id}/reports/{report_id}/datasources"
        result = requests.get(url=get_report_source_url, headers=self.get_header())
        if result.status_code == 200:
            df = pd.DataFrame(result.json()["value"])
            if not df.empty:
                df[["server", "database", "connectionString", "url", "path"]] = df["connectionDetails"].apply(extract_connection_details)
            return df
        return pd.DataFrame()
