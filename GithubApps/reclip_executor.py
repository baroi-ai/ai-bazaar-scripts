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
    if not os.path.exists("installed_apps"): os.makedirs("installed_apps")
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

def run_app(dynamic_port):
    kwargs = {}
    if os.name == 'nt':
        kwargs.update(creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kwargs.update(start_new_session=True)

    # We use the Flask CLI to force Reclip onto the dynamic port provided by your Daemon
    process = subprocess.Popen(
        [sys.executable, "-m", "flask", "--app", "app.py", "run", "--port", str(dynamic_port)], 
        cwd=APP_DIR, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL, 
        **kwargs
    )
    
    # Send the final dynamic port and the exact background PID back to the Node daemon
    print(json.dumps({
        "status": "success", 
        "message": f"Reclip is running on http://localhost:{dynamic_port}",
        "port": dynamic_port,
        "pid": process.pid
    }))

def main():
    # The Daemon will pass the open port as the 3rd argument
    target_port = sys.argv[3] if len(sys.argv) > 3 else "8899"
    
    if not os.path.exists(APP_DIR):
        install_app()
    run_app(target_port)

if __name__ == "__main__":
    main()
