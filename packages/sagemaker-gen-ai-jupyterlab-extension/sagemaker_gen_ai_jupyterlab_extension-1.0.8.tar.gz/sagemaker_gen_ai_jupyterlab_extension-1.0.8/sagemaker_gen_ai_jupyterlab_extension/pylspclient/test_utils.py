import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import get_user, log_pylspclient_action

class TestUtils(unittest.TestCase):
    
    @patch('utils.subprocess.run')
    def test_get_user_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "test-user\n"
        mock_run.return_value = mock_result
        
        result = get_user()
        
        self.assertEqual(result, "test-user")
        mock_run.assert_called_once_with(['bash', '-c', 'source ~/.bashrc && echo $LOGNAME'], capture_output=True, text=True)
    
    @patch('utils.subprocess.run')
    def test_get_user_empty_output(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        result = get_user()
        
        self.assertIsNone(result)
    
    @patch('utils.subprocess.run')
    def test_get_user_exception(self, mock_run):
        mock_run.side_effect = Exception("Command failed")
        
        result = get_user()
        
        self.assertIsNone(result)
    
    @patch('utils.get_user')
    @patch('utils.logging.info')
    def test_log_pylspclient_action_with_kwargs(self, mock_logging_info, mock_get_user):
        mock_get_user.return_value = "test_user"
        
        log_pylspclient_action("Test action", method="test_method", params={"key": "value"})
        
        mock_logging_info.assert_called_once_with("Test action: method=test_method, params={'key': 'value'}, user: test_user")
    
    @patch('utils.get_user')
    @patch('utils.logging.info')
    def test_log_pylspclient_action_no_kwargs(self, mock_logging_info, mock_get_user):
        mock_get_user.return_value = "test_user"
        
        log_pylspclient_action("Test action")
        
        mock_logging_info.assert_called_once_with("Test action: , user: test_user")
    
    @patch('utils.get_user')
    @patch('utils.logging.info')
    def test_log_pylspclient_action_no_user(self, mock_logging_info, mock_get_user):
        mock_get_user.return_value = None
        
        log_pylspclient_action("Test action", id=123)
        
        mock_logging_info.assert_called_once_with("Test action: id=123, user: None")
    
    @patch('utils.get_user')
    @patch('utils.logging.info')
    def test_log_pylspclient_action_sensitive_iam_method(self, mock_logging_info, mock_get_user):
        mock_get_user.return_value = "test_user"
        
        log_pylspclient_action("Test action", method="aws/credentials/iam/update", sensitive_param="secret_value")
        
        mock_logging_info.assert_called_once_with("Test action: method=aws/credentials/iam/update, user: test_user")
    
    @patch('utils.get_user')
    @patch('utils.logging.info')
    def test_log_pylspclient_action_sensitive_token_method(self, mock_logging_info, mock_get_user):
        mock_get_user.return_value = "test_user"
        
        log_pylspclient_action("Test action", method="aws/credentials/token/update", token="secret_token")
        
        mock_logging_info.assert_called_once_with("Test action: method=aws/credentials/token/update, user: test_user")
    
    @patch('utils.get_user')
    @patch('utils.logging.info')
    def test_log_pylspclient_action_non_sensitive_method(self, mock_logging_info, mock_get_user):
        mock_get_user.return_value = "test_user"
        
        log_pylspclient_action("Test action", method="aws/chat/sendMessage", params={"message": "hello"})
        
        mock_logging_info.assert_called_once_with("Test action: method=aws/chat/sendMessage, params={'message': 'hello'}, user: test_user")

if __name__ == '__main__':
    unittest.main()