from unittest.mock import Mock, patch, mock_open
import json
import pytest
import os

from sagemaker_gen_ai_jupyterlab_extension.extract_utils import (
    extract_bearer_token, extract_q_settings, extract_auth_mode, 
    extract_q_customization_arn, extract_q_enabled_status, AuthMode, FilePaths
)

class TestExtractUtils:
    
    def test_auth_mode_enum(self):
        """Test AuthMode enum values"""
        assert AuthMode.IDC.value == "IDC"
        assert AuthMode.IAM.value == "IAM"
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"idc_access_token": "test_token"}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_bearer_token_success(self, mock_logger, mock_expanduser, mock_file):
        """Test successful bearer token extraction"""
        mock_expanduser.return_value = "/home/user/.aws/sso/idc_access_token.json"
        
        token = extract_bearer_token()
        
        assert token == "test_token"
        mock_expanduser.assert_called_once_with("~/.aws/sso/idc_access_token.json")

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_bearer_token_file_not_found(self, mock_logger, mock_file):
        """Test bearer token extraction when file not found"""
        token = extract_bearer_token()
        
        assert token is None
        mock_logger.error.assert_called_with(f"Token file not found: {FilePaths.BEARER_TOKEN.value}")
        
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_bearer_token_invalid_json(self, mock_logger, mock_file):
        """Test bearer token extraction with invalid JSON"""
        token = extract_bearer_token()
        
        assert token is None
        mock_logger.error.assert_called_with(f"Invalid JSON in token file: {FilePaths.BEARER_TOKEN.value}")
        
    @patch('builtins.open', new_callable=mock_open, read_data='{"idc_access_token": ""}')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_bearer_token_empty_token(self, mock_logger, mock_file):
        """Test bearer token extraction with empty token"""
        token = extract_bearer_token()
        
        assert token is None
        mock_logger.error.assert_called_with(f"No bearer token found in {FilePaths.BEARER_TOKEN.value}")
        
    @patch('builtins.open', new_callable=mock_open, read_data='{"wrong_key": "test_token"}')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_bearer_token_wrong_key(self, mock_logger, mock_file):
        """Test bearer token extraction with wrong key"""
        token = extract_bearer_token()
        
        assert token is None
        mock_logger.error.assert_called_with(f"No bearer token found in {FilePaths.BEARER_TOKEN.value}")

    @patch('builtins.open', new_callable=mock_open, read_data='{"q_dev_profile_arn": "test_arn"}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_settings_success(self, mock_logger, mock_expanduser, mock_file):
        """Test successful Q settings extraction"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/q_dev_profile.json"
        
        arn = extract_q_settings()
        
        assert arn == "test_arn"
        mock_logger.info.assert_called_with("Returning Q profile ARN: test_arn")
        
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_settings_file_not_found(self, mock_logger, mock_file):
        """Test Q settings extraction when file not found"""
        arn = extract_q_settings()
        
        assert arn is None
        mock_logger.error.assert_called_with(f"Profile  not found: {FilePaths.Q_DEV_PROFILE.value}")
        
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_settings_invalid_json(self, mock_logger, mock_file):
        """Test Q settings extraction with invalid JSON"""
        arn = extract_q_settings()
        
        assert arn is None
        mock_logger.error.assert_called_with(f"Invalid JSON in token file: {FilePaths.Q_DEV_PROFILE.value}")
        
    @patch('builtins.open', new_callable=mock_open, read_data='{"q_dev_profile_arn": ""}')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_settings_empty_arn(self, mock_logger, mock_file):
        """Test Q settings extraction with empty ARN"""
        arn = extract_q_settings()
        
        assert arn is None
        mock_logger.error.assert_called_with(f"No Q profile ARN found in {FilePaths.Q_DEV_PROFILE.value}")
        
    @patch('builtins.open', new_callable=mock_open, read_data='{"wrong_key": "test_arn"}')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_settings_wrong_key(self, mock_logger, mock_file):
        """Test Q settings extraction with wrong key"""
        arn = extract_q_settings()
        
        assert arn is None
        mock_logger.error.assert_called_with(f"No Q profile ARN found in {FilePaths.Q_DEV_PROFILE.value}")

    @patch('builtins.open', new_callable=mock_open, read_data='{"auth_mode": "IDC"}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_auth_mode_idc(self, mock_logger, mock_expanduser, mock_file):
        """Test auth mode extraction with IDC value"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/settings.json"
        
        auth_mode = extract_auth_mode()
        
        assert auth_mode == AuthMode.IDC.value
        mock_logger.info.assert_called_with("Returning auth mode: IDC")

    @patch('builtins.open', new_callable=mock_open, read_data='{"auth_mode": "IAM"}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_auth_mode_iam(self, mock_logger, mock_expanduser, mock_file):
        """Test auth mode extraction with IAM value"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/settings.json"
        
        auth_mode = extract_auth_mode()
        
        assert auth_mode == AuthMode.IAM.value
        mock_logger.info.assert_called_with("Returning auth mode: IAM")

    @patch('builtins.open', new_callable=mock_open, read_data='{"auth_mode": "INVALID"}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_auth_mode_invalid(self, mock_logger, mock_expanduser, mock_file):
        """Test auth mode extraction with invalid value"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/settings.json"
        
        auth_mode = extract_auth_mode()
        
        assert auth_mode == AuthMode.IAM.value
        mock_logger.error.assert_called_with("Invalid auth mode: INVALID, defaulting to IAM")
        
    @patch('builtins.open', new_callable=mock_open, read_data='{"auth_mode": ""}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_auth_mode_empty(self, mock_logger, mock_expanduser, mock_file):
        """Test auth mode extraction with empty value"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/settings.json"
        
        auth_mode = extract_auth_mode()
        
        assert auth_mode == AuthMode.IAM.value
        mock_logger.error.assert_called_with(f"No auth mode found in {FilePaths.SETTINGS.value}")
        
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_auth_mode_file_not_found(self, mock_logger, mock_file):
        """Test auth mode extraction when file not found"""
        auth_mode = extract_auth_mode()
        
        assert auth_mode == AuthMode.IAM.value
        mock_logger.error.assert_called_with(f"Profile not found: {FilePaths.SETTINGS.value}")
        
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_auth_mode_invalid_json(self, mock_logger, mock_file):
        """Test auth mode extraction with invalid JSON"""
        auth_mode = extract_auth_mode()
        
        assert auth_mode == AuthMode.IAM.value
        mock_logger.error.assert_called_with(f"Invalid JSON in token file: {FilePaths.SETTINGS.value}")
        
    @patch('builtins.open')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_auth_mode_general_exception(self, mock_logger, mock_file):
        """Test auth mode extraction with general exception"""
        mock_file.side_effect = Exception("Test error")
        
        auth_mode = extract_auth_mode()
        
        assert auth_mode == AuthMode.IAM.value
        mock_logger.error.assert_called_with(f"Error reading token file: Test error")



    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"customization_arn": "test_arn"}')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_customization_arn_success(self, mock_logger, mock_file, mock_exists):
        """Test successful customization ARN extraction"""
        mock_exists.return_value = True
        
        arn = extract_q_customization_arn()
        
        assert arn == "test_arn"  # The function looks for 'customization_arn' key
        mock_logger.info.assert_any_call("Found Q customization ARN: test_arn")
        
    @patch('os.path.exists')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_customization_arn_file_not_exists(self, mock_logger, mock_exists):
        """Test customization ARN extraction when file doesn't exist"""
        mock_exists.return_value = False
        
        arn = extract_q_customization_arn()
        
        assert arn is None
        mock_logger.info.assert_any_call(f"Customization file does not exist at: {os.path.expanduser(FilePaths.Q_CUSTOMIZATION_ARN.value)}")
        
    @patch('os.path.exists')
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_customization_arn_file_not_found(self, mock_logger, mock_file, mock_exists):
        """Test customization ARN extraction when file not found"""
        mock_exists.return_value = True
        
        arn = extract_q_customization_arn()
        
        assert arn is None
        mock_logger.info.assert_called_with(f"Customization file not found: {os.path.expanduser(FilePaths.Q_CUSTOMIZATION_ARN.value)}")
        
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_customization_arn_invalid_json(self, mock_logger, mock_file, mock_exists):
        """Test customization ARN extraction with invalid JSON"""
        mock_exists.return_value = True
        
        arn = extract_q_customization_arn()
        
        assert arn is None
        mock_logger.error.assert_called_with(f"Invalid JSON in customization file: {os.path.expanduser(FilePaths.Q_CUSTOMIZATION_ARN.value)}")
        
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"customization_arn": ""}')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_customization_arn_empty(self, mock_logger, mock_file, mock_exists):
        """Test customization ARN extraction with empty value"""
        mock_exists.return_value = True
        
        arn = extract_q_customization_arn()
        
        assert arn is None
        mock_logger.info.assert_any_call(f"No customization ARN found in {os.path.expanduser(FilePaths.Q_CUSTOMIZATION_ARN.value)}")

    @patch('builtins.open', new_callable=mock_open, read_data='{"q_enabled": true}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_enabled_status_true(self, mock_logger, mock_expanduser, mock_file):
        """Test Q enabled status extraction with true value"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/settings.json"
        
        q_enabled = extract_q_enabled_status()
        
        assert q_enabled is True
        mock_logger.info.assert_called_with("Returning q_enabled: True")

    @patch('builtins.open', new_callable=mock_open, read_data='{"q_enabled": false}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_enabled_status_false(self, mock_logger, mock_expanduser, mock_file):
        """Test Q enabled status extraction with false value"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/settings.json"
        
        q_enabled = extract_q_enabled_status()
        
        assert q_enabled is False
        mock_logger.info.assert_called_with("Returning q_enabled: False")

    @patch('builtins.open', new_callable=mock_open, read_data='{"auth_mode": "IAM"}')
    @patch('os.path.expanduser')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_enabled_status_missing_key(self, mock_logger, mock_expanduser, mock_file):
        """Test Q enabled status extraction with missing key defaults to False"""
        mock_expanduser.return_value = "/home/user/.aws/amazon_q/settings.json"
        
        q_enabled = extract_q_enabled_status()
        
        assert q_enabled is False
        mock_logger.info.assert_called_with("Returning q_enabled: False")

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_enabled_status_file_not_found(self, mock_logger, mock_file):
        """Test Q enabled status extraction when file not found"""
        q_enabled = extract_q_enabled_status()
        
        assert q_enabled is False
        mock_logger.error.assert_called_with(f"Settings file not found: {FilePaths.SETTINGS.value}")

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_enabled_status_invalid_json(self, mock_logger, mock_file):
        """Test Q enabled status extraction with invalid JSON"""
        q_enabled = extract_q_enabled_status()
        
        assert q_enabled is False
        mock_logger.error.assert_called_with(f"Invalid JSON in settings file: {FilePaths.SETTINGS.value}")

    @patch('builtins.open')
    @patch('sagemaker_gen_ai_jupyterlab_extension.extract_utils.logger')
    def test_extract_q_enabled_status_general_exception(self, mock_logger, mock_file):
        """Test Q enabled status extraction with general exception"""
        mock_file.side_effect = Exception("Test error")
        
        q_enabled = extract_q_enabled_status()
        
        assert q_enabled is False
        mock_logger.error.assert_called_with("Error reading settings file: Test error")