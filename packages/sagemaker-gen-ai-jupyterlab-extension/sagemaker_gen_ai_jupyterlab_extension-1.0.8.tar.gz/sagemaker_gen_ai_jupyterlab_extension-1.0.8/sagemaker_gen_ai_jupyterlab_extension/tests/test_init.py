from unittest.mock import Mock, patch, call
from pathlib import Path
import sys

# Mock watchdog before importing the module
with patch.dict('sys.modules', {
    'watchdog': Mock(),
    'watchdog.observers': Mock(),
    'watchdog.events': Mock()
}):
    # Import the module under test
    import sagemaker_gen_ai_jupyterlab_extension as init_module
    from sagemaker_gen_ai_jupyterlab_extension.extract_utils import AuthMode


class TestInitModule:
    
    def test_version_exists(self):
        """Test that version is set"""
        assert hasattr(init_module, '__version__')
        assert init_module.__version__ is not None

    def test_constants(self):
        """Test module constants are properly set"""
        assert init_module.NODE_PATH == "/opt/conda/bin/node"
        assert init_module.WORKSPACE_FOLDER == "file:///home/sagemaker-user"
        assert isinstance(init_module.PACKAGE_DIR, Path)
        # LSP_EXECUTABLE_PATH may be set by other tests, just check it exists
        assert hasattr(init_module, 'LSP_EXECUTABLE_PATH')

    # Token and settings extraction tests moved to test_extract_utils.py

    def test_jupyter_labextension_paths(self):
        """Test JupyterLab extension paths configuration"""
        paths = init_module._jupyter_labextension_paths()
        
        expected = [{
            "src": "labextension",
            "dest": "sagemaker_gen_ai_jupyterlab_extension"
        }]
        assert paths == expected

    def test_get_lsp_connection(self):
        """Test getting LSP connection"""
        # Mock the global lsp_connection
        mock_connection = Mock()
        with patch.object(init_module, 'lsp_connection', mock_connection):
            result = init_module.get_lsp_connection()
            assert result == mock_connection
    
    def test_get_credential_manager(self):
        """Test getting credential manager"""
        # Mock the global credential_manager
        mock_manager = Mock()
        with patch.object(init_module, 'credential_manager', mock_manager):
            result = init_module.get_credential_manager()
            assert result == mock_manager

    def test_chat_with_prompt(self):
        """Test chat with prompt function"""
        mock_connection = Mock()
        mock_connection.get_chat_response.return_value = {"response": "test"}
        
        with patch.object(init_module, 'get_lsp_connection', return_value=mock_connection):
            result = init_module.chat_with_prompt("test prompt")
            
            assert result == {"response": "test"}
            mock_connection.get_chat_response.assert_called_once_with("test prompt")

    
    def test_load_jupyter_server_extension_success(self):
        """Test successful loading of Jupyter server extension"""
        # Setup mocks
        mock_server_app = Mock()
        mock_server_app.web_app = Mock()
        mock_server_app.log = Mock()
        with patch('sagemaker_gen_ai_jupyterlab_extension.setup_handlers') as mock_setup:    
            # Call the function
            init_module._load_jupyter_server_extension(mock_server_app)
            # Verify calls
            mock_setup.assert_called_once_with(mock_server_app.web_app)
            

    def test_unload_jupyter_server_extension(self):
        """Test unloading Jupyter server extension"""
        # Create mocks
        mock_server_app = Mock()
        mock_cred_manager = Mock()
        mock_q_custom = Mock()
        
        with patch.object(init_module, 'credential_manager', mock_cred_manager):
            with patch.object(init_module, 'q_customization', mock_q_custom):
                # Call the function
                init_module._unload_jupyter_server_extension(mock_server_app)
                
                # Verify calls
                mock_cred_manager.cleanup.assert_called_once()
                mock_q_custom.stop_watcher_for_customization_file.assert_called_once()

    def test_unload_jupyter_server_extension_with_exception(self):
        """Test unloading Jupyter server extension with exception"""
        # Create mocks
        mock_server_app = Mock()
        mock_cred_manager = Mock()
        mock_cred_manager.cleanup.side_effect = Exception("Cleanup error")
        
        with patch.object(init_module, 'credential_manager', mock_cred_manager):
            with patch.object(init_module, 'logger') as mock_logger:
                # Call the function
                init_module._unload_jupyter_server_extension(mock_server_app)
                
                # Verify error was logged
                mock_logger.error.assert_called_with("Error cleaning up credential manager: Cleanup error")

    @patch('sagemaker_gen_ai_jupyterlab_extension.requests.get')
    def test_download_and_extract_lsp_server_success(self, mock_get):
        """Test successful LSP server download and extraction"""
        # Mock manifest response
        mock_manifest = {
            'versions': [{
                'serverVersion': init_module.FLARE_SERVER_VERSION,
                'targets': [{
                    'platform': 'linux',
                    'contents': [{
                        'filename': 'servers.zip',
                        'url': 'https://test.com/servers.zip'
                    }]
                }]
            }]
        }
        
        mock_response = Mock()
        mock_response.json.return_value = mock_manifest
        mock_response.content = b'fake zip content'
        mock_get.return_value = mock_response
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.tempfile.mkdtemp', return_value='/tmp/test'):
            with patch('sagemaker_gen_ai_jupyterlab_extension.zipfile.ZipFile'):
                with patch('sagemaker_gen_ai_jupyterlab_extension.os.walk', return_value=[('/tmp/test', [], ['aws-lsp-codewhisperer.js'])]):
                    with patch('builtins.open', create=True):
                        # Call the function
                        init_module.download_and_extract_lsp_server()
                        
                        # Verify LSP_EXECUTABLE_PATH was set
                        assert init_module.LSP_EXECUTABLE_PATH == '/tmp/test/aws-lsp-codewhisperer.js'