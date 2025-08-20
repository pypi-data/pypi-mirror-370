from urllib.parse import urlencode, urljoin
from typing import Optional, Dict, List, Union, TYPE_CHECKING
from datetime import datetime

from .base import Base
from .user import User
from .apikey import ApiKey
from .utils import clean_data
from .enums import UsageScale, UsageParam

if TYPE_CHECKING:
    from . import GeoboxClient


class Usage(Base):

    BASE_ENDPOINT = 'usage/'

    def __init__(self,
                api: 'GeoboxClient',
                user: 'User'):
        """
        Constructs the necessary attributes for the Usage object.

        Args:
            api (Api): The API instance.
            user (User): the user usage object.
        """
        self.api = api
        self.user = user


    def __repr__(self) -> str:
        """
        Return a string representation of the Usage object.

        Returns:
            str: A string representation of the Usage object.
        """
        return f"Usage(user={self.user})"


    @classmethod
    def get_api_usage(cls, 
                        api: 'GeoboxClient', 
                        resource: Union['User', 'ApiKey'], 
                        scale: 'UsageScale',
                        param: 'UsageParam',
                        from_date: 'datetime' = None,
                        to_date: 'datetime' = None,
                        days_before_now: int = None,
                        limit: int = None) -> List:
        """
        Get the api usage of a user

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            resource (User | ApiKey): User or ApiKey object.
            scale (UsageScale): the scale of the report.
            param (UsageParam): traffic or calls.
            from_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            to_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            days_before_now (int, optional): number of days befor now.
            limit (int, optional): Number of items to return. default is 10.

        Raises:
            ValueError: one of days_before_now or from_date/to_date parameters must have value
            ValueError: resource must be a 'user' or 'apikey' object

        Returns:
            List: usage report

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.usage import Usage
            >>> client = GeoboxClient()
            >>> user = client.get_user() # gets current user
            >>> usage = Usage.get_api_usage(client, 
            ...                               resource=user, 
            ...                               scale=UsageScale.Day, 
            ...                               param=UsageParam.Calls, 
            ...                               days_before_now=5)
            or
            >>> usage = client.get_api_usage(resource=user, 
            ...                               scale=UsageScale.Day, 
            ...                               param=UsageParam.Calls, 
            ...                               days_before_now=5)
        """
        if not(from_date and to_date) and not days_before_now:
            raise ValueError("one of days_before_now or from_date/to_date parameters must have value")

        params = {}
        if isinstance(resource, User):
            params['eid'] = resource.user_id
        elif isinstance(resource, ApiKey):
            params['eid'] = resource.key
        else:
            raise ValueError("resource must be a 'user' or 'apikey' object")

        params = clean_data({**params,
                    'scale': scale.value if scale else None,
                    'param': param.value if param else None,
                    'from_date': from_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if from_date else None,
                    'to_date': to_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if to_date else None,
                    'days_before_now': days_before_now,
                    'limit': limit
                    })
        query_strings = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}api?{query_strings}"

        return api.get(endpoint)


    @classmethod
    def get_process_usage(cls, 
                            api: 'GeoboxClient',
                            user_id: int = None, 
                            from_date: datetime = None, 
                            to_date: datetime = None, 
                            days_before_now: int = None) -> float:
        """
        Get process usage of a user in seconds

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            user_id (int, optional): the id of the user. leave blank to get the current user report.
            from_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            to_date (datetime, optional): datetime object in this format: "%Y-%m-%dT%H:%M:%S". 
            days_before_now (int, optional): number of days befor now.

        Raises:
            ValueError: one of days_before_now or from_date/to_date parameters must have value

        Returns:
            float: process usage of a user in seconds

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.usage import Usage
            >>> client = GeoboxClient()
            >>> process_usage = Usage.get_process_usage(client, days_before_now=5)
            or
            >>> process_usage = client.get_process_usage(days_before_now=5)
        """
        if not(from_date and to_date) and not days_before_now:
            raise ValueError("one of days_before_now or from_date/to_date parameters must have value")

        params = clean_data({
            'user_id': user_id if user_id else None,
            'from_date': from_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if from_date else None,
            'to_date': to_date.strftime("%Y-%m-%dT%H:%M:%S.%f") if to_date else None,
            'days_before_now': days_before_now
        })
        query_strings = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}process?{query_strings}"
        return api.get(endpoint)


    @classmethod
    def get_usage_summary(cls, api: 'GeoboxClient', user_id: int = None) -> Dict:
        """
        Get the usage summary of a user

        Args:
            api (GeoboxClient): The API instance.
            user_id (int, optional): the id of the user. leave blank to get the current user report.

        Returns:
            Dict: the usage summery of the users

        Returns:
            >>> from geobox import GeoboxClient
            >>> from geobox.usage import Usage
            >>> client = GeoboxClient()
            >>> usage_summary = Usage.get_usage_summary(client)
            or
            >>> usage_summary = client.get_usage_summary()
        """
        params = clean_data({
            'user_id': user_id if user_id else None
        })
        query_strings = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}summary?{query_strings}"
        return api.get(endpoint)


    @classmethod
    def update_usage(cls, api: 'GeoboxClient', user_id: int = None) -> Dict:
        """
        Update usage of a user

        Args:
            api (GeoboxClient): The API instance.
            user_id (int, optional): the id of the user. leave blank to get the current user report.
            
        Returns:
            Dict: the updated data

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.usage import Usage
            >>> client = GeoboxClient()
            >>> Usage.update_usage(client)
            or
            >>> client.update_usage()
        """
        data = clean_data({
            'user_id': user_id if user_id else None
        })
        endpoint = f"{cls.BASE_ENDPOINT}update"
        return api.post(endpoint, payload=data)