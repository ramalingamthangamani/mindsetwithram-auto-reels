import os
from config import ACCESS_TOKEN, INSTAGRAM_BUSINESS_ID, GOOGLE_DRIVE_FOLDER_ID, POSTS_PER_DAY
from utils.logger import get_logger
from utils.excel_manager import ExcelManager
from utils.drive_manager import DriveManager
from utils.instagram_api import InstagramAPI

logger = get_logger(__name__)

def main():
    logger.info("=== Starting Automated Reel Posting Process ===")
    
    # Check configurations
    if not ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ID:
        logger.error("Missing required Instagram API credentials in environment variables.")
        return

    excel_manager = ExcelManager()
    drive_manager = DriveManager(GOOGLE_DRIVE_FOLDER_ID)
    ig_api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_BUSINESS_ID)

    posts_made = 0

    for _ in range(POSTS_PER_DAY):
        # 1. Read captions and hashtags from Excel
        reel = excel_manager.get_pending_reel()
        if not reel:
            logger.info("No more pending reels to post. Stopping.")
            break

        index = reel['index']
        # FileName is expected to be a Drive File ID or a public URL
        file_name = reel['FileName'] 
        caption = reel['Caption']
        hashtags = reel['Hashtags']
        
        # Construct full caption
        full_caption = str(caption)
        if hashtags and str(hashtags).strip() != "":
            full_caption += f"\n\n{hashtags}"

        logger.info(f"Processing Reel from row {index}: {file_name}")

        # Note: Meta's Graph API requires a public URL for video_url.
        # If the FileName in Excel is a Google Drive File ID, we construct a direct download link.
        if "http" in str(file_name):
            video_url = file_name
        else:
            video_url = f"https://drive.google.com/uc?export=download&id={file_name}"
            
        # 2. Download from Google Drive (For local verification / archiving if needed)
        # Though the Graph API uses the URL directly, we satisfy the requirement to download it.
        os.makedirs("downloads", exist_ok=True)
        local_path = os.path.join("downloads", f"reel_{index}.mp4")
        
        success = drive_manager.download_reel(file_name, local_path)
        if not success:
            logger.error(f"Failed to download reel '{file_name}'. Marking as failed.")
            excel_manager.mark_as_failed(index)
            continue

        # 3. Upload to Instagram
        container_id = ig_api.create_media_container(video_url, full_caption)
        if not container_id:
            excel_manager.mark_as_failed(index)
            continue

        # 4. Wait for processing
        is_ready = ig_api.check_publish_status(container_id)
        if not is_ready:
            excel_manager.mark_as_failed(index)
            continue

        # 5. Publish
        post_id = ig_api.publish_media(container_id)
        if post_id:
            # 6. Update Excel Status
            excel_manager.mark_as_posted(index)
            posts_made += 1
            logger.info(f"Successfully posted reel! Row index: {index}")
        else:
            excel_manager.mark_as_failed(index)

    logger.info(f"=== Process Completed. Total posts made: {posts_made} ===")

if __name__ == "__main__":
    main()
