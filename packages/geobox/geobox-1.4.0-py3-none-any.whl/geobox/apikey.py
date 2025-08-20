from typing import List, Dict, Optional, TYPE_CHECKING
from urllib.parse import urljoin

from .base import Base
from .utils import clean_data

if TYPE_CHECKING:
    from . import GeoboxClient

class ApiKey(Base):

    BASE_ENDPOINT = 'apikeys/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 key_id: int,
                 data: Optional[Dict] = {}):
        """
        Initialize an apikey instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            key_id (int): The unique identifier for the apikey.
            data (Dict, optional): The data of the apikey.
        """
        super().__init__(api, data=data)
        self.key_id = key_id
        self.endpoint = urljoin(self.BASE_ENDPOINT, str(self.id))


    def __repr__(self) -> str:
        """
        Return a string representation of the attachment.

        Returns:
            str: The string representation of the attachment.
        """
        return f'ApiKey(id={self.key_id}, name={self.name}, revoked={self.revoked})'


    @classmethod
    def get_apikeys(cls, api: 'GeoboxClient', **kwargs) -> List['ApiKey']:
        """
        Get a list of apikeys

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Keyword Args:
            search (str): search term for keyword-based searching among all textual fields.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of layers to skip. default is 0.
            limit (int): Maximum number of layers to return. default is 10.
            user_id (int): Specific user. privileges required.
        
        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikeys = ApiKey.get_apikeys(client)
            or
            >>> apikeys = client.get_apikeys()
        """
        params = {
            'search': kwargs.get('search'),
            'order_by': kwargs.get('order_by'),
            'skip': kwargs.get('skip'),
            'limit': kwargs.get('limit'),
            'user_id': kwargs.get('user_id')
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: ApiKey(api, item['id'], item))
    

    @classmethod
    def create_apikey(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> 'ApiKey':
        """
        Create an ApiKey

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): name of the key.
            user_id (int, optional): Specific user. privileges required.

        Returns: 
            ApiKey: the apikey object

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikey = ApiKey.create_apikey(client, name='test')
            or 
            >>> apikey = client.create_apikey(name='test')
        """
        data = clean_data({
            'name': name,
            'user_id': user_id
        })
        response = api.post(cls.BASE_ENDPOINT, payload=data, is_json=False)
        return ApiKey(api, response['id'], response)
    

    @classmethod
    def get_apikey(cls, api: 'GeoboxClient', key_id: int) -> 'ApiKey':
        """
        Get an ApiKey

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            key_id (str): the id of the apikey.

        Returns:
            ApiKey: the ApiKey object

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikey = ApiKey.get_apikey(client, key_id=1)
            or
            >>> apikey = client.get_apikey(key_id=1) 
        """
        params = {
            'f': 'json'
        }
        return super()._get_detail(api=api,
                                   endpoint=cls.BASE_ENDPOINT,
                                   uuid=key_id, 
                                   params=params, 
                                   factory_func=lambda api, item: ApiKey(api, item['id'], item))


    @classmethod
    def get_apikey_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> 'ApiKey':
        """
        Get an ApiKey by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the key to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            ApiKey | None: returns the key if a key matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikey = ApiKey.get_apikey_by_name(client, name='test')
            or
            >>> apikey = client.get_apikey_by_name(name='test')
        """
        apikeys = cls.get_apikeys(api, search=name, user_id=user_id)
        if apikeys and apikeys[0].name == name:
            return apikeys[0]
        else:
            return None
    

    def update(self, name: str, user_id: int = None) -> Dict:
        """
        Update an ApiKey

        Args:
            name (str): the name of the key
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Dict: Updated ApiKey data

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikey = ApiKey.get_apikey(client, key_id=1)
            >>> apikey.update(name="updated_name")
        """
        data = clean_data({
            "name": name,
            "user_id": user_id
        })

        response = self.api.put(self.endpoint, data, is_json=False)
        self._update_properties(response)
        return response


    def delete(self) -> None:
        """
        Delete the ApiKey.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikey = ApiKey.get_apikey(client, key_id=1)
            >>> apikey.delete()
        """
        super().delete(self.endpoint)
        self.key_id = None


    def revoke(self) -> None:
        """
        Revoke an ApiKey

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikey = ApiKey.get_apikey(client, key_id=1)
            >>> apikey.revoke()
        """
        endpoint = f"{self.endpoint}/revoke"
        self.api.post(endpoint)
        self.data['revoked'] = True


    def grant(self) -> None:
        """
        Grant an ApiKey

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.apikey import ApiKey
            >>> client = GeoboxClient()
            >>> apikey = ApiKey.get_apikey(client, key_id=1)
            >>> apikey.grant()
        """
        endpoint = f"{self.endpoint}/grant"
        self.api.post(endpoint)
        self.data['revoked'] = False