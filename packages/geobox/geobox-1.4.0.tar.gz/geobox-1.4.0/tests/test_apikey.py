import pytest
from unittest.mock import patch

from geobox.apikey import ApiKey


def test_init(api, mock_apikey_data):
    apikey = ApiKey(api, mock_apikey_data['id'], mock_apikey_data)
    assert apikey.name == mock_apikey_data['name']
    assert apikey.key_id == mock_apikey_data['id']
    assert apikey.data == mock_apikey_data
    assert apikey.endpoint == f'{ApiKey.BASE_ENDPOINT}{apikey.key_id}'


def test_repr(api, mock_apikey_data):
    apikey = ApiKey(api, mock_apikey_data['id'], mock_apikey_data)
    assert repr(apikey) == f'ApiKey(id={apikey.id}, name={apikey.name}, revoked={apikey.revoked})'


def test_get_apikeys(api, mock_apikey_data):
    api.get.return_value = [mock_apikey_data, mock_apikey_data]
    apikeys = ApiKey.get_apikeys(api)
    api.get.assert_called_once_with(f'{ApiKey.BASE_ENDPOINT}')
    assert len(apikeys) == 2
    assert type(apikeys[0]) == ApiKey
    assert apikeys[0].data == mock_apikey_data


def test_create_apikey(api, mock_apikey_data):
    api.post.return_value = mock_apikey_data
    apikey = ApiKey.create_apikey(api, name=mock_apikey_data['name'])
    api.post.assert_called_once_with(ApiKey.BASE_ENDPOINT, payload={'name': mock_apikey_data['name']}, is_json=False)
    assert type(apikey) == ApiKey
    assert apikey.key_id == mock_apikey_data['id']
    assert apikey.data == mock_apikey_data


def test_get_apikey(api, mock_apikey_data):
    api.get.return_value = mock_apikey_data
    apikey = ApiKey.get_apikey(api, key_id=mock_apikey_data['id'])
    api.get.assert_called_once_with(f"{ApiKey.BASE_ENDPOINT}{mock_apikey_data['id']}/?f=json")
    assert type(apikey) == ApiKey
    assert apikey.key_id == mock_apikey_data['id']
    assert apikey.data == mock_apikey_data


def test_get_apikey_by_name(api, mock_apikey_data):
    api.get.return_value = [mock_apikey_data]
    apikey = ApiKey.get_apikey_by_name(api, name=mock_apikey_data['name'])
    api.get.assert_called_once_with(f"{ApiKey.BASE_ENDPOINT}?search=test")
    assert type(apikey) == ApiKey
    assert apikey.key_id == mock_apikey_data['id']
    assert apikey.data == mock_apikey_data
    # not found
    apikey = ApiKey.get_apikey_by_name(api, name='invalid_name')
    assert apikey == None


def test_update(api, mock_apikey_data):
    apikey = ApiKey(api, mock_apikey_data['id'], mock_apikey_data)
    updated_data = {**mock_apikey_data,
                    'name': 'updated_name'}

    api.put.return_value = updated_data
    apikey.update(name='updated_name')
    api.put.assert_called_once_with(apikey.endpoint, {'name': 'updated_name'}, is_json=False)


def test_delete(api, mock_apikey_data):
    apikey = ApiKey(api, mock_apikey_data['id'], mock_apikey_data)
    endpoint = apikey.endpoint
    apikey.delete()
    api.delete.assert_called_once_with(endpoint)
    assert apikey.key_id is None
    assert apikey.endpoint is None


def test_revoke(api, mock_apikey_data):
    apikey = ApiKey(api, mock_apikey_data['id'], mock_apikey_data)
    apikey.revoke()
    api.post.assert_called_once_with(f'{apikey.endpoint}/revoke')
    assert apikey.revoked == True


def test_grant(api, mock_apikey_data):
    apikey = ApiKey(api, mock_apikey_data['id'], mock_apikey_data)
    apikey.grant()
    api.post.assert_called_once_with(f'{apikey.endpoint}/grant')
    assert apikey.revoked == False