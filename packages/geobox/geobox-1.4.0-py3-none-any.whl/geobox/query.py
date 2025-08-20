from urllib.parse import urljoin
from typing import Dict, List, TYPE_CHECKING, Union

from .utils import clean_data
from .base import Base
from .task import Task
from .enums import QueryResultType, QueryGeometryType, QueryParamType

if TYPE_CHECKING:
    from . import GeoboxClient
    from .user import User

class Query(Base):
    """
    A class to interact with queries in GeoBox.
    """
    BASE_ENDPOINT: str = 'queries/'

    def __init__(self, 
                api: 'GeoboxClient', 
                uuid: str = None, 
                data: Dict = {}):
        """
        Constructs all the necessary attributes for the Query object.

        Args:
            api (Api): The API instance.
            uuid (str): The UUID of the query.
            data (dict, optional): The data of the query.
        """
        self.result = {}
        self._system_query = False
        super().__init__(api, uuid=uuid, data=data)


    def _check_access(self) -> None:
        """
        Check if the query is a system query.

        Returns:
            None

        Raises:
            PermissionError: If the query is a read-only system query.
        """
        if self._system_query:
            raise PermissionError("Cannot modify system queries - they are read-only")


    @property
    def sql(self) -> str:
        """
        Get the SQL of the query.
        
        Returns:
            str: The SQL of the query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> query.sql
            'SELECT * FROM some_layer'
        """
        return self.data['sql']
    

    @sql.setter
    def sql(self, value: str) -> None:
        """
        Set the SQL of the query.

        Args:
            value (str): The SQL of the query.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> query.sql = 'SELECT * FROM some_layer'
        """
        self.data['sql'] = value


    @property
    def params(self) -> List[Dict]:
        """
        Get the parameters of the query.

        Returns:
            List[Dict]: The parameters of the query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> query.params
            [{'name': 'layer', 'value': '12345678-1234-5678-1234-567812345678', 'type': 'Layer'}]
        """
        if not isinstance(self.data.get('params'), list):
            self.data['params'] = []

        return self.data['params']


    @params.setter
    def params(self, value: Dict) -> None:
        """
        Set the parameters of the query.

        Args:
            value (Dict): The parameters of the query.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> query.params = [{'name': 'layer', 'value': '12345678-1234-5678-1234-567812345678', 'type': 'Layer'}]
        """
        if not isinstance(self.data.get('params'), list):
            self.data['params'] = []
        
        self.data['params'] = value


    @classmethod
    def get_queries(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Query'], int]:
        """
        Get Queries

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of queries to skip. default is 0.
            limit(int): Maximum number of queries to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared queries. default is False.

        Returns:
            List[Query] | int: list of queries or the number of queries.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> queries = Query.get_queries(client)
            or
            >>> queries = client.get_queries()
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_field': kwargs.get('search_field'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Query(api, item['uuid'], item))


    @classmethod
    def create_query(cls, api: 'GeoboxClient', name: str, display_name: str = None, sql: str = None, params: List = None) -> 'Query':
        """
        Creates a new query.

        Args:
            api (Api): The GeoboxClient instance for making requests.
            name (str): The name of the query.
            display_name (str, optional): The display name of the query.
            sql (str, optional): The SQL statement for the query.
            params (list, optional): The parameters for the SQL statement.

        Returns:
            Query: The created query instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.create_query(client, name='query_name', display_name='Query Name', sql='SELECT * FROM some_layer')
            or
            >>> query = client.create_query(name='query_name', display_name='Query Name', sql='SELECT * FROM some_layer')
        """
        data = {
            "name": name,
            "display_name": display_name,
            "sql": sql,
            "params": params
        }
        return super()._create(api, cls.BASE_ENDPOINT, data, factory_func=lambda api, item: Query(api, item['uuid'], item))


    @classmethod
    def get_query(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'Query':
        """
        Retrieves a query by its UUID.

        Args:
            api (Api): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the query.
            user_id (int, optional): specific user ID. privileges required.

        Returns:
            Query: The retrieved query instance.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> query = client.get_query(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, params, factory_func=lambda api, item: Query(api, item['uuid'], item))


    @classmethod
    def get_query_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['Query', None]:
        """
        Get a query by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the query to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            Query | None: returns the query if a query matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query_by_name(client, name='test')
            or
            >>> query = client.get_query_by_name(name='test')
        """
        queries = cls.get_queries(api, q=f"name = '{name}'", user_id=user_id)
        if queries and queries[0].name == name:
            return queries[0]
        else:
            return None


    @classmethod
    def get_system_queries(cls, api: 'GeoboxClient', **kwargs) -> List['Query']:
        """
        Returns the system queries as a list of Query objects.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'".
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): whether to return the total count of queries. default is False.
            skip (int): number of queries to skip. minimum is 0. default is 0.
            limit (int): number of queries to return. minimum is 1. default is 100.
            user_id (int): specific user. privileges required.
            shared (bool): whether to return shared queries. default is False.
        
        Returns:
            List[Query]: list of system queries.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> queries = Query.get_system_queries(client)
            or
            >>> queries = client.get_system_queries()
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_fields': kwargs.get('search_fields'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 100),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)            
        }
        endpoint = urljoin(cls.BASE_ENDPOINT, 'systemQueries/')
        def factory_func(api, item):
            query = Query(api, item['uuid'], item)
            query._system_query = True
            return query
            
        return super()._get_list(api, endpoint, params, factory_func=factory_func)

    
    def add_param(self, name: str, value: str, type: 'QueryParamType', default_value: str = None, Domain: Dict = None) -> None:
        """
        Add a parameter to the query parameters.
        
        Args:
            name (str): The name of the parameter.
            value (str): The value of the parameter.
            type (str): The type of the parameter (default: 'Layer').
            default_value (str, optional): The default value for the parameter.
            Domain (Dict, optional): Domain information for the parameter.
            
        Returns:
            None
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> query = client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>> query.add_param(name='param_name', value='param_value', type=QueryParamType.LAYER)
        """
        self._check_access()
        
        self.params.append({
            'name': name,
            'value': value,
            'type': type.value,
            'default_value': default_value,
            'Domain': Domain
        })


    def remove_param(self, name: str) -> None:
        """
        Remove a parameter from the query parameters by name.
        
        Args:
            name (str): The name of the parameter to remove.
            
        Returns:
            None
            
        Raises:
            ValueError: If the parameter is not found in query parameters.
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> query = client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>> query.remove_param(name='param_name')
        """
        self._check_access()
        
        for i, param in enumerate(self.params):
            if param.get('name') == name:
                self.params.pop(i)
                return
        
        raise ValueError(f"Parameter with name '{name}' not found in query parameters")


    def execute(self, 
                f: str = "json",
                result_type: QueryResultType = QueryResultType.both, 
                return_count: bool = None,
                out_srid: int = None, 
                quant_factor: int = 1000000, 
                bbox_srid: int = None, 
                skip: int = None, 
                limit: int = None,
                skip_geometry: bool = False) -> Union[Dict, int]:
        """
        Executes a query with the given SQL statement and parameters.

        Args:
            f (str): the output format of the executed query. options are: json, topojson. default is json.
            result_type (QueryResultType, optional): The type of result to return (default is "both").
            return_count (bool, optional): Whether to return the count of results.
            out_srid (int, optional): The output spatial reference ID.
            quant_factor (int, optional): The quantization factor (default is 1000000).
            bbox_srid (int, optional): The bounding box spatial reference ID.
            skip (int, optional): The number of results to skip.
            limit (int, optional): The maximum number of results to return.
            skip_geometry (bool): Whether to skip the geometry part of the features or not. default is False.

        Returns:
            Dict | int: The result of the query execution or the count number of the result

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> query = client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>> query.execute(f='json')
        """
        self._check_access()
        
        if not self.sql:
            raise ValueError('"sql" parameter is required for this action!') 
        if not self.params:
            raise ValueError('"params" parameter is required for this action!')

        data = clean_data({
            "f": f if f in ['json', 'topojson'] else None,
            "sql": self.sql,
            "params": self.params,
            "result_type": result_type.value,
            "return_count": return_count,
            "out_srid": out_srid,
            "quant_factor": quant_factor,
            "bbox_srid": bbox_srid,
            "skip": skip,
            "limit": limit,
            "skip_geometry": skip_geometry
        })

        endpoint = urljoin(self.BASE_ENDPOINT, 'exec/')
        self.result = self.api.post(endpoint, data)
        return self.result


    def update(self, **kwargs) -> Dict:
        """
        Updates the query with new data.

        Keyword Args:
            name (str): The new name of the query.
            display_name (str): The new display name of the query.
            sql (str): The new SQL statement for the query.
            params (list): The new parameters for the SQL statement.

        Returns:
            Dict: The updated query data.
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> query = client.get_query(uuid="12345678-1234-5678-1234-567812345678")
            >>> query.update(name='new_name')
        """
        self._check_access()
            
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "sql": kwargs.get('sql'),
            "params": kwargs.get('params')
        }
        super()._update(self.endpoint, data)


    def save(self) -> None:
        """
        Save the query. Creates a new query if query uuid is None, updates existing query otherwise.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> query.sql = "SELECT * FROM some_layer"
            >>> query.save()
        """
        self.params = [item for item in self.params if item.get('value')]

        try:
            if self.__getattr__('uuid'):
                self.update(name=self.data['name'], display_name=self.data['display_name'], sql=self.sql, params=self.params)
        except AttributeError:
            response = self.api.post(self.BASE_ENDPOINT, self.data)
            self.endpoint = urljoin(self.BASE_ENDPOINT, f'{response["uuid"]}/')        
            self.data.update(response)


    def delete(self) -> str:
        """
        Deletes a query.

        Returns:
            str: The response from the API.
            
        Raises:
            PermissionError: If the query is a read-only system query

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> query.delete()
        """
        self._check_access()
        super().delete(self.endpoint)


    def share(self, users: List['User']) -> None:
        """
        Shares the query with specified users.

        Args:
            users (List[User]): The list of user objects to share the query with.

        Returns:
            None
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search="John")
            >>> query.share(users=users)
        """
        self._check_access()
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the query with specified users.

        Args:
            users (List[User]): The list of user objects to unshare the query with.

        Returns:
            None
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search="John")
            >>> query.unshare(users=users)
        """
        self._check_access()
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the query is shared with.

        Args:
            search (str, optional): the search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search="John")
            >>> query.get_shared_users(search='John', skip=0, limit=10)
        """
        self._check_access()
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)


    @property
    def thumbnail(self) -> str:
        """
        Retrieves the thumbnail URL for the query.            

        Returns:
            str: The thumbnail URL.
        """
        self._check_access()
        return super().thumbnail()


    def save_as_layer(self, layer_name: str, layer_type: 'QueryGeometryType' = None) -> Task:
        """
        Saves the query as a new layer.

        Args:
            layer_name (str): The name of the new layer.
            layer_type (QueryGeometryType, optional): The type of the new layer.

        Returns:
            Task: The response task object.
            
        Raises:
            PermissionError: If the query is a read-only system query.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.query import Query
            >>> client = GeoboxClient()
            >>> query = Query.get_query(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> query.save_as_layer(layer_name='test')
        """
        self._check_access()

        params = [{
            "name": item.get('name'),
            "type": item.get('type'),
            "value": item.get('default_value') if not item.get('value') else item.get('value')
        } for item in self.params]

        data = clean_data({
            "sql": self.sql,
            "params": params,
            "layer_name": layer_name,
            "layer_type": layer_type.value if layer_type else None
        })

        endpoint = urljoin(self.BASE_ENDPOINT, 'saveAsLayer/')
        response = self.api.post(endpoint, data)
        task = Task.get_task(self.api, response.get('task_id'))
        return task
