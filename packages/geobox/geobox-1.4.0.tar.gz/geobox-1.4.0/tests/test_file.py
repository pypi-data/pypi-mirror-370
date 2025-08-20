import pytest
import os
from unittest import mock
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import zipfile
import shutil

from geobox.file import File, FileType, ValidationError
from geobox.enums import PublishFileType, InputGeomType
from geobox.task import Task
from geobox.user import User


def test_init(api, mock_file_data):
    """Test File initialization."""
    file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
    assert file.uuid == mock_file_data['uuid']
    assert file.data == mock_file_data
    assert file.endpoint == f'files/{mock_file_data["uuid"]}/'


def test_properties(api, mock_file_data):
    """Test File properties."""
    file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
    assert file.name == 'world_boundaries.shp'
    assert file.file_type.value == 'Shapefile'
    assert file.size == 7588516
    assert file.feature_count == 394
    assert file.layer_count == 1


def test_repr(api, mock_file_data):
    """Test File string representation."""
    file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
    assert repr(file) == f"File(uuid={file.uuid}, file_name={file.name}, file_type=Shapefile)"


def test_layers(api, mock_file_data):
    file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
    assert file.layers == mock_file_data['layers']['layers']


def test_upload_file_success(api):
    """Test successful file upload."""
    mock_response = {
        'uuid': 'test-uuid-123',
        'name': 'test.shp',
        'file_type': 'shp',
        'size': 1024,
        'feature_count': 100,
        'layer_count': 1
    }
    with tempfile.NamedTemporaryFile(suffix='.shp', delete=False) as temp_file:
        temp_file.write(b'test content')
        temp_file_path = temp_file.name
    
        with patch.object(api, 'post', return_value=mock_response) as mock_post:
            file = File.upload_file(api, temp_file_path, scan_archive=False)
            assert file.uuid == 'test-uuid-123'
            assert file.name == 'test.shp'
            mock_post.assert_called_once()


def test_upload_file_not_found(api):
    """Test file upload with non-existent file."""
    with pytest.raises(FileNotFoundError):
        File.upload_file(api, 'nonexistent.shp')


def test_upload_file_invalid_type(api):
    """Test file upload with invalid file type."""
    with tempfile.NamedTemporaryFile(suffix='.invalid', delete=False) as temp_file:
        temp_file.write(b'test content')
        temp_file_path = temp_file.name

    # Use the actual extension string
    invalid_extension = os.path.splitext(temp_file_path)[1]

    with pytest.raises(ValueError, match=f".invalid' is not a valid FileFormat"):
        File.upload_file(api, temp_file_path)

    # Clean up
    os.remove(temp_file_path)


def test_get_files(api):
    """Test getting list of files."""
    mock_response = [
            {
                'uuid': 'test-uuid-1',
                'name': 'test1.shp',
                'file_type': 'shp'
            },
            {
                'uuid': 'test-uuid-2',
                'name': 'test2.shp',
                'file_type': 'shp'
            }
        ]

    with patch.object(api, 'get', return_value=mock_response):
        files = File.get_files(api, search_fields='name', search='test', limit=2)
        assert len(files) == 2
        assert all(isinstance(f, File) for f in files)
        assert files[0].uuid == 'test-uuid-1'
        assert files[1].uuid == 'test-uuid-2'
        api.get.assert_called_once_with(f"{File.BASE_ENDPOINT}?f=json&search=test&search_fields=name&return_count=False&skip=0&limit=2&shared=False")


def test_get_file(api, mock_file_data):
    """Test getting file by UUID."""
    with patch.object(api, 'get', return_value=mock_file_data):
        file = File.get_file(api, uuid=mock_file_data['uuid'])
        assert isinstance(file, File)
        assert file.uuid == mock_file_data['uuid']
        assert file.name == mock_file_data['name']
        api.get.assert_called_once_with(f"{file.endpoint}info/?f=json")


def test_get_files_by_name(api, mock_file_data):
    """Test getting file by name."""
    mock_response = [mock_file_data]
    with patch.object(api, 'get', return_value=mock_response):
        files = File.get_files_by_name(api, name=mock_file_data['name'])
        assert isinstance(files[0], File)
        assert files[0].uuid == mock_file_data['uuid']
        assert files[0].name == mock_file_data['name']
        api.get.assert_called_once_with(f"{files[0].BASE_ENDPOINT}?f=json&q=name+%3D+%27world_boundaries.shp%27&return_count=False&skip=0&limit=10&shared=False")


def test_download(api, mock_file_data):
    """Test file download."""
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b'test file content']
    mock_response.__exit__.return_value = None
    mock_response.__enter__.return_value.headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': 'attachment; filename="test_file.shp"'
    }

    with patch.object(api, 'get', return_value=mock_response), \
         patch('builtins.open', MagicMock()) as mock_open, \
         patch.object(zipfile.ZipFile, 'write', return_value=None), \
         patch('os.remove', return_value=None), \
         patch('os.rename', return_value=None):
        file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
        save_path = file.download()
        assert save_path.endswith('.shp')

    mock_file_data['name'] = None
    file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b'test content']
    mock_response.__exit__.return_value = None
    mock_response.__enter__.return_value.headers = {
        'Content-Type': 'image/tiff',
        'Content-Disposition': 'attachment; filename="test_raster.tif"'
    }
    api.get.return_value = mock_response

    with tempfile.TemporaryDirectory() as temp_dir:
        downloaded_path = file.download()
        assert downloaded_path.endswith('.tif')
        assert os.path.exists(downloaded_path)


    if os.path.exists(downloaded_path):
        os.remove(downloaded_path)

    # error
    with pytest.raises(ValueError):
        file.download(save_path='path')

    file.uuid = None
    with pytest.raises(ValueError):
        file.download()

    # import warning log
    import builtins
    original_import = builtins.__import__

    def mocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tqdm.auto":
            raise ImportError("No module named 'tqdm'")
        return original_import(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=mocked_import):
        with mock.patch("geobox.api.logger") as mock_logger:
            result = file._create_progress_bar()
            assert result is None
            mock_logger.warning.assert_called_once()


def test_download_custom_path(api, mock_file_data):
    """Test file download with custom path."""
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b'test file content']
    mock_response.__exit__.return_value = None
    mock_response.__enter__.return_value.headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': 'attachment; filename="test_file.zip"'
    }

    custom_path = os.path.join(os.getcwd(), 'tests', 'custom_path') + '/'
    os.makedirs(custom_path, exist_ok=True)

    try:
        with patch.object(api, 'get', return_value=mock_response), \
             patch('builtins.open', MagicMock()) as mock_open, \
             patch.object(zipfile.ZipFile, 'write', return_value=None), \
             patch('os.remove', return_value=None), \
             patch('os.rename', return_value=None):
            file = File(api, uuid='test-uuid-123', data=mock_file_data)
            save_path = file.download(save_path=custom_path)
            assert save_path.endswith('.zip')
    finally:
        shutil.rmtree(custom_path, ignore_errors=True)


def test_download_no_filename_in_content_disposition(api, mock_file_data):
    """Test file download when Content-Disposition header has no filename."""
    mock_response = MagicMock()
    mock_response.__enter__.return_value.iter_content.return_value = [b'some content']
    mock_response.__exit__.return_value = None
    mock_response.__enter__.return_value.headers = {
        'Content-Disposition': 'attachment',  # No filename=
        'Content-Type': 'image/png'
    }
    
    # Mock the response object itself to have the headers attribute
    mock_response.__enter__.return_value.headers = mock_response.__enter__.return_value.headers
    
    with patch.object(api, 'get', return_value=mock_response), \
         patch('builtins.open', mock_open()) as mock_file_open, \
         patch('os.rename') as mock_rename, \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.path.abspath') as mock_abspath, \
         patch('os.path.dirname', return_value='dummy/path/to/'):
        
        # Configure os.path.abspath to return predictable paths
        def abspath_side_effect(path):
            if path == "dummy/path/to/file/":
                return "/absolute/dummy/path/to/file/"
            elif path == "/absolute/dummy/path/to/file/.png":
                return "/absolute/dummy/path/to/file/.png"
            return f"/absolute/{path}"
        
        mock_abspath.side_effect = abspath_side_effect
        
        file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
        result = file.download(save_path="dummy/path/to/file/")
        
        # Verify the expected behavior
        assert result.endswith('.png')
        mock_makedirs.assert_called_once()
        # mock_rename.assert_called_once()


def test_delete(api, mock_file_data):
    """Test file deletion."""
    with patch.object(api, 'delete'):
        file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
        file.delete()
        api.delete.assert_called_once_with(f'files/{mock_file_data["uuid"]}/')


@pytest.mark.parametrize("file_type", [
    (type)
    for type in FileType
    if type not in [FileType.Compressed, FileType.Complex, FileType.Video, FileType.Image, FileType.Document]
])
def test_publish(api, mock_file_data, mock_success_task_data, file_type):
    """Test file publishing with all combinations of publish types"""
    mock_response = {
        'task_id': mock_success_task_data['id']
    }
    mock_file_data['file_type'] = file_type.value
    with patch.object(api, 'post', return_value=mock_response) as mock_post:
        with patch.object(api, 'get', return_value=mock_success_task_data) as mock_post:
            file = File(api, uuid=mock_file_data['uuid'], data=mock_file_data)
            result = file.publish(
                name='test_layer'
            )
            
            # Verify the response
            assert isinstance(result, Task)
            assert result.id == mock_success_task_data['id']


def test_publish_unkown_format(api, mock_file_data):
    """Test file publishing with unknown format"""
    mock_file_data['file_type'] = FileType.Document
    with pytest.raises(ValidationError):
        File(api, uuid=mock_file_data['uuid'], data=mock_file_data).publish(name='test')
        

def test_share(api, mock_file_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        file = File(api, uuid='test-uuid-123', data=mock_file_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        file.share(users=users)
        api.post.assert_called_once_with(
            f'{file.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_file_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        file = File(api, uuid='test-uuid-123', data=mock_file_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        file.unshare(users=users)
        api.post.assert_called_once_with(
            f'{file.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_file_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        file = File(api, uuid='test-uuid-123', data=mock_file_data)
        result = file.get_shared_users(search='user', limit=2)
        
        api.get.assert_called_once_with(
            f'{file.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )
        
        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
