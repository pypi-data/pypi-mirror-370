import pytest
from unittest.mock import patch

from geobox.layout import Layout
from geobox.user import User

def test_init(api, mock_layout_data):
    layout = Layout(api, mock_layout_data['uuid'], mock_layout_data)
    assert layout.name == mock_layout_data['name']
    assert layout.uuid == mock_layout_data['uuid']
    assert layout.data == mock_layout_data
    assert layout.endpoint == f'{Layout.BASE_ENDPOINT}{layout.uuid}/'


def test_get_layouts(api, mock_layout_data):
    api.get.return_value = [mock_layout_data, mock_layout_data]
    layouts = Layout.get_layouts(api)
    api.get.assert_called_once_with(f'{Layout.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')
    assert len(layouts) == 2
    assert type(layouts[0]) == Layout
    assert layouts[0].data == mock_layout_data


def test_create_layout(api, mock_layout_data):
    api.post.return_value = mock_layout_data
    layout = Layout.create_layout(api,
                                        name=mock_layout_data['name'],
                                        display_name=mock_layout_data['display_name'],
                                        description=mock_layout_data['description'],
                                        settings=mock_layout_data['settings'],
                                        thumbnail=mock_layout_data.get('thumbnail'))
    api.post.assert_called_once_with(Layout.BASE_ENDPOINT, {'name': 'test', 'settings': {}})
    assert type(layout) == Layout
    assert layout.uuid == mock_layout_data['uuid']
    assert layout.data == mock_layout_data


def test_get_layout(api, mock_layout_data):
    api.get.return_value = mock_layout_data
    layout = Layout.get_layout(api, uuid=mock_layout_data['uuid'])
    api.get.assert_called_once_with(f"{Layout.BASE_ENDPOINT}{mock_layout_data['uuid']}/?f=json")
    assert type(layout) == Layout
    assert layout.uuid == mock_layout_data['uuid']
    assert layout.data == mock_layout_data


def test_get_layout_by_name(api, mock_layout_data):
    api.get.return_value = [mock_layout_data]
    layout = Layout.get_layout_by_name(api, name=mock_layout_data['name'])
    api.get.assert_called_once_with(f"{Layout.BASE_ENDPOINT}?f=json&q=name+%3D+%27test%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(layout) == Layout
    assert layout.uuid == mock_layout_data['uuid']
    assert layout.data == mock_layout_data
    # not found
    layout = Layout.get_layout_by_name(api, name='not_found')
    assert layout == None


def test_update(api, mock_layout_data):
    layout = Layout(api, mock_layout_data['uuid'], mock_layout_data)
    updated_data = {**mock_layout_data,
                    'settings': {'settings': 'value'},
                    'thumbnail': 'thumbnail-url'}

    api.put.return_value = updated_data
    layout.update(settings={'settings': 'value'}, thumbnail='thumbnail-url')
    api.put.assert_called_once_with(layout.endpoint, {'settings': {'settings': 'value'}, 'thumbnail': 'thumbnail-url'})


def test_delete(api, mock_layout_data):
    layout = Layout(api, mock_layout_data['uuid'], mock_layout_data)
    endpoint = layout.endpoint
    layout.delete()
    api.delete.assert_called_once_with(endpoint)
    assert layout.uuid is None
    assert layout.endpoint is None


def test_thumbnail(api, mock_layout_data):
    layout = Layout(api, mock_layout_data['uuid'], mock_layout_data)
    thumbnail_url = layout.thumbnail
    assert thumbnail_url == f"{api.base_url}{layout.endpoint}thumbnail.png"


def test_share(api, mock_layout_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        layout = Layout(api, uuid=mock_layout_data['uuid'], data=mock_layout_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        layout.share(users=users)
        api.post.assert_called_once_with(
            f'{layout.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_layout_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        layout = Layout(api, uuid=mock_layout_data['uuid'], data=mock_layout_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        layout.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{layout.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_layout_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        layout = Layout(api, uuid=mock_layout_data['uuid'], data=mock_layout_data)
        result = layout.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{layout.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
