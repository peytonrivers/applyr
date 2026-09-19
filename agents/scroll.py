import pyautogui
import time
from database.storage import supabase
import os
import subprocess

application_path = "/Users/peytonrivers/application"
file_path = "76f6e1cd-85de-46f7-b4c7-074284b3a1cc/resume/Resume.pdf"
file_name = os.path.basename(file_path)
resume_bytes = supabase.storage.from_("user-files").download(file_path)
full_path = os.path.join(application_path, file_name)
with open(full_path, "wb") as f:
    f.write(resume_bytes)


time.sleep(3)
pyautogui.moveTo(350, 400)
time.sleep(2)
pyautogui.click()
time.sleep(2)
pyautogui.press('right')
time.sleep(1)
pyautogui.press("enter")
run = subprocess.run(["rm", full_path], capture_output=True)
print(f"run: {run}")