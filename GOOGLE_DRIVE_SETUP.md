## How to Fix Google Drive Access

### Step 1: Get the Correct Folder ID

1. Open Google Drive: https://drive.google.com
2. Navigate to: **My Drive** → **AI** → **e-ALex**
3. The URL should look like:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```
4. Copy the **FOLDER_ID_HERE** part (everything after `/folders/`)

### Step 2: Share the Folder with Service Account

1. **Right-click** on the **e-ALex** folder in Google Drive
2. Click **"Share"** or **"Manage access"**
3. Click **"Add people and groups"**
4. Paste this email address:
   ```
   ai-agent-service-account@sodium-atrium-484107-u0.iam.gserviceaccount.com
   ```
5. Select **"Viewer"** permission (or "Editor" if you want the bot to potentially modify files)
6. **Uncheck** "Notify people" (the service account won't receive emails)
7. Click **"Share"** or **"Done"**

### Step 3: Verify the Current Folder ID

Your current folder ID in `.env` is:
```
1HmWA0j4BfmDJyEjChQhsDsTuJ9C3Jw77
```

**Important checks:**
- Is this the ID of the **e-ALex** folder specifically?
- Or is it the ID of a parent folder?
- Make sure you're sharing the EXACT folder whose ID is in your `.env`

### Step 4: Test Access

After sharing, run:
```bash
source venv/bin/activate && python test_drive_access.py
```

If it still shows "File not found", then the folder ID is wrong. In that case:
1. Go to the **e-ALex** folder in Google Drive
2. Copy the NEW folder ID from the URL
3. Update your `.env` file with the correct ID

### Troubleshooting

**Common issues:**
1. ❌ You shared a different folder (not the one with ID `1HmWA0j4BfmDJyEjChQhsDsTuJ9C3Jw77`)
2. ❌ The folder ID is from a different Google account
3. ❌ The folder doesn't exist or was deleted
4. ❌ Typo in the service account email when sharing

**To verify:**
- Open this link in your browser (while logged into Google Drive):
  ```
  https://drive.google.com/drive/folders/1HmWA0j4BfmDJyEjChQhsDsTuJ9C3Jw77
  ```
- If you see "File not found" → The folder ID is wrong
- If you see the folder → Copy the ID from the URL and update `.env`

---

## Quick Fix Commands

After you've shared the folder correctly:

```bash
# 1. Test access
source venv/bin/activate && python test_drive_access.py

# 2. If test passes, run ingestion
source venv/bin/activate && python -m src.ingest

# 3. Start the server
source venv/bin/activate && python -m src.main
```
