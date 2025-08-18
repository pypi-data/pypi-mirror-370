import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import base64

from contextbase import Contextbase, ContextbaseFile
from contextbase.http_response import ContextbaseResponse
from contextbase.publish import publish


class TestFileUpload:
    """Test suite for file upload functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, content: str, filename: str = "test.txt") -> Path:
        """Helper to create a test file."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    
    def create_binary_test_file(self, content: bytes, filename: str = "test.bin") -> Path:
        """Helper to create a binary test file."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_with_file_object(self, mock_post):
        """Test publishing with ContextbaseFile object (recommended way)."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "file123", "status": "uploaded"}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        # Create ContextbaseFile object
        content = "Hello, ContextbaseFile object!"
        file_obj = ContextbaseFile.from_data(content, "hello.txt")
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.publish(
            context_name="test-context",
            file=file_obj
        )
        
        # Verify
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        assert call_args[0][0] == "/v1/contexts/test-context/data"
        
        file_data = call_args[1]["data"]["file"]
        assert file_data["name"] == "hello.txt"
        assert file_data["mime_type"] == "text/plain"
        
        # Decode and verify content
        decoded_content = base64.b64decode(file_data["base64"]).decode('utf-8')
        assert decoded_content == content
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_with_file_from_path(self, mock_post):
        """Test publishing with ContextbaseFile created from path."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "file456"}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        # Create test file and ContextbaseFile object
        test_content = "ContextbaseFile from path test"
        file_path = self.create_test_file(test_content, "path_test.txt")
        file_obj = ContextbaseFile.from_path(file_path)
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.publish(
            context_name="test-context",
            file=file_obj
        )
        
        # Verify
        call_args = mock_post.call_args
        file_data = call_args[1]["data"]["file"]
        assert file_data["name"] == "path_test.txt"
        assert file_data["mime_type"] == "text/plain"
        
        decoded_content = base64.b64decode(file_data["base64"]).decode('utf-8')
        assert decoded_content == test_content
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_file_convenience_method_with_path(self, mock_post):
        """Test publish_file convenience method with file path."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "convenience123"}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        # Create test file
        content = "Convenience method with file path"
        file_path = self.create_test_file(content, "convenience.txt")
        
        client = Contextbase(api_key="test-key")
        
        # Execute using convenience method with file path
        response = client.publish_file(
            context_name="test-context",
            file_path=file_path,
            scopes={"type": "test"}
        )
        
        # Verify
        call_args = mock_post.call_args
        data = call_args[1]["data"]
        
        assert data["scopes"] == {"type": "test"}
        assert "file" in data
        assert "body" not in data
        
        file_data = data["file"]
        assert file_data["name"] == "convenience.txt"
        
        # Verify content was read correctly
        decoded_content = base64.b64decode(file_data["base64"]).decode('utf-8')
        assert decoded_content == content
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_binary_file_with_file_object(self, mock_post):
        """Test publishing a binary file using ContextbaseFile object."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "binary123"}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        # Create binary ContextbaseFile object
        binary_content = b'\x89PNG\r\n\x1a\n'  # PNG file header
        file_obj = ContextbaseFile.from_data(binary_content, "test.png")
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.publish(
            context_name="test-context",
            file=file_obj
        )
        
        # Verify
        call_args = mock_post.call_args
        file_data = call_args[1]["data"]["file"]
        assert file_data["name"] == "test.png"
        assert file_data["mime_type"] == "image/png"
        
        # Decode and verify binary content
        decoded_content = base64.b64decode(file_data["base64"])
        assert decoded_content == binary_content
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_file_unknown_mime_type(self, mock_post):
        """Test handling of files with unknown MIME types."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "unknown123"}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        # Create ContextbaseFile with unknown extension
        test_content = "Unknown file type"
        file_obj = ContextbaseFile.from_data(test_content, "test.unknownext")
        
        client = Contextbase(api_key="test-key")
        
        # Execute
        response = client.publish(
            context_name="test-context",
            file=file_obj
        )
        
        # Verify fallback MIME type
        call_args = mock_post.call_args
        file_data = call_args[1]["data"]["file"]
        assert file_data["mime_type"] == "text/plain"  # Default for string content
    
    @patch('contextbase.http_client.HttpClient.post')
    def test_publish_file_from_constructor(self, mock_post):
        """Test publishing with ContextbaseFile created using constructor."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "constructor123"}
        mock_post.return_value = ContextbaseResponse(mock_response)
        
        client = Contextbase(api_key="test-key")
        
        # Create ContextbaseFile using constructor
        content = "Constructor content"
        base64_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        file_obj = ContextbaseFile(
            name="constructor.txt",
            mime_type="text/plain",
            base64_content=base64_content
        )
        
        response = client.publish(
            context_name="test-context",
            file=file_obj
        )
        
        # Verify
        call_args = mock_post.call_args
        file_data = call_args[1]["data"]["file"]
        assert file_data["name"] == "constructor.txt"
        assert file_data["mime_type"] == "text/plain"
        assert file_data["base64"] == base64_content
    
    def test_contextbase_file_not_found_error(self):
        """Test error handling when ContextbaseFile.from_path() file doesn't exist."""
        with pytest.raises(ValueError, match="File not found"):
            ContextbaseFile.from_path("/nonexistent/file.txt")
    
    def test_contextbase_file_is_directory_error(self):
        """Test error handling when ContextbaseFile.from_path() path is a directory."""
        with pytest.raises(ValueError, match="Path is not a file"):
            ContextbaseFile.from_path(self.temp_dir)
    
    def test_publish_invalid_file_type(self):
        """Test error handling for invalid file types."""
        client = Contextbase(api_key="test-key")
        
        with pytest.raises(ValueError, match="File must be a ContextbaseFile object"):
            client.publish(
                context_name="test-context",
                file=123  # Invalid type
            )
    
    def test_publish_with_string_path_fails(self):
        """Test that passing a string path now fails (no longer supported)."""
        client = Contextbase(api_key="test-key")
        
        with pytest.raises(ValueError, match="File must be a ContextbaseFile object"):
            client.publish(
                context_name="test-context",
                file="/some/path.txt"
            )
    
    def test_publish_with_dict_fails(self):
        """Test that passing a dict now fails (no longer supported)."""
        client = Contextbase(api_key="test-key")
        
        file_dict = {
            "mime_type": "text/plain",
            "base64": base64.b64encode(b"content").decode('utf-8'),
            "name": "test.txt"
        }
        
        with pytest.raises(ValueError, match="File must be a ContextbaseFile object"):
            client.publish(
                context_name="test-context",
                file=file_dict
            )


class TestFileUploadDecorator:
    """Test suite for file upload decorator functionality."""
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_as_file_string_content(self, mock_contextbase_class):
        """Test decorator with as_file=True for string content."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate function
        @publish('reports', 'daily-summary', as_file=True, file_name='summary.txt')
        def generate_report():
            return "Daily summary: All systems operational"
        
        # Execute
        result = generate_report()
        
        # Verify function result
        assert result == "Daily summary: All systems operational"
        
        # Verify file was published with ContextbaseFile object
        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args
        
        assert call_args[1]["context_name"] == "reports"
        
        # Check that a ContextbaseFile object was passed
        file_arg = call_args[1]["file"]
        assert isinstance(file_arg, ContextbaseFile)
        assert file_arg.name == "summary.txt"
        assert file_arg.mime_type == "text/plain"
        
        # Verify content
        decoded = file_arg.get_content().decode('utf-8')
        assert decoded == "Daily summary: All systems operational"
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_as_file_binary_content(self, mock_contextbase_class):
        """Test decorator with as_file=True for binary content."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate function
        @publish('data', 'binary-output', as_file=True, file_name='output.bin')
        def generate_binary():
            return b'\x89PNG\r\n\x1a\n'  # PNG header
        
        # Execute
        result = generate_binary()
        
        # Verify ContextbaseFile object was created and used
        call_args = mock_client.publish.call_args
        file_arg = call_args[1]["file"]
        
        assert isinstance(file_arg, ContextbaseFile)
        assert file_arg.name == "output.bin"
        assert file_arg.mime_type == "application/octet-stream"
        
        decoded = file_arg.get_content()
        assert decoded == b'\x89PNG\r\n\x1a\n'
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_as_file_auto_filename(self, mock_contextbase_class):
        """Test decorator with as_file=True using automatic filename."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate function without explicit file_name
        @publish('reports', 'auto-file', as_file=True)
        def create_report():
            return "Auto-generated report content"
        
        # Execute
        result = create_report()
        
        # Verify automatic filename
        call_args = mock_client.publish.call_args
        file_arg = call_args[1]["file"]
        
        assert isinstance(file_arg, ContextbaseFile)
        assert file_arg.name == "create_report_output.txt"


if __name__ == "__main__":
    pytest.main([__file__]) 