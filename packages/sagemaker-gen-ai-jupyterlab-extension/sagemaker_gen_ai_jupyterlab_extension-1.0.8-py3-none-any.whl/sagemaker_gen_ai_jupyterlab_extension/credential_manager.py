import logging
import threading
import boto3
from .extract_utils import extract_bearer_token, extract_auth_mode, AuthMode, extract_q_settings

logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')
START_URL = "randomstring"
REFRESH_TIMER_LIMIT = 300
CREDS_PROFILE_NAME = "DomainExecutionRoleCreds"

class CredentialManager:
    def __init__(self, lsp_connection, auth_mode):
        self.lsp_connection = lsp_connection
        self.current_auth_mode = auth_mode
        self.refresh_timer = None
        
    def initialize_credentials(self):
        """Initialize credentials based on current auth mode"""
        if self.current_auth_mode == AuthMode.IDC.value:
            self._update_bearer_token()
            self._start_refresh(self.current_auth_mode)
            logger.info("Configured bearer token authentication")
        elif self.current_auth_mode == AuthMode.IAM.value:
            self._update_iam_credentials()
            self._start_refresh(self.current_auth_mode)
            logger.info("Configured IAM SigV4 authentication")
        else:
            logger.error(f"Invalid auth mode: {self.current_auth_mode}")
    
    def handle_tier_change(self):
        """Handle Q tier changes by switching credential types"""
        new_auth_mode = extract_auth_mode()
        
        if new_auth_mode != self.current_auth_mode:
            logger.info(f"Q tier changed: {self.current_auth_mode} -> {new_auth_mode}")
            self._stop_refresh_timer()
            
            # Restart LSP server with new auth mode
            from . import NODE_PATH, LSP_EXECUTABLE_PATH, WORKSPACE_FOLDER
            self.lsp_connection.restart_lsp_server(NODE_PATH, LSP_EXECUTABLE_PATH, new_auth_mode, WORKSPACE_FOLDER)
            
            if new_auth_mode == AuthMode.IDC.value:
                # Free → Pro: Switch to bearer token
                self._update_bearer_token()
                self._start_refresh(new_auth_mode)
                self._setup_paid_tier_features()
                logger.info("Configured bearer token authentication")
            elif new_auth_mode == AuthMode.IAM.value:
                # Pro → Free: Switch to IAM SigV4
                self._update_iam_credentials()
                self._start_refresh(new_auth_mode)
                logger.info("Configured IAM SigV4 authentication")
            
            self.current_auth_mode = new_auth_mode
        else:
            logger.info(f"Q tier unchanged: {self.current_auth_mode}")
            self._stop_refresh_timer()
            self.initialize_credentials()
    

    def _update_iam_credentials(self):
        """Update IAM credentials to LSP server"""
        try:
            credentials = self._get_iam_credentials()
            if credentials:
                self.lsp_connection.update_iam_credentials(credentials.access_key, credentials.secret_key, credentials.token, str(credentials._expiry_time))
                logger.info("Successfully updated IAM credentials")
            else:
                logger.error("Failed to setup IAM credentials")
        except Exception as e:
            logger.error(f"Error refreshing IAM credentials: {e}")

    def _get_iam_credentials(self):
        try:
            session = boto3.Session(profile_name=CREDS_PROFILE_NAME)
            credentials = session.get_credentials()
            return credentials
        except boto3.exceptions.Boto3Error as boto_error:
            logger.error(f"AWS credentials error: {str(boto_error)}")
        except Exception as e:
            logger.error(f"Failed to get credentials: {str(e)}")

    
    def _update_bearer_token(self):
        """Update bearer token to LSP server"""
        try:
            token = extract_bearer_token()
            # We will set start URL to Q profile ARN so it can be used 
            # to distunguish customer requests for telemetry
            start_url = extract_q_settings()
            if start_url is None:
                # Setting it to a randomstring if there is error getting q profile ARN
                # since Flare does not accept None start URL
                # Ref: https://t.corp.amazon.com/P250511444/communication
                start_url = START_URL
            if token:
                self.lsp_connection.update_access_token(token, start_url)
            else:
                logger.error("Failed to refresh bearer token")
        except Exception as e:
            logger.error(f"Error refreshing bearer token: {e}")
    
    def _start_refresh(self, auth_mode):
        """Start periodic bearer token/IAM credentials refresh"""
        def refresh_and_reschedule():
            if auth_mode == AuthMode.IDC.value:
                self._update_bearer_token()
            elif auth_mode == AuthMode.IAM.value:
                self._update_iam_credentials()
            self._start_refresh(auth_mode)
        # setting the next refresh
        self.refresh_timer = threading.Timer(REFRESH_TIMER_LIMIT, refresh_and_reschedule)
        self.refresh_timer.daemon = True
        self.refresh_timer.start()
    
    def _stop_refresh_timer(self):
        """Stop the current refresh timer"""
        if self.refresh_timer:
            self.refresh_timer.cancel()
            self.refresh_timer = None
    
    def _setup_paid_tier_features(self):
        """Setup Q profile and customization for paid tier"""
        try:
            from .extract_utils import extract_q_settings, extract_q_customization_arn
            
            # Update Q profile
            q_settings = extract_q_settings()
            if q_settings:
                self.lsp_connection.update_q_profile(q_settings)
                logger.info("Updated Q profile for paid tier")
            
            # Update Q customization
            customization_arn = extract_q_customization_arn()
            if customization_arn:
                self.lsp_connection.update_q_customization(customization_arn)
                logger.info("Updated Q customization for paid tier")
                
        except Exception as e:
            logger.error(f"Error setting up paid tier features: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self._stop_refresh_timer()