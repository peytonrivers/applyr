from PIL import Image
import io
import base64
import requests

file_path = "/Users/peytonrivers/desktop/test_screenshot.png"

img = Image.open(file_path).convert("RGB")

buffer = io.BytesIO()
img.save(buffer, format="PNG")

image_bytes = buffer.getvalue()

image_base64 = base64.b64encode(image_bytes).decode("utf-8")

data = {
    "image_input": image_base64,
    "box_threshold": 0.05,
    "iou_threshold": 0.10,
    "use_paddleocr": True,
    "imgsz": 640
}

response = requests.post(
    "http://127.0.0.1:8000/image_process",
    json=data,
    timeout=600
)

print("Status:", response.status_code)

if response.ok:
    result = response.json()
    new_bytes = result["image"]
    decoded_bytes = base64.b64decode(new_bytes.encode("utf-8"))
    buffer_again = io.BytesIO(decoded_bytes)
    image = Image.open(buffer_again)
    print(f"New image: {image}")
    print("Bounding boxes:", result["bounding_boxes"])
else:
    print("Error:", response.text)