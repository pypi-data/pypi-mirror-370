import pytest
from unittest.mock import patch

from geobox.basemap import Basemap
from geobox.user import User
from geobox.exception import NotFoundError


def test_init(api, mock_basemap_data):
    basemap = Basemap(api, mock_basemap_data)
    assert basemap.name == mock_basemap_data['name']
    assert basemap.data == mock_basemap_data
    assert basemap.endpoint == f'{Basemap.BASE_ENDPOINT}{basemap.name}/'


def test_get_basemaps(api, mock_basemap_data, mock_basemap_list_data):
    api.get.return_value = mock_basemap_list_data
    basemaps = Basemap.get_basemaps(api)
    api.get.assert_called_once_with(f'{Basemap.BASE_ENDPOINT}')
    assert len(basemaps) == 2
    assert type(basemaps[0]) == Basemap
    assert basemaps[0].data == mock_basemap_data
    # empty list
    api.reset_mock()
    api.get.return_value = []
    basemaps = Basemap.get_basemaps(api)
    api.get.assert_called_once_with(f'{Basemap.BASE_ENDPOINT}')
    assert len(basemaps) == 0


def test_get_basemap(api, mock_basemap_data, mock_basemap_list_data):
    api.get.return_value = mock_basemap_list_data
    basemap = Basemap.get_basemap(api, name=mock_basemap_data['name'])
    api.get.assert_called_once_with(f"{Basemap.BASE_ENDPOINT}")
    assert type(basemap) == Basemap
    assert basemap.data == mock_basemap_data
    #error
    with pytest.raises(NotFoundError):
        basemap = Basemap.get_basemap(api, name='invalid_name')


def test_thumbnail(api, mock_basemap_data):
    basemap = Basemap(api, mock_basemap_data)
    thumbnail_url = basemap.thumbnail
    assert thumbnail_url == f"{api.base_url}{basemap.endpoint}/thumbnail.png"


def test_wmts(api, mock_basemap_data):
    basemap = Basemap(api, mock_basemap_data)
    wmts_url = basemap.wmts
    assert wmts_url == f"{api.base_url}{basemap.endpoint}wmts/"
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    wmts_url = basemap.wmts
    assert wmts_url == f"{api.base_url}{basemap.endpoint}wmts/?apikey=apikey_1234"


def test_server_url(api, mock_basemap_data):
    basemap = Basemap(api, mock_basemap_data)
    api.get.return_value = 'test-url'
    server_url = basemap.server_url
    api.get.assert_called_once_with('https://example.com/basemaps/server_url')
    assert server_url == 'test-url'


def test_proxy_url(api, mock_basemap_data):
    basemap = Basemap(api, mock_basemap_data)
    api.get.return_value = 'test-url'
    proxy_url = basemap.proxy_url
    api.get.assert_called_once_with('https://example.com/basemaps/proxy_url')
    assert proxy_url == 'test-url'

def test_proxy_basemap(api, mock_basemap_data):
    basemap = Basemap(api, mock_basemap_data)
    basemap.proxy_basemap(api, url='test-url')
    api.get.assert_called_once_with('basemaps/?url=test-url')