from typing import Dict, List, Optional, Optional, Union, TYPE_CHECKING
from urllib.parse import urljoin, urlencode

from .base import Base
from .exception import ApiRequestError

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User

class Model(Base):
    """
    A class representing a 3D model in Geobox.
    """
    BASE_ENDPOINT = '3dmodels/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str, 
                 data: Optional[Dict] = {}):
        """
        Initialize a 3D Model instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the model.
            data (Dict, optional): The data of the model.
        """
        super().__init__(api, uuid=uuid, data=data)
    

    @classmethod
    def get_models(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Model'], int]:
        """
        Get a list of models with optional filtering and pagination.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

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
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> models = Model.get_models(api=client, 
            ...                           search="my_model",
            ...                           search_fields="name, description",
            ...                           order_by="name A",
            ...                           return_count=True,
            ...                           skip=0,
            ...                           limit=10,
            ...                           shared=False)
            or
            >>> models = client.get_models(search="my_model",
            ...                           search_fields="name, description",
            ...                           order_by="name A",
            ...                           return_count=True,
            ...                           skip=0,
            ...                           limit=10,
            ...                           shared=False)
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
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Model(api, item['uuid'], item))
    

    @classmethod
    def get_model(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Model':
        """
        Get a model by its UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the model to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Model: The model object.

        Raises:
            NotFoundError: If the model with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> model = client.get_model(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Model(api, item['uuid'], item))


    @classmethod
    def get_model_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Model', None]:
        """
        Get a model by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the model to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Model | None: returns the model if a model matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model_by_name(client, name='test')
            or
            >>> model = client.get_model_by_name(name='test')
        """
        models = cls.get_models(api, q=f"name = '{name}'", user_id=user_id)
        if models and models[0].name == name:
            return models[0]
        else:
            return None
    
    
    def update(self, **kwargs) -> Dict:
        """
        Update the model's properties.

        Keyword Args:
            name (str): The new name for the model.
            display_name (str): The new display name.
            description (str): The new description for the model.
            settings (Dict): The new settings for the model.
            thumbnail (str): The new thumbnail for the model.

        Returns:
            Dict: The updated model data.

        Raises:
            ValidationError: If the update data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> settings = {
            ...    "model_settings": {
            ...    "scale": 0,
            ...    "rotation": [
            ...        0
            ...    ],
            ...    "location": [
            ...        0
            ...    ]
            ...    },
            ...    "view_settings": {
            ...    "center": [
            ...        0
            ...    ],
            ...    "zoom": 0,
            ...    "pitch": 0,
            ...    "bearing": 0
            ...    }
            ... }
            >>> model.update(name="new_name", description="new_description", settings=settings, thumbnail="new_thumbnail")
        """
        data = {
            'name': kwargs.get('name'),
            'display_name': kwargs.get('display_name'),
            'description': kwargs.get('description'),
            'settings': kwargs.get('settings'),
            'thumbnail': kwargs.get('thumbnail')
        }
        return super()._update(self.endpoint, data)
    

    def delete(self) -> None:
        """
        Delete the model.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> model.delete()
        """
        super().delete(self.endpoint)


    def get_content(self) -> bytes:
        """
        Get the raw content of the 3D model.

        Returns:
            bytes: The raw content of the 3D model in glTF format.

        Raises:
            ApiRequestError: If the API request fails.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> content = model.get_content()
            >>> # Save the content to a file
            >>> with open('model.gltf', 'wb') as f:
            ...     f.write(content)
        """
        endpoint = urljoin(self.api.base_url, f'{self.endpoint}/content/')
        response = self.api.session.get(endpoint)
        
        if response.status_code != 200:
            raise ApiRequestError(f"Failed to get model content: {response.status_code}")
            
        return response.content


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the model.

        Returns:
            str: The thumbnail of the model.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> model.thumbnail
        """
        return super().thumbnail()
    

    def share(self, users: List['User']) -> None:
        """
        Shares the model with specified users.

        Args:
            users (List[users]): The list of user objects to share the model with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> model.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the model with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the model with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> model.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the model is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.model3d import Model
            >>> client = GeoboxClient()
            >>> model = Model.get_model(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> model.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)
