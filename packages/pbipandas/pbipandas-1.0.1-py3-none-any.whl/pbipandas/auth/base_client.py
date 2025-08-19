import requests


class BaseClient:
    """
    Base PowerBI Client Class for authentication and shared functionality.
    
    This class handles authentication and provides shared utilities for 
    interacting with the Power BI REST API.

    Attributes:
        tenant_id (str): Azure AD tenant ID.
        client_id (str): App's client ID registered in Azure.
        client_secret (str): App's client secret.
        access_token (str): Access token retrieved using client credentials.
        base_url (str): Base URL for Power BI API calls.
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize the client and retrieve an access token.

        Args:
            tenant_id (str): Azure AD tenant ID.
            client_id (str): Client/application ID.
            client_secret (str): Client/application secret.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.powerbi.com/v1.0/myorg/groups/"
        self.access_token = None

    def get_token(self) -> str:
        """
        Retrieve an OAuth2 access token for the Power BI REST API.

        Returns:
            str: The access token string.
        """
        # Grab token
        header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.microsoftonline.com:443",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": "https://analysis.windows.net/powerbi/api/.default",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        result = requests.post(
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
            headers=header,
            data=data,
        )

        token_data = result.json()

        self.access_token = token_data["access_token"]

        return self.access_token

    def get_header(self) -> dict:
        """
        Get the headers required for authenticated API calls.

        Returns:
            dict: Headers with content type and bearer token.
        """
        token = self.get_token()

        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }


