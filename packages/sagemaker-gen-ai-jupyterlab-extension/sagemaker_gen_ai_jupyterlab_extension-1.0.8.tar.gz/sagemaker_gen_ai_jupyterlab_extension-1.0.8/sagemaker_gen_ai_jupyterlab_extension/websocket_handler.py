import json
import asyncio
import logging
import os

from sagemaker_gen_ai_jupyterlab_extension.constants import Q_UNSUBSCRIBED_MESSAGE, INTERAL_SERVER_ERROR_MESSAGE
from .websocket_manager import manager
from tornado.websocket import WebSocketHandler
from uuid import uuid4
from typing import Optional
from .extract_utils import extract_q_enabled_status, FilePaths
from .file_watcher import FileWatcher

# Configure logging
logger = logging.getLogger('SageMakerGenAIJupyterLabExtension.websocket')

class WebSocketHandler(WebSocketHandler):
    def initialize(self):
        self.active_requests = {}
        self.active_tasks = set()
        self.chat_stream_tokens = {}
        self.q_enabled_file_watcher = None
        
    def open(self):
        logger.info(f"WebSocket connection opened: {self.request.remote_ip}")
        self.q_enabled = extract_q_enabled_status()
        logger.info(f"Q enabled in websocket open: {self.q_enabled}")
        
        # Start file watcher for Q enabled status
        self._start_q_enabled_file_watcher()
        
        manager.add_connection(self)
        from . import get_lsp_connection
        # initialize LSP server if not done
        if not get_lsp_connection():
            logger.info("LSP connection not set yet, initializing LSP server in websocket open")
            from . import initialize_lsp_server
            initialize_lsp_server()
        
        # Set callbacks on the connection
        lsp_conn = get_lsp_connection()
        if lsp_conn:
            lsp_conn.set_send_to_client(manager.broadcast)
        else:
            logger.warning("LSP connection not available during WebSocket open")
    
    def _start_q_enabled_file_watcher(self):
        """Start file watcher for Q enabled status file"""
        try:
            directory = os.path.expanduser("~/.aws/amazon_q")
            filename = 'settings.json'
            
            self.q_enabled_file_watcher = FileWatcher()
            self.q_enabled_file_watcher.start_watching(directory, filename, self._on_q_enabled_changed, recursive=False)
            logger.info(f"Started Q enabled status file watcher for: {directory}/{filename}")
        except Exception as e:
            logger.error(f"Failed to start Q enabled status file watcher: {e}")
    
    def _on_q_enabled_changed(self):
        """Callback when Q enabled status file changes"""
        try:
            old_status = self.q_enabled
            new_status = extract_q_enabled_status()
            if old_status != new_status:
                self.q_enabled = new_status
                logger.info(f"Q enabled status changed: {old_status} -> {new_status}")
        except Exception as e:
            logger.error(f"Error updating Q enabled status: {e}")
    
    async def on_message(self, event):
        try:
            message = json.loads(event)
            message_id = message.get('id')
            command = message.get('command')
            if not self.q_enabled:
                logger.info("Q currently not enabled")
                self.send_error_response(message_id, command, Q_UNSUBSCRIBED_MESSAGE)
                return
            logger.info(f"Received message: {command} (id: {message_id})")
            # Process message in background task to avoid blocking
            asyncio.create_task(self._process_message(message))
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            self.send_error_response(None, "unknown", f"Invalid JSON: {str(e)}")
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            # Extract ID if possible for error response
            try:
                message_dict = json.loads(event)
                message_id = message_dict.get('id')
                command = message_dict.get('command', 'unknown')
                self.send_error_response(message_id, command, str(e))
            except:
                logger.error("Could not extract message ID for error response")
                
    async def _process_message(self, message):
        """Process message in a separate task to avoid blocking the WebSocket handler"""
        task = asyncio.current_task()
        if task:
            self.active_tasks.add(task)
            
        try:
            await self.handle_inbound_event(message)
        except Exception as e:
            logger.exception(f"Error in background task: {e}")
            message_id = message.get('id')
            command = message.get('command', 'unknown')
            if message_id:
                self.send_error_response(message_id, command, str(e))
        finally:
            # Clean up task reference
            if task and task in self.active_tasks:
                self.active_tasks.remove(task)

    def send_error_response(self, message_id: Optional[str], command: str, error_message: str):
        """Send an error response for a failed request"""
        if message_id:
            error_response = {
                "id": message_id,
                "command": command,
                "error": error_message
            }
            manager.broadcast(json.dumps(error_response))
            logger.info(f"Sent error response for {command} (id: {message_id})")

    async def handle_inbound_event(self, message):
        from . import lsp_connection
        if not lsp_connection:
            logger.error("LSP connection not available")
            self.send_error_response(
                message.get('id'), 
                message.get('command', 'unknown'), 
                "LSP connection not available"
            )
            return
        id = message.get('id')
        command = message.get('command')
        params = message.get('params', {})
        tabId = message.get('tabId')
        logger.info(f"Processing command: {command}")
    
        try:
            match(command):
                case 'aws/chat/ready':
                    # refresh credentials on each page load 
                    from . import get_credential_manager
                    credential_manager = get_credential_manager()
                    if credential_manager:
                        credential_manager.handle_tier_change()
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/sendChatPrompt':
                    await self.handle_chat_prompt(lsp_connection, id, command, params, tabId)
                case 'aws/chat/buttonClick':
                    await self.handle_button_click(lsp_connection, id, command, params, tabId)
                case 'aws/chat/listMcpServers':
                    await self.handle_list_mcp_servers(lsp_connection, id, command, params, tabId)
                case 'aws/chat/mcpServerClick':
                    await self.handle_mcp_server_click(lsp_connection, id, command, params, tabId)
                case 'aws/chat/listConversations':
                    await self.list_conversations(lsp_connection, id, command, params, tabId)
                case 'aws/chat/conversationClick':
                    await self.conversation_click(lsp_connection, id, command, params, tabId)
                case 'aws/chat/tabAdd':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/openTab':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/tabChange':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/tabRemove':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/listRules':
                    await self.list_rules(lsp_connection, id, command, params, tabId)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/pinnedContextAdd':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/pinnedContextRemove':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                case 'aws/chat/createPrompt':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/fileClick':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'errorMessage':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'stopChatResponse':
                    self.handle_stop_chat_response(lsp_connection, id, command, params)
                    logger.info(f"Sent notification: {command}")
                case 'workspace/didChangeConfiguration':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/promptInputOptionChange':
                    await asyncio.to_thread(lsp_connection.send_notification, command, params)
                    logger.debug(f"Sent notification: {command}")
                case 'aws/chat/sendChatQuickAction':
                    await self.handle_chat_quick_action(lsp_connection, id, command, params, tabId)
                case 'ping':
                    response = {
                        "command": command,
                        "result": "pong"
                    }
                    manager.broadcast(json.dumps(response))
                case _:
                    logger.warning(f"Unhandled command: {command}")
                    if id:
                        self.send_error_response(id, command, f"Unsupported command: {command}")
        except Exception as e:
            logger.exception(f"Error handling command {command}: {e}")
            self.send_error_response(id, command, f"Error: {str(e)}")

    async def handle_chat_prompt(self, lsp_connection, id, command, params, tabId):
        """Handle chat prompt requests with streaming responses and cancellation support."""
        from .cancellation_token import CancellationTokenSource
        import time
        
        # User is sending a chat prompt, so we're no longer in startup mode
        if hasattr(lsp_connection, 'is_startup'):
            lsp_connection.is_startup = False
        
        if not tabId:
            self.send_error_response(id, command, "Missing tabId")
            return
            
        partial_result_token = str(uuid4())
        logger.debug(f"Starting chat prompt {id} with token: {partial_result_token}")
        
        # Setup cancellation tracking
        cancellation_token_source = CancellationTokenSource()
        last_partial_result = None
        
        self._store_chat_session(tabId, cancellation_token_source, lsp_connection.lsp_endpoint.next_id)
        
        def send_chat_update(partial_results):
            nonlocal last_partial_result
            if cancellation_token_source.token.isCancellationRequested:
                return
                
            last_partial_result = partial_results
            self._broadcast_partial_result(command, partial_results, tabId)

        dispose = None
        try:
            # Register progress handler
            dispose = await asyncio.to_thread(
                lsp_connection.on_progress, 
                partial_result_token, 
                send_chat_update,
                cancellation_token_source.token
            )
            
            # Make LSP call
            response = await asyncio.to_thread(
                lsp_connection.lsp_endpoint.call_method, 
                command, 
                **{**params, "partialResultToken": partial_result_token}
            )
            
            # Check for re-auth response and modify if needed
            if (response and isinstance(response, dict) and 
                response.get('followUp', {}).get('options')):
                for option in response['followUp']['options']:
                    if option.get('type') == 're-auth':
                        self.send_error_response(id, command, Q_UNSUBSCRIBED_MESSAGE)
                        break
            
            # Check for 500 error response
            if (response and isinstance(response, dict) and 
                response.get('error', {}).get('code') == 500):
                error_message = response.get('error', {}).get('message', 'Internal server error')
                logger.error(f"Server error in chat prompt {id}: {error_message}")
                self.send_error_response(id, command, INTERAL_SERVER_ERROR_MESSAGE)
                return

            # Handle response or cancellation
            self._send_success_response(id, command, tabId, response)

                
        except Exception as e:
            logger.exception(f"Error in chat prompt {id}: {e}")
            self.send_error_response(id, command, str(e))
        finally:
            self._cleanup_chat_session(tabId, dispose)
    
    def _store_chat_session(self, tab_id, token_source, lsp_request_id):
        """Store chat session for cancellation tracking."""
        self.chat_stream_tokens[tab_id] = {
            'token_source': token_source,
            'lsp_request_id': lsp_request_id
        }
        logger.debug(f"Stored session for tab {tab_id} with LSP ID {lsp_request_id}")
    
    def _broadcast_partial_result(self, command, partial_results, tab_id):
        """Broadcast partial result to client."""
        try:
            manager.broadcast({
                "command": command,
                "params": partial_results,
                "tabId": tab_id,
                "isPartialResult": True,
            })
        except Exception as e:
            logger.error(f"Error broadcasting partial result: {e}")
    
    def _send_success_response(self, id, command, tab_id, response):
        """Send successful chat response."""
        result = {
            "id": id,
            "command": command,
            "params": response,
            "tabId": tab_id
        }
        manager.broadcast(json.dumps(result))
        logger.info(f"Completed chat prompt: {id}")
    
    def _cleanup_chat_session(self, tab_id, dispose):
        """Clean up chat session resources."""
        if dispose:
            try:
                dispose()
            except Exception as e:
                logger.error(f"Error disposing progress handler: {e}")
        
        if tab_id in self.chat_stream_tokens:
            del self.chat_stream_tokens[tab_id]

    async def handle_button_click(self, lsp_connection, id, command, params, tabId):
        """Handle button click requests"""
        logger.info(f"Processing button click: {params.get('buttonId', 'unknown')}")
        
        try:
            response = await asyncio.to_thread(lsp_connection.call_method, command, params)
            
            # Send success response
            result = {
                "id": id,
                "command": command,
                "params": response,
                "tabId": tabId
            }
            manager.broadcast(json.dumps(result))
            logger.info(f"Button click processed successfully")
        except Exception as e:
            logger.exception(f"Button click error: {e}")
            self.send_error_response(id, command, str(e))

    async def handle_list_mcp_servers(self, lsp_connection, id, command, params, tabId):
        """Handle list MCP servers requests"""
        logger.info(f"Listing MCP servers")
        
        try:
            response = await asyncio.to_thread(lsp_connection.call_method, command, params)
            
            # Send success response
            result = {
                "id": id,
                "command": command,
                "params": response,
                "tabId": tabId
            }
            manager.broadcast(json.dumps(result))
            logger.info(f"Listed MCP servers successfully")
        except Exception as e:
            logger.exception(f"List MCP servers error: {e}")
            self.send_error_response(id, command, str(e))

    async def handle_chat_quick_action(self, lsp_connection, id, command, params, tabId):
        """Handle chat quick actions"""
        logger.info(f"Handling chat quick action")
        
        try:
            response = await asyncio.to_thread(lsp_connection.call_method, command, params)
 
            result = {
                "id": id,
                "command": command,
                "params": response,
                "tabId": tabId
            }
            
            manager.broadcast(json.dumps(result))
            logger.info(f"Handled Chat Quick Action successfully")
        except Exception as e:
            logger.exception(f"Handle Chat Quick Action error: {e}")
            self.send_error_response(id, command, str(e))
 
    async def handle_mcp_server_click(self, lsp_connection, id, command, params, tabId):
        """Handle MCP server click requests"""
        logger.info(f"Processing MCP server click")
        
        try:
            response = await asyncio.to_thread(lsp_connection.call_method, command, params)
            
            # Send success response
            result = {
                "id": id,
                "command": command,
                "params": response,
                "tabId": tabId
            }
            manager.broadcast(json.dumps(result))
            logger.info(f"MCP server click processed successfully")
        except Exception as e:
            logger.exception(f"MCP server click error: {e}")
            self.send_error_response(id, command, str(e))
    
    async def list_conversations(self, lsp_connection, id, command, params, tabId):
        """Handle list conversation requests"""
        logger.info(f"Listing conversations")
        
        try:
            response = await asyncio.to_thread(lsp_connection.call_method, command, params)
            
            # Send success response
            result = {
                "id": id,
                "command": command,
                "params": response,
                "tabId": tabId
            }
            manager.broadcast(json.dumps(result))
            logger.info(f"Listed conversations successfully")
        except Exception as e:
            logger.exception(f"List conversations error: {e}")
            self.send_error_response(id, command, str(e))

    async def list_rules(self, lsp_connection, id, command, params, tabId):
        """Handle list rules request"""
        logger.info(f"Listing rules")
        
        try:
            response = await asyncio.to_thread(lsp_connection.call_method, command, params)
            
            # Send success response
            result = {
                "id": id,
                "command": command,
                "params": response,
                "tabId": tabId
            }
            manager.broadcast(json.dumps(result))
            logger.info(f"Listed rules successfully")
        except Exception as e:
            logger.exception(f"List rules error: {e}")
            self.send_error_response(id, command, str(e))

    async def conversation_click(self, lsp_connection, id, command, params, tabId):
        """Handle conversation click requests"""
        logger.info(f"Processing conversation click")
        
        try:
            # User clicked on a conversation, so we're no longer in startup mode
            if hasattr(lsp_connection, 'is_startup'):
                lsp_connection.is_startup = False
                
            response = await asyncio.to_thread(lsp_connection.call_method, command, params)
            
            # Send success response
            result = {
                "id": id,
                "command": command,
                "params": response,
                "tabId": tabId
            }
            manager.broadcast(json.dumps(result))
            logger.info(f"Conversation click processed successfully")
        except Exception as e:
            logger.exception(f"Conversation click error: {e}")
            self.send_error_response(id, command, str(e))

    def on_close(self):
        logger.info(f"WebSocket connection closed: {self.request.remote_ip}")
        
        # Stop Q enabled status file watcher
        if self.q_enabled_file_watcher:
            try:
                self.q_enabled_file_watcher.stop_watching()
                logger.info("Stopped Q enabled status file watcher")
            except Exception as e:
                logger.error(f"Error stopping Q enabled status file watcher: {e}")
        
        # Cancel any running tasks when connection closes
        for task in list(self.active_tasks):
            if not task.done():
                logger.info(f"Cancelling task {task}")
                task.cancel()
        
        manager.remove_connection(self)

    def check_origin(self, origin):
        # Only allow connections from the same origin as the server
        server_origin = self.request.host
        client_origin = origin.replace("http://", "").replace("https://", "")
        logger.info(f"Origin check - Client origin: {client_origin}, Server origin: {server_origin}")
        return client_origin == server_origin
    
    def handle_stop_chat_response(self, lsp_connection, id, command, params):
        tab_id = params.get('tabId')
        logger.debug(f'Cancelling chat response for {tab_id}')
        if tab_id in self.chat_stream_tokens:
            token_info = self.chat_stream_tokens[tab_id]
            token_source = token_info['token_source']
            
            # Cancel token
            token_source.cancel()
            # Send $/cancelRequest to LSP server
            lsp_request_id = token_info.get('lsp_request_id')
            if lsp_request_id:
                try:
                    asyncio.create_task(
                        asyncio.to_thread(
                            lsp_connection.send_notification,
                            "$/cancelRequest",
                            {"id": lsp_request_id}
                        )
                    )
                    logger.info(f"Sent $/cancelRequest for LSP request: {lsp_request_id}")
                except Exception as e:
                    logger.error(f"Error sending $/cancelRequest: {e}")
            
            # Remove from tracking
            del self.chat_stream_tokens[tab_id]
            logger.info(f"Cancelled chat for tab: {tab_id}")
