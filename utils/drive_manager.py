import gdown
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class DriveManager:
    def __init__(self, folder_id):
        self.folder_id = folder_id

    def get_next_reel(self, file_name_or_url):
        """
        Placeholder method if there's advanced logic to resolve a file name 
        from a specific Google Drive folder.
        Currently, it's expected the FileName column in Excel contains the file ID or URL.
        """
        return file_name_or_url

    def download_reel(self, url_or_id, output_path):
        """
        Downloads a file from Google Drive using gdown.
        Accepts either a full public Google Drive link or a file ID.
        """
        try:
            logger.info(f"Attempting to download reel to {output_path}...")
            
            if "http" in url_or_id:
                # Direct download via URL
                gdown.download(url_or_id, output_path, quiet=False)
            else:
                # Download by Google Drive File ID
                gdown.download(id=url_or_id, output=output_path, quiet=False)
            
            if os.path.exists(output_path):
                logger.info("Reel download successful.")
                return True
            else:
                logger.error("Download failed, output file not found.")
                return False
        except Exception as e:
            logger.error(f"Error downloading reel from Drive: {e}")
            return False
