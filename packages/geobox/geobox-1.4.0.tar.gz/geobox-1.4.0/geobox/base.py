from typing import Any, List, Dict, Callable, TYPE_CHECKING, Union
from urllib.parse import urljoin, urlencode
from datetime import datetime

from .utils import clean_data

if TYPE_CHECKING:
    from .user import User
    from .task import Task
    from . import GeoboxClient 


class Base:
    BASE_ENDPOINT = ''
    
    def __init__(self, api, **kwargs):
        """
        Initialize the Base class.

        Args:
            api (GeoboxClient): The API client
            uuid (str, optional): The UUID of the resource
            data (dict, optional): The data of the resource
        """
        self.api = api
        self.uuid = kwargs.get('uuid')
        self.data = kwargs.get('data')
        self.endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/') if self.uuid else None


    def __dir__(self) -> List[str]:
        """
        Return a list of available attributes for the Feature object.
        
        This method extends the default dir() behavior to include:
        - All keys from the data dictionary
        
        This allows for better IDE autocompletion and introspection of feature attributes.
        
        Returns:
            list: A list of attribute names available on this object.
        """        
        return super().__dir__() + list(self.data.keys())


    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the resource.

        Args:
            name (str): The name of the attribute
        """
        if name in self.data:
            value = self.data.get(name)
            if isinstance(value, str):
                parsed = self._parse_datetime(value)
                if isinstance(parsed, datetime):
                    return parsed
            return value
        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")
    

    def __repr__(self) -> str:
        """
        Return a string representation of the resource.
        """
        return f"{self.__class__.__name__}(uuid={self.uuid}, name={self.name})"
    

    def _update_properties(self, data: dict) -> None:
        """
        Update the properties of the resource.

        Args:
            data (dict): The data to update the properties with
        """
        self.data.update(data)    


    @classmethod
    def _handle_geojson_response(cls, api: 'GeoboxClient', response: dict, factory_func: Callable) -> List['Base']:
        """Handle GeoJSON response format"""
        features_data = response.get('features', [])
        srid = cls._extract_srid(response)
        return [factory_func(api, feature, srid) for feature in features_data]


    @classmethod
    def _extract_srid(cls, response: dict) -> int:
        """Extract SRID from GeoJSON response"""
        if isinstance(response, dict) and 'crs' in response:
            return int(response['crs']['properties']['name'].split(':')[-1])


    @classmethod 
    def _get_count(cls, response: dict) -> int:
        """Get the count of resources"""
        if isinstance(response, dict) and 'count' in response:
            return response.get('count', 0)
        elif isinstance(response, int):
            return response
        else:
            raise ValueError('Invalid response format')


    @classmethod
    def _get_list(cls, api: 'GeoboxClient', endpoint: str, params: dict = {}, 
                factory_func: Callable = None, geojson: bool = False) -> Union[List['Base'], int]:
        """Get a list of resources with optional filtering and pagination"""
        query_string = urlencode(clean_data(params)) if params else ''
        endpoint = urljoin(endpoint, f'?{query_string}')
        response = api.get(endpoint)

        if params.get('return_count'):
            return cls._get_count(response)
        
        if not response:
            return []
            
        if geojson:
            return cls._handle_geojson_response(api, response, factory_func)
            
        return [factory_func(api, item) for item in response]
    

    @classmethod
    def _get_list_by_ids(cls, api: 'GeoboxClient', endpoint: str, params: dict = None, factory_func: Callable = None) -> List['Base']:
        """
        Internal method to get a list of resources by their IDs.

        Args:
            api (GeoboxClient): The API client
            endpoint (str): The endpoint of the resource
            params (dict): Additional parameters for filtering and pagination
            factory_func (Callable): A function to create the resource object

        Returns:
            List[Base]: The list of resource objects
        """
        params = clean_data(params)
        query_string = urlencode(params)
        endpoint = urljoin(endpoint, f'?{query_string}')
        response = api.get(endpoint)
        return [factory_func(api, item) for item in response]


    @classmethod
    def _get_detail(cls, api: 'GeoboxClient', endpoint: str, uuid: str, params: dict = {}, factory_func: Callable = None) -> 'Base':
        """
        Internal method to get a single resource by UUID.
        
        Args:
            api (GeoboxClient): The API client
            uuid (str): The UUID of the resource
            params (dict): Additional parameters for filtering and pagination
            factory_func (Callable): A function to create the resource object

        Returns:
            Base: The resource object
        """
        query_strings = urlencode(clean_data(params))
        endpoint = urljoin(endpoint, f'{uuid}/?{query_strings}')
        response = api.get(endpoint)
        return factory_func(api, response)
    

    @classmethod
    def _create(cls, api: 'GeoboxClient', endpoint: str, data: dict, factory_func: Callable = None) -> 'Base':
        """
        Internal method to create a resource.

        Args:
            api (GeoboxClient): The API client
            data (dict): The data to create the resource with
            factory_func (Callable): A function to create the resource object

        Returns:
            Base: The created resource object
        """
        data = clean_data(data)
        response = api.post(endpoint, data)
        return factory_func(api, response)
    

    def _update(self, endpoint: str, data: dict, clean: bool = True) -> Dict:
        """
        Update the resource.

        Args:
            data (dict): The data to update the resource with
        """
        if clean:
            data = clean_data(data)

        response = self.api.put(endpoint, data)
        self._update_properties(response)
        return response
    

    def delete(self, endpoint: str) -> None:
        """
        Delete the resource.
        """
        self.api.delete(endpoint)
        self.uuid = None
        self.endpoint = None
        

    def _share(self, endpoint: str, users: List['User']) -> None:
        """
        Internal method to share the resource with the given user IDs.

        Args:
            users (List[User]): The user objects to share the resource with
        """
        data = {"user_ids": [user.user_id for user in users]}
        endpoint = urljoin(endpoint, f'share/')
        self.api.post(endpoint, data, is_json=False)


    def _unshare(self, endpoint: str, users: List['User']) -> None:
        """
        Internal method to unshare the resource with the given user IDs.

        Args:
            users (List[User]): The user objects to unshare the resource with
        """
        data = {"user_ids": [user.user_id for user in users]}
        endpoint = urljoin(endpoint, f'unshare/')
        self.api.post(endpoint, data, is_json=False)


    def _get_shared_users(self, endpoint: str, params: dict = None) -> List['User']:
        """
        Internal method to get the users that the resource is shared with.

        Args:
            endpoint (str): resource endpoint
            params (dict): Additional parameters for filtering and pagination

        Returns:
            List[User]: The users that the resource is shared with
        """
        from .user import User

        params = clean_data(params)
        query_strings = urlencode(params)
        endpoint = urljoin(endpoint, f'shared-with-users/?{query_strings}')
        response = self.api.get(endpoint)
        return [User(self.api, item['id'], item) for item in response]
    

    def _get_settings(self, endpoint: str) -> Dict:
        """
        Internal method to get the settings of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        endpoint = urljoin(endpoint, f'settings/?f=json')
        return self.api.get(endpoint)
    

    def _set_settings(self, endpoint: str, data: dict) -> None:
        """
        Internal method to set the settings of the resource.

        Args:
            endpoint (str): The endpoint of the resource
            data (dict): The data to set the settings with
        """
        endpoint = urljoin(endpoint, f'settings/')
        return self.api.put(endpoint, data)


    def _get_task(self, response, error_message: str) -> List['Task']:
        from .task import Task  # avoid circular dependency

        if len(response) == 1 and isinstance(response, list) and response[0].get('task_id'):
            result = [self.api.get_task(response[0].get('task_id'))]
        elif len(response) == 2 and isinstance(response, list) and (response[0].get('task_id') and response[1].get('task_id')):
            result = [self.api.get_task(item.get('task_id')) for item in response]
        elif len(response) == 1 and isinstance(response, dict) and response.get('task_id'):
            result = [self.api.get_task(response.get('task_id'))]
        else:
            raise ValueError(error_message)

        return result


    def _seed_cache(self, endpoint: str, data: dict) -> List['Task']:
        """
        Internal method to cache seed the resource.

        Args:
            endpoint (str): The endpoint of the resource
            data (dict): The data to cache seed with
        """
        if data['workers'] not in [1, 2, 4, 8, 12, 16, 20, 24]:
            raise ValueError("workers must be in [1, 2, 4, 8, 12, 16, 20, 24]")
        
        data = clean_data(data)
        endpoint = urljoin(endpoint, f'cache/seed/')
        response = self.api.post(endpoint, data)
        return self._get_task(response, 'Failed to seed cache')

    def _clear_cache(self, endpoint: str) -> None:
        """
        Internal method to clear the cache of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        endpoint = urljoin(endpoint, f'cache/clear/')
        self.api.post(endpoint)


    def _cache_size(self, endpoint: str) -> int:
        """
        Internal method to get the size of the cache of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        endpoint = urljoin(endpoint, f'cache/size/')
        return self.api.post(endpoint)
    

    def _update_cache(self, endpoint: str, data: Dict = {}) -> List['Task']:
        """
        Internal method to update the cache of the resource.

        Args:
            endpoint (str): The endpoint of the resource
        """
        data = clean_data(data)
        endpoint = urljoin(endpoint, 'cache/update/')
        response = self.api.post(endpoint, data)
        return self._get_task(response, 'Failed to update cache')

    def _parse_datetime(self, date_string: str) -> Union[datetime, str]:
        """
        Parse a datetime string with multiple format support.
        
        Args:
            date_string (str): The datetime string to parse
            
        Returns:
            Union[datetime, str]: Parsed datetime object or original string if parsing fails
        """
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # With microseconds
            "%Y-%m-%dT%H:%M:%SZ",    # Without microseconds, with timezone
            "%Y-%m-%dT%H:%M:%S"      # Without microseconds, without timezone
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        # If all parsing fails, return the original string
        return date_string


    def thumbnail(self, format='.png') -> str:
        """
        Get the thumbnail URL of the resource.
        
        Returns:
            str: The thumbnail URL

        Raises:
            ValueError: 
        """
        endpoint = f'{self.api.base_url}{self.endpoint}thumbnail{format}'
        
        if not self.api.access_token and self.api.apikey:
            endpoint = f'{endpoint}?apikey={self.api.apikey}'
            
        elif not self.api.access_token and not self.api.apikey:
            raise ValueError("either access_token or apikey must be available for this action.")
        
        return endpoint