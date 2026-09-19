from database.storage import supabase
import base64
from PIL import Image
import io
import pymupdf
from pathlib import Path
import os
import subprocess
import time

file_path = (
    "76f6e1cd-85de-46f7-b4c7-074284b3a1cc/"
    "resume/"
    "Resume.pdf"
)

pdf_bytes = supabase.storage.from_("user-files").download(file_path)

saving_point = "/Users/peytonrivers/application"

filename = os.path.basename(file_path)
print(f"filename: {filename}")

full_path = os.path.join(saving_point, filename)

with open(full_path, 'wb') as f:
    f.write(pdf_bytes)
print("complete")
time.sleep(1)
run = subprocess.run(["rm", full_path])
