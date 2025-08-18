import pytest
import tempfile
import os
from pathlib import Path
import base64

from contextbase import ContextbaseFile


class TestContextbaseFile:
    """Test suite for ContextbaseFile class."""
    
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

    def test_file_from_path_text_file(self):
        """Test creating ContextbaseFile from text file path."""
        content = "Hello, world!"
        file_path = self.create_test_file(content, "hello.txt")
        
        file_obj = ContextbaseFile.from_path(file_path)
        
        assert file_obj.name == "hello.txt"
        assert file_obj.mime_type == "text/plain"
        assert file_obj.get_content() == content.encode('utf-8')
        assert file_obj.get_size() == len(content)
    
    def test_file_from_path_binary_file(self):
        """Test creating ContextbaseFile from binary file path."""
        content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR'  # PNG header
        file_path = self.create_binary_test_file(content, "image.png")
        
        file_obj = ContextbaseFile.from_path(file_path)
        
        assert file_obj.name == "image.png"
        assert file_obj.mime_type == "image/png"
        assert file_obj.get_content() == content
        assert file_obj.get_size() == len(content)
    
    def test_file_from_path_unknown_extension(self):
        """Test creating ContextbaseFile from file with unknown extension."""
        content = "Unknown file type"
        file_path = self.create_test_file(content, "unknown.unknownext")
        
        file_obj = ContextbaseFile.from_path(file_path)
        
        assert file_obj.name == "unknown.unknownext"
        assert file_obj.mime_type == "application/octet-stream"
        assert file_obj.get_content() == content.encode('utf-8')
    
    def test_file_from_path_nonexistent_file(self):
        """Test error when file doesn't exist."""
        with pytest.raises(ValueError, match="File not found"):
            ContextbaseFile.from_path("/nonexistent/file.txt")
    
    def test_file_from_path_directory(self):
        """Test error when path is a directory."""
        with pytest.raises(ValueError, match="Path is not a file"):
            ContextbaseFile.from_path(self.temp_dir)
    
    def test_file_from_data_string_content(self):
        """Test creating ContextbaseFile from string content."""
        content = "Hello, world!"
        file_obj = ContextbaseFile.from_data(content, "greeting.txt")
        
        assert file_obj.name == "greeting.txt"
        assert file_obj.mime_type == "text/plain"
        assert file_obj.get_content() == content.encode('utf-8')
        assert file_obj.get_size() == len(content)
    
    def test_file_from_data_bytes_content(self):
        """Test creating ContextbaseFile from bytes content."""
        content = b'\x89PNG\r\n\x1a\n'
        file_obj = ContextbaseFile.from_data(content, "image.png")
        
        assert file_obj.name == "image.png"
        assert file_obj.mime_type == "image/png"
        assert file_obj.get_content() == content
        assert file_obj.get_size() == len(content)
    
    def test_file_from_data_explicit_mime_type(self):
        """Test creating ContextbaseFile with explicit MIME type."""
        content = "Custom content"
        file_obj = ContextbaseFile.from_data(content, "custom.unknownext", mime_type="application/custom")
        
        assert file_obj.name == "custom.unknownext"
        assert file_obj.mime_type == "application/custom"
        assert file_obj.get_content() == content.encode('utf-8')
    
    def test_file_from_data_unknown_extension(self):
        """Test ContextbaseFile creation with unknown extension defaults."""
        content = "Unknown content"
        file_obj = ContextbaseFile.from_data(content, "unknown.unknownext")
        
        assert file_obj.name == "unknown.unknownext"
        assert file_obj.mime_type == "text/plain"  # Default for string content
        
        # Test with bytes
        binary_content = b"Binary unknown"
        file_obj2 = ContextbaseFile.from_data(binary_content, "unknown.unknownext")
        
        assert file_obj2.mime_type == "application/octet-stream"  # Default for bytes
    
    def test_to_dict(self):
        """Test converting ContextbaseFile to dictionary."""
        content = "Test content"
        file_obj = ContextbaseFile.from_data(content, "test.txt")
        
        result = file_obj.to_dict()
        
        expected_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        assert result == {
            "name": "test.txt",
            "mime_type": "text/plain",
            "base64": expected_base64
        }
    
    def test_file_equality(self):
        """Test ContextbaseFile equality comparison."""
        content = "Same content"
        
        file1 = ContextbaseFile.from_data(content, "test.txt")
        file2 = ContextbaseFile.from_data(content, "test.txt")
        file3 = ContextbaseFile.from_data("Different content", "test.txt")
        file4 = ContextbaseFile.from_data(content, "different.txt")
        
        assert file1 == file2
        assert file1 != file3
        assert file1 != file4
        assert file1 != "not a file"
    
    def test_file_string_representation(self):
        """Test ContextbaseFile string representations."""
        content = "Hello"
        file_obj = ContextbaseFile.from_data(content, "hello.txt", "text/plain")
        
        str_repr = str(file_obj)
        assert "hello.txt" in str_repr
        assert "text/plain" in str_repr
        assert "5 bytes" in str_repr  # len("Hello")
        assert "ContextbaseFile" in str_repr
        
        assert repr(file_obj) == str(file_obj)
    
    def test_file_direct_instantiation(self):
        """Test direct ContextbaseFile instantiation."""
        name = "direct.txt"
        mime_type = "text/plain"
        base64_content = base64.b64encode(b"Direct content").decode('utf-8')
        
        file_obj = ContextbaseFile(name, mime_type, base64_content)
        
        assert file_obj.name == name
        assert file_obj.mime_type == mime_type
        assert file_obj.base64_content == base64_content
        assert file_obj.get_content() == b"Direct content"
    
    def test_roundtrip_path_to_dict_to_constructor(self):
        """Test roundtrip: path -> ContextbaseFile -> dict -> ContextbaseFile."""
        original_content = "Roundtrip test content"
        file_path = self.create_test_file(original_content, "roundtrip.txt")
        
        # Path -> ContextbaseFile
        file1 = ContextbaseFile.from_path(file_path)
        
        # ContextbaseFile -> dict
        file_dict = file1.to_dict()
        
        # dict -> ContextbaseFile (using constructor)
        file2 = ContextbaseFile(
            name=file_dict['name'],
            mime_type=file_dict['mime_type'],
            base64_content=file_dict['base64']
        )
        
        # Verify they're equal
        assert file1 == file2
        assert file1.get_content() == file2.get_content() == original_content.encode('utf-8')
    
    def test_csv_file_mime_type_detection(self):
        """Test MIME type detection for CSV files."""
        csv_content = "name,age,city\nJohn,30,NYC\nJane,25,LA"
        file_obj = ContextbaseFile.from_data(csv_content, "data.csv")
        
        assert file_obj.mime_type == "text/csv"
    
    def test_json_file_mime_type_detection(self):
        """Test MIME type detection for JSON files."""
        json_content = '{"users": [{"id": 1, "name": "Alice"}]}'
        file_obj = ContextbaseFile.from_data(json_content, "data.json")
        
        assert file_obj.mime_type == "application/json"
    
    def test_pdf_file_mime_type_detection(self):
        """Test MIME type detection for PDF files."""
        # Create a minimal PDF-like binary content
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        file_path = self.create_binary_test_file(pdf_content, "document.pdf")
        
        file_obj = ContextbaseFile.from_path(file_path)
        
        assert file_obj.mime_type == "application/pdf"


if __name__ == "__main__":
    pytest.main([__file__]) 