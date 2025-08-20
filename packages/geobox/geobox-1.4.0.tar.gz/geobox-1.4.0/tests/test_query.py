import pytest
from unittest.mock import Mock, patch

from geobox.query import Query, QueryGeometryType, QueryParamType, QueryResultType
from geobox.task import Task
from geobox.user import User


def test_init(api, mock_query_data):
    """Test Query initialization."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    assert query.api == api
    assert query.uuid == mock_query_data['uuid']
    assert query.data == mock_query_data
    assert query.result == {}
    assert query._system_query == False


def test_check_access_system_query(api, mock_query_data):
    """Test _check_access raises exception for system queries."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError, match="Cannot modify system queries - they are read-only"):
        query._check_access()


def test_check_access_regular_query(api, mock_query_data):
    """Test _check_access allows regular queries."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = False
    
    query._check_access()


def test_get_sql(api, mock_query_data):
    """Test sql property getter."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    assert query.sql == mock_query_data['sql']


def test_set_sql(api, mock_query_data):
    """Test sql property setter."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    new_sql = "SELECT * FROM new_table"
    
    query.sql = new_sql
    
    assert query.data['sql'] == new_sql


def test_get_params(api, mock_query_data):
    """Test params property getter."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    assert query.params == mock_query_data['params']


def test_get_params_empty_list(api, mock_query_data):
    """Test params property getter initializes empty list."""
    mock_query_data = {**mock_query_data, **{'params': 100}}
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    assert query.params == []
    assert query.data['params'] == []


def test_set_params(api, mock_query_data):
    """Test params property setter."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    new_param = [
        {"name": "foo", "value": "bar", "type": "Layer"},
        {"name": "baz", "value": "qux", "type": "Layer"}
    ]
    query.params = new_param
    assert query.params == new_param


def test_set_params_triggers_initialization(api, mock_query_data):
    """Trigger line 131 in setter by setting params when initial params is not a list."""
    # Set initial params to a non-list value
    mock_query_data = {**mock_query_data, 'params': 100}  # integer, not list
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    # Now assign to params with any value, line 131 should execute
    query.params = [{"name": "foo", "value": "bar", "type": "Layer"}]
    
    assert isinstance(query.data['params'], list)


@patch('geobox.map.urljoin')
@patch('geobox.map.urlencode')
def test_get_queries(mock_urlencode, mock_urljoin, mock_query_data, api):
    """Test get_queries class method."""
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = 'queries/?f=json'
    
    api.get.return_value = [mock_query_data]

    queries = Query.get_queries(api, uuid=mock_query_data['uuid'], data=mock_query_data)
    assert len(queries) == 1
    assert queries[0].name == mock_query_data['name']
    assert queries[0].uuid == mock_query_data['uuid']
    assert queries[0].data == mock_query_data
    api.get.mock_query_data(f'{Query.BASE_ENDPOINT}?f=json&return_count=False&skip=0&limit=10&shared=False')

    # Test with return_count
    api.reset_mock()
    api.get.return_value = 5
    count = Query.get_queries(api, return_count=True)
    assert count == 5
    api.get.assert_called_once_with(f'{Query.BASE_ENDPOINT}?f=json&return_count=True&skip=0&limit=10&shared=False')


def test_create_query(mock_query_data, api):
    """Test create_query class method."""
    api.post.return_value = mock_query_data
    query = Query.create_query(api, 
                                name='new', 
                                sql='SELECT * FROM test', 
                                params=[{'name': 'test', 'type': 'Layer', 'value': 'test_value'}])
    assert isinstance(query, Query)
    assert query.data == mock_query_data
    api.post.assert_called_once_with(Query.BASE_ENDPOINT, {'name': 'new', 'sql': 'SELECT * FROM test', 'params': [{'name': 'test', 'type': 'Layer', 'value': 'test_value'}]})


@patch('geobox.map.urljoin')
@patch('geobox.map.urlencode')
def test_get_query(mock_urlencode, mock_urljoin, mock_query_data, api):
    """Test get_query class method."""
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = f'{Query.BASE_ENDPOINT}{mock_query_data["uuid"]}/?f=json'
    api.get.return_value = mock_query_data

    query = Query.get_query(api, mock_query_data['uuid'])
    api.get.assert_called_once_with(f'{query.endpoint}?f=json')
    assert query.data == mock_query_data


@patch('geobox.map.urljoin')
@patch('geobox.map.urlencode')
def test_get_query_by_name(mock_urlencode, mock_urljoin, mock_query_data, api):
    """Test get_query class method."""
    mock_urlencode.return_value = 'f=json'
    mock_urljoin.return_value = f'{Query.BASE_ENDPOINT}{mock_query_data["uuid"]}/?f=json'
    api.get.return_value = [mock_query_data]

    query = Query.get_query_by_name(api, name=mock_query_data['name'])
    api.get.assert_called_once_with(f'{Query.BASE_ENDPOINT}?f=json&q=name+%3D+%27new%27&return_count=False&skip=0&limit=10&shared=False')
    assert query.data == mock_query_data
    # not found
    query = Query.get_query_by_name(api, name='not_found')
    assert query == None


def test_get_system_queries(mock_query_data, api):
    """Test get_system_queries class method."""
    api.get.return_value = [mock_query_data, mock_query_data, mock_query_data]
    
    result = Query.get_system_queries(api)
    
    api.get.assert_called_once_with(f'{Query.BASE_ENDPOINT}systemQueries/?f=json&return_count=False&skip=0&limit=100&shared=False')
    assert len(result) == 3
    assert isinstance(result[0], Query)
    assert result[0]._system_query == True


def test_add_param(api, mock_query_data):
    """Test add_param method."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    original_length = len(query.params)
    
    query.add_param(
        name="test_param",
        value="test_value",
        type=QueryParamType.TEXT,
        default_value="default",
        Domain={'key': 'value'}
    )
    
    assert len(query.params) == original_length + 1
    new_param = query.params[-1]
    assert new_param['name'] == "test_param"
    assert new_param['value'] == "test_value"
    assert new_param['type'] == QueryParamType.TEXT.value
    assert new_param['default_value'] == "default"
    assert new_param['Domain'] == {'key': 'value'}

    # add param to system query
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError):
        query.add_param("test", "value", QueryParamType.TEXT)


def test_remove_param(api, mock_query_data):
    """Test remove_param method."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    original_length = len(query.params)
    param_name = query.params[0]['name']
    
    query.remove_param(param_name)
    
    assert len(query.params) == original_length - 1

    # not found
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    with pytest.raises(ValueError, match="Parameter with name 'nonexistent' not found"):
        query.remove_param("nonexistent")

    # remove system query param
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError):
        query.remove_param("test")


def test_execute(api, mock_query_data):
    """Test execute method."""
    api.post.return_value = {'result': 'success'}
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    result = query.execute(
        f="json",
        result_type=QueryResultType.both,
        return_count=True,
        out_srid=4326,
        skip=10,
        limit=100
    )
    
    api.post.assert_called_once_with(f'{query.BASE_ENDPOINT}exec/', {'f': 'json', 'sql': 'SELECT layer.*, ST_Centroid(geom) as goem\nFROM layer', 'params': [{'name': 'layer', 'type': 'Layer', 'default_value': None, 'domain': None}, {'name': 'layer', 'value': '297fa7ca-877a-400c-8003-d65de9e791c2', 'type': 'Layer', 'default_value': '297fa7ca-877a-400c-8003-d65de9e791c2', 'Domain': {}}], 'result_type': 'both', 'return_count': True, 'out_srid': 4326, 'quant_factor': 1000000, 'skip': 10, 'limit': 100, 'skip_geometry': False})
    assert result == {'result': 'success'}
    assert query.result == {'result': 'success'}


def test_execute_no_sql(api, mock_query_data):
    """Test execute raises exception when no SQL."""
    data = mock_query_data.copy()
    data['sql'] = None
    query = Query(api, data['uuid'], data)
    
    with pytest.raises(ValueError, match='"sql" parameter is required'):
        query.execute()


def test_execute_no_params(api, mock_query_data):
    """Test execute raises exception when no params."""
    mock_query_data['params'] = []
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    with pytest.raises(ValueError, match='"params" parameter is required'):
        query.execute()


def test_execute_system_query(api, mock_query_data):
    """Test execute raises exception for system queries."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError):
        query.execute()


def test_update(api, mock_query_data):
    """Test update_query method."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    updated_query_data = mock_query_data.copy()
    updated_query_data['name'] = "new_name"
    updated_query_data['display_name'] = "New Display Name"
    updated_query_data['sql'] = "SELECT * FROM new_table"
    updated_query_data['params'] = [{'name': 'new_param'}]

    api.put.return_value = updated_query_data
    query.update(
        name="new_name",
        display_name="New Display Name",
        sql="SELECT * FROM new_table",
        params=[{'name': 'new_param'}]
    )
    
    api.put.assert_called_once_with(
        query.endpoint,
        {
            "name": "new_name",
            "display_name": "New Display Name",
            "sql": "SELECT * FROM new_table",
            "params": [{'name': 'new_param'}]
        }
    )
    assert query.data == updated_query_data

    # update system queries
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError):
        query.update(name="test")


def test_save_existing_query(api, mock_query_data):
    """Test save method for existing query."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query.save()

    api.put.assert_called_once_with(query.endpoint, {'name': 'new', 'sql': 'SELECT layer.*, ST_Centroid(geom) as goem\nFROM layer', 'params': [{'name': 'layer', 'value': '297fa7ca-877a-400c-8003-d65de9e791c2', 'type': 'Layer', 'default_value': '297fa7ca-877a-400c-8003-d65de9e791c2', 'Domain': {}}]}
)


def test_save_new_query(api, mock_query_data):
    """Test save method for new query."""
    response = {**mock_query_data, **{'uuid': mock_query_data['uuid']}}
    api.post.return_value = response
    del mock_query_data['uuid']
    query = Query(api, data=mock_query_data)
    
    query.save()
        
    api.post.assert_called_once_with(query.BASE_ENDPOINT, mock_query_data)
    assert query.data == response


def test_save_removes_empty_params(api, mock_query_data):
    """Test save method removes empty params."""
    query_data_copy = mock_query_data.copy()
    query_data_copy['params'] = [
        {'name': 'param1', 'value': 'value1'},
        {'name': 'param2', 'value': ''},
        {'name': 'param3', 'value': None}
    ]
    query = Query(api, mock_query_data['uuid'], query_data_copy)
    
    query.save()
    
    # Should remove params without value
    assert len(query.params) == 1
    assert query.params[0]['name'] == 'param1'


def test_delete(api, mock_query_data):
    """Test delete method."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    endpoint = query.endpoint
    query.delete()
    api.delete.assert_called_once_with(endpoint)

    # delete system query
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError):
        query.delete()


def test_share(api, mock_query_data, mock_user_data):
    """Test file sharing."""
    with patch.object(api, 'post'):
        query = Query(api, mock_query_data['uuid'], mock_query_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        query.share(users=users)
        api.post.assert_called_once_with(
            f'{query.endpoint}share/',
            {'user_ids': [1, 2]}, is_json=False
        )
        # share system queries
        query = Query(api, mock_query_data['uuid'], mock_query_data)
        query._system_query = True
    
        with pytest.raises(PermissionError):
            query.share([Mock(spec=User)])


def test_unshare(api, mock_query_data, mock_user_data):
    """Test file unsharing."""
    with patch.object(api, 'post'):
        query = Query(api, mock_query_data['uuid'], mock_query_data)
        users = [
            User(api, user_id=mock_user_data['1']['id'], data=mock_user_data['1']),
            User(api, user_id=mock_user_data['2']['id'], data=mock_user_data['2'])
        ]
        query.unshare(users=users)
        api.post.assert_called_once_with(
            f'{query.endpoint}unshare/',
            {'user_ids': [1, 2]}, is_json=False
        )
        # unshare system queries
        query = Query(api, mock_query_data['uuid'], mock_query_data)
        query._system_query = True
    
        with pytest.raises(PermissionError):
            query.unshare([Mock(spec=User)])


def test_get_shared_users(api, mock_query_data, mock_user_data):
    """Test getting shared users."""
    mock_response = [
        mock_user_data['1'],
        mock_user_data['2']
    ]
    
    with patch.object(api, 'get', return_value=mock_response):
        query = Query(api, uuid=mock_query_data['uuid'], data=mock_query_data)
        result = query.get_shared_users(search='user', limit=2)

        api.get.assert_called_once_with(
            f'{query.endpoint}shared-with-users/?search=user&skip=0&limit=2'
        )

        assert len(result) == 2
        assert result[0].first_name == 'test 1'
        assert result[0].last_name == 'test 1'
        assert result[1].first_name == 'test 2'
        assert result[1].last_name == 'test 2'

        # get system query shared users
        query = Query(api, mock_query_data['uuid'], mock_query_data)
        query._system_query = True
    
        with pytest.raises(PermissionError):
            query.get_shared_users(search='user', limit=2)


def test_thumbnail(api, mock_query_data):
    """Test thumbnail property."""
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    thumbnail_url = query.thumbnail
    
    assert thumbnail_url == f'{api.base_url}{query.endpoint}thumbnail.png'

    # get system query thumbnail
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError):
        query.thumbnail


def test_save_as_layer(api, mock_query_data, mock_success_task_data):
    """Test save_as_layer method."""
    api.post.return_value = {'task_id': mock_success_task_data['id']}
    api.get.return_value = mock_success_task_data
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    
    task = query.save_as_layer("new_layer", QueryGeometryType.POINT)
    
    api.post.assert_called_once_with(f'{query.BASE_ENDPOINT}saveAsLayer/', {'sql': 'SELECT layer.*, ST_Centroid(geom) as goem\nFROM layer', 'params': [{'name': 'layer', 'type': 'Layer', 'value': None}, {'name': 'layer', 'type': 'Layer', 'value': '297fa7ca-877a-400c-8003-d65de9e791c2'}], 'layer_name': 'new_layer', 'layer_type': 'Point'})
    assert isinstance(task, Task)

    # save system query as layer
    query = Query(api, mock_query_data['uuid'], mock_query_data)
    query._system_query = True
    
    with pytest.raises(PermissionError):
        query.save_as_layer("test_layer", QueryGeometryType.POINT)