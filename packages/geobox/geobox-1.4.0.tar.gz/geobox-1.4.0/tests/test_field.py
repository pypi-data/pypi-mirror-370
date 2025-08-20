import pytest
from urllib.parse import urljoin

from geobox.vectorlayer import VectorLayer, LayerType
from geobox.field import Field, FieldType


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_init(api, mock_field_data, mock_vector_data,  field_type):
    """Test Field initialization."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data)
    assert field.data_type == field_type
    assert field.datatype == field_type
    assert field.data == mock_field_data
    assert field.endpoint == urljoin(field.layer.endpoint, f"fields/{mock_field_data['id']}/")
    # error
    with pytest.raises(ValueError, match="data_type must be a FieldType instance"):
        field = Field(layer,
                data_type='invalid_data_type',
                data=mock_field_data)


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_init_without_id(api, mock_field_data, mock_vector_data,  field_type):
    """Test Field initialization without field_id."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    del mock_field_data['id']
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data)
    with pytest.raises(AttributeError):
        field.id
    assert field.endpoint is None
    assert field.data_type == field_type
    assert field.data == mock_field_data


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_repr(api, mock_field_data, mock_vector_data,  field_type):
    """Test the repr method of Field object for different data types"""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data)
    assert repr(field) == f"Field(id={field.id}, name={field.name}, data_type={field.data_type})"


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_get_domain(api, mock_field_data, mock_vector_data,  field_type):
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data)
    assert field.domain is None


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_set_domain(api, mock_field_data, mock_vector_data,  field_type):
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data)
    field.domain = {'min': 1, 'max': 10, 'items': {'1': 'value1', '2': 'value2'}}
    assert field.domain == {'min': 1, 'max': 10, 'items': {'1': 'value1', '2': 'value2'}}


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_create_field(api, mock_field_data, mock_vector_data,  field_type):
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    api.post.return_value = {**mock_field_data, 'datatype': field_type.value}
    field = Field.create_field(api, layer, 'test', field_type, mock_field_data)
    assert isinstance(field, Field)
    del mock_field_data['domain']
    del mock_field_data['width']
    del mock_field_data['display_name']
    del mock_field_data['description']
    api.post.assert_called_once_with(f"vectorLayers/{mock_vector_data['uuid']}/fields/", mock_field_data)


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_save_new_field(api, mock_field_data, mock_vector_data,  field_type):
    """Test saving a new field."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    id = mock_field_data['id']
    del mock_field_data['id']
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    with pytest.raises(AttributeError):
        field.id
    
    mock_field_data['id'] = id
    api.post.return_value = mock_field_data

    field.save()

    expected_data = {'name': 'test', 'datatype': field_type.value, 'hyperlink': False}

    api.post.assert_called_once_with(urljoin(field.layer.endpoint, 'fields/'), expected_data)
    assert field.id == mock_field_data["id"]
    assert field.data == mock_field_data
    assert field.endpoint == urljoin(field.layer.endpoint, f'fields/{mock_field_data["id"]}/')


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_save_existing_field(api, mock_field_data, mock_vector_data,  field_type):
    """Test saving an existing field."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    field.name = "new_osm_id"
    field.data["display_name"] = "New OSM ID"
    field.data["description"] = "New OSM ID field"
    field.save()

    expected_data = {
        "name": "new_osm_id",
        "datatype": field_type.value,
        "display_name": "New OSM ID",
        "description": "New OSM ID field",
        'hyperlink': False
    }

    api.put.assert_called_once_with(field.endpoint, expected_data)
    assert field.id == mock_field_data['id']
    assert field.name == "new_osm_id"
    assert field.data["display_name"] == "New OSM ID"
    assert field.data["description"] == "New OSM ID field"


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_delete(api, mock_field_data, mock_vector_data,  field_type):
    """Test deleting a field."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    endpoint = field.endpoint
    field.delete()
    api.delete.assert_called_once_with(endpoint)


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_update(api, mock_field_data, mock_vector_data,  field_type):
    """Test updating field properties."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    update_data = {
        "name": "updated_osm_id",
        "display_name": "Updated OSM ID",
        "description": "Updated OSM ID field"
    }
    
    api.put.return_value = {**field.data, **update_data}
    
    response = field.update(**update_data)
    
    expected_data = {'name': 'updated_osm_id', 'display_name': 'Updated OSM ID', 'description': 'Updated OSM ID field'}
    
    api.put.assert_called_once_with(field.endpoint, expected_data)
    assert response == {**field.data, **update_data}
    assert field.data == {**field.data, **update_data}


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_get_field_unique_values(api, mock_field_data, mock_vector_data,  field_type):
    """Test getting unique values of a field."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    expected_response = {"values": ["123456", "789012", "345678"]}
    api.get.return_value = expected_response
    
    response = field.get_field_unique_values()
    
    api.get.assert_called_once_with(urljoin(field.endpoint, 'distinct/'))
    assert response == expected_response


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_get_field_unique_values_numbers(api, mock_field_data, mock_vector_data,  field_type):
    """Test getting unique values count of a field."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    expected_response = {"count": 3}
    api.get.return_value = expected_response
    
    response = field.get_field_unique_values_numbers()
    
    api.get.assert_called_once_with(urljoin(field.endpoint, 'distinctCount/'))
    assert response == expected_response


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_get_field_statistic(api, mock_field_data, mock_vector_data,  field_type):
    """Test getting field statistics."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    expected_response = {"stat": 42}
    api.get.return_value = expected_response
    
    response = field.get_field_statistic("min")
    
    api.get.assert_called_once_with(urljoin(field.endpoint, 'stats/?func_type=min'))
    assert response == expected_response


@pytest.mark.parametrize("field_type", [FieldType.Integer, FieldType.Float, FieldType.String])
def test_update_domain(api, mock_field_data, mock_vector_data,  field_type):
    """Test updating the domain."""
    mock_field_data['datatype'] = field_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    field = Field(layer,
                    data_type=field_type,
                    data=mock_field_data.copy())
    range_d = {'min': 1, 'max': 10}
    list_d = {'1': 'value1', '2': 'value2'}
    mock_field_data['domain'] = {'min': 1, 'max': 10, 'items': {'1': 'value1', '2': 'value2'}}
    api.put.return_value = mock_field_data
    result = field.update_domain(range_domain = range_d, list_domain=list_d)
    assert result == {'min': 1, 'max': 10, 'items': {'1': 'value1', '2': 'value2'}}
    expected_response = {'name': 'test', 'datatype': field_type.value, 'domain': {'min': 1, 'max': 10, 'items': {'1': 'value1', '2': 'value2'}}, 'hyperlink': False}
    api.put.assert_called_once_with(field.endpoint, expected_response)