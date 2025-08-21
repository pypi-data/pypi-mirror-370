"""
SMUS Flare JupyterLab extension for AWS Q integration
"""
try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings
    warnings.warn("Importing 'SageMakerGenAIJupyterLabExtension' outside a proper installation.")
    __version__ = "dev"
from .handlers import setup_handlers
from .request_logger import init_api_operation_logger
import logging
import os
import pathlib
import requests
import zipfile
import tempfile
from .lsp_server_connection import LspServerConnection
from .extract_utils import extract_q_customization_arn, extract_q_settings, extract_auth_mode
from .q_customization import QCustomization
from .credential_manager import CredentialManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')

# Get the directory where this __init__.py file is located
PACKAGE_DIR = pathlib.Path(__file__).parent.absolute()
MANIFEST_URL = "https://aws-toolkit-language-servers.amazonaws.com/qAgenticChatServer/0/manifest.json"
FLARE_SERVER_VERSION = "1.23.0"
NODE_PATH = "/opt/conda/bin/node"
WORKSPACE_FOLDER = "file:///home/sagemaker-user"

# Global variable to store the LSP executable path
LSP_EXECUTABLE_PATH = None

# Global variable to store the LSP connection
lsp_connection = None

# Global variable to store the credential manager
credential_manager = None

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "sagemaker_gen_ai_jupyterlab_extension"
    }]

__version__ = '1.0.8'

def get_lsp_connection():
    """
    Returns the initialized LSP connection.
    """
    global lsp_connection
    return lsp_connection

def get_credential_manager():
    """
    Returns the initialized credential manager.
    """
    global credential_manager
    return credential_manager

def chat_with_prompt(prompt):
    """
    Frontend-facing function that only requires a prompt.
    Uses the pre-initialized LSP connection from __init__.py.
    
    Args:
        prompt (str): The chat prompt from the user
        
    Returns:
        dict: The response from the LSP server
    """
    lsp_connection = get_lsp_connection()
    return lsp_connection.get_chat_response(prompt)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "sagemaker_gen_ai_jupyterlab_extension"
    }]

q_customization = None

def download_and_extract_lsp_server():
    """Download manifest, find Linux version, download and extract LSP server"""
    global LSP_EXECUTABLE_PATH
    
    try:
        # Download manifest
        logger.info(f"Downloading manifest from {MANIFEST_URL}")
        response = requests.get(MANIFEST_URL)
        response.raise_for_status()
        manifest = response.json()
        
        # Find the specified version
        version_data = None
        for version in manifest.get('versions', []):
            if version.get('serverVersion') == FLARE_SERVER_VERSION:
                version_data = version
                break
        
        if not version_data:
            raise Exception(f"Version {FLARE_SERVER_VERSION} not found in manifest")
        
        # Find Linux target
        linux_target = None
        for target in version_data.get('targets', []):
            if target.get('platform') == 'linux':
                linux_target = target
                break
        
        if not linux_target:
            raise Exception("Linux target not found in manifest")
        
        # Find servers.zip
        servers_zip_url = None
        for content in linux_target.get('contents', []):
            if content.get('filename') == 'servers.zip':
                servers_zip_url = content.get('url')
                break
        
        if not servers_zip_url:
            raise Exception("servers.zip not found in Linux target")
        
        # Download and extract servers.zip
        logger.info(f"Downloading servers.zip from {servers_zip_url}")
        zip_response = requests.get(servers_zip_url)
        zip_response.raise_for_status()
        
        # Create temp directory and extract
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'servers.zip')
        
        with open(zip_path, 'wb') as f:
            f.write(zip_response.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find aws-lsp-codewhisperer.js
        for root, dirs, files in os.walk(temp_dir):
            if 'aws-lsp-codewhisperer.js' in files:
                LSP_EXECUTABLE_PATH = os.path.join(root, 'aws-lsp-codewhisperer.js')
                logger.info(f"Found LSP executable at: {LSP_EXECUTABLE_PATH}")
                return
        
        raise Exception("aws-lsp-codewhisperer.js not found in extracted files")
        
    except Exception as e:
        logger.error(f"Error downloading LSP server: {e}")
        raise
    
def initialize_lsp_server():
    # TODO remove global variable use 
    global lsp_connection, credential_manager, q_customization

    # Download and extract LSP server
    logger.info("Downloading LSP server")
    download_and_extract_lsp_server()

    # Initialize the LSP connection when the extension loads
    logger.info(f"Starting LSP server with executable {LSP_EXECUTABLE_PATH}")
    auth_mode = extract_auth_mode()
    lsp_connection = LspServerConnection()
    lsp_connection.start_lsp_server(NODE_PATH, LSP_EXECUTABLE_PATH, auth_mode)
    lsp_connection.initialize(WORKSPACE_FOLDER)
    
    # Initialize credential manager and setup credentials
    credential_manager = CredentialManager(lsp_connection, auth_mode)
    credential_manager.initialize_credentials()
    
    # Update Q profile and customization (only for paid tier)
    from .extract_utils import AuthMode
    if auth_mode == AuthMode.IDC.value:
        # Initialize customization ARN and start file watcher
        customization_arn = extract_q_customization_arn()
        q_customization = QCustomization(lsp_connection)
        q_customization.start_customization_file_watcher()
        q_settings = extract_q_settings()
        if q_settings:
            lsp_connection.update_q_profile(q_settings)
        
        if customization_arn:
            lsp_connection.update_q_customization(customization_arn)
    logger.info("LSP server successfully initialized")
    return lsp_connection
    

def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(server_app.web_app)
    init_api_operation_logger(server_app.log)
    name = "sagemaker_gen_ai_jupyterlab_extension"
    server_app.log.info(f"Registered {name} server extension")

def _unload_jupyter_server_extension(server_app):
    """Unload the extension and stop the LSP server."""
    logger.info("In unload method")
    
    global lsp_connection, credential_manager, q_customization
    try:
        if credential_manager:
            logger.info("Cleaning up credential manager")
            credential_manager.cleanup()
            credential_manager = None
    except Exception as e:
        logger.error(f"Error cleaning up credential manager: {e}")

    # Stop customization file watcher
    try:
        if q_customization:
            logger.info("Stopping Customization file watcher")
            q_customization.stop_watcher_for_customization_file()
    except Exception as e:
         logger.error(f"Error stopping Customization file watcher: {e}")
