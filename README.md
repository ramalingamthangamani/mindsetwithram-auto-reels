# MindsetWithRam Auto Reels

Fully automated Instagram Reel posting pipeline built with Python and GitHub Actions.

## Architecture

Google Drive (Reels) → Excel (Captions/Status) → Python → Instagram Graph API → GitHub Actions → Daily Automatic Posting

## Prerequisites

1. **Python 3.12+**
2. **Meta Developer App**:
   - Create an app at [Meta for Developers](https://developers.facebook.com/).
   - Setup Instagram Graph API.
   - Get your `ACCESS_TOKEN` (Long-lived token recommended), `INSTAGRAM_BUSINESS_ID`, and `PAGE_ID`.
3. **Google Drive**:
   - Ensure the videos in Google Drive are accessible.
   - You can get the file ID from a shareable link.
   - *Note on Meta Graph API*: Instagram requires a public video URL to upload a Reel. You must make sure your Google Drive links are publicly accessible or use direct download links in the Excel file.

## Setup Instructions

### 1. Local Configuration

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in the required values:
   ```bash
   cp .env.example .env
   ```
3. Run the application once locally to generate the template `reels.xlsx`:
   ```bash
   python post_reel.py
   ```

### 2. Excel Format (`reels.xlsx`)

Fill in the generated `reels.xlsx` file with your 507 reels.

| FileName | Caption | Hashtags | Status | PostedDate |
| :--- | :--- | :--- | :--- | :--- |
| `1x2y3z...` (Drive File ID) or URL | Mindset tip! | #mindset #growth | Pending | |
| `a1b2c3...` | Stay focused! | #focus | Pending | |

- **FileName**: The Google Drive File ID or a direct public URL to the `.mp4` file.
- **Status**: Must be exactly `Pending` to be picked up by the script. (Will update to `Posted` or `Failed`).

### 3. GitHub Secrets Setup

To run this pipeline completely automated (computer OFF), configure the following repository secrets in your GitHub repository:
Navigate to **Settings > Secrets and variables > Actions > New repository secret**.

- `ACCESS_TOKEN`
- `INSTAGRAM_BUSINESS_ID`
- `PAGE_ID`
- `GOOGLE_DRIVE_FOLDER_ID`

### 4. Deployment

Push your code and the filled `reels.xlsx` to GitHub:

```bash
git add .
git commit -m "Initial commit with reels"
git push origin main
```

The GitHub Action (`.github/workflows/post.yml`) will run automatically every day at 12:00 UTC. It will read the Excel file, download the next pending video, publish it to Instagram, update the Excel file's status, and commit the changes back to the repository.

You can also trigger it manually from the "Actions" tab in GitHub.

## Local Testing

To verify dependencies and ensure basic scripts are running correctly, run tests via pytest:

```bash
pytest tests/
```
