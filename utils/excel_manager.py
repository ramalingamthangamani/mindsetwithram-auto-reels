import pandas as pd
from datetime import datetime
import os
from utils.logger import get_logger
from config import EXCEL_FILE

logger = get_logger(__name__)

class ExcelManager:
    def __init__(self, file_path=EXCEL_FILE):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            self._create_template()

    def _create_template(self):
        """Creates an empty template Excel file if it doesn't exist."""
        df = pd.DataFrame(columns=['FileName', 'Caption', 'Hashtags', 'Status', 'PostedDate'])
        df.to_excel(self.file_path, index=False)
        logger.info(f"Created template Excel file at {self.file_path}")

    def get_pending_reel(self):
        """
        Reads the Excel file and returns the first row with Status='Pending'.
        Returns a dictionary with the row data and its original index.
        """
        try:
            df = pd.read_excel(self.file_path)
            pending_reels = df[df['Status'] == 'Pending']
            if pending_reels.empty:
                logger.info("No pending reels found.")
                return None
            
            # Get the first pending reel
            reel = pending_reels.iloc[0].to_dict()
            reel['index'] = pending_reels.index[0]
            
            # Ensure nan values are handled safely
            if pd.isna(reel.get('Hashtags')):
                reel['Hashtags'] = ""
            if pd.isna(reel.get('Caption')):
                reel['Caption'] = ""
                
            return reel
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return None

    def mark_as_posted(self, index):
        """Updates the status to 'Posted' and sets the PostedDate."""
        try:
            df = pd.read_excel(self.file_path)
            df.at[index, 'Status'] = 'Posted'
            df.at[index, 'PostedDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.to_excel(self.file_path, index=False)
            logger.info(f"Row {index} successfully marked as Posted in Excel.")
        except Exception as e:
            logger.error(f"Error marking row {index} as posted: {e}")

    def mark_as_failed(self, index):
        """Updates the status to 'Failed'."""
        try:
            df = pd.read_excel(self.file_path)
            df.at[index, 'Status'] = 'Failed'
            df.to_excel(self.file_path, index=False)
            logger.info(f"Row {index} marked as Failed in Excel.")
        except Exception as e:
            logger.error(f"Error marking row {index} as failed: {e}")
