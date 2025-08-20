import pytest
from unittest.mock import patch

from geobox.workflow import Workflow
from geobox.user import User

def test_init(api, mock_workflow_data):
    workflow = Workflow(api, mock_workflow_data['uuid'], mock_workflow_data)
    assert workflow.name == mock_workflow_data['name']
    assert workflow.uuid == mock_workflow_data['uuid']
    assert workflow.data == mock_workflow_data
    assert workflow.endpoint == f'{Workflow.BASE_ENDPOINT}{workflow.uuid}/'


def test_get_workflows(api, mock_workflow_data):
    api.get.return_value = [mock_workflow_data, mock_workflow_data]
    workflows = Workflow.get_workflows(api)
    api.get.assert_called_once_with(f'{Workflow.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')
    assert len(workflows) == 2
    assert type(workflows[0]) == Workflow
    assert workflows[0].data == mock_workflow_data


def test_create_workflow(api, mock_workflow_data):
    api.post.return_value = mock_workflow_data
    workflow = Workflow.create_workflow(api,
                                        name=mock_workflow_data['name'],
                                        display_name=mock_workflow_data['display_name'],
                                        description=mock_workflow_data['description'],
                                        settings=mock_workflow_data['settings'],
                                        thumbnail=mock_workflow_data.get('thumbnail'))
    api.post.assert_called_once_with(Workflow.BASE_ENDPOINT, {'name': 'test'})
    assert type(workflow) == Workflow
    assert workflow.uuid == mock_workflow_data['uuid']
    assert workflow.data == mock_workflow_data


def test_get_workflow(api, mock_workflow_data):
    api.get.return_value = mock_workflow_data
    workflow = Workflow.get_workflow(api, uuid=mock_workflow_data['uuid'])
    api.get.assert_called_once_with(f"{Workflow.BASE_ENDPOINT}{mock_workflow_data['uuid']}/?f=json")
    assert type(workflow) == Workflow
    assert workflow.uuid == mock_workflow_data['uuid']
    assert workflow.data == mock_workflow_data


def test_get_workflow_by_name(api, mock_workflow_data):
    api.get.return_value = [mock_workflow_data]
    workflow = Workflow.get_workflow_by_name(api, name=mock_workflow_data['name'])
    api.get.assert_called_once_with(f"{Workflow.BASE_ENDPOINT}?f=json&q=name+%3D+%27test%27&return_count=False&skip=0&limit=10&shared=False")
    assert type(workflow) == Workflow
    assert workflow.uuid == mock_workflow_data['uuid']
    assert workflow.data == mock_workflow_data
    # not found
    workflow = Workflow.get_workflow_by_name(api, name='not_found')
    assert workflow == None


def test_update(api, mock_workflow_data):
    workflow = Workflow(api, mock_workflow_data['uuid'], mock_workflow_data)
    updated_data = {**mock_workflow_data,
                    'settings': {'settings': 'value'},
                    'thumbnail': 'thumbnail-url'}

    api.put.return_value = updated_data
    workflow.update(settings={'settings': 'value'}, thumbnail='thumbnail-url')
    api.put.assert_called_once_with(workflow.endpoint, {'settings': {'settings': 'value'}, 'thumbnail': 'thumbnail-url'})


def test_delete(api, mock_workflow_data):
    workflow = Workflow(api, mock_workflow_data['uuid'], mock_workflow_data)
    endpoint = workflow.endpoint
    workflow.delete()
    api.delete.assert_called_once_with(endpoint)
    assert workflow.uuid is None
    assert workflow.endpoint is None


def test_thumbnail(api, mock_workflow_data):
    workflow = Workflow(api, mock_workflow_data['uuid'], mock_workflow_data)
    thumbnail_url = workflow.thumbnail
    assert thumbnail_url == f"{api.base_url}{workflow.endpoint}thumbnail.png"


def test_share(api, mock_workflow_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        workflow = Workflow(api, uuid=mock_workflow_data['uuid'], data=mock_workflow_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        workflow.share(users=users)
        api.post.assert_called_once_with(
            f'{workflow.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_unshare(api, mock_workflow_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        workflow = Workflow(api, uuid=mock_workflow_data['uuid'], data=mock_workflow_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        workflow.unshare(users=users)
        
        # Verify the API call
        api.post.assert_called_once_with(
            f'{workflow.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )


def test_get_shared_users(api, mock_workflow_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        workflow = Workflow(api, uuid=mock_workflow_data['uuid'], data=mock_workflow_data)
        result = workflow.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{workflow.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'
