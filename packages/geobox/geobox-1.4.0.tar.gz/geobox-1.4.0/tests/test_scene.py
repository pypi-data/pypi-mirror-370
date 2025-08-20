import pytest
from unittest.mock import patch

from geobox.scene import Scene
from geobox.user import User

def test_init(api, mock_scene_data):
    scene = Scene(api, mock_scene_data['uuid'], mock_scene_data)
    assert scene.name == mock_scene_data['name']
    assert scene.uuid == mock_scene_data['uuid']
    assert scene.data == mock_scene_data
    assert scene.endpoint == f'{Scene.BASE_ENDPOINT}{scene.uuid}/'


def test_get_scenes(api, mock_scene_data):
    api.get.return_value = [mock_scene_data, mock_scene_data]
    workflows = Scene.get_scenes(api)
    api.get.assert_called_once_with(f'{Scene.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')
    assert len(workflows) == 2
    assert type(workflows[0]) == Scene
    assert workflows[0].data == mock_scene_data


def test_create_scene(api, mock_scene_data):
    api.post.return_value = mock_scene_data
    scene = Scene.create_scene(api,
                                name=mock_scene_data['name'],
                                display_name=mock_scene_data['display_name'],
                                description=mock_scene_data['description'],
                                settings=mock_scene_data['settings'],
                                thumbnail=mock_scene_data.get('thumbnail'))
    api.post.assert_called_once_with(Scene.BASE_ENDPOINT, {'name': 'test'})
    assert type(scene) == Scene
    assert scene.uuid == mock_scene_data['uuid']
    assert scene.data == mock_scene_data


def test_get_scene(api, mock_scene_data):
    api.get.return_value = mock_scene_data
    scene = Scene.get_scene(api, uuid=mock_scene_data['uuid'])
    api.get.assert_called_once_with(f"{Scene.BASE_ENDPOINT}{mock_scene_data['uuid']}/?f=json")
    assert type(scene) == Scene
    assert scene.uuid == mock_scene_data['uuid']
    assert scene.data == mock_scene_data


def test_get_scene_by_name(api, mock_scene_data):
    api.get.return_value = [mock_scene_data]
    scene = Scene.get_scene_by_name(api, name=mock_scene_data['name'])
    api.get.assert_called_once_with(f"{Scene.BASE_ENDPOINT}?f=json&q=name+%3D+%27test%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(scene) == Scene
    assert scene.uuid == mock_scene_data['uuid']
    assert scene.data == mock_scene_data
    # not found
    scene = Scene.get_scene_by_name(api, name='not_found')
    assert scene == None


def test_update(api, mock_scene_data):
    scene = Scene(api, mock_scene_data['uuid'], mock_scene_data)
    updated_data = {**mock_scene_data,
                    'settings': {'settings': 'value'},
                    'thumbnail': 'thumbnail-url'}

    api.put.return_value = updated_data
    scene.update(settings={'settings': 'value'}, thumbnail='thumbnail-url')
    api.put.assert_called_once_with(scene.endpoint, {'settings': {'settings': 'value'}, 'thumbnail': 'thumbnail-url'})


def test_delete(api, mock_scene_data):
    scene = Scene(api, mock_scene_data['uuid'], mock_scene_data)
    endpoint = scene.endpoint
    scene.delete()
    api.delete.assert_called_once_with(endpoint)
    assert scene.uuid is None
    assert scene.endpoint is None


def test_thumbnail(api, mock_scene_data):
    scene = Scene(api, mock_scene_data['uuid'], mock_scene_data)
    thumbnail_url = scene.thumbnail
    assert thumbnail_url == f"{api.base_url}{scene.endpoint}thumbnail.png"


def test_share(api, mock_scene_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        scene = Scene(api, uuid=mock_scene_data['uuid'], data=mock_scene_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        scene.share(users=users)
        api.post.assert_called_once_with(
            f'{scene.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_scene_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        scene = Scene(api, uuid=mock_scene_data['uuid'], data=mock_scene_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        scene.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{scene.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_scene_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        scene = Scene(api, uuid=mock_scene_data['uuid'], data=mock_scene_data)
        result = scene.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{scene.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
