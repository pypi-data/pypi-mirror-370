import pytest
from unittest.mock import patch

from geobox.settings import SystemSettings
from geobox.user import User
from geobox.enums import MaxLogPolicy, InvalidDataPolicy, LoginFailurePolicy, MaxConcurrentSessionPolicy


def test_init(api, mock_system_settings_data):
    settings = SystemSettings(api, mock_system_settings_data)
    assert settings.data == mock_system_settings_data


def test_properties(api, mock_system_settings_data):
    settings = SystemSettings(api, mock_system_settings_data)
    assert settings.max_log_policy == MaxLogPolicy(mock_system_settings_data['max_log_policy'])
    assert settings.invalid_data_policy == InvalidDataPolicy(mock_system_settings_data['invalid_data_policy'])
    assert settings.login_failure_policy == LoginFailurePolicy(mock_system_settings_data['login_failure_policy'])
    assert settings.max_concurrent_session_policy == MaxConcurrentSessionPolicy(mock_system_settings_data['max_concurrent_session_policy'])


def test_repr(api, mock_system_settings_data):
    settings = SystemSettings(api, mock_system_settings_data)
    assert repr(settings) == 'SystemSettings()'


def test_get_system_settings(api, mock_system_settings_data):
    api.get.return_value = mock_system_settings_data
    settings = SystemSettings.get_system_settings(api)
    api.get.assert_called_once_with(f'{SystemSettings.BASE_ENDPOINT}?f=json')
    assert type(settings) == SystemSettings
    assert settings.data == mock_system_settings_data


def test_update(api, mock_system_settings_data):
    settings = SystemSettings(api, mock_system_settings_data)
    updated_data = {**mock_system_settings_data,
                    'max_log': 100,
                    'login_failure_policy': LoginFailurePolicy.DisableAccount.value}

    api.put.return_value = updated_data
    settings.update(max_log=100, login_failure_policy=LoginFailurePolicy.DisableAccount)
    api.put.assert_called_once_with(settings.BASE_ENDPOINT, {'max_log': 100, 'login_failure_policy': 'DisableAccount'})
