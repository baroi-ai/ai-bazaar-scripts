# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "uv"
# ]
# ///
import sys
import os
import urllib.request
import zipfile
import subprocess
import json

GITHUB_ZIP_URL = "https://github.com/harry0703/MoneyPrinterTurbo/archive/refs/heads/main.zip"
APP_DIR = os.path.join(os.getcwd(), "installed_apps", "MoneyPrinterTurbo")

UV_BINARY_NAME = "uv.exe" if os.name == 'nt' else "uv"
LOCAL_UV_PATH = os.path.join(os.getcwd(), UV_BINARY_NAME)

# Global variable to track progress and prevent log spamming
last_percent = -1

def download_progress_hook(count, block_size, total_size):
    global last_percent
    if total_size > 0:
        percent = int((count * block_size * 100) / total_size)
        
        # Only send a log every 10% so we don't flood the React frontend
        if percent % 10 == 0 and percent != last_percent:
            print(json.dumps({"status": "progress", "message": f"Downloading... {percent}% complete"}))
            sys.stdout.flush() # CRITICAL: Forces Python to send the log immediately to Node
            last_percent = percent

def install_app():
    if not os.path.exists("installed_apps"):
        os.makedirs("installed_apps")

    zip_path = os.path.join(os.getcwd(), "moneyprinter_temp.zip")
    
    print(json.dumps({"status": "progress", "message": "Connecting to GitHub repository..."}))
    sys.stdout.flush()
    
    # Pass our progress hook into urlretrieve
    urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path, reporthook=download_progress_hook)
    
    print(json.dumps({"status": "progress", "message": "Download finished. Extracting application package..."}))
    sys.stdout.flush()
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("installed_apps")
    
    extracted_folder = os.path.join(os.getcwd(), "installed_apps", "MoneyPrinterTurbo-main")
    if os.path.exists(extracted_folder):
        os.rename(extracted_folder, APP_DIR)
        
    os.remove(zip_path)

    print(json.dumps({"status": "progress", "message": "UV: Compiling virtual environment freeze locks (this may take a moment)..."}))
    sys.stdout.flush()
    
    # Clean VIRTUAL_ENV during install
    install_env = os.environ.copy()
    install_env.pop("VIRTUAL_ENV", None)
    
    subprocess.run(
        [LOCAL_UV_PATH, "sync", "--frozen"], 
        cwd=APP_DIR, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
        env=install_env
    )
    
    print(json.dumps({"status": "progress", "message": "Installation complete!"}))
    sys.stdout.flush()

def run_app(dynamic_port):
    kwargs = {}
    if os.name == 'nt':
        kwargs.update(creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kwargs.update(start_new_session=True)

    config_example = os.path.join(APP_DIR, "config.example.toml")
    config_real = os.path.join(APP_DIR, "config.toml")
    if os.path.exists(config_example) and not os.path.exists(config_real):
        try:
            import shutil
            shutil.copy(config_example, config_real)
        except Exception:
            pass

    log_file_path = os.path.join(APP_DIR, "crash.log")
    log_file = open(log_file_path, "w")

    # THIS IS THE CRITICAL FIX THAT WAS MISSING
    # It forces Streamlit into headless mode and stops the environment inheritance
    app_env = os.environ.copy()
    app_env.pop("VIRTUAL_ENV", None)
    app_env["STREAMLIT_SERVER_HEADLESS"] = "true"
    app_env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    # Notice stdin=subprocess.DEVNULL and env=app_env below!
    process = subprocess.Popen(
        [
            LOCAL_UV_PATH, "run", "streamlit", "run", "./webui/Main.py", 
            "--server.port", str(dynamic_port),
            "--server.address", "127.0.0.1"
        ], 
        cwd=APP_DIR, 
        stdout=log_file, 
        stderr=log_file, 
        stdin=subprocess.DEVNULL, 
        env=app_env,
        **kwargs
    )
    
    print(json.dumps({
        "status": "success", 
        "message": f"MoneyPrinterTurbo running on http://localhost:{dynamic_port}",
        "port": dynamic_port,
        "pid": process.pid
    }))
    sys.stdout.flush()

def main():
    target_port = sys.argv[3] if len(sys.argv) > 3 else "8501"
    
    if not os.path.exists(APP_DIR):
        install_app()
    else:
        print(json.dumps({"status": "progress", "message": "App already installed. Booting from local storage..."}))
        sys.stdout.flush()
        
    run_app(target_port)

if __name__ == "__main__":
    main()
