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

def install_app():
    if not os.path.exists("installed_apps"):
        os.makedirs("installed_apps")

    zip_path = os.path.join(os.getcwd(), "moneyprinter_temp.zip")
    
    print(json.dumps({"status": "progress", "message": "Downloading MoneyPrinterTurbo from GitHub..."}))
    urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
    
    print(json.dumps({"status": "progress", "message": "Extracting application package..."}))
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("installed_apps")
    
    extracted_folder = os.path.join(os.getcwd(), "installed_apps", "MoneyPrinterTurbo-main")
    if os.path.exists(extracted_folder):
        os.rename(extracted_folder, APP_DIR)
        
    os.remove(zip_path)

    # Synchronize the locked project dependencies using the local UV core
    print(json.dumps({"status": "progress", "message": "UV: Compiling virtual environment freeze locks..."}))
    
    # We run 'uv sync --frozen' inside the app directory to install its exact requirements
    subprocess.run(["uv", "sync", "--frozen"], cwd=APP_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(json.dumps({"status": "progress", "message": "Installation complete!"}))

def run_app(dynamic_port):
    kwargs = {}
    if os.name == 'nt':
        kwargs.update(creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kwargs.update(start_new_session=True)

    # Step 1: Handle config boilerplate if the user hasn't made one yet
    config_example = os.path.join(APP_DIR, "config.example.toml")
    config_real = os.path.join(APP_DIR, "config.toml")
    if os.path.exists(config_example) and not os.path.exists(config_real):
        try:
            import shutil
            shutil.copy(config_example, config_real)
        except Exception:
            pass

    # Step 2: Boot the Streamlit UI mapping onto our dynamic port allocation
    # Command: uv run streamlit run ./webui/Main.py --server.port {port}
    process = subprocess.Popen(
        [
            "uv", "run", "streamlit", "run", "./webui/Main.py", 
            "--server.port", str(dynamic_port),
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats=False"
        ], 
        cwd=APP_DIR, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL, 
        **kwargs
    )
    
    print(json.dumps({
        "status": "success", 
        "message": f"MoneyPrinterTurbo running on http://localhost:{dynamic_port}",
        "port": dynamic_port,
        "pid": process.pid
    }))

def main():
    target_port = sys.argv[3] if len(sys.argv) > 3 else "8501"
    
    if not os.path.exists(APP_DIR):
        install_app()
    run_app(target_port)

if __name__ == "__main__":
    main()
