from typing import List, Dict, Optional, TYPE_CHECKING, Union
from urllib.parse import urljoin

from .base import Base

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User

class Dashboard(Base):

    BASE_ENDPOINT = 'dashboards/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str,
                 data: Optional[Dict] = {}):
        """
        Initialize a Dashboard instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the Dashboard.
            data (Dict, optional): The data of the Dashboard.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    def get_dashboards(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Dashboard'], int]:
        """
        Get list of Dashboards

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
            shared (bool): Whether to return shared Dashboards. default is False.

        Returns:
            List[Dashboard] | int: A list of Dashboard instances or the total number of Dashboards.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboards = Dashboard.get_dashboards(client)
            or
            >>> dashboards = client.get_dashboards()
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
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Dashboard(api, item['uuid'], item))
    

    @classmethod
    def create_dashboard(cls, 
                     api: 'GeoboxClient', 
                     name: str, 
                     display_name: str = None, 
                     description: str = None, 
                     settings: Dict = {}, 
                     thumbnail: str = None, 
                     user_id: int = None) -> 'Dashboard':
        """
        Create a new Dashboard.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
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
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.create_dashboard(client, name="my_dashboard")
            or
            >>> dashboard = client.create_dashboard(name="my_dashboard")
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "settings": settings,
            "thumbnail": thumbnail,
            "user_id": user_id,
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: Dashboard(api, item['uuid'], item))

    
    @classmethod
    def get_dashboard(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Dashboard':
        """
        Get a Dashboard by its UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the Dashboard to get.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            Dashboard: The dashboard object.

        Raises:
            NotFoundError: If the Dashboard with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> dashboard = client.get_dashboard(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Dashboard(api, item['uuid'], item))


    @classmethod
    def get_dashboard_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Dashboard', None]:
        """
        Get a dashboard by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the dashboard to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Dashboard | None: returns the dashboard if a dashboard matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard_by_name(client, name='test')
            or
            >>> dashboard = client.get_dashboard_by_name(name='test')
        """
        dashboards = cls.get_dashboards(api, q=f"name = '{name}'", user_id=user_id)
        if dashboards and dashboards[0].name == name:
            return dashboards[0]
        else:
            return None


    def update(self, **kwargs) -> Dict:
        """
        Update the Dashboard

        Keyword Args:
            name (str): The name of the Dashboard.
            display_name (str): The display name of the Dashboard.
            description (str): The description of the Dashboard.
            settings (Dict): The settings of the Dashboard.
            thumbnail (str): The thumbnail of the Dashboard.

        Returns:
            Dict: The updated Dashboard data.

        Raises:
            ValidationError: If the Dashboard data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> dashboard.update(display_name="New Display Name")
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
        Delete the dashboard.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> dashboard.delete()
        """        
        super().delete(self.endpoint)


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the dashboard.

        Returns:
            str: The thumbnail of the dashboard.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> dashboard.thumbnail
            'https://example.com/thumbnail.png'
        """
        return super().thumbnail()
    

    def share(self, users: List['User']) -> None:
        """
        Shares the Dashboard with specified users.

        Args:
            users (List[User]): The list of user objects to share the Dashboard with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> dashboard.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the Dashboard with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the Dashboard with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> dashboard.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the dashboard is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.dashboard import Dashboard
            >>> client = GeoboxClient()
            >>> dashboard = Dashboard.get_dashboard(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> dashboard.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)
