# Instagram Reel Automation (Cloudinary + GitHub Actions)

This project automates posting Instagram Reels 3 times a day using GitHub Actions. It fetches videos from a Cloudinary account, retrieves corresponding captions and hashtags from a local CSV database, and publishes them via the Instagram Graph API.

## Workflow Summary
- **Schedule**: The GitHub Action runs daily at `09:00 AM IST`, `03:00 PM IST`, and `09:00 PM IST`.
- **State Management**: `current_index.txt` keeps track of the reel number that needs to be posted next.
- **Process**:
  1. Action triggers and reads `current_index.txt`.
  2. Queries Cloudinary for all video resources and finds the one matching `reel_{current_index}`.
  3. Queries `captions.csv` for the caption corresponding to `reel_{current_index}.mp4`.
  4. Publishes to Instagram via Graph API.
  5. Updates `current_index.txt` (+1) and commits it back to the repository automatically.

## Requirements
- GitHub repository with Actions enabled.
- Cloudinary account.
- Instagram Professional/Business Account linked to a Facebook Page.
- Facebook Developer App with Instagram Graph API access.

## Setup Instructions

### 1. Add GitHub Secrets
Navigate to your repository settings on GitHub: **Settings > Secrets and variables > Actions**. Add the following repository secrets:

- `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name.
- `CLOUDINARY_API_KEY`: Your Cloudinary API key.
- `CLOUDINARY_API_SECRET`: Your Cloudinary API secret.
- `ACCESS_TOKEN`: The Facebook/Instagram Graph API long-lived access token.
- `IG_USER_ID`: Your Instagram Business Account ID.

### 2. Prepare Cloudinary
Upload your reels to Cloudinary. The automation script will search through all video assets. Ensure your filenames contain the reel number in the format `reel_1`, `reel_2_pe675n`, `reel_507`, etc.

### 3. Setup Captions Database
Ensure `captions.csv` is at the root of the repository. It must contain the columns:
- `FileName` (e.g. `reel_1.mp4`)
- `Caption` (Text caption)
- `Hashtags` (Space-separated hashtags)

### 4. Set Starting Index
Update `current_index.txt` with the reel number you want to start posting from. If left empty, it defaults to `1`.

### 5. Running Manually
You can manually trigger the workflow from the **Actions** tab in GitHub by selecting the `Auto Post Instagram Reels` workflow and clicking `Run workflow`.
