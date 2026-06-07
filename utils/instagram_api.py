import requests
import time
from utils.logger import get_logger

logger = get_logger(__name__)

class InstagramAPI:
    def __init__(self, access_token, instagram_business_id):
        self.access_token = access_token
        self.instagram_business_id = instagram_business_id
        self.base_url = "https://graph.facebook.com/v19.0"

    def create_media_container(self, video_url, caption):
        """
        Step 1: Create a media container for the Reel.
        Instagram Graph API requires the video to be accessible via a public URL.
        """
        url = f"{self.base_url}/{self.instagram_business_id}/media"
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'access_token': self.access_token
        }
        
        logger.info("Creating media container on Instagram...")
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            container_id = response.json().get('id')
            logger.info(f"Media container successfully created: {container_id}")
            return container_id
        else:
            logger.error(f"Failed to create media container: {response.text}")
            return None

    def check_publish_status(self, container_id):
        """
        Step 2: Wait for Instagram to finish processing the media container.
        """
        url = f"{self.base_url}/{container_id}"
        params = {
            'fields': 'status_code',
            'access_token': self.access_token
        }
        
        max_retries = 12
        for attempt in range(1, max_retries + 1):
            logger.info(f"Checking container status (Attempt {attempt}/{max_retries})...")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                status = response.json().get('status_code')
                logger.info(f"Container status: {status}")
                if status == 'FINISHED':
                    return True
                elif status == 'ERROR':
                    logger.error("Container processing encountered an error.")
                    return False
            else:
                logger.warning(f"Error checking status: {response.text}")
            
            # Wait 10 seconds before polling again
            time.sleep(10)
            
        logger.error("Timeout reached while waiting for container to be ready.")
        return False

    def publish_media(self, container_id):
        """
        Step 3: Publish the processed media container as a Reel.
        """
        url = f"{self.base_url}/{self.instagram_business_id}/media_publish"
        payload = {
            'creation_id': container_id,
            'access_token': self.access_token
        }
        
        logger.info(f"Publishing media {container_id}...")
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            post_id = response.json().get('id')
            logger.info(f"Successfully published reel! Post ID: {post_id}")
            return post_id
        else:
            logger.error(f"Failed to publish reel: {response.text}")
            return None
