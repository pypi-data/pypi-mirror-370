import pytest
from unittest.mock import patch

from geobox.plan import Plan
from geobox.user import User

def test_init(api, mock_plan_data):
    plan = Plan(api, mock_plan_data['id'], mock_plan_data)
    assert plan.name == mock_plan_data['name']
    assert plan.id == mock_plan_data['id']
    assert plan.data == mock_plan_data
    assert plan.endpoint == f'{Plan.BASE_ENDPOINT}{plan.id}'


def test_get_plans(api, mock_plan_data):
    api.get.return_value = [mock_plan_data, mock_plan_data]
    plans = Plan.get_plans(api)
    api.get.assert_called_once_with(f'{Plan.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')
    assert len(plans) == 2
    assert type(plans[0]) == Plan
    assert plans[0].data == mock_plan_data


def test_create_plan(api, mock_plan_data):
    api.post.return_value = mock_plan_data
    plan = Plan.create_plan(api,
                            name=mock_plan_data['name'], 
                            plan_color=mock_plan_data['plan_color'],
                            storage=mock_plan_data['storage'],
                            concurrent_tasks=mock_plan_data['concurrent_tasks'],
                            daily_api_calls=mock_plan_data['daily_api_calls'],
                            monthly_api_calls=mock_plan_data['monthly_api_calls'],
                            daily_traffic=mock_plan_data['daily_traffic'],
                            monthly_traffic=mock_plan_data['monthly_traffic'],
                            daily_process=mock_plan_data['daily_process'],
                            monthly_process=mock_plan_data['monthly_process'],
                            number_of_days=mock_plan_data['number_of_days'],
                            display_name=mock_plan_data['display_name'],
                            description=mock_plan_data['description'])
    api.post.assert_called_once_with(Plan.BASE_ENDPOINT, {'name': 'test', 'display_name': 'test plan', 'description': 'test plan description', 'plan_color': '#000000', 'storage': 1024, 'concurrent_tasks': 1, 'daily_api_calls': 10, 'monthly_api_calls': 10, 'daily_traffic': 10, 'monthly_traffic': 10, 'daily_process': 10, 'monthly_process': 10, 'number_of_days': 15})
    assert type(plan) == Plan
    assert plan.id == mock_plan_data['id']
    assert plan.data == mock_plan_data


def test_get_plan(api, mock_plan_data):
    api.get.return_value = mock_plan_data
    plan = Plan.get_plan(api, plan_id=mock_plan_data['id'])
    api.get.assert_called_once_with(f"{Plan.BASE_ENDPOINT}{mock_plan_data['id']}/?f=json")
    assert type(plan) == Plan
    assert plan.id == mock_plan_data['id']
    assert plan.data == mock_plan_data


def test_get_plan_by_name(api, mock_plan_data):
    api.get.return_value = [mock_plan_data]
    plan = Plan.get_plan_by_name(api, name=mock_plan_data['name'])
    api.get.assert_called_once_with(f"{Plan.BASE_ENDPOINT}?f=json&q=name+%3D+%27test%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(plan) == Plan
    assert plan.plan_id == mock_plan_data['id']
    assert plan.data == mock_plan_data
    # not found
    plan = Plan.get_plan_by_name(api, name='not_found')
    assert plan == None


def test_update(api, mock_plan_data):
    plan = Plan(api, mock_plan_data['id'], mock_plan_data)
    updated_data = {**mock_plan_data,
                    'storage': 2048,
                    'monthly_traffic': 1000}

    api.put.return_value = updated_data
    plan.update(storage=2048, monthly_traffic=1000)
    api.put.assert_called_once_with(plan.endpoint, {'storage': 2048, 'monthly_traffic': 1000})


def test_delete(api, mock_plan_data):
    plan = Plan(api, mock_plan_data['id'], mock_plan_data)
    endpoint = plan.endpoint
    plan.delete()
    api.delete.assert_called_once_with(endpoint)
    assert plan.plan_id is None
    assert plan.endpoint is None

