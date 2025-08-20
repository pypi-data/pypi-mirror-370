import pytest
from urllib.parse import urljoin, urlencode

from geobox.enums import FeatureType
from geobox.user import User
from geobox.view import VectorLayerView
from geobox.vectorlayer import VectorLayer, LayerType, FileOutputFormat, InputGeomType
from geobox.field import Field, FieldType
from geobox.exception import NotFoundError
from geobox.task import Task
from geobox.file import File
from geobox.utils import clean_data


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_init(api, mock_view_data, layer_type):
    """Test VectorLayerView initialization."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    assert view.name == mock_view_data['name']
    assert view.layer_type == layer_type
    assert view.uuid == mock_view_data['uuid']
    assert view.data == mock_view_data
    assert view.endpoint == f'{VectorLayerView.BASE_ENDPOINT}{view.uuid}/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_repr(api, mock_view_data, layer_type):
    """Test the repr method of VectorLayerView object"""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    assert repr(view) == f"VectorLayerView(uuid={view.uuid}, name={mock_view_data['name']}, layer_type={layer_type})"


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_vector_layer(api, mock_view_data, layer_type, mock_vector_data):
    """Test the vector_layer property."""
    view = VectorLayerView(
        api=api,
        layer_type=layer_type,
        uuid=mock_view_data['uuid'],
        data={
            **mock_view_data,
            "vector_layer": {
                **mock_vector_data,
                'layer_type': layer_type.value
            }
        }
    )

    vector_layer = view.vector_layer
    assert isinstance(vector_layer, VectorLayer)
    assert vector_layer.name == mock_vector_data['name']
    assert vector_layer.layer_type == layer_type
    assert vector_layer.uuid == mock_vector_data['uuid']


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_views(api, mock_view_data, layer_type):
    """Test getting all views."""
    view_data = {
        **mock_view_data,
        "layer_type": layer_type.value
    }
    api.get.return_value = [view_data ,view_data]

    views = VectorLayerView.get_views(api)

    expected_url = f"{VectorLayerView.BASE_ENDPOINT}?f=json&include_settings=False&temporary=False&return_count=False&skip=0&limit=10&shared=False"
    api.get.assert_called_once_with(expected_url)
    assert len(views) == 2
    assert isinstance(views[0], VectorLayerView)
    assert views[0].name == mock_view_data['name']
    assert views[0].layer_type == layer_type
    assert views[0].uuid == mock_view_data['uuid']


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_view(api, mock_view_data, layer_type):
    """Test getting a specific view."""
    view_data = {
        **mock_view_data,
        "layer_type": layer_type.value,
    }
    api.get.return_value = view_data

    view = VectorLayerView.get_view(api, mock_view_data['uuid'])

    api.get.assert_called_once_with(f'{VectorLayerView.BASE_ENDPOINT}{view.uuid}/?f=json')
    assert isinstance(view, VectorLayerView)
    assert view.name == mock_view_data['name']
    assert view.layer_type == layer_type
    assert view.uuid == mock_view_data['uuid']
    assert view.data == {
        **mock_view_data,
        "layer_type": layer_type.value,
    }


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_view_by_name(api, mock_view_data, layer_type):
    """Test getting a specific view by name."""
    view_data = {
        **mock_view_data,
        "layer_type": layer_type.value,
    }
    api.get.return_value = [view_data]

    view = VectorLayerView.get_view_by_name(api, name=mock_view_data['name'])

    api.get.assert_called_once_with(f'{VectorLayerView.BASE_ENDPOINT}?f=json&include_settings=False&temporary=False&q=name+%3D+%27capitals2%27&return_count=False&skip=0&limit=10&shared=False')
    assert isinstance(view, VectorLayerView)
    assert view.name == mock_view_data['name']
    assert view.layer_type == layer_type
    assert view.uuid == mock_view_data['uuid']
    assert view.data == {
        **mock_view_data,
        "layer_type": layer_type.value,
    }
    # not found
    view = VectorLayerView.get_view_by_name(api, name='not_found')
    assert view == None


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_views_by_ids(api, mock_view_data, layer_type):
    """Test the get_mosaics_by_ids method."""
    mock_response = [{**mock_view_data, **{'id': 1}}, {**mock_view_data, **{'id': 2}}]
    api.get.return_value = mock_response
    
    layers = VectorLayerView.get_views_by_ids(api, [1, 2])
    
    api.get.assert_called_once_with(f'{VectorLayerView.BASE_ENDPOINT}get-layers/?ids=%5B1%2C+2%5D&include_settings=False')
    assert len(layers) == 2
    assert all(isinstance(m, VectorLayerView) for m in layers)
    assert layers[0].data == {**mock_view_data, **{'id': 1}}
    assert layers[1].data == {**mock_view_data, **{'id': 2}}


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_update(api, mock_view_data, layer_type):
    """Test updating a view."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )

    # Mock the API response
    updated_data = {
        **mock_view_data,
        "name": "updated_view",
        "display_name": "Updated View",
        "description": "Updated description"
    }
    api.put.return_value = updated_data

    response = view.update(
        name="updated_view",
        display_name="Updated View",
        description="Updated description"
    )

    expected_data = {
        "name": "updated_view",
        "display_name": "Updated View",
        "description": "Updated description"
    }
    api.put.assert_called_once_with(view.endpoint, expected_data)
    assert response == updated_data
    assert view.data == updated_data


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_delete(api, mock_view_data, layer_type):
    """Test deleting a layer."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    endpoint = view.endpoint
    view.delete()
    api.delete.assert_called_once_with(endpoint)
    assert view.uuid is None
    assert view.layer_type == layer_type
    assert view.endpoint is None


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_share(api, mock_view_data, layer_type, mock_user_data):
    """Test file sharing."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    users = [
        User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
        User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
    ]
    view.share(users=users)
    api.post.assert_called_once_with(
        f'{view.endpoint}share/',
        {'user_ids': [1, 2]}, is_json=False
    )

@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_unshare(api, mock_view_data, layer_type, mock_user_data):
    """Test file unsharing."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    users = [
        User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
        User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
    ]
    view.unshare(users=users)
    api.post.assert_called_once_with(
        f'{view.endpoint}unshare/',
        {'user_ids': [1, 2]}, is_json=False
    )

@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_shared_users(api, mock_view_data, layer_type, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    api.get.return_value = mock_response
    
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    result = view.get_shared_users(search='user', limit=2)
    
    api.get.assert_called_once_with(
        f'{view.endpoint}shared-with-users/?search=user&skip=0&limit=2'
    )

    assert len(result) == 2
    assert result[0].first_name == 'test 1'
    assert result[0].last_name == 'test 1'
    assert result[1].first_name == 'test 2'
    assert result[1].last_name == 'test 2'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_fields(api, mock_view_data, layer_type, mock_field_data):
    """Test getting the fields of a layer."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.get.reset_mock()
    api.get.return_value = [mock_field_data, mock_field_data]
    fields = view.get_fields()
    assert len(fields) == 2
    assert type(fields[0]) == Field
    assert fields[0].data == mock_field_data
    api.get.assert_called_once_with(f'{view.endpoint}fields/')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_field(api, mock_view_data, layer_type, mock_field_data):
    """Test getting the fields of a layer."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.get.return_value = [mock_field_data, mock_field_data]
    field = view.get_field(field_id=mock_field_data['id'])

    assert type(field) == Field
    assert field.data == mock_field_data
    api.get.assert_called_once_with(f'{view.endpoint}fields/')


    assert type(field) == Field
    assert field.data == mock_field_data
    api.get.assert_called_once_with(f'{view.endpoint}fields/')

    # error
    api.get.return_value = []
    with pytest.raises(NotFoundError):
        view.get_field(field_id=mock_field_data['id'])


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_field_by_name(api, mock_view_data, layer_type, mock_field_data):
    """Test getting the fields of a layer."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.get.return_value = [mock_field_data, mock_field_data]
    field = view.get_field_by_name(name=mock_field_data['name'])

    assert type(field) == Field
    assert field.data == mock_field_data
    api.get.assert_called_once_with(f'{view.endpoint}fields/')

    # error
    api.get.return_value = []
    with pytest.raises(NotFoundError):
        view.get_field_by_name(name=mock_field_data['name'])


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_calculate_field(api, mock_view_data, layer_type, mock_success_task_data):
    """Test calculating a field."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.get.return_value = mock_success_task_data
    task = view.calculate_field(target_field='test_field', expression='name + "test"', q='name like "test"', bbox=[10, 20, 30, 40], bbox_srid=3857, feature_ids=[1, 2, 3])
    expected_data = {'target_field': 'test_field', 'expression': 'name + "test"', 'q': 'name like "test"', 'bbox': [10, 20, 30, 40], 'bbox_srid': 3857, 'feature_ids': [1, 2, 3], 'run_async': True}
    api.post.assert_called_once_with(urljoin(view.endpoint, 'calculateField/'), expected_data, is_json=False)
    assert isinstance(task, Task)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_features(api, mock_view_data, layer_type, mock_feature_data):
    """Test getting a specific feature."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    view.create_feature(geojson=mock_feature_data[FeatureType.Polygon.value])
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
    features = view.get_features(**params)
    query_string = urlencode(params)
    expected_endpoint = f'vectorLayerViews/{mock_view_data["uuid"]}/features/?{query_string}'
    api.get.assert_called_once_with(expected_endpoint)
    assert len(features) == 1
    assert features[0].id == mock_feature_data[FeatureType.Polygon.value]['id']
    assert features[0].layer == view
    assert features[0].data == mock_feature_data[FeatureType.Polygon.value]
    assert features[0].endpoint == f'vectorLayerViews/{mock_view_data["uuid"]}/features/{mock_feature_data[FeatureType.Polygon.value]["id"]}/'
    # return count
    api.get.return_value = {'count': 1}
    count = view.get_features(return_count=True)
    assert type(count) == int
    assert count == 1


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_feature(api, mock_view_data, layer_type, mock_feature_data):
    """Test getting a specific feature."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    view.create_feature(geojson=mock_feature_data[FeatureType.Polygon.value])
    api.get.return_value = mock_feature_data[FeatureType.Polygon.value]
    feature = view.get_feature(feature_id=int(mock_feature_data[FeatureType.Polygon.value]['id']), out_srid=4326)
    
    expected_endpoint = f'vectorLayerViews/{mock_view_data["uuid"]}/features/{int(mock_feature_data[FeatureType.Polygon.value]["id"])}'
    api.get.assert_called_once_with(expected_endpoint)
    
    assert feature is not None
    assert feature.id == mock_feature_data[FeatureType.Polygon.value]['id']
    assert feature.layer == view
    assert feature.srid == 4326
    assert feature.data == mock_feature_data[FeatureType.Polygon.value]
    assert feature.endpoint == f'vectorLayerViews/{mock_view_data["uuid"]}/features/{mock_feature_data[FeatureType.Polygon.value]["id"]}/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_create_feature(api, mock_view_data, layer_type, mock_feature_data):
    """Test creating a new feature."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.post.return_value = mock_feature_data[FeatureType.Polygon.value]
    feature = view.create_feature(geojson=mock_feature_data[FeatureType.Polygon.value])
    assert feature is not None
    assert feature.id == mock_feature_data[FeatureType.Polygon.value]['id']
    assert feature.layer == view
    assert feature.data == mock_feature_data[FeatureType.Polygon.value]
    assert feature.endpoint == f'vectorLayerViews/{mock_view_data["uuid"]}/features/{mock_feature_data[FeatureType.Polygon.value]["id"]}/'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_delete_features(api, mock_view_data, layer_type, mock_feature_data, mock_success_task_data):
    """Test deleting a specific feature."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    params = {
        'q': "name like 'test'",
        'bbox': [10, 20, 30, 40],
        'bbox_srid': 3857,
        'feature_ids': [mock_feature_data[FeatureType.Polygon.value]['id']],
        'run_async': True,
        'user_id': 123
    }
    task = view.delete_features(**params)
    assert isinstance(task, Task)
    expected_endpoint = f'vectorLayerViews/{mock_view_data["uuid"]}/deleteFeatures/'
    api.post.assert_called_once_with(expected_endpoint, params, is_json=False)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_import_features(api, mock_view_data, layer_type, mock_success_task_data, mock_file_data):
    """Test importing features."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    file = File(api, mock_file_data['uuid'], mock_file_data)
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    task = view.import_features(file=file, input_geom_type=InputGeomType.POINT, input_layer_name='test-layer', input_dataset='test-dataset', user_id=123, input_srid=3857, file_encoding='utf-8', replace_domain_codes_by_values=True, report_errors=True)
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
    api.post.assert_called_once_with(f"{view.endpoint}import/", expected_data, is_json=False)
    assert isinstance(task, Task)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_export_features(api, mock_view_data, layer_type, mock_success_task_data):
    """Test exporting features."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.get.return_value = mock_success_task_data
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    task = view.export_features(out_filename='test-file-name', out_format=FileOutputFormat.Shapefile, replace_domain_codes_by_values=True, run_async=True, bbox=[10, 20, 30, 40], out_srid=3857, zipped=True, feature_ids=[1, 2, 3], bbox_srid=3857, q='name like "test"', fields=['name', 'description'])
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
    api.post.assert_called_once_with(f"{view.endpoint}export/", expected_data, is_json=False)
    assert isinstance(task, Task)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_tile_pbf_url(api, mock_view_data, layer_type):
    """Test getting a vector tile."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    endpoint = view.get_tile_pbf_url(x=1, y=2, z=3)
    assert endpoint == f'{view.api.base_url}{view.endpoint}tiles/3/1/2.pbf'


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_get_tile_json(api, mock_view_data, layer_type):
    """Test getting a vector tile JSON."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.get.return_value = {'tile': 'value'}
    result = view.get_tile_json()
    api.get.assert_called_once_with(f'{view.endpoint}tilejson.json')
    assert result == {'tile': 'value'}


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_settings(api, mock_view_data, layer_type):
    """Test getting the settings of a layer."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.get.return_value = {'settings': 'value'}
    settings = view.settings
    api.get.assert_called_once_with(f'{view.endpoint}settings/?f=json')
    assert settings == {'settings': 'value'}


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_set_settings(api, mock_view_data, layer_type):
    """Test setting the settings of a layer."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
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
    api.put.return_value = expected_data
    new_settings = view.set_settings(**settings)
    api.put.assert_called_once_with(f'{view.endpoint}settings/', expected_data)
    assert new_settings == expected_data


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_seed_cache(api, mock_view_data, layer_type, mock_success_task_data):
    """Test caching a seed."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.post.return_value = [{'task_id': mock_success_task_data['id']}]
    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)
    task = view.seed_cache(from_zoom=0, to_zoom=10, ignore_cache=False, workers=1)[0]
    expected_data = {'from_zoom': 0, 'to_zoom': 10, 'ignore_cache': False, 'workers': 1}
    api.post.assert_called_once_with(f'{view.endpoint}cache/seed/', expected_data)
    assert isinstance(task, Task)


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_clear_cache(api, mock_view_data, layer_type):
    """Test clearing the cache."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    view.clear_cache()
    api.post.assert_called_once_with(f'{view.endpoint}cache/clear/')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_cache_size(api, mock_view_data, layer_type):
    """Test getting the size of the cache."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    api.post.return_value = 1024
    size = view.cache_size
    api.post.assert_called_once_with(f'{view.endpoint}cache/size/')
    assert size == 1024


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_update_stats(api, mock_view_data, layer_type):
    """Test updating the stats."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    view.update_stats()
    api.post.assert_called_once_with(f'{view.endpoint}updateStats/')


@pytest.mark.parametrize("layer_type", [type for type in LayerType])
def test_prune_edited_areas(api, mock_view_data, layer_type):
    """Test pruning the edited areas."""
    view = VectorLayerView(
        api=api,
        uuid=mock_view_data['uuid'],
        layer_type=layer_type,
        data=mock_view_data
    )
    view.prune_edited_areas()
    api.post.assert_called_once_with(f'{view.endpoint}prune/')