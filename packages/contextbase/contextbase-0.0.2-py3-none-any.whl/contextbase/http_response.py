from .http_error import HttpError
from typing import Optional, Dict, Any

class ContextbaseResponse:
    """
    Wrapper around HTTP responses for Contextbase API calls.
    
    This class provides a pythonic interface for handling API responses,
    with methods for checking success/failure and accessing response data.
    """

    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.status_code = raw_response.status_code
        self._json_data = None
        self._parsed = False

    @property
    def json(self) -> Optional[Dict[str, Any]]:
        """Return the parsed JSON response data."""
        if not self._parsed:
            try:
                self._json_data = self.raw_response.json()
            except (ValueError, AttributeError):
                self._json_data = None
            self._parsed = True
        return self._json_data

    @property
    def text(self) -> str:
        """Return the raw response text."""
        return self.raw_response.text

    @property
    def headers(self) -> Dict[str, str]:
        """Return the response headers."""
        return dict(self.raw_response.headers)

    @property
    def ok(self) -> bool:
        """Check if the request was successful (2xx status codes)."""
        return 200 <= self.status_code < 300

    @property
    def is_success(self) -> bool:
        """Alias for ok property."""
        return self.ok

    def raise_for_status(self) -> None:
        """
        Raise an exception if the response indicates an error.
        
        Raises:
            ContextbaseError: If the response status indicates an error
        """
        if not self.ok:
            error = self.error
            if error:
                raise ContextbaseError(error.message, status_code=self.status_code, errors=error.errors)
            else:
                raise ContextbaseError(
                    f"HTTP {self.status_code}: {self.raw_response.reason}",
                    status_code=self.status_code
                )

    @property
    def error(self) -> Optional[HttpError]:
        """
        Return error information if the response failed.
        
        Returns:
            HttpError if the response failed, None if successful
        """
        if self.ok:
            return None
        
        if self.json:
            return HttpError.from_json(self.json)
        
        # Fallback error when no JSON data available
        return HttpError(
            message=f"HTTP {self.status_code}: {self.raw_response.reason}",
            errors=[]
        )
    
    @property
    def errors(self) -> list:
        """
        Return error information if the response failed.
        
        Returns:
            List of errors, if any
        """
        error = self.error
        if error:
            return error.errors
        return []
    
    @property
    def message(self) -> Optional[str]:
        """
        Return the error message if the response failed.
        
        Returns:
            Error message if the response failed, None if successful
        """
        error = self.error
        if error:
            return error.message
        return self.get('message')

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the JSON response data.
        
        Args:
            key: The key to look up in the response data
            default: Default value if key not found
            
        Returns:
            The value associated with the key, or default
        """
        if self.json:
            return self.json.get(key, default)
        return default

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to response data."""
        if self.json is None:
            raise KeyError(f"No JSON data in response or key '{key}' not found")
        return self.json[key]

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the response data."""
        return self.json is not None and key in self.json

    def __bool__(self) -> bool:
        """Return True if the response was successful."""
        return self.ok

    def __str__(self) -> str:
        status = "SUCCESS" if self.ok else "FAILED"
        return f"ContextbaseResponse({status}, {self.status_code})"

    def __repr__(self) -> str:
        return self.__str__()


class ContextbaseError(Exception):
    """Exception raised for Contextbase API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, errors: Optional[list] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
    
    def __str__(self) -> str:
        if self.status_code:
            return f"HTTP {self.status_code}: {self.message}"
        return self.message