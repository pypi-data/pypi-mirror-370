import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import json

from contextbase import Contextbase
from contextbase.http_response import ContextbaseResponse, ContextbaseError
from contextbase.http_error import HttpError
from contextbase.http_client import HttpClient
from contextbase.file import ContextbaseFile


class TestContextbase:
    """Test suite for the main Contextbase client."""
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = Contextbase(api_key="test-key")
        assert client.http_client.api_key == "test-key"
    
    @patch.dict('os.environ', {'CONTEXTBASE_API_KEY': 'env-key'})
    def test_init_with_env_api_key(self):
        """Test initialization using environment variable."""
        client = Contextbase()
        assert client.http_client.api_key == "env-key"
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_with_body(self, mock_post):
        """Test publishing data with body."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123", "status": "published"}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.publish(
            context_name="test-context",
            body={"data": "value"}
        )
        
        # Verify
        mock_post.assert_called_once_with(
            "/v1/contexts/test-context/data",
            data={
                "body": {"data": "value"}
            }
        )
        assert response.status_code == 200
        assert response.json["id"] == "123"
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_with_file(self, mock_post):
        """Test publishing data with file."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "456"}
        mock_post.return_value = ContextbaseResponse(mock_response)

        client = Contextbase(api_key="test-key")
        
        # Create ContextbaseFile object
        file_obj = ContextbaseFile.from_data("test content", "test.txt", "text/plain")

        # Execute
        response = client.publish(
            context_name="test-context",
            file=file_obj,
            scopes={"env": "test"}
        )

        # Verify
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        assert call_args[0][0] == "/v1/contexts/test-context/data"
        
        data = call_args[1]["data"]
        assert data["scopes"] == {"env": "test"}
        assert "file" in data
        assert "body" not in data
        
        file_data = data["file"]
        assert file_data["name"] == "test.txt"
        assert file_data["mime_type"] == "text/plain"
    
    def test_publish_without_body_or_file(self):
        """Test that publish raises ValueError when neither body nor file provided."""
        client = Contextbase(api_key="test-key")
        
        with pytest.raises(ValueError, match="Either 'body' or 'file' is required"):
            client.publish("test-context")
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_resolve_context_basic(self, mock_post):
        """Test basic resolve functionality."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{"id": 1}, {"id": 2}]}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.resolve_context("test-context")
        
        # Verify
        mock_post.assert_called_once_with(
            "/v1/contexts/test-context/resolve",
            data={}
        )
        assert len(response.json["results"]) == 2
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_resolve_context_with_query_and_scopes(self, mock_post):
        """Test resolve with query and scopes."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.resolve_context(
            context_name="test-context",
            query="search term",
            scopes={"env": "prod"}
        )
        
        # Verify
        mock_post.assert_called_once_with(
            "/v1/contexts/test-context/resolve",
            data={
                "query": "search term",
                "scopes": {"env": "prod"}
            }
        )

    @patch('contextbase.http_client.HttpClient.post')
    def test_resolve_prompt_basic(self, mock_post):
        """Test basic resolve functionality."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{"id": 1}, {"id": 2}]}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.resolve_prompt("test-prompt")
        
        # Verify
        mock_post.assert_called_once_with(
            "/v1/prompts/test-prompt/resolve",
            data={}
        )
        assert len(response.json["results"]) == 2
        
    @patch('contextbase.http_client.HttpClient.post')
    def test_resolve_prompt_with_query_and_scopes(self, mock_post):
        """Test resolve with query and scopes."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.resolve_prompt(
            prompt_name="test-prompt",
            query="search term",
            scopes={"env": "prod"}
        )
        
        # Verify
        mock_post.assert_called_once_with(
            "/v1/prompts/test-prompt/resolve",
            data={
                "query": "search term",
                "scopes": {"env": "prod"}
            }
        )


class TestContextbaseResponse:
    """Test suite for the ContextbaseResponse wrapper."""
    
    def test_successful_response(self):
        """Test response wrapper with successful HTTP response."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "value", "id": "123"}
        mock_response.text = '{"data": "value", "id": "123"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.reason = "OK"
        
        # Execute
        response = ContextbaseResponse(mock_response)
        
        # Verify
        assert response.ok is True
        assert response.is_success is True
        assert response.status_code == 200
        assert response.json == {"data": "value", "id": "123"}
        assert response.text == '{"data": "value", "id": "123"}'
        assert response.headers == {"Content-Type": "application/json"}
        assert response.error is None
        assert bool(response) is True
        assert "data" in response
        assert response["id"] == "123"
        assert response.get("data") == "value"
        assert response.get("missing", "default") == "default"
    
    def test_error_response(self):
        """Test response wrapper with error HTTP response."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "Bad Request",
            "errors": ["Field 'name' is required", "Invalid format"]
        }
        mock_response.text = '{"message": "Bad Request", "errors": [...]}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.reason = "Bad Request"
        
        # Execute
        response = ContextbaseResponse(mock_response)
        
        # Verify
        assert response.ok is False
        assert response.is_success is False
        assert response.status_code == 400
        assert response.error is not None
        assert response.error.message == "Bad Request"
        assert len(response.error.errors) == 2
        assert bool(response) is False
    
    def test_response_without_json(self):
        """Test response wrapper when JSON parsing fails."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Internal Server Error"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.reason = "Internal Server Error"
        
        # Execute
        response = ContextbaseResponse(mock_response)
        
        # Verify
        assert response.ok is False
        assert response.json is None
        assert response.error is not None
        assert "HTTP 500" in response.error.message
    
    def test_raise_for_status_success(self):
        """Test raise_for_status with successful response."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        response = ContextbaseResponse(mock_response)
        
        # Should not raise any exception
        response.raise_for_status()
    
    def test_raise_for_status_with_error(self):
        """Test raise_for_status with error response."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "Validation failed",
            "errors": ["Missing field"]
        }
        mock_response.reason = "Bad Request"
        
        response = ContextbaseResponse(mock_response)
        
        # Should raise ContextbaseError
        with pytest.raises(ContextbaseError) as exc_info:
            response.raise_for_status()
        
        assert exc_info.value.status_code == 400
        assert "Validation failed" in str(exc_info.value)
    
    def test_dict_access_with_no_json(self):
        """Test dict-like access when no JSON data available."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("No JSON")
        
        response = ContextbaseResponse(mock_response)
        
        # Should raise KeyError
        with pytest.raises(KeyError):
            _ = response["key"]
        
        # get() should return default
        assert response.get("key", "default") == "default"
        assert "key" not in response


class TestHttpClient:
    """Test suite for the HttpClient."""
    
    def test_init_with_api_key(self):
        """Test HttpClient initialization with API key."""
        client = HttpClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.contextbase.dev"
    
    @patch.dict('os.environ', {'CONTEXTBASE_API_KEY': 'env-key'})
    def test_init_with_env_key(self):
        """Test HttpClient initialization with environment variable."""
        client = HttpClient()
        assert client.api_key == "env-key"
    
    def test_init_without_api_key(self):
        """Test HttpClient initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                HttpClient()
    
    @patch('requests.post')
    def test_post_request(self, mock_post):
        """Test POST request functionality."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        client = HttpClient(api_key="test-key")
        
        # Execute
        response = client.post("/test", {"data": "value"})
        
        # Verify
        mock_post.assert_called_once_with(
            "https://api.contextbase.dev/test",
            json={"data": "value"},
            headers={
                'x-api-key': 'test-key',
                'Content-Type': 'application/json',
                'User-Agent': 'contextbase-python-sdk/1.0.0'
            },
            timeout=30
        )
        assert isinstance(response, ContextbaseResponse)
    
    @patch('requests.post')
    def test_post_request_exception(self, mock_post):
        """Test POST request when requests raises exception."""
        # Setup
        mock_post.side_effect = requests.RequestException("Connection failed")
        client = HttpClient(api_key="test-key")
        
        # Execute & Verify
        with pytest.raises(requests.RequestException, match="Failed to make request"):
            client.post("/test", {"data": "value"})


class TestHttpError:
    """Test suite for the HttpError class."""
    
    def test_init_basic(self):
        """Test HttpError initialization."""
        error = HttpError("Test error", ["Detail 1", "Detail 2"])
        assert error.message == "Test error"
        assert error.errors == ["Detail 1", "Detail 2"]
    
    def test_init_without_errors(self):
        """Test HttpError initialization without errors."""
        error = HttpError("Test error")
        assert error.message == "Test error"
        assert error.errors == []
    
    def test_from_json(self):
        """Test HttpError creation from JSON data."""
        data = {
            "message": "Validation failed",
            "errors": ["Field required", "Invalid format"]
        }
        error = HttpError.from_json(data)
        assert error.message == "Validation failed"
        assert error.errors == ["Field required", "Invalid format"]
    
    def test_from_json_minimal(self):
        """Test HttpError creation from minimal JSON data."""
        data = {}
        error = HttpError.from_json(data)
        assert error.message == "Unknown error"
        assert error.errors == []
    
    def test_str_representation(self):
        """Test string representation of HttpError."""
        error = HttpError("Main error", ["Detail 1", "Detail 2"])
        assert str(error) == "Main error: Detail 1, Detail 2"
        
        error_no_details = HttpError("Main error")
        assert str(error_no_details) == "Main error"
    
    def test_repr_representation(self):
        """Test repr representation of HttpError."""
        error = HttpError("Test error", ["Detail"])
        expected = "HttpError(message='Test error', errors=['Detail'])"
        assert repr(error) == expected


if __name__ == "__main__":
    pytest.main([__file__]) 