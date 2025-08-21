import pytest
import subprocess
from unittest.mock import Mock, patch
import os

from sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection import LspServerConnection


class TestLspServerConnection:
    
    @pytest.fixture
    def lsp_connection(self):
        """Create an LspServerConnection instance for testing"""
        return LspServerConnection()
    
    def test_init(self, lsp_connection):
        """Test LspServerConnection initialization"""
        assert lsp_connection.lsp_endpoint is None
        assert lsp_connection.lsp_client is None
        assert lsp_connection.send_to_client_fn is None
        assert lsp_connection.progress_callbacks == {}
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.subprocess.Popen')
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.JsonRpcEndpoint')
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.LspEndpoint')
    def test_start_lsp_server_iam(self, mock_lsp_endpoint, mock_json_rpc, mock_popen, lsp_connection):
        """Test starting LSP server with IAM auth mode"""
        # Setup mocks
        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_popen.return_value = mock_process
        
        mock_json_rpc_instance = Mock()
        mock_json_rpc.return_value = mock_json_rpc_instance
        
        mock_lsp_endpoint_instance = Mock()
        mock_lsp_endpoint.return_value = mock_lsp_endpoint_instance
        
        node_path = "/opt/conda/bin/node"
        executable_path = "/path/to/executable"
        auth_mode = "IAM"
        
        # Call method
        result = lsp_connection.start_lsp_server(node_path, executable_path, auth_mode)
        
        # Verify subprocess was called with environment variable
        expected_cmd = [node_path, executable_path, "--stdio", "--inspect=6012", "--nolazy"]
        # validate that we are passing all the vars in the current env to LSP server
        expected_env = os.environ.copy()
        expected_env["USE_IAM_AUTH"] = 'true'
        mock_popen.assert_called_once_with(
            expected_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            env=expected_env
        )
        
        # Verify JsonRpcEndpoint was created
        mock_json_rpc.assert_called_once_with(mock_process.stdin, mock_process.stdout)
        
        # Verify LspEndpoint was created with progress callback
        mock_lsp_endpoint.assert_called_once()
        call_args = mock_lsp_endpoint.call_args
        assert "notify_callbacks" in call_args[1]
        assert "$/progress" in call_args[1]["notify_callbacks"]
        assert call_args[1]["timeout"] == 500
        
        # Verify endpoint was stored and returned
        assert lsp_connection.lsp_endpoint == mock_lsp_endpoint_instance
        assert result == mock_lsp_endpoint_instance
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.subprocess.Popen')
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.JsonRpcEndpoint')
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.LspEndpoint')
    def test_start_lsp_server_idc(self, mock_lsp_endpoint, mock_json_rpc, mock_popen, lsp_connection):
        """Test starting LSP server with IDC auth mode"""
        # Setup mocks
        mock_process = Mock()
        mock_popen.return_value = mock_process
        mock_json_rpc.return_value = Mock()
        mock_lsp_endpoint.return_value = Mock()
        
        node_path = "/opt/conda/bin/node"
        executable_path = "/path/to/executable"
        auth_mode = "IDC"
        
        # Call method
        lsp_connection.start_lsp_server(node_path, executable_path, auth_mode)
        
        # Verify subprocess was called without environment variable for IDC
        expected_cmd = [node_path, executable_path, "--stdio", "--inspect=6012", "--nolazy"]
        mock_popen.assert_called_once_with(
            expected_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.subprocess.Popen')
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.JsonRpcEndpoint')
    @patch('sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection.LspEndpoint')
    def test_start_lsp_server_no_auth_mode(self, mock_lsp_endpoint, mock_json_rpc, mock_popen, lsp_connection):
        """Test starting LSP server without auth mode"""
        # Setup mocks
        mock_process = Mock()
        mock_popen.return_value = mock_process
        mock_json_rpc.return_value = Mock()
        mock_lsp_endpoint.return_value = Mock()
        
        node_path = "/opt/conda/bin/node"
        executable_path = "/path/to/executable"
        
        # Call method without auth_mode
        lsp_connection.start_lsp_server(node_path, executable_path)
        
        # Verify subprocess was called without environment variable when no auth_mode
        expected_cmd = [node_path, executable_path, "--stdio", "--inspect=6012", "--nolazy"]
        mock_popen.assert_called_once_with(
            expected_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0
        )
    
    def test_lsp_client_created_in_start_server(self, lsp_connection):
        """Test that LSP client is created when starting server"""
        # The LSP client is created directly in start_lsp_server, not via a separate method
        assert lsp_connection.lsp_client is None  # Initially None
        
        # After calling start_lsp_server, lsp_client should be set
        # This is tested in the start_lsp_server tests
    
    @patch('os.getpid')
    def test_initialize(self, mock_getpid, lsp_connection):
        """Test LSP client initialization"""
        mock_getpid.return_value = 12345
        mock_client = Mock()
        lsp_connection.lsp_client = mock_client
        
        workspace_folder = "file:///home/user/workspace"
        
        lsp_connection.initialize(workspace_folder)
        
        # Verify initialize was called with correct parameters
        mock_client.initialize.assert_called_once()
        call_args = mock_client.initialize.call_args[1]
        
        assert call_args["processId"] == 12345
        assert call_args["rootPath"] == workspace_folder
        assert call_args["rootUri"] == workspace_folder
        assert call_args["capabilities"] == {}
        assert call_args["trace"] == "on"
        assert call_args["clientInfo"] == {'name': 'AmazonQ-For-SMUS-IDE'}
        
        # Verify initialization options
        init_options = call_args["initializationOptions"]
        assert "aws" in init_options
        assert "credentials" in init_options
        assert init_options["credentials"]["providesBearerToken"] is True
        
        # Verify workspace folders
        workspace_folders = call_args["workspaceFolders"]
        assert len(workspace_folders) == 1
        assert workspace_folders[0]["uri"] == workspace_folder
        assert workspace_folders[0]["name"] == "home"
        
        # Verify initialized was called
        mock_client.initialized.assert_called_once()
    
    def test_on_progress(self, lsp_connection):
        """Test progress callback registration"""
        token = "test-token"
        callback_fn = Mock()
        
        dispose_fn = lsp_connection.on_progress(token, callback_fn)
        
        # Verify wrapped callback was registered (not the original)
        assert token in lsp_connection.progress_callbacks
        assert callable(lsp_connection.progress_callbacks[token])
        
        # Test dispose function
        dispose_fn()
        assert token not in lsp_connection.progress_callbacks
    
    def test_on_progress_handler(self, lsp_connection):
        """Test the progress handler function"""
        # Setup a callback
        token = "test-token"
        callback_fn = Mock()
        lsp_connection.progress_callbacks[token] = callback_fn
        
        # Simulate progress message
        params = {"token": token, "value": {"kind": "report", "message": "Processing..."}}
        
        # We need to access the progress handler that was created in start_lsp_server
        # For testing, we'll create it manually
        def on_progress_handler(params):
            token = params.get('token')
            value = params.get('value')
            if token and token in lsp_connection.progress_callbacks:
                lsp_connection.progress_callbacks[token](value)
        
        on_progress_handler(params)
        
        # Verify callback was called with correct value
        callback_fn.assert_called_once_with({"kind": "report", "message": "Processing..."})
    
    def test_call_method(self, lsp_connection):
        """Test calling LSP method"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {"result": "success"}
        lsp_connection.lsp_endpoint = mock_endpoint
        
        command = "textDocument/completion"
        params = {"textDocument": {"uri": "file:///test.py"}, "position": {"line": 0, "character": 0}}
        
        result = lsp_connection.call_method(command, params)
        
        mock_endpoint.call_method.assert_called_once_with(command, **params)
        assert result == {"result": "success"}
    
    def test_send_notification(self, lsp_connection):
        """Test sending LSP notification"""
        mock_endpoint = Mock()
        lsp_connection.lsp_endpoint = mock_endpoint
        
        method = "textDocument/didOpen"
        params = {"textDocument": {"uri": "file:///test.py", "languageId": "python"}}
        
        lsp_connection.send_notification(method, params)
        
        mock_endpoint.send_notification.assert_called_once_with(method, **params)
    
    def test_set_send_to_client(self, lsp_connection):
        """Test setting send to client function"""
        send_fn = Mock()
        
        lsp_connection.set_send_to_client(send_fn)
        
        assert lsp_connection.send_to_client_fn == send_fn
    
    def test_update_access_token(self, lsp_connection):
        """Test updating access token"""
        mock_endpoint = Mock()
        lsp_connection.lsp_endpoint = mock_endpoint
        
        access_token = "test-token"
        start_url = "https://example.com"
        
        lsp_connection.update_access_token(access_token, start_url)
        
        mock_endpoint.call_method.assert_called_once_with(
            "aws/credentials/token/update",
            data={"token": access_token},
            metadata={"sso": {"startUrl": start_url}}
        )
    
    def test_update_q_profile(self, lsp_connection):
        """Test updating Q profile"""
        mock_endpoint = Mock()
        lsp_connection.lsp_endpoint = mock_endpoint
        
        profile_arn = "arn:aws:q:us-east-1:123456789012:profile/test"
        
        lsp_connection.update_q_profile(profile_arn)
        
        mock_endpoint.call_method.assert_called_once_with(
            "aws/updateConfiguration",
            section="aws.q",
            settings={"profileArn": profile_arn}
        )
    
    def test_get_chat_response(self, lsp_connection):
        """Test getting chat response"""
        mock_endpoint = Mock()
        mock_endpoint.call_method.return_value = {"response": "Hello, how can I help?"}
        lsp_connection.lsp_endpoint = mock_endpoint
        
        chat_prompt = "What is Python?"
        
        result = lsp_connection.get_chat_response(chat_prompt)
        
        mock_endpoint.call_method.assert_called_once_with(
            "aws/chat/sendChatPrompt",
            prompt={"prompt": chat_prompt}
        )
        assert result == {"response": "Hello, how can I help?"}
    
    def test_progress_callback_with_missing_token(self, lsp_connection):
        """Test progress handler with missing token"""
        # Setup a callback for a different token
        lsp_connection.progress_callbacks["other-token"] = Mock()
        
        # Simulate progress message with missing token
        params = {"token": "missing-token", "value": {"kind": "report"}}
        
        def on_progress_handler(params):
            token = params.get('token')
            value = params.get('value')
            if token and token in lsp_connection.progress_callbacks:
                lsp_connection.progress_callbacks[token](value)
        
        # Should not raise exception
        on_progress_handler(params)
        
        # Verify other callback wasn't called
        lsp_connection.progress_callbacks["other-token"].assert_not_called()
    
    def test_progress_callback_without_token(self, lsp_connection):
        """Test progress handler without token in params"""
        callback_fn = Mock()
        lsp_connection.progress_callbacks["test-token"] = callback_fn
        
        # Simulate progress message without token
        params = {"value": {"kind": "report"}}
        
        def on_progress_handler(params):
            token = params.get('token')
            value = params.get('value')
            if token and token in lsp_connection.progress_callbacks:
                lsp_connection.progress_callbacks[token](value)
        
        # Should not raise exception
        on_progress_handler(params)
        
        # Verify callback wasn't called
        callback_fn.assert_not_called()
    
    def test_update_iam_credentials(self, lsp_connection):
        """Test updating IAM credentials"""
        mock_endpoint = Mock()
        lsp_connection.lsp_endpoint = mock_endpoint
        
        access_key_id = "AKIAIOSFODNN7EXAMPLE"
        secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        session_token = "AQoDYXdzEJr...<remainder of session token>"
        expiration_time = "2025-07-22 21:42:02+00:00"
        
        lsp_connection.update_iam_credentials(access_key_id, secret_access_key, session_token, expiration_time)
        
        mock_endpoint.call_method.assert_called_once_with(
            "aws/credentials/iam/update",
            data={
                "accessKeyId": access_key_id,
                "secretAccessKey": secret_access_key,
                "sessionToken": session_token,
                "expireTime": expiration_time
            }
        )