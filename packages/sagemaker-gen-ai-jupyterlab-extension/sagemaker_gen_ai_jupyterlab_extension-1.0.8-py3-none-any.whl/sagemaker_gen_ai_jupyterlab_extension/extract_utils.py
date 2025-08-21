import os
import json
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')

class FilePaths(Enum):
    """File paths for various configurations"""
    BEARER_TOKEN = "~/.aws/sso/idc_access_token.json"
    Q_CUSTOMIZATION_ARN = "~/.aws/amazon_q/customization_arn.json"
    Q_DEV_PROFILE = "~/.aws/amazon_q/q_dev_profile.json"
    SETTINGS = "~/.aws/amazon_q/settings.json"
    CONFIG = "~/.aws/config"

class AuthMode(Enum):
    """Authentication modes for Amazon Q"""
    IDC = "IDC"  # Identity Center authentication
    IAM = "IAM"  # IAM authentication

def extract_bearer_token():
    """Extract bearer token from ~/.aws/sso/idc_access_token.json"""
    file_path = FilePaths.BEARER_TOKEN.value
    try:
        with open(os.path.expanduser(file_path), 'r') as f:
            content = json.load(f)
        
        token = content.get('idc_access_token')
        if not token or not token.strip():
            logger.error(f"No bearer token found in {file_path}")
            return None
        
        return token
    except FileNotFoundError:
        logger.error(f"Token file not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in token file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading token file: {e}")
        return None
    
def extract_q_customization_arn():
    """Extract customization ARN from ~/.aws/amazon_q/customization_arn.json"""
    file_path = os.path.expanduser(FilePaths.Q_CUSTOMIZATION_ARN.value)
    logger.info(f"Looking for customization file at: {file_path}")
    try:
        if not os.path.exists(file_path):
            logger.info(f"Customization file does not exist at: {file_path}")
            return None
  
        with open(file_path, "r") as f:
            content = json.load(f)
        customization_arn = content.get("customization_arn")
        if not customization_arn or not customization_arn.strip():
            logger.info(f"No customization ARN found in {file_path}")
            return None
        logger.info(f"Found Q customization ARN: {customization_arn}")
        return customization_arn
    except FileNotFoundError:
        logger.info(f"Customization file not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in customization file: {file_path}")
        return None
    except Exception as e:
         logger.error(f"Error reading customization file: {e}")
         return None
    
def extract_q_settings():
    """Extract bearer token from ~/.aws/sso/idc_access_token.json"""
    file_path = FilePaths.Q_DEV_PROFILE.value
    try:
        with open(os.path.expanduser(file_path), 'r') as f:
            content = json.load(f)
        q_profile_arn = content.get('q_dev_profile_arn')
        if not q_profile_arn or not q_profile_arn.strip():
            logger.error(f"No Q profile ARN found in {file_path}")
            return None
        logger.info(f"Returning Q profile ARN: {q_profile_arn}")
        return q_profile_arn
    except FileNotFoundError:
        logger.error(f"Profile  not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in token file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading token file: {e}")
        return None

def extract_q_enabled_status():
    """Extract q_enabled from ~/.aws/amazon_q/settings.json"""
    file_path = FilePaths.SETTINGS.value
    try:
        with open(os.path.expanduser(file_path), 'r') as f:
            content = json.load(f)
        q_enabled = content.get('q_enabled', False)
        logger.info(f"Returning q_enabled: {q_enabled}")
        return q_enabled
    except FileNotFoundError:
        logger.error(f"Settings file not found: {file_path}")
        return False
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in settings file: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error reading settings file: {e}")
        return False

def extract_auth_mode():
    """Extract auth mode from ~/.aws/amazon_q/settings.json"""
    file_path = FilePaths.SETTINGS.value
    try:
        with open(os.path.expanduser(file_path), 'r') as f:
            content = json.load(f)
        auth_mode = content.get('auth_mode')
        if not auth_mode or not auth_mode.strip():
            logger.error(f"No auth mode found in {file_path}")
            logger.info("Setting auth mode to default IAM")
            return AuthMode.IAM.value
        
        # Validate auth mode
        try:
            auth_mode_enum = AuthMode(auth_mode)
            logger.info(f"Returning auth mode: {auth_mode_enum.value}")
            return auth_mode_enum.value
        except ValueError:
            logger.error(f"Invalid auth mode: {auth_mode}, defaulting to IAM")
            return AuthMode.IAM.value
            
    except FileNotFoundError:
        logger.error(f"Profile not found: {file_path}")
        logger.info("Setting auth mode to default IAM")
        return AuthMode.IAM.value
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in token file: {file_path}")
        logger.info("Setting auth mode to default IAM")
        return AuthMode.IAM.value
    except Exception as e:
        logger.error(f"Error reading token file: {e}")
        logger.info("Setting auth mode to default IAM")
        return AuthMode.IAM.value
