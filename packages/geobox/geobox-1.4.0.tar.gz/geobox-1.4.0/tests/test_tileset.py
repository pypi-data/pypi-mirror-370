import pytest
from urllib.parse import urljoin
from unittest.mock import patch

from geobox.tileset import Tileset
from geobox.enums import LayerType
from geobox.user import User
from geobox.task import Task
from geobox.vectorlayer import VectorLayer
from geobox.view import VectorLayerView


def test_init(api, mock_tileset_data):
    """Test Tileset initialization."""
    tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
    assert tileset.uuid == mock_tileset_data['uuid']
    assert tileset.data == mock_tileset_data
    assert tileset.endpoint == f'{Tileset.BASE_ENDPOINT}{mock_tileset_data["uuid"]}/'


def test_repr(api, mock_tileset_data):
    """Test Tileset string representation."""
    tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
    assert repr(tileset) == f"Tileset(uuid={tileset.uuid}, name={mock_tileset_data['name']})"


def test_getattr(api, mock_tileset_data):
    """Test Tileset attribute access."""
    tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
    assert tileset.name == mock_tileset_data['name']
    assert tileset.display_name == mock_tileset_data['display_name']
    assert tileset.description == mock_tileset_data['description']
    assert tileset.min_zoom == mock_tileset_data['min_zoom']
    assert tileset.max_zoom == mock_tileset_data['max_zoom']
    assert tileset.state == mock_tileset_data['state']
    with pytest.raises(AttributeError):
        _ = tileset.nonexistent_attribute


def test_create_tileset(api, mock_tileset_data, mock_vector_data, mock_view_data):
    """Test creating a tileset"""
    api.post.return_value = mock_tileset_data
    layers = [VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data), 
                VectorLayerView(api, uuid=mock_view_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_view_data)]
    tileset = Tileset.create_tileset(api, 
                                        mock_tileset_data['name'], 
                                        layers=layers,
                                        display_name=mock_tileset_data['display_name'], 
                                        description=mock_tileset_data['description'], 
                                        min_zoom=mock_tileset_data['min_zoom'], 
                                        max_zoom=mock_tileset_data['max_zoom'])
    assert isinstance(tileset, Tileset)
    assert tileset.uuid == mock_tileset_data['uuid']
    assert tileset.data == mock_tileset_data
    api.post.assert_called_once_with('tilesets/', {'name': mock_tileset_data['name'], 
                                                    'min_zoom': mock_tileset_data['min_zoom'], 
                                                    'max_zoom': mock_tileset_data['max_zoom'], 
                                                    'layers': [{'layer_type': 'vector', 
                                                                'layer_uuid': mock_vector_data['uuid']}, 
                                                                {'layer_type': 'view', 
                                                                'layer_uuid': mock_view_data['uuid']}]})


def test_get_tilesets(api, mock_tileset_data):
    """Test getting tilesets"""
    tilesets = [mock_tileset_data for _ in range(3)]
    with patch.object(api, 'get', return_value=tilesets):
        tilesets_list = Tileset.get_tilesets(api)
        assert tilesets_list is not None
        assert len(tilesets_list) == 3
        assert isinstance(tilesets_list[0], Tileset)
        assert tilesets_list[0].uuid == mock_tileset_data['uuid']
        assert tilesets_list[0].data == mock_tileset_data


def test_get_tilesets_by_ids(api, mock_tileset_data):
    api.get.return_value = [{**mock_tileset_data, **{'id': 1}}, {**mock_tileset_data, **{'id': 2}}]
    tilesets = Tileset.get_tilesets_by_ids(api, [1, 2])
    assert isinstance(tilesets[0], Tileset)
    assert tilesets[0].uuid == mock_tileset_data['uuid']
    assert tilesets[0].data == {**mock_tileset_data, **{'id': 1}}


def test_get_tileset(api, mock_tileset_data):
    """Test getting tileset by UUID."""
    with patch.object(api, 'get', return_value=mock_tileset_data):
        tileset = Tileset.get_tileset(api, uuid=mock_tileset_data['uuid'])
        assert isinstance(tileset, Tileset)
        assert tileset.uuid == mock_tileset_data['uuid']
        assert tileset.name == mock_tileset_data['name']
        api.get.assert_called_once_with(tileset.endpoint)


def test_get_tileset_by_name(api, mock_tileset_data):
    """Test getting tileset by UUID."""
    with patch.object(api, 'get', return_value=[mock_tileset_data]):
        tileset = Tileset.get_tileset_by_name(api, name=mock_tileset_data['name'])
        assert isinstance(tileset, Tileset)
        assert tileset.uuid == mock_tileset_data['uuid']
        assert tileset.name == mock_tileset_data['name']
        api.get.assert_called_once_with(f"{Tileset.BASE_ENDPOINT}?f=json&q=name+%3D+%27test_tile%27&return_count=False&skip=0&limit=10&shared=False")
        # not found
        tileset = Tileset.get_tileset_by_name(api, name='not_found')
        assert tileset == None


def test_update(api, mock_tileset_data):
    """Test updating tileset properties."""
    updated_data = {
        'name': 'updated_name',
        'display_name': 'Updated Tileset',
        'description': 'Updated description',
        'min_zoom': 1,
        'max_zoom': 15
    }
    with patch.object(api, 'put', return_value=updated_data):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        tileset.update(
            name='updated_name',
            display_name='Updated Tileset',
            description='Updated description',
            min_zoom=1,
            max_zoom=15
        )
        assert tileset.name == 'updated_name'
        assert tileset.display_name == 'Updated Tileset'
        assert tileset.description == 'Updated description'
        assert tileset.min_zoom == 1
        assert tileset.max_zoom == 15


def test_delete(api, mock_tileset_data):
    """Test deleting tileset."""
    with patch.object(api, 'delete'):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        endpoint = tileset.endpoint
        tileset.delete()
        api.delete.assert_called_once_with(endpoint)


def test_get_layers(api, mock_tileset_data, mock_vector_data, mock_view_data):
    """Test getting tileset layers."""
    mock_layers = [
        mock_vector_data,
        mock_view_data
    ]
    with patch.object(api, 'get', return_value=mock_layers):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        layers = tileset.get_layers()
        assert len(layers) == 2
        assert layers[0].name == mock_vector_data['name']
        assert type(layers[0]) == VectorLayer
        assert layers[1].name == mock_view_data['name']
        assert type(layers[1]) == VectorLayerView

    # return count
    with patch.object(api, 'get', return_value=10):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        layer_count = tileset.get_layers(return_count=True)
        assert layer_count == 10
        api.get.assert_called_once_with(f'{tileset.endpoint}layers/?f=json&return_count=True&skip=0&limit=10&shared=False')


def test_add_layer(api, mock_tileset_data, mock_vector_data, mock_view_data):
    """Test adding layer to tileset."""
    with patch.object(api, 'post'):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
        view = VectorLayerView(api, uuid=mock_view_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_view_data)
        tileset.add_layer(layer=layer)
        endpoint = urljoin(tileset.endpoint, 'layers/')
        api.post.assert_called_once_with(endpoint, {'layer_type': 'vector', 'layer_uuid': mock_vector_data['uuid']}, is_json=False)
        api.post.reset_mock()
        tileset.add_layer(layer=view)
        api.post.assert_called_once_with(endpoint, {'layer_type': 'view', 'layer_uuid': mock_view_data['uuid']}, is_json=False)

        # usupported input
        with pytest.raises(ValueError):
            tileset.add_layer(layer='')


def test_delete_layer(api, mock_tileset_data, mock_vector_data, mock_view_data):
    """Test deleting layer from tileset."""
    with patch.object(api, 'delete'):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
        view = VectorLayerView(api, uuid=mock_view_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_view_data)
        tileset.delete_layer(layer=layer)
        endpoint = urljoin(tileset.endpoint, 'layers/')
        api.delete.assert_called_once_with(endpoint, {'layer_type': 'vector', 'layer_uuid': mock_vector_data['uuid']}, is_json=False)
        api.delete.reset_mock()
        tileset.delete_layer(layer=view)
        api.delete.assert_called_once_with(endpoint, {'layer_type': 'view', 'layer_uuid': mock_view_data['uuid']}, is_json=False)

        # usupported input
        with pytest.raises(ValueError):
            tileset.delete_layer(layer='')


def test_share(api, mock_tileset_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        tileset.share(users=users)
        api.post.assert_called_once_with(
            f'{tileset.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )

def test_unshare(api, mock_tileset_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        tileset.unshare(users=users)
        api.post.assert_called_once_with(
            f'{tileset.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_tileset_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        result = tileset.get_shared_users(search='user', limit=2)
        
        api.get.assert_called_once_with(
            f'{tileset.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'


def test_get_tile_json(api, mock_tileset_data):
    """Test getting tile JSON."""
    mock_tilejson = {
        'tiles': ['https://api.geobox.ir/v1/tilesets/test-uuid-123/tiles/{z}/{x}/{y}.pbf'],
        'minzoom': 0,
        'maxzoom': 14
    }
    with patch.object(api, 'get', return_value=mock_tilejson):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        tilejson = tileset.get_tile_json()
        assert tilejson == mock_tilejson
        endpoint = urljoin(tileset.endpoint, 'tilejson.json/')
        api.get.assert_called_once_with(endpoint)


def test_update_tileset_extent(api, mock_tileset_data):
    """Test updating tileset extent."""
    with patch.object(api, 'post', return_value={'message': 'Extent updated'}):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        result = tileset.update_tileset_extent()
        assert result == {'message': 'Extent updated'}
        endpoint = urljoin(tileset.endpoint, 'updateExtent/')
        api.post.assert_called_once_with(endpoint)


def test_get_tile_pbf_url(api, mock_tileset_data):
    """Test getting tile from tileset."""
    tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
    url = tileset.get_tile_pbf_url(x=1, y=1, z=1)
    assert url == f"{api.base_url}{tileset.endpoint}tiles/1/1/1.pbf"
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    url = tileset.get_tile_pbf_url(x=1, y=1, z=1)
    assert url == f"{api.base_url}{tileset.endpoint}tiles/1/1/1.pbf?apikey=apikey_1234"


def test_seed_cache(api, mock_tileset_data, mock_success_task_data):
    tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
    api.post.return_value = [{'task_id': mock_success_task_data['id']}, {'task_id': mock_success_task_data['id']}]
    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)

    expected_data = {
        "from_zoom": 0,
        "workers": 4,
        "to_zoom": 10,
        "extent": [10, 20, 30, 40],
        "user_id": 0
    }

    api.get.return_value = mock_success_task_data
    task = tileset.seed_cache(from_zoom=0, workers=4, to_zoom=10, extent=[10, 20, 30, 40])[0]
    assert task.id == mock_success_task_data['id']
    api.post.assert_called_once_with(f'{tileset.endpoint}cache/seed/', expected_data)


def test_update_cache(api, mock_tileset_data, mock_success_task_data):
    tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
    task_data = {'task_id': mock_success_task_data['id'], 'status': 'pending'}
    api.post.return_value = [{'task_id': mock_success_task_data['id']}]
    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)

    api.get.return_value = mock_success_task_data

    task = tileset.update_cache(from_zoom=0, to_zoom=2, extents=[[1, 2, 3, 4]], user_id=1)[0]
    assert isinstance(task, Task)
    api.post.assert_called_once_with(f'{tileset.endpoint}cache/update/', {'from_zoom': 0, 'to_zoom': 2, 'extents': [[1, 2, 3, 4]], 'user_id': 1})
    # error
    api.post.return_value = [1, 2, 3]

    api.get.return_value = mock_success_task_data

    with pytest.raises(ValueError, match="Failed to update cache"):
        task = tileset.update_cache(from_zoom=0, to_zoom=2)
        

def test_clear_cache(api, mock_tileset_data):
    """Test clearing tileset cache."""
    with patch.object(api, 'post'):
        tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
        result = tileset.clear_cache()
        endpoint = urljoin(tileset.endpoint, 'cache/clear/')
        api.post.assert_called_once_with(endpoint) 


def test_cache_size(api, mock_tileset_data):
    tileset = Tileset(api, uuid=mock_tileset_data['uuid'], data=mock_tileset_data)
    api.post.return_value = 1024
    size = tileset.cache_size
    assert size == 1024
    api.post.assert_called_once_with(f'{tileset.endpoint}cache/size/')
