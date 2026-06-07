import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Instagram API Credentials
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
PAGE_ID = os.getenv("PAGE_ID")

# Google Drive
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# Application Configuration
POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", 1))
EXCEL_FILE = "reels.xlsx"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "posting.log")

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)
