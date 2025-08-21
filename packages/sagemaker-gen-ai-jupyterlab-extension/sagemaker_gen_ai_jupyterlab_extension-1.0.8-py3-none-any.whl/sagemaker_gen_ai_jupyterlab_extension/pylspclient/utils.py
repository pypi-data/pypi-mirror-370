import subprocess
import logging

def get_user():
    """Get the current user from LOGNAME environment variable sourced from .bashrc"""
    try:
        result = subprocess.run(['bash', '-c', 'source ~/.bashrc && echo $LOGNAME'], capture_output=True, text=True)
        user = result.stdout.strip()
        return user if user else None
    except:
        return None

def log_pylspclient_action(action, **kwargs):
    """Logging callback for pylsp client actions with consistent formatting"""
    user = get_user()
    
    # Skip logging kwargs for sensitive credential methods
    method = kwargs.get('method')
    if method in ['aws/credentials/iam/update', 'aws/credentials/token/update']:
        logging.info(f"{action}: method={method}, user: {user}")
    else:
        params_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        logging.info(f"{action}: {params_str}, user: {user}")