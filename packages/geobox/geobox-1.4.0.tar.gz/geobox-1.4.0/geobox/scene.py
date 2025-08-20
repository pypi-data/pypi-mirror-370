from typing import List, Dict, Optional, TYPE_CHECKING, Union
from urllib.parse import urljoin

from .base import Base

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User 

class Scene(Base):

    BASE_ENDPOINT = 'scenes/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str,
                 data: Optional[Dict] = {}):
        """
        Initialize a Scene instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the Scene.
            data (Dict): The data of the Scene.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    def get_scenes(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Scene'], int]:
        """
        Get list of scenes with optional filtering and pagination.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

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
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scenes = Scene.get_scenes(client, q="name LIKE '%My scene%'")
            or
            >>> scenes = client.get_scenes(q="name LIKE '%My scene%'")
        """
        params = {
           'f': 'json',
           'q': kwargs.get('q'),
           'search': kwargs.get('search'),
           'search_fields': kwargs.get('search_fields'),
           'order_by': kwargs.get('order_by'),
           'return_count': kwargs.get('return_count', False),
           'skip': kwargs.get('skip', 0),
           'limit': kwargs.get('limit', 10),
           'user_id': kwargs.get('user_id'),
           'shared': kwargs.get('shared', False)
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Scene(api, item['uuid'], item))
    

    @classmethod
    def create_scene(cls, 
                     api: 'GeoboxClient', 
                     name: str, 
                     display_name: str = None, 
                     description: str = None, 
                     settings: Dict = {}, 
                     thumbnail: str = None, 
                     user_id: int = None) -> 'Scene':
        """
        Create a new scene.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
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
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.create_scene(client, name="my_scene")
            or
            >>> scene = client.create_scene(name="my_scene")
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "settings": settings,
            "thumbnail": thumbnail,
            "user_id": user_id,
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: Scene(api, item['uuid'], item))

    
    @classmethod
    def get_scene(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Scene':
        """
        Get a scene by its UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the scene to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Scene: The scene object.

        Raises:
            NotFoundError: If the scene with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> scene = client.get_scene(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Scene(api, item['uuid'], item))


    @classmethod
    def get_scene_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Scene', None]:
        """
        Get a scene by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the scene to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Scene | None: returns the scene if a scene matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene_by_name(client, name='test')
            or
            >>> scene = client.get_scene_by_name(name='test')
        """
        scenes = cls.get_scenes(api, q=f"name = '{name}'", user_id=user_id)
        if scenes and scenes[0].name == name:
            return scenes[0]
        else:
            return None


    def update(self, **kwargs) -> Dict:
        """
        Update the scene.

        Keyword Args:
            name (str): The name of the scene.
            display_name (str): The display name of the scene.
            description (str): The description of the scene.
            settings (Dict): The settings of the scene.
            thumbnail (str): The thumbnail of the scene.

        Returns:
            Dict: The updated scene data.

        Raises:
            ApiRequestError: If the API request fails.
            ValidationError: If the scene data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> scene.update(display_name="New Display Name")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
            "settings": kwargs.get('settings'),
            "thumbnail": kwargs.get('thumbnail')
        }
        return super()._update(self.endpoint, data)
    

    def delete(self) -> None:
        """
        Delete the scene.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> scene.delete()
        """
        super().delete(self.endpoint)


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the scene.

        Returns:
            str: The thumbnail of the scene.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> scene.thumbnail
            'https://example.com/thumbnail.png'
        """
        return super().thumbnail()
    

    def share(self, users: List['User']) -> None:
        """
        Shares the scene with specified users.

        Args:
            users (List[User]): The list of user objects to share the scene with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> scene.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the scene with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the scene with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> scene.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the scene is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.scene import Scene
            >>> client = GeoboxClient()
            >>> scene = Scene.get_scene(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> scene.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)
