from typing import List, Dict, Any, Optional

class HttpError:
    """
    Represents an error response from the Contextbase API.
    
    Attributes:
        message: The main error message
        errors: List of detailed error messages
    """
    
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        """
        Initialize an HttpError.
        
        Args:
            message: The main error message
            errors: Optional list of detailed error messages
        """
        self.message = message
        self.errors = errors or []

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'HttpError':
        """
        Create an HttpError from JSON response data.
        
        Args:
            data: JSON response data containing error information
            
        Returns:
            HttpError instance
        """
        message = data.get('message', 'Unknown error')
        errors = data.get('errors', [])
        return cls(message=message, errors=errors)
        
    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.errors:
            return f"{self.message}: {', '.join(self.errors)}"
        return self.message
        
    def __repr__(self) -> str:
        """Return a detailed string representation of the error."""
        return f"HttpError(message='{self.message}', errors={self.errors})"
