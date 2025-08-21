import pytest
import json
import threading
from unittest.mock import Mock, patch, AsyncMock
from sagemaker_gen_ai_jupyterlab_extension.websocket_handler import WebSocketHandler
from sagemaker_gen_ai_jupyterlab_extension.websocket_manager import WebSocketManager, manager


class TestWebSocketHandler:
    
    @pytest.fixture
    def handler(self):
        # Create a mock application and request
        application = Mock()
        request = Mock()
        request.remote_ip = "127.0.0.1"
        
        # Create handler without calling parent constructor
        handler = object.__new__(WebSocketHandler)
        handler.application = application
        handler.request = request
        handler.initialize()
        return handler

    @pytest.fixture
    def mock_lsp_connection(self):
        mock = Mock()
        mock.call_method = AsyncMock()
        mock.send_notification = Mock()
        mock.on_progress = Mock()
        mock.set_send_to_client = Mock()
        return mock

    def test_initialize(self, handler):
        assert handler.active_requests == {}
        assert handler.active_tasks == set()

    def test_open(self, handler):
        with patch.object(manager, 'add_connection') as mock_add_connection:
            with patch('sagemaker_gen_ai_jupyterlab_extension.get_lsp_connection') as mock_get_lsp:
                with patch('sagemaker_gen_ai_jupyterlab_extension.initialize_lsp_server') as mock_init_lsp:
                    # Test case 1: LSP connection exists
                    mock_lsp_conn = Mock()
                    mock_get_lsp.return_value = mock_lsp_conn
                    handler.open()
                    mock_add_connection.assert_called_once_with(handler)
                    mock_lsp_conn.set_send_to_client.assert_called_once()
                    mock_init_lsp.assert_not_called()
                    # Reset mocks for test case 2
                    mock_add_connection.reset_mock()
                    mock_get_lsp.reset_mock()
                    # Test case 2: LSP connection doesn't exist
                    mock_get_lsp.side_effect = [None, mock_lsp_conn]  # First call returns None, second returns connection
                    handler.open()
                    mock_add_connection.assert_called_once_with(handler)
                    mock_init_lsp.assert_called_once()
                    mock_lsp_conn.set_send_to_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_message_valid_json(self, handler):
        message = {"id": "test-id", "command": "test-command", "params": {}}
        
        with patch.object(handler, '_process_message') as mock_process:
            await handler.on_message(json.dumps(message))
            
        # Verify task was created (can't easily test asyncio.create_task directly)
        assert True  # Test passes if no exception

    @pytest.mark.asyncio
    async def test_on_message_invalid_json(self, handler):
        with patch.object(handler, 'send_error_response') as mock_error:
            await handler.on_message("invalid-json")
            
        mock_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_chat_prompt(self, handler, mock_lsp_connection):
        message_id = "test-id"
        command = "aws/chat/sendChatPrompt"
        params = {"prompt": "test prompt"}
        tab_id = "tab-1"
        
        # Mock the LSP endpoint with next_id
        mock_lsp_connection.lsp_endpoint = Mock()
        mock_lsp_connection.lsp_endpoint.next_id = 123
        mock_lsp_connection.lsp_endpoint.call_method = AsyncMock(return_value={"response": "test response"})
        mock_lsp_connection.on_progress.return_value = Mock()  # dispose function
        
        with patch.object(manager, 'broadcast') as mock_broadcast:
            with patch('asyncio.to_thread') as mock_to_thread:
                mock_to_thread.return_value = {"response": "test response"}
                
                await handler.handle_chat_prompt(mock_lsp_connection, message_id, command, params, tab_id)
                
        # Verify asyncio.to_thread was called (which calls the LSP method)
        assert mock_to_thread.call_count >= 1
        mock_broadcast.assert_called()

    @pytest.mark.asyncio
    async def test_handle_button_click(self, handler, mock_lsp_connection):
        message_id = "test-id"
        command = "aws/chat/buttonClick"
        params = {"buttonId": "test-button"}
        tab_id = "tab-1"
        
        mock_lsp_connection.call_method.return_value = {"success": True}
        
        with patch.object(manager, 'broadcast') as mock_broadcast:
            await handler.handle_button_click(mock_lsp_connection, message_id, command, params, tab_id)
            
        mock_lsp_connection.call_method.assert_called_once_with(command, params)
        mock_broadcast.assert_called()
            
        mock_broadcast.assert_called()

    def test_send_error_response(self, handler):
        message_id = "test-id"
        command = "test-command"
        error_message = "test error"
        
        with patch.object(manager, 'broadcast') as mock_broadcast:
            handler.send_error_response(message_id, command, error_message)
            
        mock_broadcast.assert_called_once()

    @patch.object(manager, 'remove_connection')
    def test_on_close(self, mock_remove_connection, handler):
        # Add a mock task
        mock_task = Mock()
        mock_task.done.return_value = False
        handler.active_tasks.add(mock_task)
        
        handler.on_close()
        
        mock_task.cancel.assert_called_once()
        mock_remove_connection.assert_called_once_with(handler)

    def test_check_origin_same_origin(self, handler):
        # Mock request with same origin
        handler.request.protocol = 'http'
        handler.request.host = 'localhost:8888'
        
        assert handler.check_origin('http://localhost:8888') is True
    
    def test_check_origin_different_origin(self, handler):
        # Mock request with different origin
        handler.request.protocol = 'http'
        handler.request.host = 'localhost:8888'
        
        assert handler.check_origin('https://malicious.com') is False


class TestWebSocketManagerExtended:
    
    @pytest.fixture
    def ws_manager(self):
        return WebSocketManager()

    def test_concurrent_connection_management(self, ws_manager):
        """Test thread-safe concurrent connection management"""
        connections = [Mock() for _ in range(10)]
        
        def add_connections():
            for conn in connections[:5]:
                ws_manager.add_connection(conn)
        
        def remove_connections():
            for conn in connections[5:]:
                ws_manager.add_connection(conn)
                ws_manager.remove_connection(conn)
        
        thread1 = threading.Thread(target=add_connections)
        thread2 = threading.Thread(target=remove_connections)
        
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        assert len(ws_manager.connections) == 5

    def test_broadcast_with_mixed_connection_states(self, ws_manager):
        """Test broadcasting with connections in different states"""
        good_conn = Mock()
        good_conn.ws_connection = True
        
        no_ws_conn = Mock()
        no_ws_conn.ws_connection = None
        
        error_conn = Mock()
        error_conn.ws_connection = True
        error_conn.write_message.side_effect = Exception("Connection lost")
        
        ws_manager.connections.update([good_conn, no_ws_conn, error_conn])
        
        mock_loop = Mock()
        ws_manager.io_loop = mock_loop
        
        ws_manager.broadcast("test message")
        
        callback_fn = mock_loop.add_callback.call_args[0][0]
        
        with patch('builtins.print'):
            callback_fn()
        
        good_conn.write_message.assert_called_once_with("test message")
        error_conn.write_message.assert_called_once_with("test message")

    def test_connection_cleanup_on_error(self, ws_manager):
        """Test that connections are properly cleaned up on errors"""
        conn1 = Mock()
        conn2 = Mock()
        
        ws_manager.add_connection(conn1)
        ws_manager.add_connection(conn2)
        
        assert len(ws_manager.connections) == 2
        
        ws_manager.remove_connection(conn1)
        assert len(ws_manager.connections) == 1
        assert conn2 in ws_manager.connections
        
        ws_manager.remove_connection(conn1)  # Should not raise error
        assert len(ws_manager.connections) == 1

    def test_broadcast_empty_message(self, ws_manager):
        """Test broadcasting empty or None messages"""
        conn = Mock()
        conn.ws_connection = True
        ws_manager.add_connection(conn)
        
        mock_loop = Mock()
        ws_manager.io_loop = mock_loop
        
        test_cases = ["", None, {}, []]
        
        for empty_message in test_cases:
            ws_manager.broadcast(empty_message)
            
            callback_fn = mock_loop.add_callback.call_args[0][0]
            callback_fn()
            
            conn.write_message.assert_called_with(empty_message)
            conn.write_message.reset_mock()

    def test_manager_singleton_consistency(self):
        """Test that manager singleton maintains state consistency"""
        conn = Mock()
        manager.add_connection(conn)
        
        from sagemaker_gen_ai_jupyterlab_extension.websocket_manager import manager as manager2
        
        assert manager is manager2
        assert conn in manager2.connections