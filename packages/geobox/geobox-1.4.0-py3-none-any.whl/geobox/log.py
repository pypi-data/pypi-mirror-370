from urllib.parse import urljoin
from typing import Optional, Dict, List, Union, TYPE_CHECKING
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
    from . import GeoboxClient


class Log(Base):

    BASE_ENDPOINT = 'logs/'

    def __init__(self,
                api: 'GeoboxClient',
                log_id: int,
                data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Log object.

        Args:
            api (Api): The GeoboxClient instance for making requests.
            log_id (int): The id of the log.
            data (Dict, optional): The data of the log.
        """
        super().__init__(api, data=data)
        self.log_id = log_id
        self.endpoint = f"{self.BASE_ENDPOINT}{self.log_id}"


    def __repr__(self) -> str:
        """
        Return a string representation of the Log object.

        Returns:
            str: A string representation of the Log object.
        """
        return f"Log(id={self.log_id}, activity_type={self.activity_type})"


    @classmethod
    def get_logs(cls, api: 'GeoboxClient', **kwargs) -> List['Log']:
        """
        Get a list of Logs

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Keyword Args:
            search (str): search term for keyword-based searching among all textual fields
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            skip (int): Number of items to skip. default is 0.
            limit (int): Number of items to return. default is 10.
            user_id (int): Specific user. Privileges required.
            from_date (datetime): datetime object in this format: "%Y-%m-%dT%H:%M:%S.%f". 
            to_date (datetime): datetime object in this format: "%Y-%m-%dT%H:%M:%S.%f". 
            user_identity (str): the user identity in this format: username - firstname lastname - email .
            activity_type (str): the user activity type.

        Returns:
            List[Log]: a list of logs

        Example: 
            >>> from geobox import Geobox
            >>> from geopox.log import Log
            >>> client = GeoboxClient()
            >>> logs = Log.get_logs(client)
            or
            >>> logs = client.get_logs() 
        """ 
        params = {
            'search': kwargs.get('search'),
            'order_by': kwargs.get('order_by'),
            'skip': kwargs.get('skip'),
            'limit': kwargs.get('limit'),
            'user_id': kwargs.get('user_id'),
            'from_date': kwargs.get('from_date').strftime("%Y-%m-%dT%H:%M:%S.%f") if kwargs.get('from_date') else None,
            'to_date': kwargs.get('to_date').strftime("%Y-%m-%dT%H:%M:%S.%f") if kwargs.get('to_date') else None,
            'user_identity': kwargs.get('user_identity'),
            'activity_type': kwargs.get('activity_type')
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Log(api, item['id'], item))


    def delete(self) -> None:
        """
        Delete a log (privileges required)

        Returns:
            None

        Example:
            >>> from geobox import Geobox
            >>> from geopox.log import Log
            >>> client = GeoboxClient()
            >>> log = Log.get_logs(client)[0]
            >>> log.delete()
        """
        super().delete(self.endpoint)
        self.log_id = None