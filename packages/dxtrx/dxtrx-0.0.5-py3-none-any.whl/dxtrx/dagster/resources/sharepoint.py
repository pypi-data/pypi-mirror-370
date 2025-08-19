import os
import requests
import dagster as dg

from typing import Optional
from datetime import datetime
from dataclasses import field
from pydantic import BaseModel
from msal import ConfidentialClientApplication

from dxtrx.utils.hash import hash_object_sha256

# Default configuration values for SharePoint API interaction
DEFAULT_SHAREPOINT_SCOPES = ["https://graph.microsoft.com/.default"]
DEFAULT_MS_AUTHORITY_BASE_URL = "https://login.microsoftonline.com"
DEFAULT_MS_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0/sites"

class SharePointFile(BaseModel):
    """
    Represents a file in SharePoint with its metadata and location information.
    
    Attributes:
        id (str): Unique identifier of the file in SharePoint
        queried_at (datetime): Timestamp when the file was queried
        payload (dict): Raw file metadata from SharePoint
        full_file_path (str): Complete path to the file including prefix
        prefix_relative_file_path (str): Path relative to the prefix folder
        query_execution_hash (str): Hash of the query execution context
        query_hash (str): Hash of the query parameters
    """
    id: str
    queried_at: datetime
    payload: dict
    full_file_path: str
    prefix_relative_file_path: str
    query_execution_hash: str
    query_hash: str

class SharePointFileListQueryExecutionSummary(BaseModel):
    """
    Summary information about a file list query execution.
    
    Attributes:
        query_items_found (Optional[int]): Number of items found in the query
        query_execution_start_ts (datetime): When the query started
        query_execution_end_ts (Optional[datetime]): When the query ended
    """
    query_items_found: Optional[int] = None
    query_execution_start_ts: datetime
    query_execution_end_ts: Optional[datetime] = None

class SharePointFileListQueryParameters(BaseModel):
    """
    Parameters used for querying files in SharePoint.
    
    Attributes:
        sharepoint_drive_base_url (str): Base URL for the SharePoint drive
        sharepoint_drive_prefix_folder_name (str): Prefix folder name for the query
    """
    sharepoint_drive_base_url: str
    sharepoint_drive_prefix_folder_name: str
    
class SharePointFileListQueryResults(BaseModel):
    """
    Complete results of a SharePoint file list query.
    
    Attributes:
        parameters (SharePointFileListQueryParameters): Query parameters used
        execution_summary (SharePointFileListQueryExecutionSummary): Execution details
        query_hash (str): Hash of the query parameters
        query_execution_hash (str): Hash of the execution context
        results (list[SharePointFile]): List of files found
    """
    parameters: SharePointFileListQueryParameters
    execution_summary: SharePointFileListQueryExecutionSummary
    query_hash: str
    query_execution_hash: str
    results: list[SharePointFile]

    def get_query_summary(self):
        """Returns a summary of the query excluding the results list."""
        return {k: v for k, v in self.model_dump().items() if k != "results"}


class SharePointDriveResource(dg.ConfigurableResource):
    """
    A resource for interacting with Microsoft SharePoint through the Graph API.
    Provides functionality for authentication, file listing, and downloading.
    
    Attributes:
        client_id (str): Azure app registration client ID
        client_secret (str): Azure app registration client secret
        tenant_id (str): Azure AD tenant ID
        site_id (str): SharePoint site ID
        drive_id (str): SharePoint drive ID (document library)
        scopes (list[str]): OAuth scopes for API access
        authority_base_url (str): Base URL for Microsoft authority
        graph_base_url (str): Base URL for Microsoft Graph API
        default_prefix_folder_name (str): Default prefix folder name for operations
    """

    client_id: str
    client_secret: str
    tenant_id: str
    site_id: str
    drive_id: str
    scopes: list[str] = field(default_factory=lambda: DEFAULT_SHAREPOINT_SCOPES)

    # overrideable defaults
    authority_base_url: str = field(default_factory=lambda: DEFAULT_MS_AUTHORITY_BASE_URL)
    graph_base_url: str = field(default_factory=lambda: DEFAULT_MS_GRAPH_BASE_URL)
    default_prefix_folder_name: str = field(default_factory=lambda: "")

    def setup_for_execution(self, context: dg.InitResourceContext):  
        """
        Initializes the SharePoint resource for execution with a logger and MS Graph API client.
        
        Args:
            context (dg.InitResourceContext): Dagster resource initialization context
        """
        self._app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"{self.authority_base_url}/{self.tenant_id}"
        )
        self._logger = dg.get_dagster_logger("sharepoint")

    def get_access_token(self) -> str:
        """
        Obtains an access token from Microsoft Graph API for authentication.
        
        Returns:
            str: Access token for API requests
            
        Raises:
            Exception: If token acquisition fails
        """
        if hasattr(self, "_access_token"):
            return self._access_token

        token_response = self._app.acquire_token_for_client(scopes=self.scopes)
        try:
            self._access_token = token_response["access_token"]
            self._logger.info("Authenticated successfully with Microsoft Graph!")
            return self._access_token
        
        except Exception as e:
            self._logger.error(f"Failed to obtain access token: {token_response.get('error')}")
            raise e

    def get_site_base_url(self,
                          site_id: Optional[str] = None,
                          graph_base_url: Optional[str] = "https://graph.microsoft.com/v1.0") -> str:
        """
        Constructs the base URL for a SharePoint site.
        
        Args:
            site_id (Optional[str]): SharePoint site ID, defaults to instance site_id
            graph_base_url (Optional[str]): Graph API base URL
            
        Returns:
            str: Complete site base URL
        """
        if site_id is None:
            site_id = self.site_id
        if graph_base_url is None:
            graph_base_url = self.graph_base_url

        return f"{graph_base_url}/sites/{site_id}"
    
    def get_drive_base_url(self,
                           site_id: Optional[str] = None,
                           drive_id: Optional[str] = None,
                           graph_base_url: Optional[str] = "https://graph.microsoft.com/v1.0") -> str:
        """
        Constructs the base URL for a SharePoint drive.
        
        Args:
            site_id (Optional[str]): SharePoint site ID
            drive_id (Optional[str]): SharePoint drive ID
            graph_base_url (Optional[str]): Graph API base URL
            
        Returns:
            str: Complete drive base URL
        """
        if site_id is None:
            site_id = self.site_id
        if drive_id is None:
            drive_id = self.drive_id
        if graph_base_url is None:
            graph_base_url = self.graph_base_url

        return f"{self.get_site_base_url(site_id=site_id, graph_base_url=graph_base_url)}/drives/{drive_id}"
    
    def get_headers(self) -> dict:
        """Returns headers with authentication token for API requests.
        
        Returns:
            dict: Headers with authentication token
        """
        return {
            "Authorization": f"Bearer {self.get_access_token()}"
        }

    def list_files(self,
                    extension_whitelist: Optional[list[str]] = ['xls', 'xlsb', 'xlsx'], 
                    override_prefix_folder_name: Optional[str] = None, 
                    override_drive_base_url: Optional[str] = None) -> SharePointFileListQueryResults:
        """
        Recursively lists files in a SharePoint folder structure.
        
        Args:
            extension_whitelist (Optional[list[str]]): List of allowed file extensions
            override_prefix_folder_name (Optional[str]): Override for default prefix folder
            override_drive_base_url (Optional[str]): Override for default drive base URL
            
        Returns:
            SharePointFileListQueryResults: Query results including file list and metadata
        """
        _extension_whitelist = [ext.lower() for ext in extension_whitelist]
        prefix_folder_name = self.default_prefix_folder_name if override_prefix_folder_name is None else override_prefix_folder_name
        drive_base_url = self.get_drive_base_url() if override_drive_base_url is None else override_drive_base_url
        files_list = []

        query_parameters = SharePointFileListQueryParameters(
            sharepoint_drive_base_url=drive_base_url,
            sharepoint_drive_prefix_folder_name=prefix_folder_name,
        )
        query_hash = hash_object_sha256(query_parameters.model_dump())

        query_execution_summary = SharePointFileListQueryExecutionSummary(
            query_items_found=0,
            query_execution_start_ts=datetime.now(),
            query_execution_end_ts=None
        )
        query_execution_hash = hash_object_sha256([query_parameters.model_dump(), str(query_execution_summary.query_execution_start_ts)])

        # Función recursiva para recorrer carpetas
        def traverse_folder(url, current_path=""):
            full_folder_path = f"{prefix_folder_name}/{current_path}"
            try:
                response = requests.get(url, headers=self.get_headers())
                response.raise_for_status()
                items = response.json()
                if 'value' not in items or not items['value']:
                    self._logger.debug("No se encontraron elementos en la carpeta actual.")
                else:
                    for item in items.get('value', []):
                        if "folder" in item:
                            # Si es una carpeta, hacer la llamada recursiva
                            self._logger.info(f"Entrando en carpeta: {item['name']}")

                            subfolder_path = os.path.join(current_path, item['name'])
                            subfolder_url = f"{drive_base_url}/items/{item['id']}/children"

                            traverse_folder(subfolder_url, subfolder_path)
                        elif "file" in item and item["name"].split(".")[-1].lower() in _extension_whitelist:
                            # Si es un archivo, agregarlo a la lista
                            self._logger.debug(f"Archivo encontrado: {item['name']} en {current_path}")

                            prefix_relative_file_path = os.path.join(current_path, item['name'])
                            full_file_path = os.path.join(full_folder_path, item['name'])  # Ruta completa desde la raíz de SharePoint

                            sharepoint_file = SharePointFile(
                                id=item["id"],
                                payload=item,
                                full_file_path=full_file_path,
                                prefix_relative_file_path=prefix_relative_file_path,
                                query_execution_hash=query_execution_hash,
                                query_hash=query_hash,
                                queried_at=datetime.now()
                            )

                            files_list.append(sharepoint_file)
                            
            except requests.exceptions.HTTPError as e:
                self._logger.error(f"HTTPError: {e}")
            except Exception as e:
                self._logger.error(f"Error durante la navegación de la carpeta: {e}")
        # Iniciar la navegación desde la carpeta base
        traverse_folder(f"{drive_base_url}/root:/{prefix_folder_name}:/children")

        # TODO: Rehacer filtros
        #final_list = []
        #for record in files_list:
        #    extension = record["file_name"].split(".")[-1].lower()
        #    if extension in extension_whitelist:
        #        final_list.append(record)

        query_execution_summary.query_execution_end_ts = datetime.now()
        query_execution_summary.query_items_found = len(files_list)

        return SharePointFileListQueryResults(
            query_hash=query_hash,
            query_execution_hash=query_execution_hash,
            parameters=query_parameters,
            execution_summary=query_execution_summary,
            results=files_list
        )