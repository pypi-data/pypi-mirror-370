from .contextbase import Contextbase
from .file import ContextbaseFile
from functools import wraps
from typing import Dict, Any, Optional, Callable, TypeVar, Union

# Type variable for the decorated function
F = TypeVar('F', bound=Callable[..., Any])

def publish(
    context_name: str, 
    scopes: Optional[Union[Dict[str, Any], Callable[[Any], Dict[str, Any]]]] = None, 
    raise_on_error: bool = False,
    as_file: bool = False,
    file_name: Optional[Union[str, Callable[[], str]]] = None
) -> Callable[[F], F]:
    """
    Decorator factory for publishing function results to Contextbase.

    This decorator automatically publishes the return value of a function
    to a specified Contextbase context after the function executes.

    Args:
        context_name: Name of the context to publish to
        scopes: Optional scoping information for the published data. Can be:
                - A dictionary of static scopes
                - A callable that takes the function result and returns scopes dict
        raise_on_error: If True, raises ContextbaseError on API failures.
                       If False, silently continues on API errors.
        as_file: If True, treats the return value as file content and uploads it as a file.
                When True, the function should return bytes or str content.
        file_name: Name for the file when as_file=True. Can be:
                  - A string for static file name
                  - A callable that returns a string for dynamic file names
                  - If not provided, uses "{function_name}_output.txt"

    Returns:
        Decorator function that wraps the original function

    Example:
        >>> @publish('prediction-service', raise_on_error=True)
        ... def predict(features):
        ...     return {"prediction": 0.95, "confidence": 0.87}
        ...
        >>> result = predict([1, 2, 3])  # Function runs normally
        >>> # Result is automatically published to Contextbase
        
    Example with file output:
        >>> @publish(
        ...     context_name='daily_summary', 
        ...     as_file=True,
        ...     file_name='summary.txt'
        ... )
        ... def generate_report():
        ...     return "Daily Summary: Everything looks good!"
        ...
        >>> report = generate_report()  # Content uploaded as a file
        
    Example with static scopes:
        >>> @publish(
        ...     context_name='user_events',
        ...     scopes={'environment': 'production'},
        ...     raise_on_error=False
        ... )
        ... def track_user_action(user_id, action):
        ...     return {"user_id": user_id, "action": action, "timestamp": time.time()}
        
    Example with dynamic scopes:
        >>> @publish(
        ...     context_name='user_data',
        ...     scopes=lambda result: {"user_id": result["user_id"]},
        ...     raise_on_error=False
        ... )
        ... def update_user_preferences(user_id, preferences):
        ...     return {"user_id": user_id, "preferences": preferences}
        
    Example with dynamic file names:
        >>> from datetime import datetime
        >>> @publish(
        ...     context_name='backups',
        ...     as_file=True,
        ...     file_name=lambda: f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        ... )
        ... def backup_database():
        ...     return "SQL DUMP CONTENT"
    """

    def decorator(func: F) -> F:
        """The actual decorator that wraps the function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            try:
                cb = Contextbase()
                
                # resolve dynamic scopes
                resolved_scopes = scopes
                if callable(scopes):
                    resolved_scopes = scopes(result)
                
                if as_file:
                    # resolve dynamic file name
                    file_name_final = file_name
                    if callable(file_name):
                        file_name_final = file_name()
                    elif file_name_final is None:
                        file_name_final = f"{func.__name__}_output.txt"
                    
                    # Create ContextbaseFile object from function result
                    file_obj = ContextbaseFile.from_data(
                        content=result,
                        name=file_name_final
                    )
                    
                    response = cb.publish(
                        context_name=context_name,
                        file=file_obj,
                        scopes=resolved_scopes
                    )
                else:
                    response = cb.publish(
                        context_name=context_name,
                        scopes=resolved_scopes,
                        body=result
                    )
                
                if raise_on_error:
                    response.raise_for_status()
                    
            except Exception as e:
                if raise_on_error:
                    raise
                pass
            
            return result
            
        return wrapper  # type: ignore
    return decorator
