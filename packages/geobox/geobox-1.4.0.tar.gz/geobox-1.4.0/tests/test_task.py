import pytest
from unittest import mock
from unittest.mock import patch, PropertyMock
from geobox.file import File
from geobox.task import Task
import itertools
from datetime import datetime

from geobox.enums import LayerType, TaskStatus
from geobox.vectorlayer import VectorLayer
from geobox.raster import Raster
from geobox.model3d import Model
from geobox.tile3d import Tile3d


def test_init(api, mock_success_task_data):
    """Test Task initialization."""
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    assert task.uuid == mock_success_task_data['uuid']
    assert task.data == mock_success_task_data
    assert task.endpoint == f"{Task.BASE_ENDPOINT}{mock_success_task_data['uuid']}/"


def test_repr(api, mock_success_task_data):
    """Test Task string representation."""
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    assert repr(task) == f"Task(uuid={task.uuid}, name={mock_success_task_data['name']})"


def test_output_asset_property(api, mock_publish_task_data, mock_vector_data, mock_raster_data, mock_model_data, mock_file_data, mock_tile3d_data):
    # raster layer
    task = Task(api, uuid=mock_publish_task_data['uuid'], data=mock_publish_task_data)
    api.get_raster.return_value = Raster(api, mock_raster_data['uuid'], data=mock_raster_data)
    expected_layer = Raster(api, mock_raster_data['uuid'], data=mock_raster_data)
    assert task.output_asset.name == expected_layer.name
    assert task.output_asset.uuid == expected_layer.uuid
    assert task.output_asset.data == expected_layer.data
    assert type(task.output_asset) == Raster
    # vector layer
    mock_publish_task_data['result']['layer_uuid'] = mock_publish_task_data['result']['raster_uuid']
    del mock_publish_task_data['result']['raster_uuid']
    task = Task(api, uuid=mock_publish_task_data['uuid'], data=mock_publish_task_data)
    api.get_vector.return_value = VectorLayer(api, mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    expected_layer = VectorLayer(api, mock_vector_data['uuid'], layer_type=LayerType.Polygon, data=mock_vector_data)
    assert task.output_asset.name == expected_layer.name
    assert task.output_asset.layer_type == expected_layer.layer_type
    assert task.output_asset.uuid == expected_layer.uuid
    assert task.output_asset.data == expected_layer.data
    assert type(task.output_asset) == VectorLayer
    #model
    mock_publish_task_data['result']['model_uuid'] = mock_publish_task_data['result']['layer_uuid']
    del mock_publish_task_data['result']['layer_uuid']
    task = Task(api, uuid=mock_publish_task_data['uuid'], data=mock_publish_task_data)
    api.get_model.return_value = Model(api, mock_model_data['uuid'], data=mock_model_data)
    expected_layer = Model(api, mock_model_data['uuid'], data=mock_model_data)
    assert task.output_asset.name == expected_layer.name
    assert task.output_asset.uuid == expected_layer.uuid
    assert task.output_asset.data == expected_layer.data
    assert type(task.output_asset) == Model
    # file
    mock_publish_task_data['result']['file_uuid'] = mock_publish_task_data['result']['model_uuid']
    del mock_publish_task_data['result']['model_uuid']
    task = Task(api, uuid=mock_publish_task_data['uuid'], data=mock_publish_task_data)
    api.get_file.return_value = File(api, mock_file_data['uuid'], data=mock_file_data)
    expected_layer = File(api, mock_file_data['uuid'], data=mock_file_data)
    assert task.output_asset.name == expected_layer.name
    assert task.output_asset.uuid == expected_layer.uuid
    assert task.output_asset.data == expected_layer.data
    assert type(task.output_asset) == File
    # tile3d
    mock_publish_task_data['result']['3dtiles_uuid'] = mock_publish_task_data['result']['file_uuid']
    del mock_publish_task_data['result']['file_uuid']
    task = Task(api, uuid=mock_publish_task_data['uuid'], data=mock_publish_task_data)
    api.get_3dtile.return_value = Tile3d(api, mock_tile3d_data['uuid'], data=mock_tile3d_data)
    expected_layer = Tile3d(api, mock_tile3d_data['uuid'], data=mock_tile3d_data)
    assert task.output_asset.name == expected_layer.name
    assert task.output_asset.uuid == expected_layer.uuid
    assert task.output_asset.data == expected_layer.data
    assert type(task.output_asset) == Tile3d
    #None
    mock_publish_task_data['name'] = 'import'
    del mock_publish_task_data['result']['3dtiles_uuid']
    task = Task(api, uuid=mock_publish_task_data['uuid'], data=mock_publish_task_data)
    assert task.output_asset == None


def test_properties_success(api, mock_success_task_data):
    """Test Task properties for successful task."""
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    api.get.return_value = mock_success_task_data
    assert task.name == mock_success_task_data['name']
    assert task.status == TaskStatus.SUCCESS
    assert task.errors is None
    assert task.accepted_at == datetime.strptime(mock_success_task_data['accepted_at'], "%Y-%m-%dT%H:%M:%S.%f")
    assert task.started_at == datetime.strptime(mock_success_task_data['started_at'], "%Y-%m-%dT%H:%M:%S.%f")
    assert task.finished_at == datetime.strptime(mock_success_task_data['finished_at'], "%Y-%m-%dT%H:%M:%S.%f")
    assert task.result == mock_success_task_data['result']


def test_properties_failure(api, mock_failure_task_data):
    """Test Task properties for failed task."""
    task = Task(api, uuid=mock_failure_task_data['uuid'], data=mock_failure_task_data)
    api.get.return_value = mock_failure_task_data
    assert task.name == mock_failure_task_data['name']
    assert task.status == TaskStatus.FAILURE
    assert task.errors == {
            'detail': {
                'msg': 'raster dataset with the same name already exists.',
                'type': 'geobox.DuplicatRasterDatasetNameError'
            }
        }
    assert task.accepted_at == datetime.strptime(mock_failure_task_data['accepted_at'], "%Y-%m-%dT%H:%M:%S.%f")
    assert task.started_at == datetime.strptime(mock_failure_task_data['started_at'], "%Y-%m-%dT%H:%M:%S.%f")
    assert task.finished_at == datetime.strptime(mock_failure_task_data['finished_at'], "%Y-%m-%dT%H:%M:%S.%f")
    assert task.result == mock_failure_task_data['result']


def test_progress(api, mock_success_task_data):
    """Test Task progress property."""
    mock_response = {
        'current': 50,
        'total': 100
    }
    with patch.object(api, 'get', return_value=mock_response):
        task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
        assert task.progress == 50


def test_progress_not_running(api, mock_success_task_data):
    """Test Task progress property when task is not running."""
    mock_response = {
        'current': None,
        'total': None
    }
    with patch.object(api, 'get', return_value=mock_response):
        task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
        assert task.progress is None


def test_wait_success(api, mock_success_task_data):
    """Test Task wait method with successful completion."""
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    states = [TaskStatus.PENDING, TaskStatus.SUCCESS]
    progress_values = [0, 50, 100]

    with patch.object(type(task), 'status', new_callable=PropertyMock) as mock_status, \
         patch.object(type(task), 'progress', new_callable=PropertyMock) as mock_progress:
        mock_status.side_effect = states
        mock_progress.side_effect = progress_values
        result = task.wait(timeout=5, interval=0.1)
        assert result == TaskStatus.SUCCESS

    import builtins
    original_import = builtins.__import__

    def mocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tqdm.auto":
            raise ImportError("No module named 'tqdm'")
        return original_import(name, globals, locals, fromlist, level)

    with mock.patch("builtins.__import__", side_effect=mocked_import):
        with mock.patch("geobox.api.logger") as mock_logger:
            result = task._create_progress_bar()
            assert result is None
            mock_logger.warning.assert_called_once()


def test_wait_failure(api, mock_failure_task_data):
    """Test Task wait method with failure."""
    task = Task(api, uuid=mock_failure_task_data['uuid'], data=mock_failure_task_data)
    states = [TaskStatus.PENDING, TaskStatus.FAILURE]
    progress_values = [0, 30, 60]
    
    with patch.object(type(task), 'status', new_callable=PropertyMock) as mock_status, \
         patch.object(type(task), 'progress', new_callable=PropertyMock) as mock_progress:
        mock_status.side_effect = states
        mock_progress.side_effect = progress_values
        result = task.wait(timeout=5, interval=0.1)
        assert result == TaskStatus.FAILURE


def test_wait_timeout_pending(api, mock_success_task_data):
    """Test Task wait method with timeout."""
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    with patch.object(type(task), 'status', new_callable=PropertyMock) as mock_status:
        with pytest.raises(TimeoutError, match=f"Task {mock_success_task_data['name']} timed out after 1 seconds"):
            mock_status.return_value = 'PENDING'
            result = task.wait(timeout=1, interval=0.1)
            assert result == task


def test_wait_timeout(api, mock_success_task_data):
    """Test Task wait method raises TimeoutError when task times out."""
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    with patch.object(type(task), 'status', new_callable=PropertyMock) as mock_status, \
         patch.object(type(task), 'progress', new_callable=PropertyMock) as mock_progress:
        mock_status.return_value = TaskStatus.PENDING
        mock_progress.side_effect = itertools.cycle([0, 10, 20, 30, 40, 50])  
        with pytest.raises(TimeoutError, match=f"Task {mock_success_task_data['name']} timed out after 1 seconds"):
            task.wait(timeout=1, interval=0.1)


def test_wait_without_progress_bar(api, mock_success_task_data):
    """Test Task wait method without progress bar."""
    task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
    states = [TaskStatus.PENDING, TaskStatus.SUCCESS]
    progress_values = [0, 50, 100]
    
    with patch.object(type(task), 'status', new_callable=PropertyMock) as mock_status, \
         patch.object(type(task), 'progress', new_callable=PropertyMock) as mock_progress, \
         patch('tqdm.auto.tqdm') as mock_tqdm:
        mock_status.side_effect = states
        mock_progress.side_effect = progress_values
        result = task.wait(timeout=5, interval=0.1, progress_bar=False)
        assert result == TaskStatus.SUCCESS
        mock_tqdm.assert_not_called()


def test_abort(api, mock_success_task_data):
    """Test Task abort method."""
    with patch.object(api, 'post') as mock_post:
        task = Task(api, uuid=mock_success_task_data['uuid'], data=mock_success_task_data)
        task.abort()
        mock_post.assert_called_once_with(f"tasks/{mock_success_task_data['uuid']}/abort/")


def test_get_tasks(api, mock_success_task_data):
    """Test getting list of tasks."""
    mock_response = [
        mock_success_task_data,
        mock_success_task_data
    ]

    with patch.object(api, 'get', return_value=mock_response):
        tasks = Task.get_tasks(api, search_fields='name', search='test')
        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)
        assert tasks[0].uuid == mock_success_task_data['uuid']
        assert tasks[1].uuid == mock_success_task_data['uuid']
    # return count
    mock_response = 42
    with patch.object(api, 'get', return_value=mock_response):
        count = Task.get_tasks(api, return_count=True)
        assert count == 42


def test_get_task(api, mock_success_task_data):
    """Test getting a single task."""
    with patch.object(api, 'get', return_value=mock_success_task_data):
        task = Task.get_task(api, uuid=mock_success_task_data['uuid'])
        assert isinstance(task, Task)
        assert task.uuid == mock_success_task_data['uuid']
        assert task.name == mock_success_task_data['name']
        assert task.data == mock_success_task_data
