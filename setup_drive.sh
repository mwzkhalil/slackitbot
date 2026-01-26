#!/bin/bash
# Interactive Google Drive setup helper

echo "=================================="
echo "Google Drive Access Setup Helper"
echo "=================================="
echo ""

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Activating virtual environment..."
    source venv/bin/activate
fi

echo "Current service account email:"
echo "  ai-agent-service-account@sodium-atrium-484107-u0.iam.gserviceaccount.com"
echo ""
echo "Current folder ID in .env:"
CURRENT_ID=$(grep GOOGLE_DRIVE_FOLDER_E_ALEX .env | cut -d'=' -f2)
echo "  $CURRENT_ID"
echo ""
echo "Testing if this folder is accessible..."
echo ""

# Test current access
python test_drive_access.py

echo ""
echo "=================================="
echo "Next Steps:"
echo "=================================="
echo ""
echo "1. Open this URL in your browser to verify the folder exists:"
echo "   https://drive.google.com/drive/folders/$CURRENT_ID"
echo ""
echo "2. If you see 'File not found', the folder ID is WRONG. You need to:"
echo "   a) Go to Google Drive: My Drive/AI/e-ALex"
echo "   b) Copy the folder ID from the URL"
echo "   c) Update .env file with: GOOGLE_DRIVE_FOLDER_E_ALEX=NEW_FOLDER_ID"
echo ""
echo "3. If you see the folder, then you need to SHARE it:"
echo "   a) Right-click the folder → Share"
echo "   b) Add: ai-agent-service-account@sodium-atrium-484107-u0.iam.gserviceaccount.com"
echo "   c) Give 'Viewer' permission"
echo "   d) Click Share"
echo ""
echo "4. After sharing, run this script again to verify:"
echo "   bash setup_drive.sh"
echo ""
echo "=================================="

# Offer to update folder ID
echo ""
read -p "Do you want to update the folder ID now? (y/n): " answer
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    read -p "Enter the NEW folder ID from Google Drive URL: " new_id
    if [[ ! -z "$new_id" ]]; then
        # Update .env file
        sed -i "s|GOOGLE_DRIVE_FOLDER_E_ALEX=.*|GOOGLE_DRIVE_FOLDER_E_ALEX=$new_id|" .env
        echo "✓ Updated .env file with folder ID: $new_id"
        echo ""
        echo "Now make sure to SHARE the folder with the service account!"
        echo "Then run: bash setup_drive.sh"
    fi
fi
