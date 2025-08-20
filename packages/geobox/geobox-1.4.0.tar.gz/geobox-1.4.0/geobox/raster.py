import os
from urllib.parse import urljoin, urlencode
from typing import Optional, Dict, List, Optional, Union, TYPE_CHECKING
import mimetypes
import requests
import sys

from .base import Base
from .utils import clean_data, join_url_params
from .task import Task

if TYPE_CHECKING:
    from . import GeoboxClient 
    from .user import User

class Raster(Base):
    """
    A class to represent a Raster in Geobox.

    This class provides functionality to interact with rasters in Geobox.
    It supports various operations including CRUD operations on rasters, as well as advanced operations like getting statistics, points, and tiles.
    It also provides properties to access the raster data, and a method to download the raster.
    """
    BASE_ENDPOINT: str = 'rasters/'

    def __init__(self,
                 api: 'GeoboxClient',
                 uuid: str,
                 data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Raster object.

        Args:
            api (GeoboxClient): The API instance.
            uuid (str): The UUID of the raster.
            data (Dict, optional): The raster data.
        """ 
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    def get_rasters(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Raster'], int]:
        """
        Get all rasters.

        Args:
            api (GeoboxClient): The API instance.

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
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> rasters = Raster.get_rasters(client, terrain=True, q="name LIKE '%GIS%'")
            or
            >>> rasters = client.get_rasters(terrain=True, q="name LIKE '%GIS%'")
        """
        params = {
            'terrain': kwargs.get('terrain', None),
            'f': 'json',
            'q': kwargs.get('q', None),
            'search': kwargs.get('search', None),
            'search_fields': kwargs.get('search_fields', None),
            'order_by': kwargs.get('order_by', None),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 100),
            'user_id': kwargs.get('user_id', None),
            'shared': kwargs.get('shared', False)
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Raster(api, item['uuid'], item))
    


    @classmethod
    def get_rasters_by_ids(cls, api: 'GeoboxClient', ids: List[str], user_id: int = None) -> List['Raster']:
        """
        Get rasters by their IDs.

        Args:
            api (GeoboxClient): The API instance.
            ids (List[str]): The IDs of the rasters.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List['Raster']: A list of Raster objects.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> rasters = Raster.get_rasters_by_ids(client, ids=['123', '456'])
            or
            >>> rasters = client.get_rasters_by_ids(ids=['123', '456'])
        """ 
        params = {
            'ids': ids,
            'user_id': user_id,
        }
        endpoint = urljoin(cls.BASE_ENDPOINT, 'get-rasters/')

        return super()._get_list_by_ids(api, endpoint, params, factory_func=lambda api, item: Raster(api, item['uuid'], item))


    @classmethod
    def get_raster(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Raster':
        """
        Get a raster by its UUID.

        Args:
            api (GeoboxClient): The API instance.
            uuid (str): The UUID of the raster.
            user_id (int, optional): specific user. privileges required.

        Returns:
            Raster: A Raster object.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> raster = client.get_raster(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Raster(api, item['uuid'], item))


    @classmethod
    def get_raster_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Raster', None]:
        """
        Get a raster by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the raster to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Raster | None: returns the raster if a raster matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster_by_name(client, name='test')
            or
            >>> raster = client.get_raster_by_name(name='test')
        """
        rasters = cls.get_rasters(api, q=f"name = '{name}'", user_id=user_id)
        if rasters and rasters[0].name == name:
            return rasters[0]
        else:
            return None
    
    
    def update(self, **kwargs) -> None:
        """
        Update the raster.

        Keyword Args:
            name (str): The name of the raster.
            display_name (str): The display name of the raster.
            description (str): The description of the raster.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.update(name="new_name")
        """ 
        params = {
            'name': kwargs.get('name'),
            'display_name': kwargs.get('display_name'),
            'description': kwargs.get('description')
        }
        return super()._update(self.endpoint, params)
    

    def delete(self) -> None:
        """
        Delete the raster.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.delete()
        """
        super().delete(self.endpoint)
    

    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail of the raster.

        Returns:
            str: The url of the thumbnail.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.thumbnail
        """
        return super().thumbnail(format='')
    
    
    @property
    def info(self) -> Dict:
        """
        Get the info of the raster.

        Returns:
            Dict: The info of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.info
        """
        endpoint = urljoin(self.endpoint, 'info/')
        return self.api.get(endpoint)
    

    def get_statistics(self, indexes: str = None) -> Dict:
        """
        Get the statistics of the raster.

        Args:
            indexes (str): list of comma separated band indexes. e.g. 1, 2, 3

        Returns:
            Dict: The statistics of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.get_statistics(indexes='1, 2, 3')
        """
        params = clean_data({
            'indexes': indexes,
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.endpoint, f'statistics/?{query_string}')
        return self.api.get(endpoint)
    

    def get_point(self, lat: float, lng: float) -> Dict:
        """
        Get the point of the raster.

        Args:
            lat (float): The latitude of the point. minimum is -90, maximum is 90.
            lng (float): The longitude of the point. minimum is -180, maximum is 180.

        Returns:
            Dict: The point of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.get_point(lat=60, lng=50)
        """
        if lat < -90 or lat > 90:
            raise ValueError("lat must be between -90 and 90")
        if lng < -180 or lng > 180:
            raise ValueError("lng must be between -180 and 180")
        
        params = clean_data({
            'lat': lat,
            'lng': lng,
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.endpoint, f'point?{query_string}')
        return self.api.get(endpoint)
    

    def _get_save_path(self, save_path: str = None) -> str:
        """
        Get the path where the file should be saved.

        Args:
            save_path (str, optional): The path to save the file.

        Returns:
            str: The path where the file is saved.
        
        Raises:
            ValueError: If save_path does not end with a '/'.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file_path = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
        """
        # If save_path is provided, check if it ends with a '/'
        if save_path and save_path.endswith('/'):
            return f'{save_path}'
        
        if save_path and not save_path.endswith('/'):
            raise ValueError("save_path must end with a '/'")
        
        return os.getcwd()
    
    
    def _get_file_name(self, response: requests.Response) -> str:
        """
        Get the file name from the response.

        Args:
            response (requests.Response): The response of the request.

        Returns:
            str: The file name 
        """
        if 'Content-Disposition' in response.headers and 'filename=' in response.headers['Content-Disposition']:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1].strip().strip('"')

        else:
            content_type = response.headers.get("Content-Type", "")
            file_name = f'{self.name}.{mimetypes.guess_extension(content_type.split(";")[0])}'

        return file_name


    def _create_progress_bar(self) -> 'tqdm':
        """Creates a progress bar for the task."""
        try:
            from tqdm.auto import tqdm
        except ImportError:
            from .api import logger
            logger.warning("[tqdm] extra is required to show the progress bar. install with: pip insatll geobox[tqdm]")
            return None

        return tqdm(unit="B", 
                        total=int(self.size), 
                        file=sys.stdout,
                        dynamic_ncols=True,
                        desc="Downloading",
                        unit_scale=True,
                        unit_divisor=1024, 
                        ascii=True
                )


    def download(self, save_path: str = None, progress_bar: bool = True) -> str:
        """
        Download the raster.

        Args:
            save_path (str, optional): Path where the file should be saved. 
                                    If not provided, it saves to the current working directory
                                    using the original filename and appropriate extension.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
        
        Returns:
            str: The path to save the raster.

        Raises:
            ValueError: If file_uuid is not set
            OSError: If there are issues with file operations        

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.download(save_path="path/to/save/")
        """
        if not self.uuid:
            raise ValueError("Raster UUID is required to download the raster file")
        
        save_path = self._get_save_path(save_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with self.api.get(f"{self.endpoint}download/", stream=True) as response:
            file_name = self._get_file_name(response)
            full_path = f"{save_path}/{file_name}"
            with open(full_path, 'wb') as f:
                pbar = self._create_progress_bar() if progress_bar else None
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                        pbar.refresh()
                if pbar:
                    pbar.close()

        return os.path.abspath(full_path)


    def get_content_file(self, save_path: str = None, progress_bar: bool = True) -> str: 
        """
        Get Raster Content URL

        Args:
            save_path (str, optional): Path where the file should be saved. 
                                    If not provided, it saves to the current working directory
                                    using the original filename and appropriate extension.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
        
        Returns:
            str: The path to save the raster.

        Raises:
            ValueError: If uuid is not set
            OSError: If there are issues with file operations   

        Examples:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster_tiff = raste.get_content_file()
        """
        if not self.uuid:
            raise ValueError("Raster UUID is required to download the raster content")
        
        save_path = self._get_save_path(save_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with self.api.get(f"{self.endpoint}content/", stream=True) as response:
            file_name = self._get_file_name(response)
            full_path = f"{save_path}/{file_name}"
            with open(full_path, 'wb') as f:
                pbar = self._create_progress_bar() if progress_bar else None
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                        pbar.refresh()
                if pbar:
                    pbar.close()

        return os.path.abspath(full_path)


    def get_render_png_url(self, x: int, y: int, z: int, **kwargs) -> str:
        """
        Get the PNG URL of the raster.

        Args:
            x (int): The x coordinate of the tile.
            y (int): The y coordinate of the tile.
            z (int): The zoom level of the tile.

        Keyword Args:
            indexes (str, optional): list of comma separated band indexes to be rendered. e.g. 1, 2, 3
            nodata (int, optional)
            expression (str, optional): band math expression. e.g. b1*b2+b3
            rescale (List, optional): comma (',') separated Min,Max range. Can set multiple time for multiple bands.
            color_formula (str, optional): Color formula. e.g. gamma R 0.5
            colormap_name (str, optional)
            colormap (str, optional): JSON encoded custom Colormap. e.g. {"0": "#ff0000", "1": "#00ff00"} or [[[0, 100], "#ff0000"], [[100, 200], "#00ff00"]]

        Returns:
            str: The PNG Render URL of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.get_tile_render_url(x=10, y=20, z=1)
        """
        params = clean_data({
            'indexes': kwargs.get('indexes'),
            'nodata': kwargs.get('nodata'),
            'expression': kwargs.get('expression'),
            'rescale': kwargs.get('rescale'),
            'color_formula': kwargs.get('color_formula'),
            'colormap_name': kwargs.get('colormap_name'),
            'colormap': kwargs.get('colormap')
        })
        query_string = urlencode(params)
        endpoint = f'{self.api.base_url}{self.endpoint}render/{z}/{x}/{y}.png'
        if query_string:
            endpoint = f'{endpoint}?{query_string}'

        if not self.api.access_token and self.api.apikey:
            endpoint = join_url_params(endpoint, {"apikey": self.api.apikey})
            
        return endpoint
    

    def get_tile_pbf_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}', indexes: str = None) -> str:
        """
        Get the URL of the tile.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.
            indexes (str, optional): list of comma separated band indexes to be rendered. e.g. 1, 2, 3

        Returns:
            str: The URL of the tile.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.get_tile_pbf_url(x=10, y=20, z=1)
        """
        params = clean_data({
            'indexes': indexes
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}tiles/{z}/{x}/{y}.pbf')
        endpoint = urljoin(endpoint, f'?{query_string}')

        if not self.api.access_token and self.api.apikey:
            endpoint = join_url_params(endpoint, {"apikey": self.api.apikey})

        return endpoint
    

    def get_tile_png_url(self, x: int = 'x', y: int = 'y', z: int = 'z') -> str:
        """
        Get the URL of the tile.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Returns:
            str: The URL of the tile.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.get_tile_png_url(x=10, y=20, z=1)
        """
        endpoint = f'{self.api.base_url}{self.endpoint}tiles/{z}/{x}/{y}.png'
            
        if not self.api.access_token and self.api.apikey:
            endpoint = f'{endpoint}?apikey={self.api.apikey}'

        return endpoint


    def get_tile_json(self) -> Dict:
        """
        Get the tile JSON of the raster.

        Returns:
            Dict: The tile JSON of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.get_tile_json()
        """
        endpoint = urljoin(self.endpoint, 'tilejson.json')
        return self.api.get(endpoint)


    def wmts(self, scale: int = None) -> str:
        """
        Get the WMTS URL

        Args:
            scale (int, optional): The scale of the raster. values are: 1, 2

        Returns:
            str: the raster WMTS URL

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.wmts(scale=1)
        """ 
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}wmts/')
        if scale:
            endpoint = f"{endpoint}?scale={scale}"

        if not self.api.access_token and self.api.apikey:
            endpoint = join_url_params(endpoint, {"apikey": self.api.apikey})

        return endpoint


    @property
    def settings(self) -> Dict:
        """
        Get the settings of the raster.

        Returns:
            Dict: The settings of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.settings
        """
        return super()._get_settings(self.endpoint)


    def set_settings(self, **kwargs) -> None:
        """
        Set the settings of the raster.

        Keyword Args:
            nodata (int): The nodata value of the raster.
            indexes (list[int]): The indexes of the raster.
            rescale (list[int]): The rescale of the raster.
            colormap_name (str): The colormap name of the raster.
            color_formula (str): The color formula of the raster.
            expression (str): The expression of the raster.
            exaggeraion (int): The exaggeraion of the raster.
            min_zoom (int): The min zoom of the raster.
            max_zoom (int): The max zoom of the raster.
            use_cache (bool): Whether to use cache of the raster.
            cache_until_zoom (int): The cache until zoom of the raster.


        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.set_settings(nodata=0, 
            ...                         indexes=[1], 
            ...                         rescale=[[0, 10000]], 
            ...                         colormap_name='gist_rainbow', 
            ...                         color_formula='Gamma R 0.5', 
            ...                         expression='b1 * 2', 
            ...                         exaggeraion=10, 
            ...                         min_zoom=0, 
            ...                         max_zoom=22, 
            ...                         use_cache=True, 
            ...                         cache_until_zoom=17)
        """
        visual_settings = {
            'nodata', 'indexes', 'rescale', 'colormap_name', 
            'color_formula', 'expression', 'exaggeraion'
        }
        tile_settings = {
            'min_zoom', 'max_zoom', 'use_cache', 'cache_until_zoom'
        }

        settings = self.settings

        for key, value in kwargs.items():
            if key in visual_settings:
                settings['visual_settings'][key] = value
            elif key in tile_settings:
                settings['tile_settings'][key] = value


        return super()._set_settings(self.endpoint, settings)


    def share(self, users: List['User']) -> None:
        """
        Shares the raster with specified users.

        Args:
            users (List[User]): The list of user objects to share the raster with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search="John")
            >>> raster.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the raster with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the raster with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search="John")
            >>> raster.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the raster is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)


    def seed_cache(self, from_zoom: int = None, to_zoom: int = None, extent: List[int] = None, workers: int = 1) -> List['Task']:
        """
        Seed the cache of the raster.

        Args:
            from_zoom (int, optional): The from zoom of the raster.
            to_zoom (int, optional): The to zoom of the raster.
            extent (List[int], optional): The extent of the raster.
            workers (int, optional): The number of workers to use. default is 1.

        Returns:
            Task: The task of the seed cache.

        Example:
            >>> from geobox import GeoboxClient 
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task = raster.seed_cache(from_zoom=0, to_zoom=22, extent=[0, 0, 100, 100], workers=1)
        """
        data = {
            'from_zoom': from_zoom,
            'to_zoom': to_zoom,
            'extent': extent,
            'workers': workers
        }
        return super()._seed_cache(self.endpoint, data)


    def clear_cache(self) -> None:
        """
        Clear the cache of the raster.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.clear_cache()
        """
        super()._clear_cache(self.endpoint)
        

    @property
    def cache_size(self) -> int:
        """
        Get the size of the cache of the raster.

        Returns:
            int: The size of the cache of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.raster import Raster
            >>> client = GeoboxClient()
            >>> raster = Raster.get_raster(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> raster.cache_size
        """
        return super()._cache_size(self.endpoint)
