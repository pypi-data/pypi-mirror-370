import pytest
from unittest.mock import patch

from geobox.version import VectorLayerVersion
from geobox.user import User

def test_init(api, mock_version_data):
    version = VectorLayerVersion(api, mock_version_data['uuid'], mock_version_data)
    assert version.name == mock_version_data['name']
    assert version.uuid == mock_version_data['uuid']
    assert version.data == mock_version_data
    assert version.endpoint == f'{VectorLayerVersion.BASE_ENDPOINT}{version.uuid}/'


def test_get_versions(api, mock_version_data):
    api.get.return_value = [mock_version_data, mock_version_data]
    versions = VectorLayerVersion.get_versions(api)
    api.get.assert_called_once_with(f'{VectorLayerVersion.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')
    assert len(versions) == 2
    assert type(versions[0]) == VectorLayerVersion
    assert versions[0].data == mock_version_data


def test_get_version(api, mock_version_data):
    api.get.return_value = mock_version_data
    version = VectorLayerVersion.get_version(api, uuid=mock_version_data['uuid'])
    api.get.assert_called_once_with(f"{VectorLayerVersion.BASE_ENDPOINT}{mock_version_data['uuid']}/?f=json")
    assert type(version) == VectorLayerVersion
    assert version.uuid == mock_version_data['uuid']
    assert version.data == mock_version_data


def test_get_version_by_name(api, mock_version_data):
    api.get.return_value = [mock_version_data]
    version = VectorLayerVersion.get_version_by_name(api, name=mock_version_data['name'])
    api.get.assert_called_once_with(f"{VectorLayerVersion.BASE_ENDPOINT}?f=json&q=name+%3D+%27design_version%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(version) == VectorLayerVersion
    assert version.uuid == mock_version_data['uuid']
    assert version.data == mock_version_data
    # not found
    version = VectorLayerVersion.get_version_by_name(api, name='not_found')
    assert version == None


def test_update(api, mock_version_data):
    version = VectorLayerVersion(api, mock_version_data['uuid'], mock_version_data)
    updated_data = {**mock_version_data,
                    'settings': {'settings': 'value'},
                    'thumbnail': 'thumbnail-url'}

    api.put.return_value = updated_data
    version.update(display_name='new display name', description='new description')
    api.put.assert_called_once_with(version.endpoint, {'display_name': 'new display name', 'description': 'new description'})


def test_delete(api, mock_version_data):
    version = VectorLayerVersion(api, mock_version_data['uuid'], mock_version_data)
    endpoint = version.endpoint
    version.delete()
    api.delete.assert_called_once_with(endpoint)
    assert version.uuid is None
    assert version.endpoint is None


def test_share(api, mock_version_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        version = VectorLayerVersion(api, uuid=mock_version_data['uuid'], data=mock_version_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        version.share(users=users)
        api.post.assert_called_once_with(
            f'{version.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_version_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        version = VectorLayerVersion(api, uuid=mock_version_data['uuid'], data=mock_version_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        version.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{version.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_version_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        version = VectorLayerVersion(api, uuid=mock_version_data['uuid'], data=mock_version_data)
        result = version.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{version.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
