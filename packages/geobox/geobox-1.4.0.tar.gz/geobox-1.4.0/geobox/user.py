from typing import List, Any, TYPE_CHECKING, Union, Dict
from urllib.parse import urlencode, urljoin

from .base import Base
from .utils import clean_data, xor_encode
from .enums import UserRole, UserStatus
from .plan import Plan

if TYPE_CHECKING:
    from . import GeoboxClient


class User(Base):

    BASE_ENDPOINT: str = 'users/'

    def __init__(self, api: 'GeoboxClient', user_id: int, data: dict = {}) -> None:
        """
        Initialize a User instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            user_id (int): the id of the user
            data (Dict): The data of the user.
        """
        super().__init__(api, data=data)
        self.user_id = user_id
        self.endpoint = urljoin(self.BASE_ENDPOINT, f'{self.user_id}/') if self.user_id else 'me'


    def __repr__(self) -> str:
        """
        Return a string representation of the User instance.

        Returns:
            str: A string representation of the User instance.
        """
        return f'User(id={self.id}, first_name={self.first_name}, last_name={self.last_name})'


    @property
    def role(self) -> 'UserRole':
        """
        User role property

        Returns:
            UserRole: the user role
        """
        return UserRole(self.data.get('role')) if self.data.get('role') else None
    

    @property
    def status(self) -> 'UserStatus':
        """
        User status Property

        Returns:
            UserStatus: the user status
        """
        return UserStatus(self.data.get('status')) if self.data.get('status') else None
    
    
    @property
    def plan(self) -> 'Plan':
        """
        User plan Property

        Returns:
            Plan: the plan object
        """
        plan = self.data.get('plan', {})
        return Plan(self.api, plan.get('id'), plan) if plan else None
    

    @classmethod
    def get_users(cls, api: 'GeoboxClient', **kwargs) -> Union[List['User'], int]:
        """
        Retrieves a list of users (Permission Required)

        Args:
            api (GeoboxClient): The API instance.

        Keyword Args:
            status (UserStatus): the status of the users filter.
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared maps. default is False.

        Returns:
            List[User] | int: list of users or the count number.

        Example:
            >>> from geobox import Geoboxclient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> users = User.get_users(client)
            or
            >>> users = client.get_users()
        """
        params = {
           'f': 'json',
           'status': kwargs.get('status').value if kwargs.get('status') else None,
           'q': kwargs.get('q'),
           'search': kwargs.get('search'),
           'search_fields': kwargs.get('search_fields'),
           'order_by': kwargs.get('order_by'),
           'return_count': kwargs.get('return_count', False),
           'skip': kwargs.get('skip', 0),
           'limit': kwargs.get('limit', 10),
           'user_id': kwargs.get('user_id')
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: User(api, item['id'], item))
    

    @classmethod
    def create_user(cls, 
                    api: 'GeoboxClient',
                    username: str, 
                    email: str, 
                    password: str, 
                    role: 'UserRole',
                    first_name: str,
                    last_name: str,
                    mobile: str,
                    status: 'UserStatus') -> 'User':
        """
        Create a User (Permission Required)

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            username (str): the username of the user.
            email (str): the email of the user.
            password (str): the password of the user.
            role (UserRole): the role of the user.
            first_name (str): the firstname of the user.
            last_name (str): the lastname of the user.
            mobile (str): the mobile number of the user. e.g. "+98 9120123456".
            status (UserStatus): the status of the user.

        Returns:
            User: the user object.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> user = User.create_user(client,
            ...                             username="user1",
            ...                             email="user1@example.com",
            ...                             password="P@ssw0rd",
            ...                             role=UserRole.ACCOUNT_ADMIN,
            ...                             first_name="user 1",
            ...                             last_name="user 1",
            ...                             mobile="+98 9120123456",
            ...                             status=UserStatus.ACTIVE)
            or
            >>> user = client.create_user(username="user1",
            ...                             email="user1@example.com",
            ...                             password="P@ssw0rd",
            ...                             role=UserRole.ACCOUNT_ADMIN,
            ...                             first_name="user 1",
            ...                             last_name="user 1",
            ...                             mobile="+98 9120123456",
            ...                             status=UserStatus.ACTIVE)
        """
        data = {
            "username": username,
            "email": email,
            "password": xor_encode(password),
            "role": role.value,
            "first_name": first_name,
            "last_name": last_name,
            "mobile": mobile,
            "status": status.value
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: User(api, item['id'], item))


    @classmethod
    def search_users(cls, api: 'GeoboxClient', search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Get list of users based on the search term.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            search (str, optional): The Search Term.
            skip (int, optional): Number of items to skip. default is 0.
            limit (int, optional): Number of items to return. default is 10.

        Returns:
            List[User]: A list of User instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> users = User.get_users(client, search="John")
            or
            >>> users = client.get_users(search="John")
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        endpoint = urljoin(cls.BASE_ENDPOINT, 'search/')
        return super()._get_list(api, endpoint, params, factory_func=lambda api, item: User(api, item['id'], item))


    @classmethod
    def get_user(cls, api: 'GeoboxClient', user_id: int = 'me') -> 'User':
        """
        Get a user by its id (Permission Required)

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            user_id (int, optional): Specific user. don't specify a user_id to get the current user.

        Returns:
            User: the user object.

        Raises:
            NotFoundError: If the user with the specified id is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> user = User.get_user(client, user_id=1)
            or
            >>> user = client.get_user(user_id=1)
        
            get the current user
            >>> user = User.get_user(client)
            or 
            >>> user = client.get_user()
        """
        params = {
            'f': 'json'
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, user_id, params, factory_func=lambda api, item: User(api, item['id'], item))


    def update(self, **kwargs) -> Dict:
        """
        Update the user (Permission Required)

        Keyword Args:
            username (str)
            email (str)
            first_name (str)
            last_name (str)
            mobile (str): e.g. "+98 9120123456" 
            status (UserStatus)
            role (UserRole)
            plan (Plan)
            expiration_date (str)

        Returns:
            Dict: updated data

        Example:
            >>> from geobox imoprt GeoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> user = User.get_user(client, user_id=1)
            >>> user.update_user(status=UserStatus.PENDING)
        """
        data = {
            "username": kwargs.get('username'),
            "email": kwargs.get('email'),
            "first_name": kwargs.get('first_name'),
            "last_name": kwargs.get('last_name'),
            "status": kwargs.get('status').value if kwargs.get('status') else None,
            "role": kwargs.get('role').value if kwargs.get('role') else None,
        }
        data = clean_data(data)

        try:
            data['mobile'] = None if kwargs['mobile'] == '' else kwargs['mobile']
        except:
            pass

        try:
            data['plan_id'] = None if kwargs['plan'] == '' else kwargs['plan'].id
        except:
            pass

        try:
            data['expiration_date'] = None if kwargs['expiration_date'] == '' else kwargs['expiration_date']
        except:
            pass

        response = self.api.put(self.endpoint, data)
        self._update_properties(response)
        return response
    

    def delete(self) -> None:
        """
        Delete the user (Permission Required)

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> user = User.get_user(client, user_id=1)
            >>> user.delete()
        """
        super().delete(self.endpoint)

    
    def get_sessions(self, user_id: int = 'me') -> List['Session']:
        """
        Get a list of user available sessions (Permission Required)

        Args:
            user_id (int, optional): Specific user. don't specify user_id to get the current user.

        Returns:
            List[Session]: list of user sessions.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> user = User.get_user(client, user_id=1)
            or
            >>> user = client.get_user(user_id=1)

            >>> user.get_user_sessions()       
            or
            >>> client.get_user_sessions()
        """
        params = clean_data({
            'f': 'json'
        })
        query_string = urlencode(params)
        if user_id != 'me':
            user = self.get_user(self.api, user_id=user_id)
            endpoint = f"{self.BASE_ENDPOINT}{user_id}/sessions/?{query_string}"
        else:
            user = self
            endpoint = urljoin(self.endpoint, f'sessions/?{query_string}')

        response = self.api.get(endpoint)
        return [Session(item['uuid'], item, user) for item in response]
    

    def change_password(self, new_password: str) -> None:
        """
        Change the user password (privileges required)

        Args:
            new_password (str): new password for the user.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> user = client.get_user()
            >>> user.change_password(new_password='user_new_password')
        """
        data = clean_data({
            "new_password": xor_encode(new_password)
        })
        endpoint = urljoin(self.endpoint, 'change-password')
        self.api.post(endpoint, data, is_json=False)


    def renew_plan(self) -> None:
        """
        Renew the user plan

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> user = client.get_user(user_id=1)
            >>> user.renew_plan()
        """
        endpoint = urljoin(self.endpoint, 'renewPlan')
        self.api.post(endpoint)




class Session(Base):
    def __init__(self, uuid: str, data: Dict, user: 'User'):
        """
        Initialize a user session instance.

        Args:
            uuid (str): The unique identifier for the user session.
            data (Dict): The data of the session.
            user (User): the user instance.
        """
        self.uuid = uuid
        self.data = data
        self.user = user
        self.endpoint = urljoin(self.user.endpoint, f'sessions/{self.uuid}')


    def __repr__(self) -> str:
        """
        Return a string representation of the resource.

        Returns:
            str: A string representation of the Session object.
        """
        return f"Session(user={self.user}, agent='{self.agent}')"
    

    def close(self) -> None:
        """
        Close the user session

        Returns:
            None

        Example:
            >>> from geobox import geoboxClient
            >>> from geobox.user import User
            >>> client = GeoboxClient()
            >>> user = User.get_user(client) # without user_id parameter, it gets the current user
            or
            >>> user = client.get_user() # without user_id parameter, it gets the current user
            >>> session = user.get_sessions()[0]
            >>> session.close()
        """
        data = clean_data({
            'user_id': self.user.user_id,
            'session_uuid': self.uuid
        })
        self.user.api.post(self.endpoint, data)