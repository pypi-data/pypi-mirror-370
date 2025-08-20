import pytest
from urllib.parse import urlencode
from urllib.parse import urljoin
from unittest.mock import patch

from geobox.enums import FeatureType
from geobox.vectorlayer import VectorLayer, LayerType, InputGeomType, FileOutputFormat
from geobox.version import VectorLayerVersion
from geobox.field import Field, FieldType
from geobox.view import VectorLayerView
from geobox.user import User
from geobox.task import Task
from geobox.file import File
from geobox.exception import NotFoundError
from geobox.utils import clean_data


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_init(api, mock_vector_data, layer_type):
    """Test VectorLayer initialization."""
    layer = VectorLayer(api, 
                            uuid=mock_vector_data['uuid'], 
                            data=mock_vector_data,
                            layer_type=layer_type)
    assert layer.name == mock_vector_data["name"]
    assert layer.layer_type == layer_type
    assert layer.uuid == mock_vector_data["uuid"]
    assert layer.data == mock_vector_data
    assert layer.endpoint == f'{VectorLayer.BASE_ENDPOINT}{mock_vector_data["uuid"]}/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_repr(api, mock_vector_data, layer_type):
    """Test the repr method of Layer object for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    assert repr(layer) == f"VectorLayer(uuid={layer.uuid}, name={mock_vector_data['name']}, layer_type={layer_type})"


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_vectors(api, mock_vector_data, layer_type):
    """Test getting a list of layers."""
    mock_vector_data['layer_type'] = layer_type.value
    api.get.return_value = [mock_vector_data, mock_vector_data]

    layers = VectorLayer.get_vectors(api)

    assert len(layers) == 2
    assert isinstance(layers[0], VectorLayer)
    assert layers[0].data == mock_vector_data
    assert layers[0].layer_type == layer_type
    assert layers[0].uuid == mock_vector_data['uuid']
    assert layers[0].endpoint == f"{VectorLayer.BASE_ENDPOINT}{mock_vector_data['uuid']}/"
    api.get.assert_called_once_with(f'{VectorLayer.BASE_ENDPOINT}?f=json&include_settings=False&temporary=False&return_count=False&skip=0&limit=10&shared=False')
    # return count
    api.reset_mock()
    api.get.return_value = 1
    count = VectorLayer.get_vectors(api, return_count=True)
    assert type(count) == int
    assert count == 1
    api.get.assert_called_once_with(f'{VectorLayer.BASE_ENDPOINT}?f=json&include_settings=False&temporary=False&return_count=True&skip=0&limit=10&shared=False')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_vector(api, mock_vector_data, layer_type):
    """Test getting a specific layer."""
    mock_vector_data["layer_type"] = layer_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = mock_vector_data

    layer = VectorLayer.get_vector(api, mock_vector_data["uuid"])

    assert layer.name == mock_vector_data["name"]
    assert layer.layer_type.value == layer_type.value
    assert layer.uuid == mock_vector_data["uuid"]
    assert layer.data == mock_vector_data
    assert layer.endpoint == f'{VectorLayer.BASE_ENDPOINT}{mock_vector_data["uuid"]}/'
    api.get.assert_called_once_with(f'{layer.endpoint}?f=json')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_vector_by_name(api, mock_vector_data, layer_type):
    """Test getting a specific layer."""
    mock_vector_data["layer_type"] = layer_type.value
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = [mock_vector_data]

    layer = VectorLayer.get_vector_by_name(api, name=mock_vector_data["name"])

    assert layer.name == mock_vector_data["name"]
    assert layer.layer_type.value == layer_type.value
    assert layer.uuid == mock_vector_data["uuid"]
    assert layer.data == mock_vector_data
    assert layer.endpoint == f'{VectorLayer.BASE_ENDPOINT}{mock_vector_data["uuid"]}/'
    api.get.assert_called_once_with(f'{VectorLayer.BASE_ENDPOINT}?f=json&include_settings=False&temporary=False&q=name+%3D+%27tehran_water%27&return_count=False&skip=0&limit=10&shared=False')
    # not found
    layer = VectorLayer.get_vector_by_name(api, name='not_found')
    assert layer == None


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_vectors_by_ids(api, mock_vector_data, layer_type):
    """Test the get_mosaics_by_ids method."""
    mock_response = [{**mock_vector_data, **{'id': 1}}, {**mock_vector_data, **{'id': 2}}]
    api.get.return_value = mock_response
    
    layers = VectorLayer.get_vectors_by_ids(api, [1, 2])
    
    api.get.assert_called_once_with(f'{VectorLayer.BASE_ENDPOINT}get-layers/?ids=%5B1%2C+2%5D&include_settings=False')
    assert len(layers) == 2
    assert all(isinstance(m, VectorLayer) for m in layers)
    assert layers[0].data == {**mock_vector_data, **{'id': 1}}
    assert layers[1].data == {**mock_vector_data, **{'id': 2}}



@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_create_vector(api, mock_vector_data, layer_type):
    """Test creating a new layer."""
    api.post.return_value = mock_vector_data

    layer = VectorLayer.create_vector(
        api,
        name=mock_vector_data["name"],
        layer_type=layer_type,
        display_name=mock_vector_data["display_name"]
    )

    expected_data = {
        "name": mock_vector_data["name"],
        "layer_type": layer_type.value,
        "has_z": mock_vector_data["has_z"],
        "temporary": False
    }

    api.post.assert_called_once_with('vectorLayers/', expected_data)
    assert layer.name == mock_vector_data["name"]
    assert layer.layer_type == layer_type
    assert layer.uuid == mock_vector_data["uuid"]
    assert layer.data == mock_vector_data
    assert layer.endpoint == f'{VectorLayer.BASE_ENDPOINT}{mock_vector_data["uuid"]}/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_update( api, mock_vector_data, layer_type):
    """Test updating layer properties."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    new_name = "updated_layer"
    new_display_name = "Updated Layer"
    
    # Response data - what we get back from the API
    api_response = {
        **mock_vector_data,
        'name': new_name,
        'display_name': new_display_name
    }
    api.put.return_value = api_response

    response = layer.update(
        name=new_name,
        display_name=new_display_name
    )

    # Only include the fields we're updating
    expected_data = {
        "name": new_name,
        "display_name": new_display_name
    }

    api.put.assert_called_once_with(layer.endpoint, expected_data)
    assert response == api_response
    assert layer.data == api_response


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_delete(api, mock_vector_data, layer_type):
    """Test deleting a layer."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    endpoint = layer.endpoint
    layer.delete()
    api.delete.assert_called_once_with(endpoint)
    assert layer.uuid is None
    assert layer.layer_type == layer_type
    assert layer.endpoint is None


def test_make_permanent(api, mock_vector_data):
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=LayerType.Point)
    layer.make_permanent()
    api.post.assert_called_once_with(f'{layer.endpoint}makePermanent/', is_json=False)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_share(api, mock_vector_data, layer_type, mock_user_data):
    """Test file sharing."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    users = [
        User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
        User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
    ]
    layer.share(users=users)
    api.post.assert_called_once_with(
        f'{layer.endpoint}share/',
        {'user_ids': [1, 2]}, is_json=False
    )


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_unshare(api, mock_vector_data, layer_type, mock_user_data):
    """Test file unsharing."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    users = [
        User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
        User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
    ]
    layer.unshare(users=users)
    api.post.assert_called_once_with(
        f'{layer.endpoint}unshare/',
        {'user_ids': [1, 2]}, is_json=False
    )


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_shared_users(api, mock_vector_data, layer_type, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    api.get.return_value = mock_response
    
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    result = layer.get_shared_users(search='user', limit=2)

    api.get.assert_called_once_with(
        f'{layer.endpoint}shared-with-users/?search=user&skip=0&limit=2'
    )

    assert len(result) == 2
    assert result[0].first_name == 'test 1'
    assert result[0].last_name == 'test 1'
    assert result[1].first_name == 'test 2'
    assert result[1].last_name == 'test 2'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_create_version(api, mock_vector_data, layer_type, mock_version_data):
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = mock_version_data
    version = layer.create_version(name=mock_version_data['name'], display_name=mock_version_data['display_name'], description=mock_version_data['description'])
    assert isinstance(version, VectorLayerVersion)
    assert version.uuid == mock_version_data['uuid']
    assert version.data == mock_version_data
    api.post.assert_called_once_with(f'{layer.endpoint}versions', {'name': 'design_version', 'display_name': 'Design Version', 'description': 'This layer represents design version.'})


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_versions(api, mock_vector_data, layer_type, mock_version_data):
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = [mock_version_data]
    versions = layer.get_versions()
    assert len(versions) == 1
    assert versions[0].uuid == mock_version_data['uuid']
    assert versions[0].data == mock_version_data
    api.get.assert_called_once_with(f'vectorLayerVersions/?layer_id={layer.id}&f=json&return_count=False&skip=0&limit=10&shared=False')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_wfs_access_token(api, mock_vector_data, layer_type):
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    wfs_url = layer.wfs
    assert wfs_url == f'{api.base_url}{layer.endpoint}wfs/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_wfs_apikey(api, mock_vector_data, layer_type):
    api.access_token = None
    api.apikey = '123456789'
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    wfs_url = layer.wfs
    assert wfs_url == f'{api.base_url}{layer.endpoint}apikey:{api.apikey}/wfs/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_fields(api, mock_vector_data, layer_type, mock_field_data):
    """Test getting the fields of a layer."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.reset_mock()
    api.get.return_value = [mock_field_data, mock_field_data]
    fields = layer.get_fields()
    assert len(fields) == 2
    assert type(fields[0]) == Field
    assert fields[0].data == mock_field_data
    api.get.assert_called_once_with(f'{layer.endpoint}fields/')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_field(api, mock_vector_data, layer_type, mock_field_data):
    """Test getting the fields of a layer."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = [mock_field_data, mock_field_data]
    field = layer.get_field(field_id=mock_field_data['id'])
    assert type(field) == Field
    assert field.data == mock_field_data
    api.get.assert_called_once_with(f'{layer.endpoint}fields/')


    assert type(field) == Field
    assert field.data == mock_field_data
    api.get.assert_called_once_with(f'{layer.endpoint}fields/')

    # error
    api.get.return_value = []
    with pytest.raises(NotFoundError):
        layer.get_field(field_id=mock_field_data['id'])



@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_field_by_name(api, mock_vector_data, layer_type, mock_field_data):
    """Test getting the fields of a layer."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = [mock_field_data, mock_field_data]
    field = layer.get_field_by_name(name=mock_field_data['name'])

    assert type(field) == Field
    assert field.data == mock_field_data
    api.get.assert_called_once_with(f'{layer.endpoint}fields/')

    # error
    api.get.return_value = []
    with pytest.raises(NotFoundError):
        layer.get_field_by_name(name=mock_field_data['name'])


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_add_field(api, mock_vector_data, layer_type, mock_field_data):
    """Test adding a field to a layer."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = mock_field_data
    del mock_field_data['created_at']
    field = layer.add_field(name=mock_field_data['name'], data_type=FieldType.String, data=mock_field_data)
    assert isinstance(field, Field)
    assert field.name == mock_field_data['name']
    assert field.data_type == FieldType.String
    assert field.layer == layer
    assert field.endpoint == f'{layer.endpoint}fields/{field.id}/'
    assert field.data == mock_field_data
    expected_data = {'id': mock_field_data['id'], 
                        'name': mock_field_data['name'], 
                        'datatype': mock_field_data['datatype'], 
                        'hyperlink': mock_field_data['hyperlink']}
    api.post.assert_called_once_with(f'{layer.endpoint}fields/', expected_data)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_calculate_field(api, mock_vector_data, layer_type, mock_success_task_data):
    """Test calculating a field."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = mock_success_task_data
    task = layer.calculate_field(target_field='test_field', expression='name + "test"', q='name like "test"', bbox=[10, 20, 30, 40], bbox_srid=3857, feature_ids=[1, 2, 3])
    expected_data = {'target_field': 'test_field', 'expression': 'name + "test"', 'q': 'name like "test"', 'bbox': [10, 20, 30, 40], 'bbox_srid': 3857, 'feature_ids': [1, 2, 3], 'run_async': True}
    api.post.assert_called_once_with(urljoin(layer.endpoint, 'calculateField/'), expected_data, is_json=False)
    assert isinstance(task, Task)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_calculate_field_sync(api, mock_vector_data, layer_type):
    """Test calculating a field."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = {'key': 'value'}
    response = layer.calculate_field(target_field='test_field', expression='name + "test"', q='name like "test"', bbox=[10, 20, 30, 40], bbox_srid=3857, feature_ids=[1, 2, 3], run_async=False)
    expected_data = {'target_field': 'test_field', 'expression': 'name + "test"', 'q': 'name like "test"', 'bbox': [10, 20, 30, 40], 'bbox_srid': 3857, 'feature_ids': [1, 2, 3], 'run_async': False}
    api.post.assert_called_once_with(urljoin(layer.endpoint, 'calculateField/'), expected_data, is_json=False)
    assert isinstance(response, dict)
    assert response['key'] == 'value'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_features(api, mock_vector_data, layer_type, mock_feature_data):
    """Test getting a specific feature."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    layer.create_feature(geojson=mock_feature_data[FeatureType.Polygon.value])
    api.get.return_value = {
        'features': [mock_feature_data[FeatureType.Polygon.value]],
        'crs': {
            'properties': {
                'name': 'EPSG:3857'
            }
        }
    }
    params = clean_data({
        'f': 'json',
        'quant_factor': 1000000,
        'skip': 0,
        'limit': 100,
        'user_id': 123,
        'skip_geometry': False,
        'return_count': False,
        'feature_ids': [mock_feature_data[FeatureType.Polygon.value]['id']],
        'select_fields': "[ALL]",
        'out_srid': 3857,
        'order_by': "name",
        'q': "name like 'test'",
        'bbox_srid': 3857
    })
    features = layer.get_features(**params)
    query_string = urlencode(params)
    expected_endpoint = f'vectorLayers/{mock_vector_data["uuid"]}/features/?{query_string}'
    api.get.assert_called_once_with(expected_endpoint)
    assert len(features) == 1
    assert features[0].id == mock_feature_data[FeatureType.Polygon.value]['id']
    assert features[0].layer == layer
    assert features[0].data == mock_feature_data[FeatureType.Polygon.value]
    assert features[0].endpoint == f'vectorLayers/{mock_vector_data["uuid"]}/features/{mock_feature_data[FeatureType.Polygon.value]["id"]}/'
    # return count
    api.get.return_value = {'count': 1}
    count = layer.get_features(return_count=True)
    assert type(count) == int
    assert count == 1


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_feature(api, mock_vector_data, layer_type, mock_feature_data):
    """Test getting a specific feature."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    layer.create_feature(geojson=mock_feature_data[FeatureType.Polygon.value])
    api.get.return_value = mock_feature_data[FeatureType.Polygon.value]
    feature = layer.get_feature(feature_id=int(mock_feature_data[FeatureType.Polygon.value]['id']), out_srid=4326)
    
    expected_endpoint = f'vectorLayers/{mock_vector_data["uuid"]}/features/{int(mock_feature_data[FeatureType.Polygon.value]["id"])}'
    api.get.assert_called_once_with(expected_endpoint)
    
    assert feature is not None
    assert feature.id == mock_feature_data[FeatureType.Polygon.value]['id']
    assert feature.layer == layer
    assert feature.srid == 4326
    assert feature.data == mock_feature_data[FeatureType.Polygon.value]
    assert feature.endpoint == f'vectorLayers/{mock_vector_data["uuid"]}/features/{mock_feature_data[FeatureType.Polygon.value]["id"]}/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_create_feature(api, mock_vector_data, layer_type, mock_feature_data):
    """Test creating a new feature."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = mock_feature_data[FeatureType.Polygon.value]
    feature = layer.create_feature(geojson=mock_feature_data[FeatureType.Polygon.value])
    assert feature is not None
    assert feature.id == mock_feature_data[FeatureType.Polygon.value]['id']
    assert feature.layer == layer
    assert feature.data == mock_feature_data[FeatureType.Polygon.value]
    assert feature.endpoint == f'vectorLayers/{mock_vector_data["uuid"]}/features/{mock_feature_data[FeatureType.Polygon.value]["id"]}/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_delete_features(api, mock_vector_data, layer_type, mock_feature_data, mock_success_task_data):
    """Test deleting a specific feature."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    params = {
        'q': "name like 'test'",
        'bbox': [10, 20, 30, 40],
        'bbox_srid': 3857,
        'feature_ids': [mock_feature_data[FeatureType.Polygon.value]['id']],
        'run_async': True,
        'user_id': 123
    }
    api.get.return_value = mock_success_task_data
    task = layer.delete_features(**params)
    assert isinstance(task, Task)
    expected_endpoint = f'vectorLayers/{mock_vector_data["uuid"]}/deleteFeatures/'
    api.post.assert_called_once_with(expected_endpoint, params, is_json=False)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_delete_features_sync(api, mock_vector_data, layer_type, mock_feature_data):
    """Test deleting a specific feature."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = {'key': 'value'}
    params = {
        'q': "name like 'test'",
        'bbox': [10, 20, 30, 40],
        'bbox_srid': 3857,
        'feature_ids': [mock_feature_data[FeatureType.Polygon.value]['id']],
        'run_async': False,
        'user_id': 123
    }
    response = layer.delete_features(**params)
    assert isinstance(response, dict)
    assert response['key'] == 'value'
    expected_endpoint = f'vectorLayers/{mock_vector_data["uuid"]}/deleteFeatures/'
    api.post.assert_called_once_with(expected_endpoint, params, is_json=False)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_import_features(api, mock_vector_data, layer_type, mock_success_task_data, mock_file_data):
    """Test importing features."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    file = File(api, mock_file_data['uuid'], mock_file_data)
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    task = layer.import_features(file=file, input_geom_type=InputGeomType.POINT, input_layer_name='test-layer', input_dataset='test-dataset', user_id=123, input_srid=3857, file_encoding='utf-8', replace_domain_codes_by_values=True, report_errors=True)
    expected_data = {
        'file_uuid': mock_file_data['uuid'],
        'input_layer': 'test-layer',
        'input_geom_type': 'POINT',
        'replace_domain_codes_by_values': True,
        'input_dataset': 'test-dataset',
        'user_id': 123,
        'input_srid': 3857,
        'file_encoding': 'utf-8',
        'report_errors': True
    }
    api.post.assert_called_once_with(f"{layer.endpoint}import/", expected_data, is_json=False)
    assert isinstance(task, Task)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_export_features(api, mock_vector_data, layer_type, mock_success_task_data):
    """Test exporting features."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = mock_success_task_data
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    task = layer.export_features(out_filename='test-file-name', out_format=FileOutputFormat.Shapefile, replace_domain_codes_by_values=True, run_async=True, bbox=[10, 20, 30, 40], out_srid=3857, zipped=True, feature_ids=[1, 2, 3], bbox_srid=3857, q='name like "test"', fields=['name', 'description'])
    expected_data = {
        'replace_domain_codes_by_values': True,
        'out_format': 'Shapefile',
        'run_async': True,
        'bbox': [10, 20, 30, 40],
        'out_srid': 3857,
        'zipped': True,
        'feature_ids': [1, 2, 3],
        'bbox_srid': 3857,
        'q': 'name like "test"',
        'fields': ['name', 'description'],
        'out_filename': 'test-file-name'
    }
    api.post.assert_called_once_with(f"{layer.endpoint}export/", expected_data, is_json=False)
    assert isinstance(task, Task)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_export_features_sync(api, mock_vector_data, layer_type):
    """Test exporting features."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = {'key': 'value'}
    response = layer.export_features(out_filename='test-file-name', out_format=FileOutputFormat.Shapefile, replace_domain_codes_by_values=True, run_async=False, bbox=[10, 20, 30, 40], out_srid=3857, zipped=True, feature_ids=[1, 2, 3], bbox_srid=3857, q='name like "test"', fields=['name', 'description'])
    expected_data = {
        'replace_domain_codes_by_values': True,
        'out_format': 'Shapefile',
        'run_async': False,
        'bbox': [10, 20, 30, 40],
        'out_srid': 3857,
        'zipped': True,
        'feature_ids': [1, 2, 3],
        'bbox_srid': 3857,
        'q': 'name like "test"',
        'fields': ['name', 'description'],
        'out_filename': 'test-file-name'
    }
    api.post.assert_called_once_with(f"{layer.endpoint}export/", expected_data, is_json=False)
    assert isinstance(response, dict)
    assert response['key'] == 'value'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_create_view(api, mock_vector_data, layer_type, mock_view_data):
    """Test creating a new view."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = mock_view_data
    mock_view_data['vector_layer'] = mock_vector_data
    expected_data = {
        'name': mock_view_data['name'],
        'display_name': mock_view_data['display_name'],
        'description': mock_view_data['description'],
        'view_filter': mock_view_data['view_filter'], 
        'view_extent': mock_view_data['extent'], 
        'view_cols': mock_view_data['view_cols']
    }

    view = layer.create_view(**expected_data)

    api.post.assert_called_once_with(urljoin(layer.endpoint, 'views/'), expected_data)
    
    # Verify the view object
    assert isinstance(view, VectorLayerView)
    assert view.name == mock_view_data['name']
    assert view.description == mock_view_data['description']
    assert view.layer_type == layer_type
    assert view.uuid == mock_view_data['uuid']
    assert view.data == mock_view_data
    assert isinstance(view.vector_layer, VectorLayer)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_tile_pbf_url(api, mock_vector_data, layer_type):
    """Test getting a vector tile."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    url = layer.get_tile_pbf_url(x=1, y=2, z=3)
    assert url == f'{layer.api.base_url}{layer.endpoint}tiles/3/1/2.pbf'
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    url = layer.get_tile_pbf_url(x=1, y=2, z=3)
    assert url == f'{layer.api.base_url}{layer.endpoint}tiles/3/1/2.pbf?apikey=apikey_1234'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_tile_json(api, mock_vector_data, layer_type):
    """Test getting a vector tile JSON."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = {'tile': 'value'}
    result = layer.get_tile_json()
    api.get.assert_called_once_with(f'{layer.endpoint}tilejson.json')
    assert result == {'tile': 'value'}


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_settings(api, mock_vector_data, layer_type):
    """Test getting the settings of a layer."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = {'settings': 'value'}
    settings = layer.settings
    api.get.assert_called_once_with(f'{layer.endpoint}settings/?f=json')
    assert settings == {'settings': 'value'}


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_set_settings(api, mock_vector_data, layer_type):
    """Test setting the settings of a layer."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.get.return_value = {
        "general_settings": {
            "title_field": None,
            "domain_display_type": "Value",
            "allow_export": True
        },
        "edit_settings": {
            "editable": True,
            "edit_geometry": True,
            "editable_attributes": "[ALL]",
            "allow_insert": True,
            "allow_delete": True
        },
        "tile_settings": {
            "min_zoom": 0,
            "max_zoom": 24,
            "max_features": 65536,
            "filter_features": True,
            "fields": [
            "id"
            ],
            "use_cache": True,
            "cache_until_zoom": 17
        }
        }
    settings = {
        'title_field': 'name',
        'domain_display_type': ' value',
        'allow_export': True,
        'editable': True,
        'edit_geometry': True,
        'editable_attributes': ['name', 'description'],
        'allow_insert': True,
        'allow_delete': True,
        'min_zoom': 0,
        'max_zoom': 24,
        'max_features': 10000,
        'filter_features': True,
        'fields': ['name', 'description'],
        'use_cache': True,
        'cache_until_zoom': 17
    }

    layer.set_settings(**settings)

    expected_data = {
        'general_settings': {
            'title_field': settings['title_field'],
            'domain_display_type': settings['domain_display_type'],
            'allow_export': settings['allow_export']
        },
        'edit_settings': {
            'editable': settings['editable'],
            'edit_geometry': settings['edit_geometry'],
            'editable_attributes': settings['editable_attributes'],
            'allow_insert': settings['allow_insert'],
            'allow_delete': settings['allow_delete']
        },
        'tile_settings': {
            'min_zoom': settings['min_zoom'],
            'max_zoom': settings['max_zoom'],
            'max_features': settings['max_features'],
            'filter_features': settings['filter_features'],
            'fields': settings['fields'],
            'use_cache': settings['use_cache'],
            'cache_until_zoom': settings['cache_until_zoom']
        }
    }
    api.put.assert_called_once_with(f'{layer.endpoint}settings/', expected_data)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_seed_cache(api, mock_vector_data, layer_type, mock_success_task_data):
    """Test caching a seed."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = [{'task_id': mock_success_task_data['id']}]
    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)
    task = layer.seed_cache(from_zoom=0, to_zoom=10, ignore_cache=False, workers=1)[0]
    expected_data = {'from_zoom': 0, 'to_zoom': 10, 'ignore_cache': False, 'workers': 1}
    api.post.assert_called_once_with(f'{layer.endpoint}cache/seed/', expected_data)
    assert isinstance(task, Task)
    # error
    with pytest.raises(ValueError, match="workers must be in \\[1, 2, 4, 8, 12, 16, 20, 24\\]"):
        layer.seed_cache(workers=5)

    api.post.return_value = {'ivalid_response': 'value', 'invalid_response': 'value'}
    with pytest.raises(ValueError, match="Failed to seed cache"):
        layer.seed_cache()


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_clear_cache(api, mock_vector_data, layer_type):
    """Test clearing the cache."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    layer.clear_cache()
    api.post.assert_called_once_with(f'{layer.endpoint}cache/clear/')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_cache_size(api, mock_vector_data, layer_type):
    """Test getting the size of the cache."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    api.post.return_value = 1024
    size = layer.cache_size
    api.post.assert_called_once_with(f'{layer.endpoint}cache/size/')
    assert size == 1024


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_update_stats(api, mock_vector_data, layer_type):
    """Test updating the stats."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    layer.update_stats()
    api.post.assert_called_once_with(f'{layer.endpoint}updateStats/')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_prune_edited_areas(api, mock_vector_data, layer_type):
    """Test pruning the edited areas."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], data=mock_vector_data, layer_type=layer_type)
    layer.prune_edited_areas()
    api.post.assert_called_once_with(f'{layer.endpoint}prune/')
