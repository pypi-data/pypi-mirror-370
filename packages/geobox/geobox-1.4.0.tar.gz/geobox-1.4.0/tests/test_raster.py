import pytest
from unittest.mock import MagicMock, patch
from unittest import mock
import os
import tempfile
from urllib.parse import urljoin

from geobox.raster import Raster
from geobox.user import User
from geobox.task import Task


def test_init(api, mock_raster_data):
    """Test Raster initialization."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    assert raster.uuid == mock_raster_data['uuid']
    assert raster.name == mock_raster_data['name']
    assert raster.data == mock_raster_data
    assert raster.endpoint == f"{Raster.BASE_ENDPOINT}{mock_raster_data['uuid']}/"


def test_repr(api, mock_raster_data):
    """Test Raster string representation."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    assert repr(raster) == f"Raster(uuid={raster.uuid}, name={raster.name})"


def test_getattr(api, mock_raster_data):
    """Test getting attributes of Raster object."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    assert raster.name == mock_raster_data['name']
    assert raster.display_name == mock_raster_data['display_name']
    assert raster.description == mock_raster_data['description']


def test_get_rasters(api, mock_raster_data):
    """Test getting list of rasters."""
    mock_response = [
        mock_raster_data,
        mock_raster_data
    ]
    api.get.return_value = mock_response
    
    rasters = Raster.get_rasters(api)
    assert len(rasters) == 2
    assert rasters[0].name == mock_raster_data['name']
    assert rasters[1].name == mock_raster_data['name']
    assert rasters[0].uuid == mock_raster_data['uuid']
    assert rasters[1].uuid == mock_raster_data['uuid']
    assert rasters[1].data == mock_raster_data
    api.get.assert_called_once_with(f'{Raster.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=100&shared=False')


def test_get_rasters_by_ids(api, mock_raster_data):
    mock_response = [{**mock_raster_data, **{'id': 1}}, {**mock_raster_data, **{'id': 2}}]
    api.get.return_value = mock_response
    
    mosaics = Raster.get_rasters_by_ids(api, [1, 2])
    
    api.get.assert_called_once_with(f'{Raster.BASE_ENDPOINT}get-rasters/?ids=%5B1%2C+2%5D')
    assert len(mosaics) == 2
    assert all(isinstance(m, Raster) for m in mosaics)
    assert mosaics[0].data == {**mock_raster_data, **{'id': 1}}
    assert mosaics[1].data == {**mock_raster_data, **{'id': 2}}


def test_get_raster(api, mock_raster_data):
    """Test getting a single raster."""
    api.get.return_value = mock_raster_data
    
    raster = Raster.get_raster(api, mock_raster_data['uuid'])
    assert raster.uuid == mock_raster_data['uuid']
    assert raster.name == mock_raster_data['name']
    assert raster.data == mock_raster_data
    api.get.assert_called_once_with(f'{Raster.BASE_ENDPOINT}{mock_raster_data["uuid"]}/?f=json')


def test_get_raster_by_name(api, mock_raster_data):
    """Test getting a single raster."""
    api.get.return_value = [mock_raster_data]
    
    raster = Raster.get_raster_by_name(api, name=mock_raster_data['name'])
    assert raster.uuid == mock_raster_data['uuid']
    assert raster.name == mock_raster_data['name']
    assert raster.data == mock_raster_data
    api.get.assert_called_once_with(f'{Raster.BASE_ENDPOINT}?f=json&q=name+%3D+%27sample_sample1.tif%27&return_count=False&skip=0&limit=100&shared=False')
    # not found
    raster = Raster.get_raster_by_name(api, name='not_found')
    assert raster == None


def test_update(api, mock_raster_data):
    """Test updating raster properties."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.put.return_value = {**mock_raster_data, **{'name': 'new_name', 'display_name': 'New Display Name', 'description': 'New Description'}}
    
    result = raster.update(name='new_name', display_name='New Display Name', description='New Description')
    api.put.assert_called_once_with(
        raster.endpoint,
        {'name': 'new_name', 'display_name': 'New Display Name', 'description': 'New Description'}
    )
    assert raster.name == result['name']
    assert raster.display_name == result['display_name']
    assert raster.description == result['description']


def test_delete(api, mock_raster_data):
    """Test deleting a raster."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)

    endpoint = raster.endpoint
    raster.delete()
    api.delete.assert_called_once_with(endpoint)
    assert raster.uuid is None
    assert raster.endpoint is None


def test_thumbnail(api, mock_raster_data):
    """Test getting raster thumbnail URL."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    thumbnail_url = raster.thumbnail
    assert thumbnail_url == f"{api.base_url}{raster.endpoint}thumbnail"


def test_raster_info(api, mock_raster_data):
    """Test getting raster info."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.get.return_value = mock_raster_data
    
    info = raster.info
    assert info == mock_raster_data
    api.get.assert_called_once_with(f'{raster.endpoint}info/')


def test_get_statistics(api, mock_raster_data):
    """Test getting raster statistics."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.get.return_value = {'band1': {'min': 0, 'max': 255}}
    
    stats = raster.get_statistics(indexes='1')
    assert stats == {'band1': {'min': 0, 'max': 255}}
    api.get.assert_called_once_with(f'{raster.endpoint}statistics/?indexes=1')


def test_get_point(api, mock_raster_data):
    """Test getting point data from raster."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.get.return_value = {'value': 100}
    
    point = raster.get_point(lat=35, lng=51)
    assert point == {'value': 100}
    api.get.assert_called_once_with(f'{raster.endpoint}point?lat=35&lng=51')

    # errors
    with pytest.raises(ValueError, match='lat must be between -90 and 90'):
        raster.get_point(lat=94, lng=51)

    with pytest.raises(ValueError, match='lng must be between -180 and 180'):
        raster.get_point(lat=14, lng=251)


def test_download(api, mock_raster_data):
    """Test downloading a raster."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b'test content']
    mock_response.__exit__.return_value = None
    mock_response.__enter__.return_value.headers = {
        'Content-Type': 'image/tiff',
        'Content-Disposition': 'attachment; filename="test_raster.tif"'
    }
    api.get.return_value = mock_response

    with tempfile.TemporaryDirectory() as temp_dir:
        save_path = os.path.join(temp_dir, '') + '/'
        downloaded_path = raster.download(save_path=save_path)
        assert downloaded_path.endswith('.tif')
        assert os.path.exists(downloaded_path)

    mock_raster_data['name'] = None
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b'test content']
    mock_response.__exit__.return_value = None
    mock_response.__enter__.return_value.headers = {
        'Content-Type': 'image/tiff',
        'Content-Disposition': 'attachment; filename="test_raster.tif"'
    }
    api.get.return_value = mock_response

    with tempfile.TemporaryDirectory() as temp_dir:
        downloaded_path = raster.download()
        assert downloaded_path.endswith('.tif')
        assert os.path.exists(downloaded_path)


    if os.path.exists(downloaded_path):
        os.remove(downloaded_path)

    # error
    with pytest.raises(ValueError):
        raster.download(save_path='path')

    raster.uuid = None
    with pytest.raises(ValueError):
        raster.download()

    # import warning log
    import builtins
    original_import = builtins.__import__

    def mocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tqdm.auto":
            raise ImportError("No module named 'tqdm'")
        return original_import(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=mocked_import):
        with mock.patch("geobox.api.logger") as mock_logger:
            result = raster._create_progress_bar()
            assert result is None
            mock_logger.warning.assert_called_once()


def test_get_content(api, mock_raster_data):
    """Test getting raster content."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b'test content']
    mock_response.__exit__.return_value = None
    mock_response.__enter__.return_value.headers = {
        'Content-Type': 'image/tiff'
    }
    api.get.return_value = mock_response

    with tempfile.TemporaryDirectory() as temp_dir:
        save_path = os.path.join(temp_dir, '') + '/'
        downloaded_path = raster.get_content_file(save_path=save_path)
        assert downloaded_path.endswith('.tiff')
        assert os.path.exists(downloaded_path)

    # error
    raster.uuid = None
    with pytest.raises(ValueError):
        raster.get_content_file()


def test_get_render_png_url(api, mock_raster_data):
    """Test getting tile PNG URL."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    url = raster.get_render_png_url(x=10, y=20, z=1, indexes=1)
    assert url == f"{raster.api.base_url}{raster.endpoint}render/1/10/20.png?indexes=1"
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    url = raster.get_render_png_url(x=10, y=20, z=1, indexes=1)
    assert url == f"{raster.api.base_url}{raster.endpoint}render/1/10/20.png?indexes=1&apikey=apikey_1234"
    

def test_get_tile_png_url(api, mock_raster_data):
    """Test getting tile PNG URL."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    url = raster.get_tile_png_url(x=10, y=20, z=1)
    assert url == f"{raster.api.base_url}{raster.endpoint}tiles/1/10/20.png"
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    url = raster.get_tile_png_url(x=10, y=20, z=1)
    assert url == f"{raster.api.base_url}{raster.endpoint}tiles/1/10/20.png?apikey=apikey_1234"


def test_get_tile_pbf_url(api, mock_raster_data):
    """Test getting tile URL."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    url = raster.get_tile_pbf_url(x=10, y=20, z=1)
    assert url == f"{raster.api.base_url}{raster.endpoint}tiles/1/10/20.pbf"
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    url = raster.get_tile_pbf_url(x=10, y=20, z=1)
    assert url == f"{raster.api.base_url}{raster.endpoint}tiles/1/10/20.pbf?apikey=apikey_1234"


def test_get_tile_json(api, mock_raster_data):
    """Test getting raster tile JSON."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.get.return_value = mock_raster_data
    response = raster.get_tile_json()
    assert response == mock_raster_data
    api.get.assert_called_once_with(f'{raster.endpoint}tilejson.json')


def test_wmts(api, mock_raster_data):
    """Test getting WMTS URL."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    url = raster.wmts(scale=1)
    assert url == f'{raster.api.base_url}{raster.endpoint}wmts/?scale=1'
    # apikey
    api.access_token = ''
    api.apikey = 'apikey_1234'
    url = raster.wmts(scale=1)
    assert url == f'{raster.api.base_url}{raster.endpoint}wmts/?scale=1&apikey=apikey_1234'


def test_settings(api, mock_raster_data):
    """Test getting raster settings."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.get.return_value = mock_raster_data
    settings = raster.settings
    assert settings == mock_raster_data
    api.get.assert_called_once_with(f'{raster.endpoint}settings/?f=json')


def test_set_settings(api, mock_raster_data):
    """Test setting raster settings."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.get.return_value = {
        "visual_settings": {
            "nodata": None,
            "indexes": [
            1,
            2,
            3
            ],
            "rescale": [
            [
                0,
                9848
            ],
            [
                0,
                9636
            ],
            [
                0,
                9409
            ]
            ],
            "colormap_name": None,
            "colormap": None,
            "color_formula": None,
            "expression": None,
            "exaggeration": 10
        },
        "tile_settings": {
            "min_zoom": 0,
            "max_zoom": 13,
            "use_cache": True,
            "cache_until_zoom": 17
        }
        }
    raster.set_settings(nodata=0, indexes=[1], rescale=[[0, 255]], colormap_name='viridis', color_formula='R*255', expression='R', exaggeraion=1, min_zoom=0, max_zoom=18, use_cache=True, cache_until_zoom=10)
    expected_data = {'visual_settings': 
                        {'nodata': 0, 
                            'indexes': [1], 
                            'rescale': [[0, 255]], 
                            'colormap_name': 'viridis', 
                            'colormap': None, 
                            'color_formula': 'R*255', 
                            'expression': 'R', 
                            'exaggeration': 10, 
                            'exaggeraion': 1
                        }, 
                        'tile_settings': 
                            {'min_zoom': 0, 
                                'max_zoom': 18, 
                                'use_cache': True, 
                                'cache_until_zoom': 10
                            }
                    }
    api.put.assert_called_once_with(
        f"{raster.endpoint}settings/",
        expected_data
    )


def test_share(api, mock_raster_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        raster.share(users=users)
        api.post.assert_called_once_with(
            f'{raster.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_raster_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        raster.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{raster.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_raster_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
        result = raster.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{raster.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'


def test_seed_cache(api, mock_raster_data, mock_success_task_data):
    """Test seeding cache."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.post.return_value = [{'task_id': mock_success_task_data['id']}]
    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)
    
    task = raster.seed_cache(from_zoom=0, to_zoom=10, extent=[0, 0, 100, 100], workers=2)[0]
    api.post.assert_called_once_with(f'{raster.endpoint}cache/seed/', {
        'from_zoom': 0,
        'to_zoom': 10,
        'extent': [0, 0, 100, 100],
        'workers': 2
    })
    assert isinstance(task, Task)


def test_clear_cache(api, mock_raster_data):
    """Test clearing cache."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    raster.clear_cache()
    api.post.assert_called_once_with(f"{raster.endpoint}cache/clear/")

def test_cache_size(api, mock_raster_data):
    """Test getting cache size."""
    raster = Raster(api, uuid=mock_raster_data['uuid'], data=mock_raster_data)
    api.post.return_value = 1024
    
    size = raster.cache_size
    assert size == 1024
    api.post.assert_called_once_with(f"{raster.endpoint}cache/size/") 