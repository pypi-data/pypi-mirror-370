from unittest.mock import patch

from geobox.mosaic import Mosaic
from geobox.raster import Raster
from geobox.task import Task
from geobox.user import User
from geobox.utils import clean_data


def test_init(api, mock_mosaic_data):
    """Test the initialization of a Mosaic object."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    assert mosaic.uuid == mock_mosaic_data['uuid']
    assert mosaic.name == mock_mosaic_data['name']
    assert mosaic.data == mock_mosaic_data


def test_get_mosaics(api, mock_mosaic_data):
    """Test the get_mosaics method."""
    mock_response = [mock_mosaic_data, mock_mosaic_data]
    api.get.return_value = mock_response
    
    mosaics = Mosaic.get_mosaics(api)
    
    api.get.assert_called_once_with('mosaics/?f=json&return_count=False&skip=0&limit=100&shared=False')
    assert len(mosaics) == 2
    assert all(isinstance(m, Mosaic) for m in mosaics)
    assert mosaics[0].name == mock_mosaic_data['name']
    assert mosaics[1].data == mock_mosaic_data
    assert mosaics[0].uuid == mock_mosaic_data['uuid']


def test_get_mosaic(api, mock_mosaic_data):
    """Test the get_mosaic method."""
    api.get.return_value = mock_mosaic_data
    
    mosaic = Mosaic.get_mosaic(api, mock_mosaic_data['uuid'])
    
    api.get.assert_called_once_with(f'mosaics/{mock_mosaic_data["uuid"]}/?f=json')
    assert isinstance(mosaic, Mosaic)
    assert mosaic.uuid == mock_mosaic_data['uuid']
    assert mosaic.name == mock_mosaic_data['name']


def test_get_mosaic_by_name(api, mock_mosaic_data):
    """Test the get_mosaic method."""
    api.get.return_value = [mock_mosaic_data]
    
    mosaic = Mosaic.get_mosaic_by_name(api, name=mock_mosaic_data['name'])
    
    api.get.assert_called_once_with(f'{Mosaic.BASE_ENDPOINT}?f=json&q=name+%3D+%27string%27&return_count=False&skip=0&limit=100&shared=False')
    assert isinstance(mosaic, Mosaic)
    assert mosaic.uuid == mock_mosaic_data['uuid']
    assert mosaic.name == mock_mosaic_data['name']
    # not found
    mosaic = Mosaic.get_mosaic_by_name(api, name='not_found')
    assert mosaic == None


def test_create_mosaic(api, mock_mosaic_data):
    """Test the create_mosaic method."""
    api.post.return_value = mock_mosaic_data
    
    mosaic = Mosaic.create_mosaic(
        api,
        name=mock_mosaic_data['name'],
        display_name=mock_mosaic_data['display_name'],
        description=mock_mosaic_data['description'],
        pixel_selection=mock_mosaic_data['pixel_selection'],
        min_zoom=mock_mosaic_data['min_zoom']
    )
    
    api.post.assert_called_once_with('mosaics/', {
        'name': mock_mosaic_data['name'],
        'display_name': mock_mosaic_data['display_name'],
        'description': mock_mosaic_data['description'],
        'pixel_selection': mock_mosaic_data['pixel_selection'],
        'min_zoom': mock_mosaic_data['min_zoom']
    })
    assert isinstance(mosaic, Mosaic)
    assert mosaic.uuid == mock_mosaic_data['uuid']
    assert mosaic.name == mock_mosaic_data['name']


def test_get_mosaics_by_ids(api, mock_mosaic_data):
    """Test the get_mosaics_by_ids method."""
    mock_response = [{**mock_mosaic_data, **{'id': 1}}, {**mock_mosaic_data, **{'id': 2}}]
    api.get.return_value = mock_response
    
    mosaics = Mosaic.get_mosaics_by_ids(api, [1, 2])
    
    api.get.assert_called_once_with('mosaics/get-mosaics/?ids=%5B1%2C+2%5D')
    assert len(mosaics) == 2
    assert all(isinstance(m, Mosaic) for m in mosaics)
    assert mosaics[0].data == {**mock_mosaic_data, **{'id': 1}}
    assert mosaics[1].data == {**mock_mosaic_data, **{'id': 2}}


def test_update(api, mock_mosaic_data):
    """Test the update_mosaic method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    updated_data = {**mock_mosaic_data, 'name': 'updated_name'}
    api.put.return_value = updated_data
    
    mosaic.update(name='updated_name')
    
    api.put.assert_called_once_with(f'mosaics/{mock_mosaic_data["uuid"]}/', {'name': 'updated_name'})
    assert mosaic.name == 'updated_name'


def test_delete(api, mock_mosaic_data):
    """Test the delete_mosaic method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    endpoint = mosaic.endpoint
    mosaic.delete()
    
    api.delete.assert_called_once_with(endpoint)
    assert mosaic.uuid is None
    assert mosaic.endpoint is None


def test_thumbnail(api, mock_mosaic_data):
    """Test the get_thumbnail method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    
    thumbnail = mosaic.thumbnail
    
    assert thumbnail == f"{api.base_url}{mosaic.endpoint}thumbnail"


def test_get_point(api, mock_mosaic_data):
    """Test the get_point method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    api.get.return_value = {'point': 'value'}
    
    point = mosaic.get_point(1, 2)

    assert point == {'point': 'value'}
    api.get.assert_called_once_with(f'{mosaic.endpoint}point?lat=1&lng=2')
    

def test_get_render_png_url(api, mock_mosaic_data):
    """Test the get_tile_render_url method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    
    tile_render_url = mosaic.get_render_png_url(x=1, y=2, z=3)

    assert tile_render_url == f'{api.base_url}{mosaic.endpoint}render/3/1/2.png'


def test_get_tile_png_url(api, mock_mosaic_data):
    """Test the get_tile_png_url method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    
    tile_png_url = mosaic.get_tile_png_url(x=1, y=2, z=3)

    assert tile_png_url == f'{api.base_url}{mosaic.endpoint}tiles/3/1/2.png'
    

def test_get_tile_json(api, mock_mosaic_data):
    """Test the get_tile_json method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    api.get.return_value = {'value': 'test'}
    result = mosaic.get_tile_json()    
    api.get.assert_called_once_with(f'{mosaic.endpoint}tilejson.json')
    assert result == {'value': 'test'}


def test_wmts(api, mock_mosaic_data):
    """Test the get_wmts method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    wmts_url = mosaic.wmts(scale=1)
    assert wmts_url == f'{api.base_url}{mosaic.endpoint}wmts/?scale=1'


def test_settings(api, mock_mosaic_data):
    """Test the get_settings method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    api.get.return_value = {'value': 'test'}
    
    settings = mosaic.settings

    api.get.assert_called_once_with(f'{mosaic.endpoint}settings/?f=json')
    assert settings == {'value': 'test'}


def test_set_settings(api, mock_mosaic_data):
    """Test the set_settings method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    api.put.return_value = 'test-settings-url'
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
    
    mosaic.set_settings(nodata=0, 
                        indexes=[1], 
                        rescale=[[0, 10000]], 
                        colormap_name='gist_rainbow', 
                        color_formula='Gamma R 0.5', 
                        expression='b1 * 2', 
                        exaggeraion=10, 
                        min_zoom=0, 
                        max_zoom=22, 
                        use_cache=True, 
                        cache_until_zoom=17)
    expected_data = {'visual_settings': 
                        {'nodata': 0, 
                        'indexes': [1], 
                        'rescale': [[0, 10000]], 
                        'colormap_name': 'gist_rainbow', 
                        'colormap': None, 
                        'color_formula': 'Gamma R 0.5', 
                        'expression': 'b1 * 2', 
                        'exaggeration': 10, 'exaggeraion': 10}, 
                    'tile_settings': 
                        {'min_zoom': 0, 
                        'max_zoom': 22, 
                        'use_cache': True, 
                        'cache_until_zoom': 17}}
    api.put.assert_called_once_with(f'{mosaic.endpoint}settings/', expected_data)


def test_get_rasters(api, mock_mosaic_data, mock_raster_data):
    """Test the get_rasters method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    api.get.return_value = [mock_raster_data, mock_raster_data]
    
    rasters = mosaic.get_rasters()
    
    api.get.assert_called_once_with(f'{mosaic.endpoint}rasters')
    assert len(rasters) == 2
    assert all(isinstance(r, Raster) for r in rasters)
    assert rasters[0].name == mock_raster_data['name']
    assert rasters[1].data == mock_raster_data


def test_add_rasters(api, mock_mosaic_data, mock_raster_data):
    """Test the add_raster method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    rasters = [
        Raster(api, mock_raster_data['uuid'], mock_raster_data),
        Raster(api, mock_raster_data['uuid'], mock_raster_data),
        Raster(api, mock_raster_data['uuid'], mock_raster_data),
    ]
    rasters[0].id = 1
    rasters[1].id = 2
    rasters[2].id = 3
    mosaic.add_rasters(rasters=rasters)
    
    api.post.assert_called_once_with(
        f'{mosaic.endpoint}rasters/',
        {'raster_ids': [1, 2, 3]},
        is_json=False
    )


def test_remove_rasters(api, mock_mosaic_data, mock_raster_data):
    """Test the remove_raster method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    rasters = [
        Raster(api, mock_raster_data['uuid'], mock_raster_data),
        Raster(api, mock_raster_data['uuid'], mock_raster_data),
        Raster(api, mock_raster_data['uuid'], mock_raster_data),
    ]
    rasters[0].id = 1
    rasters[1].id = 2
    rasters[2].id = 3
    mosaic.remove_rasters(rasters=rasters)
    
    api.delete.assert_called_once_with(
        f'{mosaic.endpoint}rasters/?raster_ids=%5B1%2C+2%2C+3%5D',
        is_json=False
    )


def test_share(api, mock_mosaic_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        mosaic = Mosaic(api, uuid=mock_mosaic_data['uuid'], data=mock_mosaic_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        mosaic.share(users=users)
        api.post.assert_called_once_with(
            f'{mosaic.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_mosaic_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        mosaic = Mosaic(api, uuid=mock_mosaic_data['uuid'], data=mock_mosaic_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        mosaic.unshare(users=users)
        api.post.assert_called_once_with(
            f'{mosaic.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_mosaic_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        mosaic = Mosaic(api, uuid=mock_mosaic_data['uuid'], data=mock_mosaic_data)
        result = mosaic.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{mosaic.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )
        
        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'


def test_seed_cache(api, mock_mosaic_data, mock_success_task_data):
    """Test the seed_cache method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    api.post.return_value = [{'task_id': mock_success_task_data['id']}]
    api.get_task.return_value = Task(api, mock_success_task_data['uuid'], mock_success_task_data)
    task = mosaic.seed_cache(from_zoom=0, to_zoom=22, workers=1)[0]

    expected_data = clean_data({
        'from_zoom': 0,
        'to_zoom': 22,
        'extent': None,
        'workers': 1
    })
    
    api.post.assert_called_once_with(f'{mosaic.endpoint}cache/seed/', expected_data)
    assert isinstance(task, Task)


def test_clear_cache(api, mock_mosaic_data):
    """Test the clear cache method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    mosaic.clear_cache()
    api.post.assert_called_once_with(f'{mosaic.endpoint}cache/clear/')


def test_cache_size(api, mock_mosaic_data):
    """Test the cache size method."""
    mosaic = Mosaic(api, mock_mosaic_data['uuid'], mock_mosaic_data)
    api.post.return_value = 1024
    size = mosaic.cache_size
    assert size == 1024
    api.post.assert_called_once_with(f'{mosaic.endpoint}cache/size/')