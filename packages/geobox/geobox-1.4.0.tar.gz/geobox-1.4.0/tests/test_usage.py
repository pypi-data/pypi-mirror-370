import pytest

from geobox.usage import Usage, UsageScale, UsageParam
from geobox.user import User
from geobox.apikey import ApiKey


def test_init(api, mock_user_data):
    user = User(api, mock_user_data['1']['id'], mock_user_data['1'])
    usage = Usage(api, user)
    assert usage.user == user
    assert usage.api == api


def test_repr(api, mock_user_data):
    user = User(api, mock_user_data['1']['id'], mock_user_data['1'])
    usage = Usage(api, user)
    assert repr(usage) == f"Usage(user={usage.user})"


def test_get_api_usage(api, mock_user_data, mock_apikey_data):
    data = [['2025-07-07T00:00:00', 21],
            ['2025-07-08T00:00:00', 267],
            ['2025-07-09T00:00:00', 1076],
            ['2025-07-11T00:00:00', 57],
            ['2025-07-12T00:00:00', 79]]
    api.get.return_value = data
    # user input
    user = User(api, mock_user_data['1']['id'], mock_user_data['1'])
    usage = Usage.get_api_usage(api, 
                               resource=user, 
                               scale=UsageScale.Day, 
                               param=UsageParam.Calls, 
                               days_before_now=5)
    assert usage == data
    api.get.assert_called_once_with('usage/api?eid=1&scale=day&param=calls&days_before_now=5')
    # apikey input
    api.reset_mock()
    apikey = ApiKey(api, mock_apikey_data['id'], mock_apikey_data)
    usage = Usage.get_api_usage(api, 
                               resource=apikey, 
                               scale=UsageScale.Day, 
                               param=UsageParam.Calls, 
                               days_before_now=5)
    assert usage == data
    api.get.assert_called_once_with('usage/api?eid=4t1dhyR1VHqzJDRY5ycO-daxVe-o1d8I-XzLriEHmiQ&scale=day&param=calls&days_before_now=5')
    
    # errors
    with pytest.raises(ValueError):
        Usage.get_api_usage(api, 
                            resource=apikey, 
                            scale=UsageScale.Day, 
                            param=UsageParam.Calls)

    with pytest.raises(ValueError):
        Usage.get_api_usage(api, 
                            resource='test', 
                            scale=UsageScale.Day, 
                            param=UsageParam.Calls,
                            days_before_now=5)


def test_get_process_usage(api):
    api.get.return_value = 23.458457
    process_usage = Usage.get_process_usage(api, days_before_now=5)
    assert process_usage == 23.458457

    # error
    with pytest.raises(ValueError):
        Usage.get_process_usage(api)


def test_get_usage_summary(api):
    data = {'available_storage': 396210733056,
                'used_storage': 1229062883,
                'max_daily_api_calls': 100000000,
                'daily_api_calls': 79,
                'max_monthly_api_calls': 3000000000,
                'monthly_api_calls': 2865,
                'max_daily_traffic': 10737418240,
                'daily_traffic': 251705,
                'max_monthly_traffic': 322122547200,
                'monthly_traffic': 50359396,
                'max_daily_process': 576,
                'daily_process': 0,
                'max_monthly_process': 17280,
                'monthly_process': 23,
                'remaining_days': None}
    api.get.return_value = data
    usage_summary = Usage.get_usage_summary(api)
    assert usage_summary == data


def test_update_usage(api):
    data = {'available_storage': 0,
            'used_storage': 1229062883,
            'max_daily_api_calls': 0,
            'daily_api_calls': 82,
            'max_monthly_api_calls': 0,
            'monthly_api_calls': 2868,
            'max_daily_traffic': 0,
            'daily_traffic': 252385,
            'max_monthly_traffic': 0,
            'monthly_traffic': 50360076,
            'max_daily_process': 0,
            'daily_process': 0,
            'max_monthly_process': 0,
            'monthly_process': 23,
            'remaining_days': None}
    api.post.return_value = data
    update = Usage.update_usage(api)
    assert update == data