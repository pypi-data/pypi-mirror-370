import pytest
from unittest.mock import Mock, patch
from contextbase.publish import publish
from contextbase.http_response import ContextbaseError


class TestPublishDecorator:
    """Test suite for the @publish decorator."""
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_basic_functionality(self, mock_contextbase_class):
        """Test that decorator publishes function result."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context')
        def sample_function(x, y):
            return {"result": x + y}
        
        # Execute
        result = sample_function(1, 2)
        
        # Verify function result is returned
        assert result == {"result": 3}
        
        # Verify Contextbase was called correctly
        mock_contextbase_class.assert_called_once()
        mock_client.publish.assert_called_once_with(
            context_name='test-context',
            scopes=None,
            body={"result": 3}
        )
        mock_response.raise_for_status.assert_not_called()  # raise_on_error=False by default
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_static_scopes(self, mock_contextbase_class):
        """Test decorator with static scopes."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        static_scopes = {"environment": "test", "version": "1.0"}
        
        @publish('test-context', scopes=static_scopes)
        def sample_function():
            return {"data": "test"}
        
        # Execute
        result = sample_function()
        
        # Verify
        assert result == {"data": "test"}
        mock_client.publish.assert_called_once_with(
            context_name='test-context',
            scopes=static_scopes,
            body={"data": "test"}
        )
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_dynamic_scopes(self, mock_contextbase_class):
        """Test decorator with dynamic scopes (callable)."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Dynamic scopes function
        def dynamic_scopes(result):
            return {"user_id": result["user_id"], "action_type": result["action"]}
        
        @publish('user-data', scopes=dynamic_scopes)
        def update_user_preferences(user_id, preferences):
            return {
                "user_id": user_id,
                "action": "update_preferences",
                "preferences": preferences,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        
        # Execute
        result = update_user_preferences(123, {"theme": "dark"})
        
        # Verify function result is returned
        expected_result = {
            "user_id": 123,
            "action": "update_preferences", 
            "preferences": {"theme": "dark"},
            "timestamp": "2024-01-15T10:30:00Z"
        }
        assert result == expected_result
        
        # Verify dynamic scopes were computed and used
        expected_scopes = {"user_id": 123, "action_type": "update_preferences"}
        mock_client.publish.assert_called_once_with(
            context_name='user-data',
            scopes=expected_scopes,
            body=expected_result
        )
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_dynamic_scopes_lambda(self, mock_contextbase_class):
        """Test decorator with dynamic scopes using lambda."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        @publish('analytics', scopes=lambda result: {"user_id": result["user_id"]})
        def track_event(user_id, event_type):
            return {"user_id": user_id, "event": event_type, "timestamp": "2024-01-15T10:30:00Z"}
        
        # Execute
        result = track_event(456, "login")
        
        # Verify
        expected_result = {"user_id": 456, "event": "login", "timestamp": "2024-01-15T10:30:00Z"}
        assert result == expected_result
        
        # Verify lambda scopes were computed
        expected_scopes = {"user_id": 456}
        mock_client.publish.assert_called_once_with(
            context_name='analytics',
            scopes=expected_scopes,
            body=expected_result
        )
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_static_file_name(self, mock_contextbase_class):
        """Test decorator with static file name."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        @publish('reports', as_file=True, file_name="report.txt")
        def generate_report():
            return "Daily report content"
        
        # Execute
        result = generate_report()
        
        # Verify
        assert result == "Daily report content"
        
        # Verify file was created with correct name
        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args
        
        assert call_args.kwargs['context_name'] == 'reports'
        assert call_args.kwargs['scopes'] is None
        
        # Check the file object
        file_obj = call_args.kwargs['file']
        assert file_obj.name == "report.txt"
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_dynamic_file_name(self, mock_contextbase_class):
        """Test decorator with dynamic file name (callable)."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Create a simple dynamic file name function
        call_count = [0]  # Use list to modify from inner function
        
        def dynamic_file_name():
            call_count[0] += 1
            return f"backup_{call_count[0]}.sql"
        
        @publish(
            'backups', 
            'database',
            as_file=True,
            file_name=dynamic_file_name
        )
        def backup_database():
            return "SQL DUMP CONTENT"
        
        # Execute
        result = backup_database()
        
        # Verify
        assert result == "SQL DUMP CONTENT"
        
        # Verify dynamic file name was computed
        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args
        
        assert call_args.kwargs['context_name'] == 'backups'
        
        # Check the file object has dynamic name
        file_obj = call_args.kwargs['file']
        assert file_obj.name == "backup_1.sql"
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_default_file_name(self, mock_contextbase_class):
        """Test decorator uses function name as default file name."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        @publish('reports', 'generated', as_file=True)
        def create_user_report():
            return "User report content"
        
        # Execute
        result = create_user_report()
        
        # Verify
        assert result == "User report content"
        
        # Verify default file name was used
        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args
        
        file_obj = call_args.kwargs['file']
        assert file_obj.name == "create_user_report_output.txt"
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_combined_dynamic_features(self, mock_contextbase_class):
        """Test decorator with both dynamic scopes and dynamic file names."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        @publish(
            'user-reports',
            as_file=True,
            scopes=lambda result: {"user_id": 456},  # Simplified - just use hardcoded value
            file_name=lambda: "user_report_456.pdf"
        )
        def generate_user_report(user_id):
            return "PDF content as string"  # Return simple string instead of dict
        
        # Execute
        result = generate_user_report(456)
        
        # Verify
        expected_result = "PDF content as string"
        assert result == expected_result
        
        # Verify both dynamic features worked
        mock_client.publish.assert_called_once()
        call_args = mock_client.publish.call_args
        
        assert call_args.kwargs['context_name'] == 'user-reports'
        assert call_args.kwargs['scopes'] == {"user_id": 456}
        
        file_obj = call_args.kwargs['file']
        assert file_obj.name == "user_report_456.pdf"
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_error_handling_with_dynamic_scopes(self, mock_contextbase_class):
        """Test error handling still works with dynamic scopes."""
        # Setup - simulate API error
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = ContextbaseError("API Error", 500)
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        @publish(
            'test-context', 
            scopes=lambda result: {"computed": result["value"] * 2},
            raise_on_error=True
        )
        def failing_function():
            return {"value": 10}
        
        # Execute and verify exception is raised
        with pytest.raises(ContextbaseError):
            failing_function()
        
        # Verify dynamic scopes were still computed before error
        mock_client.publish.assert_called_once_with(
            context_name='test-context',
            scopes={"computed": 20},  # 10 * 2
            body={"value": 10}
        )
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_preserves_function_metadata(self, mock_contextbase_class):
        """Test that decorator preserves original function's metadata."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context')
        def sample_function(x: int, y: int) -> dict:
            """This is a sample function that adds two numbers."""
            return {"result": x + y}
        
        # Verify metadata is preserved
        assert sample_function.__name__ == "sample_function"
        assert "sample function that adds two numbers" in sample_function.__doc__
        
        # Verify function still works
        result = sample_function(5, 3)
        assert result == {"result": 8}
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_with_complex_function_arguments(self, mock_contextbase_class):
        """Test decorator with function that has various argument types."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function with various argument types
        @publish('test-context')
        def complex_function(pos_arg, *args, kwarg_with_default="default", **kwargs):
            return {
                "pos_arg": pos_arg,
                "args": args,
                "kwarg_with_default": kwarg_with_default,
                "kwargs": kwargs
            }
        
        # Execute with various arguments
        result = complex_function(
            "first", 
            "second", 
            "third", 
            kwarg_with_default="custom",
            extra_kwarg="extra"
        )
        
        # Verify result
        expected_result = {
            "pos_arg": "first",
            "args": ("second", "third"),
            "kwarg_with_default": "custom",
            "kwargs": {"extra_kwarg": "extra"}
        }
        assert result == expected_result
        
        # Verify the result was published
        mock_client.publish.assert_called_once_with(
            context_name='test-context',
            scopes=None,
            body=expected_result
        )


if __name__ == "__main__":
    pytest.main([__file__]) 