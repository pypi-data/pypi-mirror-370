import pytest
import json
import tempfile
import os
import zipfile
from unittest.mock import Mock, patch, mock_open
from . import download_and_extract_lsp_server, MANIFEST_URL, FLARE_SERVER_VERSION


class TestDownloadAndExtractLspServer:
    
    @pytest.fixture
    def mock_manifest(self):
        return {
            "versions": [
                {
                    "serverVersion": FLARE_SERVER_VERSION,
                    "targets": [
                        {
                            "platform": "linux",
                            "contents": [
                                {
                                    "filename": "servers.zip",
                                    "url": "https://example.com/servers.zip"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    @pytest.fixture
    def mock_zip_content(self):
        # Create a temporary zip file with aws-lsp-codewhisperer.js
        temp_dir = tempfile.mkdtemp()
        js_file = os.path.join(temp_dir, 'aws-lsp-codewhisperer.js')
        with open(js_file, 'w') as f:
            f.write('// Mock LSP server')
        
        zip_path = os.path.join(temp_dir, 'test.zip')
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            zip_ref.write(js_file, 'aws-lsp-codewhisperer.js')
        
        with open(zip_path, 'rb') as f:
            return f.read()

    @patch('sagemaker_gen_ai_jupyterlab_extension.requests.get')
    @patch('sagemaker_gen_ai_jupyterlab_extension.tempfile.mkdtemp')
    @patch('builtins.open', new_callable=mock_open)
    @patch('sagemaker_gen_ai_jupyterlab_extension.zipfile.ZipFile')
    @patch('sagemaker_gen_ai_jupyterlab_extension.os.walk')
    def test_successful_download_and_extract(self, mock_walk, mock_zipfile, mock_file_open, mock_mkdtemp, mock_get, mock_manifest, mock_zip_content):
        # Setup mocks
        temp_dir = '/tmp/test_dir'
        mock_mkdtemp.return_value = temp_dir
        
        # Mock os.walk to return the JS file
        mock_walk.return_value = [('/tmp/test_dir', [], ['aws-lsp-codewhisperer.js'])]
        
        # Mock zipfile extraction
        mock_zip_instance = Mock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        # Mock manifest response
        manifest_response = Mock()
        manifest_response.json.return_value = mock_manifest
        manifest_response.raise_for_status.return_value = None
        
        # Mock zip response
        zip_response = Mock()
        zip_response.content = mock_zip_content
        zip_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [manifest_response, zip_response]
        
        # Execute
        download_and_extract_lsp_server()
        
        # Verify
        assert mock_get.call_count == 2
        mock_get.assert_any_call(MANIFEST_URL)
        mock_get.assert_any_call("https://example.com/servers.zip")
        mock_zip_instance.extractall.assert_called_once_with(temp_dir)

    @patch('sagemaker_gen_ai_jupyterlab_extension.requests.get')
    def test_version_not_found(self, mock_get):
        manifest = {"versions": [{"serverVersion": "2.0.0"}]}
        mock_response = Mock()
        mock_response.json.return_value = manifest
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match=f"Version {FLARE_SERVER_VERSION} not found"):
            download_and_extract_lsp_server()

    @patch('sagemaker_gen_ai_jupyterlab_extension.requests.get')
    def test_linux_target_not_found(self, mock_get):
        manifest = {
            "versions": [{
                "serverVersion": FLARE_SERVER_VERSION,
                "targets": [{"platform": "windows"}]
            }]
        }
        mock_response = Mock()
        mock_response.json.return_value = manifest
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="Linux target not found"):
            download_and_extract_lsp_server()

    @patch('sagemaker_gen_ai_jupyterlab_extension.requests.get')
    def test_servers_zip_not_found(self, mock_get):
        manifest = {
            "versions": [{
                "serverVersion": FLARE_SERVER_VERSION,
                "targets": [{
                    "platform": "linux",
                    "contents": [{"filename": "other.zip"}]
                }]
            }]
        }
        mock_response = Mock()
        mock_response.json.return_value = manifest
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception, match="servers.zip not found"):
            download_and_extract_lsp_server()

    @patch('sagemaker_gen_ai_jupyterlab_extension.requests.get')
    def test_manifest_download_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Network error"):
            download_and_extract_lsp_server()