from typing import Union, Dict, Any
from pathlib import Path
import base64
import mimetypes


class ContextbaseFile:
    """
    A file object for uploading to Contextbase.
    
    This class provides a clean interface for working with files, whether they're
    created from file paths or raw file data. It handles MIME type detection,
    base64 encoding, and validation automatically.
    
    Examples:
        >>> # From file path
        >>> file = ContextbaseFile.from_path("document.pdf")
        >>> 
        >>> # From file data
        >>> file = ContextbaseFile.from_data(
        ...     content=b"Hello World",
        ...     name="hello.txt",
        ...     mime_type="text/plain"
        ... )
        >>> 
        >>> # Using constructor
        >>> file = ContextbaseFile(
        ...     name="hello.txt",
        ...     mime_type="text/plain",
        ...     base64_content="SGVsbG8gV29ybGQ="
        ... )
    """
    
    def __init__(self, name: str, mime_type: str, base64_content: str):
        """
        Initialize a ContextbaseFile object.
        
        Args:
            name: The file name
            mime_type: The MIME type of the file
            base64_content: The base64-encoded file content
        """
        self.name = name
        self.mime_type = mime_type
        self.base64_content = base64_content
    
    @classmethod
    def from_path(cls, file_path: Union[str, Path]) -> 'ContextbaseFile':
        """
        Create a ContextbaseFile object from a file path.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            ContextbaseFile object ready for upload
            
        Raises:
            ValueError: If file doesn't exist or can't be read
            
        Example:
            >>> file = ContextbaseFile.from_path("report.pdf")
            >>> print(f"Uploading {file.name} ({file.mime_type})")
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
            
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            base64_content = base64.b64encode(file_content).decode('utf-8')

            mime_type, _ = mimetypes.guess_type(str(file_path))
            if mime_type is None:
                mime_type = 'application/octet-stream'

            return cls(
                name=file_path.name,
                mime_type=mime_type,
                base64_content=base64_content
            )

        except Exception as e:
            raise ValueError(f"Failed to read file {file_path}: {e}")

    @classmethod
    def from_data(
        cls, 
        content: Union[str, bytes], 
        name: str, 
        mime_type: str = None
    ) -> 'ContextbaseFile':
        """
        Create a ContextbaseFile object from raw content.
        
        Args:
            content: The file content as string or bytes
            name: The file name
            mime_type: Optional MIME type. If not provided, will be guessed from name
            
        Returns:
            ContextbaseFile object ready for upload
            
        Example:
            >>> file = ContextbaseFile.from_data(
            ...     content="Hello, world!",
            ...     name="greeting.txt"
            ... )
            >>> # MIME type automatically detected as text/plain
        """
        # convert content to bytes if it's a string
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content

        base64_content = base64.b64encode(content_bytes).decode('utf-8')
        
        # detect MIME type if not provided
        if mime_type is None:
            mime_type, _ = mimetypes.guess_type(name)
            if mime_type is None:
                if isinstance(content, str):
                    mime_type = 'text/plain'
                else:
                    mime_type = 'application/octet-stream'

        return cls(
            name=name,
            mime_type=mime_type,
            base64_content=base64_content
        )

    def to_dict(self) -> Dict[str, str]:
        """
        Convert the ContextbaseFile object to a dictionary for API requests.
        
        Returns:
            Dictionary with 'name', 'mime_type', and 'base64' keys
            
        Example:
            >>> file = ContextbaseFile.from_path("document.pdf")
            >>> api_data = file.to_dict()
            >>> # {'name': 'document.pdf', 'mime_type': 'application/pdf', 'base64': '...'}
        """
        return {
            'name': self.name,
            'mime_type': self.mime_type,
            'base64': self.base64_content
        }
    
    def get_content(self) -> bytes:
        """
        Get the decoded file content as bytes.
        
        Returns:
            The original file content as bytes
            
        Example:
            >>> file = ContextbaseFile.from_data("Hello world", "hello.txt")
            >>> content = file.get_content()
            >>> print(content.decode('utf-8'))  # "Hello world"
        """
        return base64.b64decode(self.base64_content)
    
    def get_size(self) -> int:
        """
        Get the file size in bytes.
        
        Returns:
            Size of the original file content in bytes
        """
        return len(self.get_content())

    def __str__(self) -> str:
        """String representation of the ContextbaseFile object."""
        size = self.get_size()
        return f"ContextbaseFile(name='{self.name}', mime_type='{self.mime_type}', size={size} bytes)"

    def __repr__(self) -> str:
        """Detailed string representation of the ContextbaseFile object."""
        return self.__str__()

    def __eq__(self, other) -> bool:
        """Check equality with another ContextbaseFile object."""
        if not isinstance(other, ContextbaseFile):
            return False
        return (
            self.name == other.name and
            self.mime_type == other.mime_type and
            self.base64_content == other.base64_content
        ) 