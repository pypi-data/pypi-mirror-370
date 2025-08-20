import pytest
from unittest.mock import patch

from geobox.dashboard import Dashboard
from geobox.user import User
from geobox.utils import clean_data

def test_init(api, mock_dashboard_data):
    dashboard = Dashboard(api, mock_dashboard_data['uuid'], mock_dashboard_data)
    assert dashboard.name == mock_dashboard_data['name']
    assert dashboard.uuid == mock_dashboard_data['uuid']
    assert dashboard.data == mock_dashboard_data
    assert dashboard.endpoint == f'{Dashboard.BASE_ENDPOINT}{dashboard.uuid}/'


def test_get_dashboards(api, mock_dashboard_data):
    api.get.return_value = [mock_dashboard_data, mock_dashboard_data]
    dashboards = Dashboard.get_dashboards(api)
    api.get.assert_called_once_with(f'{Dashboard.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')
    assert len(dashboards) == 2
    assert type(dashboards[0]) == Dashboard
    assert dashboards[0].data == mock_dashboard_data


def test_create_dashboard(api, mock_dashboard_data):
    api.post.return_value = mock_dashboard_data
    dashboard = Dashboard.create_dashboard(api,
                                        name=mock_dashboard_data['name'],
                                        display_name=mock_dashboard_data['display_name'],
                                        description=mock_dashboard_data['description'],
                                        settings=mock_dashboard_data['settings'],
                                        thumbnail=mock_dashboard_data.get('thumbnail'))
    expected_data = clean_data({'name': mock_dashboard_data['name'], 
                        'display_name': mock_dashboard_data['display_name'], 
                        'description': mock_dashboard_data['description'], 
                        'settings': mock_dashboard_data['settings'], 
                        'thumbnail': mock_dashboard_data.get('thumbnail')})

    api.post.assert_called_once_with(Dashboard.BASE_ENDPOINT, expected_data)
    assert type(dashboard) == Dashboard
    assert dashboard.uuid == mock_dashboard_data['uuid']
    assert dashboard.data == mock_dashboard_data


def test_get_dashboard(api, mock_dashboard_data):
    api.get.return_value = mock_dashboard_data
    dashboard = Dashboard.get_dashboard(api, uuid=mock_dashboard_data['uuid'])
    api.get.assert_called_once_with(f"{Dashboard.BASE_ENDPOINT}{mock_dashboard_data['uuid']}/?f=json")
    assert type(dashboard) == Dashboard
    assert dashboard.uuid == mock_dashboard_data['uuid']
    assert dashboard.data == mock_dashboard_data


def test_get_dashboard_by_name(api, mock_dashboard_data):
    api.get.return_value = [mock_dashboard_data]
    dashboard = Dashboard.get_dashboard_by_name(api, name=mock_dashboard_data['name'])
    api.get.assert_called_once_with(f"{Dashboard.BASE_ENDPOINT}?f=json&q=name+%3D+%27test%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(dashboard) == Dashboard
    assert dashboard.uuid == mock_dashboard_data['uuid']
    assert dashboard.data == mock_dashboard_data
    # not found
    dashboard = Dashboard.get_dashboard_by_name(api, name='not_found')
    assert dashboard == None


def test_update(api, mock_dashboard_data):
    dashboard = Dashboard(api, mock_dashboard_data['uuid'], mock_dashboard_data)
    updated_data = {**mock_dashboard_data,
                    'settings': {'settings': 'value'},
                    'thumbnail': 'thumbnail-url'}

    api.put.return_value = updated_data
    dashboard.update(settings={'settings': 'value'}, thumbnail='thumbnail-url')
    api.put.assert_called_once_with(dashboard.endpoint, {'settings': {'settings': 'value'}, 'thumbnail': 'thumbnail-url'})


def test_delete(api, mock_dashboard_data):
    dashboard = Dashboard(api, mock_dashboard_data['uuid'], mock_dashboard_data)
    endpoint = dashboard.endpoint
    dashboard.delete()
    api.delete.assert_called_once_with(endpoint)
    assert dashboard.uuid is None
    assert dashboard.endpoint is None


def test_thumbnail(api, mock_dashboard_data):
    dashboard = Dashboard(api, mock_dashboard_data['uuid'], mock_dashboard_data)
    thumbnail_url = dashboard.thumbnail
    assert thumbnail_url == f"{api.base_url}{dashboard.endpoint}thumbnail.png"


def test_share(api, mock_dashboard_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        dashboard = Dashboard(api, uuid=mock_dashboard_data['uuid'], data=mock_dashboard_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        dashboard.share(users=users)
        api.post.assert_called_once_with(
            f'{dashboard.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_dashboard_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        dashboard = Dashboard(api, uuid=mock_dashboard_data['uuid'], data=mock_dashboard_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        dashboard.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{dashboard.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_dashboard_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        dashboard = Dashboard(api, uuid=mock_dashboard_data['uuid'], data=mock_dashboard_data)
        result = dashboard.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{dashboard.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
