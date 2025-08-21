import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from sagemaker_gen_ai_jupyterlab_extension.websocket_handler import WebSocketHandler
from sagemaker_gen_ai_jupyterlab_extension.cancellation_token import CancellationTokenSource
from sagemaker_gen_ai_jupyterlab_extension.constants import Q_UNSUBSCRIBED_MESSAGE


@pytest.fixture
def websocket_handler():
    with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.WebSocketHandler.__init__', return_value=None):
        handler = WebSocketHandler.__new__(WebSocketHandler)
        handler.initialize()
        handler.q_enabled = True  # Default to enabled
        handler.send_error_response = Mock()
        handler.handle_chat_prompt = AsyncMock()
        handler.handle_button_click = AsyncMock()
        handler.handle_list_mcp_servers = AsyncMock()
        handler.handle_mcp_server_click = AsyncMock()
        handler.list_conversations = AsyncMock()
        handler.conversation_click = AsyncMock()
        handler.list_rules = AsyncMock()
        handler.handle_stop_chat_response = Mock()
        return handler


@pytest.fixture
def mock_lsp_connection():
    mock = Mock()
    mock.lsp_endpoint = Mock()
    mock.lsp_endpoint.next_id = 123
    mock.lsp_endpoint.call_method = AsyncMock(return_value={"result": "test"})
    mock.on_progress = Mock(return_value=lambda: None)
    mock.send_notification = Mock()
    return mock


class TestHandleChatPrompt:
    
    @pytest.mark.asyncio
    async def test_handle_chat_prompt_missing_tab_id(self, websocket_handler):
        """Test that missing tabId returns error"""
        with patch.object(websocket_handler, 'send_error_response') as mock_error:
            await websocket_handler.handle_chat_prompt(
                Mock(), "test-id", "aws/chat/sendChatPrompt", {}, None
            )
            mock_error.assert_called_once_with("test-id", "aws/chat/sendChatPrompt", "Missing tabId")
    
    @pytest.mark.asyncio
    async def test_handle_chat_prompt_success(self, websocket_handler, mock_lsp_connection):
        """Test successful chat prompt handling"""
        tab_id = "test-tab"
        message_id = "test-id"
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.manager') as mock_manager:
            with patch('asyncio.to_thread') as mock_to_thread:
                mock_to_thread.return_value = {"result": "test"}
                
                await websocket_handler.handle_chat_prompt(
                    mock_lsp_connection, message_id, "aws/chat/sendChatPrompt", 
                    {"prompt": "test"}, tab_id
                )
                
                # Verify LSP call was made
                assert mock_to_thread.call_count >= 1
                
                # Verify success response was sent
                mock_manager.broadcast.assert_called()


class TestChatSessionManagement:
    
    def test_store_chat_session(self, websocket_handler):
        """Test storing chat session for cancellation tracking"""
        tab_id = "test-tab"
        token_source = CancellationTokenSource()
        lsp_request_id = 123
        
        websocket_handler._store_chat_session(tab_id, token_source, lsp_request_id)
        
        assert tab_id in websocket_handler.chat_stream_tokens
        assert websocket_handler.chat_stream_tokens[tab_id]['token_source'] == token_source
        assert websocket_handler.chat_stream_tokens[tab_id]['lsp_request_id'] == lsp_request_id
    
    def test_cleanup_chat_session(self, websocket_handler):
        """Test cleaning up chat session resources"""
        tab_id = "test-tab"
        websocket_handler.chat_stream_tokens[tab_id] = {"test": "data"}
        
        mock_dispose = Mock()
        websocket_handler._cleanup_chat_session(tab_id, mock_dispose)
        
        mock_dispose.assert_called_once()
        assert tab_id not in websocket_handler.chat_stream_tokens


class TestBroadcastMethods:
    
    def test_broadcast_partial_result(self, websocket_handler):
        """Test broadcasting partial results"""
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.manager') as mock_manager:
            websocket_handler._broadcast_partial_result(
                "aws/chat/sendChatPrompt", {"data": "test"}, "test-tab"
            )
            
            mock_manager.broadcast.assert_called_once_with({
                "command": "aws/chat/sendChatPrompt",
                "params": {"data": "test"},
                "tabId": "test-tab",
                "isPartialResult": True,
            })
    
    def test_send_success_response(self, websocket_handler):
        """Test sending successful response"""
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.manager') as mock_manager:
            websocket_handler._send_success_response(
                "test-id", "aws/chat/sendChatPrompt", "test-tab", {"result": "success"}
            )
            
            expected_result = {
                "id": "test-id",
                "command": "aws/chat/sendChatPrompt",
                "params": {"result": "success"},
                "tabId": "test-tab"
            }
            mock_manager.broadcast.assert_called_once_with(json.dumps(expected_result))
    

class TestHandleInboundEvent:
    
    @pytest.mark.asyncio
    async def test_no_lsp_connection(self, websocket_handler):
        """Test error handling when LSP connection is not available"""
        message = {'id': 'test-id', 'command': 'test-command'}
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', None):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.send_error_response.assert_called_once_with(
            'test-id', 'test-command', 'LSP connection not available'
        )

    @pytest.mark.asyncio
    async def test_chat_prompt_command(self, websocket_handler, mock_lsp_connection):
        """Test aws/chat/sendChatPrompt command"""
        message = {
            'id': 'test-id',
            'command': 'aws/chat/sendChatPrompt',
            'params': {'prompt': 'test'},
            'tabId': 'tab-1'
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.handle_chat_prompt.assert_called_once_with(
            mock_lsp_connection, 'test-id', 'aws/chat/sendChatPrompt', {'prompt': 'test'}, 'tab-1'
        )

    @pytest.mark.asyncio
    async def test_button_click_command(self, websocket_handler, mock_lsp_connection):
        """Test aws/chat/buttonClick command"""
        message = {
            'id': 'test-id',
            'command': 'aws/chat/buttonClick',
            'params': {'button': 'test'},
            'tabId': 'tab-1'
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.handle_button_click.assert_called_once_with(
            mock_lsp_connection, 'test-id', 'aws/chat/buttonClick', {'button': 'test'}, 'tab-1'
        )

    @pytest.mark.asyncio
    async def test_list_mcp_servers_command(self, websocket_handler, mock_lsp_connection):
        """Test aws/chat/listMcpServers command"""
        message = {
            'id': 'test-id',
            'command': 'aws/chat/listMcpServers',
            'params': {},
            'tabId': 'tab-1'
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.handle_list_mcp_servers.assert_called_once_with(
            mock_lsp_connection, 'test-id', 'aws/chat/listMcpServers', {}, 'tab-1'
        )

    @pytest.mark.asyncio
    async def test_ready_command_with_credential_manager(self, websocket_handler, mock_lsp_connection):
        """Test aws/chat/ready command with credential manager"""
        message = {
            'command': 'aws/chat/ready',
            'params': {}
        }
        
        mock_credential_manager = Mock()
        mock_credential_manager.handle_tier_change = Mock()
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.get_credential_manager', return_value=mock_credential_manager):
                with patch('asyncio.to_thread') as mock_to_thread:
                    await websocket_handler.handle_inbound_event(message)
                    
        mock_credential_manager.handle_tier_change.assert_called_once()
        mock_to_thread.assert_called_once_with(mock_lsp_connection.send_notification, 'aws/chat/ready', {})

    @pytest.mark.asyncio
    async def test_notification_commands(self, websocket_handler, mock_lsp_connection):
        """Test commands that send notifications"""
        notification_commands = [
            'aws/chat/tabAdd',
            'aws/chat/openTab',
            'aws/chat/tabChange',
            'aws/chat/tabRemove',
            'aws/chat/pinnedContextAdd',
            'aws/chat/pinnedContextRemove',
            'aws/chat/createPrompt',
            'aws/chat/fileClick',
            'errorMessage',
            'workspace/didChangeConfiguration',
            'aws/chat/promptInputOptionChange'
        ]
        
        for command in notification_commands:
            message = {
                'command': command,
                'params': {'test': 'data'}
            }
            
            with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
                with patch('asyncio.to_thread') as mock_to_thread:
                    await websocket_handler.handle_inbound_event(message)
                    
            mock_to_thread.assert_called_with(mock_lsp_connection.send_notification, command, {'test': 'data'})
            mock_to_thread.reset_mock()

    @pytest.mark.asyncio
    async def test_stop_chat_response_command(self, websocket_handler, mock_lsp_connection):
        """Test stopChatResponse command"""
        message = {
            'id': 'test-id',
            'command': 'stopChatResponse',
            'params': {'test': 'data'}
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.handle_stop_chat_response.assert_called_once_with(
            mock_lsp_connection, 'test-id', 'stopChatResponse', {'test': 'data'}
        )

    @pytest.mark.asyncio
    async def test_unhandled_command_with_id(self, websocket_handler, mock_lsp_connection):
        """Test unhandled command with ID"""
        message = {
            'id': 'test-id',
            'command': 'unknown/command',
            'params': {}
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.send_error_response.assert_called_once_with(
            'test-id', 'unknown/command', 'Unsupported command: unknown/command'
        )

    @pytest.mark.asyncio
    async def test_exception_handling(self, websocket_handler, mock_lsp_connection):
        """Test exception handling in handle_inbound_event"""
        message = {
            'id': 'test-id',
            'command': 'aws/chat/sendChatPrompt',
            'params': {'prompt': 'test'},
            'tabId': 'tab-1'
        }
        
        # Make handle_chat_prompt raise an exception
        websocket_handler.handle_chat_prompt.side_effect = Exception("Test error")
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.send_error_response.assert_called_once_with(
            'test-id', 'aws/chat/sendChatPrompt', 'Error: Test error'
        )

    @pytest.mark.asyncio
    async def test_message_without_params(self, websocket_handler, mock_lsp_connection):
        """Test message without params field"""
        message = {
            'id': 'test-id',
            'command': 'aws/chat/sendChatPrompt',
            'tabId': 'tab-1'
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.lsp_connection', mock_lsp_connection):
            await websocket_handler.handle_inbound_event(message)
            
        websocket_handler.handle_chat_prompt.assert_called_once_with(
            mock_lsp_connection, 'test-id', 'aws/chat/sendChatPrompt', {}, 'tab-1'
        )


class TestQEnabledCheck:
    
    @pytest.mark.asyncio
    async def test_on_message_q_disabled(self, websocket_handler):
        """Test that messages are blocked when Q is disabled"""
        websocket_handler.q_enabled = False
        message = json.dumps({
            'id': 'test-id',
            'command': 'aws/chat/sendChatPrompt',
            'params': {'prompt': 'test'}
        })
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.logger') as mock_logger:
            await websocket_handler.on_message(message)
            
        mock_logger.info.assert_called_with("Q currently not enabled")
        websocket_handler.send_error_response.assert_called_once_with(
            'test-id', 'aws/chat/sendChatPrompt', Q_UNSUBSCRIBED_MESSAGE
        )
    
    @pytest.mark.asyncio
    async def test_on_message_q_enabled(self, websocket_handler):
        """Test that messages are processed when Q is enabled"""
        websocket_handler.q_enabled = True
        message = json.dumps({
            'id': 'test-id',
            'command': 'aws/chat/sendChatPrompt',
            'params': {'prompt': 'test'}
        })
        
        with patch('asyncio.create_task') as mock_create_task:
            with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.logger') as mock_logger:
                await websocket_handler.on_message(message)
                
        mock_logger.info.assert_called_with("Received message: aws/chat/sendChatPrompt (id: test-id)")
        mock_create_task.assert_called_once()
        websocket_handler.send_error_response.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_on_message_q_disabled_no_message_id(self, websocket_handler):
        """Test Q disabled handling when message has no ID"""
        websocket_handler.q_enabled = False
        message = json.dumps({
            'command': 'aws/chat/sendChatPrompt',
            'params': {'prompt': 'test'}
        })
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.logger') as mock_logger:
            await websocket_handler.on_message(message)
            
        mock_logger.info.assert_called_with("Q currently not enabled")
        websocket_handler.send_error_response.assert_called_once_with(
            None, 'aws/chat/sendChatPrompt', Q_UNSUBSCRIBED_MESSAGE
        )


class TestQEnabledFileWatcherUpdated:
    
    def test_on_q_enabled_changed_status_changes(self, websocket_handler):
        """Test Q enabled status change callback when status actually changes"""
        websocket_handler.q_enabled = False
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.extract_q_enabled_status', return_value=True) as mock_extract:
            with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.logger') as mock_logger:
                websocket_handler._on_q_enabled_changed()
                
                mock_extract.assert_called_once()
                assert websocket_handler.q_enabled is True
                mock_logger.info.assert_called_once_with("Q enabled status changed: False -> True")
    
    def test_on_q_enabled_changed_no_change(self, websocket_handler):
        """Test Q enabled status change callback when status doesn't change"""
        websocket_handler.q_enabled = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.extract_q_enabled_status', return_value=True) as mock_extract:
            with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.logger') as mock_logger:
                websocket_handler._on_q_enabled_changed()
                
                mock_extract.assert_called_once()
                assert websocket_handler.q_enabled is True
                mock_logger.info.assert_not_called()
    
    def test_on_q_enabled_changed_true_to_false(self, websocket_handler):
        """Test Q enabled status change from True to False"""
        websocket_handler.q_enabled = True
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.extract_q_enabled_status', return_value=False) as mock_extract:
            with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.logger') as mock_logger:
                websocket_handler._on_q_enabled_changed()
                
                mock_extract.assert_called_once()
                assert websocket_handler.q_enabled is False
                mock_logger.info.assert_called_once_with("Q enabled status changed: True -> False")
    
    def test_on_q_enabled_changed_false_to_false(self, websocket_handler):
        """Test Q enabled status remains False"""
        websocket_handler.q_enabled = False
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.extract_q_enabled_status', return_value=False) as mock_extract:
            with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.logger') as mock_logger:
                websocket_handler._on_q_enabled_changed()
                
                mock_extract.assert_called_once()
                assert websocket_handler.q_enabled is False
                mock_logger.info.assert_not_called()