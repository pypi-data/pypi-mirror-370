from typing import List, Dict, Optional, TYPE_CHECKING
from urllib.parse import urljoin, urlencode

from .base import Base
from .exception import NotFoundError
from .utils import clean_data

if TYPE_CHECKING:
    from . import GeoboxClient

class Basemap(Base):

    BASE_ENDPOINT = 'basemaps/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 data: Optional[Dict] = {}):
        """
        Initialize a basemap instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            data (Dict): The data of the basemap.
        """
        super().__init__(api, data=data)
        self.endpoint = f"{self.BASE_ENDPOINT}{self.data.get('name')}/"


    @classmethod
    def get_basemaps(cls, api: 'GeoboxClient') -> List['Basemap']:
        """
        Get a list of basemaps

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Returns:
            List[BaseMap]: list of basemaps.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.basemap import Basemap
            >>> client = GeoboxClient()
            >>> basemaps = Basemap.get_basemaps(client)
            or
            >>> basemaps = client.get_basemaps()
        """
        response = api.get(cls.BASE_ENDPOINT)
        if not response:
            return []

        items = []
        for item in response:
            response[item]['name'] = item
            items.append(response[item])

        return [cls(api, item) for item in items]


    @classmethod
    def get_basemap(cls, api: 'GeoboxClient', name: str) -> 'Basemap':
        """
        Get a basemap object

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name: the basemap name

        Returns:
            Basemap: the basemap object

        Raises:
            NotFoundError: if the base,ap with the specified name not found

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.basemap import Basemap
            >>> client = GeoboxClient()
            >>> basemap = Basemap.get_basemap(client, name='test')
            or
            >>> basemap = client.get_basemap(name='test')
        """
        basemap = [basemap for basemap in cls.get_basemaps(api) if basemap.name == name]
        if not basemap:
            raise NotFoundError(f'Basemap with name "{name}" not found.')

        return basemap[0]


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail url of the basemap

        Returns:
            str: the thumbnail url
        """
        endpoint = f"{self.api.base_url}{self.endpoint}/thumbnail.png" 
        return endpoint
    

    @property
    def wmts(self) -> str:
        """
        Get the wmts url of the basemap

        Returns:
            str: the wmts url
        """
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}wmts/')

        if not self.api.access_token and self.api.apikey:
            endpoint = f"{endpoint}?apikey={self.api.apikey}"
            
        return endpoint
    

    @property
    def server_url(self) -> str:
        """
        Get the server url of the basemap

        Returns:
            str: the server url
        """
        endpoint = f'{self.api.base_url}{self.BASE_ENDPOINT}server_url'
        return self.api.get(endpoint)
    

    @property
    def proxy_url(self) -> str:
        """
        Get the proxy url of the basemap

        Returns:
            str: the proxy url
        """
        endpoint = f'{self.api.base_url}{self.BASE_ENDPOINT}proxy_url'
        return self.api.get(endpoint)
    

    @classmethod
    def proxy_basemap(cls, api: 'GeoboxClient', url: str) -> None:
        """
        Proxy the basemap

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            url (str): the proxy server url.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.basemap import Basemap
            >>> client = GeoboxClient()
            >>> Basemap.proxy_basemap(client, url='proxy_server_url')
            or
            >>> client.proxy_basemap(url='proxy_server_url')
        """
        param = clean_data({
            'url': url
        })
        query_string = urlencode(param)
        endpoint = urljoin(cls.BASE_ENDPOINT, f"?{query_string}")
        api.get(endpoint)