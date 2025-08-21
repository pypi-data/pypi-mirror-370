import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from sagemaker_gen_ai_jupyterlab_extension.websocket_handler import WebSocketHandler


@pytest.fixture
def websocket_handler():
    with patch('sagemaker_gen_ai_jupyterlab_extension.websocket_handler.WebSocketHandler.__init__', return_value=None):
        handler = WebSocketHandler.__new__(WebSocketHandler)
        handler.initialize()
        return handler


@pytest.fixture
def mock_lsp_connection():
    mock = Mock()
    mock.send_notification = Mock()
    return mock


class TestChatReadyCommand:
    
    @pytest.mark.asyncio
    async def test_aws_chat_ready_calls_credential_manager(self, websocket_handler, mock_lsp_connection):
        """Test that aws/chat/ready command calls credential manager"""
        message = {
            "id": "test-id",
            "command": "aws/chat/ready",
            "params": {"test": "data"}
        }
        
        mock_credential_manager = Mock()
        with patch('sagemaker_gen_ai_jupyterlab_extension.get_credential_manager', return_value=mock_credential_manager):
            with patch('sagemaker_gen_ai_jupyterlab_extension.lsp_connection', mock_lsp_connection):
                with patch('asyncio.to_thread') as mock_to_thread:
                    mock_to_thread.return_value = None
                    
                    await websocket_handler.handle_inbound_event(message)
                    
                    # Verify credential manager handle_tier_change was called
                    mock_credential_manager.handle_tier_change.assert_called_once()
                    
                    # Verify LSP notification was sent
                    mock_to_thread.assert_called_once_with(
                        mock_lsp_connection.send_notification,
                        "aws/chat/ready",
                        {"test": "data"}
                    )
    
    @pytest.mark.asyncio
    async def test_aws_chat_ready_without_lsp_connection(self, websocket_handler):
        """Test aws/chat/ready when LSP connection is not available"""
        message = {
            "id": "test-id",
            "command": "aws/chat/ready",
            "params": {}
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.lsp_connection', None):
            with patch.object(websocket_handler, 'send_error_response') as mock_error:
                await websocket_handler.handle_inbound_event(message)
                
                # Should send error response when LSP connection unavailable
                mock_error.assert_called_once_with(
                    "test-id",
                    "aws/chat/ready", 
                    "LSP connection not available"
                )
    
    @pytest.mark.asyncio
    async def test_aws_chat_ready_no_credential_manager(self, websocket_handler, mock_lsp_connection):
        """Test aws/chat/ready when credential manager is not available"""
        message = {
            "id": "test-id",
            "command": "aws/chat/ready",
            "params": {}
        }
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.get_credential_manager', return_value=None):
            with patch('sagemaker_gen_ai_jupyterlab_extension.lsp_connection', mock_lsp_connection):
                with patch('asyncio.to_thread') as mock_to_thread:
                    mock_to_thread.return_value = None
                    
                    await websocket_handler.handle_inbound_event(message)
                    
                    # Should still send LSP notification even without credential manager
                    mock_to_thread.assert_called_once_with(
                        mock_lsp_connection.send_notification,
                        "aws/chat/ready",
                        {}
                    )
