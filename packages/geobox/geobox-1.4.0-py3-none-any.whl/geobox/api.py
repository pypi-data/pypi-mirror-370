import requests
import logging
import os
from urllib.parse import urljoin
from typing import Dict, List, Union
from datetime import datetime

from .exception import AuthenticationError, ApiRequestError, NotFoundError, ValidationError, ServerError, AuthorizationError
from .vectorlayer import VectorLayer, LayerType
from .feature import Feature
from .utils import join_url_params
from .file import File
from .task import Task
from .view import VectorLayerView
from .tileset import Tileset
from .raster import Raster
from .mosaic import Mosaic
from .model3d import Model
from .map import Map
from .user import User, UserRole, UserStatus, Session
from .query import Query
from .workflow import Workflow
from .layout import Layout
from .version import VectorLayerVersion
from .tile3d import Tile3d
from .settings import SystemSettings
from .scene import Scene
from .route import Routing
from .plan import Plan
from .dashboard import Dashboard
from .basemap import Basemap
from .attachment import Attachment, AttachmentResourceType
from .apikey import ApiKey
from .log import Log
from .usage import Usage, UsageScale, UsageParam

logger = logging.getLogger(__name__)

class HttpMethods:
    """
    A class to represent HTTP methods.
    """
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'


class _RequestSession(requests.Session):
    """A custom session class that maintains headers and authentication state."""
    
    def __init__(self, access_token=None):
        """
        Initialize the session with authentication.
        
        Args:
            access_token (str, optional): Bearer token for authentication
            apikey (str, optional): API key for authentication
        """
        super().__init__()
        self.access_token = access_token
        self.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'

    def update_access_token(self, access_token: str) -> None:
        """
        Update the access token of the session.

        Args:
            access_token (str): The new access token

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> client.update_access_token(access_token="new_access_token")
        """
        self.access_token = access_token
        self.headers['Authorization'] = f'Bearer {self.access_token}'
    
    def _manage_headers_for_request(self, files=None, is_json=True) -> str:
        """
        Manages headers for different types of requests.
        
        Args:
            files (dict, optional): Files to upload
            is_json (bool, optional): Whether payload is JSON
            
        Returns:
            str: Original content type if it was modified
        """
        original_content_type = None
        
        if files:
            original_content_type = self.headers.get('Content-Type')
            if 'Content-Type' in self.headers:
                del self.headers['Content-Type']
        elif not is_json:
            original_content_type = self.headers.get('Content-Type')
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
        return original_content_type
            
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Override request method with header management.
        
        Args:
            method (str): HTTP method
            url (str): Request URL
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response: Response object

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> client.request(method="GET", url="https://api.geobox.ir/v1/layers/")
        """
        files = kwargs.get('files')
        is_json = 'json' in kwargs
        
        original_content_type = self._manage_headers_for_request(files, is_json)
        
        # Create a copy of headers to pass to the request
        request_headers = self.headers.copy()
        kwargs['headers'] = request_headers
        
        try:
            response = super().request(method, url, **kwargs)
        finally:
            if original_content_type:
                self.headers['Content-Type'] = original_content_type
                
        return response


class GeoboxClient:
    """
    A class to interact with the Geobox API.
    """

    def __init__(self,
                host: str = 'https://api.geobox.ir',
                ver: str = 'v1/',
                username: str = None,
                password: str = None,
                access_token: str = None, 
                apikey: str = None):
        """
        Constructs all the necessary attributes for the Api object.

        You can set these parameters in the environment variables to avoid passing them as arguments:
            - GEOBOX_USERNAME
            - GEOBOX_PASSWORD
            - GEOBOX_ACCESS_TOKEN
            - GEOBOX_APIKEY
            - DEBUG
        
        You can set the DEBUG to True to set the logging level to DEBUG.
            
        Args:
            host (str): API host URL
            ver (str): API version
            username (str, optional): Username for authentication
            password (str, optional): Password for authentication
            access_token (str, optional): Bearer token for authentication
            apikey (str, optional): API key for authentication

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient(host="https://api.geobox.ir", ver="v1/", 
                                        username="username", 
                                        password="password")
            >>> client = GeoboxClient(apikey="apikey")
            >>> client = GeoboxClient(access_token="access_token")
        """
        self.username = os.getenv('GEOBOX_USERNAME') if os.getenv('GEOBOX_USERNAME') else username
        self.password = os.getenv('GEOBOX_PASSWORD') if os.getenv('GEOBOX_PASSWORD') else password
        self.access_token = os.getenv('GEOBOX_ACCESS_TOKEN') if os.getenv('GEOBOX_ACCESS_TOKEN') else access_token
        self.apikey = os.getenv('GEOBOX_APIKEY') if os.getenv('GEOBOX_APIKEY') else apikey

        self.session = _RequestSession(access_token=self.access_token)

        host = host.lower()
        self.base_url = urljoin(host, ver)
        
        # Check input conditions
        if not self.access_token:
            if not self.apikey:
                if self.username and self.password:
                    self.access_token = self.get_access_token()
                    self.session.update_access_token(self.access_token)
                else:
                    raise ValueError("Please provide either username/password, apikey or access_token.")

        
    def __repr__(self) -> str:
        """
        Return a string representation of the GeoboxClient object.

        Returns:
            str: A string representation of the GeoboxClient object.
        """
        if self.access_token and not self.username:
            return f"GeoboxClient(access_token={self.access_token[:20] + '...' if len(self.access_token) > 20 else self.access_token})"
        elif self.apikey:
            return f"GeoboxClient(apikey={self.apikey[:20] + '...' if len(self.apikey) > 20 else self.apikey})"
        elif self.username:
            return f"GeoboxClient(username={self.username[:20] + '...' if len(self.username) > 20 else self.username})"


    def get_access_token(self) -> str:
        """
        Obtains an access token using the username and password.

        Returns:
            str: The access token.

        Raises:
            AuthenticationError: If there is an error obtaining the access token.
        """
        url = urljoin(self.base_url, "auth/token/")
        data = {"username": self.username, "password": self.password}
        try:
            response = requests.post(url, data=data)
            response_data = response.json()     
            if response.status_code == 200:
                return response_data["access_token"]
            else:
                raise AuthenticationError(f"Error obtaining access token: {response_data}")
            
        except Exception as e:
            raise AuthenticationError(f"Error obtaining access token: {e}")


    def _parse_error_message(self, response: requests.Response) -> str:
        """
        Parse error message from API response.

        Args:
            response (requests.Response): The API response object.

        Returns:
            str: The parsed error message.
        """
        detail = response.json().get('detail')
        
        if not detail:
            return str(response.json())
            
        if isinstance(detail, list) and len(detail) == 1:
            error = detail[0]
            error_msg = error.get('msg', '')
            loc = error.get('loc', [])
            
            if loc and len(loc) >= 2:
                return f'{error_msg}: "{loc[-1]}"'
            return error_msg
            
        if isinstance(detail, dict):
            return detail.get('msg', str(detail))
            
        return str(detail)


    def _handle_error(self, response: requests.Response) -> None:
        """
        Handle API error response.

        Args:
            response (requests.Response): The API response object.

        Raises:
            AuthenticationError: If authentication fails (401)
            AuthorizationError: If access is forbidden (403)
            NotFoundError: If resource is not found (404)
            ValidationError: If request validation fails (422)
            ServerError: If server error occurs (500+)
        """
        error_msg = self._parse_error_message(response)
        
        if response.status_code == 401:
            raise AuthenticationError(f'Invalid Authentication: {error_msg}')
        elif response.status_code == 403:
            raise AuthorizationError(f'Access forbidden: {error_msg}')
        elif response.status_code == 404:
            raise NotFoundError(f'Resource not found: {error_msg}')
        elif response.status_code == 422:
            raise ValidationError(error_msg)
        elif response.status_code >= 500:
            raise ServerError(error_msg)
        else:
            raise ApiRequestError(f"API request failed: {error_msg}")


    def _make_request(self,
                method: str,
                endpoint: str,
                payload=None,
                is_json=True,
                files=None,
                stream=None) -> dict:
        """
        Makes an HTTP request to the API using the session.
        
        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            payload (dict, optional): Request payload
            is_json (bool, optional): Whether payload is JSON
            files (dict, optional): Files to upload
            stream (bool, optional): Whether to stream response
        """
        url = urljoin(self.base_url, endpoint)
        
        if not self.access_token and self.apikey:
            url = join_url_params(url, {'apikey': self.apikey})

        try:
            if files:
                response = self.session.request(method, url, data=payload, files=files)
            elif is_json:
                response = self.session.request(method, url, json=payload)
            else:
                response = self.session.request(method, url, data=payload)
                
        except requests.exceptions.Timeout as e:
            raise ApiRequestError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(f"Request failed: {e}")

        # Failure responses
        if response.status_code in [401, 403, 404, 422, 500]:
            self._handle_error(response)

        # Log success responses
        if response.status_code == 200:
            logger.info("Request successful: Status code 200")
        elif response.status_code == 201:
            logger.info("Resource created successfully: Status code 201")
        elif response.status_code == 202:
            logger.info("Request accepted successfully: Status code 202")
        elif response.status_code == 203:
            logger.info("Non-authoritative information: Status code 203")
        elif response.status_code == 204:
            logger.info("Deleted, operation successful: Status code 204")

        try:
            if stream:
                return response
            else:
                return response.json()
        except:
            return None
                

    def get(self, endpoint: str, stream: bool = False) -> Dict:
        """
        Sends a GET request to the API.

        Args:
            endpoint (str): The API endpoint.

        Returns:
            Dict: The response data.
        """
        return self._make_request(HttpMethods.GET, endpoint, stream=stream)


    def post(self, endpoint: str, payload: Dict = None, is_json: bool = True, files=None) -> Dict:
        """
        Sends a POST request to the API.

        Args:
            endpoint (str): The API endpoint.
            payload (Dict, optional): The data to send with the request.
            is_json (bool, optional): Whether the payload is in JSON format.

        Returns:
            Dict: The response data.
        """
        return self._make_request(HttpMethods.POST, endpoint, payload, is_json, files=files)


    def put(self, endpoint: str, payload: Dict, is_json: bool = True) -> Dict:
        """
        Sends a PUT request to the API.

        Args:
            endpoint (str): The API endpoint.\n
            payload (Dict): The data to send with the request.\n
            is_json (bool, optional): Whether the payload is in JSON format.

        Returns:
            Dict: The response data.
        """
        return self._make_request(HttpMethods.PUT, endpoint, payload, is_json)


    def delete(self, endpoint: str, payload: Dict = None, is_json: bool = None) -> Dict:
        """
        Sends a DELETE request to the API.

        Args:
            endpoint (str): The API endpoint.

        Returns:
            Dict: The response data.
        """
        return self._make_request(HttpMethods.DELETE, endpoint, payload, is_json)


    def get_vectors(self, **kwargs) -> Union[List['VectorLayer'], int]:
        """
        Get a list of vector layers with optional filtering and pagination.
        
        Keyword Args:
            include_settings (bool): Whether to include layer settings. Default is False.
            temporary (bool): Whether to return temporary layers, default is False
            q (str): Query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): Search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): Comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of layers to skip. default is 0.
            limit (int): Maximum number of layers to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared layers. default is False.
                
        Returns:
            List[VectorLayer] | int: A list of VectorLayer instances or the layers count if return_count is True.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layers = client.get_vectors(include_settings=True, 
            ...                                 skip=0, 
            ...                                 limit=100, 
            ...                                 return_count=False, 
            ...                                 search="my_layer",
            ...                                 search_fields="name, description",
            ...                                 order_by="name",
            ...                                 shared=True)
        """
        return VectorLayer.get_vectors(self, **kwargs)
    

    def get_vector(self, uuid: str, user_id: int = None) -> 'VectorLayer':
        """
        Get a specific vector layer by its UUID.
        
        Args:
            uuid (str): The UUID of the layer to retrieve.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            VectorLayer: The requested layer instance.
            
        Raises:
            NotFoundError: If the layer with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
        """
        return VectorLayer.get_vector(self, uuid, user_id)
    

    def get_vectors_by_ids(self, ids: List[int], user_id: int = None, include_settings: bool = False) -> List['VectorLayer']:
        """
        Get vector layers by their IDs.

        Args:
            ids (List[int]): The IDs of the layers to retrieve.
            user_id (int, optional): Specific user. privileges required.
            include_settings (bool, optional): Whether to include the layer settings. default is False.

        Returns:
            List[VectorLayer]: The list of VectorLayer instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layers = client.get_vectors_by_ids(ids=[1, 2, 3])
        """
        return VectorLayer.get_vectors_by_ids(self, ids, user_id, include_settings)


    def create_vector(self, 
                     name: str, 
                     layer_type: 'LayerType', 
                     display_name: str = None, 
                     description: str = None,
                     has_z: bool = False,
                     temporary: bool = False,
                     fields: List = None) -> 'VectorLayer':
        """
        Create a new vector layer.
        
        Args:
            name (str): The name of the layer.
            layer_type (LayerType): The type of geometry to store.
            display_name (str, optional): A human-readable name for the layer. default is None.
            description (str, optional): A description of the layer. default is None.
            has_z (bool, optional): Whether the layer includes Z coordinates. default is False.
            temporary (bool, optional): Whether to create a temporary layer. temporary layers will be deleted after 24 hours. default is False.
            fields (List, optional): List of field definitions for the layer. default is None.
            
        Returns:
            VectorLayer: The newly created layer instance.
            
        Raises:
            ValidationError: If the layer data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.create_vector(name="my_layer", 
            ...                                 layer_type=LayerType.Point,
            ...                                 display_name="My Layer",
            ...                                 description="This is a description of my layer",
            ...                                 has_z=False,
            ...                                 fields=[{"name": "my_field", "datatype": "FieldTypeString"}])
        """
        return VectorLayer.create_vector(self, name=name, layer_type=layer_type, display_name=display_name, description=description, has_z=has_z, temporary=temporary, fields=fields)


    def get_vector_by_name(self, name: str, user_id: int = None) -> Union['VectorLayer', None]:
        """
        Get a vector layer by name

        Args:
            name (str): the name of the vector to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            VectorLayer | None: returns the vector if a vector matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector_by_name(name='test')
        """
        return VectorLayer.get_vector_by_name(self, name, user_id)
    

    def get_files(self, **kwargs) -> Union[List['File'], int]:
        """
        Retrieves a list of files.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D.NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if true, the total number of results will be returned. default is False.
            skip (int): number of results to skip. default is 0.
            limit (int): number of results to return. default is 10.
            user_id (int): filter by user id.
            shared (bool): Whether to return shared files. default is False.
            
        Returns:
            List[File] | int: A list of File objects or the total number of results.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> files = client.get_files(search_fields='name', search='GIS', order_by='name', skip=10, limit=10)
        """
        return File.get_files(self, **kwargs)


    def get_file(self, uuid: str) -> 'File':
        """
        Retrieves a file by its UUID.

        Args:
            uuid (str, optional): The UUID of the file.

        Returns:
            File: The retrieved file instance.

        Raises:
            NotFoundError: If the file with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file = client.get_file(uuid="12345678-1234-5678-1234-567812345678")
        """
        return File.get_file(self, uuid=uuid)
    

    def get_files_by_name(self, name: str, user_id: int = None) -> List['File']:
        """
        Get files by name

        Args:
            name (str): the name of the file to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[File]: returns files that matches the given name

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> files = client.get_files_by_name(name='test')
        """
        return File.get_files_by_name(self, name, user_id)


    def upload_file(self, path: str, user_id: int = None, scan_archive: bool = True) -> 'File':
        """
        Upload a file to the GeoBox API.

        Args:
            path (str): The path to the file to upload.
            user_id (int, optional): specific user. privileges required.
            scan_archive (bool, optional): Whether to scan the archive for layers. default: True

        Returns:
            File: The uploaded file instance.

        Raises:
            ValueError: If the file type is invalid.
            FileNotFoundError: If the file does not exist.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file = client.upload_file(path='path/to/file.shp')
        """
        return File.upload_file(self, path=path, user_id=user_id, scan_archive=scan_archive)


    def get_tasks(self, **kwargs) -> Union[List['Task'], int]:
        """
        Get a list of tasks

        Keyword Args:
            state (TaskStatus): Available values : TaskStatus.PENDING, TaskStatus.PROGRESS, TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.ABORTED
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): The count of the tasks. default is False.
            skip (int): The skip of the task. default is 0.
            limit (int): The limit of the task. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared tasks. default is False.

        Returns:
            List[Task] | int: The list of task objects or the count of the tasks if return_count is True.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tasks = client.get_tasks()
        """
        return Task.get_tasks(self, **kwargs)


    def get_task(self, uuid: str) -> 'Task':
        """
        Gets a task.

        Args:
            uuid (str): The UUID of the task.

        Returns:
            Task: The task object.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> task = client.get_task(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Task.get_task(self, uuid)


    def get_views(self, **kwargs) -> Union[List['VectorLayerView'], int]:
        """
        Get vector layer views.

        Keyword Args:
            layer_id(int): The id of the layer.
            include_settings(bool): Whether to include the settings of the layer. default is False.
            q(str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search(str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields(str): Comma separated list of fields for searching.
            order_by(str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count(bool): Whether to return the count of the layer views. default is False.
            skip(int): The number of layer views to skip. minimum is 0.
            limit(int): The maximum number of layer views to return. minimum is 1. default is 10.
            user_id(int): Specific user. privileges required.
            shared(bool): Whether to return shared views. default is False.

        Returns:
            list[VectorLayerView] | int: A list of VectorLayerView instances or the layer views count if return_count is True.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> views = client.get_views(layer_id=1,
                                            include_settings=True,
                                            search="test",
                                            search_fields="name",
                                            order_by="name A",
                                            return_count=False,
                                            skip=0,
                                            limit=10,
                                            shared=True)
        """
        return VectorLayerView.get_views(self, **kwargs)


    def get_views_by_ids(self, ids: List[int], user_id: int = None, include_settings: bool = False) -> List['VectorLayerView']:
        """
        Get vector layer views by their IDs.

        Args:
            ids (List[int]): list of comma separated layer ids to be returned. e.g. 1, 2, 3
            user_id (int, optional): specific user. privileges required.
            include_settings (bool, optional): Whether to include the settings of the vector layer views. default is False.

        Returns:
            List[VectorLayerView]: A list of VectorLayerView instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> views = client.get_views_by_ids(ids=[1,2,3])
        """
        return VectorLayerView.get_views_by_ids(self, ids, user_id, include_settings)
    

    def get_view(self, uuid: str) -> 'VectorLayerView':
        """
        Get a specific vector layer view by its UUID.

        Args:
            uuid (str): The UUID of the vector layer view.
            user_id (int, optional): Specific user. privileges required.

        Returns:    
            VectorLayerView: A VectorLayerView instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> view = client.get_view(uuid="12345678-1234-5678-1234-567812345678")
        """
        return VectorLayerView.get_view(self, uuid)


    def get_view_by_name(self, name: str, user_id: int = None) -> Union['VectorLayerView', None]:
        """
        Get a view by name

        Args:
            name (str): the name of the view to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            VectorLayerView | None: returns the view if a view matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> view = client.get_view_by_name(name='test')
        """
        return VectorLayerView.get_view_by_name(self, name, user_id)


    def create_tileset(self, name: str, layers: List[Union['VectorLayer', 'VectorLayerView']], display_name: str = None, description: str = None,
                        min_zoom: int = None, max_zoom: int = None, user_id: int = None) -> 'Tileset':
        """
        Create a new tileset.

        Args:
            name (str): The name of the tileset.
            layers (List['VectorLayer' | 'VectorLayerView']): list of vectorlayer and view objects to add to tileset.
            display_name (str, optional): The display name of the tileset.
            description (str, optional): The description of the tileset.
            min_zoom (int, optional): The minimum zoom level of the tileset.
            max_zoom (int, optional): The maximum zoom level of the tileset.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Tileset: The created tileset instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> view = client.get_view(uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset = client.create_tileset(name="your_tileset_name", 
            ...                                     display_name="Your Tileset", 
            ...                                     description="Your description", 
            ...                                     min_zoom=0, 
            ...                                     max_zoom=14, 
            ...                                     layers=[layer, view])
        """
        return Tileset.create_tileset(api=self, 
                                      name=name, 
                                      layers=layers, 
                                      display_name=display_name, 
                                      description=description, 
                                      min_zoom=min_zoom, 
                                      max_zoom=max_zoom, 
                                      user_id=user_id)


    def get_tilesets(self, **kwargs) -> Union[List['Tileset'], int]:
        """
        Retrieves a list of tilesets.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if True, returns the total number of tilesets matching the query. default is False.
            skip (int): number of records to skip. default is 0.
            limit (int): number of records to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared tilesets. default is False.

        Returns:
            List[Tileset] | int: A list of Tileset instances or the total number of tilesets

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tilesets = client.get_tilesets(q="name LIKE '%your_tileset_name%'",
            ...     order_by="name A",
            ...     skip=0,
            ...     limit=10,
            ... )
        """
        return Tileset.get_tilesets(self, **kwargs)


    def get_tilesets_by_ids(self, ids: List[int], user_id: int = None) -> List['Tileset']:
        """
        Retrieves a list of tilesets by their IDs.

        Args:
            ids (List[str]): The list of tileset IDs.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            List[Tileset]: A list of Tileset instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tilesets = client.get_tilesets_by_ids(ids=['123', '456'])
        """
        return Tileset.get_tilesets_by_ids(self, ids, user_id)


    def get_tileset(self, uuid: str) -> 'Tileset':
        """
        Retrieves a tileset by its UUID.

        Args:
            uuid (str): The UUID of the tileset.

        Returns:
            Tileset: The retrieved tileset instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tileset = client.get_tileset(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Tileset.get_tileset(self, uuid)


    def get_tileset_by_name(self, name: str, user_id: int = None) -> Union['Tileset', None]:
        """
        Get a tileset by name

        Args:
            name (str): the name of the tileset to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Tileset | None: returns the tileset if a tileset matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tileset = client.get_tileset_by_name(name='test')
        """
        return Tileset.get_tileset_by_name(self, name, user_id)
    

    def get_rasters(self, **kwargs) -> Union[List['Raster'], int]:
        """
        Get all rasters.

        Keyword Args:
            terrain (bool): whether to get terrain rasters.
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.        
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return the total count of rasters. default is False.
            skip (int): number of rasters to skip. minimum is 0.
            limit (int): number of rasters to return. minimum is 1.
            user_id (int): user id to show the rasters of the user. privileges required.
            shared (bool): whether to return shared rasters. default is False.

        Returns:
            List[Raster] | int: A list of Raster objects or the total count of rasters.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> rasters = client.get_rasters(terrain=True, q="name LIKE '%GIS%'")
        """
        return Raster.get_rasters(self, **kwargs)


    def get_rasters_by_ids(self, ids: List[int], user_id: int = None) -> List['Raster']:
        """
        Get rasters by their IDs.

        Args:
            ids (List[str]): The IDs of the rasters.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List['Raster']: A list of Raster objects.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> rasters = client.get_rasters_by_ids(ids=['123', '456'])
        """ 
        return Raster.get_rasters_by_ids(self, ids, user_id)


    def get_raster(self, uuid: str) -> 'Raster':
        """
        Get a raster by its UUID.

        Args:
            uuid (str): The UUID of the raster.
            user_id (int, optional): specific user. privileges required.

        Returns:
            Raster: A Raster object.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> raster = client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Raster.get_raster(self, uuid)    


    def get_raster_by_name(self, name: str, user_id: int = None) -> Union['Raster', None]:
        """
        Get a raster by name

        Args:
            name (str): the name of the raster to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Raster | None: returns the raster if a raster matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> raster = client.get_raster_by_name(name='test')
        """
        return Raster.get_raster_by_name(self, name, user_id)


    def get_mosaics(self, **kwargs) -> Union[List['Mosaic'], int]:
        """
        Get a list of mosaics.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            seacrh (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if true, the number of mosaics will be returned.
            skip (int): number of mosaics to skip. minimum value is 0.
            limit (int): maximum number of mosaics to return. minimum value is 1.
            user_id (int): specific user. privileges required.
            shared (bool): Whether to return shared mosaics. default is False.

        Returns:
            List['Mosaic'] | int: A list of Mosaic instances or the number of mosaics.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> mosaics = client.get_mosaics(q="name LIKE '%GIS%'")
        """
        return Mosaic.get_mosaics(self, **kwargs)


    def get_mosaics_by_ids(self, ids: List[int], user_id: int = None) -> List['Mosaic']:
        """
        Get mosaics by their IDs.

        Args:
            ids (List[str]): The IDs of the mosaics.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[Mosaic]: A list of Mosaic instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> mosaics = client.get_mosaics_by_ids(ids=['1, 2, 3'])
        """
        return Mosaic.get_mosaics_by_ids(self, ids, user_id)


    def create_mosaic(self, 
                      name:str,
                      display_name: str = None,
                      description: str = None,
                      pixel_selection: str = None,
                      min_zoom: int = None,
                      user_id: int = None) -> 'Mosaic':
        """
        Create New Raster Mosaic

        Args:
            name (str): The name of the mosaic.
            display_name (str, optional): The display name of the mosaic.
            description (str, optional): The description of the mosaic.
            pixel_selection (str, optional): The pixel selection of the mosaic.
            min_zoom (int, optional): The minimum zoom of the mosaic.
            user_id (int, optional): specific user. privileges required.

        Returns:
            Mosaic: The created mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> mosaic = client.create_mosaic(name='mosaic_name')
        """
        return Mosaic.create_mosaic(self, name, display_name, description, pixel_selection, min_zoom, user_id)


    def get_mosaic(self, uuid: str, user_id: int = None) -> 'Mosaic':
        """
        Get a mosaic by uuid.

        Args:
            uuid (str): The UUID of the mosaic.
            user_id (int, optional): specific user. privileges required.

        Returns:
            Mosaic: The mosaic object.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> mosaic = client.get_mosaic(uuid="12345678-1234-5678-1234-567812345678")
        """      
        return Mosaic.get_mosaic(self, uuid, user_id)


    def get_mosaic_by_name(self, name: str, user_id: int = None) -> Union['Mosaic', None]:
        """
        Get a mosaic by name

        Args:
            name (str): the name of the mosaic to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Mosaic | None: returns the mosaic if a mosaic matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> mosaic = client.get_mosaic_by_name(name='test')
        """
        return Mosaic.get_mosaic_by_name(self, name, user_id)


    def get_models(self, **kwargs) -> Union[List['Model'], int]:
        """
        Get a list of models with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return total count. default is False.
            skip (int): number of models to skip. default is 0.
            limit (int): maximum number of models to return. default is 10.
            user_id (int): specific user. privileges required.
            shared (bool): Whether to return shared models. default is False.

        Returns:
            List[Model] | int: A list of Model objects or the count number.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> models = client.get_models(search="my_model",
            ...                           search_fields="name, description",
            ...                           order_by="name A",
            ...                           return_count=True,
            ...                           skip=0,
            ...                           limit=10,
            ...                           shared=False)
        """
        return Model.get_models(self, **kwargs)
    

    def get_model(self, uuid: str, user_id: int = None) -> 'Model':
        """
        Get a model by its UUID.

        Args:
            uuid (str): The UUID of the model to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Model: The model object.

        Raises:
            NotFoundError: If the model with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> model = client.get_model(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Model.get_model(self, uuid, user_id)


    def get_model_by_name(self, name: str, user_id: int = None) -> Union['Model', None]:
        """
        Get a model by name

        Args:
            name (str): the name of the model to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Model | None: returns the model if a model matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> model = client.get_model_by_name(name='test')
        """
        return Model.get_model_by_name(self, name, user_id)
    
    
    def get_maps(self, **kwargs) -> Union[List['Map'], int]:
        """
        Get list of maps with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared maps. default is False.

        Returns:
            List[Map] | int: A list of Map instances or the total number of maps.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> maps = client.get_maps(q="name LIKE '%My Map%'")
        """
        return Map.get_maps(self, **kwargs)
    

    def create_map(self, 
                   name: str, 
                   display_name: str = None, 
                   description: str = None,
                   extent: List[float] = None,
                   thumbnail: str = None,
                   style: Dict = None,
                   user_id: int = None) -> 'Map':
        """
        Create a new map.

        Args:
            name (str): The name of the map.
            display_name (str, optional): The display name of the map.
            description (str, optional): The description of the map.
            extent (List[float], optional): The extent of the map.
            thumbnail (str, optional): The thumbnail of the map.
            style (Dict, optional): The style of the map.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Map: The newly created map instance.

        Raises:
            ValidationError: If the map data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> map = client.create_map(name="my_map", display_name="My Map", description="This is a description of my map", extent=[10, 20, 30, 40], thumbnail="https://example.com/thumbnail.png", style={"type": "style"})
        """
        return Map.create_map(self, name, display_name, description, extent, thumbnail, style, user_id)
    

    def get_map(self, uuid: str, user_id: int = None) -> 'Map':
        """
        Get a map by its UUID.

        Args:
            uuid (str): The UUID of the map to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Map: The map object.

        Raises:
            NotFoundError: If the map with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> map = client.get_map(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Map.get_map(self, uuid, user_id)


    def get_map_by_name(self, name: str, user_id: int = None) -> Union['Map', None]:
        """
        Get a map by name

        Args:
            name (str): the name of the map to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Map | None: returns the map if a map matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> map = client.get_map_by_name(name='test')
        """
        return Map.get_map_by_name(self, name, user_id)
    

    def get_queries(self, **kwargs) -> Union[List['Query'], int]:
        """
        Get Queries

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of queries to skip. default is 0.
            limit(int): Maximum number of queries to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared queries. default is False.

        Returns:
            List[Query] | int: list of queries or the number of queries.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> queries = client.get_queries()
        """
        return Query.get_queries(self, **kwargs)
    

    def create_query(self, name: str, display_name: str = None, sql: str = None, params: List = None) -> 'Query':
        """
        Creates a new query.

        Args:
            name (str): The name of the query.
            display_name (str, optional): The display name of the query.
            sql (str, optional): The SQL statement for the query.
            params (list, optional): The parameters for the SQL statement.

        Returns:
            Query: The created query instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> query = client.create_query(name='query_name', display_name='Query Name', sql='SELECT * FROM some_layer')
        """
        return Query.create_query(self, name, display_name, sql, params)
    

    def get_query(self, uuid: str, user_id: int = None) -> 'Query':
        """
        Retrieves a query by its UUID.

        Args:
            uuid (str): The UUID of the query.
            user_id (int, optional): specific user ID. privileges required.

        Returns:
            Query: The retrieved query instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> query = client.get_query(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Query.get_query(self, uuid, user_id)


    def get_query_by_name(self, name: str, user_id: int = None) -> Union['Query', None]:
        """
        Get a query by name

        Args:
            name (str): the name of the query to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Query | None: returns the query if a query matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> query = client.get_query_by_name(name='test')
        """
        return Query.get_query_by_name(self, name, user_id)
    

    def get_system_queries(self, **kwargs) -> List['Query']:
        """
        Returns the system queries as a list of Query objects.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return the total count of queries. default is False.
            skip (int): number of queries to skip. minimum is 0. default is 0.
            limit (int): number of queries to return. minimum is 1. default is 100.
            user_id (int): specific user. privileges required.
            shared (bool): whether to return shared queries. default is False.
        
        Returns:
            List[Query]: list of system queries.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> queries = client.get_system_queries()
        """
        return Query.get_system_queries(self, **kwargs)
    

    def get_users(self, **kwrags) -> Union[List['User'], int]:
        """
        Retrieves a list of users (Permission Required)

        Keyword Args:
            status (UserStatus): the status of the users filter.
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared maps. default is False.

        Returns:
            List[User] | int: list of users or the count number.

        Example:
            >>> from geobox import Geoboxclient
            >>> client = GeoboxClient()
            >>> users = client.get_users()
        """
        return User.get_users(self, **kwrags)
    

    def create_user(self,
                    username: str, 
                    email: str, 
                    password: str, 
                    role: 'UserRole',
                    first_name: str,
                    last_name: str,
                    mobile: str,
                    status: 'UserStatus') -> 'User':
        """
        Create a User (Permission Required)

        Args:
            username (str): the username of the user.
            email (str): the email of the user.
            password (str): the password of the user.
            role (UserRole): the role of the user.
            first_name (str): the firstname of the user.
            last_name (str): the lastname of the user.
            mobile (str): the mobile number of the user. e.g. "+98 9120123456".
            status (UserStatus): the status of the user.

        Returns:
            User: the user object.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> user = client.create_user(username="user1",
            ...                             email="user1@example.com",
            ...                             password="P@ssw0rd",
            ...                             role=UserRole.ACCOUNT_ADMIN,
            ...                             first_name="user 1",
            ...                             last_name="user 1",
            ...                             mobile="+98 9120123456",
            ...                             status=UserStatus.ACTIVE)
        """
        return User.create_user(self, username, email, password, role, first_name, last_name, mobile, status)
    

    def search_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Get list of users based on the search term.

        Args:
            search (str, optional): The Search Term.
            skip (int, optional): Number of items to skip. default is 0.
            limit (int, optional): Number of items to return. default is 10.

        Returns:
            List[User]: A list of User instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> users = client.get_users(search="John")
        """
        return User.search_users(self, search, skip, limit)
    

    def get_user(self, user_id: str = 'me') -> 'User':
        """
        Get a user by its id (Permission Required)

        Args:
            user_id (int, optional): Specific user. don't specify a user_id to get the current user.

        Returns:
            User: the user object.

        Raises:
            NotFoundError: If the user with the specified id is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> user = client.get_user(user_id=1)
            get the current user
            >>> user = client.get_user()
        """
        return User.get_user(self, user_id)
    

    def get_my_sessions(self) -> List['Session']:
        """
        Get a list of user available sessions (Permission Required)

        Returns:
            List[Session]: list of user sessions.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> client.get_my_sessions()
        """
        user = self.get_user()
        return user.get_sessions()
    

    def get_workflows(self, **kwargs) -> Union[List['Workflow'], int]:
        """
        Get list of workflows with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared workflows. default is False.

        Returns:
            List[Workflow] | int: A list of workflow instances or the total number of workflows.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> workflows = client.get_workflows(q="name LIKE '%My workflow%'")
        """
        return Workflow.get_workflows(self, **kwargs)
    

    def create_workflow(self,
                    name: str, 
                    display_name: str = None, 
                    description: str = None, 
                    settings: Dict = {}, 
                    thumbnail: str = None, 
                    user_id: int = None) -> 'Workflow':
        """
        Create a new workflow.

        Args:
            name (str): The name of the Workflow.
            display_name (str): The display name of the workflow.
            description (str): The description of the workflow.
            settings (Dict): The settings of the workflow.
            thumbnail (str): The thumbnail of the workflow.
            user_id (int): Specific user. privileges workflow.

        Returns:
            Workflow: The newly created workflow instance.

        Raises:
            ValidationError: If the workflow data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> workflow = client.create_workflow(name="my_workflow")
        """
        return Workflow.create_workflow(self, name, display_name, description, settings, thumbnail, user_id)


    def get_workflow(self, uuid: str, user_id: int = None) -> 'Workflow':
        """
        Get a workflow by its UUID.

        Args:
            uuid (str): The UUID of the workflow to get.
            user_id (int): Specific user. privileges required.

        Returns:
            Workflow: The workflow object.

        Raises:
            NotFoundError: If the workflow with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> workflow = client.get_workflow(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Workflow.get_workflow(self, uuid, user_id)


    def get_workflow_by_name(self, name: str, user_id: int = None) -> Union['Workflow', None]:
        """
        Get a workflow by name

        Args:
            name (str): the name of the workflow to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Workflow | None: returns the workflow if a workflow matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> workflow = client.get_workflow_by_name(name='test')
        """
        return Workflow.get_workflow_by_name(self, name, user_id)
    

    def get_versions(self, **kwargs) -> Union[List['VectorLayerVersion'], int]:
        """
        Get list of versions with optional filtering and pagination.

        Keyword Args:
            layer_id (str): the id of the vector layer.
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared versions. default is False.

        Returns:
            List[VectorLayerVersion] | int: A list of vector layer version instances or the total number of versions.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> versions = client.get_versions(q="name LIKE '%My version%'")
        """
        return VectorLayerVersion.get_versions(self, **kwargs)
    

    def get_version(self, uuid: str, user_id: int = None) -> 'VectorLayerVersion':
        """
        Get a version by its UUID.

        Args:
            uuid (str): The UUID of the version to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            VectorLayerVersion: The vector layer version object.

        Raises:
            NotFoundError: If the version with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> version = client.get_version(uuid="12345678-1234-5678-1234-567812345678")
        """
        return VectorLayerVersion.get_version(self, uuid, user_id)


    def get_version_by_name(self, name: str, user_id: int = None) -> 'VectorLayerVersion':
        """
        Get a version by name

        Args:
            name (str): the name of the version to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            VectorLayerVersion | None: returns the version if a version matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> version = client.get_version_by_name(name='test')
        """
        return VectorLayerVersion.get_version_by_name(self, name, user_id)
    

    def get_layouts(self, **kwargs) -> Union[List['Layout'], int]:
        """
        Get list of layouts with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared layouts. default is False.

        Returns:
            List[Layout] | int: A list of layout instances or the total number of layouts.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layouts = client.get_layouts(q="name LIKE '%My layout%'")
        """
        return Layout.get_layouts(self, **kwargs)
    

    def create_layout(self,
                    name: str, 
                    display_name: str = None, 
                    description: str = None, 
                    settings: Dict = {}, 
                    thumbnail: str = None, 
                    user_id: int = None) -> 'Layout':
        """
        Create a new layout.

        Args:
            name (str): The name of the layout.
            display_name (str): The display name of the layout.
            description (str): The description of the layout.
            settings (Dict): The settings of the layout.
            thumbnail (str): The thumbnail of the layout.
            user_id (int): Specific user. privileges layout.

        Returns:
            Layout: The newly created layout instance.

        Raises:
            ValidationError: If the layout data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layout = client.create_layout(name="my_layout")
        """
        return Layout.create_layout(self, name, display_name, description, settings, thumbnail, user_id)


    def get_layout(self, uuid: str, user_id: int = None) -> 'Layout':
        """
        Get a layout by its UUID.

        Args:
            uuid (str): The UUID of the layout to get.
            user_id (int): Specific user. privileges required.

        Returns:
            Layout: The layout object.

        Raises:
            NotFoundError: If the layout with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layout = client.get_layout(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Layout.get_layout(self, uuid, user_id)


    def get_layout_by_name(self, name: str, user_id: int = None) -> Union['Layout', None]:
        """
        Get a layout by name

        Args:
            name (str): the name of the layout to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Layout | None: returns the layout if a layout matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layout = client.get_layout_by_name(name='test')
        """
        return Layout.get_layout_by_name(self, name, user_id)


    def get_3dtiles(self, **kwargs) -> Union[List['Tile3d'], int]:
        """
        Get list of 3D Tiles with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared maps. default is False.

        Returns:
            List[Tile3d] | int: A list of 3D Tile instances or the total number of 3D Tiles.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tiles = client.get_3dtiles(q="name LIKE '%My tile%'")
        """ 
        return Tile3d.get_3dtiles(self, **kwargs)
    

    def get_3dtile(self, uuid: str, user_id: int = None) -> 'Tile3d':
        """
        Get a 3D Tile by its UUID.

        Args:
            uuid (str): The UUID of the map to 3D Tile.
            user_id (int): Specific user. privileges required.

        Returns:
            Tile3d: The 3D Tile object.

        Raises:
            NotFoundError: If the 3D Tile with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tile = client.get_3dtile(uuid="12345678-1234-5678-1234-567812345678")
        """ 
        return Tile3d.get_3dtile(self, uuid, user_id)


    def get_3dtile_by_name(self, name: str, user_id: int = None) -> Union['Tile3d', None]:
        """
        Get a 3dtile by name

        Args:
            name (str): the name of the 3dtile to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Tile3d | None: returns the 3dtile if a 3dtile matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> tile3d = client.get_3dtile_by_name(name='test')
        """
        return Tile3d.get_3dtile_by_name(self, name, user_id)
    

    def get_system_settings(self) -> 'SystemSettings':
        """
        Get System Settings object (Permission Required).

        Returns:
            SystemSetting: the system settings object.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> setting = client.get_system_settings()
        """
        return SystemSettings.get_system_settings(self)


    def get_scenes(self, **kwargs) -> Union[List['Scene'], int]:
        """
        Get list of scenes with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared scenes. default is False.

        Returns:
            List[Scene] | int: A list of scene instances or the total number of scenes.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> scenes = client.get_scenes(q="name LIKE '%My scene%'")
        """
        return Scene.get_scenes(self, **kwargs)
    

    def create_scene(self, 
                     name: str, 
                     display_name: str = None, 
                     description: str = None, 
                     settings: Dict = {}, 
                     thumbnail: str = None, 
                     user_id: int = None) -> 'Scene':
        """
        Create a new scene.

        Args:
            name (str): The name of the scene.
            display_name (str, optional): The display name of the scene.
            description (str, optional): The description of the scene.
            settings (Dict,optional): The settings of the scene.
            thumbnail (str, optional): The thumbnail of the scene.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Scene: The newly created scene instance.

        Raises:
            ValidationError: If the scene data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> scene = client.create_scene(name="my_scene")
        """
        return Scene.create_scene(self, 
                                  name, 
                                  display_name, 
                                  description, 
                                  settings, 
                                  thumbnail, 
                                  user_id)
    

    def get_scene(self, uuid: str, user_id: int = None) -> 'Scene':
        """
        Get a scene by its UUID.

        Args:
            uuid (str): The UUID of the scene to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Scene: The scene object.

        Raises:
            NotFoundError: If the scene with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> scene = client.get_scene(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Scene.get_scene(self, uuid, user_id)


    def get_scene_by_name(self, name: str, user_id: int = None) -> Union['Scene', None]:
        """
        Get a scene by name

        Args:
            name (str): the name of the scene to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Scene | None: returns the scene if a scene matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> scene = client.get_scene_by_name(name='test')
        """
        return Scene.get_scene_by_name(self, name, user_id)


    def route(self, stops: str, **kwargs) -> Dict:
        """
        Find best driving routes between coordinates and return results.

        Args:
            stops (str): Comma-separated list of stop coordinates in the format lon,lat;lon,lat.

        Keyword Args:
            alternatives (bool): Whether to return alternative routes. Default value : False.
            steps (bool): Whether to include step-by-step navigation instructions. Default value : False.
            geometries (RoutingGeometryType): Format of the returned geometry.
            overview (RoutingOverviewLevel): Level of detail in the returned geometry.
            annotations (bool): Whether to include additional metadata like speed, weight, etc.

        Returns:
            Dict: the routing output

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> route = client.route(stops="53,33;56,36",
            ...                         alternatives=True,
            ...                         steps=True,
            ...                         geometries=RoutingGeometryType.geojson,
            ...                         overview=RoutingOverviewLevel.full,
            ...                         annotations=True)
        """
        return Routing.route(self, stops, **kwargs)
    

    def get_plans(self, **kwargs) -> Union[List['Plan'], int]:
        """
        Get list of plans with optional filtering and pagination.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared plans. default is False.

        Returns:
            List[Plan] | int: A list of plan instances or the total number of plans.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> plans = client.get_plan(q="name LIKE '%My plan%'")
        """
        return Plan.get_plans(self, **kwargs)
    

    def create_plan(self,
                    name: str,
                    plan_color: str,
                    storage: int,
                    concurrent_tasks: int,
                    daily_api_calls: int,
                    monthly_api_calls: int,
                    daily_traffic: int,
                    monthly_traffic: int,
                    daily_process: int,
                    monthly_process: int,
                    number_of_days: int = None,
                    display_name: str = None,
                    description: str = None) -> 'Plan':
        """
        Create a new plan.

        Args:
            name (str): The name of the plan.
            plan_color (str): hex value of the color. e.g. #000000.
            storage (int): storage value in bytes. must be greater that 1.
            concurrent_tasks (int): number of concurrent tasks. must be greater that 1.
            daily_api_calls (int): number of daily api calls. must be greater that 1.
            monthly_api_calls (int): number of monthly api calls. must be greater that 1.
            daily_traffic (int): number of daily traffic. must be greater that 1.
            monthly_traffic (int): number of monthly traffic. must be greater that 1.
            daily_process (int): number of daily processes. must be greater that 1.
            monthly_process (int): number of monthly processes. must be greater that 1.
            number_of_days (int, optional): number of days. must be greater that 1.
            display_name (str, optional): display name of the plan.
            description (str, optional): description of the plan.

        Returns:
            Plan: The newly created plan instance.

        Raises:
            ValidationError: If the plan data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> plan = client.create_plan(name="new_plan",
            ...                             display_name=" New Plan",
            ...                             description="new plan description",
            ...                             plan_color="#000000",
            ...                             storage=10,
            ...                             concurrent_tasks=10,
            ...                             daily_api_calls=10,
            ...                             monthly_api_calls=10,
            ...                             daily_traffic=10,
            ...                             monthly_traffic=10,
            ...                             daily_process=10,
            ...                             monthly_process=10,
            ...                             number_of_days=10)
        """
        return Plan.create_plan(self,
                                name,
                                plan_color,
                                storage,
                                concurrent_tasks,
                                daily_api_calls,
                                monthly_api_calls,
                                daily_traffic,
                                monthly_traffic,
                                daily_process,
                                monthly_process,
                                number_of_days,
                                display_name,
                                description)
    

    def get_plan(self, plan_id: int) -> 'Plan':
        """
        Get a plan by its id.

        Args:
            plan_id (int): The id of the plan to get.

        Returns:
            Plan: The plan object

        Raises:
            NotFoundError: If the plan with the specified id is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> plan = client.get_plan(plan_id=1)
        """
        return Plan.get_plan(self, plan_id)
    

    def get_plan_by_name(self, name: str) -> Union['Plan', None]:
        """
        Get a plan by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the plan to get

        Returns:
            Plan | None: returns the plan if a plan matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> plan = client.get_plan_by_name(name='test')
        """
        return Plan.get_plan_by_name(self, name)
    

    def get_dashboards(self, **kwargs) -> Union[List['Dashboard'], int]:
        """
        Get list of Dashboards

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared Dashboards. default is False.

        Returns:
            List[Dashboard] | int: A list of Dashboard instances or the total number of Dashboards.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> dashboards = client.get_dashboards()
        """
        return Dashboard.get_dashboards(self, **kwargs)
    

    def create_dashboard(self,
                     name: str, 
                     display_name: str = None, 
                     description: str = None, 
                     settings: Dict = {}, 
                     thumbnail: str = None, 
                     user_id: int = None) -> 'Dashboard':
        """
        Create a new Dashboard.

        Args:
            name (str): The name of the Dashboard.
            display_name (str, optional): The display name of the Dashboard.
            description (str, optional): The description of the Dashboard.
            settings (Dict, optional): The settings of the sceDashboarde.
            thumbnail (str, optional): The thumbnail of the Dashboard.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Dashboard: The newly created Dashboard instance.

        Raises:
            ValidationError: If the Dashboard data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> dashboard = client.create_dashboard(name="my_dashboard")
        """
        return Dashboard.create_dashboard(self,
                                          name,
                                          display_name,
                                          description,
                                          settings,
                                          thumbnail,
                                          user_id)
    

    def get_dashboard(self, uuid: str, user_id: int = None) -> 'Dashboard':
        """
        Get a Dashboard by its UUID.

        Args:
            uuid (str): The UUID of the Dashboard to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Dashboard: The dashboard object.

        Raises:
            NotFoundError: If the Dashboard with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> dashboard = client.get_dashboard(uuid="12345678-1234-5678-1234-567812345678")
        """
        return Dashboard.get_dashboard(self, uuid, user_id)


    def get_dashboard_by_name(self, name: str, user_id: int = None) -> Union['Dashboard', None]:
        """
        Get a dashboard by name

        Args:
            name (str): the name of the dashboard to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Dashboard | None: returns the dashboard if a dashboard matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> dashboard = client.get_dashboard_by_name(name='test')
        """
        return Dashboard.get_dashboard_by_name(self, name, user_id)
    

    def get_basemaps(self) -> List['Basemap']:
        """
        Get a list of basemaps

        Returns:
            List[BaseMap]: list of basemaps.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> basemaps = client.get_basemaps()
        """
        return Basemap.get_basemaps(self)
    

    def get_basemap(self, name: str) -> 'Basemap':
        """
        Get a basemap object

        Args:
            name: the basemap name

        Returns:
            Basemap: the basemap object

        Raises:
            NotFoundError: if the base,ap with the specified name not found

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> basemap = client.get_basemap(name='test')
        """
        return Basemap.get_basemap(self, name)
    

    def proxy_basemap(self, url: str) -> None:
        """
        Proxy the basemap

        Args:
            url (str): the proxy server url.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> client.proxy_basemap(url='proxy_server_url')
        """
        return Basemap.proxy_basemap(self, url)
    

    def get_attachments(self, resource_type: AttachmentResourceType, resource_uuid: str, **kwargs) -> Union[List['Attachment'], int]:
        """
        Get list of attachments with optional filtering and pagination.

        Args:
            resource_type (AttachmentResourceType): The resource type of the attachment. options are: Map, Vector, View
            resource_uuid (str): The Resoource uuid of the attachment.

        Keyword Args:
            element_id (str): the id of the element with attachment.
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            return_count (bool): Whether to return total count. default is False.

        Returns:
            List[Attachment] | int: A list of attachments instances or the total number of attachments.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> attachments = client.get_attachments(q="name LIKE '%My attachment%'")
        """
        return Attachment.get_attachments(self, resource_type, resource_uuid, **kwargs)
    

    def create_attachment(self,
                     name: str, 
                     loc_x: int,
                     loc_y: int,
                     resource: Union['Map', 'VectorLayer', 'VectorLayerView'],
                     file: 'File',
                     feature: 'Feature' = None,
                     display_name: str = None, 
                     description: str = None, ) -> 'Attachment':
        """
        Create a new Attachment.

        Args:
            name (str): The name of the scene.
            loc_x (int): x parameter of the attachment location.
            loc_y (int): y parameter of the attachment location.
            resource (Map | VectorLayer | VectorLayerView): the resource object.
            file (File): the file object.
            feature (Feature, optional): the feature object.
            display_name (str, optional): The display name of the scene.
            description (str, optional): The description of the scene.

        Returns:
            Attachment: The newly created Attachment instance.

        Raises:
            ValidationError: If the Attachment data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(feature_id=1)
            >>> file = client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>> attachment = client.create_attachment(name="my_attachment", 
            ...                                             loc_x=30, 
            ...                                             loc_y=50, 
            ...                                             resource=layer, 
            ...                                             file=file, 
            ...                                             feature=feature, 
            ...                                             display_name="My Attachment", 
            ...                                             description="Attachment Description")
        """
        return Attachment.create_attachment(self,
                                            name,
                                            loc_x,
                                            loc_y,
                                            resource,
                                            file,
                                            feature,
                                            display_name,
                                            description)
    

    def update_attachment(self, attachment_id: int, **kwargs) -> Dict:
        """
        Update the attachment.

        Args:
            attachment_id (int): the attachment id.

        Keyword Args:
            name (str): The name of the attachment.
            display_name (str): The display name of the attachment.
            description (str): The description of the attachment.
            loc_x (int): x parameter of the attachment location.
            loc_y (int): y parameter of the attachment location.

        Returns:
            Dict: The updated attachment data.

        Raises:
            ValidationError: If the attachment data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> client.update_attachment(attachment_id=1, display_name="New Display Name")
        """
        return Attachment.update_attachment(self, attachment_id, **kwargs)
    

    def get_apikeys(self, **kwargs) -> List['ApiKey']:
        """
        Get a list of apikeys

        Keyword Args:
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of layers to skip. default is 0.
            limit (int): Maximum number of layers to return. default is 10.
            user_id (int): Specific user. privileges required.
        
        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> apikeys = client.get_apikeys()
        """
        return ApiKey.get_apikeys(self, **kwargs)
    

    def create_apikey(self, name: str, user_id: int = None) -> 'ApiKey':
        """
        Create an ApiKey

        Args:
            name (str): name of the key.
            user_id (int, optional): Specific user. privileges required.

        Returns: 
            ApiKey: the apikey object

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> apikey = client.create_apikey(name='test')
        """
        return ApiKey.create_apikey(self, name, user_id)
    

    def get_apikey(self, key_id: int) -> 'ApiKey':
        """
        Get an ApiKey

        Args:
            key_id (str): the id of the apikey.

        Returns:
            ApiKey: the ApiKey object

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> apikey = client.get_apikey(key_id=1) 
        """
        return ApiKey.get_apikey(self, key_id)


    def get_apikey_by_name(self, name: str, user_id: int = None) -> 'ApiKey':
        """
        Get an ApiKey by name

        Args:
            name (str): the name of the key to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            ApiKey | None: returns the key if a key matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> apikey = client.get_apikey_by_name(name='test')
        """
        return ApiKey.get_apikey_by_name(self, name, user_id)


    def get_logs(self, **kwargs) -> List['Log']:
        """
        Get a list of Logs

        Keyword Args:
            search (str): search term for keyword-based searching among all textual fields
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. Privileges required.
            from_date (datetime): datetime object in this format: "%Y-%m-%dT%H:%M:%S.%f". 
            to_date (datetime): datetime object in this format: "%Y-%m-%dT%H:%M:%S.%f". 
            user_identity (str): the user identity in this format: username - firstname lastname - email .
            activity_type (str): the user activity type.

        Returns:
            List[Log]: a list of logs

        Example: 
            >>> from geobox import Geobox
            >>> client = GeoboxClient()
            >>> logs = client.get_logs() 
        """ 
        return Log.get_logs(self, **kwargs)


    def get_api_usage(self, 
                        resource: Union['User', 'ApiKey'], 
                        scale: 'UsageScale',
                        param: 'UsageParam',
                        from_date: 'datetime' = None,
                        to_date: 'datetime' = None,
                        days_before_now: int = None,
                        limit: int = None) -> List:
        """
        Get the api usage of a user

        Args:
            resource (User | ApiKey): User or ApiKey object.
            scale (UsageScale): the scale of the report.
            param (UsageParam): traffic or calls.
            from_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            to_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            days_before_now (int, optional): number of days befor now.
            limit (int, optional): Number of items to return. default is 10.

        Raises:
            ValueError: one of days_before_now or from_date/to_date parameters must have value
            ValueError: resource must be a 'user' or 'apikey' object

        Returns:
            List: usage report

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> user = client.get_user() # gets current user
            >>> usage = client.get_api_usage(resource=user, 
            ...                               scale=UsageScale.Day, 
            ...                               param=UsageParam.Calls, 
            ...                               days_before_now=5)
        """
        return Usage.get_api_usage(self,
                                    resource=resource, 
                                    scale=scale,
                                    param=param,
                                    from_date=from_date,
                                    to_date=to_date,
                                    days_before_now=days_before_now,
                                    limit=limit)


    def get_process_usage(self, 
                            user_id: int = None, 
                            from_date: datetime = None, 
                            to_date: datetime = None, 
                            days_before_now: int = None) -> float:
        """
        Get process usage of a user in seconds

        Args:
            user_id (int, optional): the id of the user. leave blank to get the current user report.
            from_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            to_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            days_before_now (int, optional): number of days befor now.

        Raises:
            ValueError: one of days_before_now or from_date/to_date parameters must have value

        Returns:
            float: process usage of a user in seconds

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> process_usage = client.get_process_usage(days_before_now=5)
        """
        return Usage.get_process_usage(self,
                                        user_id=user_id,
                                        from_date=from_date,
                                        to_date=to_date,
                                        days_before_now=days_before_now)


    def get_usage_summary(self, user_id: int = None) -> Dict:
        """
        Get the usage summary of a user

        Args:
            user_id (int, optional): the id of the user. leave blank to get the current user report.

        Returns:
            Dict: the usage summery of the users

        Returns:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> usage_summary = client.get_usage_summary()
        """
        return Usage.get_usage_summary(self, user_id=user_id)


    def update_usage(self, user_id: int = None) -> Dict:
        """
        Update usage of a user

        Args:
            user_id (int, optional): the id of the user. leave blank to get the current user report.
            
        Returns:
            Dict: the updated data

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> client.update_usage()
        """
        return Usage.update_usage(self, user_id=user_id)