# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "yt-dlp",
#     "flask",
#     "imageio-ffmpeg"
# ]
# ///
import sys
import os
import urllib.request
import zipfile
import subprocess
import json

GITHUB_ZIP_URL = "https://github.com/averygan/reclip/archive/refs/heads/main.zip"
APP_DIR = os.path.join(os.getcwd(), "installed_apps", "reclip")

def install_app():
    if not os.path.exists("installed_apps"):
        os.makedirs("installed_apps")

    zip_path = os.path.join(os.getcwd(), "reclip_temp.zip")
    
    print(json.dumps({"status": "progress", "message": "Downloading Reclip from GitHub..."}))
    urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
    
    print(json.dumps({"status": "progress", "message": "Extracting files..."}))
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("installed_apps")
    
    extracted_folder = os.path.join(os.getcwd(), "installed_apps", "reclip-main")
    if os.path.exists(extracted_folder):
        os.rename(extracted_folder, APP_DIR)
        
    os.remove(zip_path)
    print(json.dumps({"status": "progress", "message": "Installation complete!"}))

def run_app():
    backend_script = os.path.join(APP_DIR, "app.py") 
    
    print(json.dumps({"status": "success", "message": "Reclip is running on http://localhost:8899"}))
    
    kwargs = {}
    if os.name == 'nt':
        kwargs.update(creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kwargs.update(start_new_session=True)

    # FIXED: We route stdout and stderr to DEVNULL so the Flask server stops talking to the UI.
    # This allows the script to finish and trigger the green "Success" UI!
    subprocess.Popen(
        [sys.executable, backend_script], 
        cwd=APP_DIR, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL, 
        **kwargs
    )

def main():
    if not os.path.exists(APP_DIR):
        install_app()
    run_app()

if __name__ == "__main__":
    main()
