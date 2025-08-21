import os
import time
import logging
from .extract_utils import extract_q_customization_arn
from .file_watcher import FileWatcher

logger = logging.getLogger(__name__)

RETRY_COUNT = 3


class QCustomization:
    """Handles Q customization related logic"""
    
    def __init__(self, lsp_connection):
        self.lsp_connection = lsp_connection
        self.file_watcher = FileWatcher()
        
    def start_customization_file_watcher(self):
        """Start file watcher for customization ARN file"""
        customization_dir = os.path.expanduser("~/.aws/amazon_q")
        self.file_watcher.start_watching(
            customization_dir, 
            'customization_arn.json', 
            self._handle_customization_file_change,
            recursive=False
        )

    def _handle_customization_file_change(self):
        """Handle customization file change event"""        
        # Retry logic to handle file write timing issues
        for attempt in range(RETRY_COUNT):
            try:
                time.sleep(0.1)  # Brief delay to let file write complete
                new_arn = extract_q_customization_arn()
                logger.info(f"Customization file changed, sending update: {new_arn}")
                self.lsp_connection.update_q_customization(new_arn)
                break  # Success, exit retry loop
            except Exception as e:
                if attempt == 2:  # Last attempt
                    logger.error(f"Error handling customization file change after retries: {e}")
                else:
                    logger.debug(f"Retry {attempt + 1}: File read error (likely temporary): {e}")
  
    def stop_watcher_for_customization_file(self):
        """Shutdown file watcher"""
        self.file_watcher.stop_watching()