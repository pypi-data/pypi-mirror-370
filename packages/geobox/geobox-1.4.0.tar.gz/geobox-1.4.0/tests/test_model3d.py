import pytest
from unittest.mock import patch, MagicMock

from geobox.model3d import Model
from geobox.user import User
from geobox.exception import ApiRequestError


def test_init(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert model.uuid == mock_model_data['uuid']
    assert model.data == mock_model_data
    assert model.endpoint == f'3dmodels/{mock_model_data["uuid"]}/'


def test_model_repr(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert repr(model) == f"Model(uuid={model.uuid}, name={model.name})"


def test_model_getattr(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert model.name == mock_model_data['name']
    assert model.description == mock_model_data['description']
    
    with pytest.raises(AttributeError):
        _ = model.nonexistent_attribute


@patch('geobox.model3d.urljoin')
@patch('geobox.model3d.urlencode')
def test_get_models(mock_urlencode, mock_urljoin, api, mock_model_data):
    mock_response = [
        mock_model_data,
        mock_model_data
    ]
    api.get.return_value = mock_response
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = 'https://api.geobox.ir/v1/3dmodels/?f=json'

    models = Model.get_models(api)
    assert len(models) == 2
    assert models[0].name == mock_model_data['name']
    assert models[0].data == mock_model_data
    assert models[1].name == mock_model_data['name']

    api.get.assert_called_once_with(f"{Model.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False")

    # Test getting models with custom parameters
    api.reset_mock()
    api.get.return_value = {'count': 2}
    count = Model.get_models(
        api,
        q="name like 'test'",
        search="test",
        search_fields="name,description",
        order_by="name A",
        return_count=True,
        skip=0,
        limit=10,
        user_id=1,
        shared=False
    )
    assert count == 2
    api.get.assert_called_once_with(f"{Model.BASE_ENDPOINT}?f=json&q=name+like+%27test%27&search=test&search_fields=name%2Cdescription&order_by=name+A&return_count=True&skip=0&limit=10&user_id=1&shared=False")


@patch('geobox.model3d.urljoin')
@patch('geobox.model3d.urlencode')
def test_get_model(mock_urlencode, mock_urljoin, api, mock_model_data):
    api.get.return_value = mock_model_data
    mock_urlencode.return_value = 'f=json'

    mock_urljoin.return_value = f"3dmodels/{mock_model_data['uuid']}/?f=json"
    model = Model.get_model(api, mock_model_data['uuid'])
    assert model.uuid == mock_model_data['uuid']
    assert model.data == mock_model_data
    api.get.assert_called_once_with(f"3dmodels/{mock_model_data['uuid']}/?f=json")


@patch('geobox.model3d.urljoin')
@patch('geobox.model3d.urlencode')
def test_get_model_by_name(mock_urlencode, mock_urljoin, api, mock_model_data):
    api.get.return_value = [mock_model_data]
    mock_urlencode.return_value = 'f=json'

    mock_urljoin.return_value = f"{Model.BASE_ENDPOINT}?f=json"
    model = Model.get_model_by_name(api, name=mock_model_data['name'])
    assert model.uuid == mock_model_data['uuid']
    assert model.data == mock_model_data
    api.get.assert_called_once_with(f"{Model.BASE_ENDPOINT}?f=json&q=name+%3D+%27Treemodel%27&return_count=False&skip=0&limit=10&shared=False")
    # not found
    model = Model.get_model_by_name(api, name='not_found')
    assert model == None


def test_update(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    updated_data = {
        'name': 'Updated Name',
        'description': 'Updated Description',
        'settings': {
            'model_settings': {
                'scale': 2.0,
                'rotation': [45, 0, 0],
                'location': [1, 1, 1]
            }
        },
        'thumbnail': 'https://example.com/new-thumbnail.jpg'
    }
    api.put.return_value = updated_data

    response = model.update(
        name='Updated Name',
        description='Updated Description',
        settings=updated_data['settings'],
        thumbnail='https://example.com/new-thumbnail.jpg'
    )
    assert response == updated_data
    assert model.name == 'Updated Name'
    assert model.description == 'Updated Description'
    api.put.assert_called_once_with(model.endpoint, updated_data)


def test_delete(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    endpoint = model.endpoint
    model.delete()
    assert model.uuid is None
    assert model.endpoint is None
    api.delete.assert_called_once_with(endpoint)


def test_get_content(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'test content'
    
    api.session = MagicMock()
    api.session.get.return_value = mock_response
    
    content = model.get_content()
    
    api.session.get.assert_called_once_with(f"{model.api.base_url}{model.endpoint}content/")
    
    assert content == b'test content'

    mock_response.status_code = 404
    with pytest.raises(ApiRequestError):
        content = model.get_content()
        

def test_thumbnail(api, mock_model_data):
    model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
    assert model.thumbnail == f"{api.base_url}{model.endpoint}thumbnail.png"


def test_share(api, mock_model_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        model.share(users=users)
        api.post.assert_called_once_with(
            f'{model.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )

def test_unshare(api, mock_model_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        model.unshare(users=users)
        api.post.assert_called_once_with(
            f'{model.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )

def test_get_shared_users(api, mock_model_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        model = Model(api, uuid=mock_model_data['uuid'], data=mock_model_data)
        result = model.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{model.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
