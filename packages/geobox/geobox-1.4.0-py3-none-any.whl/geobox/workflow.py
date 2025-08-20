from typing import List, Dict, Optional, TYPE_CHECKING, Union

from .base import Base

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User

class Workflow(Base):

    BASE_ENDPOINT = 'workflows/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str,
                 data: Optional[Dict] = {}):
        """
        Initialize a workflow instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the workflow.
            data (Dict): The data of the workflow.
        """
        super().__init__(api, uuid=uuid, data=data)


    @classmethod
    def get_workflows(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Workflow'], int]:
        """
        Get list of workflows with optional filtering and pagination.

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
            shared (bool): Whether to return shared workflows. default is False.

        Returns:
            List[Workflow] | int: A list of workflow instances or the total number of workflows.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflows = Workflow.get_workflows(client, q="name LIKE '%My workflow%'")
            or
            >>> workflows = client.get_workflows(q="name LIKE '%My workflow%'")
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
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Workflow(api, item['uuid'], item))
    

    @classmethod
    def create_workflow(cls, 
                     api: 'GeoboxClient', 
                     name: str, 
                     display_name: str = None, 
                     description: str = None, 
                     settings: Dict = {}, 
                     thumbnail: str = None, 
                     user_id: int = None) -> 'Workflow':
        """
        Create a new workflow.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): The name of the Workflow.
            display_name (str): The display name of the workflow.
            description (str): The description of the workflow.
            settings (Dict): The settings of the workflow.
            thumbnail (str): The thumbnail of the workflow.
            user_id (int): Specific user. privileges workflow.

        Returns:
            Workflow: The newly created workflow instance.

        Raises:
            ValidationError: If the workflow data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.create_workflow(client, name="my_workflow")
            or
            >>> workflow = client.create_workflow(name="my_workflow")
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "settings": settings,
            "thumbnail": thumbnail,
            "user_id": user_id,
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: Workflow(api, item['uuid'], item))

    
    @classmethod
    def get_workflow(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Workflow':
        """
        Get a workflow by its UUID.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the workflow to get.
            user_id (int): Specific user. privileges required.

        Returns:
            Workflow: The workflow object.

        Raises:
            NotFoundError: If the workflow with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> workflow = client.get_workflow(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id,
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Workflow(api, item['uuid'], item))


    @classmethod
    def get_workflow_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Workflow', None]:
        """
        Get a workflow by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the workflow to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Workflow | None: returns the workflow if a workflow matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow_by_name(client, name='test')
            or
            >>> workflow = client.get_workflow_by_name(name='test')
        """
        workflows = cls.get_workflows(api, q=f"name = '{name}'", user_id=user_id)
        if workflows and workflows[0].name == name:
            return workflows[0]
        else:
            return None


    def update(self, **kwargs) -> Dict:
        """
        Update the workflow.

        Keyword Args:
            name (str): The name of the workflow.
            display_name (str): The display name of the workflow.
            description (str): The description of the workflow.
            settings (Dict): The settings of the workflow.
            thumbnail (str): The thumbnail of the workflow.

        Returns:
            Dict: The updated workflow data.

        Raises:
            ValidationError: If the workflow data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> workflow.update_workflow(display_name="New Display Name")
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
        Delete the Workflow.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> workflow.delete()
        """
        super().delete(self.endpoint)


    @property
    def thumbnail(self) -> str:
        """
        Get the thumbnail URL of the Workflow.

        Returns:
            str: The thumbnail of the Workflow.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> workflow.thumbnail
            'https://example.com/thumbnail.png'
        """
        return super().thumbnail()
    

    def share(self, users: List['User']) -> None:
        """
        Shares the workflow with specified users.

        Args:
            users (List[User]): The list of user objects to share the workflow with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> workflow.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the workflow with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the workflow with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient             
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> workflow.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the workflow is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.workflow import Workflow
            >>> client = GeoboxClient()
            >>> workflow = Workflow.get_workflow(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> workflow.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)
