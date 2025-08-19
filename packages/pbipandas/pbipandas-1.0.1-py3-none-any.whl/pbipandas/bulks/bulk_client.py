import pandas as pd
from ..auth import BaseClient
from ..workspace.workspace_client import WorkspaceClient
from ..dataset.dataset_client import DatasetClient
from ..report.report_client import ReportClient
from ..dataflow.dataflow_client import DataflowClient


class BulkClient(BaseClient):
    """
    Bulk data retrieval operations for Power BI.
    
    This class provides methods for retrieving data in bulk from multiple
    Power BI objects across workspaces. It creates instances of individual
    clients to perform specific operations.
    """

    def get_all_datasets(self) -> pd.DataFrame:
        """
        Retrieve all datasets from all available Power BI workspaces.
        Returns:
            pd.DataFrame: A DataFrame containing dataset metadata, enriched with workspace context.
        """
        # Create instances of the individual clients
        workspace_client = WorkspaceClient(self.tenant_id, self.client_id, self.client_secret)
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_workspaces = workspace_client.get_all_workspaces()
        df_all_datasets = pd.DataFrame()

        for _, workspace in df_workspaces.iterrows():
            try:
                df = dataset_client.get_datasets_by_id(workspace['id'])
                if not df.empty:
                    df['workspaceId'] = workspace['id']
                    df['workspaceName'] = workspace['name']
                    df_all_datasets = pd.concat([df_all_datasets, df])
            except Exception as e:
                print(f"Error processing workspace {workspace['id']}: {e}")
                continue

        return df_all_datasets

    def get_all_dataflows(self) -> pd.DataFrame:
        """
        Retrieve all dataflows from all accessible Power BI workspaces.
        Returns:
            pd.DataFrame: A DataFrame containing dataflow metadata across all workspaces.
        """
        # Create instances of the individual clients
        workspace_client = WorkspaceClient(self.tenant_id, self.client_id, self.client_secret)
        dataflow_client = DataflowClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_workspaces = workspace_client.get_all_workspaces()
        df_all_dataflows = pd.DataFrame()

        for _, workspace in df_workspaces.iterrows():
            try:
                df = dataflow_client.get_dataflows_by_id(workspace['id'])
                if not df.empty:
                    df['workspaceId'] = workspace['id']
                    df['workspaceName'] = workspace['name']
                    df_all_dataflows = pd.concat([df_all_dataflows, df])
            except Exception as e:
                print(f"Error processing workspace {workspace['id']}: {e}")
                continue

        return df_all_dataflows

    def get_all_reports(self) -> pd.DataFrame:
        """
        Retrieve all reports from all accessible Power BI workspaces.
        Returns:
            pd.DataFrame: A DataFrame containing report metadata across all workspaces.
        """
        # Create instances of the individual clients
        workspace_client = WorkspaceClient(self.tenant_id, self.client_id, self.client_secret)
        report_client = ReportClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_workspaces = workspace_client.get_all_workspaces()
        df_all_reports = pd.DataFrame()

        for _, workspace in df_workspaces.iterrows():
            try:
                df = report_client.get_reports_by_id(workspace['id'])
                if not df.empty:
                    df['workspaceId'] = workspace['id']
                    df['workspaceName'] = workspace['name']
                    df_all_reports = pd.concat([df_all_reports, df])
            except Exception as e:
                print(f"Error processing workspace {workspace['id']}: {e}")
                continue

        return df_all_reports

    def get_all_dataset_refresh_history(self) -> pd.DataFrame:
        """
        Retrieve refresh history for all refreshable datasets.
        Returns:
            pd.DataFrame: A DataFrame containing refresh history for all datasets.
        """
        # Create instances of the individual clients
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_datasets = self.get_all_datasets()
        df_all_refresh_history = pd.DataFrame()
        
        refreshable_datasets = df_datasets[df_datasets['isRefreshable'] == 'True']
        
        for _, dataset in refreshable_datasets.iterrows():
            try:
                df = dataset_client.get_dataset_refresh_history_by_id(dataset['workspaceId'], dataset['id'])
                if not df.empty:
                    df['datasetId'] = dataset['id']
                    df['datasetName'] = dataset['name']
                    df['workspaceId'] = dataset['workspaceId']
                    df['workspaceName'] = dataset['workspaceName']
                    df_all_refresh_history = pd.concat([df_all_refresh_history, df])
            except Exception as e:
                print(f"Error processing dataset refresh history {dataset['id']}: {e}")
                continue

        return df_all_refresh_history

    def get_all_dataflow_refresh_history(self) -> pd.DataFrame:
        """
        Retrieve refresh history for all dataflows.
        Returns:
            pd.DataFrame: A DataFrame containing refresh history for all dataflows.
        """
        # Create instances of the individual clients
        dataflow_client = DataflowClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_dataflows = self.get_all_dataflows()
        df_all_refresh_history = pd.DataFrame()

        for _, dataflow in df_dataflows.iterrows():
            try:
                df = dataflow_client.get_dataflow_refresh_history_by_id(
                    dataflow['workspaceId'], 
                    dataflow['objectId']
                )
                if not df.empty:
                    df['dataflowId'] = dataflow['objectId']
                    df['dataflowName'] = dataflow['name']
                    df['workspaceId'] = dataflow['workspaceId']
                    df['workspaceName'] = dataflow['workspaceName']
                    df_all_refresh_history = pd.concat([df_all_refresh_history, df])
            except Exception as e:
                print(f"Error processing dataflow refresh history {dataflow['objectId']}: {e}")
                continue

        return df_all_refresh_history

    def get_all_dataset_users(self) -> pd.DataFrame:
        """
        Retrieve user access information for all datasets.
        Returns:
            pd.DataFrame: A DataFrame containing user access details for all datasets.
        """
        # Create instances of the individual clients
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_datasets = self.get_all_datasets()
        df_datasets = df_datasets[~df_datasets['name'].str.contains("Usage Metrics")]
        df_all_users = pd.DataFrame()

        for _, dataset in df_datasets.iterrows():
            try:
                df = dataset_client.get_dataset_users_by_id(dataset['workspaceId'], dataset['id'])
                if not df.empty:
                    df['datasetId'] = dataset['id']
                    df['datasetName'] = dataset['name']
                    df['workspaceId'] = dataset['workspaceId']
                    df['workspaceName'] = dataset['workspaceName']
                    df_all_users = pd.concat([df_all_users, df])
            except Exception as e:
                print(f"Error processing dataset users {dataset['id']}: {e}")
                continue

        return df_all_users

    def get_all_dataset_sources(self) -> pd.DataFrame:
        """
        Retrieve all data sources for all datasets.
        Returns:
            pd.DataFrame: A DataFrame containing data source details for all datasets.
        """
        # Create instances of the individual clients
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_datasets = self.get_all_datasets()
        df_datasets = df_datasets[~df_datasets['name'].str.contains("Usage Metrics")]
        df_all_sources = pd.DataFrame()

        for _, dataset in df_datasets.iterrows():
            try:
                df = dataset_client.get_dataset_sources_by_id(dataset['workspaceId'], dataset['id'])
                if not df.empty:
                    df['datasetId'] = dataset['id']
                    df['datasetName'] = dataset['name']
                    df['workspaceId'] = dataset['workspaceId']
                    df['workspaceName'] = dataset['workspaceName']
                    df_all_sources = pd.concat([df_all_sources, df])
            except Exception as e:
                print(f"Error processing dataset sources {dataset['id']}: {e}")
                continue

        return df_all_sources

    def get_all_dataflow_sources(self) -> pd.DataFrame:
        """
        Retrieve all data sources for all dataflows.
        Returns:
            pd.DataFrame: A DataFrame containing data source details for all dataflows.
        """
        # Create instances of the individual clients
        dataflow_client = DataflowClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_dataflows = self.get_all_dataflows()
        df_all_sources = pd.DataFrame()

        for _, dataflow in df_dataflows.iterrows():
            try:
                df = dataflow_client.get_dataflow_sources_by_id(
                    dataflow['workspaceId'], 
                    dataflow['objectId']
                )
                if not df.empty:
                    df['dataflowId'] = dataflow['objectId']
                    df['dataflowName'] = dataflow['name']
                    df['workspaceId'] = dataflow['workspaceId']
                    df['workspaceName'] = dataflow['workspaceName']
                    df_all_sources = pd.concat([df_all_sources, df])
            except Exception as e:
                print(f"Error processing dataflow sources {dataflow['objectId']}: {e}")
                continue

        return df_all_sources

    def get_all_report_sources(self) -> pd.DataFrame:
        """
        Retrieve all data sources for all reports.
        Returns:
            pd.DataFrame: A DataFrame containing data source details for all reports.
        """
        # Create instances of the individual clients
        report_client = ReportClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_reports = self.get_all_reports()
        df_all_sources = pd.DataFrame()

        for _, report in df_reports.iterrows():
            try:
                df = report_client.get_report_sources_by_id(report['workspaceId'], report['id'])
                if not df.empty:
                    df['reportId'] = report['id']
                    df['reportName'] = report['name']
                    df['workspaceId'] = report['workspaceId']
                    df['workspaceName'] = report['workspaceName']
                    df_all_sources = pd.concat([df_all_sources, df])
            except Exception as e:
                print(f"Error processing report sources {report['id']}: {e}")
                continue

        return df_all_sources

    def get_all_dataset_tables(self) -> pd.DataFrame:
        """
        Retrieve all tables from all datasets.
        Returns:
            pd.DataFrame: A DataFrame containing table metadata for all datasets.
        """
        # Create instances of the individual clients
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_datasets = self.get_all_datasets()
        df_all_tables = pd.DataFrame()

        for _, dataset in df_datasets.iterrows():
            try:
                df = dataset_client.get_dataset_tables_by_id(dataset['workspaceId'], dataset['id'])
                if not df.empty:
                    df['datasetId'] = dataset['id']
                    df['datasetName'] = dataset['name']
                    df['workspaceId'] = dataset['workspaceId']
                    df['workspaceName'] = dataset['workspaceName']
                    df_all_tables = pd.concat([df_all_tables, df])
            except Exception as e:
                print(f"Error processing dataset tables {dataset['id']}: {e}")
                continue

        return df_all_tables

    def get_all_dataset_columns(self) -> pd.DataFrame:
        """
        Retrieve all columns from all datasets.
        Returns:
            pd.DataFrame: A DataFrame containing column metadata for all datasets.
        """
        # Create instances of the individual clients
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_datasets = self.get_all_datasets()
        df_all_columns = pd.DataFrame()

        for _, dataset in df_datasets.iterrows():
            try:
                df = dataset_client.get_dataset_columns_by_id(dataset['workspaceId'], dataset['id'])
                if not df.empty:
                    df['datasetId'] = dataset['id']
                    df['datasetName'] = dataset['name']
                    df['workspaceId'] = dataset['workspaceId']
                    df['workspaceName'] = dataset['workspaceName']
                    df_all_columns = pd.concat([df_all_columns, df])
            except Exception as e:
                print(f"Error processing dataset columns {dataset['id']}: {e}")
                continue

        return df_all_columns

    def get_all_dataset_measures(self) -> pd.DataFrame:
        """
        Retrieve all measures from all datasets.
        Returns:
            pd.DataFrame: A DataFrame containing measure metadata for all datasets.
        """
        # Create instances of the individual clients
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_datasets = self.get_all_datasets()
        df_all_measures = pd.DataFrame()

        for _, dataset in df_datasets.iterrows():
            try:
                df = dataset_client.get_dataset_measures_by_id(dataset['workspaceId'], dataset['id'])
                if not df.empty:
                    df['datasetId'] = dataset['id']
                    df['datasetName'] = dataset['name']
                    df['workspaceId'] = dataset['workspaceId']
                    df['workspaceName'] = dataset['workspaceName']
                    df_all_measures = pd.concat([df_all_measures, df])
            except Exception as e:
                print(f"Error processing dataset measures {dataset['id']}: {e}")
                continue

        return df_all_measures

    def get_measures_for_dataset_ids_across_workspaces(self, dataset_id_list: list) -> pd.DataFrame:
        """
        Retrieve measures for a specific list of dataset IDs across all workspaces.
        
        Args:
            dataset_id_list (list): List of dataset IDs to retrieve measures for.
            
        Returns:
            pd.DataFrame: DataFrame containing measures from all specified datasets,
                         with additional columns for dataset_id, dataset_name, workspace_id, and workspace_name.
        """
        # Create instances of the individual clients
        workspace_client = WorkspaceClient(self.tenant_id, self.client_id, self.client_secret)
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_all_measures = pd.DataFrame()
        
        # Get all workspaces to search through
        df_workspaces = workspace_client.get_all_workspaces()
        
        for _, workspace in df_workspaces.iterrows():
            workspace_id = workspace['id']
            workspace_name = workspace['name']
            
            # Get datasets in this workspace
            try:
                df_datasets = dataset_client.get_dataset_by_id(workspace_id)
                if not df_datasets.empty:
                    # Filter to only the datasets we're interested in
                    matching_datasets = df_datasets[df_datasets['id'].isin(dataset_id_list)]
                    
                    for _, dataset in matching_datasets.iterrows():
                        try:
                            df_measures = dataset_client.get_dataset_measures_by_id(workspace_id, dataset['id'])
                            if not df_measures.empty:
                                df_measures['datasetId'] = dataset['id']
                                df_measures['datasetName'] = dataset['name']
                                df_measures['workspaceId'] = workspace_id
                                df_measures['workspaceName'] = workspace_name
                                df_all_measures = pd.concat([df_all_measures, df_measures])
                        except Exception as e:
                            print(f"Warning: Failed to retrieve measures for dataset {dataset['id']}: {str(e)}")
                            continue
            except Exception as e:
                print(f"Warning: Failed to retrieve datasets for workspace {workspace_id}: {str(e)}")
                continue
        
        return df_all_measures

    def get_all_dataset_calc_dependencies(self) -> pd.DataFrame:
        """
        Retrieve all calculation dependencies from all datasets.
        Returns:
            pd.DataFrame: A DataFrame containing calculation dependency metadata for all datasets.
        """
        # Create instances of the individual clients
        dataset_client = DatasetClient(self.tenant_id, self.client_id, self.client_secret)
        
        df_datasets = self.get_all_datasets()
        df_all_dependencies = pd.DataFrame()

        for _, dataset in df_datasets.iterrows():
            try:
                df = dataset_client.get_dataset_calc_dependencies_by_id(dataset['workspaceId'], dataset['id'])
                if not df.empty:
                    df['datasetId'] = dataset['id']
                    df['datasetName'] = dataset['name']
                    df['workspaceId'] = dataset['workspaceId']
                    df['workspaceName'] = dataset['workspaceName']
                    df_all_dependencies = pd.concat([df_all_dependencies, df])
            except Exception as e:
                print(f"Error processing dataset calc dependencies {dataset['id']}: {e}")
                continue

        return df_all_dependencies
