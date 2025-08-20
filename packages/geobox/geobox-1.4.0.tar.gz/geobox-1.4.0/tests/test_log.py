import pytest
from unittest.mock import patch

from geobox.log import Log

def test_init(api, mock_log_data):
    log = Log(api, mock_log_data['id'], mock_log_data)
    assert log.log_id == mock_log_data['id']
    assert log.data == mock_log_data
    assert log.endpoint == f'{Log.BASE_ENDPOINT}{log.log_id}'


def test_repr(api, mock_log_data):
    log = Log(api, mock_log_data['id'], mock_log_data)
    assert repr(log) == f"Log(id={log.log_id}, activity_type={log.activity_type})"


def test_get_logs(api, mock_log_data):
    api.get.return_value = [mock_log_data, mock_log_data]
    logs = Log.get_logs(api)
    api.get.assert_called_once_with(f'{Log.BASE_ENDPOINT}')
    assert len(logs) == 2
    assert type(logs[0]) == Log
    assert logs[0].data == mock_log_data


def test_delete(api, mock_log_data):
    log = Log(api, mock_log_data['id'], mock_log_data)
    endpoint = log.endpoint
    log.delete()
    api.delete.assert_called_once_with(endpoint)
    assert log.log_id is None
    assert log.endpoint is None

