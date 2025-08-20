from urllib.parse import urljoin
from typing import Optional, Dict, TYPE_CHECKING, Any

from .base import Base
from .utils import clean_data
from .enums import FieldType

if TYPE_CHECKING:
    from .api import GeoboxClient
    from .vectorlayer import VectorLayer

class Field(Base):
    """
    A class representing a field in a vector layer in Geobox.

    This class provides functionality to create, manage, and manipulate fields in a vector layer.
    It supports various operations including CRUD operations on fields, as well as advanced operations like getting unique values, statistics, and updating fields.
    It also provides properties to access the field data, and a method to update the field.
    """
    def __init__(self, 
                 layer: 'VectorLayer',
                 data_type: 'FieldType',
                 field_id: int = None,
                 data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Field object.

        Args:
            layer (VectorLayer): The vector layer that the field belongs to.
            data_type (FieldType): type of the field
            field_id (int): the id of the field
            data (Dict, optional): The data of the field.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> field_data = {
            ...     "name": "test"
            ... }
            >>> field = Field(layer=layer, data_type=FieldType.Integere, data=field_data)
            >>> field.save()
        """
        super().__init__(api=layer.api, data=data)
        self.layer = layer
        self.field_id = field_id
        if not isinstance(data_type, FieldType):
            raise ValueError("data_type must be a FieldType instance")
        self.data_type = data_type
        self.endpoint = urljoin(layer.endpoint, f'fields/{self.id}/') if self.data.get('id') else None


    def __repr__(self) -> str:
        """
        Return a string representation of the field.

        Returns:
            str: The string representation of the field.
        """
        return f"Field(id={self.id}, name={self.name}, data_type={self.data_type})"

        
    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the resource.

        Args:
            name (str): The name of the attribute
        """
        if name == 'datatype':
            return FieldType(self.data['datatype'])
        return super().__getattr__(name)


    @property
    def domain(self) -> Dict:
        """
        Domain property

        Returns:
            Dict: domain data
        """
        return self.data.get('domain')


    @domain.setter
    def domain(self, value: Dict) -> None:
        """
        Domain property setter

        Returns:
            None
        """
        self.data['domain'] = value
        

    @classmethod
    def create_field(cls, api: 'GeoboxClient', layer: 'VectorLayer', name: str, data_type: 'FieldType', data: Dict = {}) -> 'Field':
        """
        Create a new field

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            layer (VectorLayer): field's layer
            name (str): name of the field
            data_type (FieldType): type of the field
            data (Dict, optional): the data of the field

        Returns:
            Field: the created field object

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.vectorlayer import VectorLayer
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_layer(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = Field.create_field(client, layer=layer, name='test', data_type=FieldType.Integer)
        """
        data.update({
            "name": name,
            "datatype": data_type.value
        })
        endpoint = urljoin(layer.endpoint, 'fields/')
        return super()._create(api, endpoint, data, factory_func=lambda api, item: Field(layer, data_type, item['id'], item))


    def save(self) -> None:
        """
        Save the field. Creates a new field if field_id is None, updates existing field otherwise.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = Field(layer=layer, data_type=FieldType.String)
            >>> field.save()
        """
        data = clean_data({
            "name": self.name,
            "datatype": FieldType(self.data_type).value,
            "display_name": self.data.get("display_name"),
            "description": self.data.get("description"),
            "domain": self.data.get("domain"),
            "width": self.data.get("width"),
            "hyperlink": self.data.get("hyperlink")
        })
        
        try: 
            if self.id:
                response = self.layer.api.put(self.endpoint, data)
        except AttributeError:
            endpoint = urljoin(self.layer.endpoint, 'fields/')
            response = self.layer.api.post(endpoint, data)
            self.id = response['id']
            self.endpoint = urljoin(self.layer.endpoint, f'fields/{self.id}/')
        
        self._update_properties(response)


    def delete(self) -> None:
        """
        Delete the field.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = layer.get_field(name='test')
            >>> field.delete()
        """
        super().delete(self.endpoint)
        self.field_id = None


    def update(self, **kwargs) -> Dict:
        """
        Update the field.

        Keyword Args:
            name (str): The name of the field.
            display_name (str): The display name of the field.
            description (str): The description of the field.
            domain (Dict): the domain of the field
            width (int): The width of the field.
            hyperlink (bool): the hyperlink field.

        Returns:
            Dict: The updated data.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = Field(layer=layer, data_type=FieldType.String)
            >>> field.update(name="my_field", display_name="My Field", description="My Field Description")
        """       
        data = {
            "name": kwargs.get('name'),
            "display_name": kwargs.get('display_name'),
            "description": kwargs.get('description'),
            "domain": kwargs.get('domain'),
            "hyperlink": kwargs.get('hyperlink')
        }
        return super()._update(self.endpoint, data)


    def get_field_unique_values(self) -> Dict:
        """
        Get the unique values of the field.

        Returns:
            Dict: The response data.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = layer.get_field(name='test')
            >>> field.get_field_unique_values()
        """
        endpoint = urljoin(self.endpoint, 'distinct/')
        return self.layer.api.get(endpoint)


    def get_field_unique_values_numbers(self) -> Dict:
        """
        Get the unique values of the field.

        Returns:
            Dict: The response data.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = layer.get_field(name='test')
            >>> field.get_field_unique_values_numbers()
        """
        endpoint = urljoin(self.endpoint, 'distinctCount/')
        return self.layer.api.get(endpoint)


    def get_field_statistic(self, func: str) -> Dict:
        """
        Get the statistic of the field.

        Args:
            func (str): The function to apply to the field. values are: min, max, avg

        Returns:
            Dict: The response data.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.field import Field
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> field = layer.get_field(name='test')
            >>> field.get_field_statistic(func='avg')
        """
        endpoint = urljoin(self.endpoint, f'stats/?func_type={func}')
        return self.layer.api.get(endpoint)


    def update_domain(self, range_domain: Dict = None, list_domain: Dict = None) -> Dict:
        """
        Update field domian values

        Args:
            range_domain (Dict): a dictionary with min and max keys.
            list_domain (Dict): a dictionary containing the domain codes and values.

        Returns:
            Dict: the updated field domain

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> field = client.get_vector(uuid="12345678-1234-5678-1234-567812345678").get_fields()[0]
            >>> range_d = {'min': 1, 'max': 10}
            >>> list_d = {'1': 'value1', '2': 'value2'}
            >>> field.update_domain(range_domain = range_d, list_domain=list_d)
            {'min': 1, 'max': 10, 'items: {'1': 'value1', '2': 'value2'}}
        """
        if not self.domain:
            self.domain = {'min': None, 'max': None, 'items': {}}

        if range_domain:
            self.domain['min'] = range_domain['min']
            self.domain['max'] = range_domain['max']

        if list_domain:
            self.domain['items'] = {**self.domain['items'], **list_domain}

        self.save()
        return self.domain
