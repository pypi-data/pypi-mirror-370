import pytest
from unittest.mock import patch

from geobox.tile3d import Tile3d
from geobox.user import User

def test_init(api, mock_tile3d_data):
    tile3d = Tile3d(api, mock_tile3d_data['uuid'], mock_tile3d_data)
    assert tile3d.name == mock_tile3d_data['name']
    assert tile3d.uuid == mock_tile3d_data['uuid']
    assert tile3d.data == mock_tile3d_data
    assert tile3d.endpoint == f'{Tile3d.BASE_ENDPOINT}{tile3d.uuid}/'


def test_get_3dtiles(api, mock_tile3d_data):
    api.get.return_value = [mock_tile3d_data, mock_tile3d_data]
    tile3ds = Tile3d.get_3dtiles(api)
    api.get.assert_called_once_with(f'{Tile3d.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')
    assert len(tile3ds) == 2
    assert type(tile3ds[0]) == Tile3d
    assert tile3ds[0].data == mock_tile3d_data


def test_get_3dtile(api, mock_tile3d_data):
    api.get.return_value = mock_tile3d_data
    tile3d = Tile3d.get_3dtile(api, uuid=mock_tile3d_data['uuid'])
    api.get.assert_called_once_with(f"{Tile3d.BASE_ENDPOINT}{mock_tile3d_data['uuid']}/?f=json")
    assert type(tile3d) == Tile3d
    assert tile3d.uuid == mock_tile3d_data['uuid']
    assert tile3d.data == mock_tile3d_data


def test_get_3dtile_by_name(api, mock_tile3d_data):
    api.get.return_value = [mock_tile3d_data]
    tile3d = Tile3d.get_3dtile_by_name(api, name=mock_tile3d_data['name'])
    api.get.assert_called_once_with(f"{Tile3d.BASE_ENDPOINT}?f=json&q=name+%3D+%27abasabad%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(tile3d) == Tile3d
    assert tile3d.uuid == mock_tile3d_data['uuid']
    assert tile3d.data == mock_tile3d_data
    # not found
    tile3d = Tile3d.get_3dtile_by_name(api, name='not_found')
    assert tile3d == None


def test_update(api, mock_tile3d_data):
    tile3d = Tile3d(api, mock_tile3d_data['uuid'], mock_tile3d_data)
    updated_data = {**mock_tile3d_data,
                    'settings': {'settings': 'value'},
                    'thumbnail': 'thumbnail-url'}

    api.put.return_value = updated_data
    tile3d.update(settings={'settings': 'value'}, thumbnail='thumbnail-url')
    api.put.assert_called_once_with(tile3d.endpoint, {'settings': {'settings': 'value'}, 'thumbnail': 'thumbnail-url'})


def test_delete(api, mock_tile3d_data):
    tile3d = Tile3d(api, mock_tile3d_data['uuid'], mock_tile3d_data)
    endpoint = tile3d.endpoint
    tile3d.delete()
    api.delete.assert_called_once_with(endpoint)
    assert tile3d.uuid is None
    assert tile3d.endpoint is None


def test_thumbnail(api, mock_tile3d_data):
    tile3d = Tile3d(api, mock_tile3d_data['uuid'], mock_tile3d_data)
    thumbnail_url = tile3d.thumbnail
    assert thumbnail_url == f"{api.base_url}{tile3d.endpoint}thumbnail.png"


def test_get_item(api, mock_tile3d_data):
    tile3d = Tile3d(api, mock_tile3d_data['uuid'], mock_tile3d_data)
    api.get.return_value = {'data': 'test'}
    item = tile3d.get_item(path='test-path')
    api.get.assert_called_once_with(f"{tile3d.endpoint}test-path")
    assert item == {'data': 'test'}


def test_share(api, mock_tile3d_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        tile3d = Tile3d(api, uuid=mock_tile3d_data['uuid'], data=mock_tile3d_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        tile3d.share(users=users)
        api.post.assert_called_once_with(
            f'{tile3d.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_tile3d_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        tile3d = Tile3d(api, uuid=mock_tile3d_data['uuid'], data=mock_tile3d_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        tile3d.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{tile3d.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_tile3d_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        tile3d = Tile3d(api, uuid=mock_tile3d_data['uuid'], data=mock_tile3d_data)
        result = tile3d.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{tile3d.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'


def test_get_tileset_json(api, mock_tile3d_data):
    mock_response = {
        'key': 'value'
    }
    with patch.object(api, 'get', return_value=mock_response):
        tile3d = Tile3d(api, uuid=mock_tile3d_data['uuid'], data=mock_tile3d_data)
        result = tile3d.get_tileset_json()
        
        assert result == mock_response

        api.get.assert_called_once_with('3dtiles/fa1e14c3-bb36-4541-a7c3-d0a7f70d8852/tileset.json')


