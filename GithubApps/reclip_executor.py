# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "yt-dlp",
#     "flask", # Assuming it uses flask or a similar lightweight web framework
#     "imageio-ffmpeg" # MAGIC TRICK: This installs ffmpeg binaries via Python so the user doesn't have to install ffmpeg on their OS!
# ]
# ///
import sys
import os
import urllib.request
import zipfile
import subprocess
import json
import shutil

# The direct URL to the GitHub zip file
GITHUB_ZIP_URL = "https://github.com/averygan/reclip/archive/refs/heads/main.zip"
APP_DIR = os.path.join(os.getcwd(), "installed_apps", "reclip")

def install_app():
    """Downloads and unzips the GitHub repository."""
    if not os.path.exists("installed_apps"):
        os.makedirs("installed_apps")

    zip_path = os.path.join(os.getcwd(), "reclip_temp.zip")
    
    print(json.dumps({"status": "progress", "message": "Downloading Reclip from GitHub..."}))
    urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
    
    print(json.dumps({"status": "progress", "message": "Extracting files..."}))
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("installed_apps")
    
    # GitHub zips always append '-main' or '-master' to the folder name
    extracted_folder = os.path.join(os.getcwd(), "installed_apps", "reclip-main")
    
    # Rename it to our clean APP_DIR
    if os.path.exists(extracted_folder):
        os.rename(extracted_folder, APP_DIR)
        
    # Cleanup the zip file
    os.remove(zip_path)
    print(json.dumps({"status": "progress", "message": "Installation complete!"}))

def run_app():
    """Starts the local server."""
    # Note: Replace 'backend.py' with the actual python file Reclip uses to start the server
    backend_script = os.path.join(APP_DIR, "backend.py") 
    
    print(json.dumps({"status": "success", "message": "Reclip is running on http://localhost:8899"}))
    
    # We use sys.executable to ensure the script runs inside the isolated 'uv' environment
    subprocess.run([sys.executable, backend_script], cwd=APP_DIR)

def main():
    # 1. Install if not exists
    if not os.path.exists(APP_DIR):
        install_app()
    
    # 2. Run the application
    run_app()

if __name__ == "__main__":
    main()
