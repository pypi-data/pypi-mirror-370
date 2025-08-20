from typing import TYPE_CHECKING, Dict, List, Optional, Union

from .base import Base

if TYPE_CHECKING:
    from .api import GeoboxClient
    from .user import User

class VectorLayerVersion(Base):

    BASE_ENDPOINT = 'vectorLayerVersions/'

    def __init__(self, 
                 api: 'GeoboxClient',
                 uuid: str,
                 data: Optional[Dict] = {}):
        """
        Initialize a vector layer version instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the version.
            data (Dict): The data of the version.
        """
        super().__init__(api, uuid=uuid, data=data)
    

    @classmethod
    def get_versions(cls, api: 'GeoboxClient', **kwargs) -> Union[List['VectorLayerVersion'], int]:
        """
        Get list of versions with optional filtering and pagination.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

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
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> versions = VectorLayerVersion.get_versions(client, q="name LIKE '%My version%'")
            or
            >>> versions = client.get_versions(q="name LIKE '%My version%'")
        """
        params = {
            'layer_id': kwargs.get('layer_id'),
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
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: VectorLayerVersion(api, item['uuid'], item))


    @classmethod
    def get_version(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'VectorLayerVersion':
        """
        Get a version by its UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the version to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            VectorLayerVersion: The vector layer version object.

        Raises:
            NotFoundError: If the version with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> version = VectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> version = client.get_version(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: VectorLayerVersion(api, item['uuid'], item))
    

    @classmethod
    def get_version_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> 'VectorLayerVersion':
        """
        Get a version by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the version to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            VectorLayerVersion | None: returns the version if a version matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> version = VectorLayerView.get_version_by_name(client, name='test')
            or
            >>> version = client.get_version_by_name(name='test')
        """
        versions = cls.get_versions(api, q=f"name = '{name}'", user_id=user_id)
        if versions and versions[0].name == name:
            return versions[0]
        else:
            return None


    def update(self, **kwargs) -> Dict:
        """
        Update the version.

        Args:
            name (str): The name of the version.
            display_name (str): The display name of the version.
            description (str): The description of the version.

        Returns:
            Dict: The updated version data.

        Raises:
            ValidationError: If the version data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> version = VectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> version.update_version(display_name="New Display Name")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),   
            "description": kwargs.get('description'),
        }
        return super()._update(self.endpoint, data)


    def delete(self) -> None:
        """
        Delete the version.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> version = VectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> version.delete()
        """
        super().delete(self.endpoint)


    def share(self, users: List['User']) -> None:
        """
        Shares the version with specified users.

        Args:
            users (List[User]): The list of user objects to share the version with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> version = VectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> version.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the version with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the version with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> version = VectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> version.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the version is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.version import VectorLayerVersion
            >>> client = GeoboxClient()
            >>> version = VectorLayerVersion.get_version(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> version.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)

    