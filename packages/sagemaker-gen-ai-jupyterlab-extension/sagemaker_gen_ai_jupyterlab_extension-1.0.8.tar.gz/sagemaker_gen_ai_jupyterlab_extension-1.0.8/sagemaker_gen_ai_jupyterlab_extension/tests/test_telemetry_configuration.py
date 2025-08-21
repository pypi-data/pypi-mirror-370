import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from sagemaker_gen_ai_jupyterlab_extension.lsp_server_connection import LspServerConnection


class TestTelemetryConfiguration(unittest.TestCase):
    
    def setUp(self):
        self.lsp_connection = LspServerConnection()
    
    def test_handle_workspace_configuration_aws_optout_telemetry_true(self):
        """Test workspace configuration returns True when optInToQTelemetry is False"""
        with patch.object(self.lsp_connection, 'get_telemetry_settings', return_value={"optInToQTelemetry": False}):
            params = {
                "items": [{"section": "aws.optOutTelemetry"}]
            }
            
            result = self.lsp_connection.handle_workspace_configuration(params)
            
            self.assertEqual(result, [True])
    
    def test_handle_workspace_configuration_aws_optout_telemetry_false(self):
        """Test workspace configuration returns False when optInToQTelemetry is True"""
        with patch.object(self.lsp_connection, 'get_telemetry_settings', return_value={"optInToQTelemetry": True}):
            params = {
                "items": [{"section": "aws.optOutTelemetry"}]
            }
            
            result = self.lsp_connection.handle_workspace_configuration(params)
            
            self.assertEqual(result, [False])
    
    def test_get_telemetry_settings_file_exists(self):
        """Test reading telemetry settings when file exists"""
        mock_settings = {"optInToQTelemetry": True}
        
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = MagicMock()
            settings_path = mock_home.return_value / ".jupyter/lab/user-settings/@amzn/sagemaker_gen_ai_jupyterlab_extension/plugin.jupyterlab-settings"
            settings_path.exists.return_value = True
            
            with patch('builtins.open', mock_open(read_data=json.dumps(mock_settings))):
                result = self.lsp_connection.get_telemetry_settings()
                
                self.assertEqual(result, mock_settings)
    
    def test_get_telemetry_settings_file_not_exists(self):
        """Test default telemetry settings when file doesn't exist"""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = MagicMock()
            settings_path = mock_home.return_value / ".jupyter/lab/user-settings/@amzn/sagemaker_gen_ai_jupyterlab_extension/plugin.jupyterlab-settings"
            settings_path.exists.return_value = False
            
            result = self.lsp_connection.get_telemetry_settings()
            
            self.assertEqual(result, {"optInToQTelemetry": False})
    
    def test_get_telemetry_settings_error_handling(self):
        """Test error handling when reading telemetry settings fails"""
        with patch('pathlib.Path.home', side_effect=Exception("File error")):
            result = self.lsp_connection.get_telemetry_settings()
            
            self.assertEqual(result, {"optInToQTelemetry": False})


if __name__ == '__main__':
    unittest.main()