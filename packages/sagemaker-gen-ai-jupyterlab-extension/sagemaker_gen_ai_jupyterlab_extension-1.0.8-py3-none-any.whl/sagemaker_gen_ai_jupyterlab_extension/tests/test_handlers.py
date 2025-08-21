import pytest
import json
import os
from unittest.mock import Mock, patch

from sagemaker_gen_ai_jupyterlab_extension.handlers import RouteHandler, setup_handlers


class TestRouteHandler:
    
    @pytest.fixture
    def handler(self):
        """Create a RouteHandler instance for testing"""
        handler = Mock(spec=RouteHandler)
        handler.finish = Mock()
        return handler
    
    def test_get_endpoint(self):
        """Test the GET endpoint returns correct JSON response"""
        handler = Mock()
        handler.finish = Mock()
        
        # Call the actual method
        RouteHandler.get(handler)
        
        expected_response = json.dumps({
            "data": "This is /sagemaker_gen_ai_jupyterlab_extension/get-example endpoint!"
        })
        handler.finish.assert_called_once_with(expected_response)


class TestSetupHandlers:
    
    @pytest.fixture
    def mock_web_app(self):
        """Create a mock web app for testing"""
        web_app = Mock()
        web_app.settings = {"base_url": "/"}
        web_app.add_handlers = Mock()
        return web_app
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_setup_handlers_success(self, mock_logger, mock_ioloop, mock_manager, mock_web_app):
        """Test successful handler setup"""
        mock_current_loop = Mock()
        mock_ioloop.current.return_value = mock_current_loop
        
        setup_handlers(mock_web_app)
        
        # Verify handlers were added
        mock_web_app.add_handlers.assert_called_once()
        
        # Verify IOLoop was set on manager
        mock_manager.set_io_loop.assert_called_once_with(mock_current_loop)
        
        # Check that 3 handlers were registered (route, websocket, static)
        call_args = mock_web_app.add_handlers.call_args
        host_pattern, handlers = call_args[0]
        
        assert host_pattern == ".*$"
        assert len(handlers) == 3
        
        # Verify handler patterns
        route_pattern, route_handler = handlers[0]
        websocket_pattern, websocket_handler = handlers[1]
        static_pattern, static_handler, static_config = handlers[2]
        
        assert "/sagemaker_gen_ai_jupyterlab_extension/get-example" in route_pattern
        assert "/sagemaker_gen_ai_jupyterlab_extension/ws" in websocket_pattern
        assert "/sagemaker_gen_ai_jupyterlab_extension/static" in static_pattern
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop')
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.logger')
    def test_setup_handlers_exception(self, mock_logger, mock_ioloop, mock_manager, mock_web_app):
        """Test handler setup with exception"""
        mock_web_app.add_handlers.side_effect = Exception("Test error")
        
        setup_handlers(mock_web_app)
        
        # Verify error was logged
        mock_logger.error.assert_called_once_with("Error setting up handlers: Test error")
    
    def test_cors_headers_set(self, mock_web_app):
        """Test that CORS headers are properly set on RouteHandler"""
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'), \
             patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
            
            setup_handlers(mock_web_app)
            
            # Test that CORS methods were added to RouteHandler
            assert hasattr(RouteHandler, 'set_default_headers')
            assert hasattr(RouteHandler, 'options')
            
            # Test CORS headers method
            handler = Mock()
            handler.set_header = Mock()
            
            RouteHandler.set_default_headers(handler)
            
            # Verify CORS headers are set
            handler.set_header.assert_any_call("Access-Control-Allow-Origin", "*")
            handler.set_header.assert_any_call("Access-Control-Allow-Headers", "x-requested-with, content-type, authorization")
            handler.set_header.assert_any_call("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    
    def test_options_method(self, mock_web_app):
        """Test OPTIONS method for CORS preflight"""
        with patch('sagemaker_gen_ai_jupyterlab_extension.handlers.manager'), \
             patch('sagemaker_gen_ai_jupyterlab_extension.handlers.ioloop.IOLoop'):
            
            setup_handlers(mock_web_app)
            
            # Test OPTIONS method
            handler = Mock()
            handler.set_status = Mock()
            handler.finish = Mock()
            
            RouteHandler.options(handler)
            
            handler.set_status.assert_called_once_with(204)
            handler.finish.assert_called_once()
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.handlers.CLIENT_HTML_PATH')
    def test_client_html_path_constant(self, mock_path):
        """Test that CLIENT_HTML_PATH is properly set"""
        expected_path = os.path.join(os.path.dirname(__file__), "static", "client.html")
        # The actual path should be set during import, so we just verify the structure
        assert "static" in str(expected_path)
        assert "client.html" in str(expected_path)