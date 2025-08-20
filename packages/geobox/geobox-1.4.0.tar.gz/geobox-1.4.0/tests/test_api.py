import pytest
import os
from unittest.mock import patch, Mock
import tempfile

from geobox.api import *
from geobox.exception import AuthenticationError
from geobox.enums import RoutingGeometryType, RoutingOverviewLevel, UsageParam, UsageScale


def test_init_with_apikey(env_vars):
    """Test initialization with API key."""
    client = GeoboxClient(apikey='test_key')
    assert client.apikey == 'test_key'


def test_init_with_access_token(env_vars):
    """Test initialization with access token."""
    client = GeoboxClient(access_token='test_token')
    assert client.access_token == 'test_token'
    assert client.session.headers['Authorization'] == 'Bearer test_token'


def test_init_with_username_password(env_vars):
    """Test initialization with username and password."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {'access_token': 'test_token'}
        mock_post.return_value.status_code = 200
        
        client = GeoboxClient(
            username='test_user',
            password='test_pass'
        )
        
        assert client.access_token == 'test_token'
        mock_post.assert_called_once_with(f'{client.base_url}auth/token/', data={'username': 'test_user', 'password': 'test_pass'})


def test_init_with_env_vars(env_vars):
    """Test initialization with environment variables."""
    # Set environment variables
    os.environ['GEOBOX_USERNAME'] = 'env_user'
    os.environ['GEOBOX_PASSWORD'] = 'env_pass'
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {'access_token': 'env_token'}
        mock_post.return_value.status_code = 200
        
        client = GeoboxClient(username='testuser', password='testpassword')
        assert client.username == 'env_user'
        assert client.password == 'env_pass'
        assert client.access_token == 'env_token'
        mock_post.assert_called_once_with(f'{client.base_url}auth/token/', data={'username': 'env_user', 'password': 'env_pass'})


def test_init_without_credentials(env_vars):
    """Test initialization without credentials raises error."""
    with pytest.raises(ValueError, match="Please provide either username/password, apikey or access_token."):
        GeoboxClient()


def test_get_access_token_success(env_vars):
    """Test successful access token retrieval."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {'access_token': 'test_token'}
        mock_post.return_value.status_code = 200
        
        
        client = GeoboxClient(
            username='test_user',
            password='test_pass'
        )
        token = client.get_access_token()
        assert token == 'test_token'
        mock_post.assert_called_with(f'{client.base_url}auth/token/', data={'username': 'test_user', 'password': 'test_pass'})


def test_get_access_token_failure(env_vars):
    """Test failed access token retrieval."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_vaue = {'detail': 'Invalid credentials'}
        mock_post.return_value.status_code = 401,
        
        with pytest.raises(AuthenticationError):
            client = GeoboxClient(
                username='test_user',
                password='test_pass'
            )
            client.get_access_token()
            mock_post.assert_called_once_with(f'{client.base_url}auth/token/', data={'username': 'test_user', 'password': 'test_pass'})


def test_request_json_false(env_vars):
    """Test that Content-Type is set to x-www-form-urlencoded when is_json=False."""
    client = GeoboxClient(access_token='access_token')
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        client.post('layers/', is_json=False)

        # Verify the method was called once
        mock_request.assert_called_once()
        
        # Get the call arguments
        args, kwargs = mock_request.call_args
        
        # Check specific aspects we care about
        assert args[0] == 'POST'  # HTTP method
        assert args[1] == f'{client.base_url}layers/'  # URL
        assert kwargs['data'] is None  # No data for this test
        
        # Check that Content-Type header is set correctly
        headers = kwargs.get('headers', {})
        assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer access_token'


def test_repr_with_apikey(env_vars):
    """Test the repr method with API key initialization."""
    client = GeoboxClient(apikey='test_key')
    assert repr(client) == "GeoboxClient(apikey=test_key)"


def test_repr_with_long_apikey(env_vars):
    """Test the repr method with a long API key."""
    long_key = 'x' * 25  # Longer than 20 characters
    client = GeoboxClient(apikey=long_key)
    assert repr(client) == "GeoboxClient(apikey=xxxxxxxxxxxxxxxxxxxx...)"


def test_repr_with_username_password(env_vars):
    """Test the repr method with username/password initialization."""
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token:
        mock_get_token.return_value = 'test_token'
        client = GeoboxClient(username='test_user', password='test_pass')
        assert repr(client) == "GeoboxClient(username=test_user)"


def test_repr_with_long_username(env_vars):
    """Test the repr method with a long username."""
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token:
        mock_get_token.return_value = 'test_token'
        long_username = 'x' * 25  # Longer than 20 characters
        client = GeoboxClient(username=long_username, password='test_pass')
        assert repr(client) == "GeoboxClient(username=xxxxxxxxxxxxxxxxxxxx...)"


def test_repr_with_access_token(env_vars):
    """Test the repr method with access token initialization."""
    client = GeoboxClient(access_token='test_token')
    assert repr(client) == "GeoboxClient(access_token=test_token)"


def test_repr_with_long_access_token(env_vars):
    """Test the repr method with a long access token."""
    long_token = 'x' * 25  # Longer than 20 characters
    client = GeoboxClient(access_token=long_token)
    assert repr(client) == "GeoboxClient(access_token=xxxxxxxxxxxxxxxxxxxx...)"


def test_manage_headers_for_request_with_files(env_vars):
    """Test _manage_headers_for_request when files are provided."""
    client = GeoboxClient(access_token='test_token')
    
    # Test with files - should remove Content-Type header
    original_content_type = client.session._manage_headers_for_request(files={'file': 'data'}, is_json=True)
    assert original_content_type == 'application/json'
    assert 'Content-Type' not in client.session.headers


def test_manage_headers_for_request_without_files_not_json(env_vars):
    """Test _manage_headers_for_request when no files and not JSON."""
    client = GeoboxClient(access_token='test_token')
    
    # Test without files and not JSON - should set Content-Type to form-urlencoded
    original_content_type = client.session._manage_headers_for_request(files=None, is_json=False)
    assert original_content_type == 'application/json'
    assert client.session.headers['Content-Type'] == 'application/x-www-form-urlencoded'


def test_manage_headers_for_request_with_files_restore_header(env_vars):
    """Test _manage_headers_for_request restores original Content-Type header."""
    client = GeoboxClient(access_token='test_token')
    
    client.session.headers['Content-Type'] = 'application/json'
    
    # Test with files - should remove and return original
    original_content_type = client.session._manage_headers_for_request(files={'file': 'data'}, is_json=True)
    assert original_content_type == 'application/json'
    assert 'Content-Type' not in client.session.headers


def test_init_calls_update_access_token(env_vars):
    """Test that __init__ calls update_access_token when using username/password."""
    with patch('requests.post') as mock_post, \
         patch('geobox.api._RequestSession.update_access_token') as mock_update:
        
        mock_post.return_value.json.return_value = {'access_token': 'test_token'}
        mock_post.return_value.status_code = 200
        
        GeoboxClient(username='test_user', password='test_pass')
        
        mock_update.assert_called_once_with('test_token')


def test_parse_error_message_no_detail(env_vars):
    """Test _parse_error_message when detail is not present."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.json.return_value = {'error': 'Some error'}
        
        result = client._parse_error_message(mock_response)
        assert result == "{'error': 'Some error'}"


def test_parse_error_message_detail_list(env_vars):
    """Test _parse_error_message when detail is a list with location."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.json.return_value = {
            'detail': [{'msg': 'Field error', 'loc': ['body', 'field_name']}]
        }
        
        result = client._parse_error_message(mock_response)
        assert result == 'Field error: "field_name"'


def test_parse_error_message_detail_list_no_location(env_vars):
    """Test _parse_error_message when detail is a list without location."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.json.return_value = {
            'detail': [{'msg': 'Field error'}]
        }
        
        result = client._parse_error_message(mock_response)
        assert result == 'Field error'


def test_parse_error_message_detail_dict(env_vars):
    """Test _parse_error_message when detail is a dictionary."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.json.return_value = {
            'detail': {'msg': 'Validation error', 'code': 'INVALID'}
        }
        
        result = client._parse_error_message(mock_response)
        assert result == 'Validation error'


def test_parse_error_message_detail_string(env_vars):
    """Test _parse_error_message when detail is a string."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.json.return_value = {
            'detail': 'Simple error message'
        }
        
        result = client._parse_error_message(mock_response)
        assert result == 'Simple error message'


def test_handle_error_401(env_vars):
    """Test _handle_error raises AuthenticationError for 401."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.status_code = 401
        mock_response.json.return_value = {'detail': 'Invalid credentials'}
        
        with pytest.raises(AuthenticationError, match="Invalid Authentication: Invalid credentials"):
            client._handle_error(mock_response)


def test_handle_error_403(env_vars):
    """Test _handle_error raises AuthorizationError for 403."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.status_code = 403
        mock_response.json.return_value = {'detail': 'Access denied'}
        
        with pytest.raises(AuthorizationError, match="Access forbidden: Access denied"):
            client._handle_error(mock_response)


def test_handle_error_404(env_vars):
    """Test _handle_error raises NotFoundError for 404."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.status_code = 404
        mock_response.json.return_value = {'detail': 'Resource not found'}
        
        with pytest.raises(NotFoundError, match="Resource not found: Resource not found"):
            client._handle_error(mock_response)


def test_handle_error_422(env_vars):
    """Test _handle_error raises ValidationError for 422."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.status_code = 422
        mock_response.json.return_value = {'detail': 'Validation failed'}
        
        with pytest.raises(ValidationError, match="Validation failed"):
            client._handle_error(mock_response)


def test_handle_error_500(env_vars):
    """Test _handle_error raises ServerError for 500+."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.status_code = 500
        mock_response.json.return_value = {'detail': 'Server error'}
        
        with pytest.raises(ServerError, match="Server error"):
            client._handle_error(mock_response)


def test_handle_error_other_status(env_vars):
    """Test _handle_error raises ApiRequestError for other status codes."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Response') as mock_response:
        mock_response.status_code = 418
        mock_response.json.return_value = {'detail': 'test error'}
        
        with pytest.raises(ApiRequestError, match="API request failed: test error"):
            client._handle_error(mock_response)


def test_make_request_with_apikey_no_access_token(env_vars):
    """Test _make_request adds apikey to URL when no access token."""
    client = GeoboxClient(apikey='test_key')
    
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        client._make_request('GET', 'test/endpoint')
        
        args, kwargs = mock_request.call_args
        assert 'apikey=test_key' in args[1]


def test_make_request_with_files(env_vars):
    """Test _make_request handles files correctly."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        files = {'file': 'data'}
        client._make_request('POST', 'test/endpoint', files=files)
        
        args, kwargs = mock_request.call_args
        assert kwargs['files'] == files


def test_make_request_with_json(env_vars):
    """Test _make_request handles JSON payload correctly."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        payload = {'key': 'value'}
        client._make_request('POST', 'test/endpoint', payload=payload, is_json=True)
        
        # Verify JSON parameter was passed
        args, kwargs = mock_request.call_args
        assert kwargs['json'] == payload


def test_make_request_with_form_data(env_vars):
    """Test _make_request handles form data correctly."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        payload = {'key': 'value'}
        client._make_request('POST', 'test/endpoint', payload=payload, is_json=False)
        
        # Verify data parameter was passed
        args, kwargs = mock_request.call_args
        assert kwargs['data'] == payload


def test_make_request_timeout_exception(env_vars):
    """Test _make_request handles timeout exceptions."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(ApiRequestError, match="Request timed out: Request timed out"):
            client._make_request('GET', 'test/endpoint')


def test_make_request_request_exception(env_vars):
    """Test _make_request handles request exceptions."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_request.side_effect = requests.exceptions.RequestException("Connection error")
        
        with pytest.raises(ApiRequestError, match="Request failed: Connection error"):
            client._make_request('GET', 'test/endpoint')


def test_make_request_error_status_codes(env_vars):
    """Test _make_request handles error status codes."""
    client = GeoboxClient(access_token='test_token')
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'detail': 'Invalid credentials'}
        mock_request.return_value = mock_response
        with pytest.raises(AuthenticationError):
            client._make_request('GET', 'test/endpoint')


def test_make_request_success_logging_200(env_vars):
    """Test _make_request logs success for status code 200."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request, \
         patch('geobox.api.logger') as mock_logger:
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        client._make_request('GET', 'test/endpoint')
        
        mock_logger.info.assert_called_with("Request successful: Status code 200")


def test_make_request_success_logging_201(env_vars):
    """Test _make_request logs success for status code 201."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request, \
         patch('geobox.api.logger') as mock_logger:
        
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        client._make_request('POST', 'test/endpoint')
        
        mock_logger.info.assert_called_with("Resource created successfully: Status code 201")


def test_make_request_success_logging_202(env_vars):
    """Test _make_request logs success for status code 202."""
    client = GeoboxClient(access_token='test_token')
    with patch('requests.Session.request') as mock_request, \
         patch('geobox.api.logger') as mock_logger:
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        client._make_request('GET', 'test/endpoint')
        mock_logger.info.assert_called_with("Request accepted successfully: Status code 202")


def test_make_request_success_logging_203(env_vars):
    """Test _make_request logs success for status code 203."""
    client = GeoboxClient(access_token='test_token')
    with patch('requests.Session.request') as mock_request, \
         patch('geobox.api.logger') as mock_logger:
        mock_response = Mock()
        mock_response.status_code = 203
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        client._make_request('GET', 'test/endpoint')
        mock_logger.info.assert_called_with("Non-authoritative information: Status code 203")


def test_make_request_success_logging_204(env_vars):
    """Test _make_request logs success for status code 204."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request, \
         patch('geobox.api.logger') as mock_logger:
        
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        client._make_request('DELETE', 'test/endpoint')
        
        mock_logger.info.assert_called_with("Deleted, operation successful: Status code 204")


def test_make_request_return_stream(env_vars):
    """Test _make_request returns response object when streaming."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        result = client._make_request('GET', 'test/endpoint', stream=True)
        
        assert result == mock_response


def test_make_request_return_json(env_vars):
    """Test _make_request returns JSON when not streaming."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'value'}
        mock_request.return_value = mock_response
        
        result = client._make_request('GET', 'test/endpoint', stream=False)
        
        assert result == {'data': 'value'}


def test_make_request_return_none_on_json_error(env_vars):
    """Test _make_request returns None when JSON parsing fails."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('requests.Session.request') as mock_request:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("JSON decode error")
        mock_request.return_value = mock_response
        
        result = client._make_request('GET', 'test/endpoint', stream=False)
        
        assert result is None


def test_get_method_delegation(env_vars):
    """Test get method delegates to _make_request correctly."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('geobox.api.GeoboxClient._make_request') as mock_make_request:
        mock_make_request.return_value = {'data': 'value'}
        
        result = client.get('test/endpoint', stream=True)
        
        mock_make_request.assert_called_once_with('GET', 'test/endpoint', stream=True)
        assert result == {'data': 'value'}


def test_post_method_delegation(env_vars):
    """Test post method delegates to _make_request correctly."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('geobox.api.GeoboxClient._make_request') as mock_make_request:
        mock_make_request.return_value = {'data': 'value'}
        
        payload = {'key': 'value'}
        files = {'file': 'data'}
        result = client.post('test/endpoint', payload=payload, is_json=False, files=files)
        
        mock_make_request.assert_called_once_with('POST', 'test/endpoint', payload, False, files=files)
        assert result == {'data': 'value'}


def test_put_method_delegation(env_vars):
    """Test put method delegates to _make_request correctly."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('geobox.api.GeoboxClient._make_request') as mock_make_request:
        mock_make_request.return_value = {'data': 'value'}
        
        payload = {'key': 'value'}
        result = client.put('test/endpoint', payload=payload, is_json=True)
        
        mock_make_request.assert_called_once_with('PUT', 'test/endpoint', payload, True)
        assert result == {'data': 'value'}


def test_delete_method_delegation(env_vars):
    """Test delete method delegates to _make_request correctly."""
    client = GeoboxClient(access_token='test_token')
    
    with patch('geobox.api.GeoboxClient._make_request') as mock_make_request:       
        payload = {'key': 'value'}
        result = client.delete('test/endpoint')
        
        mock_make_request.assert_called_once_with('DELETE', 'test/endpoint', None, None)


def test_init_calls_update_access_token_always_triggers(env_vars):
    """Test __init__ always triggers update_access_token for username/password."""
    with patch('requests.post') as mock_post, \
         patch('geobox.api._RequestSession.update_access_token') as mock_update:
        mock_post.return_value.json.return_value = {'access_token': 'test_token'}
        mock_post.return_value.status_code = 200
        # Unset env vars to ensure branch is triggered
        os.environ.pop('GEOBOX_USERNAME', None)
        os.environ.pop('GEOBOX_PASSWORD', None)
        os.environ.pop('GEOBOX_ACCESS_TOKEN', None)
        os.environ.pop('GEOBOX_APIKEY', None)
        client = GeoboxClient(username='test_user', password='test_pass')
        mock_update.assert_called_once_with('test_token')


def test_get_vectors(mock_vector_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_vector_data, mock_vector_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layers = client.get_vectors()
        
        assert len(layers) == 2
        assert isinstance(layers[0], VectorLayer)
        assert layers[0].data == mock_vector_data


def test_get_vector(mock_vector_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_vector_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layer = client.get_vector(uuid=mock_vector_data['uuid'])
        
        assert isinstance(layer, VectorLayer)
        assert layer.data == mock_vector_data


def test_get_vector_by_name(mock_vector_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_vector_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layer = client.get_vector_by_name(name=mock_vector_data['name'])
        
        assert isinstance(layer, VectorLayer)
        assert layer.data == mock_vector_data


def test_get_vectors_by_ids(mock_vector_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_vector_data, mock_vector_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layers = client.get_vectors_by_ids(ids=[1, 2])
        
        assert isinstance(layers[0], VectorLayer)
        assert layers[0].data == mock_vector_data


def test_create_vector(mock_vector_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_vector_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layer = client.create_vector(name=mock_vector_data["name"],
                                        layer_type=LayerType(mock_vector_data['layer_type']),
                                        display_name=mock_vector_data["display_name"])
        
        assert isinstance(layer, VectorLayer)
        assert layer.data == mock_vector_data


def test_get_files(mock_file_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_file_data, mock_file_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        files = client.get_files()
        
        assert len(files) == 2
        assert isinstance(files[0], File)
        assert files[0].data == mock_file_data


def test_get_file(mock_file_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_file_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        file = client.get_file(uuid=mock_file_data['uuid'])
        
        assert isinstance(file, File)
        assert file.data == mock_file_data


def test_get_files_by_name(mock_file_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_file_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        files = client.get_files_by_name(name=mock_file_data['name'])
        
        assert isinstance(files[0], File)
        assert files[0].data == mock_file_data


def test_upload_file():
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token:
        client = GeoboxClient(username='testuser', password='testpassword')
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
        
            with patch.object(client, 'post', return_value=mock_response) as mock_post:
                file = client.upload_file(temp_file_path, scan_archive=False)
                assert file.uuid == 'test-uuid-123'
                assert file.name == 'test.shp'


def test_get_tasks(mock_success_task_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_success_task_data, mock_success_task_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tasks = client.get_tasks()
        
        assert len(tasks) == 2
        assert isinstance(tasks[0], Task)
        assert tasks[0].data == mock_success_task_data


def test_get_task(mock_success_task_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_success_task_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tasks = client.get_task(uuid=mock_success_task_data['uuid'])
        
        assert isinstance(tasks, Task)
        assert tasks.data == mock_success_task_data


def test_get_views(mock_view_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_view_data, mock_view_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        views = client.get_views()
        
        assert len(views) == 2
        assert isinstance(views[0], VectorLayerView)
        assert views[0].data == mock_view_data


def test_get_views_by_ids(mock_view_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_view_data, mock_view_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        views = client.get_views_by_ids(ids=[1, 2])
        
        assert isinstance(views[0], VectorLayerView)
        assert views[0].data == mock_view_data


def test_get_view(mock_view_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_view_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        view = client.get_view(uuid=mock_view_data['uuid'])
        
        assert isinstance(view, VectorLayerView)
        assert view.data == mock_view_data


def test_get_view_by_name(mock_view_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_view_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        view = client.get_view_by_name(name=mock_view_data['name'])
        
        assert isinstance(view, VectorLayerView)
        assert view.data == mock_view_data


def test_create_tileset(mock_tileset_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_tileset_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layers = [
                 {
                 "layer_type": "vector",
                 "layer_uuid": "your_layer_uuid"
                 }
            ]
        tileset = client.create_tileset(mock_tileset_data['name'], 
                                        layers=layers,
                                        display_name=mock_tileset_data['display_name'], 
                                        description=mock_tileset_data['description'], 
                                        min_zoom=mock_tileset_data['min_zoom'], 
                                        max_zoom=mock_tileset_data['max_zoom'])
        
        assert isinstance(tileset, Tileset)
        assert tileset.data == mock_tileset_data


def test_get_tilesets(mock_tileset_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_tileset_data, mock_tileset_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tilesets = client.get_tilesets()
        
        assert len(tilesets) == 2
        assert isinstance(tilesets[0], Tileset)
        assert tilesets[0].data == mock_tileset_data


def test_get_tilesets_by_ids(mock_tileset_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_tileset_data, mock_tileset_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tilesets = client.get_tilesets_by_ids(ids=[1, 2])
        
        assert isinstance(tilesets[0], Tileset)
        assert tilesets[0].data == mock_tileset_data


def test_get_tileset(mock_tileset_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_tileset_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tileset = client.get_tileset(uuid=mock_tileset_data['uuid'])
        
        assert isinstance(tileset, Tileset)
        assert tileset.data == mock_tileset_data


def test_get_tileset_by_name(mock_tileset_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_tileset_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tileset = client.get_tileset_by_name(name=mock_tileset_data['name'])
        
        assert isinstance(tileset, Tileset)
        assert tileset.data == mock_tileset_data


def test_get_rasters(mock_raster_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_raster_data, mock_raster_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        rasters = client.get_rasters()
        
        assert len(rasters) == 2
        assert isinstance(rasters[0], Raster)
        assert rasters[0].data == mock_raster_data


def test_get_rasters_by_ids(mock_raster_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_raster_data, mock_raster_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        rasters = client.get_rasters_by_ids(ids=[1, 2])
        
        assert isinstance(rasters[0], Raster)
        assert rasters[0].data == mock_raster_data


def test_get_raster(mock_raster_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_raster_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        raster = client.get_raster(uuid=mock_raster_data['uuid'])
        
        assert isinstance(raster, Raster)
        assert raster.data == mock_raster_data


def test_get_raster_by_name(mock_raster_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_raster_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        raster = client.get_raster_by_name(name=mock_raster_data['name'])
        
        assert isinstance(raster, Raster)
        assert raster.data == mock_raster_data


def test_get_mosaics(mock_mosaic_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_mosaic_data, mock_mosaic_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        mosaics = client.get_mosaics()
        
        assert len(mosaics) == 2
        assert isinstance(mosaics[0], Mosaic)
        assert mosaics[0].data == mock_mosaic_data


def test_get_mosaics_by_ids(mock_mosaic_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_mosaic_data, mock_mosaic_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        mosaics = client.get_mosaics_by_ids(ids=[1, 2])
        
        assert isinstance(mosaics[0], Mosaic)
        assert mosaics[0].data == mock_mosaic_data


def test_create_mosaic(mock_mosaic_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_mosaic_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        mosaic = client.create_mosaic(name=mock_mosaic_data['name'],
                                        display_name=mock_mosaic_data['display_name'],
                                        description=mock_mosaic_data['description'],
                                        pixel_selection=mock_mosaic_data['pixel_selection'],
                                        min_zoom=mock_mosaic_data['min_zoom'])
        
        assert isinstance(mosaic, Mosaic)
        assert mosaic.data == mock_mosaic_data


def test_get_mosaic(mock_mosaic_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_mosaic_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        mosaic = client.get_mosaic(uuid=mock_mosaic_data['uuid'])
        
        assert isinstance(mosaic, Mosaic)
        assert mosaic.data == mock_mosaic_data


def test_get_mosaic_by_name(mock_mosaic_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_mosaic_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        mosaic = client.get_mosaic_by_name(name=mock_mosaic_data['name'])
        
        assert isinstance(mosaic, Mosaic)
        assert mosaic.data == mock_mosaic_data


def test_get_models(mock_model_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_model_data, mock_model_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        models = client.get_models()
        
        assert len(models) == 2
        assert isinstance(models[0], Model)
        assert models[0].data == mock_model_data


def test_get_model(mock_model_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_model_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        model = client.get_model(uuid=mock_model_data['uuid'])
        
        assert isinstance(model, Model)
        assert model.data == mock_model_data


def test_get_model_by_name(mock_model_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_model_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        model = client.get_model_by_name(name=mock_model_data['name'])
        
        assert isinstance(model, Model)
        assert model.data == mock_model_data


def test_get_maps(mock_map_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_map_data, mock_map_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        maps = client.get_maps()
        
        assert len(maps) == 2
        assert isinstance(maps[0], Map)
        assert maps[0].data == mock_map_data


def test_create_map(mock_map_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_map_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        map = client.create_map(name='Test Map',
                                display_name='Test Display Name',
                                description='Test Description',
                                extent=[10, 20, 30, 40],
                                thumbnail='https://example.com/thumbnail.png',
                                style={'type': 'style'})
        
        assert isinstance(map, Map)
        assert map.data == mock_map_data


def test_get_map(mock_map_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_map_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        map = client.get_map(uuid=mock_map_data['uuid'])
        
        assert isinstance(map, Map)
        assert map.data == mock_map_data


def test_get_map_by_name(mock_map_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_map_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        map = client.get_map_by_name(name=mock_map_data['name'])
        
        assert isinstance(map, Map)
        assert map.data == mock_map_data


def test_get_queries(mock_query_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_query_data, mock_query_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        queries = client.get_queries()
        
        assert len(queries) == 2
        assert isinstance(queries[0], Query)
        assert queries[0].data == mock_query_data


def test_create_query(mock_query_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_query_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        query = client.create_query(name='new', 
                                    sql='SELECT * FROM test', 
                                    params=[{'name': 'test', 'type': 'Layer', 'value': 'test_value'}])
        
        assert isinstance(query, Query)
        assert query.data == mock_query_data


def test_get_query(mock_query_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_query_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        query = client.get_query(uuid=mock_query_data['uuid'])
        
        assert isinstance(query, Query)
        assert query.data == mock_query_data


def test_get_query_by_name(mock_query_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_query_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        query = client.get_query_by_name(name=mock_query_data['name'])
        
        assert isinstance(query, Query)
        assert query.data == mock_query_data


def test_get_system_queries(mock_query_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_query_data, mock_query_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        queries = client.get_system_queries()
        
        assert len(queries) == 2
        assert isinstance(queries[0], Query)
        assert queries[0].data == mock_query_data


def test_get_users(mock_admin_user_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_admin_user_data, mock_admin_user_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        users = client.get_users()
        
        assert len(users) == 2
        assert isinstance(users[0], User)
        assert users[0].data == mock_admin_user_data


def test_create_user(mock_admin_user_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_admin_user_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        user = client.create_user(username=mock_admin_user_data['username'],
                                    email=mock_admin_user_data['email'],
                                    password='password',
                                    role=UserRole.ACCOUNT_ADMIN,
                                    first_name=mock_admin_user_data['first_name'],
                                    last_name=mock_admin_user_data['last_name'],
                                    mobile=mock_admin_user_data['mobile'],
                                    status=UserStatus.ACTIVE)
        
        assert isinstance(user, User)
        assert user.data == mock_admin_user_data


def test_search_users(mock_user_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_user_data['1'], mock_user_data['1']]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        users = client.search_users()
        
        assert len(users) == 2
        assert isinstance(users[0], User)
        assert users[0].data == mock_user_data['1']


def test_get_user(mock_admin_user_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_admin_user_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        user = client.get_user(user_id=mock_admin_user_data['id'])
        
        assert isinstance(user, User)
        assert user.data == mock_admin_user_data


def test_get_my_sessions(mock_session_data, mock_admin_user_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get, \
         patch('geobox.user.User.get_user') as mock_get_user:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_session_data, mock_session_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        mock_get_user.return_value = User(client, mock_admin_user_data)
        sessions = client.get_my_sessions()
        
        assert len(sessions) == 2
        assert isinstance(sessions[0], Session)
        assert sessions[0].data == mock_session_data


def test_get_workflows(mock_workflow_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_workflow_data, mock_workflow_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        workflows = client.get_workflows()
        
        assert len(workflows) == 2
        assert isinstance(workflows[0], Workflow)
        assert workflows[0].data == mock_workflow_data


def test_create_workflow(mock_workflow_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_workflow_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        workflow = client.create_workflow(name=mock_workflow_data['name'],
                                        display_name=mock_workflow_data['display_name'],
                                        description=mock_workflow_data['description'],
                                        settings=mock_workflow_data['settings'],
                                        thumbnail=mock_workflow_data.get('thumbnail'))
        
        assert isinstance(workflow, Workflow)
        assert workflow.data == mock_workflow_data


def test_get_workflow(mock_workflow_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_workflow_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        workflow = client.get_workflow(uuid=mock_workflow_data['uuid'])
        
        assert isinstance(workflow, Workflow)
        assert workflow.data == mock_workflow_data


def test_get_workflow_by_name(mock_workflow_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_workflow_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        workflow = client.get_workflow_by_name(name=mock_workflow_data['name'])
        
        assert isinstance(workflow, Workflow)
        assert workflow.data == mock_workflow_data


def test_get_versions(mock_version_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_version_data, mock_version_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        versions = client.get_versions()
        
        assert len(versions) == 2
        assert isinstance(versions[0], VectorLayerVersion)
        assert versions[0].data == mock_version_data


def test_get_version(mock_version_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_version_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        version = client.get_version(uuid=mock_version_data['uuid'])
        
        assert isinstance(version, VectorLayerVersion)
        assert version.data == mock_version_data


def test_get_version_by_name(mock_version_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_version_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        version = client.get_version_by_name(name=mock_version_data['name'])
        
        assert isinstance(version, VectorLayerVersion)
        assert version.data == mock_version_data


def test_get_layouts(mock_layout_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_layout_data, mock_layout_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layouts = client.get_layouts()
        
        assert len(layouts) == 2
        assert isinstance(layouts[0], Layout)
        assert layouts[0].data == mock_layout_data


def test_create_layout(mock_layout_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_layout_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layout = client.create_layout(name=mock_layout_data['name'],
                                        display_name=mock_layout_data['display_name'],
                                        description=mock_layout_data['description'],
                                        settings=mock_layout_data['settings'],
                                        thumbnail=mock_layout_data.get('thumbnail'))
        
        assert isinstance(layout, Layout)
        assert layout.data == mock_layout_data


def test_get_layout(mock_layout_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_layout_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layout = client.get_layout(uuid=mock_layout_data['uuid'])
        
        assert isinstance(layout, Layout)
        assert layout.data == mock_layout_data


def test_get_layout_by_name(mock_layout_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_layout_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layout = client.get_layout_by_name(name=mock_layout_data['name'])
        
        assert isinstance(layout, Layout)
        assert layout.data == mock_layout_data


def test_get_3dtiles(mock_tile3d_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_tile3d_data, mock_tile3d_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tiles = client.get_3dtiles()
        
        assert len(tiles) == 2
        assert isinstance(tiles[0], Tile3d)
        assert tiles[0].data == mock_tile3d_data


def test_get_3dtile(mock_tile3d_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_tile3d_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tile = client.get_3dtile(uuid=mock_tile3d_data['uuid'])
        
        assert isinstance(tile, Tile3d)
        assert tile.data == mock_tile3d_data


def test_get_3dtile_by_name(mock_tile3d_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_tile3d_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        tile = client.get_3dtile_by_name(name=mock_tile3d_data['name'])
        
        assert isinstance(tile, Tile3d)
        assert tile.data == mock_tile3d_data


def test_get_system_settings(mock_system_settings_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_system_settings_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        settings = client.get_system_settings()
        
        assert isinstance(settings, SystemSettings)
        assert settings.data == mock_system_settings_data


def test_get_scenes(mock_scene_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_scene_data, mock_scene_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        scenes = client.get_scenes()
        
        assert len(scenes) == 2
        assert isinstance(scenes[0], Scene)
        assert scenes[0].data == mock_scene_data


def test_create_scene(mock_scene_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_scene_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        scene = client.create_scene(name=mock_scene_data['name'],
                                        display_name=mock_scene_data['display_name'],
                                        description=mock_scene_data['description'],
                                        settings=mock_scene_data['settings'],
                                        thumbnail=mock_scene_data.get('thumbnail'))
        
        assert isinstance(scene, Scene)
        assert scene.data == mock_scene_data


def test_get_scene(mock_scene_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_scene_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        scene = client.get_scene(uuid=mock_scene_data['uuid'])
        
        assert isinstance(scene, Scene)
        assert scene.data == mock_scene_data


def test_get_scene_by_name(mock_scene_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_scene_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        scene = client.get_scene_by_name(name=mock_scene_data['name'])
        
        assert isinstance(scene, Scene)
        assert scene.data == mock_scene_data


def test_route():
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
            mock_get_token.return_value = 'test_token'
            mock_get.return_value = {'route': 'value'}
            
            client = GeoboxClient(username='testuser', password='testpassword')
            route = client.route(stops='53,33;56,36', 
                                    alternatives=True, 
                                    steps=True,
                                    geometries=RoutingGeometryType.geojson,
                                    overview=RoutingOverviewLevel.Full,
                                    annotations=True)
            assert route == {'route': 'value'}


def test_get_plans(mock_plan_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_plan_data, mock_plan_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        plans = client.get_plans()
        
        assert len(plans) == 2
        assert isinstance(plans[0], Plan)
        assert plans[0].data == mock_plan_data


def test_create_plan(mock_plan_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_plan_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        plan = client.create_plan(name=mock_plan_data['name'], 
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
        
        assert isinstance(plan, Plan)
        assert plan.data == mock_plan_data


def test_get_plan(mock_plan_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_plan_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        plan = client.get_plan(plan_id=mock_plan_data['id'])
        
        assert isinstance(plan, Plan)
        assert plan.data == mock_plan_data


def test_get_plan_by_name(mock_plan_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_plan_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        plan = client.get_plan_by_name(name=mock_plan_data['name'])
        
        assert isinstance(plan, Plan)
        assert plan.data == mock_plan_data


def test_get_dashboards(mock_dashboard_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_dashboard_data, mock_dashboard_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        dashboards = client.get_dashboards()
        
        assert len(dashboards) == 2
        assert isinstance(dashboards[0], Dashboard)
        assert dashboards[0].data == mock_dashboard_data


def test_create_dashboard(mock_dashboard_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_dashboard_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        dashboard = client.create_dashboard(name=mock_dashboard_data['name'],
                                        display_name=mock_dashboard_data['display_name'],
                                        description=mock_dashboard_data['description'],
                                        settings=mock_dashboard_data['settings'],
                                        thumbnail=mock_dashboard_data.get('thumbnail'))
        
        assert isinstance(dashboard, Dashboard)
        assert dashboard.data == mock_dashboard_data


def test_get_dashboard(mock_dashboard_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_dashboard_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        dashboard = client.get_dashboard(uuid=mock_dashboard_data['uuid'])
        
        assert isinstance(dashboard, Dashboard)
        assert dashboard.data == mock_dashboard_data


def test_get_dashboard_by_name(mock_dashboard_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_dashboard_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        dashboard = client.get_dashboard_by_name(name=mock_dashboard_data['name'])
        
        assert isinstance(dashboard, Dashboard)
        assert dashboard.data == mock_dashboard_data


def test_get_basemaps(mock_basemap_list_data, mock_basemap_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_basemap_list_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        basemaps = client.get_basemaps()
        
        assert len(basemaps) == 2
        assert isinstance(basemaps[0], Basemap)
        assert basemaps[0].data == mock_basemap_data


def test_get_basemap(mock_basemap_list_data, mock_basemap_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_basemap_list_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        basemap = client.get_basemap(name=mock_basemap_data['name'])
        
        assert isinstance(basemap, Basemap)
        assert basemap.data == mock_basemap_data


def test_proxy_basemap(mock_basemap_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:

        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_basemap_data

        client = GeoboxClient(username='testuser', password='testpassword')
        client.proxy_basemap(url='test-url')
        mock_get.assert_called_once_with('basemaps/?url=test-url')


def test_get_attachments(mock_attachment_data, mock_vector_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_attachment_data, mock_attachment_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        layer = VectorLayer(client, mock_vector_data['uuid'], LayerType.Polygon, mock_vector_data)
        attachments = client.get_attachments(resource_type=AttachmentResourceType.Vector, resource_uuid=layer.uuid)
        
        assert len(attachments) == 2
        assert isinstance(attachments[0], Attachment)
        assert attachments[0].data == mock_attachment_data


def test_create_attachment(mock_attachment_data, mock_feature_data, mock_vector_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        client = GeoboxClient(username='testuser', password='testpassword')
        layer = VectorLayer(client, mock_attachment_data['key'].split(':')[1], LayerType.Polygon, mock_vector_data)
        mock_feature_data['Polygon']['id'] = 1
        feature = Feature(layer, data=mock_feature_data['Polygon'])
        file = File(client, mock_attachment_data['file']['uuid'], mock_attachment_data['file'])
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_attachment_data
        
        attachment = client.create_attachment(name=mock_attachment_data['name'],
                                                loc_x=mock_attachment_data['loc_x'],
                                                loc_y=mock_attachment_data['loc_y'],
                                                resource=layer,
                                                file=file,
                                                feature=feature,
                                                display_name=mock_attachment_data['display_name'],
                                                description=mock_attachment_data['description'])
        
        assert isinstance(attachment, Attachment)
        assert attachment.data == mock_attachment_data


def test_update_attachment(mock_attachment_data):
    expected_data = {'name': 'updated_name', 
                'display_name': 'updated display name', 
                'description': 'updated description', 
                'loc_x': 10, 
                'loc_y': 20}
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.put') as mock_put:
            mock_get_token.return_value = 'test_token'
            mock_put.return_value = {**mock_attachment_data, **expected_data}
            
            client = GeoboxClient(username='testuser', password='testpassword')
            updated_data = client.update_attachment(attachment_id=mock_attachment_data['id'],
                                                name=expected_data['name'],
                                                display_name=expected_data['display_name'],
                                                description=expected_data['description'],
                                                loc_x=expected_data['loc_x'],
                                                loc_y=expected_data['loc_y'])
            assert updated_data == {**mock_attachment_data, **expected_data}


def test_get_apikeys(mock_apikey_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_apikey_data, mock_apikey_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        apikeys = client.get_apikeys()
        
        assert len(apikeys) == 2
        assert isinstance(apikeys[0], ApiKey)
        assert apikeys[0].data == mock_apikey_data


def test_create_apikey(mock_apikey_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.post') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_apikey_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        apikey = client.create_apikey(name=mock_apikey_data['name'])
        
        assert isinstance(apikey, ApiKey)
        assert apikey.data == mock_apikey_data


def test_get_apikey(mock_apikey_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = mock_apikey_data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        apikey = client.get_apikey(key_id=mock_apikey_data['id'])
        
        assert isinstance(apikey, ApiKey)
        assert apikey.data == mock_apikey_data


def test_get_apikey_by_name(mock_apikey_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_apikey_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        apikey = client.get_apikey_by_name(name=mock_apikey_data['name'])
        
        assert isinstance(apikey, ApiKey)
        assert apikey.data == mock_apikey_data


def test_get_logs(mock_log_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
         patch('geobox.api.GeoboxClient.get') as mock_get:
        
        mock_get_token.return_value = 'test_token'
        mock_get.return_value = [mock_log_data, mock_log_data]
        
        client = GeoboxClient(username='testuser', password='testpassword')
        logs = client.get_logs()
        
        assert len(logs) == 2
        assert isinstance(logs[0], Log)
        assert logs[0].data == mock_log_data


def test_get_api_usage(mock_user_data):
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
        patch('geobox.api.GeoboxClient.get') as mock_get:
    
        mock_get_token.return_value = 'test_token'
        data = [['2025-07-07T00:00:00', 21],
                ['2025-07-08T00:00:00', 267],
                ['2025-07-09T00:00:00', 1076],
                ['2025-07-11T00:00:00', 57],
                ['2025-07-12T00:00:00', 79]]
        mock_get.return_value = data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        user = User(client, mock_user_data['1']['id'], mock_user_data)
        usage = client.get_api_usage(resource=user, scale=UsageScale.Day, param=UsageParam.Calls, days_before_now=5)

        assert usage == data


def test_get_process_usage():
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
        patch('geobox.api.GeoboxClient.get') as mock_get:
    
        mock_get_token.return_value = 'test_token'
        data = 23.458457
        mock_get.return_value = data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        process_usage = client.get_process_usage(days_before_now=5)

        assert process_usage == data


def test_get_usage_summary():
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
        patch('geobox.api.GeoboxClient.get') as mock_get:
    
        mock_get_token.return_value = 'test_token'
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
        mock_get.return_value = data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        usage_summary = client.get_usage_summary()

        assert usage_summary == data


def test_update_usage():
    with patch('geobox.api.GeoboxClient.get_access_token') as mock_get_token, \
        patch('geobox.api.GeoboxClient.post') as mock_post:
    
        mock_get_token.return_value = 'test_token'
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
        mock_post.return_value = data
        
        client = GeoboxClient(username='testuser', password='testpassword')
        update = client.update_usage()

        assert update == data