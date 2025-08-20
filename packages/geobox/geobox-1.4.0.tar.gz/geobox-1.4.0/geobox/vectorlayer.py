from urllib.parse import urljoin
from typing import List, Optional, TYPE_CHECKING, Dict, Union

from .base import Base
from .utils import clean_data
from .exception import NotFoundError
from .field import Field, FieldType
from .feature import Feature
from .enums import LayerType
from .task import Task
from .enums import InputGeomType, FileOutputFormat
from .version import VectorLayerVersion


if TYPE_CHECKING:
    from .api import GeoboxClient
    from .view import VectorLayerView
    from .user import User
    from .file import File

class VectorLayer(Base):
    """
    A class representing a vector layer in Geobox.
    
    This class provides functionality to create, manage, and manipulate vector layers.
    It supports various operations including CRUD operations on layers, features, and fields,
    as well as advanced operations like importing/exporting features and calculating field values.
    """
    BASE_ENDPOINT = 'vectorLayers/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str, 
                 layer_type: LayerType, 
                 data: Optional[Dict] = {}):
        """
        Initialize a VectorLayer instance.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The unique identifier for the layer.
            layer_type (LayerType): The type of geometry stored in the layer.
            data (Dict, optional): Additional layer metadata and configuration.
        """
        super().__init__(api=api, uuid=uuid, data=data)
        self.layer_type = layer_type if isinstance(layer_type, LayerType) else LayerType(layer_type)


    def __repr__(self) -> str:
        """
        Return a string representation of the VectorLayer object.

        Returns:
            str: A string representation of the VectorLayer object.
        """
        return f"VectorLayer(uuid={self.uuid}, name={self.name}, layer_type={self.layer_type})"


    @classmethod
    def get_vectors(cls, api: 'GeoboxClient', **kwargs) -> Union[List['VectorLayer'], int]:
        """
        Get a list of vector layers with optional filtering and pagination.
        
        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Keyword Args:
            include_settings (bool): Whether to include layer settings. Default is False.
            temporary (bool): Whether to return temporary layers, default is False
            q (str): Query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): Search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): Comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): Whether to return total count. default is False.
            skip (int): Number of layers to skip. default is 0.
            limit (int): Maximum number of layers to return. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared layers. default is False.
                
        Returns:
            List[VectorLayer] | int: A list of VectorLayer instances or the layers count if return_count is True.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layers = VectorLayer.get_vectors(api=client, 
            ...                                 include_settings=True, 
            ...                                 skip=0, 
            ...                                 limit=100, 
            ...                                 return_count=False, 
            ...                                 search="my_layer",
            ...                                 search_fields="name, description",
            ...                                 order_by="name",
            ...                                 shared=True)
            or
            >>> layers = client.get_vectors(include_settings=True, 
            ...                                 skip=0, 
            ...                                 limit=100, 
            ...                                 return_count=False, 
            ...                                 search="my_layer",
            ...                                 search_fields="name, description",
            ...                                 order_by="name",
            ...                                 shared=True)
        """
        params = {
            'f': 'json',
            'include_settings': kwargs.get('include_settings', False),
            'temporary': kwargs.get('temporary', False),
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
        return super()._get_list(api=api, 
                                 endpoint=cls.BASE_ENDPOINT,
                                 params=params, 
                                 factory_func=lambda api, item: VectorLayer(api, item['uuid'], LayerType(item['layer_type']), item))


    @classmethod
    def get_vector(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'VectorLayer':
        """
        Get a specific vector layer by its UUID.
        
        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the layer to retrieve.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            VectorLayer: The requested layer instance.
            
        Raises:
            NotFoundError: If the layer with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return super()._get_detail(api=api,
                                   endpoint=cls.BASE_ENDPOINT,
                                   uuid=uuid, 
                                   params=params, 
                                   factory_func=lambda api, item: VectorLayer(api, item['uuid'], LayerType(item['layer_type']), item))


    @classmethod
    def get_vector_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> Union['VectorLayer', None]:
        """
        Get a vector layer by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the vector to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            VectorLayer | None: returns the vector if a vector matches the given name, else None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector_by_name(client, name='test')
            or
            >>> layer = client.get_vector_by_name(name='test')
        """
        layers = cls.get_vectors(api, q=f"name = '{name}'", user_id=user_id)
        if layers and layers[0].name == name:
            return layers[0]
        else:
            return None


    @classmethod
    def get_vectors_by_ids(cls, api: 'GeoboxClient', ids: List[int], user_id: int = None, include_settings: bool = False) -> List['VectorLayer']:
        """
        Get vector layers by their IDs.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            ids (List[int]): The IDs of the layers to retrieve.
            user_id (int, optional): Specific user. privileges required.
            include_settings (bool, optional): Whether to include the layer settings. default is False.

        Returns:
            List[VectorLayer]: The list of VectorLayer instances.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layers = VectorLayer.get_vectors_by_ids(api=client, ids=[1, 2, 3])
            or
            >>> layers = client.get_vectors_by_ids(ids=[1, 2, 3])
        """
        params = {
            'ids': ids,
            'user_id': user_id,
            'include_settings': include_settings
        }
        return super()._get_list_by_ids(api=api, 
                                        endpoint=f'{cls.BASE_ENDPOINT}get-layers/', 
                                        params=params, 
                                        factory_func=lambda api, item: VectorLayer(api, item['uuid'], LayerType(item['layer_type']), item))


    @classmethod
    def create_vector(cls, 
                     api: 'GeoboxClient', 
                     name: str, 
                     layer_type: LayerType, 
                     display_name: str = None,
                     description: str = None, 
                     has_z: bool = False, 
                     temporary: bool = False,
                     fields: List = None) -> 'VectorLayer':
        """
        Create a new vector layer.
        
        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): The name of the layer.
            layer_type (LayerType): The type of geometry to store.
            display_name (str, optional): A human-readable name for the layer. default is None.
            description (str, optional): A description of the layer. default is None.
            has_z (bool, optional): Whether the layer includes Z coordinates. default is False.
            temporary (bool, optional): Whether to create a temporary layer. temporary layers will be deleted after 24 hours. default is False.
            fields (List, optional): List of field definitions for the layer. default is None.
            
        Returns:
            VectorLayer: The newly created layer instance.
            
        Raises:
            ValidationError: If the layer data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.create_vector(api=client, 
            ...                                 name="my_layer", 
            ...                                 layer_type=LayerType.Point,
            ...                                 display_name="My Layer",
            ...                                 description="This is a description of my layer",
            ...                                 has_z=False,
            ...                                 temporary=True,
            ...                                 fields=[{"name": "my_field", "datatype": "FieldTypeString"}])
            or
            >>> layer = client.create_vector(name="my_layer", 
            ...                                 layer_type=LayerType.Point,
            ...                                 display_name="My Layer",
            ...                                 description="This is a description of my layer",
            ...                                 has_z=False,
            ...                                 temporary=True,
            ...                                 fields=[{"name": "my_field", "datatype": "FieldTypeString"}])
        """
        data = {
            "name": name,
            "layer_type": layer_type.value,
            "display_name": display_name,
            "description": description,
            "has_z": has_z,
            "temporary": temporary,
            "fields": fields
        }
        return super()._create(api=api, 
                               endpoint=cls.BASE_ENDPOINT,
                               data=data, 
                               factory_func=lambda api, item: VectorLayer(api, item['uuid'], layer_type, item))


    def update(self, **kwargs) -> Dict:
        """
        Update the layer's properties.
        
        Keyword Args:
            name (str): The new name for the layer.
            display_name (str): The new display name for the layer.
            description (str): The new description for the layer.
            
        Returns:
            Dict: The updated layer data.
            
        Raises:
            ValidationError: If the update data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.update(name="new_name")
            >>> layer.update(display_name="new_display_name")
            >>> layer.update(description="new_description")
        """
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "description": kwargs.get('description')
        }
        return super()._update(endpoint=self.endpoint, data=data)


    def delete(self) -> None:
        """
        Delete the layer.
                    
        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.delete()
        """
        super().delete(endpoint=self.endpoint)


    def make_permanent(self) -> None:
        """
        Make the layer permanent.
        """
        endpoint = urljoin(self.endpoint, 'makePermanent/')
        response = self.api.post(endpoint, is_json=False)
        self._update_properties(response)


    def share(self, users: List['User']) -> None:
        """
        Shares the layer with specified users.

        Args:
            users (List[User]): The list of user objects to share the layer with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search="John")
            >>> layer.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the layer with specified users.

        Args:
            users (List[User]): The list of user objectss to unshare the layer with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search="John")
            >>> layer.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the layer is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)
    

    def create_version(self, name: str, display_name: str = None, description: str = None) -> 'VectorLayerVersion':
        """
        Create a version from the layer

        Args:
            name (str): the name of the version.
            display_name (str, optional): the display name of the version.
            description (str, optional): the description of the version.

        Returns:
            VectorLayerVersion: the object of the version.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectoLayer
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> version = layer.create_version(name="my_version")
        """
        data = {
            "name": name,
            "display_name": display_name,
            "description": description
        }
        endpoint = urljoin(self.endpoint, 'versions')
        return super()._create(self.api, endpoint, data, factory_func=lambda api, item: VectorLayerVersion(api, item['uuid'], item))


    def get_versions(self, **kwargs) -> List['VectorLayerVersion']:
        """
        Get list of versions of the current vector layer object with optional filtering and pagination.

        Keyword Args:
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
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> versions = layer.get_versions()
            or
            >>> versions = layer.get_versions()
        """
        return VectorLayerVersion.get_versions(self.api, layer_id=self.id, **kwargs)


    @property    
    def wfs(self) -> str:
        """
        Get the WFS endpoint for the layer.

        Returns:
            str: The WFS endpoint for the layer.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.wfs
        """
        if self.api.access_token:
            return f'{self.api.base_url}{self.endpoint}wfs/'
        elif self.api.apikey:
            return f'{self.api.base_url}{self.endpoint}apikey:{self.api.apikey}/wfs/'


    def get_fields(self) -> List['Field']:
        """
        Get all fields in the layer.
        
        Returns:
            List[Field]: A list of Field instances representing the layer's fields.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> fields = layer.get_fields()
        """
        endpoint = urljoin(self.endpoint, 'fields/')
        return super()._get_list(api=self.api, 
                            endpoint=endpoint,
                            factory_func=lambda api, item: Field(layer=self, data_type=FieldType(item['datatype']), field_id=item['id'], data=item))


    def get_field(self, field_id: int) -> 'Field':
        """
        Get a specific field by its ID.
        
        Args:
            field_id (int, optional): The ID of the field to retrieve.

        Returns:
            Field: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified ID is not found. 

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> field = layer.get_field(field_id=1)
        """        
        field = next((f for f in self.get_fields() if f.id == field_id), None)
        if not field:
            raise NotFoundError(f'Field with ID {field_id} not found in layer {self.name}')
            
        return field


    def get_field_by_name(self, name: str) -> 'Field':
        """
        Get a specific field by its name.
        
        Args:
            name (str, optional): The name of the field to retrieve.

        Returns:
            Field: The requested field instance.
            
        Raises:
            NotFoundError: If the field with the specified name is not found. 

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> field = layer.get_field_by_name(name='test')
        """        
        field = next((f for f in self.get_fields() if f.name == name), None)
        if not field:
            raise NotFoundError(f"Field with name '{name}' not found in layer {self.name}")
            
        return field


    def add_field(self, name: str, data_type: 'FieldType', data: Dict = {}) -> 'Field':
        """
        Add a new field to the layer.
        
        Args:
            name (str): The name of the new field.
            data_type (FieldType): The data type of the new field.
            data (Dict): Additional field properties (display_name, description, etc.).
            
        Returns:
            Field: The newly created field instance.
            
        Raises:
            ValidationError: If the field data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> field = layer.add_field(name="new_field", data_type=FieldType.String)
        """
        return Field.create_field(self.api, layer=self, name=name, data_type=data_type, data=data)


    def calculate_field(self, 
                        target_field: str, 
                        expression: str, 
                        q: str = None, 
                        bbox: List = None, 
                        bbox_srid: int = None, 
                        feature_ids: List = None, 
                        run_async: bool = True, 
                        user_id: int = None) -> Union['Task', Dict]:
        """
        Calculate values for a field based on an expression.
        
        Args:
            target_field (str): The field to calculate values for.
            expression (str): The expression to use for calculation.
            q (str, optional): Query to filter features. default is None.
            bbox (List, optional): Bounding box to filter features. default is None.
            bbox_srid (int, optional): Spatial reference ID for the bounding box. default is None.
            feature_ids (List, optional): List of specific feature IDs to include. default is None
            run_async (bool, optional): Whether to run the calculation asynchronously. default is True.
            user_id (int, optional): Specific user. privileges required.
            
        Returns:
            Task | Dict: The task instance of the calculation operation or the api response if the run_async=False.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task = layer.calculate_field(target_field="target_field", 
            ...                         expression="expression", 
            ...                         q="name like 'my_layer'", 
            ...                         bbox=[10, 20, 30, 40], 
            ...                         bbox_srid=3857, 
            ...                         feature_ids=[1, 2, 3], 
            ...                         run_async=True)
        """
        data = clean_data({
            "target_field": target_field,
            "expression": expression,
            "q": q,
            "bbox": bbox,
            "bbox_srid": bbox_srid,
            "feature_ids": feature_ids,
            "run_async": run_async,
            "user_id": user_id
        })
        
        endpoint = urljoin(self.endpoint, 'calculateField/')
        response = self.api.post(endpoint, data, is_json=False)
        if run_async:
            task = Task.get_task(self.api, response.get('task_id'))
            return task

        return response


    def get_features(self, **kwargs) -> Union[List['Feature'], int]:
        """
        Get features from the layer with optional filtering and pagination.
        
        Keyword Args:
            quant_factor (int): Quantization factor. This parameter is only used by topojson encoder and is ignored for other formats. Higher quantizaion value means higher geometry precision. default is 1000000.
            skip (int): Number of features to skip. default is 0.
            limit (int): Maximum number of features to return. default is 100.
            user_id (int): Specific user. privileges required.
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            skip_geometry (bool): Whether to exclude geometry data. default is False.
            return_count (bool): Whether to return total count. default is False.
            feature_ids (list): Comma separated list of feature ids which should be filtered.
            select_fields (str): comma separated field names which should be included to the result. default is "[ALL]".
            skip_fields (str): comma separated field names which should be excluded from the result.
            out_srid (int): srid (epsg code) of result features. e.g. 4326. default is 3857.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, length D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            q (str): query filter based on OGC CQL standard. e.g. Name LIKE '%GIS%' AND INTERSECTS(geometry, 'SRID=3857;POLYGON((4901948 2885079, 7049893 2885079, 7049893 4833901, 4901948 4833901, 4901948 2885079))').
            bbox (str): Bounding box to filter features by. e.g. [50.275, 35.1195, 51.4459, 36.0416].
            bbox_srid (int): srid (epsg code) of bbox. e.g. 4326. default is 3857.
                
        Returns:
            List[Feature] | int: A list of Feature instances or the features count if return_count is True.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> features = layer.get_features(quant_factor=1000000, 
            ...                                 skip=0, 
            ...                                 limit=100, 
            ...                                 skip_geometry=False, 
            ...                                 return_count=False, 
            ...                                 select_fields="fclass, osm_id", 
            ...                                 out_srid=3857, 
            ...                                 bbox_srid=3857)
        """
        params = {
            'f': 'json',
            'quant_factor': kwargs.get('quant_factor', 1000000),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 100),
            'user_id': kwargs.get('user_id', None),
            'search': kwargs.get('search', None),
            'search_fields': kwargs.get('search_fields', None),
            'skip_geometry': kwargs.get('skip_geometry', False),
            'return_count': kwargs.get('return_count', False),
            'feature_ids': kwargs.get('feature_ids', None),
            'select_fields': kwargs.get('select_fields', '[ALL]'),
            'skip_fields': kwargs.get('skip_fields', None),
            'out_srid': kwargs.get('out_srid', 3857),
            'order_by': kwargs.get('order_by', None),
            'q': kwargs.get('q', None),
            'bbox': kwargs.get('bbox', None),
            'bbox_srid': kwargs.get('bbox_srid', 3857)
        }

        return super()._get_list(api=self.api,
                            endpoint=f'{self.endpoint}features/',
                            params=params,
                            factory_func=lambda api, item, srid: Feature(self, srid, item),
                            geojson=True)


    def get_feature(self, feature_id: int, out_srid: int = Feature.BASE_SRID) -> 'Feature':
        """
        Get a specific feature by its ID.
        
        Args:
            feature_id (int): The ID of the feature to retrieve.
            out_srid (int, optional): Output spatial reference ID. default is 3857.

        Returns:
            Feature: The requested feature instance.
            
        Raises:
            NotFoundError: If the feature with the specified ID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(feature_id=1, out_srid=4326)
        """
        endpoint = f"{self.endpoint}features/{feature_id}"
        response = self.api.get(endpoint)
        feature = Feature(self, data=response)
        if out_srid != Feature.BASE_SRID:
            feature.transform(out_srid)

        return feature


    def create_feature(self, geojson: Dict)-> 'Feature':
        """
        Create a new feature in the layer.
        
        Args:
            geojson (Dict): The feature data including properties and geometry.
            
        Returns:
            Feature: The newly created feature instance.
            
        Raises:
            ValidationError: If the feature data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> geojson = {
            ...    "type": "Feature",
            ...    "geometry": {"type": "Point", "coordinates": [10, 20]},
            ...    "properties": {"name": "My Point"}
            ... }
            >>> feature = layer.create_feature(geojson=geojson)
        """
        return Feature.create_feature(self, geojson)


    def delete_features(self, q: str = None, bbox: str = None, bbox_srid: int = None, feature_ids: List[int] = None, 
                        run_async: bool = True, user_id: int = None) -> Union['Task', Dict]:
        """
        Delete features from the layer based on specified criteria.
        
        Args:
            q (str, optional): Query to filter features to delete.
            bbox (str, optional): Comma seprated bbox.
            bbox_srid (int, optional): Spatial reference ID for the bounding box.
            feature_ids (str, optional): Comma seprated feature ids.
            run_async (bool, optional): Whether to run the deletion asynchronously. default is True.
            user_id (int, optional): Specific user. privileges required.
            
        Returns:
            Task | Dict: The task instance of the deletion operation or the api response if run_async=False.
            
        Raises:
            ValidationError: If the deletion parameters are invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.delete_features(q="name like 'my_layer'", 
            ...                         bbox='10, 20, 30, 40',
            ...                         bbox_srid=3857, 
            ...                         feature_ids='1, 2, 3', 
            ...                         run_async=True)
        """
        data = clean_data({
            "q": q,
            "bbox": bbox,
            "bbox_srid": bbox_srid,
            "feature_ids": feature_ids,
            "run_async": run_async,
            "user_id": user_id
        })

        endpoint = urljoin(self.endpoint, 'deleteFeatures/')
        response = self.api.post(endpoint, data, is_json=False)
        if run_async:
            task = Task.get_task(self.api, response.get('task_id'))
            return task

        return response


    def import_features(self, 
                            file: 'File', 
                            input_geom_type: 'InputGeomType' = None, 
                            input_layer_name: str = None, 
                            input_dataset: str = None, 
                            user_id: int = None, 
                            input_srid: int = None, 
                            file_encoding: str = "utf-8", 
                            replace_domain_codes_by_values: bool = False, 
                            report_errors: bool = True) -> 'Task':
        """
        Import features from a file into the layer.
        
        Args:
            file (File): file object to import.
            input_geom_type (InputGeomType, optional): Type of geometry in the input file.
            input_layer_name (str, optional): Name of the layer in the input file.
            input_dataset (str, optional): Name of the dataset in the input file.
            user_id (int, optional): Specific user. privileges required.
            input_srid (int, optional): Spatial reference ID of the input data.
            file_encoding (str, optional): Character encoding of the input file.
            replace_domain_codes_by_values (bool, optional): Whether to replace domain codes with values.
            report_errors (bool, optional): Whether to report import errors.
            
        Returns:
            Task: The task instance of the import operation.
            
        Raises:
            ValidationError: If the import parameters are invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file = client.get_file(uuid="12345678-1234-5678-1234-567812345678")
            >>> task = layer.import_features(file=file, 
            ...                         input_geom_type=InputGeomType.POINT,
            ...                         input_layer_name="my_layer",
            ...                         input_dataset="my_dataset",
            ...                         input_srid=3857,
            ...                         file_encoding="utf-8",
            ...                         replace_domain_codes_by_values=False, 
            ...                         report_errors=True)
        """
        data = clean_data({
            "file_uuid": file.uuid,
            "input_layer": input_layer_name,
            "input_geom_type": input_geom_type.value if isinstance(input_geom_type, InputGeomType) else input_geom_type,
            "replace_domain_codes_by_values": replace_domain_codes_by_values,
            "input_dataset": input_dataset,
            "user_id": user_id,
            "input_srid": input_srid,
            "file_encoding": file_encoding,
            "report_errors": report_errors
        })

        endpoint = urljoin(self.endpoint, 'import/')
        response = self.api.post(endpoint, data, is_json=False)
        task = Task.get_task(self.api, response.get('task_id'))
        return task


    def export_features(self, 
                            out_filename: str, 
                            out_format: 'FileOutputFormat', 
                            replace_domain_codes_by_values: bool = False, 
                            run_async: bool = True, 
                            bbox: List[float] = None, 
                            out_srid: int = None, 
                            zipped: bool = True, 
                            feature_ids: List[int] = None, 
                            bbox_srid: int = None, 
                            q: str = None, fields: List[str] = None) -> Union['Task', Dict]:
        """
        Export features from the layer to a file.
        
        Args:
            out_filename (str): Name of the output file.
            out_format (FileOutputFormat): Format of the output file (e.g., 'Shapefile', 'GPKG', 'GeoJSON', 'CSV', 'KML', 'DXF').
            replace_domain_codes_by_values (bool, optional): Whether to replace domain codes with values.
            run_async (bool, optional): Whether to run the export asynchronously.
            bbox (List, optional): Bounding box to filter features.
            out_srid (int): Spatial reference ID for the output.
            zipped (bool, optional): Whether to compress the output file.
            feature_ids (List[int], optional): List of specific feature IDs to export.
            bbox_srid (int, optional): Spatial reference ID for the bounding box.
            q (str, optional): Query to filter features.
            fields (List[str], optional): List of fields to include in the export.
            
        Returns:
            Task | Dict: The task instance of the export operation or the api response if run_async=False.
            
        Raises:
            ValidationError: If the export parameters are invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task = layer.export_features(out_filename="output.shp", 
            ...                         out_format="shp",
            ...                         replace_domain_codes_by_values=False, 
            ...                         run_async=True, 
            ...                         bbox=[10, 20, 30, 40], 
            ...                         out_srid=3857, 
            ...                         zipped=True, 
            ...                         feature_ids=[1, 2, 3])
        """
        data = clean_data({
            "replace_domain_codes_by_values": replace_domain_codes_by_values,
            "out_format": out_format.value,
            "run_async": run_async,
            "bbox": bbox,
            "out_srid": out_srid,
            "zipped": zipped,
            "feature_ids": feature_ids,
            "bbox_srid": bbox_srid,
            "q": q,
            "out_filename": out_filename,
            "fields": fields
        })

        endpoint = urljoin(self.endpoint, 'export/')
        response = self.api.post(endpoint, data, is_json=False)
        if run_async:
            task = Task.get_task(self.api, response.get('task_id'))
            return task

        return response


    def create_view(self, name: str, display_name: str = None, description: str = None, 
                    view_filter: str = None, view_extent: Dict = None, view_cols: str = None) -> 'VectorLayerView':
        """
        Create a view of the vector layer.

        Args:
            name (str): The name of the view.
            display_name (str, optional): The display name of the view.
            description (str, optional): The description of the view.
            view_filter (str, optional): The filter for the view.
            view_extent (List[float], optional): The extent of the view.
            view_cols (str, optional): The columns to include in the view.

        Returns:
            VectorLayerView: The created view instance.

        Raises:
            ValidationError: If the view parameters are invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> view = layer.create_view(name="my_view", 
            ...                         display_name="My View", 
            ...                         description="This is a view of my layer", 
            ...                         view_filter="province_name = 'Tehran'", 
            ...                         view_extent=[10, 20, 30, 40], 
            ...                         view_cols="[ALL]")
        """
        from .view import VectorLayerView

        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "view_filter": view_filter,
            "view_extent": view_extent,
            "view_cols": view_cols
        }

        return super()._create(api=self.api,
                            endpoint=f'{self.endpoint}views/',
                            data=data,
                            factory_func=lambda api, item: VectorLayerView(api, item['uuid'], self.layer_type, item))


    def get_tile_pbf_url(self, x: int = '{x}', y: int = '{y}', z: int = '{z}') -> str:
        """
        Get a vector tile for the layer.
        
        Args:
            x (int, optional): X coordinate of the tile.
            y (int, optional): Y coordinate of the tile.
            z (int, optioanl): Zoom level of the tile.

        Returns:
            str: The vector tile url.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tile = layer.get_tile(x=10, y=20, z=1)
        """
        endpoint = f'{self.api.base_url}{self.endpoint}tiles/{z}/{x}/{y}.pbf'

        if not self.api.access_token and self.api.apikey:
            endpoint = f'{endpoint}?apikey={self.api.apikey}'

        return endpoint


    def get_tile_json(self) -> Dict:
        """
        Get the vector tile JSON configuration for the layer.
        
        Returns:
            Dict: The vector tile JSON configuration.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> tile_json = layer.get_tile_json()
        """
        endpoint = urljoin(self.endpoint, 'tilejson.json') 
        return self.api.get(endpoint)


    @property
    def settings(self) -> Dict:
        """
        Get the layer's settings.
        
        Returns:
            Dict: The layer settings.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> setting = layer.setting
        """
        return super()._get_settings(endpoint=self.endpoint)


    def set_settings(self, **kwargs) -> Dict:
        """
        Set the settings of the Vector Layer.
        
        Keyword Args:
            title_field (str): The field to use as the title.
            domain_display_type (str): The type of domain display.
            allow_export (bool): Whether to allow export.
            editable (bool): Whether to allow editing.
            edit_geometry (bool): Whether to allow editing the geometry.
            editable_attributes (str): The attributes to allow editing.
            allow_insert (bool): Whether to allow inserting.
            allow_delete (bool): Whether to allow deleting.
            min_zoom (int): The minimum zoom level.
            max_zoom (int): The maximum zoom level.
            max_features (int): The maximum number of features.
            filter_features (bool): Whether to filter features.
            fields (List[str]): The fields to include in the layer.
            use_cache (bool): Whether to use caching.
            cache_until_zoom (int): The zoom level to cache until.
            
        Returns:
            Dict: The updated settings.
            
        Raises:
            ValidationError: If the settings data is invalid.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.set_settings(title_field="name",
            ...                      domain_display_type="Value",
            ...                      allow_export=True,
            ...                      editable=True,
            ...                      edit_geometry=True,
            ...                      editable_attributes="[ALL]",
            ...                      allow_insert=True,
            ...                      allow_delete=True,
            ...                      min_zoom=0,
            ...                      max_zoom=24,
            ...                      max_features=65536,
            ...                      filter_features=True,
            ...                      fields=["id"],
            ...                      use_cache=True,
            ...                      cache_until_zoom=17)
        """
        general_settings = {'title_field', 'domain_display_type', 'allow_export'}
        edit_settings = {'editable', 'edit_geometry', 'editable_attributes', 'allow_insert', 'allow_delete'}
        tile_settings = {'min_zoom', 'max_zoom', 'max_features', 'filter_features', 'fields', 'use_cache', 'cache_until_zoom'}

        settings = self.settings

        for key, value in kwargs.items():
            if key in general_settings:
                settings['general_settings'][key] = value
            elif key in edit_settings:
                settings['edit_settings'][key] = value
            elif key in tile_settings:
                settings['tile_settings'][key] = value

        return super()._set_settings(endpoint=self.endpoint, data=settings)


    def seed_cache(self, from_zoom: int = None, to_zoom: int = None, ignore_cache: bool = False, workers: int = 1, user_id: int = None) -> List['Task']:
        """
        Seed the cache for the layer.
        
        Args:
            from_zoom (int, optional): The zoom level to start caching from.
            to_zoom (int, optional): The zoom level to stop caching at.
            ignore_cache (bool, optional): Whether to ignore the cache. default is False.
            workers (int, optional): The number of workers to use. default is 1.
            user_id (int, optional): Specific user. privileges required.

        Returns:
            List[Task]: The task instance of the cache seeding operation.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task = layer.seed_cache(from_zoom=0, to_zoom=10, ignore_cache=False, workers=1)
        """
        data = {
            'from_zoom': from_zoom,
            'to_zoom': to_zoom,
            'ignore_cache': ignore_cache,
            'workers': workers,
            'user_id': user_id
        }
        return super()._seed_cache(endpoint=self.endpoint, data=data)
        

    def clear_cache(self) -> None:
        """
        Clear the layer's cache.
        
        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.clear_cache()
        """
        super()._clear_cache(endpoint=self.endpoint)
    

    @property
    def cache_size(self) -> int:
        """
        Get the size of the layer's cache.
        
        Returns:
            int: The size of the layer's cache.
            
        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.cache_size
        """
        return super()._cache_size(endpoint=self.endpoint)


    def update_stats(self) -> None:
        """
        Update the layer's statistics.
        
        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.update_stats()
        """
        endpoint = urljoin(self.endpoint, 'updateStats/')
        return self.api.post(endpoint)
    

    def prune_edited_areas(self) -> None:
        """
        Prune edited areas. This method eliminates edited areas when there are too many of them. Cache builder uses this edited areas for partial cache generating.
        
        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> client = GeoboxClient()
            >>> layer = VectorLayer.get_vector(api=client, uuid="12345678-1234-5678-1234-567812345678")
            >>> layer.prune_edited_areas()
        """
        endpoint = urljoin(self.endpoint, 'prune/')
        return self.api.post(endpoint)