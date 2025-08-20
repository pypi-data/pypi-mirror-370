from urllib.parse import urljoin
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from geobox.map import Map
from geobox.model3d import Model
from geobox.user import User
from geobox.task import Task


def test_init(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    assert map.name == mock_map_data['name']
    assert map.uuid == mock_map_data['uuid']
    assert map.endpoint == f'maps/{mock_map_data["uuid"]}/'


def test_repr(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    assert repr(map) == f"Map(uuid={map.uuid}, name={map.name})"


def test_attribute_access(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    assert map.display_name == mock_map_data['display_name']
    assert map.description == mock_map_data['description']
    assert map.extent == mock_map_data['extent']
    assert map.created_at == datetime.strptime(mock_map_data['created_at'], "%Y-%m-%dT%H:%M:%S.%f")
    assert map.last_modified_at == datetime.strptime(mock_map_data['last_modified_at'], "%Y-%m-%dT%H:%M:%S.%f")

    with pytest.raises(AttributeError):
        _ = map.nonexistent_attribute


@patch('geobox.map.urljoin')
@patch('geobox.map.urlencode')
def test_get_maps(mock_urlencode, mock_urljoin, api, mock_map_data):
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = 'maps/?f=json'
    
    # Mock API response
    api.get.return_value = [mock_map_data, mock_map_data]

    maps = Map.get_maps(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    assert len(maps) == 2
    assert maps[0].uuid == mock_map_data['uuid']
    assert maps[0].data == mock_map_data
    api.get.assert_called_once_with(f'{Map.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')

    # Test with return_count
    api.reset_mock()
    api.get.return_value = 5
    count = Map.get_maps(api, return_count=True)
    assert count == 5
    api.get.assert_called_once_with(f'{Map.BASE_ENDPOINT}?f=json&return_count=True&skip=0&limit=10&shared=False')


def test_create_map(api):
    map_data = {
        'uuid': 'test-uuid-123',
        'name': 'Test Map',
        'display_name': 'Test Display Name',
        'description': 'Test Description',
        'extent': [10, 20, 30, 40],
        'thumbnail': 'https://example.com/thumbnail.png',
        'style': {'type': 'style'}
    }
    api.post.return_value = map_data

    map = Map.create_map(
        api,
        name='Test Map',
        display_name='Test Display Name',
        description='Test Description',
        extent=[10, 20, 30, 40],
        thumbnail='https://example.com/thumbnail.png',
        style={'type': 'style'}
    )

    assert map.uuid == map_data['uuid']
    assert map.data == map_data
    del map_data['uuid']
    api.post.assert_called_once_with(Map.BASE_ENDPOINT, map_data)


@patch('geobox.map.urljoin')
@patch('geobox.map.urlencode')
def test_get_map(mock_urlencode, mock_urljoin, api, mock_map_data):
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = f'maps/{mock_map_data["uuid"]}/?f=json'
    api.get.return_value = mock_map_data

    map = Map.get_map(api, mock_map_data['uuid'])
    assert map.uuid == mock_map_data['uuid']
    assert map.data == mock_map_data
    api.get.assert_called_once_with(f"{map.endpoint}?f=json")


@patch('geobox.map.urljoin')
@patch('geobox.map.urlencode')
def test_get_map_by_name(mock_urlencode, mock_urljoin, api, mock_map_data):
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = f'{Map.BASE_ENDPOINT}?f=json'
    api.get.return_value = [mock_map_data]

    map = Map.get_map_by_name(api, name=mock_map_data['name'])
    assert map.uuid == mock_map_data['uuid']
    assert map.data == mock_map_data
    api.get.assert_called_once_with(f"{Map.BASE_ENDPOINT}?f=json&q=name+%3D+%27my_map%27&return_count=False&skip=0&limit=10&shared=False")
    # not found
    map = Map.get_map_by_name(api, name='not_found')
    assert map == None


def test_update(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    updated_data = {
        'name': 'Updated Map',
        'display_name': 'Updated Display Name',
        'description': 'Updated Description'
    }
    api.put.return_value = updated_data

    response = map.update(
        name='Updated Map',
        display_name='Updated Display Name',
        description='Updated Description'
    )

    assert response == updated_data
    assert map.name == 'Updated Map'
    assert map.display_name == 'Updated Display Name'
    assert map.description == 'Updated Description'
    api.put.assert_called_once_with(map.endpoint, updated_data)


def test_delete(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    endpoint = map.endpoint
    map.delete()
    assert map.uuid is None
    assert map.endpoint is None
    api.delete.assert_called_once_with(endpoint)


def test_style(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    style_data = {'type': 'style', 'version': '1.0'}
    api.get.return_value = style_data
    style = map.style
    assert style == style_data
    api.get.assert_called_once_with(f"{map.endpoint}style/")


def test_thumbnail(api, mock_map_data):
    api.access_token = ''
    api.apikey = 'apikey_1234'
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    thumbnail_url = map.thumbnail
    assert thumbnail_url == f'{api.base_url}{map.endpoint}thumbnail.png?apikey=apikey_1234'
    # error
    api.apikey = ''
    with pytest.raises(ValueError):
        map.thumbnail


def test_set_readonly(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    response_data = {'readonly': True}
    api.post.return_value = response_data

    map.set_readonly(True)
    assert map.readonly is True
    api.post.assert_called_once_with(urljoin(map.endpoint, 'setReadonly/'), response_data, is_json=False)


def test_set_multiuser(api, mock_map_data):
    map = Map(api, uuid='test-uuid-123', data=mock_map_data)
    response_data = {'multiuser': True}
    api.post.return_value = response_data

    map.set_multiuser(True)
    assert map.multiuser is True
    api.post.assert_called_once_with(urljoin(map.endpoint, 'setMultiuser/'), response_data, is_json=False)


def test_wmts(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    wmts_url = map.wmts(scale=1)
    assert wmts_url == f'{api.base_url}{map.endpoint}wmts/?scale=1'
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    wmts_url = map.wmts(scale=1)
    assert wmts_url == f"{api.base_url}{map.endpoint}wmts/?scale=1&apikey=apikey_1234"


def test_share(api, mock_map_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        map.share(users=users)
        api.post.assert_called_once_with(
            f'{map.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_map_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        map = Map(api, uuid='test-uuid-123', data=mock_map_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        map.unshare(users=users)
        api.post.assert_called_once_with(
            f'{map.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_map_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
        result = map.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{map.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'


def test_seed_cache(api, mock_map_data, mock_success_task_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    task_data = {'task_id': mock_success_task_data['id']}
    api.post.return_value = task_data

    expected_data = {
        "from_zoom": 0,
        "workers": 4,
        "to_zoom": 10,
        "extent": [10, 20, 30, 40]
    }

    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)
    task = map.seed_cache(from_zoom=0, workers=4, to_zoom=10, extent=[10, 20, 30, 40])[0]
    assert task.id == mock_success_task_data['id']
    api.post.assert_called_once_with(f'{map.endpoint}cache/seed/', expected_data)


def test_update_cache(api, mock_map_data, mock_success_task_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    task_data = {'task_id': mock_success_task_data['id'], 'status': 'pending'}
    api.post.return_value = [task_data]

    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)

    task = map.update_cache(from_zoom=0, to_zoom=10, extent=[10, 20, 30, 40])[0]
    assert task.id == mock_success_task_data['id']
    api.post.assert_called_once_with(f'{map.endpoint}cache/update/', 
                                    {'from_zoom': 0, 'to_zoom': 10, 'extent': [10, 20, 30, 40]})


def test_clear_cache(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    map.clear_cache()
    api.post.assert_called_once_with(f'{map.endpoint}cache/clear/')


def test_cache_size(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    api.post.return_value = 1024
    size = map.cache_size
    assert size == 1024
    api.post.assert_called_once_with(f'{map.endpoint}cache/size/')


def test_settings(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    api.get.return_value = {'settings': 'value'}
    settings = map.settings
    assert settings == mock_map_data['settings']


def test_set_settings(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    settings = map.settings
    settings['general_settings']['base_map'] = 'osm-light'
    settings['edit_settings']['editable_layers'] = 'test'
    settings['snap_settings']['snap_cache'] = 1000
    settings['search_settings']['geosearch'] = True
    settings['marker_settings']['remvoe_unused_tags'] = False
    settings['controls'] = ["coordinates"]
    settings['terrain_settings']['exaggeration'] = 2
    settings['grid_settings']['grid_width'] = 2
    settings['view_settings']['zoom'] = 22
    settings['toc_settings'] = ['test']
    api.put.return_value = settings

    map.set_settings(base_map='osm-light', 
                        editable_layers='test', 
                        snap_cache=1000,
                        geosearch=True,
                        remove_unused_tags=False,
                        controls=["coordinates"],
                        exaggeration=2,
                        grid_width=2,
                        zoom=22,
                        toc_settings=['test'])
    assert map.settings == settings
    api.put.assert_called_once_with(f'{map.endpoint}settings/', settings)


def test_get_markers(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    markers_data = {
        'tags': {'#general': {'color': '#ff0000'}},
        'locations': [
            {
                'id': 1,
                'tag': '#general',
                'name': 'test',
                'geometry': [51.13162784422988, 35.766603814763045],
                'description': 'string'
            }
        ]
    }
    api.get.return_value = markers_data

    result = map.get_markers()
    assert result == markers_data
    api.get.assert_called_once_with(f'{map.endpoint}markers/')


def test_set_markers(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    markers_data = {
        'tags': {'#general': {'color': '#ff0000'}},
        'locations': [
            {
                'id': 1,
                'tag': '#general',
                'name': 'test',
                'geometry': [51.13162784422988, 35.766603814763045],
                'description': 'string'
            }
        ]
    }
    api.put.return_value = markers_data

    response = map.set_markers(markers_data)
    assert response == markers_data
    api.put.assert_called_once_with(f'{map.endpoint}markers/', markers_data)


def test_get_models(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    models_data = {
        'objects': [
            {
                'name': 'transmission_tower',
                'alias': None,
                'desc': None,
                'obj': '4079e850-055b-42a0-b35a-40d6d29ae21e',
                'loc': [53.1859045261684, 33.37762747390032, 0.0],
                'rotation': [0.0, 0.0, 0.0],
                'scale': 1.0,
                'min_zoom': 0,
                'max_zoom': 22
            }
        ]
    }
    api.get.return_value = models_data

    # Test with json=True
    result = map.get_models(json=True)
    assert result == models_data
    api.get.assert_called_once_with(f'{map.endpoint}models/')

    # Test without json=True
    result = map.get_models()
    assert len(result) == 1
    assert result[0].name == 'transmission_tower'
    assert result[0].data == models_data['objects'][0]
    assert isinstance(result[0], Model)


def test_set_models(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    
    # Create a mock Model object
    model = MagicMock()
    model.json = {
        'name': 'transmission_tower',
        'alias': None,
        'desc': None,
        'obj': '4079e850-055b-42a0-b35a-40d6d29ae21e',
        'loc': [53.1859045261684, 33.37762747390032, 0.0],
        'rotation': [0.0, 0.0, 0.0],
        'scale': 1.0,
        'min_zoom': 0,
        'max_zoom': 22
    }
    
    models_data = {
        'objects': [model.json]
    }
    api.put.return_value = models_data

    # Pass a dictionary as expected by the current implementation
    response = map.set_models(models_data)
    assert len(response) == 1
    assert response[0].name == 'transmission_tower'
    api.put.assert_called_once_with(f'{map.endpoint}models/', models_data)


def test_add_model(api, mock_map_data, mock_model_data, mock_map_model_data):
    # Initialize Map and Model objects with mock data
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    
    # Create a Model instance using the same UUID as in mock_map_model_data
    model = Model(
        api, 
        uuid=mock_map_model_data['obj'],  # Use the UUID from mock_map_model_data
        data={
            **mock_model_data,
            'uuid': mock_map_model_data['obj'],  # Override with expected UUID
            'name': mock_map_model_data['name']  # Override with expected name
        }
    )
    
    # Test Case 1: Adding first model to empty map
    api.get.return_value = {'objects': []}  # Empty map
    api.put.return_value = {'objects': [mock_map_model_data]}
    
    result = map.add_model(
        model,
        location=mock_map_model_data['loc'],
        rotation=mock_map_model_data['rotation'],
        scale=mock_map_model_data['scale'],
        min_zoom=mock_map_model_data['min_zoom'],
        max_zoom=mock_map_model_data['max_zoom']
    )
    
    # Verify API calls
    api.get.assert_called_once()  # Should check existing models
    api.put.assert_called_once_with(
        urljoin(map.endpoint, 'models/'),
        {'objects': [mock_map_model_data]}  # Now this will match exactly
    )
    
    # Verify return value
    assert len(result) == 1
    assert isinstance(result[0], Model)
    assert result[0].uuid == mock_map_model_data['obj']


def test_add_model_with_existing_models(api, mock_map_data, mock_model_data, mock_map_model_data):
    # Initialize Map with mock data
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)
    
    # Create a Model instance using the same UUID as in mock_map_model_data
    model = Model(
        api,
        uuid=mock_map_model_data['obj'],
        data={
            **mock_model_data,
            'uuid': mock_map_model_data['obj'],
            'name': mock_map_model_data['name']
        }
    )

    # Test Case: Adding a model to a map that already has models
    existing_model = {
        'name': 'existing_model',
        'alias': 'old_alias',
        'desc': 'old_description',
        'obj': 'existing-uuid-123',
        'loc': [10.0, 20.0, 0.0],
        'rotation': [0.0, 0.0, 0.0],
        'scale': 1.0,
        'min_zoom': 0,
        'max_zoom': 22
    }

    # Mock the initial GET response (map with existing models)
    api.get.return_value = {'objects': [existing_model]}
    
    # Expected response after adding new model
    expected_response = {
        'objects': [existing_model, mock_map_model_data]
    }
    api.put.return_value = expected_response

    # Call add_model
    result = map.add_model(
        model,
        location=mock_map_model_data['loc'],
        rotation=mock_map_model_data['rotation'],
        scale=mock_map_model_data['scale'],
        min_zoom=mock_map_model_data['min_zoom'],
        max_zoom=mock_map_model_data['max_zoom']
    )

    # Verify the API was called with both existing and new model
    expected_data = {
        'objects': [
            existing_model,
            {
                'name': mock_map_model_data['name'],
                'alias': None,
                'desc': None,
                'obj': mock_map_model_data['obj'],
                'loc': mock_map_model_data['loc'],
                'rotation': mock_map_model_data['rotation'],
                'scale': mock_map_model_data['scale'],
                'min_zoom': mock_map_model_data['min_zoom'],
                'max_zoom': mock_map_model_data['max_zoom']
            }
        ]
    }
    api.put.assert_called_once_with(
        urljoin(map.endpoint, 'models/'),
        expected_data
    )

    # Verify return value contains both models
    assert len(result) == 2
    assert all(isinstance(m, Model) for m in result)
    assert result[0].uuid == existing_model['obj']
    assert result[1].uuid == mock_map_model_data['obj']


def test_image_tile_url(api, mock_map_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)

    assert map.image_tile_url() == f"{map.api.base_url}{map.endpoint}tiles/"+"{z}/{x}/{y}.png"
    assert map.image_tile_url(x=1, y=2, z=3, format='.pbf') == f"{map.api.base_url}{map.endpoint}tiles/3/1/2.pbf"

    # apikey
    api.access_token = ''
    api.apikey = 'apikey@1234'

    assert map.image_tile_url() == f"{map.api.base_url}{map.endpoint}tiles/"+"{z}/{x}/{y}.png?apikey=apikey@1234"


def test_export_map_to_image(api, mock_map_data, mock_success_task_data):
    map = Map(api, uuid=mock_map_data['uuid'], data=mock_map_data)

    api.post.return_value = {
        'task_id': mock_success_task_data['uuid']
    }
    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)

    task = map.export_map_to_image(bbox=[50.275, 35.1195, 51.4459, 36.0416], width=100, height=100)
    
    api.post.assert_called_once_with('maps/da9a505b-7b51-4042-a3ba-c821e4f2cd34/export/?uuid=da9a505b-7b51-4042-a3ba-c821e4f2cd34&bbox=%5B50.275%2C+35.1195%2C+51.4459%2C+36.0416%5D&width=100&height=100')
    assert type(task) == Task
