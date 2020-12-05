from PIL import ImageGrab
from datetime import datetime
from win32api import GetSystemMetrics
import time
import os


output_path = "D:\\DRIVE\\Development\\csgo-captures"
extension = "png"

# box_dimension = [320, 320] # w, h
box_dimension = [640, 640] # w, h


if __name__ == "__main__":
    # get desktop width and height
    dimension = [GetSystemMetrics(0), GetSystemMetrics(1)] # x, y
    center = [int(dimension[0] / 2), int(dimension[1] / 2)]

    # calculate center square dimension
    x1 = center[0] - int(box_dimension[0] / 2)
    y1 = center[1] - int(box_dimension[1] / 2)
    x2 = center[0] + int(box_dimension[0] / 2)
    y2 = center[1] + int(box_dimension[1] / 2)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    while True:
        dt = datetime.now()
        fname = f"{output_path}/cs-{dt.strftime('%H%M%S')}-{dt.microsecond // 100000}.{extension}"
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        img.save(fname, extension)
        time.sleep(0.5)
