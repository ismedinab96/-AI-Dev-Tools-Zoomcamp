import os
import requests

ZIP_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"
ZIP_FILE = "fastmcp.zip"

if not os.path.exists(ZIP_FILE):
    r = requests.get(ZIP_URL)
    with open(ZIP_FILE, "wb") as f:
        f.write(r.content)