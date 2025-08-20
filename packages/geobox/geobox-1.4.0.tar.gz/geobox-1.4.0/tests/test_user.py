import pytest
from unittest.mock import patch, ANY
from urllib.parse import urljoin, urlencode

from geobox.user import User
from geobox.enums import UserRole, UserStatus
from geobox.plan import Plan
from geobox.utils import xor_encode


def test_init(api, mock_user_data):
    user = User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1'])
    assert user.data == mock_user_data['1']
    assert user.endpoint == f"users/{mock_user_data['1']['id']}/"
    assert user.api == api


def test_repr(api, mock_user_data):
    user = User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1'])
    assert repr(user) == f"User(id={user.id}, first_name=test 1, last_name=test 1)"


def test_role(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    assert user.role == UserRole.ACCOUNT_ADMIN


def test_status(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    assert user.status == UserStatus.DISABLED


def test_plan(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    assert type(user.plan) == Plan

def test_get_users(api, mock_admin_user_data):
    api.get.return_value = [mock_admin_user_data, mock_admin_user_data]
    result = User.get_users(api, search='test')
    assert isinstance(result, list)
    assert isinstance(result[0], User)
    api.get.assert_called_once_with('users/?f=json&search=test&return_count=False&skip=0&limit=10')

def test_create_user(api, mock_admin_user_data):
    api.post.return_value = mock_admin_user_data
    user = User.create_user(
        api,
        username=mock_admin_user_data['username'],
        email=mock_admin_user_data['email'],
        password='password',
        role=UserRole.ACCOUNT_ADMIN,
        first_name=mock_admin_user_data['first_name'],
        last_name=mock_admin_user_data['last_name'],
        mobile=mock_admin_user_data['mobile'],
        status=UserStatus.ACTIVE
    )
    assert isinstance(user, User)
    expected_data = {
        "username": mock_admin_user_data['username'],
        "email": mock_admin_user_data['email'],
        "password": xor_encode('password'),
        "role": UserRole.ACCOUNT_ADMIN.value,
        "first_name": mock_admin_user_data['first_name'],
        "last_name": mock_admin_user_data['last_name'],
        "status": UserStatus.ACTIVE.value
    }
    api.post.assert_called_once_with(User.BASE_ENDPOINT, expected_data)


def test_search_users(api, mock_user_data):
    api.get.return_value = [mock_user_data['1'], mock_user_data['1']]
    result = User.search_users(api, search='Test', skip=1, limit=5)
    assert isinstance(result, list)
    assert isinstance(result[0], User)
    api.get.assert_called_once_with(f"{User.BASE_ENDPOINT}search/?search=Test&skip=1&limit=5")


def test_get_user(api, mock_admin_user_data):
    api.get.return_value = mock_admin_user_data
    user = User.get_user(api, user_id=mock_admin_user_data['id'])
    assert isinstance(user, User)
    expected_params = {'f': 'json'}
    api.get.assert_called_once_with(f"{User.BASE_ENDPOINT}{mock_admin_user_data['id']}/?f=json")


def test_update(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    updated = mock_admin_user_data.copy()
    updated['status'] = UserStatus.PENDING.value
    api.put.return_value = updated
    result = user.update(status=UserStatus.PENDING)
    api.put.assert_called_once_with(f"{user.endpoint}", {'status': 'Pending'})
    assert result['status'] == UserStatus.PENDING.value


def test_delete(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    endpoint = user.endpoint
    user.delete()
    api.delete.assert_called_once_with(endpoint)
    assert user.uuid is None
    assert user.endpoint is None


def test_get_sessions(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    with patch.object(api, 'get', return_value=[{'uuid': 'sess-1', 'id': 1}, {'uuid': 'sess-2', 'id': 2}]):
        sessions = user.get_sessions()
        assert len(sessions) == 2
        assert sessions[0].uuid == 'sess-1'
        assert sessions[1].uuid == 'sess-2'
        expected_endpoint = urljoin(user.endpoint, 'sessions/?f=json')
        api.get.assert_called_once_with(expected_endpoint) 

    with patch.object(api, 'get', return_value=[{'uuid': 'sess-1', 'id': 1}, {'uuid': 'sess-2', 'id': 2}]) as mock_api,\
         patch.object(User, 'get_user', return_value=User(api, mock_admin_user_data['id'], mock_admin_user_data)) as mock_get_user:
        sessions = user.get_sessions(user_id=1)
        assert len(sessions) == 2
        assert sessions[0].uuid == 'sess-1'
        assert sessions[1].uuid == 'sess-2'
        expected_endpoint = f"{user.BASE_ENDPOINT}1/sessions/?f=json"
        api.get.assert_called_once_with(expected_endpoint) 


def test_change_password(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    with patch.object(api, 'post', return_value={"message": "success"}):
        user.change_password('new_password')
        expected_endpoint = urljoin(user.endpoint, 'change-password')
        api.post.assert_called_once_with(expected_endpoint, {'new_password': xor_encode('new_password')}, is_json=False)


def test_renew_plan(api, mock_admin_user_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    with patch.object(api, 'post'):
        user.renew_plan()
        expected_endpoint = urljoin(user.endpoint, 'renewPlan')
        api.post.assert_called_once_with(expected_endpoint)


def test_session_repr(api, mock_admin_user_data, mock_session_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    api.get.return_value = [mock_session_data, mock_session_data]
    sessions = user.get_sessions()
    assert repr(sessions[0]) == f"Session(user={user}, agent='{sessions[0].agent}')"


def test_close_seesion(api, mock_admin_user_data, mock_session_data):
    user = User(api, user_id=mock_admin_user_data['id'], data=mock_admin_user_data)
    api.get.return_value = [mock_session_data, mock_session_data]
    sessions = user.get_sessions()
    api.reset_mock()
    sessions[0].close()
    api.post.assert_called_once_with('users/165/sessions/3857eb38-69d8-4b3c-8f60-29bac352a8d9', {'user_id': 165, 'session_uuid': '3857eb38-69d8-4b3c-8f60-29bac352a8d9'})
