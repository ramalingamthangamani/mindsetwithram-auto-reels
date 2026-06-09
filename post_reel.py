import sys
import os
import re
import time
import requests
import pandas as pd
import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration from environment variables
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

def get_current_index():
    index_file = "current_index.txt"
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                return int(content)
    return 1

def update_current_index(new_index):
    with open("current_index.txt", "w") as f:
        f.write(str(new_index))
    logger.info(f"Updated current_index.txt to {new_index}")

def fetch_cloudinary_videos():
    """Fetch all video resources from Cloudinary and sort them by reel number."""
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )
    
    videos = []
    next_cursor = None
    
    logger.info("Fetching video assets from Cloudinary...")
    while True:
        try:
            response = cloudinary.api.resources(
                resource_type="video",
                max_results=500,
                next_cursor=next_cursor
            )
            videos.extend(response.get("resources", []))
            next_cursor = response.get("next_cursor")
            if not next_cursor:
                break
        except Exception as e:
            logger.error(f"Error fetching from Cloudinary: {e}")
            break
            
    # Extract reel number and sort
    parsed_videos = []
    for v in videos:
        # e.g. public_id is "reel_1_pe675n" or similar
        filename = v.get("public_id", "")
        match = re.search(r'reel_(\d+)', filename, re.IGNORECASE)
        if match:
            reel_num = int(match.group(1))
            parsed_videos.append({
                "reel_num": reel_num,
                "url": v.get("secure_url"),
                "public_id": filename
            })
            
    # Sort numerically
    parsed_videos.sort(key=lambda x: x["reel_num"])
    logger.info(f"Found {len(parsed_videos)} valid reel videos in Cloudinary.")
    return parsed_videos

def get_caption_for_reel(reel_num):
    """Read caption from captions.csv for the given reel number."""
    try:
        df = pd.read_csv("captions.csv")
        target_filename = f"reel_{reel_num}.mp4"
        
        row = df[df["FileName"] == target_filename]
        if row.empty:
            logger.warning(f"No caption found in captions.csv for {target_filename}")
            return ""
            
        caption = str(row.iloc[0]["Caption"]).strip()
        hashtags = str(row.iloc[0]["Hashtags"]).strip()
        
        if pd.isna(row.iloc[0]["Caption"]) or caption == "nan":
            caption = ""
        if pd.isna(row.iloc[0]["Hashtags"]) or hashtags == "nan":
            hashtags = ""
            
        if hashtags:
            full_caption = f"{caption}\n\n{hashtags}"
        else:
            full_caption = caption
            
        return full_caption
    except Exception as e:
        logger.error(f"Error reading captions.csv: {e}")
        return ""

def create_ig_container(video_url, caption):
    """Create a media container for Instagram Reel."""
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    logger.info("Creating Instagram media container...")
    response = requests.post(url, data=payload)
    data = response.json()
    
    if "id" in data:
        logger.info(f"Container created successfully. ID: {data['id']}")
        return data["id"]
    else:
        logger.error(f"Failed to create container: {data}")
        return None

def check_container_status(container_id):
    """Wait and check if the container is ready for publishing."""
    url = f"https://graph.facebook.com/v18.0/{container_id}"
    params = {
        "fields": "status_code",
        "access_token": ACCESS_TOKEN
    }
    
    max_retries = 10
    for i in range(max_retries):
        logger.info(f"Checking status for container {container_id} (Attempt {i+1}/{max_retries})...")
        response = requests.get(url, params=params)
        data = response.json()
        
        status = data.get("status_code")
        if status == "FINISHED":
            return True
        elif status == "ERROR":
            logger.error(f"Container processing error: {data}")
            return False
            
        time.sleep(15) # Wait before polling again
        
    logger.error("Container processing timed out.")
    return False

def publish_container(container_id):
    """Publish the ready container to Instagram."""
    url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN
    }
    
    logger.info("Publishing container...")
    response = requests.post(url, data=payload)
    data = response.json()
    
    if "id" in data:
        logger.info(f"Successfully published Reel! Post ID: {data['id']}")
        return True
    else:
        logger.error(f"Failed to publish container: {data}")
        return False

def main():
    logger.info("=== Starting Instagram Reel Automation ===")
    
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, ACCESS_TOKEN, IG_USER_ID]):
        logger.error("Missing one or more required environment variables (Cloudinary or IG).")
        sys.exit(1)
        
    current_index = get_current_index()
    logger.info(f"Current Reel Index to post: {current_index}")
    
    # 1. Fetch Cloudinary Videos
    videos = fetch_cloudinary_videos()
    if not videos:
        logger.error("No videos found in Cloudinary.")
        sys.exit(1)
        
    # 2. Find the correct video
    target_video = None
    for v in videos:
        if v["reel_num"] == current_index:
            target_video = v
            break
            
    if not target_video:
        logger.error(f"Could not find video for reel_{current_index} in Cloudinary.")
        sys.exit(1)
        
    logger.info(f"Found target video: {target_video['public_id']} ({target_video['url']})")
    
    # 3. Get Caption
    caption = get_caption_for_reel(current_index)
    logger.info(f"Generated caption length: {len(caption)} characters")
    
    # 4. Create Container
    container_id = create_ig_container(target_video["url"], caption)
    if not container_id:
        sys.exit(1)
        
    # 5. Check Status
    is_ready = check_container_status(container_id)
    if not is_ready:
        sys.exit(1)
        
    # 6. Publish
    success = publish_container(container_id)
    if success:
        # Increment index on success
        update_current_index(current_index + 1)
        logger.info("=== Post complete and index updated! ===")
    else:
        logger.error("=== Post failed, index not updated ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
