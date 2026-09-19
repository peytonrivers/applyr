from PIL import Image
import io
import requests
import base64
import numpy as np

file_path = "/Users/peytonrivers/Desktop/small13.png"
image = Image.open(file_path)
buf = io.BytesIO()
image.save(buf, format="PNG")
byt = buf.getvalue()
encoded_bytes = base64.b64encode(byt).decode("utf-8")

data = {"image_input": encoded_bytes, "box_threshold": 0.05, "iou_threshold": 0.10, "use_paddleocr": True, "imgsz": 640}
data = requests.post("http://127.0.0.1:8000/image_process", json=data)
data_details = data.json()
encoded_bytes = data_details["encoded_bytes"]
boxes_details = data_details["boxes_details"]
coordinates = []
for i in range(len(boxes_details)):
    current_box = boxes_details[i]
    coordinates.append(current_box["bbox"])
decoded_bytes = base64.b64decode(encoded_bytes.encode("utf-8"))
buffer = io.BytesIO(decoded_bytes)
image = Image.open(buffer)
width, height = image.size
image.show()
arr = np.array(image)
column_remove = list(range(width))
row_remove = list(range(height))
for l in range(len(coordinates)):
    box = coordinates[l]
    x1, y1 = (round(box[0] * width), round(box[1] * height))
    x2, y2 = (round(box[2] * width), round(box[3] * height))
    temp_column = list(range(x1-2, x2+2))
    temp_row = list(range(y1-2, y2+2))
    for column in temp_column:
        if column in column_remove:
            column_remove.remove(column)
    for row in temp_row:
        if row in row_remove:
            row_remove.remove(row)
arr = np.delete(arr, column_remove, axis=1)
arr = np.delete(arr, row_remove, axis=0)
new_image = Image.fromarray(arr)
new_image.show()
