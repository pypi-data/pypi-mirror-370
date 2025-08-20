from urllib.parse import urljoin
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from .base import Base
from .vectorlayer import VectorLayer
from .view import VectorLayerView
from .task import Task

if TYPE_CHECKING:
    from . import GeoboxClient 
    from .user import User 

class Tileset(Base):
    """
    A class to interact with tilesets in Geobox.

    This class provides functionality to interact with tilesets in Geobox.
    It supports various operations including CRUD operations on tilesets, as well as advanced operations like getting layers, and sharing tilesets.
    """
    BASE_ENDPOINT: str = 'tilesets/'

    def __init__(self, 
                api: 'GeoboxClient', 
                uuid: str, 
                data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Tilesets object.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the tileset.
            data (Dict, optional): The data of the tileset.
        """
        super().__init__(api=api, uuid=uuid, data=data)


    @classmethod
    def create_tileset(cls, api: 'GeoboxClient', name: str, layers: List[Union['VectorLayer', 'VectorLayerView']], display_name: str = None, description: str = None,
                        min_zoom: int = None, max_zoom: int = None, user_id: int = None) -> 'Tileset':
        """
        Create a new tileset.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): The name of the tileset.
            layers (List[VectorLayer | VectorLayerView]): list of vectorlayer and view objects to add to tileset.
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
            >>> tileset = Tileset.create_tileset(client, 
            ...                                     name="your_tileset_name", 
            ...                                     display_name="Your Tileset", 
            ...                                     description="Your description", 
            ...                                     min_zoom=0, 
            ...                                     max_zoom=14, 
            ...                                     layers=[layer, view])
            or 
            >>> tileset = client.create_tileset(name="your_tileset_name", 
            ...                                     display_name="Your Tileset", 
            ...                                     description="Your description", 
            ...                                     min_zoom=0, 
            ...                                     max_zoom=14, 
            ...                                     layers=[layer, view])
        """
        formatted_layers = []
        for item in layers:
            if type(item) == VectorLayer:
                item_type = 'vector'

            elif type(item) == VectorLayerView:
                item_type = 'view'

            else:
                continue

            formatted_layers.append({
                'layer_type': item_type,
                'layer_uuid': item.uuid
            })

        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "min_zoom": min_zoom,
            "max_zoom": max_zoom,
            "layers": formatted_layers,
            "user_id": user_id
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: Tileset(api, item['uuid'], item))


    @classmethod
    def get_tilesets(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Tileset'], int]:
        """
        Retrieves a list of tilesets.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
        
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
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tilesets = Tileset.get_tilesets(client,
            ...     q="name LIKE '%your_tileset_name%'",
            ...     order_by="name A",
            ...     skip=0,
            ...     limit=10,
            ... )
            or
            >>> tilesets = client.get_tilesets(q="name LIKE '%your_tileset_name%'",
            ...     order_by="name A",
            ...     skip=0,
            ...     limit=10,
            ... )
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q', None),
            'search': kwargs.get('search', None),
            'search_fields': kwargs.get('search_fields', None),
            'order_by': kwargs.get('order_by', None),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id', None),
            'shared': kwargs.get('shared', False)
        }
        return super()._get_list(api=api, endpoint=cls.BASE_ENDPOINT, params=params, factory_func=lambda api, item: Tileset(api, item['uuid'], item))
    

    @classmethod
    def get_tilesets_by_ids(cls, api: 'GeoboxClient', ids: List[str], user_id: int = None) -> List['Tileset']:
        """
        Retrieves a list of tilesets by their IDs.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            ids (List[str]): The list of tileset IDs.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            List[Tileset]: A list of Tileset instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tilesets = Tileset.get_tilesets_by_ids(client, ids=['123', '456'])
            or
            >>> tilesets = client.get_tilesets_by_ids(ids=['123', '456'])
        """
        params = {
            'ids': ids,
            'user_id': user_id
        }
        return super()._get_list_by_ids(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Tileset(api, item['uuid'], item))


    @classmethod
    def get_tileset(cls, api: 'GeoboxClient', uuid: str) -> 'Tileset':
        """
        Retrieves a tileset by its UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the tileset.

        Returns:
            Tileset: The retrieved tileset instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> tileset = client.get_tileset(uuid="12345678-1234-5678-1234-567812345678")
        """
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, factory_func=lambda api, item: Tileset(api, item['uuid'], item))


    @classmethod
    def get_tileset_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Tileset', None]:
        """
        Get a tileset by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the tileset to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Tileset | None: returns the tileset if a tileset matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = VectorLayer.get_tileset_by_name(client, name='test')
            or
            >>> tileset = client.get_tileset_by_name(name='test')
        """
        tilesets = cls.get_tilesets(api, q=f"name = '{name}'", user_id=user_id)
        if tilesets and tilesets[0].name == name:
            return tilesets[0]
        else:
            return None


    def update(self, **kwargs) -> None:
        """
        Updates the properties of the tileset.

        Keyword Args:
            name (str): The new name of the tileset.
            display_name (str): The new display name of the tileset.
            description (str): The new description of the tileset.
            min_zoom (int): The new minimum zoom level of the tileset.
            max_zoom (int): The new maximum zoom level of the tileset.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.update_tileset(
            ...     name="new_name",
            ...     display_name="New Display Name",
            ...     description="New description",
            ...     min_zoom=0,
            ...     max_zoom=14
            ... )
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "description": kwargs.get('description'),
            "min_zoom": kwargs.get('min_zoom'),
            "max_zoom": kwargs.get('max_zoom')
        }

        return super()._update(urljoin(self.BASE_ENDPOINT, f'{self.uuid}/'), data)


    def delete(self) -> None:
        """
        Deletes the tileset.

        Raises:
            ValueError: if the tileset uuid is not set.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.delete()
        """
        super().delete(urljoin(self.BASE_ENDPOINT, f'{self.uuid}/'))
    
    
    def get_layers(self, **kwargs) -> List['VectorLayer']:
        """
        Retrieves the layers of the tileset with optional parameters.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if True, returns the total number of layers matching the query. default is False.
            skip (int): number of records to skip. default is 0.
            limit (int): number of records to return. default is 10.
            user_id (int): specific user. privileges required.
            shared (bool): if True, returns only the layers that has been shared with you. default is False.

        Returns:
            List: A list of VectorLayer instances.

        Raises:
            ApiRequestError: If the API request fails.

        Example:

        Returns:
            List: A list of VectorLayer or VectorLayerView instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layers = tileset.get_layers()
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'seacrh_fields': kwargs.get('seacrh_fields'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)
        }
        endpoint = urljoin(self.BASE_ENDPOINT, f'{self.uuid}/layers/')
        return super()._get_list(self.api, endpoint, params, factory_func=lambda api, item: VectorLayer(api, item['uuid'], item['layer_type'], item) if not item['is_view'] else \
                                                                                            VectorLayerView(api, item['uuid'], item['layer_type'], item)                                    )


    def add_layer(self, layer: Union['VectorLayer', 'VectorLayerView']) -> None:
        """
        Adds a layer to the tileset.

        Args:
            layer (VectorLayer | VectorLayerView): the layer object to add to the tileset

        Returns:
            None

        Raises:
            ValueError: if the layer input is not a 'VectorLayer' or 'VetorLayerview' object

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.add_layer(layer)
        """
        if type(layer) == VectorLayer:
            layer_type = 'vector'

        elif type(layer) == VectorLayerView:
            layer_type = 'view'

        else:
            raise ValueError("layer input must be either 'VectorLayer' or 'VetorLayerview' object")

        data = {
            "layer_type": layer_type,
            "layer_uuid": layer.uuid
        }

        endpoint = urljoin(self.endpoint, 'layers/')
        return self.api.post(endpoint, data, is_json=False)


    def delete_layer(self, layer: Union['VectorLayer', 'VectorLayerView']) -> None:
        """
        Deletes a layer from the tileset.

        Args:
            layer (VectorLayer | VectorLayerView): the layer object to delete from the tileset

        Returns:
            None

        Raises:
            ValueError: if the layer input is not a 'VectorLayer' or 'VetorLayerview' object

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.delete_layer(layer)
        """
        if type(layer) == VectorLayer:
            layer_type = 'vector'

        elif type(layer) == VectorLayerView:
            layer_type = 'view'

        else:
            raise ValueError("layer input must be either 'VectorLayer' or 'VetorLayerview' object")

        data = {
            "layer_type": layer_type,
            "layer_uuid": layer.uuid
        }

        endpoint = urljoin(self.endpoint, 'layers/')
        return self.api.delete(endpoint, data, is_json=False)


    def share(self, users: List['User']) -> None:
        """
        Shares the file with specified users.

        Args:
            users (List[User]): The list of user IDs to share the file with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_usesrs(search='John')
            >>> tileset.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the file with specified users.

        Args:
            users (List[User]): The list of user IDs to unshare the file with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_usesrs(search='John')
            >>> tileset.unshare(users=users)
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
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)
        

    def get_tile_json(self) -> Dict:
        """
        Retrieves the tile JSON configuration.

        Returns:
            Dict: The tile JSON configuration.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.get_tile_json()
        """ 
        endpoint = urljoin(self.endpoint, 'tilejson.json/')
        return self.api.get(endpoint)


    def update_tileset_extent(self) -> Dict:
        """
        Updates the extent of the tileset.

        Returns:
            Dict: The response from the API.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.update_tileset_extent()
        """
        endpoint = urljoin(self.endpoint, 'updateExtent/')
        return self.api.post(endpoint)


    def get_tile_pbf_url(self, x: 'int' = '{x}', y: int = '{y}', z: int = '{z}') -> str:
        """
        Retrieves a tile from the tileset.

        Args:
            x (int, optional): The x coordinate of the tile.
            y (int, optioanl): The y coordinate of the tile.
            z (int, optional): The zoom level of the tile.

        Returns:
            str: The url of the tile.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.get_tile_tileset(x=1, y=1, z=1)
        """
        endpoint = f'{self.api.base_url}{self.endpoint}tiles/{z}/{x}/{y}.pbf'

        if not self.api.access_token and self.api.apikey:
            endpoint = f'{endpoint}?apikey={self.api.apikey}'

        return endpoint


    def seed_cache(self, from_zoom: int = 0, to_zoom: int = 14, extent: list = [], workers: int = 1, user_id: int = 0) -> List['Task']:
        """
        Seeds the cache of the tileset.

        Args:
            from_zoom (int, optional): The starting zoom level.
            to_zoom (int, optional): The ending zoom level.
            extent (list, optional): The extent of the tileset.
            workers (int, optional): The number of workers to use.
            user_id (int, optional): The user ID.

        Returns:
            List[Task]: list of task objects.

        Raises:
            ValueError: If the number of workers is not one of the following: 1, 2, 4, 8, 12, 16, 20, 24.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.seed_cache(from_zoom=0, to_zoom=14, extent=[], workers=1)
        """
        data = {
            "from_zoom": from_zoom,
            "to_zoom": to_zoom,
            "extent": extent,
            "workers": workers,
            "user_id": user_id
        }
        return super()._seed_cache(endpoint=self.endpoint, data=data)


    def update_cache(self, from_zoom: int, to_zoom: int, extents: List[List[float]] = None, user_id: int = 0) -> List['Task']:
        """
        Updates the cache of the tileset.

        Args:
            from_zoom (int): The starting zoom level.
            to_zoom (int): The ending zoom level.
            extents (List[List[float]], optional): The list of extents to update the cache for.
            user_id (int, optional): The user ID.

        Returns:
            List[Task]: list of task objects.
        """
        data = {
            "from_zoom": from_zoom,
            "to_zoom": to_zoom,
            "extents": extents,
            "user_id": user_id
        }
        return super()._update_cache(endpoint=self.endpoint, data=data)


    @property
    def cache_size(self) -> int:
        """
        Retrieves the size of the cache of the tileset.

        Returns:
            int: The size of the cache of the tileset.
        """
        return super()._cache_size(endpoint=self.endpoint)


    def clear_cache(self) -> None:
        """
        Clears the cache of the tileset.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.tileset import Tileset
            >>> client = GeoboxClient()
            >>> tileset = Tileset.get_tileset(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tileset.clear_cache()
        """
        super()._clear_cache(endpoint=self.endpoint)
