from urllib.parse import urljoin, urlencode
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from .utils import clean_data
from .raster import Raster

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User
    from .task import Task

class Mosaic(Raster):
    """
    A class to represent a Mosaic in Geobox.

    This class provides methods to interact with the mosaic in Geobox.
    It inherits from the Raster class and provides additional methods to interact with the mosaic.
    It also provides properties to access the mosaic data, and a method to update the mosaic.
    """
    BASE_ENDPOINT: str = 'mosaics/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str, 
                 data: Optional[Dict] = {}):
        """
        Initialize a Mosaic instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the mosaic.
            data (Dict, optional): The data of the mosaic.
        """
        super().__init__(api, uuid, data)
    

    @classmethod
    def get_mosaics(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Mosaic'], int]:
        """
        Get a list of mosaics.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

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
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaics = Mosaic.get_mosaics(client, q="name LIKE '%GIS%'")
            or
            >>> mosaics = client.get_mosaics(q="name LIKE '%GIS%'")
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
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Mosaic(api, item['uuid'], item))
    
    
    @classmethod
    def get_mosaics_by_ids(cls, api: 'GeoboxClient', ids: List[str], user_id: int = None) -> List['Mosaic']:
        """
        Get mosaics by their IDs.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            ids (List[str]): The IDs of the mosaics.
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[Mosaic]: A list of Mosaic instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaics = Mosaic.get_mosaics_by_ids(client, ids=['1, 2, 3'])
            or
            >>> mosaics = client.get_mosaics_by_ids(ids=['1, 2, 3'])
        """
        params = {
            'ids': ids,
            'user_id': user_id
        }
        endpoint = urljoin(cls.BASE_ENDPOINT, 'get-mosaics/')
        return super()._get_list_by_ids(api, endpoint, params, factory_func=lambda api, item: Mosaic(api, item['uuid'], item))

    
    @classmethod
    def create_mosaic(cls,
                      api: 'GeoboxClient',
                      name:str,
                      display_name: str = None,
                      description: str = None,
                      pixel_selection: str = None,
                      min_zoom: int = None,
                      user_id: int = None) -> 'Mosaic':
        """
        Create New Raster Mosaic

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
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
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.create_mosaic(client, name='mosaic_name')
            or
            >>> mosaic = client.create_mosaic(name='mosaic_name')
        """
        data = {
            'name': name,
            'display_name': display_name,
            'description': description,
            'pixel_selection': pixel_selection,
            'min_zoom': min_zoom,
            'user_id': user_id
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: Mosaic(api, item['uuid'], item))
    

    @classmethod
    def get_mosaic(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Mosaic':
        """
        Get a mosaic by uuid.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the mosaic.
            user_id (int, optional): specific user. privileges required.

        Returns:
            Mosaic: The mosaic object.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> mosaic = client.get_mosaic(uuid="12345678-1234-5678-1234-567812345678")
        """      
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Mosaic(api, item['uuid'], item))


    @classmethod
    def get_mosaic_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Mosaic', None]:
        """
        Get a mosaic by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the mosaic to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Mosaic | None: returns the mosaic if a mosaic matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic_by_name(client, name='test')
            or
            >>> mosaic = client.get_mosaic_by_name(name='test')
        """
        mosaics = cls.get_mosaics(api, q=f"name = '{name}'", user_id=user_id)
        if mosaics and mosaics[0].name == name:
            return mosaics[0]
        else:
            return None


    def update(self, **kwargs) -> Dict:
        """
        Update a mosaic.

        Keyword Args:
            name (str): The name of the mosaic.
            display_name (str): The display name of the mosaic.
            description (str): The description of the mosaic.
            pixel_selection (str): The pixel selection of the mosaic.
            min_zoom (int): The minimum zoom of the mosaic.

        Returns:
            Dict: the updated data

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.update_mosaic(name='new_name', display_name='new_display_name', description='new_description', pixel_selection='new_pixel_selection', min_zoom=10)
        """
        data = {
            'name': kwargs.get('name'),
            'display_name': kwargs.get('display_name'),
            'description': kwargs.get('description'),
            'pixel_selection': kwargs.get('pixel_selection'),
            'min_zoom': kwargs.get('min_zoom')
        }
        return super()._update(self.endpoint, data)


    def delete(self) -> None:
        """
        Delete the mosaic.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.delete()
        """
        super().delete()
    

    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail of the mosaic.

        Returns:
            str: The thumbnail url of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.thumbnail
        """
        return super().thumbnail


    def get_point(self, lat: float, lng: float) -> List[float]:
        """
        Get the points of the mosaic.

        Args:
            lat (float): The latitude of the point.
            lng (float): The longitude of the point.

        Returns:
            List[float]: The points of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.get_point(lat=60, lng=50)
        """
        return super().get_point(lat, lng)


    def get_render_png_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}', **kwargs) -> str:
        """
        Get the tile render URL of the mosaic.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Keyword Args:
            indexes (str, optional): list of comma separated band indexes to be rendered. e.g. 1, 2, 3
            nodata (int, optional)
            expression (str, optional): band math expression. e.g. b1*b2+b3
            rescale (List, optional): comma (',') separated Min,Max range. Can set multiple time for multiple bands.
            color_formula (str, optional): Color formula. e.g. gamma R 0.5
            colormap_name (str, optional)
            colormap (str, optional): JSON encoded custom Colormap. e.g. {"0": "#ff0000", "1": "#00ff00"} or [[[0, 100], "#ff0000"], [[100, 200], "#00ff00"]]

        Returns:
            str: The tile render URL of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.get_tile_render_url(x=1, y=1, z=1)
        """
        return super().get_render_png_url(x, y, z, **kwargs)
    

    def get_tile_png_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}') -> str:
        """
        Get the tile PNG URL of the mosaic.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optional): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Returns:
            str: The tile PNG URL of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.get_tile_png_url(x=1, y=1, z=1)
        """
        return super().get_tile_png_url(x, y, z)
    

    def get_tile_json(self) -> str:
        """
        Get the tile JSON of the raster.

        Returns:
            str: The tile JSON of the raster.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.get_tile_json()
        """
        return super().get_tile_json()
    

    def wmts(self, scale: int = None) -> str:
        """
        Get the WMTS URL

        Args:
            scale (int, optional): The scale of the raster. values are: 1, 2

        Returns:
            str: The WMTS URL of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.wmts(scale=1)
        """
        return super().wmts(scale)

    @property
    def settings(self) -> Dict:
        """
        Get the settings of the mosaic.

        Returns:
            Dict: The settings of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.settings
        """
        return super().settings
    
    
    def set_settings(self, **kwargs) -> None:
        """
        Set the settings of the mosaic.

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

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.set_settings(nodata=0, 
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
        return super().set_settings(**kwargs)


    def get_rasters(self, user_id: int = None) -> List[Raster]:
        """
        Get the rasters of the mosaic

        Args:
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[Raster]: The rasters of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> rasters = mosaic.get_rasters()
        """
        params = clean_data({
            'user_id': user_id
        })
        query_string = urlencode(params)
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/rasters?{query_string}')
        response = self.api.get(endpoint)
        return [Raster(self.api, raster_data['uuid'], raster_data) for raster_data in response]
    

    def add_rasters(self, rasters: List['Raster']) -> None:
        """
        Add a raster to the mosaic.

        Args:
            rasters (List[Raster]): list of raster objects to add

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> rasters = client.get_rasters()
            >>> mosaic.add_raster(rasters=rasters)
        """
        data = clean_data({
            'raster_ids': [raster.id for raster in rasters]
        })
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/rasters/')
        self.api.post(endpoint, data, is_json=False)
    

    def remove_rasters(self, rasters: List['Raster']) -> None:
        """
        Remove a raster from the mosaic.

        Args:
            rasters (List[Raster]): list of raster objects to remove

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> rasters = client.get_raster()
            >>> mosaic.remove_rasters(rasters=rasters)
        """
        param = clean_data({
            'raster_ids': [raster.id for raster in rasters]
        })
        query_string = urlencode(param)
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/rasters/?{query_string}')
        self.api.delete(endpoint, is_json=False)


    def share(self, users: List['User']) -> None:
        """
        Shares the mosaic with specified users.

        Args:
            users (List[User]): The list of user objects to share the mosaic with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> mosaic.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the mosaic with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the mosaic with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> mosaic.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the file is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)


    def seed_cache(self, 
                   from_zoom: int = None, 
                   to_zoom: int = None, 
                   extent: List[int] = None, 
                   workers: int = 1) -> List['Task']:
        """
        Seed the cache of the mosaic.

        Args:
            from_zoom (int, optional): The from zoom of the mosaic.
            to_zoom (int, optional): The to zoom of the mosaic.
            extent (list[int], optional): The extent of the mosaic.
            workers (int, optional): The number of workers to use. default is 1.

        Returns:
            List[Task]: The task of the seed cache.

        Example:
            >>> from geobox import GeoboxClient 
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task = mosaic.seed_cache(from_zoom=0, to_zoom=22, extent=[0, 0, 100, 100], workers=1)
        """
        data = {
            'from_zoom': from_zoom,
            'to_zoom': to_zoom,
            'extent': extent,
            'workers': workers
        }
        return super()._seed_cache(endpoint=self.endpoint, data=data)


    def clear_cache(self) -> None:
        """
        Clear the cache of the mosaic.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.clear_cache()
        """
        return super().clear_cache()


    @property
    def cache_size(self) -> int:
        """
        Get the size of the cache of the mosaic.

        Returns:
            int: The size of the cache of the mosaic.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.mosaic import Mosaic
            >>> client = GeoboxClient()
            >>> mosaic = Mosaic.get_mosaic(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> mosaic.cache_size
        """
        return super().cache_size
