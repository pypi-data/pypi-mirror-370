from unittest.mock import Mock, patch, call
import pytest
import threading
import json
import sys

# Mock watchdog before importing
with patch.dict('sys.modules', {
    'watchdog': Mock(),
    'watchdog.observers': Mock(),
    'watchdog.events': Mock()
}):
    from sagemaker_gen_ai_jupyterlab_extension.credential_manager import CredentialManager
    from sagemaker_gen_ai_jupyterlab_extension.extract_utils import AuthMode


class TestCredentialManager:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_lsp_connection = Mock()
        self.auth_mode = AuthMode.IDC.value
        
    def test_init(self):
        """Test CredentialManager initialization"""
        manager = CredentialManager(self.mock_lsp_connection, self.auth_mode)
        
        assert manager.lsp_connection == self.mock_lsp_connection
        assert manager.current_auth_mode == self.auth_mode
        assert manager.refresh_timer is None

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_q_settings')
    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_bearer_token')
    def test_initialize_credentials_idc(self, mock_extract_token, mock_q_settings):
        """Test credential initialization for IDC mode"""
        mock_extract_token.return_value = "test_token"
        mock_q_settings.return_value = "arn:aws:codewhisperer:us-east-1:124345667788666:profile/XXXXXXXXXXX"
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        manager.initialize_credentials()
        
        # Verify bearer token setup (called once on setup)
        assert self.mock_lsp_connection.update_access_token.call_count == 1
        self.mock_lsp_connection.update_access_token.assert_called_with("test_token", "arn:aws:codewhisperer:us-east-1:124345667788666:profile/XXXXXXXXXXX")

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.boto3.Session')
    def test_initialize_credentials_iam(self, mock_session_class):
        """Test credential initialization for IAM mode"""
        # Mock boto3 session and credentials
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_credentials = Mock()
        mock_credentials.access_key = "test_key"
        mock_credentials.secret_key = "test_secret"
        mock_credentials.token = "test_token"
        mock_credentials._expiry_time = "2025-07-22 21:42:02+00:00"
        mock_session.get_credentials.return_value = mock_credentials
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IAM.value)
        manager.initialize_credentials()
        
        # Verify IAM credentials setup (called once on setup)
        assert self.mock_lsp_connection.update_iam_credentials.call_count == 1
        self.mock_lsp_connection.update_iam_credentials.assert_called_with("test_key", "test_secret", "test_token", "2025-07-22 21:42:02+00:00")

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_auth_mode')
    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_bearer_token')
    def test_handle_tier_change_iam_to_idc(self, mock_extract_token, mock_extract_auth):
        """Test tier change from IAM to IDC"""
        mock_extract_auth.return_value = AuthMode.IDC.value
        mock_extract_token.return_value = "new_token"
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IAM.value)
        
        with patch.object(manager, '_stop_refresh_timer') as mock_stop:
            with patch.object(manager.lsp_connection, 'restart_lsp_server') as mock_restart:
                manager.handle_tier_change()
                
                # Verify tier change handling
                mock_stop.assert_called_once()
                mock_restart.assert_called_once()
                # Verify bearer token setup
                self.mock_lsp_connection.update_access_token.assert_called_with("new_token", "randomstring")
                assert manager.current_auth_mode == AuthMode.IDC.value

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_auth_mode')
    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.boto3.Session')
    def test_handle_tier_change_idc_to_iam(self, mock_session_class, mock_extract_auth):
        """Test tier change from IDC to IAM"""
        mock_extract_auth.return_value = AuthMode.IAM.value
        
        # Mock boto3 session and credentials
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_credentials = Mock()
        mock_credentials.access_key = "test_key"
        mock_credentials.secret_key = "test_secret"
        mock_credentials.token = "test_token"
        mock_credentials._expiry_time = "2025-07-22 21:42:02+00:00"
        mock_session.get_credentials.return_value = mock_credentials
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        
        with patch.object(manager, '_stop_refresh_timer') as mock_stop:
            with patch.object(manager.lsp_connection, 'restart_lsp_server') as mock_restart:
                manager.handle_tier_change()
                
                # Verify tier change handling
                mock_stop.assert_called_once()
                mock_restart.assert_called_once()
                # Verify IAM credentials setup (called twice: setup + refresh)
                assert self.mock_lsp_connection.update_iam_credentials.call_count >= 1
                self.mock_lsp_connection.update_iam_credentials.assert_called_with("test_key", "test_secret", "test_token", "2025-07-22 21:42:02+00:00")
                assert manager.current_auth_mode == AuthMode.IAM.value

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_auth_mode')
    def test_handle_tier_change_no_change(self, mock_extract_auth):
        """Test tier change when auth mode hasn't changed"""
        mock_extract_auth.return_value = AuthMode.IDC.value
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        
        with patch.object(manager.lsp_connection, 'restart_lsp_server') as mock_restart:
            manager.handle_tier_change()
            
            # Verify no change occurred
            mock_restart.assert_not_called()

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_bearer_token')
    def test_update_bearer_token_success(self, mock_extract_token):
        """Test successful bearer token refresh"""
        mock_extract_token.return_value = "refreshed_token"
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        manager._update_bearer_token()
        
        self.mock_lsp_connection.update_access_token.assert_called_once_with("refreshed_token", "randomstring")

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_bearer_token')
    def test_update_bearer_token_failure(self, mock_extract_token):
        """Test bearer token refresh failure"""
        mock_extract_token.return_value = None
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.logger') as mock_logger:
            manager._update_bearer_token()
            
            mock_logger.error.assert_called_once_with("Failed to refresh bearer token")

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.boto3.Session')
    def test_refresh_iam_credentials_success(self, mock_session_class):
        """Test successful IAM credentials refresh"""
        # Mock boto3 session and credentials
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_credentials = Mock()
        mock_credentials.access_key = "key"
        mock_credentials.secret_key = "secret"
        mock_credentials.token = "token"
        mock_credentials._expiry_time = "2025-07-22 21:42:02+00:00"
        mock_session.get_credentials.return_value = mock_credentials
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IAM.value)
        manager._update_iam_credentials()
        
        self.mock_lsp_connection.update_iam_credentials.assert_called_once_with("key", "secret", "token", "2025-07-22 21:42:02+00:00")

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.boto3.Session')
    def test_refresh_iam_credentials_failure(self, mock_session_class):
        """Test IAM credentials refresh with boto3 failure"""
        # Mock boto3 session to return None credentials
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_credentials.return_value = None
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IAM.value)
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.logger') as mock_logger:
            manager._update_iam_credentials()
            
            mock_logger.error.assert_called_with("Failed to setup IAM credentials")

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.boto3.Session')
    def test_refresh_iam_credentials_boto3_error(self, mock_session_class):
        """Test IAM credentials refresh with boto3 exception"""
        # Mock boto3 session to raise exception
        mock_session_class.side_effect = Exception("AWS error")
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IAM.value)
        
        with patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.logger') as mock_logger:
            manager._update_iam_credentials()
            mock_logger.error.assert_called_with("Failed to setup IAM credentials")

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.threading.Timer')
    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.extract_bearer_token')
    def test_start_refresh_idc(self, mock_extract_token, mock_timer):
        """Test starting refresh timer for IDC mode"""
        mock_extract_token.return_value = "test_token"
        mock_timer_instance = Mock()
        mock_timer.return_value = mock_timer_instance
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        manager._start_refresh(AuthMode.IDC.value)
        
        # Verify timer was created and started
        assert mock_timer.call_count == 1
        args, kwargs = mock_timer.call_args
        assert args[0] == 300  # timer interval
        callback_func = args[1]  # the refresh_and_reschedule function
        
        # Execute the callback to test its behavior
        with patch.object(manager, '_update_bearer_token') as mock_update:
            callback_func()
            mock_update.assert_called_once()
        
        # refresh_and_reschedule calls the timer again so total count is 2
        assert mock_timer.call_count == 2

    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.threading.Timer')
    @patch('sagemaker_gen_ai_jupyterlab_extension.credential_manager.boto3.Session')
    def test_start_refresh_iam(self, mock_session_class, mock_timer):
        """Test starting refresh timer for IAM mode"""
        mock_timer_instance = Mock()
        mock_timer.return_value = mock_timer_instance
        
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IAM.value)
        manager._start_refresh(AuthMode.IAM.value)
        
        # Verify timer was created and started
        assert mock_timer.call_count == 1
        args, kwargs = mock_timer.call_args
        assert args[0] == 300  # timer interval
        callback_func = args[1]  # the refresh_and_reschedule function
        
        # Execute the callback to test its behavior
        with patch.object(manager, '_update_iam_credentials') as mock_update:
            callback_func()
            mock_update.assert_called_once()
        # refresh_and_reschedule calls the timer again so total count is 2
        assert mock_timer.call_count == 2



    def test_cleanup(self):
        """Test cleanup functionality"""
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        mock_timer = Mock()
        manager.refresh_timer = mock_timer
        
        manager.cleanup()
        
        mock_timer.cancel.assert_called_once()

    def test_stop_refresh_timer(self):
        """Test stopping refresh timer"""
        manager = CredentialManager(self.mock_lsp_connection, AuthMode.IDC.value)
        mock_timer = Mock()
        manager.refresh_timer = mock_timer
        
        manager._stop_refresh_timer()
        
        mock_timer.cancel.assert_called_once()
        assert manager.refresh_timer is None

