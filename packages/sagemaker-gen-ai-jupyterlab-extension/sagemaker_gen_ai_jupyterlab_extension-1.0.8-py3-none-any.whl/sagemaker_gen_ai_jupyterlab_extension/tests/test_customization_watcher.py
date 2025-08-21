import unittest
import tempfile
import os
import json
import time
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock watchdog before importing
with patch.dict('sys.modules', {
    'watchdog': Mock(),
    'watchdog.observers': Mock(),
    'watchdog.events': Mock()
}):
    from ..q_customization import QCustomization


class TestQCustomization(unittest.TestCase):
    
    def setUp(self):
        self.mock_lsp_connection = Mock()
        self.watcher = QCustomization(self.mock_lsp_connection)
        
    def tearDown(self):
        self.watcher.stop_watcher_for_customization_file()
    
    def test_start_watcher(self):
        with patch.object(self.watcher.file_watcher, 'start_watching') as mock_start:
            self.watcher.start_customization_file_watcher()
            mock_start.assert_called_once()
        
    def test_stop_watcher(self):
        with patch.object(self.watcher.file_watcher, 'stop_watching') as mock_stop:
            self.watcher.stop_watcher_for_customization_file()
            mock_stop.assert_called_once()
    
    @patch('sagemaker_gen_ai_jupyterlab_extension.q_customization.extract_q_customization_arn')
    def test_handle_file_change(self, mock_extract):
        mock_extract.return_value = 'test-arn'
        
        self.watcher._handle_customization_file_change()
        
        self.mock_lsp_connection.update_q_customization.assert_called_once_with('test-arn')


if __name__ == '__main__':
    unittest.main()